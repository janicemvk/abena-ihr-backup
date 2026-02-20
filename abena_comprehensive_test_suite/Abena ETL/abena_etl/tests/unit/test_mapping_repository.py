import pytest
from unittest.mock import patch, MagicMock
from abena_etl import MappingRepository

@pytest.fixture
def mock_repo():
    with patch('abena_etl.create_engine'), \
         patch('abena_etl.Base.metadata.create_all'), \
         patch('abena_etl.sessionmaker') as mock_sessionmaker, \
         patch('abena_etl.redis.Redis') as mock_redis:
        mock_session = MagicMock()
        mock_sessionmaker.return_value = lambda: mock_session
        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance
        repo = MappingRepository(db_url='sqlite:///:memory:')
        repo.session = mock_session
        repo.redis_client = mock_redis_instance
        yield repo, mock_session, mock_redis_instance

def test_create_and_get_mapping(mock_repo):
    repo, mock_session, mock_redis = mock_repo
    mapping_config = {'patient_mappings': {'A': 'B'}, 'observation_mappings': {'C': 'D'}}
    # Simulate DB add/commit
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    # Simulate DB query
    mock_mapping_obj = MagicMock()
    mock_mapping_obj.mapping_config = '{"patient_mappings": {"A": "B"}, "observation_mappings": {"C": "D"}}'
    mock_session.query().filter_by().first.return_value = mock_mapping_obj
    # Simulate Redis cache miss then hit
    mock_redis.get.return_value = None
    mapping_id = repo.create_mapping('TestSys', 'FHIR', mapping_config, '1.0')
    assert isinstance(mapping_id, int)
    # Now test get_mapping (should cache after DB fetch)
    result = repo.get_mapping('TestSys', 'FHIR', '1.0')
    assert result['patient_mappings']['A'] == 'B'
    # Now simulate cache hit
    mock_redis.get.return_value = mock_mapping_obj.mapping_config.encode()
    result2 = repo.get_mapping('TestSys', 'FHIR', '1.0')
    assert result2['observation_mappings']['C'] == 'D'
    # Ensure cache setex was called
    assert mock_redis.setex.called 