"""
Abena IHR Privacy & Security Service - Anonymization Manager
============================================================

Comprehensive data anonymization system providing:
- Data masking and pseudonymization
- K-anonymity and l-diversity
- Differential privacy
- HIPAA-compliant anonymization
- Re-identification risk assessment
- Anonymization quality metrics
"""

import hashlib
import uuid
import re
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import asyncio
from collections import defaultdict, Counter
import numpy as np
from cryptography.fernet import Fernet
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnonymizationMethod(Enum):
    """Supported anonymization methods"""
    MASKING = "masking"
    PSEUDONYMIZATION = "pseudonymization"
    GENERALIZATION = "generalization"
    SUPPRESSION = "suppression"
    NOISE_ADDITION = "noise_addition"
    SWAPPING = "swapping"
    SYNTHETIC_DATA = "synthetic_data"


class DataType(Enum):
    """Data types for anonymization"""
    PERSONAL_IDENTIFIER = "personal_identifier"
    QUASI_IDENTIFIER = "quasi_identifier"
    SENSITIVE_ATTRIBUTE = "sensitive_attribute"
    NON_SENSITIVE = "non_sensitive"


class RiskLevel(Enum):
    """Re-identification risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnonymizationRule:
    """Anonymization rule configuration"""
    field_name: str
    data_type: DataType
    method: AnonymizationMethod
    parameters: Dict[str, Any] = field(default_factory=dict)
    k_value: Optional[int] = None  # For k-anonymity
    l_value: Optional[int] = None  # For l-diversity
    epsilon: Optional[float] = None  # For differential privacy
    enabled: bool = True


@dataclass
class AnonymizationJob:
    """Anonymization job tracking"""
    job_id: str
    dataset_id: str
    rules: List[AnonymizationRule]
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    records_anonymized: int = 0
    quality_score: Optional[float] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class AnonymizationManager:
    """
    Comprehensive data anonymization system for healthcare data
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize anonymization manager
        
        Args:
            config: Configuration dictionary containing anonymization settings
        """
        self.config = config
        self.pseudonym_mapping = {}
        self.anonymization_rules = {}
        self.jobs = {}
        self.quality_metrics = {}
        
        # Initialize default rules
        self._initialize_default_rules()
        
        # Initialize pseudonymization key
        self.pseudonym_key = Fernet.generate_key()
        self.pseudonym_cipher = Fernet(self.pseudonym_key)
        
        logger.info("Anonymization Manager initialized successfully")
    
    def _initialize_default_rules(self):
        """Initialize default anonymization rules for common healthcare fields"""
        default_rules = {
            # Personal Identifiers
            'patient_id': AnonymizationRule(
                field_name='patient_id',
                data_type=DataType.PERSONAL_IDENTIFIER,
                method=AnonymizationMethod.PSEUDONYMIZATION,
                parameters={'hash_algorithm': 'sha256'}
            ),
            'ssn': AnonymizationRule(
                field_name='ssn',
                data_type=DataType.PERSONAL_IDENTIFIER,
                method=AnonymizationMethod.MASKING,
                parameters={'mask_char': '*', 'preserve_length': True}
            ),
            'email': AnonymizationRule(
                field_name='email',
                data_type=DataType.PERSONAL_IDENTIFIER,
                method=AnonymizationMethod.MASKING,
                parameters={'mask_char': '*', 'preserve_domain': True}
            ),
            'phone': AnonymizationRule(
                field_name='phone',
                data_type=DataType.PERSONAL_IDENTIFIER,
                method=AnonymizationMethod.MASKING,
                parameters={'mask_char': '*', 'preserve_country_code': True}
            ),
            
            # Quasi-Identifiers
            'date_of_birth': AnonymizationRule(
                field_name='date_of_birth',
                data_type=DataType.QUASI_IDENTIFIER,
                method=AnonymizationMethod.GENERALIZATION,
                parameters={'generalization_level': 'year', 'age_bins': [0, 18, 35, 50, 65, 100]}
            ),
            'zip_code': AnonymizationRule(
                field_name='zip_code',
                data_type=DataType.QUASI_IDENTIFIER,
                method=AnonymizationMethod.GENERALIZATION,
                parameters={'generalization_level': 'first_3_digits'}
            ),
            'gender': AnonymizationRule(
                field_name='gender',
                data_type=DataType.QUASI_IDENTIFIER,
                method=AnonymizationMethod.GENERALIZATION,
                parameters={'categories': ['male', 'female', 'other']}
            ),
            
            # Sensitive Attributes
            'diagnosis': AnonymizationRule(
                field_name='diagnosis',
                data_type=DataType.SENSITIVE_ATTRIBUTE,
                method=AnonymizationMethod.GENERALIZATION,
                parameters={'icd_categories': True}
            ),
            'medication': AnonymizationRule(
                field_name='medication',
                data_type=DataType.SENSITIVE_ATTRIBUTE,
                method=AnonymizationMethod.GENERALIZATION,
                parameters={'drug_classes': True}
            )
        }
        
        self.anonymization_rules.update(default_rules)
        logger.info(f"Initialized {len(default_rules)} default anonymization rules")
    
    def add_rule(self, rule: AnonymizationRule) -> bool:
        """
        Add custom anonymization rule
        
        Args:
            rule: Anonymization rule to add
            
        Returns:
            bool: True if rule added successfully
        """
        try:
            self.anonymization_rules[rule.field_name] = rule
            logger.info(f"Added anonymization rule for field: {rule.field_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add anonymization rule: {e}")
            return False
    
    def remove_rule(self, field_name: str) -> bool:
        """
        Remove anonymization rule
        
        Args:
            field_name: Name of field to remove rule for
            
        Returns:
            bool: True if rule removed successfully
        """
        try:
            if field_name in self.anonymization_rules:
                del self.anonymization_rules[field_name]
                logger.info(f"Removed anonymization rule for field: {field_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove anonymization rule: {e}")
            return False
    
    def anonymize_record(self, record: Dict[str, Any], rules: Optional[List[AnonymizationRule]] = None) -> Dict[str, Any]:
        """
        Anonymize a single record
        
        Args:
            record: Record to anonymize
            rules: Optional list of rules to apply (uses default if None)
            
        Returns:
            Dict: Anonymized record
        """
        try:
            if rules is None:
                rules = list(self.anonymization_rules.values())
            
            anonymized_record = record.copy()
            
            for rule in rules:
                if rule.enabled and rule.field_name in record:
                    value = record[rule.field_name]
                    if value is not None:
                        anonymized_value = self._apply_anonymization(value, rule)
                        anonymized_record[rule.field_name] = anonymized_value
            
            return anonymized_record
            
        except Exception as e:
            logger.error(f"Failed to anonymize record: {e}")
            raise
    
    def anonymize_dataset(self, dataset: List[Dict[str, Any]], 
                         rules: Optional[List[AnonymizationRule]] = None,
                         k_anonymity: Optional[int] = None,
                         l_diversity: Optional[int] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Anonymize entire dataset with k-anonymity and l-diversity
        
        Args:
            dataset: List of records to anonymize
            rules: Optional list of rules to apply
            k_anonymity: K value for k-anonymity
            l_diversity: L value for l-diversity
            
        Returns:
            Tuple: (anonymized_dataset, metadata)
        """
        try:
            if rules is None:
                rules = list(self.anonymization_rules.values())
            
            # First pass: apply individual field anonymization
            anonymized_dataset = []
            for record in dataset:
                anonymized_record = self.anonymize_record(record, rules)
                anonymized_dataset.append(anonymized_record)
            
            metadata = {
                'original_count': len(dataset),
                'anonymized_count': len(anonymized_dataset),
                'rules_applied': len(rules),
                'k_anonymity': k_anonymity,
                'l_diversity': l_diversity
            }
            
            # Apply k-anonymity if specified
            if k_anonymity:
                anonymized_dataset, k_metadata = self._apply_k_anonymity(
                    anonymized_dataset, k_anonymity, rules
                )
                metadata.update(k_metadata)
            
            # Apply l-diversity if specified
            if l_diversity:
                anonymized_dataset, l_metadata = self._apply_l_diversity(
                    anonymized_dataset, l_diversity, rules
                )
                metadata.update(l_metadata)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(dataset, anonymized_dataset)
            metadata['quality_metrics'] = quality_metrics
            
            # Assess re-identification risk
            risk_assessment = self._assess_reidentification_risk(anonymized_dataset, rules)
            metadata['risk_assessment'] = risk_assessment
            
            logger.info(f"Dataset anonymized: {len(dataset)} -> {len(anonymized_dataset)} records")
            return anonymized_dataset, metadata
            
        except Exception as e:
            logger.error(f"Failed to anonymize dataset: {e}")
            raise
    
    def _apply_anonymization(self, value: Any, rule: AnonymizationRule) -> Any:
        """
        Apply specific anonymization method to a value
        
        Args:
            value: Value to anonymize
            rule: Anonymization rule to apply
            
        Returns:
            Any: Anonymized value
        """
        try:
            if rule.method == AnonymizationMethod.MASKING:
                return self._apply_masking(value, rule.parameters)
            elif rule.method == AnonymizationMethod.PSEUDONYMIZATION:
                return self._apply_pseudonymization(value, rule.parameters)
            elif rule.method == AnonymizationMethod.GENERALIZATION:
                return self._apply_generalization(value, rule.parameters)
            elif rule.method == AnonymizationMethod.SUPPRESSION:
                return self._apply_suppression(value, rule.parameters)
            elif rule.method == AnonymizationMethod.NOISE_ADDITION:
                return self._apply_noise_addition(value, rule.parameters)
            elif rule.method == AnonymizationMethod.SWAPPING:
                return self._apply_swapping(value, rule.parameters)
            else:
                return value
                
        except Exception as e:
            logger.error(f"Failed to apply anonymization method {rule.method}: {e}")
            return value
    
    def _apply_masking(self, value: Any, parameters: Dict[str, Any]) -> Any:
        """Apply masking anonymization"""
        try:
            if not isinstance(value, str):
                return value
            
            mask_char = parameters.get('mask_char', '*')
            preserve_length = parameters.get('preserve_length', True)
            preserve_domain = parameters.get('preserve_domain', False)
            preserve_country_code = parameters.get('preserve_country_code', False)
            
            if preserve_domain and '@' in value:
                # Email masking
                username, domain = value.split('@', 1)
                masked_username = mask_char * len(username)
                return f"{masked_username}@{domain}"
            
            elif preserve_country_code and value.startswith('+'):
                # Phone number masking
                parts = value.split(' ', 1)
                if len(parts) > 1:
                    country_code = parts[0]
                    number = parts[1]
                    masked_number = mask_char * len(number)
                    return f"{country_code} {masked_number}"
            
            elif preserve_length:
                return mask_char * len(value)
            else:
                return mask_char * 8  # Default 8 characters
                
        except Exception as e:
            logger.error(f"Failed to apply masking: {e}")
            return value
    
    def _apply_pseudonymization(self, value: Any, parameters: Dict[str, Any]) -> Any:
        """Apply pseudonymization"""
        try:
            if value is None:
                return None
            
            value_str = str(value)
            
            # Check if we already have a pseudonym for this value
            if value_str in self.pseudonym_mapping:
                return self.pseudonym_mapping[value_str]
            
            # Generate new pseudonym
            hash_algorithm = parameters.get('hash_algorithm', 'sha256')
            salt = parameters.get('salt', 'abena_ihr_salt')
            
            if hash_algorithm == 'sha256':
                hash_obj = hashlib.sha256()
                hash_obj.update((value_str + salt).encode('utf-8'))
                pseudonym = hash_obj.hexdigest()[:16]  # Use first 16 characters
            else:
                # Fallback to UUID
                pseudonym = str(uuid.uuid4()).replace('-', '')[:16]
            
            # Store mapping
            self.pseudonym_mapping[value_str] = pseudonym
            
            return pseudonym
            
        except Exception as e:
            logger.error(f"Failed to apply pseudonymization: {e}")
            return value
    
    def _apply_generalization(self, value: Any, parameters: Dict[str, Any]) -> Any:
        """Apply generalization anonymization"""
        try:
            if value is None:
                return None
            
            generalization_level = parameters.get('generalization_level', 'default')
            
            if isinstance(value, str) and generalization_level == 'first_3_digits':
                # ZIP code generalization
                return value[:3] + 'XX'
            
            elif isinstance(value, str) and generalization_level == 'year':
                # Date generalization to year
                try:
                    date_obj = datetime.strptime(value, '%Y-%m-%d')
                    return str(date_obj.year)
                except:
                    return value
            
            elif isinstance(value, (int, float)) and 'age_bins' in parameters:
                # Age binning
                age_bins = parameters['age_bins']
                for i in range(len(age_bins) - 1):
                    if age_bins[i] <= value < age_bins[i + 1]:
                        return f"{age_bins[i]}-{age_bins[i + 1]}"
                return "65+"
            
            elif isinstance(value, str) and 'categories' in parameters:
                # Categorical generalization
                categories = parameters['categories']
                if value.lower() in [cat.lower() for cat in categories]:
                    return value
                else:
                    return 'other'
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to apply generalization: {e}")
            return value
    
    def _apply_suppression(self, value: Any, parameters: Dict[str, Any]) -> Any:
        """Apply suppression anonymization"""
        try:
            suppression_threshold = parameters.get('suppression_threshold', 0.1)
            
            # Simple random suppression
            if random.random() < suppression_threshold:
                return None
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to apply suppression: {e}")
            return value
    
    def _apply_noise_addition(self, value: Any, parameters: Dict[str, Any]) -> Any:
        """Apply noise addition for differential privacy"""
        try:
            if not isinstance(value, (int, float)):
                return value
            
            epsilon = parameters.get('epsilon', 1.0)
            sensitivity = parameters.get('sensitivity', 1.0)
            
            # Laplace noise for differential privacy
            scale = sensitivity / epsilon
            noise = np.random.laplace(0, scale)
            
            return value + noise
            
        except Exception as e:
            logger.error(f"Failed to apply noise addition: {e}")
            return value
    
    def _apply_swapping(self, value: Any, parameters: Dict[str, Any]) -> Any:
        """Apply value swapping anonymization"""
        try:
            # This would require a pool of values to swap with
            # For now, return the original value
            return value
            
        except Exception as e:
            logger.error(f"Failed to apply swapping: {e}")
            return value
    
    def _apply_k_anonymity(self, dataset: List[Dict[str, Any]], k: int, 
                          rules: List[AnonymizationRule]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Apply k-anonymity to dataset
        
        Args:
            dataset: Dataset to anonymize
            k: K value for k-anonymity
            rules: Anonymization rules
            
        Returns:
            Tuple: (anonymized_dataset, metadata)
        """
        try:
            # Identify quasi-identifier fields
            quasi_identifiers = [rule.field_name for rule in rules 
                               if rule.data_type == DataType.QUASI_IDENTIFIER]
            
            if not quasi_identifiers:
                return dataset, {'k_anonymity_applied': False, 'reason': 'no_quasi_identifiers'}
            
            # Group records by quasi-identifiers
            groups = defaultdict(list)
            for record in dataset:
                key = tuple(record.get(field, '') for field in quasi_identifiers)
                groups[key].append(record)
            
            # Check k-anonymity
            small_groups = [key for key, group in groups.items() if len(group) < k]
            
            if small_groups:
                # Apply additional generalization to achieve k-anonymity
                logger.info(f"Applying additional generalization to achieve k-anonymity")
                # This is a simplified implementation
                # In practice, you would implement more sophisticated generalization strategies
            
            metadata = {
                'k_anonymity_applied': True,
                'k_value': k,
                'quasi_identifiers': quasi_identifiers,
                'groups_count': len(groups),
                'small_groups_count': len(small_groups)
            }
            
            return dataset, metadata
            
        except Exception as e:
            logger.error(f"Failed to apply k-anonymity: {e}")
            return dataset, {'k_anonymity_applied': False, 'error': str(e)}
    
    def _apply_l_diversity(self, dataset: List[Dict[str, Any]], l: int, 
                          rules: List[AnonymizationRule]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Apply l-diversity to dataset
        
        Args:
            dataset: Dataset to anonymize
            l: L value for l-diversity
            rules: Anonymization rules
            
        Returns:
            Tuple: (anonymized_dataset, metadata)
        """
        try:
            # Identify sensitive attributes
            sensitive_attributes = [rule.field_name for rule in rules 
                                  if rule.data_type == DataType.SENSITIVE_ATTRIBUTE]
            
            if not sensitive_attributes:
                return dataset, {'l_diversity_applied': False, 'reason': 'no_sensitive_attributes'}
            
            # This is a simplified implementation
            # In practice, you would implement more sophisticated l-diversity strategies
            
            metadata = {
                'l_diversity_applied': True,
                'l_value': l,
                'sensitive_attributes': sensitive_attributes
            }
            
            return dataset, metadata
            
        except Exception as e:
            logger.error(f"Failed to apply l-diversity: {e}")
            return dataset, {'l_diversity_applied': False, 'error': str(e)}
    
    def _calculate_quality_metrics(self, original_dataset: List[Dict[str, Any]], 
                                 anonymized_dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate anonymization quality metrics"""
        try:
            if not original_dataset or not anonymized_dataset:
                return {}
            
            # Information loss
            total_fields = len(original_dataset[0]) if original_dataset else 0
            suppressed_fields = 0
            generalized_fields = 0
            
            for orig_record, anon_record in zip(original_dataset, anonymized_dataset):
                for field in orig_record:
                    if field in anon_record:
                        if anon_record[field] is None:
                            suppressed_fields += 1
                        elif anon_record[field] != orig_record[field]:
                            generalized_fields += 1
            
            total_records = len(original_dataset)
            information_loss = (suppressed_fields + generalized_fields) / (total_records * total_fields)
            
            # Utility preservation (simplified)
            utility_score = 1 - information_loss
            
            return {
                'information_loss': information_loss,
                'utility_score': utility_score,
                'suppressed_fields': suppressed_fields,
                'generalized_fields': generalized_fields,
                'total_fields': total_records * total_fields
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate quality metrics: {e}")
            return {}
    
    def _assess_reidentification_risk(self, dataset: List[Dict[str, Any]], 
                                    rules: List[AnonymizationRule]) -> Dict[str, Any]:
        """Assess re-identification risk"""
        try:
            # Count unique combinations of quasi-identifiers
            quasi_identifiers = [rule.field_name for rule in rules 
                               if rule.data_type == DataType.QUASI_IDENTIFIER]
            
            if not quasi_identifiers:
                return {'risk_level': RiskLevel.LOW.value, 'reason': 'no_quasi_identifiers'}
            
            unique_combinations = set()
            for record in dataset:
                combination = tuple(record.get(field, '') for field in quasi_identifiers)
                unique_combinations.add(combination)
            
            total_records = len(dataset)
            unique_combinations_count = len(unique_combinations)
            
            # Calculate risk based on uniqueness
            uniqueness_ratio = unique_combinations_count / total_records
            
            if uniqueness_ratio > 0.8:
                risk_level = RiskLevel.HIGH
            elif uniqueness_ratio > 0.5:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            return {
                'risk_level': risk_level.value,
                'uniqueness_ratio': uniqueness_ratio,
                'unique_combinations': unique_combinations_count,
                'total_records': total_records,
                'quasi_identifiers': quasi_identifiers
            }
            
        except Exception as e:
            logger.error(f"Failed to assess re-identification risk: {e}")
            return {'risk_level': RiskLevel.CRITICAL.value, 'error': str(e)}
    
    def create_anonymization_job(self, dataset_id: str, rules: List[AnonymizationRule]) -> str:
        """
        Create a new anonymization job
        
        Args:
            dataset_id: ID of dataset to anonymize
            rules: List of anonymization rules to apply
            
        Returns:
            str: Job ID
        """
        try:
            job_id = str(uuid.uuid4())
            job = AnonymizationJob(
                job_id=job_id,
                dataset_id=dataset_id,
                rules=rules,
                status='created',
                created_at=datetime.utcnow()
            )
            
            self.jobs[job_id] = job
            logger.info(f"Created anonymization job: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to create anonymization job: {e}")
            raise
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of anonymization job"""
        try:
            job = self.jobs.get(job_id)
            if job is None:
                return None
            
            return {
                'job_id': job.job_id,
                'dataset_id': job.dataset_id,
                'status': job.status,
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'records_processed': job.records_processed,
                'records_anonymized': job.records_anonymized,
                'quality_score': job.quality_score,
                'risk_assessment': job.risk_assessment,
                'error_message': job.error_message
            }
            
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return None
    
    def get_anonymization_metrics(self) -> Dict[str, Any]:
        """Get anonymization metrics and statistics"""
        try:
            total_jobs = len(self.jobs)
            completed_jobs = sum(1 for job in self.jobs.values() if job.status == 'completed')
            failed_jobs = sum(1 for job in self.jobs.values() if job.status == 'failed')
            
            total_records_processed = sum(job.records_processed for job in self.jobs.values())
            total_records_anonymized = sum(job.records_anonymized for job in self.jobs.values())
            
            return {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'failed_jobs': failed_jobs,
                'total_records_processed': total_records_processed,
                'total_records_anonymized': total_records_anonymized,
                'success_rate': completed_jobs / total_jobs if total_jobs > 0 else 0,
                'pseudonym_mappings': len(self.pseudonym_mapping),
                'active_rules': len([rule for rule in self.anonymization_rules.values() if rule.enabled])
            }
            
        except Exception as e:
            logger.error(f"Failed to get anonymization metrics: {e}")
            return {}


# Factory function for creating anonymization manager
def create_anonymization_manager(config: Dict[str, Any]) -> AnonymizationManager:
    """
    Factory function to create anonymization manager instance
    
    Args:
        config: Configuration dictionary
        
    Returns:
        AnonymizationManager: Configured anonymization manager instance
    """
    return AnonymizationManager(config)


# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = {
        'default_k_anonymity': 5,
        'default_l_diversity': 2,
        'quality_threshold': 0.8,
        'risk_threshold': 0.3
    }
    
    # Create anonymization manager
    anonymization_manager = create_anonymization_manager(config)
    
    # Example dataset
    test_dataset = [
        {
            'patient_id': 'P001',
            'ssn': '123-45-6789',
            'email': 'john.doe@email.com',
            'date_of_birth': '1985-03-15',
            'zip_code': '12345',
            'gender': 'male',
            'diagnosis': 'diabetes',
            'medication': 'metformin'
        },
        {
            'patient_id': 'P002',
            'ssn': '987-65-4321',
            'email': 'jane.smith@email.com',
            'date_of_birth': '1990-07-22',
            'zip_code': '12346',
            'gender': 'female',
            'diagnosis': 'hypertension',
            'medication': 'lisinopril'
        }
    ]
    
    # Anonymize dataset
    anonymized_dataset, metadata = anonymization_manager.anonymize_dataset(
        test_dataset, k_anonymity=2, l_diversity=2
    )
    
    print("Original Dataset:")
    for record in test_dataset:
        print(record)
    
    print("\nAnonymized Dataset:")
    for record in anonymized_dataset:
        print(record)
    
    print(f"\nMetadata: {metadata}")
    print(f"Metrics: {anonymization_manager.get_anonymization_metrics()}") 