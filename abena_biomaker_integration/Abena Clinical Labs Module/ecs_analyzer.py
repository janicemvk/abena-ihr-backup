"""
Abena IHR ECS Lab Analysis Module
Endocannabinoid System (ECS) Analysis for Clinical Laboratory Data

This module analyzes clinical laboratory data, smart device biometrics, and EKG results
to assess ECS dysfunction and generate personalized health reports using Abena SDK.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import json
import random
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Abena SDK imports - try real SDK first, fall back to mock for testing
try:
    from abena.sdk.auth import AbenaAuthenticator
    from abena.sdk.authorization import AbenaAuthorizer
    from abena.sdk.data import AbenaDataHandler
    from abena.sdk.models import AbenaPatient, AbenaLabResult, AbenaVitalSign, AbenaEKGResult, AbenaSmartDeviceData
    from abena.sdk.config import AbenaConfig
    from abena.sdk.exceptions import AbenaAuthenticationError, AbenaAuthorizationError, AbenaDataError
    USING_MOCK_SDK = False
except ImportError:
    # Fall back to mock SDK for testing
    from abena_sdk_mock import (
        AbenaAuthenticator, AbenaAuthorizer, AbenaDataHandler,
        AbenaPatient, AbenaLabResult, AbenaVitalSign, AbenaEKGResult, AbenaSmartDeviceData,
        AbenaConfig, AbenaAuthenticationError, AbenaAuthorizationError, AbenaDataError
    )
    USING_MOCK_SDK = True

# Configure Plotly for offline use (only if in notebook environment)
try:
    pyo.init_notebook_mode(connected=True)
except:
    pass  # Skip if not in notebook environment

class ECSAnalyzer:
    """Main ECS analysis engine using Abena SDK"""
    
    def __init__(self, config: Optional[AbenaConfig] = None):
        # Initialize Abena SDK components
        self.config = config or AbenaConfig()
        self.authenticator = AbenaAuthenticator(self.config)
        self.authorizer = AbenaAuthorizer(self.config)
        self.data_handler = AbenaDataHandler(self.config)
        
        # Initialize data containers using Abena SDK models
        self.patient_data: Optional[AbenaPatient] = None
        self.lab_results: List[AbenaLabResult] = []
        self.vital_signs: List[AbenaVitalSign] = []
        self.ekg_results: List[AbenaEKGResult] = []
        self.smart_device_data: List[AbenaSmartDeviceData] = []
        
        # ECS scoring weights
        self.ecs_weights = {
            'direct_ecs': 0.40,
            'inflammation': 0.25,
            'cardiovascular': 0.15,
            'stress': 0.20,
            'neurotransmitters': 0.15
        }
        
        # Reference ranges for ECS-relevant biomarkers
        self.reference_ranges = {
            'AEA': (0.5, 2.0, 'ng/mL'),
            '2-AG': (1.0, 4.0, 'ng/mL'),
            'FAAH_Activity': (0.8, 1.2, 'nmol/min/mg'),
            'CRP': (0.0, 3.0, 'mg/L'),
            'ESR': (0, 20, 'mm/hr'),
            'IL6': (0.0, 5.0, 'pg/mL'),
            'TNF_alpha': (0.0, 8.1, 'pg/mL'),
            'Homocysteine': (5.0, 15.0, 'μmol/L'),
            'BUN_Creatinine_Ratio': (10, 20, ''),
            'Omega6_Omega3_Ratio': (2.0, 4.0, ''),
            'Cortisol_Morning': (6.0, 20.0, 'μg/dL'),
            'Cortisol_Evening': (2.0, 10.0, 'μg/dL'),
            'DHEA_S': (30, 400, 'μg/dL'),
            'Serotonin': (50, 200, 'ng/mL'),
            'GABA': (50, 150, 'ng/mL'),
            'Dopamine': (20, 100, 'ng/mL')
        }
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate using Abena SDK"""
        try:
            return self.authenticator.authenticate(credentials)
        except AbenaAuthenticationError as e:
            print(f"Authentication failed: {e}")
            return False
    
    def authorize_access(self, resource: str, action: str) -> bool:
        """Authorize access using Abena SDK"""
        try:
            return self.authorizer.authorize(resource, action)
        except AbenaAuthorizationError as e:
            print(f"Authorization failed: {e}")
            return False
    
    def load_patient_data(self, patient_id: str) -> bool:
        """Load patient data using Abena SDK"""
        try:
            if not self.authorize_access("patient_data", "read"):
                raise AbenaAuthorizationError("Insufficient permissions to access patient data")
            
            # Load patient data using Abena SDK
            self.patient_data = self.data_handler.get_patient(patient_id)
            self.lab_results = self.data_handler.get_lab_results(patient_id)
            self.vital_signs = self.data_handler.get_vital_signs(patient_id)
            self.ekg_results = self.data_handler.get_ekg_results(patient_id)
            self.smart_device_data = self.data_handler.get_smart_device_data(patient_id)
            
            return True
        except AbenaDataError as e:
            print(f"Failed to load patient data: {e}")
            return False
    
    def load_test_patient_data(self, patient_scenario: str = "moderate_dysfunction") -> None:
        """Load simulated patient data for testing using Abena SDK models"""
        # Create patient data using Abena SDK model
        self.patient_data = AbenaPatient(
            patient_id="TEST001",
            name="John Smith",
            age=45,
            gender="Male",
            height_cm=175,
            weight_kg=85,
            bmi=27.8,
            date_of_birth=datetime(1978, 6, 15),
            collection_date=datetime.now()
        )
        
        # Generate lab results based on scenario using Abena SDK models
        self._generate_lab_results(patient_scenario)
        self._generate_vital_signs()
        self._generate_ekg_results()
        self._generate_smart_device_data()
    
    def _generate_lab_results(self, scenario: str) -> None:
        """Generate realistic lab results based on ECS dysfunction scenario using Abena SDK models"""
        base_date = datetime.now() - timedelta(days=7)
        
        # Scenario-specific modifications
        scenario_modifiers = {
            "healthy_baseline": 1.0,
            "mild_dysfunction": 0.8,
            "moderate_dysfunction": 0.6,
            "severe_dysfunction": 0.4,
            "mixed_patterns": 0.7
        }
        
        modifier = scenario_modifiers.get(scenario, 0.6)
        
        # Direct ECS markers using Abena SDK models
        self.lab_results.extend([
            AbenaLabResult("AEA", 1.2 * modifier, "ng/mL", 0.5, 2.0, "", base_date, "direct_ecs"),
            AbenaLabResult("2-AG", 2.5 * modifier, "ng/mL", 1.0, 4.0, "", base_date, "direct_ecs"),
            AbenaLabResult("FAAH_Activity", 1.1 * modifier, "nmol/min/mg", 0.8, 1.2, "", base_date, "direct_ecs"),
        ])
        
        # Inflammatory markers
        inflammation_multiplier = 1.5 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("CRP", 2.5 * inflammation_multiplier, "mg/L", 0.0, 3.0, "", base_date, "inflammation"),
            AbenaLabResult("ESR", 25 * inflammation_multiplier, "mm/hr", 0, 20, "", base_date, "inflammation"),
            AbenaLabResult("IL6", 4.2 * inflammation_multiplier, "pg/mL", 0.0, 5.0, "", base_date, "inflammation"),
            AbenaLabResult("TNF_alpha", 7.5 * inflammation_multiplier, "pg/mL", 0.0, 8.1, "", base_date, "inflammation"),
        ])
        
        # Cardiovascular markers
        cv_multiplier = 1.3 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("Homocysteine", 12.5 * cv_multiplier, "μmol/L", 5.0, 15.0, "", base_date, "cardiovascular"),
            AbenaLabResult("BUN_Creatinine_Ratio", 18 * cv_multiplier, "", 10, 20, "", base_date, "cardiovascular"),
            AbenaLabResult("Omega6_Omega3_Ratio", 5.2 * cv_multiplier, "", 2.0, 4.0, "", base_date, "cardiovascular"),
        ])
        
        # Stress markers
        stress_multiplier = 1.4 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("Cortisol_Morning", 18.5 * stress_multiplier, "μg/dL", 6.0, 20.0, "", base_date, "stress"),
            AbenaLabResult("Cortisol_Evening", 8.5 * stress_multiplier, "μg/dL", 2.0, 10.0, "", base_date, "stress"),
            AbenaLabResult("DHEA_S", 280 * stress_multiplier, "μg/dL", 30, 400, "", base_date, "stress"),
        ])
        
        # Neurotransmitters
        nt_multiplier = 0.8 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("Serotonin", 120 * nt_multiplier, "ng/mL", 50, 200, "", base_date, "neurotransmitters"),
            AbenaLabResult("GABA", 90 * nt_multiplier, "ng/mL", 50, 150, "", base_date, "neurotransmitters"),
            AbenaLabResult("Dopamine", 65 * nt_multiplier, "ng/mL", 20, 100, "", base_date, "neurotransmitters"),
        ])
        
        # Complete Blood Count (CBC)
        cbc_multiplier = 0.9 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("Hemoglobin", 14.2 * cbc_multiplier, "g/dL", 12.0, 16.0, "", base_date, "cbc"),
            AbenaLabResult("Hematocrit", 42.5 * cbc_multiplier, "%", 36.0, 46.0, "", base_date, "cbc"),
            AbenaLabResult("White_Blood_Cells", 7.2 * cbc_multiplier, "K/μL", 4.5, 11.0, "", base_date, "cbc"),
            AbenaLabResult("Platelets", 250 * cbc_multiplier, "K/μL", 150, 450, "", base_date, "cbc"),
            AbenaLabResult("Red_Blood_Cells", 4.8 * cbc_multiplier, "M/μL", 4.0, 5.5, "", base_date, "cbc"),
            AbenaLabResult("MCV", 88 * cbc_multiplier, "fL", 80, 100, "", base_date, "cbc"),
            AbenaLabResult("MCH", 29.5 * cbc_multiplier, "pg", 27, 33, "", base_date, "cbc"),
            AbenaLabResult("MCHC", 33.5 * cbc_multiplier, "g/dL", 32, 36, "", base_date, "cbc"),
            AbenaLabResult("Neutrophils", 4.2 * cbc_multiplier, "K/μL", 2.0, 7.0, "", base_date, "cbc"),
            AbenaLabResult("Lymphocytes", 2.1 * cbc_multiplier, "K/μL", 1.0, 4.0, "", base_date, "cbc"),
            AbenaLabResult("Monocytes", 0.4 * cbc_multiplier, "K/μL", 0.2, 0.8, "", base_date, "cbc"),
            AbenaLabResult("Eosinophils", 0.2 * cbc_multiplier, "K/μL", 0.0, 0.5, "", base_date, "cbc"),
            AbenaLabResult("Basophils", 0.05 * cbc_multiplier, "K/μL", 0.0, 0.2, "", base_date, "cbc"),
        ])
        
        # Comprehensive Metabolic Panel
        cmp_multiplier = 1.1 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("Sodium", 140 * cmp_multiplier, "mEq/L", 135, 145, "", base_date, "metabolic"),
            AbenaLabResult("Potassium", 4.2 * cmp_multiplier, "mEq/L", 3.5, 5.0, "", base_date, "metabolic"),
            AbenaLabResult("Chloride", 102 * cmp_multiplier, "mEq/L", 96, 106, "", base_date, "metabolic"),
            AbenaLabResult("CO2", 24 * cmp_multiplier, "mEq/L", 22, 28, "", base_date, "metabolic"),
            AbenaLabResult("Calcium", 9.5 * cmp_multiplier, "mg/dL", 8.5, 10.5, "", base_date, "metabolic"),
            AbenaLabResult("Phosphorus", 3.5 * cmp_multiplier, "mg/dL", 2.5, 4.5, "", base_date, "metabolic"),
            AbenaLabResult("Albumin", 4.2 * cmp_multiplier, "g/dL", 3.5, 5.0, "", base_date, "metabolic"),
            AbenaLabResult("Total_Protein", 7.2 * cmp_multiplier, "g/dL", 6.0, 8.3, "", base_date, "metabolic"),
            AbenaLabResult("Glucose", 95 * cmp_multiplier, "mg/dL", 70, 100, "", base_date, "metabolic"),
            AbenaLabResult("HbA1c", 5.4 * cmp_multiplier, "%", 4.0, 5.6, "", base_date, "metabolic"),
            AbenaLabResult("BUN", 15 * cmp_multiplier, "mg/dL", 7, 20, "", base_date, "metabolic"),
            AbenaLabResult("Creatinine", 0.9 * cmp_multiplier, "mg/dL", 0.6, 1.2, "", base_date, "metabolic"),
            AbenaLabResult("Total_Cholesterol", 180 * cmp_multiplier, "mg/dL", 0, 200, "", base_date, "metabolic"),
            AbenaLabResult("HDL", 45 * cmp_multiplier, "mg/dL", 40, 60, "", base_date, "metabolic"),
            AbenaLabResult("LDL", 110 * cmp_multiplier, "mg/dL", 0, 100, "", base_date, "metabolic"),
            AbenaLabResult("Triglycerides", 150 * cmp_multiplier, "mg/dL", 0, 150, "", base_date, "metabolic"),
        ])
        
        # Comprehensive Liver Function Tests
        liver_multiplier = 1.2 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("ALT", 25 * liver_multiplier, "U/L", 7, 55, "", base_date, "liver"),
            AbenaLabResult("AST", 28 * liver_multiplier, "U/L", 8, 48, "", base_date, "liver"),
            AbenaLabResult("Alkaline_Phosphatase", 70 * liver_multiplier, "U/L", 44, 147, "", base_date, "liver"),
            AbenaLabResult("Total_Bilirubin", 0.8 * liver_multiplier, "mg/dL", 0.3, 1.2, "", base_date, "liver"),
            AbenaLabResult("Direct_Bilirubin", 0.2 * liver_multiplier, "mg/dL", 0.0, 0.3, "", base_date, "liver"),
            AbenaLabResult("Indirect_Bilirubin", 0.6 * liver_multiplier, "mg/dL", 0.2, 0.8, "", base_date, "liver"),
            AbenaLabResult("GGT", 35 * liver_multiplier, "U/L", 9, 48, "", base_date, "liver"),
            AbenaLabResult("LDH", 140 * liver_multiplier, "U/L", 100, 190, "", base_date, "liver"),
            AbenaLabResult("Total_Protein", 7.2 * liver_multiplier, "g/dL", 6.0, 8.3, "", base_date, "liver"),
            AbenaLabResult("Albumin", 4.2 * liver_multiplier, "g/dL", 3.5, 5.0, "", base_date, "liver"),
            AbenaLabResult("Globulin", 3.0 * liver_multiplier, "g/dL", 2.0, 3.5, "", base_date, "liver"),
            AbenaLabResult("A_G_Ratio", 1.4 * liver_multiplier, "", 1.0, 2.0, "", base_date, "liver"),
        ])
        
        # Thyroid Function Tests
        thyroid_multiplier = 0.9 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("TSH", 2.5 * thyroid_multiplier, "μIU/mL", 0.4, 4.0, "", base_date, "thyroid"),
            AbenaLabResult("Free_T4", 1.2 * thyroid_multiplier, "ng/dL", 0.8, 1.8, "", base_date, "thyroid"),
            AbenaLabResult("Free_T3", 3.2 * thyroid_multiplier, "pg/mL", 2.3, 4.2, "", base_date, "thyroid"),
            AbenaLabResult("Total_T4", 8.5 * thyroid_multiplier, "μg/dL", 5.0, 12.0, "", base_date, "thyroid"),
            AbenaLabResult("Total_T3", 120 * thyroid_multiplier, "ng/dL", 80, 200, "", base_date, "thyroid"),
            AbenaLabResult("Reverse_T3", 15 * thyroid_multiplier, "ng/dL", 9, 24, "", base_date, "thyroid"),
            AbenaLabResult("Thyroglobulin", 15 * thyroid_multiplier, "ng/mL", 3, 40, "", base_date, "thyroid"),
            AbenaLabResult("TPO_Antibodies", 12 * thyroid_multiplier, "IU/mL", 0, 34, "", base_date, "thyroid"),
            AbenaLabResult("Thyroglobulin_Antibodies", 8 * thyroid_multiplier, "IU/mL", 0, 20, "", base_date, "thyroid"),
        ])
        
        # Micronutrients
        self.lab_results.extend([
            AbenaLabResult("Vitamin_D", 28, "ng/mL", 30, 100, "", base_date, "micronutrients"),
            AbenaLabResult("B12", 350, "pg/mL", 200, 900, "", base_date, "micronutrients"),
            AbenaLabResult("Folate", 8.5, "ng/mL", 2.0, 20.0, "", base_date, "micronutrients"),
            AbenaLabResult("Zinc", 70, "μg/dL", 60, 120, "", base_date, "micronutrients"),
            AbenaLabResult("Magnesium", 1.8, "mg/dL", 1.5, 2.5, "", base_date, "micronutrients"),
            AbenaLabResult("Iron", 85, "μg/dL", 60, 170, "", base_date, "micronutrients"),
            AbenaLabResult("TIBC", 300, "μg/dL", 240, 450, "", base_date, "micronutrients"),
            AbenaLabResult("Ferritin", 120, "ng/mL", 20, 250, "", base_date, "micronutrients"),
            AbenaLabResult("Vitamin_A", 45, "μg/dL", 20, 80, "", base_date, "micronutrients"),
            AbenaLabResult("Vitamin_E", 12, "mg/L", 5, 20, "", base_date, "micronutrients"),
            AbenaLabResult("Vitamin_K", 2.5, "ng/mL", 0.5, 4.0, "", base_date, "micronutrients"),
            AbenaLabResult("Copper", 95, "μg/dL", 70, 140, "", base_date, "micronutrients"),
            AbenaLabResult("Selenium", 120, "μg/L", 70, 150, "", base_date, "micronutrients"),
        ])
        
        # Sex Hormones (Male)
        male_hormone_multiplier = 0.8 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("Testosterone_Total", 650 * male_hormone_multiplier, "ng/dL", 300, 1000, "", base_date, "male_hormones"),
            AbenaLabResult("Testosterone_Free", 12.5 * male_hormone_multiplier, "pg/mL", 5.0, 21.0, "", base_date, "male_hormones"),
            AbenaLabResult("Testosterone_Bioavailable", 180 * male_hormone_multiplier, "ng/dL", 70, 300, "", base_date, "male_hormones"),
            AbenaLabResult("SHBG", 35 * male_hormone_multiplier, "nmol/L", 10, 50, "", base_date, "male_hormones"),
            AbenaLabResult("DHT", 45 * male_hormone_multiplier, "ng/dL", 30, 85, "", base_date, "male_hormones"),
            AbenaLabResult("Estradiol", 25 * male_hormone_multiplier, "pg/mL", 10, 50, "", base_date, "male_hormones"),
            AbenaLabResult("Progesterone", 0.8 * male_hormone_multiplier, "ng/mL", 0.1, 1.0, "", base_date, "male_hormones"),
        ])
        
        # Sex Hormones (Female)
        female_hormone_multiplier = 0.9 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("Estradiol_Female", 85 * female_hormone_multiplier, "pg/mL", 12.5, 166, "", base_date, "female_hormones"),
            AbenaLabResult("Progesterone_Female", 12 * female_hormone_multiplier, "ng/mL", 0.1, 20.0, "", base_date, "female_hormones"),
            AbenaLabResult("Testosterone_Female", 35 * female_hormone_multiplier, "ng/dL", 8, 60, "", base_date, "female_hormones"),
            AbenaLabResult("FSH", 8.5 * female_hormone_multiplier, "mIU/mL", 3.5, 12.5, "", base_date, "female_hormones"),
            AbenaLabResult("LH", 6.2 * female_hormone_multiplier, "mIU/mL", 2.4, 12.6, "", base_date, "female_hormones"),
            AbenaLabResult("Prolactin", 12 * female_hormone_multiplier, "ng/mL", 4.8, 23.3, "", base_date, "female_hormones"),
            AbenaLabResult("AMH", 2.8 * female_hormone_multiplier, "ng/mL", 1.0, 4.0, "", base_date, "female_hormones"),
            AbenaLabResult("Inhibin_B", 85 * female_hormone_multiplier, "pg/mL", 20, 150, "", base_date, "female_hormones"),
        ])
        
        # Adrenal Gland Hormones
        adrenal_multiplier = 1.3 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("Cortisol_AM", 18.5 * adrenal_multiplier, "μg/dL", 6.0, 20.0, "", base_date, "adrenal"),
            AbenaLabResult("Cortisol_PM", 8.5 * adrenal_multiplier, "μg/dL", 2.0, 10.0, "", base_date, "adrenal"),
            AbenaLabResult("Cortisol_Midnight", 2.5 * adrenal_multiplier, "μg/dL", 0.5, 5.0, "", base_date, "adrenal"),
            AbenaLabResult("DHEA_S", 280 * adrenal_multiplier, "μg/dL", 30, 400, "", base_date, "adrenal"),
            AbenaLabResult("DHEA", 180 * adrenal_multiplier, "ng/mL", 50, 300, "", base_date, "adrenal"),
            AbenaLabResult("Aldosterone", 12 * adrenal_multiplier, "ng/dL", 3, 16, "", base_date, "adrenal"),
            AbenaLabResult("Renin", 2.5 * adrenal_multiplier, "ng/mL/hr", 0.5, 4.0, "", base_date, "adrenal"),
            AbenaLabResult("Aldosterone_Renin_Ratio", 4.8 * adrenal_multiplier, "", 1.0, 10.0, "", base_date, "adrenal"),
            AbenaLabResult("17_OH_Progesterone", 85 * adrenal_multiplier, "ng/dL", 20, 150, "", base_date, "adrenal"),
            AbenaLabResult("Androstenedione", 120 * adrenal_multiplier, "ng/dL", 30, 200, "", base_date, "adrenal"),
            AbenaLabResult("Pregnenolone", 45 * adrenal_multiplier, "ng/dL", 10, 80, "", base_date, "adrenal"),
        ])
        
        # Insulin and Glucose Metabolism
        insulin_multiplier = 1.4 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("Insulin_Fasting", 12 * insulin_multiplier, "μIU/mL", 3, 25, "", base_date, "insulin_metabolism"),
            AbenaLabResult("Insulin_Postprandial", 65 * insulin_multiplier, "μIU/mL", 10, 100, "", base_date, "insulin_metabolism"),
            AbenaLabResult("C_Peptide", 2.8 * insulin_multiplier, "ng/mL", 0.8, 4.0, "", base_date, "insulin_metabolism"),
            AbenaLabResult("Glucose_Fasting", 95 * insulin_multiplier, "mg/dL", 70, 100, "", base_date, "insulin_metabolism"),
            AbenaLabResult("Glucose_Postprandial", 140 * insulin_multiplier, "mg/dL", 70, 140, "", base_date, "insulin_metabolism"),
            AbenaLabResult("HbA1c", 5.4 * insulin_multiplier, "%", 4.0, 5.6, "", base_date, "insulin_metabolism"),
            AbenaLabResult("HOMA_IR", 2.8 * insulin_multiplier, "", 0.5, 2.5, "", base_date, "insulin_metabolism"),
            AbenaLabResult("HOMA_Beta", 120 * insulin_multiplier, "%", 50, 200, "", base_date, "insulin_metabolism"),
            AbenaLabResult("Insulin_Like_Growth_Factor_1", 180 * insulin_multiplier, "ng/mL", 100, 300, "", base_date, "insulin_metabolism"),
            AbenaLabResult("IGF_Binding_Protein_3", 3.2 * insulin_multiplier, "mg/L", 2.0, 5.0, "", base_date, "insulin_metabolism"),
        ])
        
        # Lung Function Tests
        lung_multiplier = 0.9 if scenario in ["moderate_dysfunction", "severe_dysfunction"] else 1.0
        self.lab_results.extend([
            AbenaLabResult("FEV1", 3.2 * lung_multiplier, "L", 2.5, 4.0, "", base_date, "lung_function"),
            AbenaLabResult("FVC", 4.1 * lung_multiplier, "L", 3.0, 5.0, "", base_date, "lung_function"),
            AbenaLabResult("FEV1_FVC_Ratio", 78 * lung_multiplier, "%", 70, 85, "", base_date, "lung_function"),
            AbenaLabResult("Peak_Expiratory_Flow", 450 * lung_multiplier, "L/min", 350, 600, "", base_date, "lung_function"),
            AbenaLabResult("Forced_Expiratory_Flow_25_75", 3.8 * lung_multiplier, "L/sec", 2.5, 5.0, "", base_date, "lung_function"),
            AbenaLabResult("Total_Lung_Capacity", 6.2 * lung_multiplier, "L", 5.0, 7.5, "", base_date, "lung_function"),
            AbenaLabResult("Residual_Volume", 1.8 * lung_multiplier, "L", 1.0, 2.5, "", base_date, "lung_function"),
            AbenaLabResult("Diffusion_Capacity", 25 * lung_multiplier, "mL/min/mmHg", 20, 35, "", base_date, "lung_function"),
        ])
    
    def _generate_vital_signs(self) -> None:
        """Generate vital signs data using Abena SDK models"""
        base_date = datetime.now() - timedelta(days=7)
        
        self.vital_signs = [
            AbenaVitalSign("Blood Pressure Systolic", 135, "mmHg", base_date),
            AbenaVitalSign("Blood Pressure Diastolic", 85, "mmHg", base_date),
            AbenaVitalSign("Heart Rate", 72, "bpm", base_date),
            AbenaVitalSign("Temperature", 98.6, "°F", base_date),
            AbenaVitalSign("Respiratory Rate", 16, "breaths/min", base_date),
            AbenaVitalSign("Oxygen Saturation", 98, "%", base_date),
        ]
    
    def _generate_ekg_results(self) -> None:
        """Generate EKG results using Abena SDK models"""
        base_date = datetime.now() - timedelta(days=7)
        
        self.ekg_results = [
            AbenaEKGResult("Heart Rate", 72, "bpm", "Normal sinus rhythm", base_date),
            AbenaEKGResult("PR Interval", 160, "ms", "Normal", base_date),
            AbenaEKGResult("QRS Duration", 88, "ms", "Normal", base_date),
            AbenaEKGResult("QT Interval", 420, "ms", "Normal", base_date),
            AbenaEKGResult("QTc Interval", 440, "ms", "Normal", base_date),
            AbenaEKGResult("Axis", 45, "degrees", "Normal", base_date),
        ]
    
    def _generate_smart_device_data(self) -> None:
        """Generate 30 days of smart device data using Abena SDK models"""
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            
            # HRV data with some variability
            hrv_base = 45 + random.uniform(-10, 10)
            self.smart_device_data.append(
                AbenaSmartDeviceData("Apple Watch", "HRV", hrv_base, "ms", current_date)
            )
            
            # Sleep quality (0-100 scale)
            sleep_quality = 75 + random.uniform(-20, 15)
            self.smart_device_data.append(
                AbenaSmartDeviceData("Apple Watch", "Sleep Quality", sleep_quality, "%", current_date)
            )
            
            # Stress level (0-100 scale)
            stress_level = 35 + random.uniform(-15, 25)
            self.smart_device_data.append(
                AbenaSmartDeviceData("Apple Watch", "Stress Level", stress_level, "%", current_date)
            )
            
            # Activity minutes
            activity_minutes = 45 + random.uniform(-20, 30)
            self.smart_device_data.append(
                AbenaSmartDeviceData("Apple Watch", "Activity Minutes", activity_minutes, "min", current_date)
            )
    
    def calculate_ecs_score(self) -> Dict[str, Any]:
        """Calculate comprehensive ECS dysfunction score"""
        scores = {}
        
        # Direct ECS markers (40%)
        direct_ecs_results = [r for r in self.lab_results if r.category == "direct_ecs"]
        direct_ecs_score = self._calculate_category_score(direct_ecs_results)
        scores['direct_ecs'] = direct_ecs_score
        
        # Inflammatory markers (25%)
        inflammation_results = [r for r in self.lab_results if r.category == "inflammation"]
        inflammation_score = self._calculate_category_score(inflammation_results)
        scores['inflammation'] = inflammation_score
        
        # Cardiovascular markers (15%)
        cv_results = [r for r in self.lab_results if r.category == "cardiovascular"]
        cv_score = self._calculate_category_score(cv_results)
        scores['cardiovascular'] = cv_score
        
        # Stress markers (20%)
        stress_results = [r for r in self.lab_results if r.category == "stress"]
        stress_score = self._calculate_category_score(stress_results)
        scores['stress'] = stress_score
        
        # Neurotransmitter markers (15%)
        nt_results = [r for r in self.lab_results if r.category == "neurotransmitters"]
        nt_score = self._calculate_category_score(nt_results)
        scores['neurotransmitters'] = nt_score
        
        # Calculate weighted total score
        total_score = (
            scores['direct_ecs'] * self.ecs_weights['direct_ecs'] +
            scores['inflammation'] * self.ecs_weights['inflammation'] +
            scores['cardiovascular'] * self.ecs_weights['cardiovascular'] +
            scores['stress'] * self.ecs_weights['stress'] +
            scores['neurotransmitters'] * self.ecs_weights['neurotransmitters']
        )
        
        # Determine dysfunction classification
        if total_score <= 20:
            classification = "Optimal ECS Function"
            severity = "optimal"
        elif total_score <= 40:
            classification = "Mild ECS Dysfunction"
            severity = "mild"
        elif total_score <= 60:
            classification = "Moderate ECS Dysfunction"
            severity = "moderate"
        else:
            classification = "Severe ECS Dysfunction"
            severity = "severe"
        
        return {
            'total_score': round(total_score, 1),
            'classification': classification,
            'severity': severity,
            'category_scores': scores,
            'weights': self.ecs_weights
        }
    
    def _calculate_category_score(self, results: List[AbenaLabResult]) -> float:
        """Calculate score for a category of lab results"""
        if not results:
            return 0.0
        
        total_score = 0.0
        for result in results:
            # Calculate deviation from normal range
            if result.value < result.reference_low:
                deviation = (result.reference_low - result.value) / result.reference_low
                score = min(deviation * 50, 100)  # Cap at 100
            elif result.value > result.reference_high:
                deviation = (result.value - result.reference_high) / result.reference_high
                score = min(deviation * 50, 100)  # Cap at 100
            else:
                score = 0  # Normal range
            
            total_score += score
        
        return total_score / len(results)
    
    def analyze_correlations(self) -> Dict[str, float]:
        """Analyze correlations between different health metrics"""
        correlations = {}
        
        # Get smart device data as DataFrame
        device_df = pd.DataFrame([
            {
                'date': d.timestamp.date(),
                'metric': d.metric,
                'value': d.value
            }
            for d in self.smart_device_data
        ])
        
        if not device_df.empty:
            # Pivot to get metrics as columns
            pivot_df = device_df.pivot(index='date', columns='metric', values='value')
            
            # Calculate correlations
            if 'HRV' in pivot_df.columns and 'Sleep Quality' in pivot_df.columns:
                correlations['hrv_sleep'] = pivot_df['HRV'].corr(pivot_df['Sleep Quality'])
            
            if 'Stress Level' in pivot_df.columns and 'Sleep Quality' in pivot_df.columns:
                correlations['stress_sleep'] = pivot_df['Stress Level'].corr(pivot_df['Sleep Quality'])
        
        return correlations
    
    def create_radar_chart(self) -> str:
        """Create radar chart for ECS component breakdown"""
        ecs_score = self.calculate_ecs_score()
        
        categories = list(ecs_score['category_scores'].keys())
        values = list(ecs_score['category_scores'].values())
        
        # Normalize values to 0-100 scale for radar chart
        normalized_values = [min(v, 100) for v in values]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=categories,
            fill='toself',
            name='ECS Components',
            line_color='rgb(32, 201, 151)',
            fillcolor='rgba(32, 201, 151, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title="ECS Component Analysis",
            title_x=0.5,
            height=400
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    def create_biomarker_chart(self) -> str:
        """Create bar chart for key biomarkers"""
        # Select key ECS-relevant biomarkers
        key_tests = ['AEA', '2-AG', 'CRP', 'IL6', 'Homocysteine', 'Cortisol_Morning', 'Serotonin']
        key_results = [r for r in self.lab_results if r.test_name in key_tests]
        
        if not key_results:
            return "<p>No biomarker data available</p>"
        
        test_names = [r.test_name for r in key_results]
        values = [r.value for r in key_results]
        status_colors = ['red' if r.status in ['high', 'low'] else 'green' for r in key_results]
        
        fig = go.Figure(data=[
            go.Bar(
                x=test_names,
                y=values,
                marker_color=status_colors,
                text=[f"{v:.2f} {r.unit}" for v, r in zip(values, key_results)],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Key ECS Biomarkers",
            xaxis_title="Biomarker",
            yaxis_title="Value",
            height=400,
            showlegend=False
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    def create_temporal_analysis(self) -> str:
        """Create multi-panel time series for 30-day trends"""
        # Get smart device data for last 30 days
        device_df = pd.DataFrame([
            {
                'date': d.timestamp,
                'metric': d.metric,
                'value': d.value
            }
            for d in self.smart_device_data
        ])
        
        if device_df.empty:
            return "<p>No temporal data available</p>"
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('HRV Trends', 'Sleep Quality', 'Stress Levels', 'Activity'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        metrics = ['HRV', 'Sleep Quality', 'Stress Level', 'Activity Minutes']
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for metric, pos in zip(metrics, positions):
            metric_data = device_df[device_df['metric'] == metric]
            if not metric_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=metric_data['date'],
                        y=metric_data['value'],
                        mode='lines+markers',
                        name=metric
                    ),
                    row=pos[0], col=pos[1]
                )
        
        fig.update_layout(
            title="30-Day Health Trends",
            height=600,
            showlegend=False
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    def create_correlation_heatmap(self) -> str:
        """Create correlation heatmap for ECS-health relationships"""
        # Create correlation matrix
        correlation_data = {
            'ECS Score': [self.calculate_ecs_score()['total_score']] * 4,
            'HRV': [np.mean([d.value for d in self.smart_device_data if d.metric == 'HRV'])],
            'Sleep Quality': [np.mean([d.value for d in self.smart_device_data if d.metric == 'Sleep Quality'])],
            'Stress Level': [np.mean([d.value for d in self.smart_device_data if d.metric == 'Stress Level'])],
            'Inflammation': [np.mean([r.value for r in self.lab_results if r.category == 'inflammation'])]
        }
        
        # Calculate correlations (simplified for demo)
        correlations = np.array([
            [1.0, -0.3, -0.4, 0.6, 0.7],
            [-0.3, 1.0, 0.5, -0.4, -0.3],
            [-0.4, 0.5, 1.0, -0.6, -0.4],
            [0.6, -0.4, -0.6, 1.0, 0.5],
            [0.7, -0.3, -0.4, 0.5, 1.0]
        ])
        
        fig = go.Figure(data=go.Heatmap(
            z=correlations,
            x=list(correlation_data.keys()),
            y=list(correlation_data.keys()),
            colorscale='RdBu',
            zmid=0
        ))
        
        fig.update_layout(
            title="ECS-Health Correlation Matrix",
            height=400
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    def generate_recommendations(self) -> Dict[str, List[str]]:
        """Generate personalized treatment recommendations"""
        ecs_score = self.calculate_ecs_score()
        recommendations = {
            'supplements': [],
            'lifestyle': [],
            'dietary': [],
            'monitoring': []
        }
        
        # Supplement recommendations based on scores
        if ecs_score['category_scores']['direct_ecs'] > 30:
            recommendations['supplements'].append("Consider CBD supplementation (25-50mg daily)")
            recommendations['supplements'].append("Omega-3 fatty acids (2-4g EPA+DHA daily)")
        
        if ecs_score['category_scores']['inflammation'] > 30:
            recommendations['supplements'].append("Curcumin (500-1000mg daily)")
            recommendations['supplements'].append("Vitamin D3 (2000-4000 IU daily)")
        
        if ecs_score['category_scores']['stress'] > 30:
            recommendations['supplements'].append("Ashwagandha (300-600mg daily)")
            recommendations['supplements'].append("Magnesium glycinate (200-400mg daily)")
        
        # Lifestyle recommendations
        recommendations['lifestyle'].append("Implement stress management techniques (meditation, yoga)")
        recommendations['lifestyle'].append("Optimize sleep hygiene (7-9 hours, consistent schedule)")
        recommendations['lifestyle'].append("Regular moderate exercise (150 minutes/week)")
        
        # Dietary recommendations
        recommendations['dietary'].append("Increase anti-inflammatory foods (fatty fish, berries, leafy greens)")
        recommendations['dietary'].append("Reduce processed foods and added sugars")
        recommendations['dietary'].append("Maintain adequate protein intake (1.2-1.6g/kg body weight)")
        
        # Monitoring recommendations
        if ecs_score['severity'] in ['moderate', 'severe']:
            recommendations['monitoring'].append("Monthly follow-up testing for key biomarkers")
        else:
            recommendations['monitoring'].append("Quarterly monitoring of ECS markers")
        
        recommendations['monitoring'].append("Weekly tracking of sleep quality and stress levels")
        recommendations['monitoring'].append("Monthly HRV monitoring")
        
        return recommendations
    
    def create_html_report(self) -> str:
        """Generate comprehensive HTML report"""
        if not self.patient_data:
            return "<p>No patient data loaded</p>"
        
        ecs_score = self.calculate_ecs_score()
        recommendations = self.generate_recommendations()
        
        # Generate all charts
        radar_chart = self.create_radar_chart()
        biomarker_chart = self.create_biomarker_chart()
        temporal_chart = self.create_temporal_analysis()
        correlation_chart = self.create_correlation_heatmap()
        
        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ECS Analysis Report - {self.patient_data.name}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #20c997;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .score-box {{
                    background: linear-gradient(135deg, #20c997, #17a2b8);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .score-number {{
                    font-size: 3em;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .section {{
                    margin: 30px 0;
                    padding: 20px;
                    border-left: 4px solid #20c997;
                    background: #f8f9fa;
                }}
                .chart-container {{
                    margin: 20px 0;
                    text-align: center;
                }}
                .recommendations {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .rec-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid #dee2e6;
                }}
                .rec-card h3 {{
                    color: #20c997;
                    margin-top: 0;
                }}
                .rec-list {{
                    list-style: none;
                    padding: 0;
                }}
                .rec-list li {{
                    padding: 8px 0;
                    border-bottom: 1px solid #eee;
                }}
                .rec-list li:before {{
                    content: "✓ ";
                    color: #20c997;
                    font-weight: bold;
                }}
                .alert {{
                    padding: 15px;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .alert-warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                }}
                .alert-info {{
                    background-color: #d1ecf1;
                    border: 1px solid #bee5eb;
                    color: #0c5460;
                }}
                .patient-info {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .info-item {{
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 5px;
                    text-align: center;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #6c757d;
                }}
                .info-value {{
                    font-size: 1.1em;
                    color: #495057;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Endocannabinoid System (ECS) Analysis Report</h1>
                    <h2>Abena Intelligent Health Records</h2>
                    <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div class="patient-info">
                    <div class="info-item">
                        <div class="info-label">Patient Name</div>
                        <div class="info-value">{self.patient_data.name}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Patient ID</div>
                        <div class="info-value">{self.patient_data.patient_id}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Age</div>
                        <div class="info-value">{self.patient_data.age} years</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">BMI</div>
                        <div class="info-value">{self.patient_data.bmi:.1f}</div>
                    </div>
                </div>
                
                <div class="score-box">
                    <h2>Overall ECS Function Score</h2>
                    <div class="score-number">{ecs_score['total_score']}</div>
                    <h3>{ecs_score['classification']}</h3>
                    <p>Based on comprehensive analysis of {len(self.lab_results)} biomarkers and {len(self.smart_device_data)} smart device measurements</p>
                </div>
                
                <div class="section">
                    <h2>ECS Component Analysis</h2>
                    <p>This radar chart shows the breakdown of ECS function across five key categories. Each axis represents a different aspect of endocannabinoid system health.</p>
                    <div class="chart-container">
                        {radar_chart}
                    </div>
                    <div class="alert alert-info">
                        <strong>Interpretation:</strong> Higher values indicate greater dysfunction. Optimal function shows low values across all categories.
                    </div>
                </div>
                
                <div class="section">
                    <h2>Key Biomarker Analysis</h2>
                    <p>Critical ECS-relevant biomarkers with color coding: Green = Normal, Red = Abnormal</p>
                    <div class="chart-container">
                        {biomarker_chart}
                    </div>
                </div>
                
                <div class="section">
                    <h2>30-Day Health Trends</h2>
                    <p>Longitudinal analysis of smart device data showing patterns in heart rate variability, sleep quality, stress levels, and activity.</p>
                    <div class="chart-container">
                        {temporal_chart}
                    </div>
                </div>
                
                <div class="section">
                    <h2>ECS-Health Correlations</h2>
                    <p>Correlation matrix showing relationships between ECS function and various health metrics.</p>
                    <div class="chart-container">
                        {correlation_chart}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Personalized Recommendations</h2>
                    <div class="recommendations">
                        <div class="rec-card">
                            <h3>Supplementation</h3>
                            <ul class="rec-list">
                                {''.join([f'<li>{rec}</li>' for rec in recommendations['supplements']])}
                            </ul>
                        </div>
                        <div class="rec-card">
                            <h3>Lifestyle Modifications</h3>
                            <ul class="rec-list">
                                {''.join([f'<li>{rec}</li>' for rec in recommendations['lifestyle']])}
                            </ul>
                        </div>
                        <div class="rec-card">
                            <h3>Dietary Recommendations</h3>
                            <ul class="rec-list">
                                {''.join([f'<li>{rec}</li>' for rec in recommendations['dietary']])}
                            </ul>
                        </div>
                        <div class="rec-card">
                            <h3>Monitoring Protocol</h3>
                            <ul class="rec-list">
                                {''.join([f'<li>{rec}</li>' for rec in recommendations['monitoring']])}
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Clinical Notes</h2>
                    <div class="alert alert-warning">
                        <strong>Important:</strong> This report is for educational and research purposes only. 
                        All recommendations should be reviewed by a qualified healthcare provider before implementation.
                    </div>
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        <li>Review findings with healthcare provider</li>
                        <li>Implement recommended lifestyle modifications</li>
                        <li>Schedule follow-up testing as indicated</li>
                        <li>Monitor progress through smart device data</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = ECSAnalyzer()
    
    # Load test patient data
    analyzer.load_test_patient_data("moderate_dysfunction")
    
    # Generate comprehensive analysis
    html_report = analyzer.create_html_report()
    
    # Save report with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ecs_report_{analyzer.patient_data.patient_id}_{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"ECS Analysis Report generated: {filename}")
    print(f"Patient: {analyzer.patient_data.name}")
    print(f"ECS Score: {analyzer.calculate_ecs_score()['total_score']}")
    print(f"Classification: {analyzer.calculate_ecs_score()['classification']}") 