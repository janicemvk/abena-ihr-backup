//! Benchmarks for the ABENA Data Separation pallet.
//!
//! Note: register_data_asset, request_data_license, and related extrinsics
//! require the caller to be registered in the patient-identity pallet first.
//! The setup blocks below call the patient-identity dispatchable directly.

use crate::pallet::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_support::BoundedVec;
use frame_system::RawOrigin;

const SEED: u32 = 0;

fn empty_query<T: Config>() -> DataQuery {
    DataQuery {
        conditions: BoundedVec::default(),
        demographics: DemographicFilter {
            age_min: None,
            age_max: None,
            gender_allowed: BoundedVec::default(),
        },
        data_fields: BoundedVec::default(),
        min_records: 0,
    }
}

fn register_patient_identity<T: Config + pallet_patient_identity::Config>(
    who: &T::AccountId,
) -> Result<(), frame_support::pallet_prelude::DispatchError> {
    pallet_patient_identity::Pallet::<T>::register_patient(
        RawOrigin::Signed(who.clone()).into(),
        [1u8; 32],
        [2u8; 32],
        None,
    )
}

benchmarks! {
    where_clause {
        where T: pallet_patient_identity::Config,
    }

    // ── register_data_asset ──────────────────────────────────────────────────
    register_data_asset {
        let caller: T::AccountId = whitelisted_caller();
        register_patient_identity::<T>(&caller)?;
        let data_hash = [1u8; 32];
    }: _(
        RawOrigin::Signed(caller.clone()),
        data_hash,
        DataTier::ClinicalData,
        AnonymizationLevel::Full,
        vec![LicensePurpose::AcademicResearch],
        100u128,
        None
    )
    verify {
        let asset_id = Pallet::<T>::generate_asset_id(&caller, &data_hash);
        assert!(DataAssets::<T>::contains_key(asset_id));
    }

    // ── set_anonymization_preferences ───────────────────────────────────────
    set_anonymization_preferences {
        let caller: T::AccountId = whitelisted_caller();
        let min_k = T::MinKAnonymity::get();
    }: _(RawOrigin::Signed(caller.clone()), min_k, 2u32, true)
    verify {
        assert!(AnonymizationPreferences::<T>::contains_key(&caller));
    }

    // ── register_commercial_entity ───────────────────────────────────────────
    register_commercial_entity {
        let caller: T::AccountId = whitelisted_caller();
    }: _(RawOrigin::Signed(caller.clone()))
    verify {
        assert!(CommercialEntities::<T>::contains_key(&caller));
    }

    // ── license_data ─────────────────────────────────────────────────────────
    license_data {
        let patient: T::AccountId  = account("patient", 0, SEED);
        let licensee: T::AccountId = whitelisted_caller();

        register_patient_identity::<T>(&patient)?;

        let data_hash = [2u8; 32];
        Pallet::<T>::register_data_asset(
            RawOrigin::Signed(patient.clone()).into(),
            data_hash,
            DataTier::ClinicalData,
            AnonymizationLevel::Full,
            vec![LicensePurpose::DrugDevelopment],
            0u128,
            None,
        )?;
        let asset_id = Pallet::<T>::generate_asset_id(&patient, &data_hash);
    }: _(
        RawOrigin::Signed(licensee.clone()),
        empty_query::<T>(),
        LicensePurpose::DrugDevelopment,
        10u128,
        500u64,
        BoundedVec::default(),
        vec![asset_id]
    )
    verify {
        let lid = NextLicenseId::<T>::get().saturating_sub(1);
        assert!(Licenses::<T>::contains_key(lid));
    }

    // ── calculate_compensation ───────────────────────────────────────────────
    calculate_compensation {
        let patient: T::AccountId  = account("patient", 0, SEED);
        let licensee: T::AccountId = account("licensee", 0, SEED);
        let caller: T::AccountId   = whitelisted_caller();

        register_patient_identity::<T>(&patient)?;

        let data_hash = [3u8; 32];
        Pallet::<T>::register_data_asset(
            RawOrigin::Signed(patient.clone()).into(),
            data_hash,
            DataTier::ClinicalData,
            AnonymizationLevel::Full,
            vec![LicensePurpose::ClinicalTrial],
            0u128,
            None,
        )?;
        let asset_id = Pallet::<T>::generate_asset_id(&patient, &data_hash);
        Pallet::<T>::license_data(
            RawOrigin::Signed(licensee.clone()).into(),
            empty_query::<T>(),
            LicensePurpose::ClinicalTrial,
            50u128,
            100u64,
            BoundedVec::default(),
            vec![asset_id],
        )?;
        let license_id = NextLicenseId::<T>::get().saturating_sub(1);
    }: _(RawOrigin::Signed(caller), license_id, patient.clone())
    verify {}

    // ── verify_privacy_guarantees ─────────────────────────────────────────────
    verify_privacy_guarantees {
        let patient: T::AccountId  = account("patient", 0, SEED);
        let licensee: T::AccountId = account("licensee", 0, SEED);
        let caller: T::AccountId   = whitelisted_caller();

        register_patient_identity::<T>(&patient)?;

        let data_hash = [4u8; 32];
        Pallet::<T>::register_data_asset(
            RawOrigin::Signed(patient.clone()).into(),
            data_hash,
            DataTier::ClinicalData,
            AnonymizationLevel::Full,
            vec![LicensePurpose::AcademicResearch],
            0u128,
            None,
        )?;
        let asset_id = Pallet::<T>::generate_asset_id(&patient, &data_hash);
        Pallet::<T>::license_data(
            RawOrigin::Signed(licensee).into(),
            empty_query::<T>(),
            LicensePurpose::AcademicResearch,
            0u128,
            100u64,
            BoundedVec::default(),
            vec![asset_id],
        )?;
        let license_id = NextLicenseId::<T>::get().saturating_sub(1);
    }: _(RawOrigin::Signed(caller), license_id)
    verify {}

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}
