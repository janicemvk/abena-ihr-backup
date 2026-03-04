//! Tests for data-separation pallet

use crate::mock::{new_test_ext, RuntimeOrigin, Test};
use crate::pallet::{
    DataTier, AnonymizationLevel, DataViolation, DataQuery, DemographicFilter,
    LicensePurpose, PrivacyGuarantee,
};
use frame_support::{assert_ok, assert_err};
use pallet_patient_identity::Pallet as PatientIdentity;
use sp_core::H256;
use sp_runtime::BoundedVec;

type DataSeparation = crate::pallet::Pallet<Test>;

fn register_patient(account: u64) {
    let public_key = [1u8; 32];
    let metadata_hash = [2u8; 32];
    assert_ok!(PatientIdentity::<Test>::register_patient(
        RuntimeOrigin::signed(account),
        public_key,
        metadata_hash,
        None
    ));
}

#[test]
fn set_anonymization_preferences_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        assert_ok!(DataSeparation::set_anonymization_preferences(
            RuntimeOrigin::signed(patient),
            5,   // k_min
            2,   // l_diversity_min
            true // allow_differential_privacy
        ));
        let prefs = DataSeparation::anonymization_preferences(patient);
        assert!(prefs.is_some());
        assert_eq!(prefs.unwrap().k_min, 5);
    });
}

#[test]
fn register_data_asset_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        let data_hash = [1u8; 32];
        let allowed = vec![LicensePurpose::ClinicalTrial, LicensePurpose::AcademicResearch];

        assert_ok!(DataSeparation::register_data_asset(
            RuntimeOrigin::signed(patient),
            data_hash,
            DataTier::ClinicalData,
            AnonymizationLevel::KAnonymity(5),
            allowed,
            100u128, // min_compensation
            None,    // consent_duration
        ));

        let asset_id = DataSeparation::generate_asset_id(&patient, &data_hash);
        let asset = DataSeparation::data_assets(asset_id).expect("asset should exist");
        assert_eq!(asset.owner, patient);
        assert_eq!(asset.data_hash, data_hash);
        assert_eq!(asset.compensation_earned, 0);
        assert_eq!(asset.min_compensation, 100);
    });
}

#[test]
fn register_data_asset_fails_without_patient_identity() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        // Do NOT register patient

        let data_hash = [1u8; 32];
        assert!(DataSeparation::register_data_asset(
            RuntimeOrigin::signed(patient),
            data_hash,
            DataTier::ClinicalData,
            AnonymizationLevel::Full,
            vec![],
            0u128,
            None,
        )
        .is_err());
    });
}

#[test]
fn register_direct_identifiers_fails() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);

        let data_hash = [1u8; 32];
        assert!(DataSeparation::register_data_asset(
            RuntimeOrigin::signed(patient),
            data_hash,
            DataTier::DirectIdentifiers,
            AnonymizationLevel::Full,
            vec![],
            0u128,
            None,
        )
        .is_err());
    });
}

#[test]
fn commercial_entity_and_violation_flow() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let licensee = 2u64;
        let reporter = 3u64;
        register_patient(patient);
        assert_ok!(DataSeparation::register_commercial_entity(RuntimeOrigin::signed(licensee)));

        let data_hash = [1u8; 32];
        let allowed = vec![LicensePurpose::ClinicalTrial];
        assert_ok!(DataSeparation::register_data_asset(
            RuntimeOrigin::signed(patient),
            data_hash,
            DataTier::ClinicalData,
            AnonymizationLevel::KAnonymity(5),
            allowed,
            100u128,
            None,
        ));

        let data_query = DataQuery {
            conditions: BoundedVec::default(),
            demographics: DemographicFilter {
                age_min: None,
                age_max: None,
                gender_allowed: BoundedVec::default(),
            },
            data_fields: BoundedVec::default(),
            min_records: 1,
        };
        let privacy_guarantees: BoundedVec<PrivacyGuarantee, _> = BoundedVec::default();
        assert_ok!(DataSeparation::request_data_license(
            RuntimeOrigin::signed(licensee),
            data_query.clone(),
            LicensePurpose::ClinicalTrial,
            100u128,
            1000u64,
            privacy_guarantees,
        ));

        let license_id = DataSeparation::generate_license_id(&licensee, &data_query);
        assert!(DataSeparation::data_licenses(license_id).is_some());
        assert!(DataSeparation::license_escrow(license_id).is_some());

        let evidence_hash = [5u8; 32];
        assert_ok!(DataSeparation::report_data_violation(
            RuntimeOrigin::signed(reporter),
            license_id,
            DataViolation::PurposeMisuse,
            evidence_hash,
        ));
        let report = DataSeparation::violation_reports(license_id);
        assert!(report.is_some());
        assert_eq!(report.unwrap().1, DataViolation::PurposeMisuse);

        assert_ok!(DataSeparation::confirm_violation_and_penalize(
            RuntimeOrigin::root(),
            license_id,
        ));
        assert!(DataSeparation::banned_entities(licensee).is_some());
        assert!(DataSeparation::commercial_entities(licensee).is_none());
        assert!(DataSeparation::violation_reports(license_id).is_none());
        assert!(DataSeparation::license_escrow(license_id).is_none());
    });
}

#[test]
fn banned_entity_cannot_register_or_request_license() {
    new_test_ext().execute_with(|| {
        let licensee = 2u64;
        assert_ok!(DataSeparation::register_commercial_entity(RuntimeOrigin::signed(licensee)));
        // Simulate ban (in real flow this is done by confirm_violation_and_penalize)
        crate::pallet::BannedEntities::<Test>::insert(&licensee, ());

        assert_err!(
            DataSeparation::register_commercial_entity(RuntimeOrigin::signed(licensee)),
            crate::pallet::Error::<Test>::EntityBanned
        );
    });
}

#[test]
fn register_commercial_entity_works() {
    new_test_ext().execute_with(|| {
        let licensee = 2u64;
        assert_ok!(DataSeparation::register_commercial_entity(RuntimeOrigin::signed(licensee)));
        assert!(DataSeparation::commercial_entities(licensee).is_some());
    });
}

#[test]
fn set_anonymization_preferences_fails_below_min_k() {
    new_test_ext().execute_with(|| {
        // MinKAnonymity = 2 in mock; k_min = 1 should fail
        assert_err!(
            DataSeparation::set_anonymization_preferences(
                RuntimeOrigin::signed(1), 1, 0, false
            ),
            crate::pallet::Error::<Test>::InvalidPreference
        );
    });
}

#[test]
fn register_quasi_identifier_data_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        register_patient(patient);
        let data_hash = [2u8; 32];
        assert_ok!(DataSeparation::register_data_asset(
            RuntimeOrigin::signed(patient),
            data_hash,
            DataTier::QuasiIdentifiers,
            AnonymizationLevel::LDiversity(3),
            vec![LicensePurpose::InsuranceActuary],
            200u128,
            None,
        ));
        let asset_id = DataSeparation::generate_asset_id(&patient, &data_hash);
        let asset = DataSeparation::data_assets(asset_id).unwrap();
        assert_eq!(asset.data_tier, DataTier::QuasiIdentifiers);
    });
}

#[test]
fn calculate_compensation_updates_usage() {
    new_test_ext().execute_with(|| {
        let patient  = 1u64;
        let licensee = 2u64;
        register_patient(patient);
        assert_ok!(DataSeparation::register_commercial_entity(RuntimeOrigin::signed(licensee)));

        let data_hash = [3u8; 32];
        let allowed = vec![LicensePurpose::AcademicResearch];
        assert_ok!(DataSeparation::register_data_asset(
            RuntimeOrigin::signed(patient),
            data_hash,
            DataTier::ClinicalData,
            AnonymizationLevel::Full,
            allowed,
            50u128,
            None,
        ));

        // license_data to create a license in the Licenses map (used by calculate_compensation)
        let asset_id = DataSeparation::generate_asset_id(&patient, &data_hash);
        assert_ok!(DataSeparation::license_data(
            RuntimeOrigin::signed(licensee),
            DataQuery {
                conditions: BoundedVec::default(),
                demographics: DemographicFilter {
                    age_min: None, age_max: None, gender_allowed: BoundedVec::default(),
                },
                data_fields: BoundedVec::default(),
                min_records: 0,
            },
            LicensePurpose::AcademicResearch,
            50u128,
            1000u64,
            BoundedVec::default(),
            vec![asset_id],
        ));
        let license_id = DataSeparation::next_license_id().saturating_sub(1);
        assert_ok!(DataSeparation::calculate_compensation(
            RuntimeOrigin::signed(3),
            license_id,
            patient,
        ));
    });
}

#[test]
fn license_data_works() {
    new_test_ext().execute_with(|| {
        let patient  = 1u64;
        let licensee = 2u64;
        register_patient(patient);
        assert_ok!(DataSeparation::register_commercial_entity(RuntimeOrigin::signed(licensee)));

        let data_hash = [4u8; 32];
        assert_ok!(DataSeparation::register_data_asset(
            RuntimeOrigin::signed(patient),
            data_hash,
            DataTier::ClinicalData,
            AnonymizationLevel::KAnonymity(2),
            vec![LicensePurpose::DrugDevelopment],
            0u128,
            None,
        ));

        let asset_id = DataSeparation::generate_asset_id(&patient, &data_hash);
        assert_ok!(DataSeparation::license_data(
            RuntimeOrigin::signed(licensee),
            DataQuery {
                conditions: BoundedVec::default(),
                demographics: DemographicFilter {
                    age_min: None, age_max: None, gender_allowed: BoundedVec::default(),
                },
                data_fields: BoundedVec::default(),
                min_records: 0,
            },
            LicensePurpose::DrugDevelopment,
            10u128,
            500u64,
            BoundedVec::default(),
            vec![asset_id],
        ));
    });
}

#[test]
fn verify_privacy_guarantees_emits_event() {
    new_test_ext().execute_with(|| {
        let patient  = 1u64;
        let licensee = 2u64;
        register_patient(patient);
        assert_ok!(DataSeparation::register_commercial_entity(RuntimeOrigin::signed(licensee)));

        assert_ok!(DataSeparation::register_data_asset(
            RuntimeOrigin::signed(patient),
            [5u8; 32],
            DataTier::ClinicalData,
            AnonymizationLevel::Full,
            vec![LicensePurpose::CannabisResearch],
            0u128,
            None,
        ));
        let asset_id = DataSeparation::generate_asset_id(&patient, &[5u8; 32]);
        assert_ok!(DataSeparation::license_data(
            RuntimeOrigin::signed(licensee),
            DataQuery {
                conditions: BoundedVec::default(),
                demographics: DemographicFilter {
                    age_min: None, age_max: None, gender_allowed: BoundedVec::default(),
                },
                data_fields: BoundedVec::default(),
                min_records: 0,
            },
            LicensePurpose::CannabisResearch,
            0u128,
            100u64,
            BoundedVec::default(),
            vec![asset_id],
        ));
        let license_id = DataSeparation::next_license_id().saturating_sub(1);
        assert_ok!(DataSeparation::verify_privacy_guarantees(
            RuntimeOrigin::signed(3), license_id
        ));
    });
}
