"""
Abena SDK Data Handling

Centralized data handling for the Abena SDK including FHIR conversion,
data transformation, and EMR integration. All modules should use this
for data operations instead of implementing their own.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import requests

from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.identifier import Identifier
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.quantity import Quantity

from .exceptions import DataTransformationError, FHIRConversionError, ValidationError
from .config import AbenaConfig


@dataclass
class DataRequest:
    """Data request with context"""
    resource_type: str
    resource_id: str
    user_id: str
    purpose: str
    scope: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


@dataclass
class DataResponse:
    """Data response with metadata"""
    data: Any
    resource_type: str
    resource_id: str
    timestamp: datetime
    version: str
    source: str
    audit_trail: Optional[Dict[str, Any]] = None


class DataTransformer:
    """Centralized data transformation for Abena SDK"""
    
    def __init__(self, config: AbenaConfig):
        self.config = config
        self._data_service_url = config.get_api_url("data")
        self._mapping_cache: Dict[str, Any] = {}
    
    def transform_emr_data(self, source_data: Dict[str, Any], 
                          source_system: str, target_format: str = "FHIR") -> Dict[str, Any]:
        """Transform EMR data to target format"""
        try:
            response = requests.post(
                f"{self._data_service_url}/transform",
                json={
                    "source_data": source_data,
                    "source_system": source_system,
                    "target_format": target_format,
                    "fhir_version": self.config.fhir_version
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()["transformed_data"]
            
        except requests.RequestException as e:
            raise DataTransformationError(f"Data transformation failed: {str(e)}")
    
    def get_mapping_config(self, source_system: str, target_system: str, 
                          version: str = "latest") -> Dict[str, Any]:
        """Get data mapping configuration"""
        cache_key = f"{source_system}:{target_system}:{version}"
        
        if cache_key in self._mapping_cache:
            return self._mapping_cache[cache_key]
        
        try:
            response = requests.get(
                f"{self._data_service_url}/mappings/{source_system}/{target_system}/{version}",
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            mapping_config = response.json()
            self._mapping_cache[cache_key] = mapping_config
            
            return mapping_config
            
        except requests.RequestException as e:
            raise DataTransformationError(f"Failed to get mapping config: {str(e)}")
    
    def validate_data(self, data: Dict[str, Any], schema_type: str) -> bool:
        """Validate data against schema"""
        try:
            response = requests.post(
                f"{self._data_service_url}/validate",
                json={
                    "data": data,
                    "schema_type": schema_type
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()["is_valid"]
            
        except requests.RequestException as e:
            raise ValidationError(f"Data validation failed: {str(e)}")
    
    def clean_data(self, data: Dict[str, Any], cleaning_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Clean and normalize data"""
        try:
            response = requests.post(
                f"{self._data_service_url}/clean",
                json={
                    "data": data,
                    "cleaning_rules": cleaning_rules or {}
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()["cleaned_data"]
            
        except requests.RequestException as e:
            raise DataTransformationError(f"Data cleaning failed: {str(e)}")


class FHIRConverter:
    """Centralized FHIR conversion for Abena SDK"""
    
    def __init__(self, config: AbenaConfig):
        self.config = config
        self._fhir_service_url = config.get_api_url("fhir")
        self._loinc_codes = self._initialize_loinc_codes()
    
    def _initialize_loinc_codes(self) -> Dict[str, str]:
        """Initialize LOINC codes for common observations"""
        return {
            "glucose": "2339-0",
            "blood_pressure": "85354-9",
            "heart_rate": "8867-4",
            "temperature": "8310-5",
            "weight": "29463-7",
            "height": "8302-2",
            "bmi": "39156-5"
        }
    
    def create_patient_resource(self, patient_data: Dict[str, Any]) -> Patient:
        """Create FHIR Patient resource"""
        try:
            # Validate required fields
            required_fields = ["id", "first_name", "last_name", "gender", "birth_date"]
            for field in required_fields:
                if field not in patient_data:
                    raise ValidationError(f"Missing required field: {field}")
            
            # Create patient resource
            patient = Patient(
                id=patient_data["id"],
                identifier=[
                    Identifier(
                        system="https://hospital.com/patients",
                        value=patient_data["id"]
                    )
                ],
                name=[
                    {
                        "use": "official",
                        "family": patient_data["last_name"],
                        "given": [patient_data["first_name"]]
                    }
                ],
                gender=patient_data["gender"],
                birth_date=patient_data["birth_date"]
            )
            
            # Add optional fields
            if "address" in patient_data:
                patient.address = [patient_data["address"]]
            
            if "telecom" in patient_data:
                patient.telecom = patient_data["telecom"]
            
            return patient
            
        except Exception as e:
            raise FHIRConversionError(f"Failed to create Patient resource: {str(e)}")
    
    def create_observation_resource(self, obs_data: Dict[str, Any], 
                                  patient_id: str) -> Observation:
        """Create FHIR Observation resource"""
        try:
            # Validate required fields
            required_fields = ["id", "type", "value", "unit", "date"]
            for field in required_fields:
                if field not in obs_data:
                    raise ValidationError(f"Missing required field: {field}")
            
            # Get LOINC code
            loinc_code = self._loinc_codes.get(obs_data["type"], "unknown")
            
            # Create observation resource
            observation = Observation(
                id=obs_data["id"],
                status="final",
                category=[
                    CodeableConcept(
                        coding=[
                            Coding(
                                system="http://terminology.hl7.org/CodeSystem/observation-category",
                                code="vital-signs",
                                display="Vital Signs"
                            )
                        ]
                    )
                ],
                code=CodeableConcept(
                    coding=[
                        Coding(
                            system="http://loinc.org",
                            code=loinc_code,
                            display=obs_data["type"].replace("_", " ").title()
                        )
                    ]
                ),
                subject={
                    "reference": f"Patient/{patient_id}"
                },
                effective_date_time=obs_data["date"],
                value_quantity=Quantity(
                    value=obs_data["value"],
                    unit=obs_data["unit"],
                    system="http://unitsofmeasure.org",
                    code=self._get_ucum_code(obs_data["unit"])
                )
            )
            
            return observation
            
        except Exception as e:
            raise FHIRConversionError(f"Failed to create Observation resource: {str(e)}")
    
    def _get_ucum_code(self, unit: str) -> str:
        """Get UCUM code for unit"""
        ucum_mapping = {
            "mg/dL": "mg/dL",
            "mmol/L": "mmol/L",
            "mmHg": "mm[Hg]",
            "bpm": "/min",
            "C": "Cel",
            "F": "[degF]",
            "kg": "kg",
            "lb": "[lb_av]",
            "cm": "cm",
            "in": "[in_i]"
        }
        return ucum_mapping.get(unit, unit)
    
    def convert_to_fhir(self, data: Dict[str, Any], resource_type: str) -> Dict[str, Any]:
        """Convert data to FHIR format"""
        try:
            response = requests.post(
                f"{self._fhir_service_url}/convert",
                json={
                    "data": data,
                    "resource_type": resource_type,
                    "fhir_version": self.config.fhir_version
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()["fhir_resource"]
            
        except requests.RequestException as e:
            raise FHIRConversionError(f"FHIR conversion failed: {str(e)}")
    
    def validate_fhir_resource(self, resource: Dict[str, Any], 
                              resource_type: str) -> bool:
        """Validate FHIR resource"""
        try:
            response = requests.post(
                f"{self._fhir_service_url}/validate",
                json={
                    "resource": resource,
                    "resource_type": resource_type,
                    "fhir_version": self.config.fhir_version
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()["is_valid"]
            
        except requests.RequestException as e:
            raise FHIRConversionError(f"FHIR validation failed: {str(e)}")
    
    def get_fhir_schema(self, resource_type: str) -> Dict[str, Any]:
        """Get FHIR schema for resource type"""
        try:
            response = requests.get(
                f"{self._fhir_service_url}/schemas/{resource_type}",
                params={"version": self.config.fhir_version},
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            raise FHIRConversionError(f"Failed to get FHIR schema: {str(e)}") 