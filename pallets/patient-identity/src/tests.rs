//! Tests for patient identity pallet

use crate::mock::*;
use crate::*;
use frame_support::{assert_err, assert_ok};

#[test]
fn register_patient_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let public_key = [1u8; 32];
        let metadata_hash = [2u8; 32];

        assert_ok!(PatientIdentity::register_patient(
            RuntimeOrigin::signed(patient),
            public_key,
            metadata_hash,
            None
        ));

        let patient_did = PatientIdentity::patient_identity(&patient);
        assert!(patient_did.is_some());
        let did = patient_did.unwrap();
        assert_eq!(did.public_key, public_key);
        assert_eq!(did.metadata_hash, metadata_hash);
        assert!(did.active);
    });
}

#[test]
fn register_patient_duplicate_fails() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let public_key = [1u8; 32];
        let metadata_hash = [2u8; 32];

        assert_ok!(PatientIdentity::register_patient(
            RuntimeOrigin::signed(patient),
            public_key,
            metadata_hash,
            None
        ));

        assert_err!(
            PatientIdentity::register_patient(
                RuntimeOrigin::signed(patient),
                public_key,
                metadata_hash,
                None
            ),
            Error::<Test>::PatientAlreadyExists
        );
    });
}

#[test]
fn update_consent_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let public_key = [1u8; 32];
        let metadata_hash = [2u8; 32];

        // Register patient first
        assert_ok!(PatientIdentity::register_patient(
            RuntimeOrigin::signed(patient),
            public_key,
            metadata_hash,
            None
        ));

        // Grant consent for Western Medicine
        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(patient),
            TherapeuticModality::WesternMedicine,
            true,
            None
        ));

        // Verify consent
        assert!(PatientIdentity::verify_consent(&patient, &TherapeuticModality::WesternMedicine));
    });
}

#[test]
fn grant_provider_access_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        let public_key = [1u8; 32];
        let metadata_hash = [2u8; 32];

        // Register patient first
        assert_ok!(PatientIdentity::register_patient(
            RuntimeOrigin::signed(patient),
            public_key,
            metadata_hash,
            None
        ));

        // Grant provider access
        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider,
            AccessLevel::Read,
            None
        ));

        // Verify access
        assert!(PatientIdentity::verify_provider_access(&patient, &provider));
    });
}

#[test]
fn revoke_provider_access_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        let public_key = [1u8; 32];
        let metadata_hash = [2u8; 32];

        // Register patient
        assert_ok!(PatientIdentity::register_patient(
            RuntimeOrigin::signed(patient),
            public_key,
            metadata_hash,
            None
        ));

        // Grant access
        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider,
            AccessLevel::Read,
            None
        ));

        // Revoke access
        assert_ok!(PatientIdentity::revoke_provider_access(
            RuntimeOrigin::signed(patient),
            provider
        ));

        // Verify access is revoked
        assert!(!PatientIdentity::verify_provider_access(&patient, &provider));
    });
}

#[test]
fn emergency_access_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let emergency_contact = 3u64;
        let public_key = [1u8; 32];
        let metadata_hash = [2u8; 32];

        // Register patient with emergency contact
        assert_ok!(PatientIdentity::register_patient(
            RuntimeOrigin::signed(patient),
            public_key,
            metadata_hash,
            Some(emergency_contact)
        ));

        // Emergency contact can activate emergency access
        assert_ok!(PatientIdentity::emergency_access(
            RuntimeOrigin::signed(emergency_contact),
            patient
        ));

        // Verify emergency access
        assert!(PatientIdentity::verify_provider_access(&patient, &emergency_contact));
    });
}

#[test]
fn deactivate_patient_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let public_key = [1u8; 32];
        let metadata_hash = [2u8; 32];

        // Register patient
        assert_ok!(PatientIdentity::register_patient(
            RuntimeOrigin::signed(patient),
            public_key,
            metadata_hash,
            None
        ));

        // Deactivate patient
        assert_ok!(PatientIdentity::deactivate_patient(
            RuntimeOrigin::signed(patient)
        ));

        // Verify patient is deactivated
        let patient_did = PatientIdentity::patient_identity(&patient).unwrap();
        assert!(!patient_did.active);
    });
}
