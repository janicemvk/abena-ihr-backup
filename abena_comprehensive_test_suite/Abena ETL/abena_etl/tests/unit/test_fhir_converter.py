import pytest
from unittest.mock import MagicMock
from abena_etl import FHIRConverter, UnitType

@pytest.fixture
def mock_unit_service():
    service = MagicMock()
    service.convert_value.side_effect = lambda v, f, t, u: 50 if t == 'kg' else 170 if t == 'cm' else 37 if t == 'C' else v
    return service

@pytest.fixture
def fhir_converter(mock_unit_service):
    return FHIRConverter(mock_unit_service)

def test_create_patient_resource(fhir_converter):
    patient_data = {
        'mrn': '12345',
        'first_name': 'Jane',
        'last_name': 'Doe',
        'gender': 'FEMALE',
        'birth_date': '1990-01-01'
    }
    patient = fhir_converter.create_patient_resource(patient_data)
    assert patient.resource_type == 'Patient'
    assert patient.identifier[0].value == '12345'
    assert patient.name[0]['given'][0] == 'Jane'
    assert patient.gender == 'female'
    assert patient.birthDate == '1990-01-01'

def test_create_observation_resource_weight(fhir_converter):
    obs_data = {
        'type': 'weight',
        'value': 110,
        'unit': 'lb',
        'timestamp': '2024-01-01T00:00:00Z'
    }
    obs = fhir_converter.create_observation_resource(obs_data, 'pat1')
    assert obs.resource_type == 'Observation'
    assert obs.valueQuantity.value == 50
    assert obs.valueQuantity.unit == 'kg'
    assert obs.code.coding[0].code == '29463-7'
    assert obs.subject['reference'] == 'Patient/pat1'

def test_create_observation_resource_height(fhir_converter):
    obs_data = {
        'type': 'height',
        'value': 67,
        'unit': 'in',
        'timestamp': '2024-01-01T00:00:00Z'
    }
    obs = fhir_converter.create_observation_resource(obs_data, 'pat2')
    assert obs.valueQuantity.value == 170
    assert obs.valueQuantity.unit == 'cm'
    assert obs.code.coding[0].code == '8302-2'

def test_create_observation_resource_temperature(fhir_converter):
    obs_data = {
        'type': 'temperature',
        'value': 98.6,
        'unit': 'F',
        'timestamp': '2024-01-01T00:00:00Z'
    }
    obs = fhir_converter.create_observation_resource(obs_data, 'pat3')
    assert obs.valueQuantity.value == 37
    assert obs.valueQuantity.unit == 'C'
    assert obs.code.coding[0].code == '8310-5'

def test_create_observation_resource_unknown_type(fhir_converter):
    obs_data = {
        'type': 'unknown_type',
        'value': 10,
        'unit': 'foo',
        'timestamp': '2024-01-01T00:00:00Z'
    }
    with pytest.raises(ValueError):
        fhir_converter.create_observation_resource(obs_data, 'pat4') 