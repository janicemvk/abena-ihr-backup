from abena_etl import MappingRepository, UnitConversionService, UnitType, ConversionRule

# Set up custom mapping for a new EMR system
repo = MappingRepository()
custom_mapping = {
    'patient_mappings': {
        'PATIENT_ID': 'mrn',
        'GIVEN_NAME': 'first_name',
        'FAMILY_NAME': 'last_name',
        'SEX': 'gender',
        'DOB': 'birth_date',
        'EMAIL': 'email',
        'PHONE': 'phone'
    },
    'observation_mappings': {
        'PATIENT_ID': 'patient_id',
        'OBS_TYPE': 'type',
        'OBS_VALUE': 'value',
        'OBS_UNIT': 'unit',
        'OBS_TIMESTAMP': 'timestamp',
        'SOURCE_SYS': 'source_system'
    }
}
repo.create_mapping("CustomEMR", "FHIR", custom_mapping, "1.0")
print("Custom EMR mapping added.")

# Example: Add a custom unit conversion rule (e.g., stone to kg)
unit_service = UnitConversionService()
unit_service.conversion_rules[UnitType.WEIGHT].append(ConversionRule("stone", "kg", 6.35029))
print("Custom unit conversion rule (stone to kg) added.") 