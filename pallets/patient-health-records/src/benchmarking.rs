//! Benchmarking for patient health records pallet

use super::*;
use frame_benchmarking::{benchmarks, whitelisted_caller};
use frame_system::RawOrigin;

benchmarks! {
    create_health_record {
        let caller: T::AccountId = whitelisted_caller();
        let encrypted_data = vec![0u8; 1024];
        let metadata = EncryptionMetadataRecord {
            algorithm: EncryptionAlgorithm::Kyber,
            parameters: vec![],
            kdf: vec![],
            metadata: vec![],
        };
    }: _(RawOrigin::Signed(caller.clone()), encrypted_data, metadata)
    verify {
        assert!(HealthRecords::<T>::contains_key(&caller));
    }

    update_health_record {
        let caller: T::AccountId = whitelisted_caller();
        let encrypted_data = vec![0u8; 1024];
        let metadata = EncryptionMetadataRecord {
            algorithm: EncryptionAlgorithm::Kyber,
            parameters: vec![],
            kdf: vec![],
            metadata: vec![],
        };
        Pallet::<T>::create_health_record(
            RawOrigin::Signed(caller.clone()).into(),
            encrypted_data.clone(),
            metadata.clone(),
        )?;
        let new_data = vec![1u8; 1024];
    }: _(RawOrigin::Signed(caller.clone()), caller.clone(), new_data)
    verify {
        assert!(HealthRecords::<T>::contains_key(&caller));
    }

    grant_access {
        let patient: T::AccountId = whitelisted_caller();
        let doctor: T::AccountId = frame_benchmarking::account("doctor", 0, 0);
        let encrypted_data = vec![0u8; 1024];
        let metadata = EncryptionMetadataRecord {
            algorithm: EncryptionAlgorithm::Kyber,
            parameters: vec![],
            kdf: vec![],
            metadata: vec![],
        };
        Pallet::<T>::create_health_record(
            RawOrigin::Signed(patient.clone()).into(),
            encrypted_data,
            metadata,
        )?;
    }: _(RawOrigin::Signed(patient.clone()), doctor, PermissionLevel::Read)
    verify {
        assert!(AccessPermissions::<T>::contains_key(&patient, &doctor));
    }

    revoke_access {
        let patient: T::AccountId = whitelisted_caller();
        let doctor: T::AccountId = frame_benchmarking::account("doctor", 0, 0);
        let encrypted_data = vec![0u8; 1024];
        let metadata = EncryptionMetadataRecord {
            algorithm: EncryptionAlgorithm::Kyber,
            parameters: vec![],
            kdf: vec![],
            metadata: vec![],
        };
        Pallet::<T>::create_health_record(
            RawOrigin::Signed(patient.clone()).into(),
            encrypted_data,
            metadata,
        )?;
        Pallet::<T>::grant_access(
            RawOrigin::Signed(patient.clone()).into(),
            doctor.clone(),
            PermissionLevel::Read,
        )?;
    }: _(RawOrigin::Signed(patient.clone()), doctor)
    verify {
        assert!(!AccessPermissions::<T>::contains_key(&patient, &doctor));
    }

    update_encryption_metadata {
        let caller: T::AccountId = whitelisted_caller();
        let encrypted_data = vec![0u8; 1024];
        let metadata = EncryptionMetadataRecord {
            algorithm: EncryptionAlgorithm::Kyber,
            parameters: vec![],
            kdf: vec![],
            metadata: vec![],
        };
        Pallet::<T>::create_health_record(
            RawOrigin::Signed(caller.clone()).into(),
            encrypted_data,
            metadata,
        )?;
        let new_metadata = EncryptionMetadataRecord {
            algorithm: EncryptionAlgorithm::Dilithium,
            parameters: vec![],
            kdf: vec![],
            metadata: vec![],
        };
    }: _(RawOrigin::Signed(caller.clone()), new_metadata)
    verify {
        assert!(EncryptionMetadata::<T>::contains_key(&caller));
    }

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}

