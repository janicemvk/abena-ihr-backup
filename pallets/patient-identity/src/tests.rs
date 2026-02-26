//! Comprehensive test suite for pallet-patient-identity
//!
//! Tests all functions with success and failure cases, helper functions,
//! integration workflows, and edge cases.

use crate::mock::*;
use crate::pallet::{AccessLevel, Error, TherapeuticModality};
use frame_support::{assert_err, assert_ok};
use frame_system::Pallet as System;

// ---------------------------------------------------------------------------
// 1. register_patient
// ---------------------------------------------------------------------------

#[test]
fn register_patient_success() {
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

        let did = PatientIdentity::patient_identity(&patient).unwrap();
        assert_eq!(did.public_key, public_key);
        assert_eq!(did.metadata_hash, metadata_hash);
        assert!(did.active);
        assert_eq!(did.patient_account, patient);
    });
}

#[test]
fn register_patient_fails_when_already_exists() {
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
fn register_patient_fails_invalid_public_key_all_zeros() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let public_key = [0u8; 32];
        let metadata_hash = [2u8; 32];

        assert_err!(
            PatientIdentity::register_patient(
                RuntimeOrigin::signed(patient),
                public_key,
                metadata_hash,
                None
            ),
            Error::<Test>::InvalidPublicKey
        );
    });
}

#[test]
fn register_patient_stores_emergency_contact() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let emergency_contact = 99u64;
        let public_key = [1u8; 32];
        let metadata_hash = [2u8; 32];

        assert_ok!(PatientIdentity::register_patient(
            RuntimeOrigin::signed(patient),
            public_key,
            metadata_hash,
            Some(emergency_contact)
        ));

        let did = PatientIdentity::patient_identity(&patient).unwrap();
        assert_eq!(did.emergency_contact, Some(emergency_contact));
    });
}

#[test]
fn register_patient_emits_event() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let patient = 1u64;
        let public_key = [1u8; 32];
        let metadata_hash = [2u8; 32];

        assert_ok!(PatientIdentity::register_patient(
            RuntimeOrigin::signed(patient),
            public_key,
            metadata_hash,
            None
        ));

        let events = System::<Test>::events();
        assert!(
            events.iter().any(|r| matches!(&r.event, RuntimeEvent::PatientIdentity(_))),
            "PatientIdentity event should be emitted"
        );
    });
}

// ---------------------------------------------------------------------------
// 2. update_consent
// ---------------------------------------------------------------------------

#[test]
fn update_consent_grants_therapeutic_modality() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(patient),
            TherapeuticModality::WesternMedicine,
            true,
            None
        ));

        assert!(PatientIdentity::verify_consent(&patient, &TherapeuticModality::WesternMedicine));
    });
}

#[test]
fn update_consent_revokes_modality() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(patient),
            TherapeuticModality::Ayurveda,
            true,
            None
        ));
        assert!(PatientIdentity::verify_consent(&patient, &TherapeuticModality::Ayurveda));

        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(patient),
            TherapeuticModality::Ayurveda,
            false,
            None
        ));
        assert!(!PatientIdentity::verify_consent(&patient, &TherapeuticModality::Ayurveda));
    });
}

#[test]
fn update_consent_fails_nonexistent_patient() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;

        assert_err!(
            PatientIdentity::update_consent(
                RuntimeOrigin::signed(patient),
                TherapeuticModality::WesternMedicine,
                true,
                None
            ),
            Error::<Test>::PatientNotFound
        );
    });
}

#[test]
fn update_consent_fails_deactivated_patient() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);
        assert_ok!(PatientIdentity::deactivate_patient(RuntimeOrigin::signed(patient)));

        assert_err!(
            PatientIdentity::update_consent(
                RuntimeOrigin::signed(patient),
                TherapeuticModality::WesternMedicine,
                true,
                None
            ),
            Error::<Test>::PatientDeactivated
        );
    });
}

#[test]
fn update_consent_records_timestamp() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);
        run_to_block(10);

        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(patient),
            TherapeuticModality::Homeopathy,
            true,
            None
        ));

        let consent = PatientIdentity::consent_records(patient, TherapeuticModality::Homeopathy);
        assert!(consent.is_some());
        assert_eq!(consent.unwrap().granted_at, 60);
    });
}

#[test]
fn update_consent_handles_expiration() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);
        run_to_block(1);

        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(patient),
            TherapeuticModality::Naturopathy,
            true,
            Some(30)
        ));

        assert!(PatientIdentity::verify_consent(&patient, &TherapeuticModality::Naturopathy));

        run_to_block(6);
        assert!(!PatientIdentity::verify_consent(&patient, &TherapeuticModality::Naturopathy));
    });
}

#[test]
fn update_consent_emits_event() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let patient = 1u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(patient),
            TherapeuticModality::TraditionalChineseMedicine,
            true,
            None
        ));

        let events = System::<Test>::events();
        assert!(
            events.iter().any(|r| matches!(&r.event, RuntimeEvent::PatientIdentity(_))),
            "ConsentUpdated event should be emitted"
        );
    });
}

// ---------------------------------------------------------------------------
// 3. grant_provider_access
// ---------------------------------------------------------------------------

#[test]
fn grant_provider_access_success() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider,
            AccessLevel::Read,
            None
        ));

        assert!(PatientIdentity::verify_provider_access(&patient, &provider));
    });
}

#[test]
fn grant_provider_access_sets_read_level() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider,
            AccessLevel::Read,
            None
        ));

        let access = PatientIdentity::provider_access(patient, provider).unwrap();
        assert_eq!(access.access_level, AccessLevel::Read);
    });
}

#[test]
fn grant_provider_access_sets_readwrite_and_emergency() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider2 = 2u64;
        let provider3 = 3u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider2,
            AccessLevel::ReadWrite,
            None
        ));
        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider3,
            AccessLevel::Emergency,
            None
        ));

        assert_eq!(
            PatientIdentity::provider_access(patient, provider2).unwrap().access_level,
            AccessLevel::ReadWrite
        );
        assert_eq!(
            PatientIdentity::provider_access(patient, provider3).unwrap().access_level,
            AccessLevel::Emergency
        );
    });
}

#[test]
fn grant_provider_access_sets_expiration() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider,
            AccessLevel::Read,
            Some(1000)
        ));

        let access = PatientIdentity::provider_access(patient, provider).unwrap();
        assert_eq!(access.expires_at, Some(1000));
    });
}

#[test]
fn grant_provider_access_fails_already_granted() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider,
            AccessLevel::Read,
            None
        ));

        assert_err!(
            PatientIdentity::grant_provider_access(
                RuntimeOrigin::signed(patient),
                provider,
                AccessLevel::ReadWrite,
                None
            ),
            Error::<Test>::ProviderAccessAlreadyGranted
        );
    });
}

#[test]
fn grant_provider_access_fails_deactivated_patient() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        register_patient(patient);
        assert_ok!(PatientIdentity::deactivate_patient(RuntimeOrigin::signed(patient)));

        assert_err!(
            PatientIdentity::grant_provider_access(
                RuntimeOrigin::signed(patient),
                provider,
                AccessLevel::Read,
                None
            ),
            Error::<Test>::PatientDeactivated
        );
    });
}

#[test]
fn grant_provider_access_emits_event() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let patient = 1u64;
        let provider = 2u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider,
            AccessLevel::Read,
            None
        ));

        let events = System::<Test>::events();
        assert!(
            events.iter().any(|r| matches!(&r.event, RuntimeEvent::PatientIdentity(_))),
            "ProviderAccessGranted event should be emitted"
        );
    });
}

// ---------------------------------------------------------------------------
// 4. revoke_provider_access
// ---------------------------------------------------------------------------

#[test]
fn revoke_provider_access_success() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        register_patient(patient);
        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider,
            AccessLevel::Read,
            None
        ));

        assert_ok!(PatientIdentity::revoke_provider_access(
            RuntimeOrigin::signed(patient),
            provider
        ));

        assert!(!PatientIdentity::verify_provider_access(&patient, &provider));
    });
}

#[test]
fn revoke_provider_access_fails_no_access() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        register_patient(patient);

        assert_err!(
            PatientIdentity::revoke_provider_access(
                RuntimeOrigin::signed(patient),
                provider
            ),
            Error::<Test>::ProviderAccessNotFound
        );
    });
}

#[test]
fn revoke_provider_access_emits_event() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let patient = 1u64;
        let provider = 2u64;
        register_patient(patient);
        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider,
            AccessLevel::Read,
            None
        ));

        assert_ok!(PatientIdentity::revoke_provider_access(
            RuntimeOrigin::signed(patient),
            provider
        ));

        let events = System::<Test>::events();
        assert!(
            events.iter().any(|r| matches!(&r.event, RuntimeEvent::PatientIdentity(_))),
            "ProviderAccessRevoked event should be emitted"
        );
    });
}

// ---------------------------------------------------------------------------
// 5. emergency_access
// ---------------------------------------------------------------------------

#[test]
fn emergency_access_contact_can_activate() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let emergency_contact = 3u64;
        register_patient_with_emergency(patient, emergency_contact);

        assert_ok!(PatientIdentity::emergency_access(
            RuntimeOrigin::signed(emergency_contact),
            patient
        ));

        assert!(PatientIdentity::verify_provider_access(&patient, &emergency_contact));
        let access = PatientIdentity::provider_access(patient, emergency_contact).unwrap();
        assert_eq!(access.access_level, AccessLevel::Emergency);
    });
}

#[test]
fn emergency_access_non_contact_cannot_activate() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let emergency_contact = 3u64;
        let stranger = 4u64;
        register_patient_with_emergency(patient, emergency_contact);

        assert_err!(
            PatientIdentity::emergency_access(RuntimeOrigin::signed(stranger), patient),
            Error::<Test>::NotAuthorized
        );
    });
}

#[test]
fn emergency_access_sets_24h_expiration() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let emergency_contact = 3u64;
        register_patient_with_emergency(patient, emergency_contact);
        run_to_block(100);

        assert_ok!(PatientIdentity::emergency_access(
            RuntimeOrigin::signed(emergency_contact),
            patient
        ));

        let access = PatientIdentity::provider_access(patient, emergency_contact).unwrap();
        assert_eq!(access.expires_at, Some(100 * 6 + 86400));
    });
}

#[test]
fn emergency_access_grants_emergency_level() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let emergency_contact = 3u64;
        register_patient_with_emergency(patient, emergency_contact);

        assert_ok!(PatientIdentity::emergency_access(
            RuntimeOrigin::signed(emergency_contact),
            patient
        ));

        let access = PatientIdentity::provider_access(patient, emergency_contact).unwrap();
        assert_eq!(access.access_level, AccessLevel::Emergency);
    });
}

#[test]
fn emergency_access_emits_event() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let patient = 1u64;
        let emergency_contact = 3u64;
        register_patient_with_emergency(patient, emergency_contact);

        assert_ok!(PatientIdentity::emergency_access(
            RuntimeOrigin::signed(emergency_contact),
            patient
        ));

        let events = System::<Test>::events();
        assert!(
            events.iter().any(|r| matches!(&r.event, RuntimeEvent::PatientIdentity(_))),
            "EmergencyAccessActivated event should be emitted"
        );
    });
}

// ---------------------------------------------------------------------------
// 6. deactivate_patient
// ---------------------------------------------------------------------------

#[test]
fn deactivate_patient_success() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::deactivate_patient(RuntimeOrigin::signed(patient)));

        let did = PatientIdentity::patient_identity(&patient).unwrap();
        assert!(!did.active);
    });
}

#[test]
fn deactivate_patient_updates_timestamp() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);
        run_to_block(50);

        assert_ok!(PatientIdentity::deactivate_patient(RuntimeOrigin::signed(patient)));

        let did = PatientIdentity::patient_identity(&patient).unwrap();
        assert_eq!(did.updated_at, 50 * 6);
    });
}

#[test]
fn deactivate_patient_preserves_data() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let public_key = [7u8; 32];
        let metadata_hash = [8u8; 32];
        register_patient_with_keys(patient, public_key, metadata_hash, None);

        assert_ok!(PatientIdentity::deactivate_patient(RuntimeOrigin::signed(patient)));

        let did = PatientIdentity::patient_identity(&patient).unwrap();
        assert_eq!(did.public_key, public_key);
        assert_eq!(did.metadata_hash, metadata_hash);
        assert!(!did.active);
    });
}

#[test]
fn deactivate_patient_emits_event() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let patient = 1u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::deactivate_patient(RuntimeOrigin::signed(patient)));

        let events = System::<Test>::events();
        assert!(
            events.iter().any(|r| matches!(&r.event, RuntimeEvent::PatientIdentity(_))),
            "PatientDeactivated event should be emitted"
        );
    });
}

// ---------------------------------------------------------------------------
// 7. verify_provider_access (helper)
// ---------------------------------------------------------------------------

#[test]
fn verify_provider_access_returns_true_for_valid() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        register_patient(patient);
        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider,
            AccessLevel::Read,
            None
        ));

        assert!(PatientIdentity::verify_provider_access(&patient, &provider));
    });
}

#[test]
fn verify_provider_access_returns_false_for_expired() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        register_patient(patient);
        run_to_block(1);

        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider,
            AccessLevel::Read,
            Some(10)
        ));

        assert!(PatientIdentity::verify_provider_access(&patient, &provider));

        run_to_block(5);
        assert!(!PatientIdentity::verify_provider_access(&patient, &provider));
    });
}

#[test]
fn verify_provider_access_returns_false_for_nonexistent() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        register_patient(patient);

        assert!(!PatientIdentity::verify_provider_access(&patient, &provider));
    });
}

// ---------------------------------------------------------------------------
// 8. verify_consent (helper)
// ---------------------------------------------------------------------------

#[test]
fn verify_consent_returns_true_for_granted() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(patient),
            TherapeuticModality::WesternMedicine,
            true,
            None
        ));

        assert!(PatientIdentity::verify_consent(&patient, &TherapeuticModality::WesternMedicine));
    });
}

#[test]
fn verify_consent_returns_false_for_revoked() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(patient),
            TherapeuticModality::Homeopathy,
            false,
            None
        ));

        assert!(!PatientIdentity::verify_consent(&patient, &TherapeuticModality::Homeopathy));
    });
}

#[test]
fn verify_consent_returns_false_for_expired() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);
        run_to_block(1);

        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(patient),
            TherapeuticModality::Ayurveda,
            true,
            Some(12)
        ));

        run_to_block(5);
        assert!(!PatientIdentity::verify_consent(&patient, &TherapeuticModality::Ayurveda));
    });
}

#[test]
fn verify_consent_returns_false_for_nonexistent() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        assert!(!PatientIdentity::verify_consent(
            &patient,
            &TherapeuticModality::TraditionalChineseMedicine
        ));
    });
}

// ---------------------------------------------------------------------------
// 9. Integration: Complete patient workflow
// ---------------------------------------------------------------------------

#[test]
fn integration_register_grant_consent_add_provider_access() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;

        assert_ok!(PatientIdentity::register_patient(
            RuntimeOrigin::signed(patient),
            [1u8; 32],
            [2u8; 32],
            None
        ));

        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(patient),
            TherapeuticModality::WesternMedicine,
            true,
            None
        ));

        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            provider,
            AccessLevel::ReadWrite,
            None
        ));

        assert!(PatientIdentity::verify_consent(&patient, &TherapeuticModality::WesternMedicine));
        assert!(PatientIdentity::verify_provider_access(&patient, &provider));
    });
}

#[test]
fn integration_register_deactivate_cannot_update_consent() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::deactivate_patient(RuntimeOrigin::signed(patient)));

        assert_err!(
            PatientIdentity::update_consent(
                RuntimeOrigin::signed(patient),
                TherapeuticModality::WesternMedicine,
                true,
                None
            ),
            Error::<Test>::PatientDeactivated
        );
    });
}

// ---------------------------------------------------------------------------
// 10–13. Edge cases
// ---------------------------------------------------------------------------

#[test]
fn edge_max_providers_per_patient() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        for i in 0..5 {
            assert_ok!(PatientIdentity::grant_provider_access(
                RuntimeOrigin::signed(patient),
                i + 10,
                AccessLevel::Read,
                None
            ));
        }

        assert_err!(
            PatientIdentity::grant_provider_access(
                RuntimeOrigin::signed(patient),
                99u64,
                AccessLevel::Read,
                None
            ),
            Error::<Test>::TooManyProviders
        );
    });
}

#[test]
fn edge_max_consent_records() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        let modalities = [
            TherapeuticModality::WesternMedicine,
            TherapeuticModality::TraditionalChineseMedicine,
            TherapeuticModality::Ayurveda,
            TherapeuticModality::Homeopathy,
            TherapeuticModality::Naturopathy,
        ];

        for m in modalities {
            assert_ok!(PatientIdentity::update_consent(
                RuntimeOrigin::signed(patient),
                m,
                true,
                None
            ));
        }

        assert_err!(
            PatientIdentity::update_consent(
                RuntimeOrigin::signed(patient),
                TherapeuticModality::Other,
                true,
                None
            ),
            Error::<Test>::TooManyConsentRecords
        );
    });
}

#[test]
fn edge_concurrent_access_grants() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            10u64,
            AccessLevel::Read,
            None
        ));
        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            11u64,
            AccessLevel::ReadWrite,
            None
        ));
        assert_ok!(PatientIdentity::grant_provider_access(
            RuntimeOrigin::signed(patient),
            12u64,
            AccessLevel::Emergency,
            None
        ));

        assert!(PatientIdentity::verify_provider_access(&patient, &10u64));
        assert!(PatientIdentity::verify_provider_access(&patient, &11u64));
        assert!(PatientIdentity::verify_provider_access(&patient, &12u64));
    });
}

#[test]
fn edge_timestamp_at_block_zero() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        let consent = PatientIdentity::consent_records(patient, TherapeuticModality::WesternMedicine);
        assert!(consent.is_none());

        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(patient),
            TherapeuticModality::WesternMedicine,
            true,
            None
        ));

        let consent = PatientIdentity::consent_records(patient, TherapeuticModality::WesternMedicine);
        assert!(consent.is_some());
        assert_eq!(consent.unwrap().granted_at, 0);
    });
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn register_patient(patient: u64) {
    assert_ok!(PatientIdentity::register_patient(
        RuntimeOrigin::signed(patient),
        [1u8; 32],
        [2u8; 32],
        None
    ));
}

fn register_patient_with_emergency(patient: u64, emergency_contact: u64) {
    assert_ok!(PatientIdentity::register_patient(
        RuntimeOrigin::signed(patient),
        [1u8; 32],
        [2u8; 32],
        Some(emergency_contact)
    ));
}

fn register_patient_with_keys(
    patient: u64,
    public_key: [u8; 32],
    metadata_hash: [u8; 32],
    emergency_contact: Option<u64>,
) {
    assert_ok!(PatientIdentity::register_patient(
        RuntimeOrigin::signed(patient),
        public_key,
        metadata_hash,
        emergency_contact
    ));
}
