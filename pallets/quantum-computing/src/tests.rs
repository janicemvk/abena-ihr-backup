//! Comprehensive tests for the ABENA Quantum Computing pallet.

use crate::mock::*;
use crate::*;
use frame_support::{assert_err, assert_ok};
use sp_core::H256;

fn result_hash(n: u8) -> H256 { H256::from_slice(&[n; 32]) }

// ── submit_job ───────────────────────────────────────────────────────────────

#[test]
fn submit_job_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1),
            QuantumJobType::Simulation,
            vec![1, 2, 3, 4, 5],
            None, None, None,
        ));
        let job = QuantumComputing::quantum_jobs(1).unwrap();
        assert_eq!(job.job_type, QuantumJobType::Simulation);
        assert_eq!(job.status, JobStatus::Pending);
    });
}

#[test]
fn submit_job_increments_job_counter() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1), QuantumJobType::VQE,
            vec![0u8; 32], None, None, None,
        ));
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1), QuantumJobType::QML,
            vec![0u8; 32], None, None, None,
        ));
        assert_eq!(JobCounter::<Test>::get(), 2);
        assert!(QuantumJobs::<Test>::contains_key(1u64));
        assert!(QuantumJobs::<Test>::contains_key(2u64));
    });
}

#[test]
fn submit_job_all_types() {
    new_test_ext().execute_with(|| {
        for jtype in [
            QuantumJobType::VQE, QuantumJobType::QML, QuantumJobType::QAOA,
            QuantumJobType::Simulation, QuantumJobType::Optimization,
            QuantumJobType::MachineLearning, QuantumJobType::Cryptography,
            QuantumJobType::DrugDiscovery, QuantumJobType::ProteinFolding,
        ] {
            assert_ok!(QuantumComputing::submit_job(
                RuntimeOrigin::signed(1), jtype, vec![0u8; 16], None, None, None,
            ));
        }
    });
}

#[test]
fn submit_job_with_patient_link() {
    new_test_ext().execute_with(|| {
        let record_hash = H256::from_slice(&[9u8; 32]);
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1),
            QuantumJobType::DrugDiscovery,
            vec![1u8; 64],
            None,
            Some(5u64),
            Some(record_hash),
        ));
        let job = QuantumJobs::<Test>::get(1u64).unwrap();
        assert_eq!(job.patient, Some(5u64));
        assert_eq!(job.health_record_hash, Some(record_hash));
    });
}

#[test]
fn submit_job_fails_for_invalid_integration_point() {
    new_test_ext().execute_with(|| {
        assert_err!(
            QuantumComputing::submit_job(
                RuntimeOrigin::signed(1),
                QuantumJobType::Simulation,
                vec![1u8; 16],
                Some(999u32),  // nonexistent integration point
                None, None,
            ),
            Error::<Test>::IntegrationPointNotFound
        );
    });
}

#[test]
fn submit_job_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1), QuantumJobType::QAOA,
            vec![0u8; 8], None, None, None,
        ));
        System::assert_has_event(RuntimeEvent::QuantumComputing(
            Event::QuantumJobSubmitted { job_id: 1, submitter: 1, job_type: QuantumJobType::QAOA }
        ));
    });
}

// ── store_result ─────────────────────────────────────────────────────────────

#[test]
fn store_result_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1), QuantumJobType::Simulation,
            vec![1, 2, 3], None, None, None,
        ));
        assert_ok!(QuantumComputing::store_result(
            RuntimeOrigin::signed(1), 1u64, vec![10, 20, 30], result_hash(1)
        ));
        let result = QuantumComputing::quantum_results(1u64).unwrap();
        assert_eq!(result.result_data, vec![10, 20, 30]);
        assert_eq!(result.result_hash, result_hash(1));
    });
}

#[test]
fn store_result_updates_job_status_to_completed() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1), QuantumJobType::VQE, vec![1u8; 8], None, None, None,
        ));
        assert_ok!(QuantumComputing::store_result(
            RuntimeOrigin::signed(1), 1u64, vec![42u8; 16], result_hash(2)
        ));
        assert_eq!(QuantumJobs::<Test>::get(1u64).unwrap().status, JobStatus::Completed);
    });
}

#[test]
fn store_result_fails_if_job_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            QuantumComputing::store_result(RuntimeOrigin::signed(1), 999u64, vec![1u8], result_hash(1)),
            Error::<Test>::JobNotFound
        );
    });
}

#[test]
fn store_result_fails_if_already_stored() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1), QuantumJobType::Simulation, vec![1u8], None, None, None,
        ));
        assert_ok!(QuantumComputing::store_result(
            RuntimeOrigin::signed(1), 1u64, vec![1u8], result_hash(1)
        ));
        assert_err!(
            QuantumComputing::store_result(
                RuntimeOrigin::signed(1), 1u64, vec![2u8], result_hash(2)
            ),
            Error::<Test>::ResultAlreadyStored
        );
    });
}

#[test]
fn store_result_fails_with_empty_result_data() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1), QuantumJobType::Simulation, vec![1u8], None, None, None,
        ));
        assert_err!(
            QuantumComputing::store_result(
                RuntimeOrigin::signed(1), 1u64, vec![], result_hash(1)
            ),
            Error::<Test>::InvalidResultData
        );
    });
}

#[test]
fn store_result_emits_events() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1), QuantumJobType::QML, vec![1u8], None, None, None,
        ));
        assert_ok!(QuantumComputing::store_result(
            RuntimeOrigin::signed(1), 1u64, vec![42u8], result_hash(3)
        ));
        System::assert_has_event(RuntimeEvent::QuantumComputing(
            Event::QuantumResultStored { job_id: 1, result_hash: result_hash(3) }
        ));
        System::assert_has_event(RuntimeEvent::QuantumComputing(
            Event::QuantumJobCompleted { job_id: 1, result_hash: result_hash(3) }
        ));
    });
}

// ── register_integration_point ───────────────────────────────────────────────

#[test]
fn register_integration_point_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::register_integration_point(
            RuntimeOrigin::signed(1), 1u32,
            b"IBM Quantum".to_vec(), b"https://quantum.ibm.com".to_vec(),
            vec![QuantumCapability::Simulation, QuantumCapability::NISQ],
        ));
        let point = QuantumComputing::integration_points(1u32).unwrap();
        assert_eq!(point.provider_name.as_slice(), b"IBM Quantum");
        assert!(point.active);
    });
}

#[test]
fn register_integration_point_all_capabilities() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::register_integration_point(
            RuntimeOrigin::signed(1), 1u32,
            b"Full-Stack Quantum".to_vec(), b"https://fqc.example.com".to_vec(),
            vec![
                QuantumCapability::Simulation,
                QuantumCapability::Optimization,
                QuantumCapability::MachineLearning,
                QuantumCapability::Cryptography,
                QuantumCapability::NISQ,
                QuantumCapability::FaultTolerant,
            ],
        ));
        assert!(IntegrationPoints::<Test>::contains_key(1u32));
    });
}

#[test]
fn register_integration_point_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::register_integration_point(
            RuntimeOrigin::signed(1), 7u32,
            b"Provider".to_vec(), b"ep".to_vec(), vec![QuantumCapability::Simulation],
        ));
        System::assert_has_event(RuntimeEvent::QuantumComputing(
            Event::IntegrationPointRegistered { point_id: 7, provider: 1 }
        ));
    });
}

// ── update_integration_point ─────────────────────────────────────────────────

#[test]
fn update_integration_point_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::register_integration_point(
            RuntimeOrigin::signed(1), 1u32,
            b"IBM Quantum".to_vec(), b"https://quantum.ibm.com".to_vec(),
            vec![QuantumCapability::Simulation],
        ));
        assert_ok!(QuantumComputing::update_integration_point(
            RuntimeOrigin::signed(1), 1u32,
            Some(b"https://new.quantum.ibm.com".to_vec()),
            Some(vec![QuantumCapability::FaultTolerant]),
            None,
        ));
        let point = IntegrationPoints::<Test>::get(1u32).unwrap();
        assert_eq!(point.endpoint.as_slice(), b"https://new.quantum.ibm.com");
    });
}

#[test]
fn update_integration_point_can_deactivate() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::register_integration_point(
            RuntimeOrigin::signed(1), 1u32, b"P".to_vec(), b"ep".to_vec(),
            vec![QuantumCapability::NISQ],
        ));
        assert_ok!(QuantumComputing::update_integration_point(
            RuntimeOrigin::signed(1), 1u32, None, None, Some(false)
        ));
        assert!(!IntegrationPoints::<Test>::get(1u32).unwrap().active);
    });
}

#[test]
fn update_integration_point_fails_for_non_provider() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::register_integration_point(
            RuntimeOrigin::signed(1), 1u32, b"P".to_vec(), b"ep".to_vec(),
            vec![QuantumCapability::Simulation],
        ));
        assert_err!(
            QuantumComputing::update_integration_point(
                RuntimeOrigin::signed(99), 1u32, None, None, Some(false)
            ),
            Error::<Test>::IntegrationPointNotFound
        );
    });
}

#[test]
fn update_integration_point_fails_if_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            QuantumComputing::update_integration_point(
                RuntimeOrigin::signed(1), 999u32, None, None, Some(true)
            ),
            Error::<Test>::IntegrationPointNotFound
        );
    });
}

#[test]
fn update_integration_point_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::register_integration_point(
            RuntimeOrigin::signed(1), 1u32, b"P".to_vec(), b"ep".to_vec(),
            vec![QuantumCapability::Simulation],
        ));
        assert_ok!(QuantumComputing::update_integration_point(
            RuntimeOrigin::signed(1), 1u32, None, None, Some(true)
        ));
        System::assert_has_event(RuntimeEvent::QuantumComputing(
            Event::IntegrationPointUpdated { point_id: 1 }
        ));
    });
}

// ── query_result ─────────────────────────────────────────────────────────────

#[test]
fn query_result_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1), QuantumJobType::Simulation,
            vec![1, 2, 3], None, None, None,
        ));
        assert_ok!(QuantumComputing::store_result(
            RuntimeOrigin::signed(1), 1u64, vec![10, 20, 30], result_hash(1)
        ));
        assert_ok!(QuantumComputing::query_result(RuntimeOrigin::signed(1), 1u64));
    });
}

#[test]
fn query_result_fails_if_result_not_stored() {
    new_test_ext().execute_with(|| {
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1), QuantumJobType::Simulation,
            vec![1u8], None, None, None,
        ));
        assert_err!(
            QuantumComputing::query_result(RuntimeOrigin::signed(1), 1u64),
            Error::<Test>::JobNotFound
        );
    });
}

#[test]
fn query_result_fails_for_nonexistent_job() {
    new_test_ext().execute_with(|| {
        assert_err!(
            QuantumComputing::query_result(RuntimeOrigin::signed(1), 999u64),
            Error::<Test>::JobNotFound
        );
    });
}

// ── integration ──────────────────────────────────────────────────────────────

#[test]
fn integration_full_drug_discovery_workflow() {
    new_test_ext().execute_with(|| {
        // Register IBM Quantum integration point
        assert_ok!(QuantumComputing::register_integration_point(
            RuntimeOrigin::signed(1), 1u32,
            b"IBM Quantum".to_vec(), b"https://quantum.ibm.com".to_vec(),
            vec![QuantumCapability::Simulation, QuantumCapability::Optimization],
        ));

        // Submit drug discovery job with patient link
        let patient_health_hash = H256::from_slice(&[7u8; 32]);
        assert_ok!(QuantumComputing::submit_job(
            RuntimeOrigin::signed(1),
            QuantumJobType::DrugDiscovery,
            b"molecular_parameters".to_vec(),
            Some(1u32),
            Some(100u64),
            Some(patient_health_hash),
        ));

        // Store result with patient link preserved
        assert_ok!(QuantumComputing::store_result(
            RuntimeOrigin::signed(1), 1u64,
            b"binding_affinity_results".to_vec(),
            result_hash(42)
        ));

        let result = QuantumResults::<Test>::get(1u64).unwrap();
        assert_eq!(result.patient, Some(100u64));
        assert_eq!(result.health_record_hash, Some(patient_health_hash));
        assert_eq!(result.result_hash, result_hash(42));

        // Query the result
        assert_ok!(QuantumComputing::query_result(RuntimeOrigin::signed(1), 1u64));
    });
}

#[test]
fn integration_multiple_jobs_with_results() {
    new_test_ext().execute_with(|| {
        // Submit several different types of jobs
        for (i, jtype) in [
            QuantumJobType::VQE, QuantumJobType::QML, QuantumJobType::ProteinFolding
        ].into_iter().enumerate() {
            assert_ok!(QuantumComputing::submit_job(
                RuntimeOrigin::signed(1), jtype, vec![i as u8; 16], None, None, None,
            ));
        }

        // Store results for all
        for job_id in 1u64..=3 {
            assert_ok!(QuantumComputing::store_result(
                RuntimeOrigin::signed(1), job_id,
                vec![job_id as u8; 32], result_hash(job_id as u8),
            ));
        }

        // Verify all jobs completed
        for job_id in 1u64..=3 {
            assert_eq!(QuantumJobs::<Test>::get(job_id).unwrap().status, JobStatus::Completed);
        }
    });
}

