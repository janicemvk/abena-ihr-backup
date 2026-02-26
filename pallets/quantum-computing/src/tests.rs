//! Tests for quantum computing pallet

use crate::mock::*;
use crate::*;
use frame_support::{assert_err, assert_ok};
use sp_core::H256;

#[test]
fn submit_job_works() {
    new_test_ext().execute_with(|| {
        let submitter = 1u64;
        let job_type = QuantumJobType::Simulation;
        let parameters = vec![1, 2, 3, 4, 5];

        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(submitter),
            job_type.clone(),
            parameters.clone(),
            None,
            None,
            None,
        ));

        let job = QuantumComputing::quantum_jobs(1);
        assert!(job.is_some());
        let job = job.unwrap();
        assert_eq!(job.job_type, job_type);
        assert_eq!(job.status, JobStatus::Pending);
    });
}

#[test]
fn store_result_works() {
    new_test_ext().execute_with(|| {
        let submitter = 1u64;
        let job_type = QuantumJobType::Simulation;
        let parameters = vec![1, 2, 3, 4, 5];

        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(submitter),
            job_type,
            parameters,
            None,
            None,
            None,
        ));

        let result_data = vec![10, 20, 30];
        let result_hash = H256::from_slice(&[1u8; 32]);

        assert_ok!(QuantumComputing::store_result(
            RuntimeOrigin::signed(submitter),
            1,
            result_data.clone(),
            result_hash
        ));

        let result = QuantumComputing::quantum_results(1);
        assert!(result.is_some());
        let result = result.unwrap();
        assert_eq!(result.result_data, result_data);
        assert_eq!(result.result_hash, result_hash);
    });
}

#[test]
fn register_integration_point_works() {
    new_test_ext().execute_with(|| {
        let provider = 1u64;
        let point_id = 1u32;
        let provider_name = b"IBM Quantum".to_vec();
        let endpoint = b"https://quantum.ibm.com".to_vec();
        let capabilities = vec![QuantumCapability::Simulation, QuantumCapability::NISQ];

        assert_ok!(QuantumComputing::register_integration_point(
            RuntimeOrigin::signed(provider),
            point_id,
            provider_name.clone(),
            endpoint.clone(),
            capabilities.clone()
        ));

        let point = QuantumComputing::integration_points(point_id);
        assert!(point.is_some());
        let point = point.unwrap();
        assert_eq!(point.provider_name, provider_name);
        assert_eq!(point.endpoint, endpoint);
        assert_eq!(point.capabilities, capabilities);
    });
}

#[test]
fn update_integration_point_works() {
    new_test_ext().execute_with(|| {
        let provider = 1u64;
        let point_id = 1u32;
        let provider_name = b"IBM Quantum".to_vec();
        let endpoint = b"https://quantum.ibm.com".to_vec();
        let capabilities = vec![QuantumCapability::Simulation];

        assert_ok!(QuantumComputing::register_integration_point(
            RuntimeOrigin::signed(provider),
            point_id,
            provider_name,
            endpoint,
            capabilities
        ));

        let new_endpoint = b"https://new.quantum.ibm.com".to_vec();
        let new_capabilities = vec![QuantumCapability::Simulation, QuantumCapability::FaultTolerant];

        assert_ok!(QuantumComputing::update_integration_point(
            RuntimeOrigin::signed(provider),
            point_id,
            Some(new_endpoint.clone()),
            Some(new_capabilities.clone()),
            None
        ));

        let point = QuantumComputing::integration_points(point_id);
        assert_eq!(point.unwrap().endpoint, new_endpoint);
    });
}

#[test]
fn query_result_works() {
    new_test_ext().execute_with(|| {
        let submitter = 1u64;
        let job_type = QuantumJobType::Simulation;
        let parameters = vec![1, 2, 3, 4, 5];

        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(submitter),
            job_type,
            parameters,
            None,
            None,
            None,
        ));

        let result_data = vec![10, 20, 30];
        let result_hash = H256::from_slice(&[1u8; 32]);

        assert_ok!(QuantumComputing::store_result(
            RuntimeOrigin::signed(submitter),
            1,
            result_data,
            result_hash
        ));

        assert_ok!(QuantumComputing::query_result(
            RuntimeOrigin::signed(submitter),
            1
        ));
    });
}

