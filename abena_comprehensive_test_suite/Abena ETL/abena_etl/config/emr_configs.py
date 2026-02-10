from enum import Enum
from typing import Dict

class EMRConfig:
    EPIC = {
        'type': 'epic',
        'fhir_base_url': 'https://fhir.epic.com/interconnect-fhir-oauth',
        'oauth_url': '/oauth2/token',
        'required_scopes': ['patient/Patient.read', 'patient/Observation.read']
    }
    
    CERNER = {
        'type': 'cerner',
        'fhir_base_url': 'https://fhir-ehr.cerner.com/r4',
        'oauth_url': '/tenants/{tenant}/protocols/oauth2/profiles/smart-v1/token',
        'required_scopes': ['patient/Patient.read', 'patient/Observation.read']
    }