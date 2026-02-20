"""
ETL (Extract, Transform, Load) Processor for Healthcare Data
===========================================================

This module provides ETL capabilities for processing healthcare data from various sources
and loading it into the analytics system.
"""

import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import asyncio
import aiohttp
import sqlalchemy
from sqlalchemy import create_engine, text
import redis
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger(__name__)

class ETLProcessor:
    """ETL processor for healthcare data"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0),
            decode_responses=True
        )
        
        # Database connections
        self.source_engine = None
        self.target_engine = None
        
        if 'source_db' in config:
            self.source_engine = create_engine(config['source_db'])
        if 'target_db' in config:
            self.target_engine = create_engine(config['target_db'])
            
    async def extract_from_api(self, api_config: Dict[str, Any]) -> pd.DataFrame:
        """Extract data from REST API"""
        try:
            url = api_config['url']
            headers = api_config.get('headers', {})
            params = api_config.get('params', {})
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return pd.DataFrame(data)
                    else:
                        raise Exception(f"API request failed with status {response.status}")
                        
        except Exception as e:
            logger.error(f"Error extracting data from API: {e}")
            raise
            
    def extract_from_database(self, query: str, engine: Optional[sqlalchemy.engine.Engine] = None) -> pd.DataFrame:
        """Extract data from database"""
        try:
            if engine is None:
                engine = self.source_engine
                
            if engine is None:
                raise ValueError("No database engine configured")
                
            with engine.connect() as connection:
                result = connection.execute(text(query))
                data = result.fetchall()
                columns = result.keys()
                return pd.DataFrame(data, columns=columns)
                
        except Exception as e:
            logger.error(f"Error extracting data from database: {e}")
            raise
            
    def extract_from_file(self, file_path: str, file_type: str = 'csv') -> pd.DataFrame:
        """Extract data from file"""
        try:
            if file_type.lower() == 'csv':
                return pd.read_csv(file_path)
            elif file_type.lower() == 'json':
                return pd.read_json(file_path)
            elif file_type.lower() == 'excel':
                return pd.read_excel(file_path)
            elif file_type.lower() == 'parquet':
                return pd.read_parquet(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            logger.error(f"Error extracting data from file: {e}")
            raise
            
    def transform_patient_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform patient data"""
        try:
            # Create a copy to avoid modifying original
            transformed_df = df.copy()
            
            # Standardize column names
            transformed_df.columns = [col.lower().replace(' ', '_') for col in transformed_df.columns]
            
            # Handle missing values
            numeric_columns = transformed_df.select_dtypes(include=[np.number]).columns
            transformed_df[numeric_columns] = transformed_df[numeric_columns].fillna(0)
            
            categorical_columns = transformed_df.select_dtypes(include=['object']).columns
            transformed_df[categorical_columns] = transformed_df[categorical_columns].fillna('unknown')
            
            # Convert data types
            if 'age' in transformed_df.columns:
                transformed_df['age'] = pd.to_numeric(transformed_df['age'], errors='coerce')
                
            if 'height_cm' in transformed_df.columns:
                transformed_df['height_cm'] = pd.to_numeric(transformed_df['height_cm'], errors='coerce')
                
            if 'weight_kg' in transformed_df.columns:
                transformed_df['weight_kg'] = pd.to_numeric(transformed_df['weight_kg'], errors='coerce')
                
            # Calculate BMI if height and weight are available
            if 'height_cm' in transformed_df.columns and 'weight_kg' in transformed_df.columns:
                transformed_df['bmi'] = transformed_df['weight_kg'] / ((transformed_df['height_cm'] / 100) ** 2)
                
            # Standardize gender values
            if 'gender' in transformed_df.columns:
                transformed_df['gender'] = transformed_df['gender'].str.lower()
                transformed_df['gender'] = transformed_df['gender'].map({
                    'm': 'male', 'male': 'male',
                    'f': 'female', 'female': 'female',
                    'o': 'other', 'other': 'other'
                }).fillna('unknown')
                
            # Standardize smoking status
            if 'smoking_status' in transformed_df.columns:
                transformed_df['smoking_status'] = transformed_df['smoking_status'].str.lower()
                transformed_df['smoking_status'] = transformed_df['smoking_status'].map({
                    'current': 'current',
                    'former': 'former',
                    'never': 'never',
                    'ex': 'former'
                }).fillna('unknown')
                
            # Add timestamp
            transformed_df['processed_at'] = datetime.now()
            
            return transformed_df
            
        except Exception as e:
            logger.error(f"Error transforming patient data: {e}")
            raise
            
    def transform_lab_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform laboratory data"""
        try:
            transformed_df = df.copy()
            
            # Standardize column names
            transformed_df.columns = [col.lower().replace(' ', '_') for col in transformed_df.columns]
            
            # Convert lab values to numeric
            lab_value_columns = [col for col in transformed_df.columns if 'value' in col or 'result' in col]
            for col in lab_value_columns:
                transformed_df[col] = pd.to_numeric(transformed_df[col], errors='coerce')
                
            # Handle missing values
            transformed_df = transformed_df.fillna(0)
            
            # Add timestamp
            transformed_df['processed_at'] = datetime.now()
            
            return transformed_df
            
        except Exception as e:
            logger.error(f"Error transforming lab data: {e}")
            raise
            
    def transform_vital_signs(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform vital signs data"""
        try:
            transformed_df = df.copy()
            
            # Standardize column names
            transformed_df.columns = [col.lower().replace(' ', '_') for col in transformed_df.columns]
            
            # Convert vital signs to numeric
            vital_signs_columns = ['heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
                                 'temperature', 'oxygen_saturation', 'respiratory_rate']
            
            for col in vital_signs_columns:
                if col in transformed_df.columns:
                    transformed_df[col] = pd.to_numeric(transformed_df[col], errors='coerce')
                    
            # Handle missing values
            transformed_df = transformed_df.fillna(0)
            
            # Add timestamp
            transformed_df['processed_at'] = datetime.now()
            
            return transformed_df
            
        except Exception as e:
            logger.error(f"Error transforming vital signs: {e}")
            raise
            
    def load_to_database(self, df: pd.DataFrame, table_name: str, 
                        engine: Optional[sqlalchemy.engine.Engine] = None,
                        if_exists: str = 'append') -> bool:
        """Load data to database"""
        try:
            if engine is None:
                engine = self.target_engine
                
            if engine is None:
                raise ValueError("No target database engine configured")
                
            df.to_sql(table_name, engine, if_exists=if_exists, index=False)
            logger.info(f"Successfully loaded {len(df)} rows to table {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data to database: {e}")
            raise
            
    def load_to_redis(self, df: pd.DataFrame, key_prefix: str, 
                     expire_seconds: int = 3600) -> bool:
        """Load data to Redis cache"""
        try:
            for index, row in df.iterrows():
                key = f"{key_prefix}:{index}"
                value = json.dumps(row.to_dict())
                self.redis_client.setex(key, expire_seconds, value)
                
            logger.info(f"Successfully loaded {len(df)} rows to Redis with prefix {key_prefix}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data to Redis: {e}")
            raise
            
    def load_to_file(self, df: pd.DataFrame, file_path: str, 
                    file_type: str = 'csv') -> bool:
        """Load data to file"""
        try:
            if file_type.lower() == 'csv':
                df.to_csv(file_path, index=False)
            elif file_type.lower() == 'json':
                df.to_json(file_path, orient='records', indent=2)
            elif file_type.lower() == 'excel':
                df.to_excel(file_path, index=False)
            elif file_type.lower() == 'parquet':
                df.to_parquet(file_path, index=False)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
            logger.info(f"Successfully saved data to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving data to file: {e}")
            raise
            
    async def process_patient_data_pipeline(self, source_config: Dict[str, Any]) -> bool:
        """Complete ETL pipeline for patient data"""
        try:
            # Extract
            if source_config['type'] == 'api':
                df = await self.extract_from_api(source_config)
            elif source_config['type'] == 'database':
                df = self.extract_from_database(source_config['query'])
            elif source_config['type'] == 'file':
                df = self.extract_from_file(source_config['file_path'], source_config.get('file_type', 'csv'))
            else:
                raise ValueError(f"Unsupported source type: {source_config['type']}")
                
            # Transform
            transformed_df = self.transform_patient_data(df)
            
            # Load
            if 'target_database' in source_config:
                self.load_to_database(transformed_df, source_config['target_table'])
                
            if 'target_redis' in source_config:
                self.load_to_redis(transformed_df, source_config['redis_key_prefix'])
                
            if 'target_file' in source_config:
                self.load_to_file(transformed_df, source_config['target_file_path'])
                
            logger.info("Patient data ETL pipeline completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in patient data ETL pipeline: {e}")
            raise
            
    def validate_data_quality(self, df: pd.DataFrame, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data quality based on rules"""
        try:
            validation_results = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': {},
                'data_type_issues': {},
                'range_violations': {},
                'duplicate_rows': len(df[df.duplicated()]),
                'overall_score': 0
            }
            
            # Check missing values
            for column in df.columns:
                missing_count = df[column].isnull().sum()
                missing_percentage = (missing_count / len(df)) * 100
                validation_results['missing_values'][column] = {
                    'count': missing_count,
                    'percentage': missing_percentage
                }
                
            # Check data types
            for column, expected_type in rules.get('data_types', {}).items():
                if column in df.columns:
                    actual_type = str(df[column].dtype)
                    if actual_type != expected_type:
                        validation_results['data_type_issues'][column] = {
                            'expected': expected_type,
                            'actual': actual_type
                        }
                        
            # Check value ranges
            for column, range_rule in rules.get('value_ranges', {}).items():
                if column in df.columns:
                    min_val = df[column].min()
                    max_val = df[column].max()
                    
                    if 'min' in range_rule and min_val < range_rule['min']:
                        validation_results['range_violations'][column] = {
                            'type': 'below_minimum',
                            'value': min_val,
                            'threshold': range_rule['min']
                        }
                        
                    if 'max' in range_rule and max_val > range_rule['max']:
                        validation_results['range_violations'][column] = {
                            'type': 'above_maximum',
                            'value': max_val,
                            'threshold': range_rule['max']
                        }
                        
            # Calculate overall quality score
            total_checks = len(df.columns) * 3  # missing, type, range
            passed_checks = total_checks
            
            # Deduct for missing values > 10%
            for column, missing_info in validation_results['missing_values'].items():
                if missing_info['percentage'] > 10:
                    passed_checks -= 1
                    
            # Deduct for data type issues
            passed_checks -= len(validation_results['data_type_issues'])
            
            # Deduct for range violations
            passed_checks -= len(validation_results['range_violations'])
            
            validation_results['overall_score'] = (passed_checks / total_checks) * 100
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating data quality: {e}")
            raise
            
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get ETL processing statistics"""
        try:
            stats = {
                'last_processed': datetime.now(),
                'redis_keys': len(self.redis_client.keys('*')),
                'source_connection': self.source_engine is not None,
                'target_connection': self.target_engine is not None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Configuration
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'source_db': 'postgresql://user:password@localhost/source_db',
        'target_db': 'postgresql://user:password@localhost/target_db'
    }
    
    # Create ETL processor
    etl = ETLProcessor(config)
    
    # Example source configuration
    source_config = {
        'type': 'file',
        'file_path': 'patient_data.csv',
        'file_type': 'csv',
        'target_database': True,
        'target_table': 'patients',
        'target_redis': True,
        'redis_key_prefix': 'patient'
    }
    
    # Run pipeline
    # asyncio.run(etl.process_patient_data_pipeline(source_config)) 