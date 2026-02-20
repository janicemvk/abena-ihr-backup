//! Tests for patient health records pallet

use crate::mock::*;
use crate::*;
use frame_support::{assert_err, assert_ok};

#[test]
fn create_health_record_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let encrypted_data = vec![1, 2, 3, 4, 5];
        let metadata = EncryptionMetadataRecord {
            algorithm: EncryptionAlgorithm::Kyber,
            parameters: vec![],
            kdf: vec![],
            metadata: vec![],
        };

        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(patient),
            encrypted_data.clone(),
            metadata.clone()
        ));

        let record = PatientHealthRecords::health_records(patient);
        assert!(record.is_some());
    });
}

#[test]
fn update_health_record_requires_authorization() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let unauthorized = 2u64;
        let encrypted_data = vec![1, 2, 3, 4, 5];
        let metadata = EncryptionMetadataRecord {
            algorithm: EncryptionAlgorithm::Kyber,
            parameters: vec![],
            kdf: vec![],
            metadata: vec![],
        };

        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(patient),
            encrypted_data.clone(),
            metadata.clone()
        ));

        // Unauthorized update should fail
        assert_err!(
            PatientHealthRecords::update_health_record(
                RuntimeOrigin::signed(unauthorized),
                patient,
                vec![6, 7, 8]
            ),
            Error::<Test>::UnauthorizedAccess
        );

        // Patient can update their own record
        assert_ok!(PatientHealthRecords::update_health_record(
            RuntimeOrigin::signed(patient),
            patient,
            vec![6, 7, 8]
        ));
    });
}

#[test]
fn grant_and_revoke_access_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let doctor = 2u64;
        let encrypted_data = vec![1, 2, 3, 4, 5];
        let metadata = EncryptionMetadataRecord {
            algorithm: EncryptionAlgorithm::Kyber,
            parameters: vec![],
            kdf: vec![],
            metadata: vec![],
        };

        assert_ok!(PatientHealthRecords::create_health_record(
            RuntimeOrigin::signed(patient),
            encrypted_data.clone(),
            metadata.clone()
        ));

        assert_ok!(PatientHealthRecords::grant_access(
            RuntimeOrigin::signed(patient),
            doctor,
            PermissionLevel::Read
        ));

        // Doctor should now have read access
        assert!(PatientHealthRecords::has_permission(
            &patient,
            &doctor,
            PermissionLevel::Read
        ));

        assert_ok!(PatientHealthRecords::revoke_access(
            RuntimeOrigin::signed(patient),
            doctor
        ));

        // Doctor should no longer have access
        assert!(!PatientHealthRecords::has_permission(
            &patient,
            &doctor,
            PermissionLevel::Read
        ));
    });
}

