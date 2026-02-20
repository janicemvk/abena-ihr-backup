//! Tests for patient identity pallet

use crate::mock::*;
use crate::*;
use frame_support::{assert_err, assert_ok};

#[test]
fn register_did_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let did = b"did:abena:patient123".to_vec();
        let public_keys = vec![];

        assert_ok!(PatientIdentity::register_did(
            RuntimeOrigin::signed(patient),
            did.clone(),
            public_keys
        ));

        let did_doc = PatientIdentity::patient_dids(patient);
        assert!(did_doc.is_some());
        assert_eq!(did_doc.unwrap().did, did);
    });
}

#[test]
fn update_did_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let did = b"did:abena:patient123".to_vec();
        let public_keys = vec![];

        assert_ok!(PatientIdentity::register_did(
            RuntimeOrigin::signed(patient),
            did,
            public_keys.clone()
        ));

        let new_keys = vec![PublicKey {
            key_type: b"Ed25519".to_vec(),
            public_key: vec![1, 2, 3, 4],
            key_id: b"key1".to_vec(),
        }];

        assert_ok!(PatientIdentity::update_did(
            RuntimeOrigin::signed(patient),
            new_keys.clone()
        ));

        let did_doc = PatientIdentity::patient_dids(patient);
        assert_eq!(did_doc.unwrap().public_keys, new_keys);
    });
}

#[test]
fn grant_and_revoke_consent_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        let scope = ConsentScope::ReadRecords;

        assert_ok!(PatientIdentity::grant_consent(
            RuntimeOrigin::signed(patient),
            provider,
            scope.clone(),
            None
        ));

        let consent = PatientIdentity::consent_records(patient, provider);
        assert!(consent.is_some());
        assert_eq!(consent.unwrap().scope, scope);

        assert_ok!(PatientIdentity::revoke_consent(
            RuntimeOrigin::signed(patient),
            provider
        ));

        let consent_after = PatientIdentity::consent_records(patient, provider);
        assert!(consent_after.is_some());
        assert!(consent_after.unwrap().revoked);
    });
}

#[test]
fn issue_zk_credential_works() {
    new_test_ext().execute_with(|| {
        let issuer = 1u64;
        let patient = 2u64;
        let did = b"did:abena:patient123".to_vec();

        // Register DID first
        assert_ok!(PatientIdentity::register_did(
            RuntimeOrigin::signed(patient),
            did,
            vec![]
        ));

        let credential_type = CredentialType::AgeVerification;
        let proof_hash = sp_core::H256::from_slice(&[1u8; 32]);

        assert_ok!(PatientIdentity::issue_zk_credential(
            RuntimeOrigin::signed(issuer),
            patient,
            credential_type.clone(),
            proof_hash
        ));

        let credential = PatientIdentity::zk_credentials(patient, credential_type);
        assert!(credential.is_some());
    });
}

#[test]
fn issue_auth_token_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;

        // Grant consent first
        assert_ok!(PatientIdentity::grant_consent(
            RuntimeOrigin::signed(patient),
            provider,
            ConsentScope::ReadRecords,
            None
        ));

        let token_hash = sp_core::H256::from_slice(&[5u8; 32]);
        let expires_at = 100u64;

        assert_ok!(PatientIdentity::issue_auth_token(
            RuntimeOrigin::signed(patient),
            provider,
            token_hash,
            expires_at
        ));

        let token = PatientIdentity::auth_tokens(token_hash);
        assert!(token.is_some());
        assert_eq!(token.unwrap().patient, patient);
        assert_eq!(token.unwrap().provider, provider);
    });
}

