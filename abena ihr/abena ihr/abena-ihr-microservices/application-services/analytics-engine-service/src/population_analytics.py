"""
Population Analytics Module for Abena IHR
=========================================

This module provides population-level analytics capabilities including:
- Population health trends analysis
- Disease prevalence and incidence rates
- Risk factor analysis across populations
- Health outcome comparisons
- Demographic health patterns
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import redis
import httpx
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for data validation
class PopulationData(BaseModel):
    """Population data model"""
    population_id: str
    region: str
    age_groups: Dict[str, int]  # age_group: count
    gender_distribution: Dict[str, int]  # gender: count
    health_metrics: Dict[str, List[float]]  # metric: values
    risk_factors: Dict[str, List[float]]  # factor: values
    disease_prevalence: Dict[str, float]  # disease: prevalence_rate
    socioeconomic_data: Dict[str, Any] = {}

class PopulationAnalysisRequest(BaseModel):
    """Request model for population analysis"""
    population_data: PopulationData
    analysis_type: str = Field(..., regex="^(trends|clustering|risk_analysis|health_outcomes|demographic_patterns)$")
    time_period: Optional[str] = "1_year"
    confidence_level: float = Field(0.95, ge=0.8, le=0.99)

class PopulationAnalysisResponse(BaseModel):
    """Response model for population analysis"""
    population_id: str
    analysis_type: str
    results: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    visualizations: Dict[str, str]  # chart_type: base64_encoded_chart
    timestamp: datetime
    confidence_level: float

class PopulationAnalytics:
    """Population analytics engine"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.scaler = StandardScaler()
        
    def analyze_health_trends(self, population_data: PopulationData, time_period: str = "1_year") -> Dict[str, Any]:
        """Analyze health trends over time"""
        try:
            results = {
                'trend_analysis': {},
                'seasonal_patterns': {},
                'forecasting': {},
                'anomalies': []
            }
            
            # Analyze trends for each health metric
            for metric, values in population_data.health_metrics.items():
                if len(values) >= 2:
                    # Calculate trend
                    x = np.arange(len(values))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                    
                    trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
                    trend_significance = "significant" if p_value < 0.05 else "not_significant"
                    
                    results['trend_analysis'][metric] = {
                        'slope': slope,
                        'r_squared': r_value ** 2,
                        'p_value': p_value,
                        'trend_direction': trend_direction,
                        'trend_significance': trend_significance,
                        'current_value': values[-1] if values else None,
                        'change_percentage': ((values[-1] - values[0]) / values[0] * 100) if values and values[0] != 0 else 0
                    }
                    
                    # Detect anomalies (values outside 2 standard deviations)
                    mean_val = np.mean(values)
                    std_val = np.std(values)
                    anomalies = [i for i, v in enumerate(values) if abs(v - mean_val) > 2 * std_val]
                    
                    if anomalies:
                        results['anomalies'].append({
                            'metric': metric,
                            'anomaly_indices': anomalies,
                            'anomaly_values': [values[i] for i in anomalies]
                        })
                        
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing health trends: {e}")
            raise
            
    def perform_clustering_analysis(self, population_data: PopulationData) -> Dict[str, Any]:
        """Perform clustering analysis to identify population segments"""
        try:
            results = {
                'clusters': [],
                'cluster_characteristics': {},
                'cluster_health_profiles': {},
                'recommendations': []
            }
            
            # Prepare data for clustering
            features = []
            feature_names = []
            
            # Add demographic features
            for age_group, count in population_data.age_groups.items():
                features.append(count)
                feature_names.append(f"age_group_{age_group}")
                
            for gender, count in population_data.gender_distribution.items():
                features.append(count)
                feature_names.append(f"gender_{gender}")
                
            # Add health metrics (use means)
            for metric, values in population_data.health_metrics.items():
                if values:
                    features.append(np.mean(values))
                    feature_names.append(f"health_{metric}")
                    
            # Add risk factors (use means)
            for factor, values in population_data.risk_factors.items():
                if values:
                    features.append(np.mean(values))
                    feature_names.append(f"risk_{factor}")
                    
            # Add disease prevalence
            for disease, prevalence in population_data.disease_prevalence.items():
                features.append(prevalence)
                feature_names.append(f"disease_{disease}")
                
            # Normalize features
            features_array = np.array(features).reshape(1, -1)
            features_normalized = self.scaler.fit_transform(features_array)
            
            # Perform clustering (K-means with 3 clusters)
            kmeans = KMeans(n_clusters=3, random_state=42)
            cluster_labels = kmeans.fit_predict(features_normalized)
            
            # Analyze clusters
            for cluster_id in range(3):
                cluster_mask = cluster_labels == cluster_id
                cluster_data = features_normalized[cluster_mask]
                
                cluster_characteristics = {}
                for i, feature_name in enumerate(feature_names):
                    cluster_characteristics[feature_name] = float(cluster_data[:, i].mean()) if len(cluster_data) > 0 else 0
                    
                results['clusters'].append({
                    'cluster_id': cluster_id,
                    'size': int(np.sum(cluster_mask)),
                    'characteristics': cluster_characteristics
                })
                
                # Generate health profile for cluster
                health_profile = self._generate_cluster_health_profile(cluster_characteristics)
                results['cluster_health_profiles'][cluster_id] = health_profile
                
                # Generate recommendations for cluster
                recommendations = self._generate_cluster_recommendations(cluster_characteristics)
                results['recommendations'].extend(recommendations)
                
            return results
            
        except Exception as e:
            logger.error(f"Error performing clustering analysis: {e}")
            raise
            
    def analyze_risk_factors(self, population_data: PopulationData) -> Dict[str, Any]:
        """Analyze risk factors across the population"""
        try:
            results = {
                'risk_factor_analysis': {},
                'correlations': {},
                'high_risk_groups': [],
                'intervention_targets': []
            }
            
            # Analyze each risk factor
            for factor, values in population_data.risk_factors.items():
                if values:
                    factor_stats = {
                        'mean': np.mean(values),
                        'median': np.median(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values),
                        'high_risk_threshold': np.percentile(values, 75),  # Top 25% as high risk
                        'high_risk_count': sum(1 for v in values if v > np.percentile(values, 75))
                    }
                    
                    results['risk_factor_analysis'][factor] = factor_stats
                    
                    # Calculate correlations with health metrics
                    correlations = {}
                    for metric, metric_values in population_data.health_metrics.items():
                        if len(metric_values) == len(values):
                            correlation, p_value = stats.pearsonr(values, metric_values)
                            correlations[metric] = {
                                'correlation': correlation,
                                'p_value': p_value,
                                'significant': p_value < 0.05
                            }
                            
                    results['correlations'][factor] = correlations
                    
                    # Identify high-risk groups
                    if factor_stats['high_risk_count'] > len(values) * 0.1:  # More than 10% high risk
                        results['high_risk_groups'].append({
                            'factor': factor,
                            'high_risk_count': factor_stats['high_risk_count'],
                            'percentage': factor_stats['high_risk_count'] / len(values) * 100,
                            'threshold': factor_stats['high_risk_threshold']
                        })
                        
                        # Add to intervention targets
                        results['intervention_targets'].append({
                            'factor': factor,
                            'intervention_type': self._suggest_intervention_type(factor),
                            'priority': 'high' if factor_stats['high_risk_count'] / len(values) > 0.2 else 'medium'
                        })
                        
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing risk factors: {e}")
            raise
            
    def analyze_health_outcomes(self, population_data: PopulationData) -> Dict[str, Any]:
        """Analyze health outcomes across the population"""
        try:
            results = {
                'outcome_analysis': {},
                'outcome_comparisons': {},
                'quality_metrics': {},
                'improvement_opportunities': []
            }
            
            # Analyze disease prevalence
            total_population = sum(population_data.age_groups.values())
            
            for disease, prevalence in population_data.disease_prevalence.items():
                affected_count = int(prevalence * total_population / 100)
                
                outcome_metrics = {
                    'prevalence_rate': prevalence,
                    'affected_count': affected_count,
                    'severity_level': self._classify_disease_severity(prevalence),
                    'trend': self._analyze_disease_trend(disease, population_data),
                    'risk_factors': self._identify_disease_risk_factors(disease, population_data)
                }
                
                results['outcome_analysis'][disease] = outcome_metrics
                
                # Compare with benchmarks
                benchmark = self._get_disease_benchmark(disease)
                if benchmark:
                    comparison = {
                        'current_rate': prevalence,
                        'benchmark_rate': benchmark,
                        'difference': prevalence - benchmark,
                        'performance': 'above_benchmark' if prevalence < benchmark else 'below_benchmark'
                    }
                    results['outcome_comparisons'][disease] = comparison
                    
                    # Identify improvement opportunities
                    if prevalence > benchmark:
                        results['improvement_opportunities'].append({
                            'disease': disease,
                            'current_rate': prevalence,
                            'target_rate': benchmark,
                            'improvement_potential': prevalence - benchmark,
                            'priority': 'high' if (prevalence - benchmark) > 5 else 'medium'
                        })
                        
            # Calculate overall quality metrics
            results['quality_metrics'] = {
                'overall_health_score': self._calculate_overall_health_score(population_data),
                'preventable_conditions': self._identify_preventable_conditions(population_data),
                'care_gaps': self._identify_care_gaps(population_data)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing health outcomes: {e}")
            raise
            
    def analyze_demographic_patterns(self, population_data: PopulationData) -> Dict[str, Any]:
        """Analyze health patterns across demographic groups"""
        try:
            results = {
                'demographic_analysis': {},
                'health_disparities': [],
                'equity_metrics': {},
                'targeted_interventions': []
            }
            
            # Analyze age group patterns
            age_group_analysis = {}
            for age_group, count in population_data.age_groups.items():
                age_health_profile = self._analyze_age_group_health(age_group, population_data)
                age_group_analysis[age_group] = age_health_profile
                
            results['demographic_analysis']['age_groups'] = age_group_analysis
            
            # Analyze gender patterns
            gender_analysis = {}
            for gender, count in population_data.gender_distribution.items():
                gender_health_profile = self._analyze_gender_health(gender, population_data)
                gender_analysis[gender] = gender_health_profile
                
            results['demographic_analysis']['gender'] = gender_analysis
            
            # Identify health disparities
            disparities = self._identify_health_disparities(population_data)
            results['health_disparities'] = disparities
            
            # Calculate equity metrics
            results['equity_metrics'] = {
                'gini_coefficient': self._calculate_health_equity(population_data),
                'disparity_index': self._calculate_disparity_index(population_data),
                'access_equity': self._assess_access_equity(population_data)
            }
            
            # Generate targeted interventions
            for disparity in disparities:
                intervention = self._generate_targeted_intervention(disparity)
                results['targeted_interventions'].append(intervention)
                
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing demographic patterns: {e}")
            raise
            
    def _generate_cluster_health_profile(self, characteristics: Dict[str, float]) -> Dict[str, Any]:
        """Generate health profile for a cluster"""
        profile = {
            'overall_health_status': 'unknown',
            'primary_health_concerns': [],
            'risk_level': 'unknown',
            'care_needs': []
        }
        
        # Analyze health metrics
        health_metrics = {k: v for k, v in characteristics.items() if k.startswith('health_')}
        
        if health_metrics:
            avg_health_score = np.mean(list(health_metrics.values()))
            
            if avg_health_score > 0.7:
                profile['overall_health_status'] = 'excellent'
                profile['risk_level'] = 'low'
            elif avg_health_score > 0.5:
                profile['overall_health_status'] = 'good'
                profile['risk_level'] = 'moderate'
            else:
                profile['overall_health_status'] = 'poor'
                profile['risk_level'] = 'high'
                
        # Identify primary health concerns
        risk_factors = {k: v for k, v in characteristics.items() if k.startswith('risk_')}
        high_risk_factors = [k.replace('risk_', '') for k, v in risk_factors.items() if v > 0.6]
        profile['primary_health_concerns'] = high_risk_factors
        
        # Determine care needs
        if profile['risk_level'] == 'high':
            profile['care_needs'] = ['intensive_monitoring', 'preventive_care', 'lifestyle_interventions']
        elif profile['risk_level'] == 'moderate':
            profile['care_needs'] = ['regular_monitoring', 'preventive_care']
        else:
            profile['care_needs'] = ['maintenance_care', 'preventive_screenings']
            
        return profile
        
    def _generate_cluster_recommendations(self, characteristics: Dict[str, float]) -> List[str]:
        """Generate recommendations for a cluster"""
        recommendations = []
        
        # Analyze risk factors
        risk_factors = {k: v for k, v in characteristics.items() if k.startswith('risk_')}
        high_risk_factors = [k.replace('risk_', '') for k, v in risk_factors.items() if v > 0.6]
        
        if 'smoking' in high_risk_factors:
            recommendations.append("Implement smoking cessation programs")
            
        if 'obesity' in high_risk_factors:
            recommendations.append("Develop weight management initiatives")
            
        if 'hypertension' in high_risk_factors:
            recommendations.append("Enhance blood pressure monitoring programs")
            
        # Analyze age distribution
        age_groups = {k: v for k, v in characteristics.items() if k.startswith('age_group_')}
        elderly_population = sum(v for k, v in age_groups.items() if '65' in k or '75' in k)
        
        if elderly_population > 0.3:  # More than 30% elderly
            recommendations.append("Strengthen geriatric care services")
            recommendations.append("Implement fall prevention programs")
            
        return recommendations
        
    def _suggest_intervention_type(self, factor: str) -> str:
        """Suggest intervention type for a risk factor"""
        intervention_map = {
            'smoking': 'behavioral',
            'obesity': 'lifestyle',
            'hypertension': 'medical',
            'diabetes': 'medical',
            'sedentary': 'lifestyle',
            'alcohol': 'behavioral',
            'diet': 'lifestyle'
        }
        
        return intervention_map.get(factor, 'general')
        
    def _classify_disease_severity(self, prevalence: float) -> str:
        """Classify disease severity based on prevalence"""
        if prevalence > 20:
            return 'high'
        elif prevalence > 10:
            return 'moderate'
        else:
            return 'low'
            
    def _analyze_disease_trend(self, disease: str, population_data: PopulationData) -> str:
        """Analyze disease trend (simplified)"""
        # This would typically use historical data
        return 'stable'  # Placeholder
        
    def _identify_disease_risk_factors(self, disease: str, population_data: PopulationData) -> List[str]:
        """Identify risk factors for a specific disease"""
        # This would use medical knowledge base
        disease_risk_map = {
            'diabetes': ['obesity', 'family_history', 'sedentary_lifestyle'],
            'hypertension': ['obesity', 'high_salt_diet', 'stress'],
            'heart_disease': ['smoking', 'obesity', 'hypertension'],
            'cancer': ['smoking', 'age', 'family_history']
        }
        
        return disease_risk_map.get(disease, [])
        
    def _get_disease_benchmark(self, disease: str) -> Optional[float]:
        """Get benchmark prevalence for a disease"""
        benchmarks = {
            'diabetes': 9.4,  # US average
            'hypertension': 32.0,
            'heart_disease': 4.8,
            'cancer': 1.8
        }
        
        return benchmarks.get(disease)
        
    def _calculate_overall_health_score(self, population_data: PopulationData) -> float:
        """Calculate overall health score for the population"""
        # Simplified calculation
        health_metrics = list(population_data.health_metrics.values())
        if health_metrics:
            return np.mean([np.mean(values) for values in health_metrics if values])
        return 0.5
        
    def _identify_preventable_conditions(self, population_data: PopulationData) -> List[str]:
        """Identify preventable conditions in the population"""
        preventable_conditions = []
        
        for disease, prevalence in population_data.disease_prevalence.items():
            if disease in ['diabetes', 'hypertension', 'obesity'] and prevalence > 15:
                preventable_conditions.append(disease)
                
        return preventable_conditions
        
    def _identify_care_gaps(self, population_data: PopulationData) -> List[Dict[str, Any]]:
        """Identify care gaps in the population"""
        care_gaps = []
        
        # Example care gaps
        if 'diabetes' in population_data.disease_prevalence:
            care_gaps.append({
                'gap_type': 'screening',
                'condition': 'diabetes',
                'description': 'Regular blood glucose screening needed',
                'priority': 'high'
            })
            
        return care_gaps
        
    def _analyze_age_group_health(self, age_group: str, population_data: PopulationData) -> Dict[str, Any]:
        """Analyze health patterns for a specific age group"""
        return {
            'health_status': 'good',
            'primary_concerns': [],
            'care_needs': []
        }
        
    def _analyze_gender_health(self, gender: str, population_data: PopulationData) -> Dict[str, Any]:
        """Analyze health patterns for a specific gender"""
        return {
            'health_status': 'good',
            'primary_concerns': [],
            'care_needs': []
        }
        
    def _identify_health_disparities(self, population_data: PopulationData) -> List[Dict[str, Any]]:
        """Identify health disparities across demographic groups"""
        disparities = []
        
        # Example disparities
        disparities.append({
            'disparity_type': 'age',
            'description': 'Older adults have higher disease prevalence',
            'magnitude': 'moderate',
            'priority': 'medium'
        })
        
        return disparities
        
    def _calculate_health_equity(self, population_data: PopulationData) -> float:
        """Calculate health equity using Gini coefficient"""
        # Simplified calculation
        return 0.3  # Placeholder
        
    def _calculate_disparity_index(self, population_data: PopulationData) -> float:
        """Calculate disparity index"""
        return 0.2  # Placeholder
        
    def _assess_access_equity(self, population_data: PopulationData) -> str:
        """Assess access equity"""
        return 'good'  # Placeholder
        
    def _generate_targeted_intervention(self, disparity: Dict[str, Any]) -> Dict[str, Any]:
        """Generate targeted intervention for a disparity"""
        return {
            'disparity_type': disparity['disparity_type'],
            'intervention_type': 'targeted_program',
            'description': f"Address {disparity['description']}",
            'priority': disparity['priority']
        }

# Initialize population analytics
population_analytics = PopulationAnalytics()

# FastAPI app for population analytics
app = FastAPI(
    title="Abena IHR Population Analytics",
    description="Population-level health analytics and insights",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "population_analytics",
        "timestamp": datetime.now()
    }

@app.post("/analyze", response_model=PopulationAnalysisResponse)
async def analyze_population(request: PopulationAnalysisRequest):
    """Perform population analysis"""
    try:
        population_data = request.population_data
        analysis_type = request.analysis_type
        
        # Perform analysis based on type
        if analysis_type == "trends":
            results = population_analytics.analyze_health_trends(population_data, request.time_period)
        elif analysis_type == "clustering":
            results = population_analytics.perform_clustering_analysis(population_data)
        elif analysis_type == "risk_analysis":
            results = population_analytics.analyze_risk_factors(population_data)
        elif analysis_type == "health_outcomes":
            results = population_analytics.analyze_health_outcomes(population_data)
        elif analysis_type == "demographic_patterns":
            results = population_analytics.analyze_demographic_patterns(population_data)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported analysis type: {analysis_type}")
            
        # Generate insights and recommendations
        insights = population_analytics._generate_insights(results, analysis_type)
        recommendations = population_analytics._generate_recommendations(results, analysis_type)
        
        # Generate visualizations
        visualizations = population_analytics._generate_visualizations(results, analysis_type)
        
        return PopulationAnalysisResponse(
            population_id=population_data.population_id,
            analysis_type=analysis_type,
            results=results,
            insights=insights,
            recommendations=recommendations,
            visualizations=visualizations,
            timestamp=datetime.now(),
            confidence_level=request.confidence_level
        )
        
    except Exception as e:
        logger.error(f"Error performing population analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add methods to PopulationAnalytics class
def _generate_insights(self, results: Dict[str, Any], analysis_type: str) -> List[str]:
    """Generate insights from analysis results"""
    insights = []
    
    if analysis_type == "trends":
        for metric, trend_data in results.get('trend_analysis', {}).items():
            if trend_data['trend_significance'] == 'significant':
                direction = trend_data['trend_direction']
                change = trend_data['change_percentage']
                insights.append(f"{metric} shows {direction} trend with {change:.1f}% change")
                
    elif analysis_type == "clustering":
        for cluster in results.get('clusters', []):
            size = cluster['size']
            insights.append(f"Cluster {cluster['cluster_id']} contains {size} individuals with distinct health profile")
            
    elif analysis_type == "risk_analysis":
        for factor, analysis in results.get('risk_factor_analysis', {}).items():
            high_risk_pct = analysis['high_risk_count'] / analysis['count'] * 100
            if high_risk_pct > 20:
                insights.append(f"{factor} affects {high_risk_pct:.1f}% of population")
                
    return insights

def _generate_recommendations(self, results: Dict[str, Any], analysis_type: str) -> List[str]:
    """Generate recommendations from analysis results"""
    recommendations = []
    
    if analysis_type == "trends":
        for metric, trend_data in results.get('trend_analysis', {}).items():
            if trend_data['trend_direction'] == 'increasing' and trend_data['trend_significance'] == 'significant':
                recommendations.append(f"Implement interventions to address increasing {metric}")
                
    elif analysis_type == "clustering":
        recommendations.extend(results.get('recommendations', []))
        
    elif analysis_type == "risk_analysis":
        for target in results.get('intervention_targets', []):
            recommendations.append(f"Develop {target['intervention_type']} program for {target['factor']}")
            
    return recommendations

def _generate_visualizations(self, results: Dict[str, Any], analysis_type: str) -> Dict[str, str]:
    """Generate visualizations for analysis results"""
    visualizations = {}
    
    # This would generate actual charts using plotly
    # For now, return placeholder
    visualizations['main_chart'] = "base64_encoded_chart_placeholder"
    
    return visualizations

# Add methods to PopulationAnalytics class
PopulationAnalytics._generate_insights = _generate_insights
PopulationAnalytics._generate_recommendations = _generate_recommendations
PopulationAnalytics._generate_visualizations = _generate_visualizations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011) 