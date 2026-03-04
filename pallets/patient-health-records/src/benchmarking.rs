//! Benchmarks for patient-health-records pallet.
//!
//! Covers all 5 extrinsics: create_health_record, update_health_record,
//! grant_access, revoke_access, update_encryption_metadata.

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_support::BoundedVec;
use frame_system::RawOrigin;

fn kyber_metadata() -> EncryptionMetadataRecord {
    EncryptionMetadataRecord {
        algorithm: EncryptionAlgorithm::Kyber,
        parameters: BoundedVec::default(),
        kdf: BoundedVec::default(),
        metadata: BoundedVec::default(),
    }
}

benchmarks! {

    // ── create_health_record ─────────────────────────────────────────────────
    create_health_record {
        let caller: T::AccountId = whitelisted_caller();
        let encrypted_data = vec![0u8; 1024];
    }: _(RawOrigin::Signed(caller.clone()), encrypted_data, kyber_metadata())
    verify {
        assert!(HealthRecords::<T>::contains_key(&caller));
        assert!(EncryptionMetadata::<T>::contains_key(&caller));
    }

    // ── update_health_record ─────────────────────────────────────────────────
    update_health_record {
        let caller: T::AccountId = whitelisted_caller();
        Pallet::<T>::create_health_record(
            RawOrigin::Signed(caller.clone()).into(),
            vec![0u8; 512],
            kyber_metadata(),
        )?;
        let new_data = vec![1u8; 1024];
    }: _(RawOrigin::Signed(caller.clone()), caller.clone(), new_data)
    verify {
        assert!(HealthRecords::<T>::contains_key(&caller));
    }

    // ── grant_access ─────────────────────────────────────────────────────────
    grant_access {
        let patient: T::AccountId = whitelisted_caller();
        let doctor: T::AccountId  = account("doctor", 0, 0);
        let doctor_key            = doctor.clone();
        Pallet::<T>::create_health_record(
            RawOrigin::Signed(patient.clone()).into(),
            vec![0u8; 512],
            kyber_metadata(),
        )?;
    }: _(RawOrigin::Signed(patient.clone()), doctor, PermissionLevel::Read)
    verify {
        assert!(AccessPermissions::<T>::contains_key(&patient, &doctor_key));
    }

    // ── revoke_access ────────────────────────────────────────────────────────
    revoke_access {
        let patient: T::AccountId = whitelisted_caller();
        let doctor: T::AccountId  = account("doctor", 0, 0);
        let doctor_key            = doctor.clone();
        Pallet::<T>::create_health_record(
            RawOrigin::Signed(patient.clone()).into(),
            vec![0u8; 512],
            kyber_metadata(),
        )?;
        Pallet::<T>::grant_access(
            RawOrigin::Signed(patient.clone()).into(),
            doctor.clone(),
            PermissionLevel::Read,
        )?;
    }: _(RawOrigin::Signed(patient.clone()), doctor)
    verify {
        assert!(!AccessPermissions::<T>::contains_key(&patient, &doctor_key));
    }

    // ── update_encryption_metadata ───────────────────────────────────────────
    update_encryption_metadata {
        let caller: T::AccountId = whitelisted_caller();
        Pallet::<T>::create_health_record(
            RawOrigin::Signed(caller.clone()).into(),
            vec![0u8; 512],
            kyber_metadata(),
        )?;
        let new_metadata = EncryptionMetadataRecord {
            algorithm: EncryptionAlgorithm::Dilithium,
            parameters: BoundedVec::default(),
            kdf:        BoundedVec::default(),
            metadata:   BoundedVec::default(),
        };
    }: _(RawOrigin::Signed(caller.clone()), new_metadata)
    verify {
        let stored = EncryptionMetadata::<T>::get(&caller).unwrap();
        assert_eq!(stored.algorithm, EncryptionAlgorithm::Dilithium);
    }

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}
