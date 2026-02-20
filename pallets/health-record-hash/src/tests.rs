//! Tests for health record hash pallet

use crate::mock::*;
use crate::*;
use frame_support::{assert_err, assert_ok};
use sp_core::H256;

#[test]
fn record_hash_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        let record_id = 1u64;
        let record_hash = H256::from_slice(&[1u8; 32]);
        let record_type = RecordType::ClinicalEncounter;

        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(provider),
            patient,
            record_id,
            record_hash,
            record_type,
            None
        ));

        let entry = HealthRecordHash::record_hashes(patient, record_id);
        assert!(entry.is_some());
        assert_eq!(entry.unwrap().record_hash, record_hash);
        assert_eq!(entry.unwrap().version, 1);
    });
}

#[test]
fn update_hash_creates_new_version() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        let record_id = 1u64;
        let initial_hash = H256::from_slice(&[1u8; 32]);
        let new_hash = H256::from_slice(&[2u8; 32]);

        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(provider),
            patient,
            record_id,
            initial_hash,
            RecordType::ClinicalEncounter,
            None
        ));

        assert_ok!(HealthRecordHash::update_hash(
            RuntimeOrigin::signed(provider),
            patient,
            record_id,
            new_hash,
            None
        ));

        let entry = HealthRecordHash::record_hashes(patient, record_id);
        assert_eq!(entry.unwrap().record_hash, new_hash);
        assert_eq!(entry.unwrap().version, 2);

        // Check version history
        let versions = HealthRecordHash::record_versions(patient, record_id);
        assert_eq!(versions.len(), 2);
    });
}

#[test]
fn set_multi_sig_requirement_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let record_id = 1u64;
        let required_signatures = 2u32;
        let signers = vec![2u64, 3u64, 4u64];

        assert_ok!(HealthRecordHash::set_multi_sig_requirement(
            RuntimeOrigin::signed(patient),
            patient,
            record_id,
            required_signatures,
            signers.clone()
        ));

        let config = HealthRecordHash::multi_sig_requirements(patient, record_id);
        assert!(config.is_some());
        assert_eq!(config.unwrap().required_signatures, required_signatures);
    });
}

