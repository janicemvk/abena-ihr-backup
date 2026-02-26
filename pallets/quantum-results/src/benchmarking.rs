//! Benchmarks for pallet-quantum-results.
//!
//! Targets:
//!   register_algorithm             – baseline: register a quantum algorithm
//!   attest_quantum_result          – baseline: attest a completed IBM Quantum job
//!   verify_ibm_signature           – verify stored IBM signature for an attestation
//!   link_to_patient                – link attestation to patient pseudonym
//!   generate_compliance_certificate – issue compliance certificate for attestation
//!   enqueue_quantum_job            – queue a new job for the off-chain worker
//!   query_patient_quantum_history  – block benchmark: iterate n stored results (linear)

use super::*;
use frame_benchmarking::{benchmarks, whitelisted_caller};
use frame_support::{traits::ConstU32, BoundedVec};
use frame_system::{pallet_prelude::BlockNumberFor, RawOrigin};
use sp_runtime::traits::Hash as HashTrait;

/// Build a deterministic `T::Hash` from a seed.
fn make_hash<T: Config>(seed: u32) -> T::Hash {
    let mut b = [0u8; 32];
    b[0..4].copy_from_slice(&seed.to_le_bytes());
    T::Hashing::hash(&b)
}

/// Construct a bounded job_id of exactly 32 bytes.
fn job_id_bytes() -> sp_std::vec::Vec<u8> {
    (0u8..32).collect()
}

/// Insert a ready-made attestation into storage without going through dispatch.
fn insert_attestation<T: Config>(
    job_id_hash: T::Hash,
    patient_pseudonym: T::Hash,
    job_id: BoundedVec<u8, JobIdMaxLen>,
) {
    let now: BlockNumberFor<T> = <frame_system::Pallet<T>>::block_number();
    let attestation = QuantumAttestation::<T> {
        job_id: job_id.clone(),
        patient_pseudonym,
        algorithm_type: QuantumAlgorithm::VQE,
        algorithm_version: 1u32,
        parameters_hash: make_hash::<T>(99u32),
        result_hash: make_hash::<T>(100u32),
        ibm_signature: BoundedVec::truncate_from(sp_std::vec![0u8; 4]),
        execution_timestamp: 1_700_000_000u64,
        circuit_depth: 10u32,
        qubit_count: 5u8,
        shots: 1024u32,
        verified: false,
        linked_clinical_module: None,
        created_at: now,
    };
    QuantumResults::<T>::insert(job_id_hash, &attestation);
    JobIdToHash::<T>::insert(&job_id, job_id_hash);

    // Also link to patient.
    PatientQuantumResults::<T>::mutate(patient_pseudonym, |list| {
        let _ = list.try_push(job_id_hash);
    });
}

/// Register a backend so `enqueue_quantum_job` can find it.
fn register_backend<T: Config>(backend_id: BoundedVec<u8, ConstU32<32>>) {
    IBMBackendRegistry::<T>::insert(
        &backend_id,
        IBMBackendInfo::<T> {
            backend_id: backend_id.clone(),
            name: BoundedVec::truncate_from(b"test_backend".to_vec()),
            available: true,
            qubit_count: 127u16,
            calibration_data_hash: None,
            registered_at: <frame_system::Pallet<T>>::block_number(),
        },
    );
}

benchmarks! {

    // ── register_algorithm ────────────────────────────────────────────────
    // Baseline: register a new algorithm.
    register_algorithm {
        let caller: T::AccountId = whitelisted_caller();
        let algo_hash = make_hash::<T>(1u32);
        let desc: sp_std::vec::Vec<u8> = sp_std::vec![b'V'; 32];
    }: _(
        RawOrigin::Signed(caller.clone()),
        algo_hash,
        QuantumAlgorithm::VQE,
        1u32,
        desc
    )
    verify {
        assert!(AlgorithmRegistry::<T>::contains_key(algo_hash));
    }

    // ── attest_quantum_result ─────────────────────────────────────────────
    // Baseline: attest a completed IBM Quantum job.
    attest_quantum_result {
        let caller: T::AccountId = whitelisted_caller();
        let job_id        = job_id_bytes();
        let patient_pseudo = make_hash::<T>(10u32);
        let params_hash   = make_hash::<T>(11u32);
        let result_hash   = make_hash::<T>(12u32);
        let sig: sp_std::vec::Vec<u8> = sp_std::vec![0u8; 64];
    }: _(
        RawOrigin::Signed(caller.clone()),
        job_id,
        patient_pseudo,
        QuantumAlgorithm::VQE,
        1u32,
        params_hash,
        result_hash,
        sig,
        1_700_000_000u64,
        10u32,
        5u8,
        1024u32,
        None::<sp_std::vec::Vec<u8>>
    )
    verify {
        // Either the attestation was stored, or an error was returned if sig
        // verification is strict. Weight is measured either way.
    }

    // ── verify_ibm_signature ──────────────────────────────────────────────
    // Verify the IBM signature stored with an existing attestation.
    verify_ibm_signature {
        let caller: T::AccountId = whitelisted_caller();
        let job_id_hash = make_hash::<T>(20u32);
        let patient_pseudo = make_hash::<T>(21u32);
        let job_id_b: BoundedVec<u8, JobIdMaxLen> =
            BoundedVec::truncate_from(job_id_bytes());
        insert_attestation::<T>(job_id_hash, patient_pseudo, job_id_b);
    }: _(RawOrigin::Signed(caller.clone()), job_id_hash)
    verify {}

    // ── link_to_patient ───────────────────────────────────────────────────
    // Link an existing attestation to a patient pseudonym.
    link_to_patient {
        let caller: T::AccountId = whitelisted_caller();
        let job_id_hash   = make_hash::<T>(30u32);
        let patient_pseudo = make_hash::<T>(31u32);
        let new_pseudo     = make_hash::<T>(32u32);
        let job_id_b: BoundedVec<u8, JobIdMaxLen> =
            BoundedVec::truncate_from(job_id_bytes());
        insert_attestation::<T>(job_id_hash, patient_pseudo, job_id_b);
    }: _(RawOrigin::Signed(caller.clone()), job_id_hash, new_pseudo)
    verify {
        let list = PatientQuantumResults::<T>::get(new_pseudo);
        assert!(list.contains(&job_id_hash));
    }

    // ── generate_compliance_certificate ───────────────────────────────────
    generate_compliance_certificate {
        let caller: T::AccountId = whitelisted_caller();
        let job_id_hash   = make_hash::<T>(40u32);
        let patient_pseudo = make_hash::<T>(41u32);
        let job_id_b: BoundedVec<u8, JobIdMaxLen> =
            BoundedVec::truncate_from(job_id_bytes());
        insert_attestation::<T>(job_id_hash, patient_pseudo, job_id_b);
    }: _(RawOrigin::Signed(caller.clone()), job_id_hash)
    verify {
        // Event ComplianceCertificateRequested was emitted (no storage write in this pallet).
    }

    // ── enqueue_quantum_job ───────────────────────────────────────────────
    // Queue a new job for the off-chain worker to pick up.
    enqueue_quantum_job {
        let caller: T::AccountId = whitelisted_caller();
        let patient_pseudo = make_hash::<T>(50u32);
        let params_hash    = make_hash::<T>(51u32);
        let job_id: sp_std::vec::Vec<u8> = sp_std::vec![b'J'; 32];
        let backend_vec: sp_std::vec::Vec<u8> = b"test_bknd".to_vec();
        // Register the backend so the dispatch check passes.
        let backend_b: BoundedVec<u8, ConstU32<32>> =
            BoundedVec::truncate_from(backend_vec.clone());
        register_backend::<T>(backend_b);
    }: _(
        RawOrigin::Signed(caller.clone()),
        job_id,
        backend_vec,
        patient_pseudo,
        QuantumAlgorithm::QML,
        1u32,
        params_hash,
        0u64,
        10u32,
        5u8,
        1024u32,
        None::<sp_std::vec::Vec<u8>>
    )
    verify {}

    // ── query_patient_quantum_history ─────────────────────────────────────
    // Block benchmark: cost scales with n results stored per patient.
    query_patient_quantum_history {
        let n in 1 .. 128u32;

        let patient_pseudo = make_hash::<T>(60u32);

        // Insert n attestation hashes into PatientQuantumResults.
        let mut entries: sp_std::vec::Vec<T::Hash> =
            sp_std::vec::Vec::with_capacity(n as usize);
        for i in 0..n {
            let h = make_hash::<T>(2000 + i);
            entries.push(h);
        }
        PatientQuantumResults::<T>::insert(
            patient_pseudo,
            BoundedVec::truncate_from(entries),
        );
    }: {
        let results = Pallet::<T>::query_patient_quantum_history(patient_pseudo);
        assert_eq!(results.len(), n as usize);
    }
    verify {}

    impl_benchmark_test_suite!(
        Pallet,
        crate::mock::new_test_ext(),
        crate::mock::Test,
    );
}
