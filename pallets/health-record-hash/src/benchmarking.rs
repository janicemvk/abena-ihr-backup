//! Benchmarks for pallet-health-record-hash.
//!
//! Targets:
//!   create_record_hash         – baseline: create fresh record
//!   update_record_hash         – update existing record
//!   grant_record_access        – grant access to a record
//!   revoke_record_access       – revoke access from a record
//!   access_record              – access with n existing log entries (linear)
//!   verify_record_integrity    – verify hash against stored value
//!   link_to_quantum_result     – link record to quantum attestation
//!   access_record_full_log     – worst-case: access log at capacity (100 entries)

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_system::RawOrigin;
use sp_runtime::traits::Hash as HashTrait;

const SEED: u32 = 0;

/// Build a `BoundedVec<u8, ConstU32<512>>` with `n` bytes.
fn sig_bytes(n: usize) -> BoundedVec<u8, ConstU32<512>> {
    let v: sp_std::vec::Vec<u8> = (0..n).map(|i| (i % 256) as u8).collect();
    BoundedVec::truncate_from(v)
}

/// Build a test `T::Hash` from a u32 seed (deterministic).
fn make_hash<T: Config>(seed: u32) -> T::Hash {
    let mut bytes = [0u8; 32];
    bytes[0..4].copy_from_slice(&seed.to_le_bytes());
    T::Hashing::hash(&bytes)
}

/// Insert a record directly into `RecordHashStore` without validation.
fn insert_record<T: Config>(
    record_id: T::Hash,
    patient: T::AccountId,
    version: u32,
    previous_version: Option<T::Hash>,
) {
    RecordHashStore::<T>::insert(
        record_id,
        RecordHash::<T> {
            record_id,
            patient_id: patient,
            record_hash: [0xABu8; 32],
            ipfs_cid: None,
            record_type: RecordTypeSpec::ClinicalNote,
            therapeutic_modality: TherapeuticModality::WesternMedicine,
            created_at: 0u64,
            updated_at: 0u64,
            version,
            previous_version,
            provider_signature: sig_bytes(32),
            encryption_key_hash: [0u8; 32],
            active: true,
        },
    );
}

benchmarks! {

    // ── create_record_hash ─────────────────────────────────────────────────
    // Baseline: provider creates a brand-new record (no prior state).
    create_record_hash {
        let provider: T::AccountId = whitelisted_caller();
        let patient: T::AccountId  = account("patient", 0, SEED);
        let record_id = make_hash::<T>(1u32);
        let sig = sig_bytes(32);
    }: _(
        RawOrigin::Signed(provider.clone()),
        record_id,
        patient,
        [0xABu8; 32],
        None,
        RecordTypeSpec::ClinicalNote,
        TherapeuticModality::WesternMedicine,
        sig,
        [0u8; 32]
    )
    verify {
        assert!(RecordHashStore::<T>::contains_key(record_id));
    }

    // ── update_record_hash ─────────────────────────────────────────────────
    // Update an existing record (v=1 → v=2); provider is the patient.
    update_record_hash {
        let caller: T::AccountId = whitelisted_caller();
        let record_id = make_hash::<T>(10u32);
        insert_record::<T>(record_id, caller.clone(), 1, None);
        let sig = sig_bytes(32);
    }: _(
        RawOrigin::Signed(caller.clone()),
        record_id,
        [0xCDu8; 32],
        None,
        sig
    )
    verify {
        assert_eq!(RecordHashStore::<T>::get(record_id).map(|e| e.version), Some(2));
    }

    // ── grant_record_access ────────────────────────────────────────────────
    // Grant read access to an accessor for an existing record.
    grant_record_access {
        let patient: T::AccountId  = whitelisted_caller();
        let accessor: T::AccountId = account("accessor", 0, SEED);
        let record_id = make_hash::<T>(20u32);
        insert_record::<T>(record_id, patient.clone(), 1, None);
        let expiry: BlockNumberFor<T> = 1000u32.into();
    }: _(RawOrigin::Signed(patient.clone()), record_id, accessor.clone(), expiry)
    verify {
        assert!(AccessGrants::<T>::contains_key(record_id, &accessor));
    }

    // ── revoke_record_access ───────────────────────────────────────────────
    revoke_record_access {
        let patient: T::AccountId  = whitelisted_caller();
        let accessor: T::AccountId = account("accessor", 0, SEED);
        let record_id = make_hash::<T>(30u32);
        insert_record::<T>(record_id, patient.clone(), 1, None);
        let expiry: BlockNumberFor<T> = 1000u32.into();
        Pallet::<T>::grant_record_access(
            RawOrigin::Signed(patient.clone()).into(),
            record_id,
            accessor.clone(),
            expiry,
        )?;
    }: _(RawOrigin::Signed(patient.clone()), record_id, accessor.clone())
    verify {
        assert!(!AccessGrants::<T>::contains_key(record_id, &accessor));
    }

    // ── access_record ──────────────────────────────────────────────────────
    // Worst-case: n existing entries in the AccessLog for this (record_id, accessor).
    // BoundedVec decode/encode cost is O(n); cap is 100 entries.
    access_record {
        let n in 0 .. 99u32;

        let patient: T::AccountId = whitelisted_caller();
        let record_id = make_hash::<T>(40u32);
        insert_record::<T>(record_id, patient.clone(), 1, None);

        // Pre-fill n existing log entries for (record_id, patient).
        if n > 0 {
            let existing: BoundedVec<AccessRecord<T>, ConstU32<100>> = {
                let mut v = sp_std::vec::Vec::with_capacity(n as usize);
                for _ in 0..n {
                    v.push(AccessRecord::<T> {
                        accessor: patient.clone(),
                        block: 0u32.into(),
                        granted: true,
                        emergency_override: false,
                    });
                }
                BoundedVec::truncate_from(v)
            };
            AccessLog::<T>::insert(record_id, &patient, existing);
        }
    }: _(RawOrigin::Signed(patient.clone()), record_id)
    verify {
        let log = AccessLog::<T>::get(record_id, &patient);
        assert!(log.len() > n as usize);
    }

    // ── verify_record_integrity ────────────────────────────────────────────
    // Baseline O(1): read record and compare hash.
    // Additional variant `verify_record_integrity_with_versions` models a
    // version chain of depth v.
    verify_record_integrity {
        let caller: T::AccountId = whitelisted_caller();
        let record_id = make_hash::<T>(50u32);
        insert_record::<T>(record_id, caller.clone(), 1, None);
    }: _(RawOrigin::Signed(caller.clone()), record_id, [0xABu8; 32])
    verify {
        // Event was emitted; no error means success.
    }

    // ── verify_record_integrity (with version chain depth v) ──────────────
    // Models building a deep version chain, then verifying the latest entry.
    // `verify_record_integrity` reads the record directly (O(1)) but the chain
    // represents realistic storage state for worst-case estimation.
    verify_record_integrity_with_versions {
        let v in 1 .. 100u32;

        let provider: T::AccountId = whitelisted_caller();
        let record_id = make_hash::<T>(51u32);

        // Build a chain of v versions in RecordHashStore.
        let mut prev: Option<T::Hash> = None;
        for i in 0..v {
            let vid = make_hash::<T>(1000 + i);
            insert_record::<T>(vid, provider.clone(), i + 1, prev);
            prev = Some(vid);
        }
        // Latest record with link back to chain.
        RecordHashStore::<T>::insert(
            record_id,
            RecordHash::<T> {
                record_id,
                patient_id: provider.clone(),
                record_hash: [0xABu8; 32],
                ipfs_cid: None,
                record_type: RecordTypeSpec::ClinicalNote,
                therapeutic_modality: TherapeuticModality::WesternMedicine,
                created_at: 0u64,
                updated_at: 0u64,
                version: v + 1,
                previous_version: prev,
                provider_signature: sig_bytes(32),
                encryption_key_hash: [0u8; 32],
                active: true,
            },
        );
    }: verify_record_integrity(RawOrigin::Signed(provider.clone()), record_id, [0xABu8; 32])
    verify {}

    // ── link_to_quantum_result ─────────────────────────────────────────────
    link_to_quantum_result {
        let caller: T::AccountId = whitelisted_caller();
        let record_id  = make_hash::<T>(60u32);
        let qr_id      = make_hash::<T>(61u32);
        insert_record::<T>(record_id, caller.clone(), 1, None);
    }: _(RawOrigin::Signed(caller.clone()), record_id, qr_id)
    verify {
        assert!(QuantumResultLinks::<T>::contains_key(record_id));
    }

    impl_benchmark_test_suite!(
        Pallet,
        crate::mock::new_test_ext(),
        crate::mock::Test,
    );
}
