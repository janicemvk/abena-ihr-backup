# =============================================================================
# 5. DATA QUALITY ANALYTICS ENGINE
# =============================================================================

import asyncio
import json
import statistics
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import redis
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from prometheus_metrics import PrometheusMetrics
from intelligence_layer import DataQualityMetrics

class DataQualityDimension(Enum):
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"

@dataclass
class QualityRule:
    dimension: DataQualityDimension
    field: str
    rule_type: str  # required, format, range, etc.
    parameters: Dict[str, Any]
    weight: float = 1.0

class DataQualityAnalyzer:
    def __init__(self, redis_client: redis.Redis, db_session, prometheus_metrics: PrometheusMetrics):
        self.redis_client = redis_client
        self.db_session = db_session
        self.prometheus_metrics = prometheus_metrics
        self.quality_rules = {}
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
    def add_quality_rules(self, data_type: str, rules: List[QualityRule]):
        """Add data quality rules for a specific data type"""
        self.quality_rules[data_type] = rules
    
    def setup_default_quality_rules(self):
        """Set up default data quality rules for common data types"""
        
        # Patient data quality rules
        patient_rules = [
            QualityRule(DataQualityDimension.COMPLETENESS, "mrn", "required", {}),
            QualityRule(DataQualityDimension.COMPLETENESS, "first_name", "required", {}),
            QualityRule(DataQualityDimension.COMPLETENESS, "last_name", "required", {}),
            QualityRule(DataQualityDimension.VALIDITY, "email", "email_format", {}),
            QualityRule(DataQualityDimension.VALIDITY, "phone", "phone_format", {}),
            QualityRule(DataQualityDimension.CONSISTENCY, "gender", "enum", 
                       {"values": ["male", "female", "other", "unknown"]}),
        ]
        self.add_quality_rules("patient", patient_rules)
        
        # Observation data quality rules
        observation_rules = [
            QualityRule(DataQualityDimension.COMPLETENESS, "patient_id", "required", {}),
            QualityRule(DataQualityDimension.COMPLETENESS, "value", "required", {}),
            QualityRule(DataQualityDimension.COMPLETENESS, "unit", "required", {}),
            QualityRule(DataQualityDimension.VALIDITY, "value", "numeric", {}),
            QualityRule(DataQualityDimension.TIMELINESS, "timestamp", "recent", 
                       {"max_age_days": 30}),
            QualityRule(DataQualityDimension.CONSISTENCY, "unit", "standard_units", {}),
        ]
        self.add_quality_rules("observation", observation_rules)
    
    def evaluate_completeness(self, data: pd.DataFrame, field: str, rule: QualityRule) -> Dict[str, Any]:
        """Evaluate completeness of a field"""
        total_records = len(data)
        if total_records == 0:
            return {"score": 0.0, "issues": ["No data to evaluate"]}
        
        non_null_count = data[field].notna().sum()
        non_empty_count = (data[field].astype(str).str.strip() != "").sum()
        
        completeness_score = non_empty_count / total_records
        
        issues = []
        if completeness_score < 0.95:
            missing_count = total_records - non_empty_count
            issues.append(f"{missing_count} records missing {field} ({missing_count/total_records*100:.1f}%)")
        
        return {
            "score": completeness_score,
            "issues": issues,
            "details": {
                "total_records": total_records,
                "complete_records": non_empty_count,
                "missing_records": total_records - non_empty_count
            }
        }
    
    def evaluate_validity(self, data: pd.DataFrame, field: str, rule: QualityRule) -> Dict[str, Any]:
        """Evaluate validity of a field based on format/type rules"""
        total_records = len(data)
        if total_records == 0:
            return {"score": 0.0, "issues": ["No data to evaluate"]}
        
        valid_count = 0
        issues = []
        
        if rule.rule_type == "email_format":
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            valid_mask = data[field].astype(str).str.match(email_pattern, na=False)
            valid_count = valid_mask.sum()
            
            if valid_count < total_records:
                invalid_count = total_records - valid_count
                issues.append(f"{invalid_count} invalid email formats")
        
        elif rule.rule_type == "phone_format":
            phone_pattern = r'^\+?1?[0-9]{10,15}$'
            # Clean phone numbers first
            cleaned_phones = data[field].astype(str).str.replace(r'[^\d+]', '', regex=True)
            valid_mask = cleaned_phones.str.match(phone_pattern, na=False)
            valid_count = valid_mask.sum()
            
            if valid_count < total_records:
                invalid_count = total_records - valid_count
                issues.append(f"{invalid_count} invalid phone formats")
        
        elif rule.rule_type == "numeric":
            valid_mask = pd.to_numeric(data[field], errors='coerce').notna()
            valid_count = valid_mask.sum()
            
            if valid_count < total_records:
                invalid_count = total_records - valid_count
                issues.append(f"{invalid_count} non-numeric values in numeric field")
        
        validity_score = valid_count / total_records if total_records > 0 else 0
        
        return {
            "score": validity_score,
            "issues": issues,
            "details": {
                "total_records": total_records,
                "valid_records": valid_count,
                "invalid_records": total_records - valid_count
            }
        }
    
    def evaluate_consistency(self, data: pd.DataFrame, field: str, rule: QualityRule) -> Dict[str, Any]:
        """Evaluate consistency of a field"""
        total_records = len(data)
        if total_records == 0:
            return {"score": 0.0, "issues": ["No data to evaluate"]}
        
        consistent_count = 0
        issues = []
        
        if rule.rule_type == "enum":
            allowed_values = set(rule.parameters.get("values", []))
            actual_values = set(data[field].dropna().astype(str).str.lower())
            
            valid_values = actual_values.intersection(allowed_values)
            invalid_values = actual_values - allowed_values
            
            consistent_mask = data[field].astype(str).str.lower().isin(allowed_values)
            consistent_count = consistent_mask.sum()
            
            if invalid_values:
                issues.append(f"Invalid values found: {list(invalid_values)}")
        
        elif rule.rule_type == "standard_units":
            # Check for standard medical units
            standard_units = {"kg", "cm", "C", "F", "bpm", "mg/dL", "mmol/L"}
            unit_values = set(data[field].dropna().astype(str))
            
            valid_units = unit_values.intersection(standard_units)
            invalid_units = unit_values - standard_units
            
            consistent_mask = data[field].isin(standard_units)
            consistent_count = consistent_mask.sum()
            
            if invalid_units:
                issues.append(f"Non-standard units found: {list(invalid_units)}")
        
        consistency_score = consistent_count / total_records if total_records > 0 else 0
        
        return {
            "score": consistency_score,
            "issues": issues,
            "details": {
                "total_records": total_records,
                "consistent_records": consistent_count,
                "inconsistent_records": total_records - consistent_count
            }
        }
    
    def evaluate_timeliness(self, data: pd.DataFrame, field: str, rule: QualityRule) -> Dict[str, Any]:
        """Evaluate timeliness of timestamp fields"""
        total_records = len(data)
        if total_records == 0:
            return {"score": 0.0, "issues": ["No data to evaluate"]}
        
        timely_count = 0
        issues = []
        
        if rule.rule_type == "recent":
            max_age_days = rule.parameters.get("max_age_days", 30)
            cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
            
            # Convert to datetime if not already
            timestamps = pd.to_datetime(data[field], errors='coerce')
            recent_mask = timestamps >= cutoff_date
            timely_count = recent_mask.sum()
            
            old_count = total_records - timely_count
            if old_count > 0:
                issues.append(f"{old_count} records older than {max_age_days} days")
        
        timeliness_score = timely_count / total_records if total_records > 0 else 0
        
        return {
            "score": timeliness_score,
            "issues": issues,
            "details": {
                "total_records": total_records,
                "timely_records": timely_count,
                "outdated_records": total_records - timely_count
            }
        }
    
    async def analyze_data_quality(self, data: pd.DataFrame, data_type: str, 
                                 source_system: str) -> Dict[str, Any]:
        """Perform comprehensive data quality analysis"""
        if data_type not in self.quality_rules:
            return {"error": f"No quality rules defined for data type: {data_type}"}
        
        rules = self.quality_rules[data_type]
        dimension_scores = {}
        all_issues = []
        
        # Evaluate each quality dimension
        for rule in rules:
            if rule.field not in data.columns:
                continue
            
            if rule.dimension == DataQualityDimension.COMPLETENESS:
                result = self.evaluate_completeness(data, rule.field, rule)
            elif rule.dimension == DataQualityDimension.VALIDITY:
                result = self.evaluate_validity(data, rule.field, rule)
            elif rule.dimension == DataQualityDimension.CONSISTENCY:
                result = self.evaluate_consistency(data, rule.field, rule)
            elif rule.dimension == DataQualityDimension.TIMELINESS:
                result = self.evaluate_timeliness(data, rule.field, rule)
            else:
                continue
            
            dimension_key = f"{rule.dimension.value}_{rule.field}"
            dimension_scores[dimension_key] = result["score"] * rule.weight
            all_issues.extend(result["issues"])
        
        # Calculate overall scores for each dimension
        dimension_averages = {}
        for dimension in DataQualityDimension:
            dimension_scores_list = [
                score for key, score in dimension_scores.items() 
                if key.startswith(dimension.value)
            ]
            if dimension_scores_list:
                dimension_averages[dimension.value] = statistics.mean(dimension_scores_list)
            else:
                dimension_averages[dimension.value] = 1.0
        
        # Calculate overall quality score
        overall_score = statistics.mean(dimension_averages.values())
        
        # Update Prometheus metrics
        for dimension, score in dimension_averages.items():
            self.prometheus_metrics.data_quality_score.labels(
                source_system=source_system,
                data_type=data_type,
                metric_type=dimension
            ).set(score)
        
        # Store results in database
        db = next(self.db_session())
        quality_metric = DataQualityMetrics(
            source_system=source_system,
            data_type=data_type,
            total_records=len(data),
            valid_records=int(len(data) * overall_score),
            completeness_score=dimension_averages.get('completeness', 1.0),
            accuracy_score=dimension_averages.get('validity', 1.0),
            consistency_score=dimension_averages.get('consistency', 1.0),
            timeliness_score=dimension_averages.get('timeliness', 1.0),
            quality_issues=all_issues
        )
        db.add(quality_metric)
        db.commit()
        
        return {
            "overall_score": overall_score,
            "dimension_scores": dimension_averages,
            "total_records": len(data),
            "issues": all_issues,
            "detailed_scores": dimension_scores,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def detect_anomalies(self, data: pd.DataFrame, numeric_columns: List[str]) -> Dict[str, Any]:
        """Detect anomalies in numeric data using Isolation Forest"""
        if len(numeric_columns) == 0 or len(data) < 10:
            return {"anomalies": [], "anomaly_score": 0.0}
        
        try:
            # Prepare numeric data
            numeric_data = data[numeric_columns].select_dtypes(include=[np.number])
            if numeric_data.empty:
                return {"anomalies": [], "anomaly_score": 0.0}
            
            # Handle missing values
            numeric_data = numeric_data.fillna(numeric_data.median())
            
            # Scale the data
            scaled_data = self.scaler.fit_transform(numeric_data)
            
            # Detect anomalies
            anomaly_labels = self.anomaly_detector.fit_predict(scaled_data)
            anomaly_scores = self.anomaly_detector.decision_function(scaled_data)
            
            # Get anomalous records
            anomaly_indices = np.where(anomaly_labels == -1)[0]
            anomalies = []
            
            for idx in anomaly_indices:
                anomalies.append({
                    "index": int(idx),
                    "score": float(anomaly_scores[idx]),
                    "values": data.iloc[idx][numeric_columns].to_dict()
                })
            
            # Calculate overall anomaly rate
            anomaly_rate = len(anomalies) / len(data)
            
            return {
                "anomalies": anomalies,
                "anomaly_score": anomaly_rate,
                "total_records": len(data),
                "anomalous_records": len(anomalies)
            }
            
        except Exception as e:
            logging.error(f"Anomaly detection failed: {str(e)}")
            return {"anomalies": [], "anomaly_score": 0.0, "error": str(e)} 