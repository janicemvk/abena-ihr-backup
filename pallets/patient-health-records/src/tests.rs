//! Comprehensive tests for the ABENA Patient Health Records pallet.

use crate::{mock::*, *};
use frame_support::{assert_err, assert_ok};

fn kyber_meta() -> EncryptionMetadataRecord {
    EncryptionMetadataRecord {
        algorithm: EncryptionAlgorithm::Kyber,
        parameters: Default::default(),
        kdf:        Default::default(),
        metadata:   Default::default(),
    }
}

fn dilithium_meta() -> EncryptionMetadataRecord {
    EncryptionMetadataRecord {
        algorithm: EncryptionAlgorithm::Dilithium,
        parameters: Default::default(),
        kdf:        Default::default(),
        metadata:   Default::default(),
    }
}

// ── create_health_record ─────────────────────────────────────────────────────

#[test]
fn create_health_record_stores_entry() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"encrypted_data".to_vec(), kyber_meta()
        ));
        assert!(HealthRecords::<Test>::contains_key(1u64));
    });
}

#[test]
fn create_health_record_stores_encryption_metadata() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), dilithium_meta()
        ));
        let meta = EncryptionMetadata::<Test>::get(1u64).unwrap();
        assert_eq!(meta.algorithm, EncryptionAlgorithm::Dilithium);
    });
}

#[test]
fn create_health_record_fails_if_already_exists() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data1".to_vec(), kyber_meta()
        ));
        assert_err!(
            PatientHealthRecords::create_health_record(
                RuntimeOrigin::signed(1), b"data2".to_vec(), kyber_meta()
            ),
            Error::<Test>::RecordAlreadyExists
        );
    });
}

#[test]
fn create_health_record_fails_with_unknown_algorithm() {
    new_test_ext().execute_with(|| {
        let bad_meta = EncryptionMetadataRecord {
            algorithm: EncryptionAlgorithm::Unknown,
            parameters: Default::default(),
            kdf:        Default::default(),
            metadata:   Default::default(),
        };
        assert_err!(
            PatientHealthRecords::create_health_record(
                RuntimeOrigin::signed(1), b"data".to_vec(), bad_meta
            ),
            Error::<Test>::InvalidEncryptionMetadata
        );
    });
}

#[test]
fn create_health_record_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        System::assert_has_event(RuntimeEvent::PatientHealthRecords(
            Event::HealthRecordCreated { patient: 1 }
        ));
    });
}

#[test]
fn create_health_record_stores_block_number() {
    new_test_ext().execute_with(|| {
        System::set_block_number(77);
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        let record = HealthRecords::<Test>::get(1u64).unwrap();
        assert_eq!(record.created_at, 77);
        assert_eq!(record.updated_at, 77);
    });
}

#[test]
fn create_health_record_all_quantum_algorithms() {
    new_test_ext().execute_with(|| {
        for (account, algo) in [
            (1u64, EncryptionAlgorithm::Kyber),
            (2, EncryptionAlgorithm::Dilithium),
            (3, EncryptionAlgorithm::SphincsPlus),
            (4, EncryptionAlgorithm::Ntru),
        ] {
            let meta = EncryptionMetadataRecord {
                algorithm: algo,
                parameters: Default::default(),
                kdf:        Default::default(),
                metadata:   Default::default(),
            };
            assert_ok!(PatientHealthRecords::create_health_record(
                RuntimeOrigin::signed(account), b"data".to_vec(), meta
            ));
        }
    });
}

// ── update_health_record ─────────────────────────────────────────────────────

#[test]
fn update_health_record_by_owner_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"original".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::update_health_record(
            RuntimeOrigin::signed(1), 1, b"updated".to_vec()
        ));
        assert!(HealthRecords::<Test>::contains_key(1u64));
    });
}

#[test]
fn update_health_record_by_authorized_writer_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(1), 2, PermissionLevel::Write
        ));
        assert_ok!(PatientHealthRecords::update_health_record(
            RuntimeOrigin::signed(2), 1, b"updated_by_doctor".to_vec()
        ));
    });
}

#[test]
fn update_health_record_fails_for_unauthorized_account() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_err!(
            PatientHealthRecords::update_health_record(
                RuntimeOrigin::signed(99), 1, b"unauthorized".to_vec()
            ),
            Error::<Test>::UnauthorizedAccess
        );
    });
}

#[test]
fn update_health_record_fails_for_read_only_permission() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(1), 2, PermissionLevel::Read
        ));
        assert_err!(
            PatientHealthRecords::update_health_record(
                RuntimeOrigin::signed(2), 1, b"blocked".to_vec()
            ),
            Error::<Test>::UnauthorizedAccess
        );
    });
}

#[test]
fn update_health_record_fails_if_record_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            PatientHealthRecords::update_health_record(
                RuntimeOrigin::signed(1), 1, b"data".to_vec()
            ),
            Error::<Test>::RecordNotFound
        );
    });
}

#[test]
fn update_health_record_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::update_health_record(
            RuntimeOrigin::signed(1), 1, b"new_data".to_vec()
        ));
        System::assert_has_event(RuntimeEvent::PatientHealthRecords(
            Event::HealthRecordUpdated { patient: 1 }
        ));
    });
}

// ── grant_access ─────────────────────────────────────────────────────────────

#[test]
fn grant_access_read_permission_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(1), 2, PermissionLevel::Read
        ));
        assert!(AccessPermissions::<Test>::contains_key(1u64, 2u64));
    });
}

#[test]
fn grant_access_write_permission_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(1), 2, PermissionLevel::Write
        ));
        assert_eq!(
            AccessPermissions::<Test>::get(1u64, 2u64).unwrap(),
            PermissionLevel::Write
        );
    });
}

#[test]
fn grant_access_full_permission_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(1), 3, PermissionLevel::Full
        ));
        assert_eq!(
            AccessPermissions::<Test>::get(1u64, 3u64).unwrap(),
            PermissionLevel::Full
        );
    });
}

#[test]
fn grant_access_fails_if_record_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            PatientHealthRecords::grant_access(
                RuntimeOrigin::signed(1), 2, PermissionLevel::Read
            ),
            Error::<Test>::RecordNotFound
        );
    });
}

#[test]
fn grant_access_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(1), 5, PermissionLevel::Read
        ));
        System::assert_has_event(RuntimeEvent::PatientHealthRecords(
            Event::AccessGranted { patient: 1, authorized_account: 5, permission: PermissionLevel::Read }
        ));
    });
}

#[test]
fn grant_access_multiple_providers_for_same_patient() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        for provider in 2u64..=6 {
            assert_ok!(PatientHealthRecords::grant_access(
                RuntimeOrigin::signed(1), provider, PermissionLevel::Read
            ));
        }
        for provider in 2u64..=6 {
            assert!(AccessPermissions::<Test>::contains_key(1u64, provider));
        }
    });
}

// ── revoke_access ─────────────────────────────────────────────────────────────

#[test]
fn revoke_access_removes_entry() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(1), 2, PermissionLevel::Read
        ));
        assert_ok!(PatientHealthRecords::revoke_access(RuntimeOrigin::signed(1), 2));
        assert!(!AccessPermissions::<Test>::contains_key(1u64, 2u64));
    });
}

#[test]
fn revoke_access_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(1), 2, PermissionLevel::Full
        ));
        assert_ok!(PatientHealthRecords::revoke_access(RuntimeOrigin::signed(1), 2));
        System::assert_has_event(RuntimeEvent::PatientHealthRecords(
            Event::AccessRevoked { patient: 1, authorized_account: 2 }
        ));
    });
}

#[test]
fn revoke_access_is_idempotent() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        // Revoke without prior grant — should not panic
        assert_ok!(PatientHealthRecords::revoke_access(RuntimeOrigin::signed(1), 99));
    });
}

// ── update_encryption_metadata ───────────────────────────────────────────────

#[test]
fn update_encryption_metadata_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::update_encryption_metadata(
            RuntimeOrigin::signed(1), dilithium_meta()
        ));
        let meta = EncryptionMetadata::<Test>::get(1u64).unwrap();
        assert_eq!(meta.algorithm, EncryptionAlgorithm::Dilithium);
    });
}

#[test]
fn update_encryption_metadata_fails_if_record_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            PatientHealthRecords::update_encryption_metadata(
                RuntimeOrigin::signed(1), dilithium_meta()
            ),
            Error::<Test>::RecordNotFound
        );
    });
}

#[test]
fn update_encryption_metadata_fails_with_unknown_algorithm() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        let bad = EncryptionMetadataRecord {
            algorithm: EncryptionAlgorithm::Unknown,
            parameters: Default::default(),
            kdf:        Default::default(),
            metadata:   Default::default(),
        };
        assert_err!(
            PatientHealthRecords::update_encryption_metadata(RuntimeOrigin::signed(1), bad),
            Error::<Test>::InvalidEncryptionMetadata
        );
    });
}

#[test]
fn update_encryption_metadata_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::update_encryption_metadata(
            RuntimeOrigin::signed(1), dilithium_meta()
        ));
        System::assert_has_event(RuntimeEvent::PatientHealthRecords(
            Event::EncryptionMetadataUpdated { patient: 1 }
        ));
    });
}

// ── has_permission helper ─────────────────────────────────────────────────────

#[test]
fn has_permission_patient_always_has_full_access() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert!(PatientHealthRecords::has_permission(&1u64, &1u64, PermissionLevel::Full));
    });
}

#[test]
fn has_permission_read_only_blocks_write() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(1), 2, PermissionLevel::Read
        ));
        assert!(PatientHealthRecords::has_permission(&1u64, &2u64, PermissionLevel::Read));
        assert!(!PatientHealthRecords::has_permission(&1u64, &2u64, PermissionLevel::Write));
    });
}

#[test]
fn has_permission_write_allows_read_and_write() {
    new_test_ext().execute_with(|| {
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"data".to_vec(), kyber_meta()
        ));
        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(1), 2, PermissionLevel::Write
        ));
        assert!(PatientHealthRecords::has_permission(&1u64, &2u64, PermissionLevel::Read));
        assert!(PatientHealthRecords::has_permission(&1u64, &2u64, PermissionLevel::Write));
    });
}

// ── integration ──────────────────────────────────────────────────────────────

#[test]
fn integration_full_patient_record_lifecycle() {
    new_test_ext().execute_with(|| {
        // Patient creates encrypted health record with Kyber
        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(1), b"initial_encrypted_data".to_vec(), kyber_meta()
        ));

        // Grant access to doctor (write) and insurance (read)
        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(1), 2, PermissionLevel::Write
        ));
        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(1), 3, PermissionLevel::Read
        ));

        // Doctor updates the record
        assert_ok!(PatientHealthRecords::update_health_record(
            RuntimeOrigin::signed(2), 1, b"updated_with_diagnosis".to_vec()
        ));

        // Migrate to post-quantum: update to Dilithium
        assert_ok!(PatientHealthRecords::update_encryption_metadata(
            RuntimeOrigin::signed(1), dilithium_meta()
        ));
        let meta = EncryptionMetadata::<Test>::get(1u64).unwrap();
        assert_eq!(meta.algorithm, EncryptionAlgorithm::Dilithium);

        // Revoke insurance access
        assert_ok!(PatientHealthRecords::revoke_access(RuntimeOrigin::signed(1), 3));
        assert!(!AccessPermissions::<Test>::contains_key(1u64, 3u64));

        // Doctor still has write access
        assert!(AccessPermissions::<Test>::contains_key(1u64, 2u64));
    });
}

#[test]
fn independent_records_for_multiple_patients() {
    new_test_ext().execute_with(|| {
        for patient in 1u64..=5 {
            assert_ok!(PatientHealthRecords::create_health_record(
                RuntimeOrigin::signed(patient),
                format!("data_patient_{}", patient).into_bytes(),
                kyber_meta()
            ));
        }
        for patient in 1u64..=5 {
            assert!(HealthRecords::<Test>::contains_key(patient));
        }
    });
}
