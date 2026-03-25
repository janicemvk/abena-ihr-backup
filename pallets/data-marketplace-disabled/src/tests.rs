//! Comprehensive test suite for pallet-data-marketplace
//!
//! Tests the current pallet implementation: request_data_license,
//! finalize_data_license, distribute_compensation, and find_matching_assets.
//! Additional tests for register_entity, register_data_asset, violations, etc.
//! are placeholders for future pallet extensions.

use crate::mock::*;
use crate::pallet::{DataAssets, DataLicenses};
use crate::types::*;
use crate::*;
use frame_support::{assert_err, assert_ok};
use frame_system::Pallet as System;
use sp_core::H256;

// ---------------------------------------------------------------------------
// DATA LICENSE TESTS (current implementation)
// ---------------------------------------------------------------------------

#[test]
fn request_data_license_success() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let requester = 1u64;
        let license_id = H256::random();
        let query = DataQuery {
            fields: vec![DataField::Diagnosis].try_into().unwrap(),
            condition: Some(ClinicalCondition::Diabetes),
            demographic: None,
        };
        let purpose = LicensePurpose::ClinicalTrial;
        let privacy = PrivacyGuarantee {
            k_anonymity: Some(5),
            l_diversity: Some(2),
            differential_privacy_epsilon: None,
            no_reidentification_clause: true,
        };

        assert_ok!(DataMarketplace::request_data_license(
            RuntimeOrigin::signed(requester),
            license_id,
            query,
            purpose,
            privacy,
        ));

        let license = DataMarketplace::data_license(license_id).unwrap();
        assert_eq!(license.requester, requester);
        assert_eq!(license.status, LicenseStatus::Pending);
        assert!(license.dataset_hash.is_none());
    });
}

#[test]
fn request_data_license_fails_duplicate() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let requester = 1u64;
        let license_id = H256::random();
        let query = DataQuery {
            fields: vec![DataField::LabResults].try_into().unwrap(),
            condition: None,
            demographic: None,
        };
        let purpose = LicensePurpose::AcademicResearch;
        let privacy = default_privacy();

        assert_ok!(DataMarketplace::request_data_license(
            RuntimeOrigin::signed(requester),
            license_id,
            query.clone(),
            purpose.clone(),
            privacy.clone(),
        ));

        assert_err!(
            DataMarketplace::request_data_license(
                RuntimeOrigin::signed(requester),
                license_id,
                query,
                purpose,
                privacy,
            ),
            Error::<Test>::InvalidStatus
        );
    });
}

#[test]
fn request_data_license_emits_event() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let requester = 2u64;
        let license_id = H256::random();

        assert_ok!(DataMarketplace::request_data_license(
            RuntimeOrigin::signed(requester),
            license_id,
            default_query(),
            LicensePurpose::DrugDevelopment,
            default_privacy(),
        ));

        let events = System::<Test>::events();
        assert!(
            events.iter().any(|r| matches!(&r.event, RuntimeEvent::DataMarketplace(_))),
            "DataLicenseRequested event should be emitted"
        );
    });
}

#[test]
fn finalize_data_license_success() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let requester = 1u64;
        let license_id = H256::random();
        create_pending_license(requester, license_id);

        let dataset_hash = H256::random();

        assert_ok!(DataMarketplace::finalize_data_license(
            RuntimeOrigin::none(),
            license_id,
            dataset_hash,
        ));

        let license = DataMarketplace::data_license(license_id).unwrap();
        assert_eq!(license.status, LicenseStatus::Active);
        assert_eq!(license.dataset_hash, Some(dataset_hash));
    });
}

#[test]
fn finalize_data_license_fails_nonexistent() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let license_id = H256::random();

        assert_err!(
            DataMarketplace::finalize_data_license(
                RuntimeOrigin::none(),
                license_id,
                H256::random(),
            ),
            Error::<Test>::LicenseNotFound
        );
    });
}

#[test]
fn finalize_data_license_fails_wrong_status() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let requester = 1u64;
        let license_id = H256::random();
        create_pending_license(requester, license_id);

        assert_ok!(DataMarketplace::finalize_data_license(
            RuntimeOrigin::none(),
            license_id,
            H256::random(),
        ));

        assert_err!(
            DataMarketplace::finalize_data_license(
                RuntimeOrigin::none(),
                license_id,
                H256::random(),
            ),
            Error::<Test>::InvalidStatus
        );
    });
}

#[test]
fn finalize_data_license_emits_event() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let license_id = H256::random();
        create_pending_license(1, license_id);
        let dataset_hash = H256::random();

        assert_ok!(DataMarketplace::finalize_data_license(
            RuntimeOrigin::none(),
            license_id,
            dataset_hash,
        ));

        let events = System::<Test>::events();
        assert!(
            events.iter().any(|r| matches!(&r.event, RuntimeEvent::DataMarketplace(_))),
            "DataLicenseFinalized event should be emitted"
        );
    });
}

#[test]
fn distribute_compensation_signed_success() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let license_id = H256::random();
        create_active_license(license_id);

        assert_ok!(DataMarketplace::distribute_compensation(
            RuntimeOrigin::signed(1),
            license_id,
            vec![],
        ));

        let events = System::<Test>::events();
        assert!(
            events.iter().any(|r| matches!(&r.event, RuntimeEvent::DataMarketplace(_))),
            "CompensationDistributed event should be emitted"
        );
    });
}

#[test]
fn distribute_compensation_unsigned_success() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let license_id = H256::random();
        create_active_license(license_id);

        assert_ok!(DataMarketplace::distribute_compensation(
            RuntimeOrigin::none(),
            license_id,
            vec![],
        ));
    });
}

#[test]
fn distribute_compensation_fails_nonexistent_license() {
    new_test_ext().execute_with(|| {
        run_to_block(1);

        assert_err!(
            DataMarketplace::distribute_compensation(
                RuntimeOrigin::signed(1),
                H256::random(),
                vec![],
            ),
            Error::<Test>::LicenseNotFound
        );
    });
}

#[test]
fn distribute_compensation_fails_pending_license() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let license_id = H256::random();
        create_pending_license(1, license_id);

        assert_err!(
            DataMarketplace::distribute_compensation(
                RuntimeOrigin::signed(1),
                license_id,
                vec![],
            ),
            Error::<Test>::InvalidStatus
        );
    });
}

// ---------------------------------------------------------------------------
// HELPER: find_matching_assets
// ---------------------------------------------------------------------------

#[test]
fn find_matching_assets_empty_storage() {
    new_test_ext().execute_with(|| {
        let result = DataMarketplace::find_matching_assets(
            &default_query(),
            &LicensePurpose::ClinicalTrial,
        );
        assert_ok!(&result);
        assert!(result.unwrap().is_empty());
    });
}

#[test]
fn find_matching_assets_returns_assets() {
    new_test_ext().execute_with(|| {
        let asset_hash = H256::random();
        DataAssets::<Test>::insert(
            asset_hash,
            crate::pallet::DataAsset::<Test> {
                owner: 1,
                data_hash: H256::random(),
                tier: DataTier::ClinicalData,
            },
        );

        let result = DataMarketplace::find_matching_assets(
            &default_query(),
            &LicensePurpose::AcademicResearch,
        );
        assert_ok!(&result);
        let matched = result.unwrap();
        assert!(!matched.is_empty());
        assert!(matched.contains(&asset_hash));
    });
}

// ---------------------------------------------------------------------------
// INTEGRATION: Complete license workflow
// ---------------------------------------------------------------------------

#[test]
fn integration_request_finalize_distribute() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let requester = 1u64;
        let license_id = H256::random();

        assert_ok!(DataMarketplace::request_data_license(
            RuntimeOrigin::signed(requester),
            license_id,
            default_query(),
            LicensePurpose::ClinicalTrial,
            default_privacy(),
        ));

        assert_eq!(
            DataMarketplace::data_license(license_id).unwrap().status,
            LicenseStatus::Pending
        );

        assert_ok!(DataMarketplace::finalize_data_license(
            RuntimeOrigin::none(),
            license_id,
            H256::random(),
        ));

        assert_eq!(
            DataMarketplace::data_license(license_id).unwrap().status,
            LicenseStatus::Active
        );

        assert_ok!(DataMarketplace::distribute_compensation(
            RuntimeOrigin::signed(requester),
            license_id,
            vec![],
        ));
    });
}

// ---------------------------------------------------------------------------
// EDGE CASES
// ---------------------------------------------------------------------------

#[test]
fn concurrent_license_requests() {
    new_test_ext().execute_with(|| {
        run_to_block(1);
        let requester = 1u64;

        for i in 0..3 {
            let license_id = H256::from_low_u64_be(i);
            assert_ok!(DataMarketplace::request_data_license(
                RuntimeOrigin::signed(requester),
                license_id,
                default_query(),
                LicensePurpose::QualityImprovement,
                default_privacy(),
            ));
        }

        assert!(DataLicenses::<Test>::iter().count() >= 3);
    });
}

#[test]
fn find_matching_assets_caps_at_32() {
    new_test_ext().execute_with(|| {
        for i in 0..40u64 {
            let hash = H256::from_low_u64_be(i);
            DataAssets::<Test>::insert(
                hash,
                crate::pallet::DataAsset::<Test> {
                    owner: 1,
                    data_hash: H256::random(),
                    tier: DataTier::ClinicalData,
                },
            );
        }

        let result = DataMarketplace::find_matching_assets(
            &default_query(),
            &LicensePurpose::PublicHealth,
        );
        assert_ok!(&result);
        assert_eq!(result.unwrap().len(), 32);
    });
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn default_query() -> DataQuery {
    DataQuery {
        fields: vec![DataField::Diagnosis].try_into().unwrap(),
        condition: None,
        demographic: None,
    }
}

fn default_privacy() -> PrivacyGuarantee {
    PrivacyGuarantee {
        k_anonymity: Some(5),
        l_diversity: None,
        differential_privacy_epsilon: None,
        no_reidentification_clause: true,
    }
}

fn create_pending_license(requester: u64, license_id: H256) {
    assert_ok!(DataMarketplace::request_data_license(
        RuntimeOrigin::signed(requester),
        license_id,
        default_query(),
        LicensePurpose::ClinicalTrial,
        default_privacy(),
    ));
}

fn create_active_license(license_id: H256) {
    create_pending_license(1, license_id);
    assert_ok!(DataMarketplace::finalize_data_license(
        RuntimeOrigin::none(),
        license_id,
        H256::random(),
    ));
}
