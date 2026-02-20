import pytest
import json
from unittest.mock import patch, MagicMock
from abena_etl import TransformationEngine

@pytest.fixture
def sample_emr_data(tmp_path):
    # Create a sample CSV file for EMR data
    csv_content = (
        'MRN,FirstName,LastName,Sex,DOB,EmailAddress,HomePhone,ObservationType,ObservationValue,ObservationUnit,ObservationDateTime,SourceSystem,PatientMRN\n'
        '12345,Jane,Doe,FEMALE,1990-01-01,jane@example.com,555-1234,weight,110,lb,2024-01-01T00:00:00Z,TestSys,12345\n'
        '12345,Jane,Doe,FEMALE,1990-01-01,jane@example.com,555-1234,height,67,in,2024-01-01T00:00:00Z,TestSys,12345\n'
    )
    file_path = tmp_path / "sample_emr.csv"
    file_path.write_text(csv_content)
    return str(file_path)

@patch('abena_etl.MappingRepository')
@patch('abena_etl.SparkSession')
def test_etl_pipeline(mock_spark, mock_mapping_repo, sample_emr_data, tmp_path):
    # Mock mapping config
    mapping_config = {
        'patient_mappings': {
            'MRN': 'mrn',
            'FirstName': 'first_name',
            'LastName': 'last_name',
            'Sex': 'gender',
            'DOB': 'birth_date',
            'EmailAddress': 'email',
            'HomePhone': 'phone'
        },
        'observation_mappings': {
            'PatientMRN': 'patient_id',
            'ObservationType': 'type',
            'ObservationValue': 'value',
            'ObservationUnit': 'unit',
            'ObservationDateTime': 'timestamp',
            'SourceSystem': 'source_system'
        }
    }
    mock_mapping_repo.return_value.get_mapping.return_value = mapping_config

    # Mock Spark DataFrame behavior
    mock_spark_instance = MagicMock()
    mock_spark.return_value.builder.getOrCreate.return_value = mock_spark_instance
    # Simulate reading CSV and returning a DataFrame with select/filter/withColumn/collect/count
    class FakeRow:
        def __init__(self, d): self._d = d
        def asDict(self): return self._d
    patient_row = FakeRow({'mrn': '12345', 'first_name': 'Jane', 'last_name': 'Doe', 'gender': 'female', 'birth_date': '1990-01-01', 'email': 'jane@example.com', 'phone': '5551234'})
    obs_row1 = FakeRow({'patient_id': '12345', 'type': 'weight', 'value': 110, 'unit': 'lb', 'timestamp': '2024-01-01T00:00:00Z', 'source_system': 'TestSys'})
    obs_row2 = FakeRow({'patient_id': '12345', 'type': 'height', 'value': 67, 'unit': 'in', 'timestamp': '2024-01-01T00:00:00Z', 'source_system': 'TestSys'})
    fake_patients_df = MagicMock()
    fake_patients_df.collect.return_value = [patient_row]
    fake_patients_df.count.return_value = 1
    fake_obs_df = MagicMock()
    fake_obs_df.collect.return_value = [obs_row1, obs_row2]
    fake_obs_df.count.return_value = 2
    # The select/filter/withColumn chain returns itself
    fake_patients_df.withColumn.return_value = fake_patients_df
    fake_patients_df.filter.return_value = fake_patients_df
    fake_obs_df.withColumn.return_value = fake_obs_df
    fake_obs_df.filter.return_value = fake_obs_df
    # The select returns the correct df
    def select_side_effect(*args, **kwargs):
        if any(a == 'mrn' or (hasattr(a, 'alias') and a.alias == 'mrn') for a in args):
            return fake_patients_df
        else:
            return fake_obs_df
    fake_raw_df = MagicMock()
    fake_raw_df.columns = ['MRN','FirstName','LastName','Sex','DOB','EmailAddress','HomePhone','ObservationType','ObservationValue','ObservationUnit','ObservationDateTime','SourceSystem','PatientMRN']
    fake_raw_df.select.side_effect = select_side_effect
    mock_spark_instance.read.csv.return_value = fake_raw_df
    # Patch clean_patient_data and clean_observation_data to return the fake dfs
    with patch('abena_etl.TransformationEngine.clean_patient_data', return_value=fake_patients_df), \
         patch('abena_etl.TransformationEngine.clean_observation_data', return_value=fake_obs_df):
        engine = TransformationEngine()
        output_path = str(tmp_path / "fhir_output")
        result = engine.process_batch(sample_emr_data, 'TestSys', output_path)
        assert result['status'] == 'success'
        assert result['records_processed']['patients'] == 1
        assert result['records_processed']['observations'] == 2
        assert result['fhir_resources_created'] >= 3  # 1 patient + 2 obs
        assert result['output_path'] == output_path
        assert 'timestamp' in result 