//! Comprehensive tests for pallet-quantum-results.
//!
//! Coverage:
//!  - Algorithm registration & version updates
//!  - Quantum attestation (all algorithm types, duplicate guard)
//!  - IBM key registration & signature verification
//!  - Backend registration & job completion status
//!  - Patient linking & query helpers
//!  - Compliance certificate requests
//!  - Batch job grouping
//!  - Circuit metadata & quality metrics / confidence scoring
//!  - Queue management (enqueue)
//!  - Integration workflow
//!  - Edge cases (large values, pseudonym collision resistance, etc.)

use crate::mock::*;
use crate::pallet::{
    AlgorithmRegistry, BatchJobs, CircuitMetadataMap, Error, Event, IBMBackendRegistry,
    IBMQuantumKeys, JobIdToHash, Pallet as QR, PatientQuantumResults, QualityMetricsMap,
    QuantumAlgorithm, QuantumJobQueue, QuantumResults,
};
use codec::Encode;
use frame_support::{assert_noop, assert_ok};
use sp_core::H256;
use sp_runtime::traits::{BlakeTwo256, Hash};

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

/// Compute the on-chain job_id_hash the same way the pallet does.
fn job_id_hash(job: &[u8]) -> H256 {
    use sp_runtime::BoundedVec;
    let bounded: BoundedVec<u8, crate::pallet::JobIdMaxLen> =
        BoundedVec::try_from(job.to_vec()).unwrap();
    BlakeTwo256::hash_of(&bounded.encode())
}

fn register_backend(backend: &[u8]) {
    assert_ok!(QR::<Test>::register_ibm_backend(
        RuntimeOrigin::root(),
        backend.to_vec(),
        b"Test Backend".to_vec(),
        127,
        None,
    ));
}

/// Register an algorithm and return its hash.
fn register_algo(owner: u64, alg: QuantumAlgorithm, hash_seed: u8) -> H256 {
    let h = h256(hash_seed);
    assert_ok!(QR::<Test>::register_algorithm(
        RuntimeOrigin::signed(owner),
        h,
        alg,
        1,
        b"test algorithm".to_vec(),
    ));
    h
}

/// Attest a quantum result. Returns the job_id_hash.
fn attest(
    origin: u64,
    job: &[u8],
    pseudonym: H256,
    alg: QuantumAlgorithm,
    result: H256,
) -> H256 {
    assert_ok!(QR::<Test>::attest_quantum_result(
        RuntimeOrigin::signed(origin),
        job.to_vec(),
        pseudonym,
        alg,
        1,
        h256(0xaa),
        result,
        vec![],       // no IBM signature → verified = false
        1_700_000_000,
        20,
        6,
        8192,
        None,
    ));
    job_id_hash(job)
}

// ─────────────────────────────────────────────────────────────────────────────
// 1. ALGORITHM REGISTRATION
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn register_algorithm_stores_metadata() {
    new_test_ext().execute_with(|| {
        let alg_hash = h256(0x01);
        assert_ok!(QR::<Test>::register_algorithm(
            RuntimeOrigin::signed(ALICE),
            alg_hash,
            QuantumAlgorithm::VQE,
            1,
            b"VQE for molecular energy".to_vec(),
        ));

        let meta = AlgorithmRegistry::<Test>::get(alg_hash).unwrap();
        assert_eq!(meta.algorithm_type, QuantumAlgorithm::VQE);
        assert_eq!(meta.version, 1);
        assert_eq!(meta.owner, ALICE);
    });
}

#[test]
fn register_algorithm_emits_event() {
    new_test_ext().execute_with(|| {
        let alg_hash = h256(0x02);
        assert_ok!(QR::<Test>::register_algorithm(
            RuntimeOrigin::signed(ALICE),
            alg_hash,
            QuantumAlgorithm::QML,
            2,
            b"QML classifier".to_vec(),
        ));
        System::assert_has_event(
            Event::<Test>::AlgorithmRegistered {
                algorithm_hash: alg_hash,
                algorithm_type: QuantumAlgorithm::QML,
                version: 2,
            }
            .into(),
        );
    });
}

#[test]
fn register_algorithm_overwrites_if_same_hash() {
    // The pallet does a plain insert; second call with same hash overwrites.
    new_test_ext().execute_with(|| {
        let h = h256(0x03);
        assert_ok!(QR::<Test>::register_algorithm(
            RuntimeOrigin::signed(ALICE),
            h,
            QuantumAlgorithm::VQE,
            1,
            b"first".to_vec(),
        ));
        assert_ok!(QR::<Test>::register_algorithm(
            RuntimeOrigin::signed(ALICE),
            h,
            QuantumAlgorithm::VQE,
            2,
            b"overwrite".to_vec(),
        ));
        assert_eq!(AlgorithmRegistry::<Test>::get(h).unwrap().version, 2);
    });
}

#[test]
fn register_algorithm_description_too_long_fails() {
    new_test_ext().execute_with(|| {
        // Description is stored in a BoundedVec<u8, 256>; > 256 bytes should error.
        let long_desc = vec![b'x'; 257];
        assert_noop!(
            QR::<Test>::register_algorithm(
                RuntimeOrigin::signed(ALICE),
                h256(0x04),
                QuantumAlgorithm::QAOA,
                1,
                long_desc,
            ),
            Error::<Test>::JobIdTooLong
        );
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 2. UPDATE ALGORITHM VERSION
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn update_algorithm_version_works() {
    new_test_ext().execute_with(|| {
        let h = register_algo(ALICE, QuantumAlgorithm::VQE, 0x10);
        assert_ok!(QR::<Test>::update_algorithm_version(
            RuntimeOrigin::signed(ALICE),
            h,
            3,
            b"improved VQE".to_vec(),
        ));
        let meta = AlgorithmRegistry::<Test>::get(h).unwrap();
        assert_eq!(meta.version, 3);
    });
}

#[test]
fn update_algorithm_version_emits_event() {
    new_test_ext().execute_with(|| {
        let h = register_algo(ALICE, QuantumAlgorithm::VQE, 0x11);
        assert_ok!(QR::<Test>::update_algorithm_version(
            RuntimeOrigin::signed(ALICE),
            h,
            5,
            b"v5".to_vec(),
        ));
        System::assert_has_event(
            Event::<Test>::AlgorithmVersionUpdated { algorithm_hash: h, new_version: 5 }.into(),
        );
    });
}

#[test]
fn update_algorithm_version_fails_for_non_owner() {
    new_test_ext().execute_with(|| {
        let h = register_algo(ALICE, QuantumAlgorithm::QML, 0x12);
        assert_noop!(
            QR::<Test>::update_algorithm_version(
                RuntimeOrigin::signed(BOB),
                h,
                2,
                b"BOB hijack".to_vec(),
            ),
            Error::<Test>::PatientNotAuthorized
        );
    });
}

#[test]
fn update_algorithm_version_fails_for_unknown_hash() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            QR::<Test>::update_algorithm_version(
                RuntimeOrigin::signed(ALICE),
                h256(0xFF),
                1,
                b"none".to_vec(),
            ),
            Error::<Test>::AlgorithmNotRegistered
        );
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 3. QUANTUM ATTESTATION
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn attest_quantum_result_stores_attestation() {
    new_test_ext().execute_with(|| {
        let pseudonym = h256(0x20);
        let result_hash = h256(0x21);
        let jid = job_id("vqe-001");

        assert_ok!(QR::<Test>::attest_quantum_result(
            RuntimeOrigin::signed(ALICE),
            jid.clone(),
            pseudonym,
            QuantumAlgorithm::VQE,
            1,
            h256(0xAA),
            result_hash,
            vec![],
            1_700_000_000,
            20,
            6,
            8192,
            None,
        ));

        let jh = job_id_hash(&jid);
        let att = QuantumResults::<Test>::get(jh).unwrap();
        assert_eq!(att.result_hash, result_hash);
        assert_eq!(att.patient_pseudonym, pseudonym);
        assert_eq!(att.algorithm_type, QuantumAlgorithm::VQE);
        assert_eq!(att.circuit_depth, 20);
        assert_eq!(att.qubit_count, 6);
        assert_eq!(att.shots, 8192);
        assert_eq!(att.execution_timestamp, 1_700_000_000);
    });
}

#[test]
fn attest_quantum_result_populates_job_id_index() {
    new_test_ext().execute_with(|| {
        let jid = job_id("idx-001");
        let jh = attest(ALICE, &jid, h256(0x30), QuantumAlgorithm::QML, h256(0x31));

        use sp_runtime::BoundedVec;
        let bounded: BoundedVec<u8, crate::pallet::JobIdMaxLen> =
            BoundedVec::try_from(jid).unwrap();
        let stored_hash = JobIdToHash::<Test>::get(&bounded).unwrap();
        assert_eq!(stored_hash, jh);
    });
}

#[test]
fn attest_quantum_result_adds_to_patient_list() {
    new_test_ext().execute_with(|| {
        let pseudonym = h256(0x40);
        let jh = attest(ALICE, &job_id("patient-001"), pseudonym, QuantumAlgorithm::QAOA, h256(0x41));
        let list = PatientQuantumResults::<Test>::get(pseudonym);
        assert!(list.contains(&jh));
    });
}

#[test]
fn attest_quantum_result_emits_event() {
    new_test_ext().execute_with(|| {
        let pseudonym = h256(0x50);
        let jid = job_id("event-001");
        let jh = job_id_hash(&jid);
        attest(ALICE, &jid, pseudonym, QuantumAlgorithm::GroversSearch, h256(0x51));
        System::assert_has_event(
            Event::<Test>::QuantumResultAttested {
                job_id_hash: jh,
                algorithm_type: QuantumAlgorithm::GroversSearch,
                patient_pseudonym: pseudonym,
                verified: false, // no IBM key registered → always false
            }
            .into(),
        );
    });
}

#[test]
fn attest_quantum_result_rejects_duplicate_job_id() {
    new_test_ext().execute_with(|| {
        let jid = job_id("dup-001");
        attest(ALICE, &jid, h256(0x60), QuantumAlgorithm::VQE, h256(0x61));
        assert_noop!(
            QR::<Test>::attest_quantum_result(
                RuntimeOrigin::signed(ALICE),
                jid,
                h256(0x60),
                QuantumAlgorithm::VQE,
                1,
                h256(0xAA),
                h256(0x62),
                vec![],
                0,
                5,
                4,
                1024,
                None,
            ),
            Error::<Test>::DuplicateJobId
        );
    });
}

#[test]
fn attest_quantum_result_rejects_job_id_too_long() {
    new_test_ext().execute_with(|| {
        let long_id = vec![b'x'; 65]; // JobIdMaxLen = 64
        assert_noop!(
            QR::<Test>::attest_quantum_result(
                RuntimeOrigin::signed(ALICE),
                long_id,
                h256(0x70),
                QuantumAlgorithm::VQE,
                1,
                h256(0xAA),
                h256(0x71),
                vec![],
                0,
                5,
                4,
                1024,
                None,
            ),
            Error::<Test>::JobIdTooLong
        );
    });
}

#[test]
fn attest_quantum_result_rejects_signature_too_long() {
    new_test_ext().execute_with(|| {
        let long_sig = vec![0u8; 513]; // SignatureMaxLen = 512
        assert_noop!(
            QR::<Test>::attest_quantum_result(
                RuntimeOrigin::signed(ALICE),
                job_id("sig-long"),
                h256(0x80),
                QuantumAlgorithm::VQE,
                1,
                h256(0xAA),
                h256(0x81),
                long_sig,
                0,
                5,
                4,
                1024,
                None,
            ),
            Error::<Test>::SignatureTooLong
        );
    });
}

#[test]
fn attest_with_linked_clinical_module() {
    new_test_ext().execute_with(|| {
        let jid = job_id("clin-001");
        assert_ok!(QR::<Test>::attest_quantum_result(
            RuntimeOrigin::signed(ALICE),
            jid.clone(),
            h256(0x90),
            QuantumAlgorithm::QML,
            1,
            h256(0xAA),
            h256(0x91),
            vec![],
            0,
            10,
            5,
            4096,
            Some(b"module-002-drug-interactions".to_vec()),
        ));
        let att = QuantumResults::<Test>::get(job_id_hash(&jid)).unwrap();
        assert!(att.linked_clinical_module.is_some());
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 4. ALL ALGORITHM TYPES
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn all_algorithm_variants_can_be_attested() {
    let variants = [
        QuantumAlgorithm::VQE,
        QuantumAlgorithm::QML,
        QuantumAlgorithm::QAOA,
        QuantumAlgorithm::QuantumSampling,
        QuantumAlgorithm::GroversSearch,
        QuantumAlgorithm::Custom,
    ];
    for (i, alg) in variants.into_iter().enumerate() {
        new_test_ext().execute_with(|| {
            let tag = format!("alg-{}", i);
            let jid = job_id(&tag);
            let pseudonym = h256(i as u8);
            assert_ok!(QR::<Test>::attest_quantum_result(
                RuntimeOrigin::signed(ALICE),
                jid.clone(),
                pseudonym,
                alg.clone(),
                1,
                h256(0xAA),
                h256(0xBB),
                vec![],
                0,
                5,
                4,
                1024,
                None,
            ));
            let att = QuantumResults::<Test>::get(job_id_hash(&jid)).unwrap();
            assert_eq!(att.algorithm_type, alg);
        });
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// 5. IBM KEY REGISTRATION & SIGNATURE VERIFICATION
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn register_ibm_key_requires_root() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            QR::<Test>::register_ibm_key(
                RuntimeOrigin::signed(ALICE),
                b"key-001".to_vec(),
                vec![0u8; 32],
            ),
            sp_runtime::traits::BadOrigin
        );
    });
}

#[test]
fn register_ibm_key_stores_entry() {
    new_test_ext().execute_with(|| {
        assert_ok!(QR::<Test>::register_ibm_key(
            RuntimeOrigin::root(),
            b"ibm-key-1".to_vec(),
            vec![1u8; 32],
        ));
        let kid: sp_runtime::BoundedVec<u8, sp_runtime::traits::ConstU32<32>> =
            sp_runtime::BoundedVec::try_from(b"ibm-key-1".to_vec()).unwrap();
        assert!(IBMQuantumKeys::<Test>::contains_key(&kid));
    });
}

#[test]
fn register_ibm_key_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(QR::<Test>::register_ibm_key(
            RuntimeOrigin::root(),
            b"ev-key".to_vec(),
            vec![2u8; 32],
        ));
        let kid: sp_runtime::BoundedVec<u8, sp_runtime::traits::ConstU32<32>> =
            sp_runtime::BoundedVec::try_from(b"ev-key".to_vec()).unwrap();
        System::assert_has_event(Event::<Test>::IBMKeyRegistered { key_id: kid }.into());
    });
}

#[test]
fn verify_ibm_signature_emits_false_when_no_key_registered() {
    new_test_ext().execute_with(|| {
        let jid = job_id("sig-001");
        let jh = attest(ALICE, &jid, h256(0xA0), QuantumAlgorithm::VQE, h256(0xA1));

        assert_ok!(QR::<Test>::verify_ibm_signature(RuntimeOrigin::signed(ALICE), jh));
        System::assert_has_event(
            Event::<Test>::IBMSignatureVerified { job_id_hash: jh, valid: false }.into(),
        );
    });
}

#[test]
fn verify_ibm_signature_fails_for_missing_attestation() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            QR::<Test>::verify_ibm_signature(RuntimeOrigin::signed(ALICE), h256(0xFF)),
            Error::<Test>::AttestationNotFound
        );
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 6. BACKEND REGISTRATION
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn register_ibm_backend_requires_root() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            QR::<Test>::register_ibm_backend(
                RuntimeOrigin::signed(ALICE),
                b"ibm_brisbane".to_vec(),
                b"IBM Brisbane".to_vec(),
                127,
                None,
            ),
            sp_runtime::traits::BadOrigin
        );
    });
}

#[test]
fn register_ibm_backend_stores_entry() {
    new_test_ext().execute_with(|| {
        register_backend(b"ibm_brisbane");
        let bid: sp_runtime::BoundedVec<u8, sp_runtime::traits::ConstU32<32>> =
            sp_runtime::BoundedVec::try_from(b"ibm_brisbane".to_vec()).unwrap();
        let info = IBMBackendRegistry::<Test>::get(&bid).unwrap();
        assert_eq!(info.qubit_count, 127);
        assert!(info.available);
    });
}

#[test]
fn register_ibm_backend_emits_event() {
    new_test_ext().execute_with(|| {
        register_backend(b"ibm_kyoto");
        let bid: sp_runtime::BoundedVec<u8, sp_runtime::traits::ConstU32<32>> =
            sp_runtime::BoundedVec::try_from(b"ibm_kyoto".to_vec()).unwrap();
        let name: sp_runtime::BoundedVec<u8, sp_runtime::traits::ConstU32<64>> =
            sp_runtime::BoundedVec::try_from(b"Test Backend".to_vec()).unwrap();
        System::assert_has_event(
            Event::<Test>::BackendRegistered { backend_id: bid, name }.into(),
        );
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 7. PATIENT LINKING
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn link_to_patient_updates_pseudonym() {
    new_test_ext().execute_with(|| {
        let original_pseudo = h256(0xB0);
        let new_pseudo = h256(0xB1);
        let jid = job_id("link-001");
        let jh = attest(ALICE, &jid, original_pseudo, QuantumAlgorithm::VQE, h256(0xB2));

        assert_ok!(QR::<Test>::link_to_patient(
            RuntimeOrigin::signed(ALICE),
            jh,
            new_pseudo,
        ));

        let att = QuantumResults::<Test>::get(jh).unwrap();
        assert_eq!(att.patient_pseudonym, new_pseudo);
        assert!(PatientQuantumResults::<Test>::get(new_pseudo).contains(&jh));
    });
}

#[test]
fn link_to_patient_emits_event() {
    new_test_ext().execute_with(|| {
        let jh = attest(ALICE, &job_id("link-ev"), h256(0xC0), QuantumAlgorithm::QML, h256(0xC1));
        let np = h256(0xC2);
        assert_ok!(QR::<Test>::link_to_patient(RuntimeOrigin::signed(ALICE), jh, np));
        System::assert_has_event(
            Event::<Test>::LinkedToPatient { job_id_hash: jh, patient_pseudonym: np }.into(),
        );
    });
}

#[test]
fn link_to_patient_fails_for_unknown_attestation() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            QR::<Test>::link_to_patient(RuntimeOrigin::signed(ALICE), h256(0xFF), h256(0x01)),
            Error::<Test>::AttestationNotFound
        );
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 8. COMPLIANCE CERTIFICATE
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn generate_compliance_certificate_emits_event() {
    new_test_ext().execute_with(|| {
        let jh = attest(ALICE, &job_id("cert-001"), h256(0xD0), QuantumAlgorithm::VQE, h256(0xD1));
        assert_ok!(QR::<Test>::generate_compliance_certificate(RuntimeOrigin::signed(ALICE), jh));
        System::assert_has_event(
            Event::<Test>::ComplianceCertificateRequested {
                job_id_hash: jh,
                requester: ALICE,
            }
            .into(),
        );
    });
}

#[test]
fn generate_compliance_certificate_fails_for_unknown_attestation() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            QR::<Test>::generate_compliance_certificate(RuntimeOrigin::signed(ALICE), h256(0xFF)),
            Error::<Test>::AttestationNotFound
        );
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 9. QUERY FUNCTIONS
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn query_patient_quantum_history_returns_all_jobs() {
    new_test_ext().execute_with(|| {
        let pseudonym = h256(0xE0);
        let jh1 = attest(ALICE, &job_id("history-1"), pseudonym, QuantumAlgorithm::VQE, h256(0xE1));
        let jh2 = attest(ALICE, &job_id("history-2"), pseudonym, QuantumAlgorithm::QML, h256(0xE2));
        let jh3 = attest(ALICE, &job_id("history-3"), pseudonym, QuantumAlgorithm::QAOA, h256(0xE3));

        let history = QR::<Test>::query_patient_quantum_history(pseudonym);
        assert_eq!(history.len(), 3);
        assert!(history.contains(&jh1));
        assert!(history.contains(&jh2));
        assert!(history.contains(&jh3));
    });
}

#[test]
fn query_patient_quantum_history_returns_empty_for_unknown_patient() {
    new_test_ext().execute_with(|| {
        let history = QR::<Test>::query_patient_quantum_history(h256(0xFF));
        assert!(history.is_empty());
    });
}

#[test]
fn get_quantum_result_succeeds_for_existing_job() {
    new_test_ext().execute_with(|| {
        let jid = job_id("get-001");
        let jh = attest(ALICE, &jid, h256(0xF0), QuantumAlgorithm::VQE, h256(0xF1));
        assert!(QuantumResults::<Test>::get(jh).is_some());
    });
}

#[test]
fn get_quantum_result_returns_none_for_missing_job() {
    new_test_ext().execute_with(|| {
        assert!(QuantumResults::<Test>::get(h256(0xFF)).is_none());
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 10. BATCH JOB GROUPING
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn submit_batch_job_works() {
    new_test_ext().execute_with(|| {
        let jh1 = attest(ALICE, &job_id("batch-a"), h256(0x10), QuantumAlgorithm::VQE, h256(0x11));
        let jh2 = attest(ALICE, &job_id("batch-b"), h256(0x12), QuantumAlgorithm::QML, h256(0x13));
        let analysis = h256(0x14);

        assert_ok!(QR::<Test>::submit_batch_job(
            RuntimeOrigin::signed(ALICE),
            analysis,
            vec![jh1, jh2],
        ));

        let stored = BatchJobs::<Test>::get(analysis).unwrap();
        assert_eq!(stored.len(), 2);
        assert!(stored.contains(&jh1));
        assert!(stored.contains(&jh2));
    });
}

#[test]
fn submit_batch_job_emits_event() {
    new_test_ext().execute_with(|| {
        let jh = attest(ALICE, &job_id("batch-ev"), h256(0x20), QuantumAlgorithm::VQE, h256(0x21));
        let analysis = h256(0x22);
        assert_ok!(QR::<Test>::submit_batch_job(
            RuntimeOrigin::signed(ALICE),
            analysis,
            vec![jh],
        ));
        System::assert_has_event(
            Event::<Test>::BatchSubmitted { analysis_id: analysis, job_count: 1 }.into(),
        );
    });
}

#[test]
fn submit_batch_job_fails_for_missing_attestation() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            QR::<Test>::submit_batch_job(
                RuntimeOrigin::signed(ALICE),
                h256(0x30),
                vec![h256(0xFF)],
            ),
            Error::<Test>::AttestationNotFound
        );
    });
}

#[test]
fn link_batch_results_updates_patient_linkage() {
    new_test_ext().execute_with(|| {
        let pseudonym = h256(0x40);
        let jh1 = attest(ALICE, &job_id("lb-a"), h256(0x41), QuantumAlgorithm::VQE, h256(0x42));
        let jh2 = attest(ALICE, &job_id("lb-b"), h256(0x41), QuantumAlgorithm::QML, h256(0x43));
        let analysis = h256(0x44);
        assert_ok!(QR::<Test>::submit_batch_job(
            RuntimeOrigin::signed(ALICE),
            analysis,
            vec![jh1, jh2],
        ));
        assert_ok!(QR::<Test>::link_batch_results(
            RuntimeOrigin::signed(ALICE),
            analysis,
            pseudonym,
        ));
        let list = PatientQuantumResults::<Test>::get(pseudonym);
        // Both jobs are now linked to pseudonym
        assert!(list.contains(&jh1));
        assert!(list.contains(&jh2));
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 11. CIRCUIT METADATA & QUALITY METRICS / CONFIDENCE
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn store_circuit_metadata_works() {
    new_test_ext().execute_with(|| {
        register_backend(b"ibm_eagle");
        let jh = attest(ALICE, &job_id("circ-001"), h256(0x50), QuantumAlgorithm::VQE, h256(0x51));
        assert_ok!(QR::<Test>::store_circuit_metadata(
            RuntimeOrigin::signed(ALICE),
            jh,
            b"ibm_eagle".to_vec(),
            42,
            999_000,
            1_000,
            None,
        ));
        let meta = CircuitMetadataMap::<Test>::get(jh).unwrap();
        assert_eq!(meta.transpilation_depth, 42);
        assert_eq!(meta.gate_fidelity_micro, 999_000);
    });
}

#[test]
fn store_circuit_metadata_fails_for_missing_attestation() {
    new_test_ext().execute_with(|| {
        register_backend(b"ibm_eagle2");
        assert_noop!(
            QR::<Test>::store_circuit_metadata(
                RuntimeOrigin::signed(ALICE),
                h256(0xFF),
                b"ibm_eagle2".to_vec(),
                10,
                990_000,
                500,
                None,
            ),
            Error::<Test>::AttestationNotFound
        );
    });
}

#[test]
fn calculate_result_confidence_stores_metrics() {
    new_test_ext().execute_with(|| {
        let jh = attest(ALICE, &job_id("conf-001"), h256(0x60), QuantumAlgorithm::QML, h256(0x61));
        assert_ok!(QR::<Test>::calculate_result_confidence(
            RuntimeOrigin::signed(ALICE),
            jh,
            1_000,       // 0.1% readout error
            999_000,     // 99.9% gate fidelity
            500_000,     // 50% mitigation factor
        ));
        let metrics = QualityMetricsMap::<Test>::get(jh).unwrap();
        // confidence = 1_000_000 – min(reduced_err, 1_000_000)
        assert!(metrics.confidence_score_micro > 0);
        assert!(metrics.confidence_score_micro <= 1_000_000);
    });
}

#[test]
fn calculate_result_confidence_emits_event() {
    new_test_ext().execute_with(|| {
        let jh = attest(ALICE, &job_id("conf-ev"), h256(0x70), QuantumAlgorithm::QAOA, h256(0x71));
        assert_ok!(QR::<Test>::calculate_result_confidence(
            RuntimeOrigin::signed(ALICE),
            jh,
            0,
            1_000_000,
            1_000_000,
        ));
        // confidence should be 1_000_000 (no errors, full mitigation)
        let metrics = QualityMetricsMap::<Test>::get(jh).unwrap();
        System::assert_has_event(
            Event::<Test>::ResultConfidenceCalculated {
                job_id_hash: jh,
                confidence_micro: metrics.confidence_score_micro,
            }
            .into(),
        );
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 12. QUEUE MANAGEMENT (enqueue_quantum_job)
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn enqueue_quantum_job_adds_to_queue() {
    new_test_ext().execute_with(|| {
        register_backend(b"ibm_q1");
        assert_ok!(QR::<Test>::enqueue_quantum_job(
            RuntimeOrigin::signed(ALICE),
            b"job-q-001".to_vec(),
            b"ibm_q1".to_vec(),
            h256(0x80),
            QuantumAlgorithm::VQE,
            1,
            h256(0xAA),
            0,
            10,
            5,
            2048,
            None,
        ));
        let q = QuantumJobQueue::<Test>::get();
        assert_eq!(q.len(), 1);
        assert_eq!(q[0].job_id.as_slice(), b"job-q-001");
    });
}

#[test]
fn enqueue_quantum_job_fails_for_unknown_backend() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            QR::<Test>::enqueue_quantum_job(
                RuntimeOrigin::signed(ALICE),
                b"job-q-bad".to_vec(),
                b"unknown_backend".to_vec(),
                h256(0x81),
                QuantumAlgorithm::VQE,
                1,
                h256(0xAA),
                0,
                10,
                5,
                2048,
                None,
            ),
            Error::<Test>::BackendUnavailable
        );
    });
}

#[test]
fn enqueue_quantum_job_fails_for_duplicate_job_id() {
    new_test_ext().execute_with(|| {
        register_backend(b"ibm_q2");
        assert_ok!(QR::<Test>::enqueue_quantum_job(
            RuntimeOrigin::signed(ALICE),
            b"job-dup".to_vec(),
            b"ibm_q2".to_vec(),
            h256(0x82),
            QuantumAlgorithm::VQE,
            1,
            h256(0xAA),
            0,
            5,
            4,
            1024,
            None,
        ));
        // Attest it to put it in QuantumResults storage
        assert_ok!(QR::<Test>::attest_quantum_result(
            RuntimeOrigin::signed(ALICE),
            b"job-dup".to_vec(),
            h256(0x82),
            QuantumAlgorithm::VQE,
            1,
            h256(0xAA),
            h256(0x83),
            vec![],
            0,
            5,
            4,
            1024,
            None,
        ));
        // Now enqueue again – should fail because QuantumResults already has it
        assert_noop!(
            QR::<Test>::enqueue_quantum_job(
                RuntimeOrigin::signed(ALICE),
                b"job-dup".to_vec(),
                b"ibm_q2".to_vec(),
                h256(0x82),
                QuantumAlgorithm::VQE,
                1,
                h256(0xAA),
                0,
                5,
                4,
                1024,
                None,
            ),
            Error::<Test>::DuplicateJobId
        );
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 13. VERIFY JOB COMPLETION
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn verify_job_completion_updates_queue_status() {
    new_test_ext().execute_with(|| {
        use crate::pallet::JobCompletionStatus;
        register_backend(b"ibm_q3");
        assert_ok!(QR::<Test>::enqueue_quantum_job(
            RuntimeOrigin::signed(ALICE),
            b"job-status".to_vec(),
            b"ibm_q3".to_vec(),
            h256(0x90),
            QuantumAlgorithm::VQE,
            1,
            h256(0xAA),
            0,
            5,
            4,
            1024,
            None,
        ));
        let jh = job_id_hash(b"job-status");
        assert_ok!(QR::<Test>::verify_job_completion(
            RuntimeOrigin::signed(ALICE),
            jh,
            JobCompletionStatus::Running,
            b"ibm_q3".to_vec(),
        ));
        let q = QuantumJobQueue::<Test>::get();
        assert_eq!(q[0].status, JobCompletionStatus::Running);
    });
}

#[test]
fn verify_job_completion_fails_for_unknown_backend() {
    new_test_ext().execute_with(|| {
        use crate::pallet::JobCompletionStatus;
        assert_noop!(
            QR::<Test>::verify_job_completion(
                RuntimeOrigin::signed(ALICE),
                h256(0x91),
                JobCompletionStatus::Completed,
                b"no_such_backend".to_vec(),
            ),
            Error::<Test>::BackendUnavailable
        );
    });
}

#[test]
fn verify_job_completion_fails_when_status_is_failed() {
    new_test_ext().execute_with(|| {
        use crate::pallet::JobCompletionStatus;
        register_backend(b"ibm_q4");
        assert_noop!(
            QR::<Test>::verify_job_completion(
                RuntimeOrigin::signed(ALICE),
                h256(0x92),
                JobCompletionStatus::Failed,
                b"ibm_q4".to_vec(),
            ),
            Error::<Test>::JobFailed
        );
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 14. INTEGRATION: complete quantum workflow
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn complete_quantum_workflow() {
    new_test_ext().execute_with(|| {
        // Step 1 – Register algorithm
        let alg_hash = h256(0x01);
        assert_ok!(QR::<Test>::register_algorithm(
            RuntimeOrigin::signed(ALICE),
            alg_hash,
            QuantumAlgorithm::VQE,
            1,
            b"VQE for treatment optimisation".to_vec(),
        ));

        // Step 2 – Register IBM backend
        register_backend(b"ibm_brisbane");

        // Step 3 – Attest quantum result
        let pseudonym = h256(0x02);
        let jid = job_id("workflow-001");
        let result_hash = h256(0x03);
        let jh = attest(ALICE, &jid, pseudonym, QuantumAlgorithm::VQE, result_hash);

        // Step 4 – Link to patient
        assert_ok!(QR::<Test>::link_to_patient(RuntimeOrigin::signed(ALICE), jh, pseudonym));

        // Step 5 – Store circuit metadata
        assert_ok!(QR::<Test>::store_circuit_metadata(
            RuntimeOrigin::signed(ALICE),
            jh,
            b"ibm_brisbane".to_vec(),
            25,
            998_000,
            2_000,
            None,
        ));

        // Step 6 – Calculate confidence
        assert_ok!(QR::<Test>::calculate_result_confidence(
            RuntimeOrigin::signed(ALICE),
            jh,
            2_000,
            998_000,
            800_000,
        ));

        // Step 7 – Compliance certificate
        assert_ok!(QR::<Test>::generate_compliance_certificate(RuntimeOrigin::signed(ALICE), jh));

        // Verify all state
        let att = QuantumResults::<Test>::get(jh).unwrap();
        assert_eq!(att.algorithm_type, QuantumAlgorithm::VQE);
        assert!(PatientQuantumResults::<Test>::get(pseudonym).contains(&jh));
        assert!(CircuitMetadataMap::<Test>::get(jh).is_some());
        assert!(QualityMetricsMap::<Test>::get(jh).is_some());
        System::assert_has_event(
            Event::<Test>::ComplianceCertificateRequested { job_id_hash: jh, requester: ALICE }
                .into(),
        );
    });
}

#[test]
fn multi_job_patient_all_algorithms_tracked() {
    new_test_ext().execute_with(|| {
        let pseudonym = h256(0xAB);
        let algs = [
            QuantumAlgorithm::VQE,
            QuantumAlgorithm::QML,
            QuantumAlgorithm::QAOA,
        ];
        for (i, alg) in algs.into_iter().enumerate() {
            attest(ALICE, &job_id(&format!("multi-{}", i)), pseudonym, alg, h256(i as u8));
        }
        let history = QR::<Test>::query_patient_quantum_history(pseudonym);
        assert_eq!(history.len(), 3);
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// 15. EDGE CASES
// ─────────────────────────────────────────────────────────────────────────────

#[test]
fn edge_case_max_qubit_count_127() {
    new_test_ext().execute_with(|| {
        assert_ok!(QR::<Test>::attest_quantum_result(
            RuntimeOrigin::signed(ALICE),
            job_id("edge-127q"),
            h256(0xC0),
            QuantumAlgorithm::VQE,
            1,
            h256(0xAA),
            h256(0xBB),
            vec![],
            0,
            50,
            127, // max qubit count for u8 is 255; 127 is valid
            8192,
            None,
        ));
        let jh = job_id_hash(&job_id("edge-127q"));
        assert_eq!(QuantumResults::<Test>::get(jh).unwrap().qubit_count, 127);
    });
}

#[test]
fn edge_case_deep_circuit() {
    new_test_ext().execute_with(|| {
        assert_ok!(QR::<Test>::attest_quantum_result(
            RuntimeOrigin::signed(ALICE),
            job_id("edge-deep"),
            h256(0xC1),
            QuantumAlgorithm::VQE,
            1,
            h256(0xAA),
            h256(0xBB),
            vec![],
            0,
            10_000, // very deep circuit
            20,
            8192,
            None,
        ));
        let jh = job_id_hash(&job_id("edge-deep"));
        assert_eq!(QuantumResults::<Test>::get(jh).unwrap().circuit_depth, 10_000);
    });
}

#[test]
fn edge_case_high_shot_count() {
    new_test_ext().execute_with(|| {
        assert_ok!(QR::<Test>::attest_quantum_result(
            RuntimeOrigin::signed(ALICE),
            job_id("edge-shots"),
            h256(0xC2),
            QuantumAlgorithm::QuantumSampling,
            1,
            h256(0xAA),
            h256(0xBB),
            vec![],
            0,
            10,
            5,
            1_000_000, // 1M shots
            None,
        ));
        let jh = job_id_hash(&job_id("edge-shots"));
        assert_eq!(QuantumResults::<Test>::get(jh).unwrap().shots, 1_000_000);
    });
}

#[test]
fn edge_case_pseudonym_collision_resistance() {
    new_test_ext().execute_with(|| {
        // Two different patients with different pseudonyms should have separate lists
        let pseudo_a = h256(0xD0);
        let pseudo_b = h256(0xD1);
        let jha = attest(ALICE, &job_id("col-a"), pseudo_a, QuantumAlgorithm::VQE, h256(0xD2));
        let jhb = attest(ALICE, &job_id("col-b"), pseudo_b, QuantumAlgorithm::VQE, h256(0xD3));

        assert!(PatientQuantumResults::<Test>::get(pseudo_a).contains(&jha));
        assert!(!PatientQuantumResults::<Test>::get(pseudo_a).contains(&jhb));
        assert!(PatientQuantumResults::<Test>::get(pseudo_b).contains(&jhb));
        assert!(!PatientQuantumResults::<Test>::get(pseudo_b).contains(&jha));
    });
}

#[test]
fn edge_case_confidence_score_perfect_hardware() {
    new_test_ext().execute_with(|| {
        let jh = attest(ALICE, &job_id("perf-hw"), h256(0xE0), QuantumAlgorithm::VQE, h256(0xE1));
        assert_ok!(QR::<Test>::calculate_result_confidence(
            RuntimeOrigin::signed(ALICE),
            jh,
            0,         // zero readout error
            1_000_000, // 100% gate fidelity
            1_000_000, // 100% mitigation
        ));
        let m = QualityMetricsMap::<Test>::get(jh).unwrap();
        assert_eq!(m.confidence_score_micro, 1_000_000); // perfect score
    });
}

#[test]
fn edge_case_confidence_score_worst_case_hardware() {
    new_test_ext().execute_with(|| {
        let jh = attest(ALICE, &job_id("worst-hw"), h256(0xE2), QuantumAlgorithm::VQE, h256(0xE3));
        assert_ok!(QR::<Test>::calculate_result_confidence(
            RuntimeOrigin::signed(ALICE),
            jh,
            1_000_000, // 100% readout error
            0,         // 0% gate fidelity
            0,         // no mitigation
        ));
        let m = QualityMetricsMap::<Test>::get(jh).unwrap();
        assert_eq!(m.confidence_score_micro, 0); // worst score
    });
}

#[test]
fn edge_case_confidence_does_not_overflow() {
    new_test_ext().execute_with(|| {
        let jh = attest(ALICE, &job_id("overflow"), h256(0xE4), QuantumAlgorithm::VQE, h256(0xE5));
        // All values at max u32 – should saturate, not panic
        assert_ok!(QR::<Test>::calculate_result_confidence(
            RuntimeOrigin::signed(ALICE),
            jh,
            u32::MAX,
            u32::MAX,
            u32::MAX,
        ));
        let m = QualityMetricsMap::<Test>::get(jh).unwrap();
        // Just verify it doesn't panic and returns a value in [0, 1_000_000]
        assert!(m.confidence_score_micro <= 1_000_000);
    });
}

#[test]
fn edge_case_job_id_exactly_64_bytes_allowed() {
    new_test_ext().execute_with(|| {
        let max_id = vec![b'x'; 64]; // exactly JobIdMaxLen
        assert_ok!(QR::<Test>::attest_quantum_result(
            RuntimeOrigin::signed(ALICE),
            max_id,
            h256(0xF0),
            QuantumAlgorithm::Custom,
            1,
            h256(0xAA),
            h256(0xBB),
            vec![],
            0,
            5,
            4,
            512,
            None,
        ));
    });
}

#[test]
fn edge_case_concurrent_attestations_different_jobs() {
    new_test_ext().execute_with(|| {
        let pseudonym = h256(0xF1);
        // Simulate multiple attestations in one block (no block advancement needed)
        for i in 0u8..10 {
            let tag = format!("concurrent-{}", i);
            attest(ALICE, &job_id(&tag), pseudonym, QuantumAlgorithm::QML, h256(i));
        }
        let history = QR::<Test>::query_patient_quantum_history(pseudonym);
        assert_eq!(history.len(), 10);
    });
}
