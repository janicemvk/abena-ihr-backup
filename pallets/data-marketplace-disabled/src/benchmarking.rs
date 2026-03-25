//! Benchmarks for pallet-data-marketplace.
//!
//! Targets:
//!   request_data_license       – baseline: create a Pending license request
//!   finalize_data_license      – transition a license from Pending → Active
//!   distribute_compensation    – distribute compensation for an Active license
//!   find_matching_assets       – block benchmark: iterate n assets (capped at 32)
//!   register_data_asset        – direct-storage benchmark: insert n-th asset
//!   request_license_many_assets – worst-case: request license with n assets in store

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_support::BoundedVec;
use frame_system::RawOrigin;
use sp_runtime::traits::Hash as HashTrait;
use crate::types::{
    ClinicalCondition, DataField, DataTier, LicensePurpose, PrivacyGuarantee,
};

const SEED: u32 = 0;

fn make_hash<T: Config>(seed: u32) -> T::Hash {
    let mut b = [0u8; 32];
    b[0..4].copy_from_slice(&seed.to_le_bytes());
    T::Hashing::hash(&b)
}

fn default_query() -> DataQuery {
    DataQuery {
        fields: BoundedVec::truncate_from(sp_std::vec![DataField::Diagnosis, DataField::Age]),
        condition: Some(ClinicalCondition::Diabetes),
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

/// Insert `n` data assets directly into `DataAssets` storage.
fn insert_assets<T: Config>(n: u32) {
    let owner: T::AccountId = account("asset_owner", 0, SEED);
    for i in 0..n {
        let h = make_hash::<T>(10_000 + i);
        DataAssets::<T>::insert(
            h,
            DataAsset::<T> {
                owner: owner.clone(),
                data_hash: h,
                tier: DataTier::ClinicalData,
            },
        );
    }
}

/// Insert a Pending license and return its ID.
fn insert_pending_license<T: Config>(seed: u32) -> T::Hash {
    let requester: T::AccountId = account("requester", 0, SEED);
    let license_id = make_hash::<T>(seed);
    DataLicenses::<T>::insert(
        license_id,
        DataLicense::<T> {
            license_id,
            requester,
            data_query: default_query(),
            purpose: LicensePurpose::AcademicResearch,
            privacy_guarantees: default_privacy(),
            status: LicenseStatus::Pending,
            dataset_hash: None,
        },
    );
    license_id
}

/// Insert an Active license and return its ID.
fn insert_active_license<T: Config>(seed: u32) -> T::Hash {
    let requester: T::AccountId = account("requester", 0, SEED);
    let license_id = make_hash::<T>(seed);
    DataLicenses::<T>::insert(
        license_id,
        DataLicense::<T> {
            license_id,
            requester,
            data_query: default_query(),
            purpose: LicensePurpose::AcademicResearch,
            privacy_guarantees: default_privacy(),
            status: LicenseStatus::Active,
            dataset_hash: Some(make_hash::<T>(seed + 1000)),
        },
    );
    license_id
}

benchmarks! {

    // ── request_data_license ──────────────────────────────────────────────
    // Baseline: create a fresh Pending license with no prior state.
    request_data_license {
        let requester: T::AccountId = whitelisted_caller();
        let license_id = make_hash::<T>(1u32);
    }: _(
        RawOrigin::Signed(requester.clone()),
        license_id,
        default_query(),
        LicensePurpose::AcademicResearch,
        default_privacy()
    )
    verify {
        let lic = DataLicenses::<T>::get(license_id).expect("license must exist");
        assert_eq!(lic.status, LicenseStatus::Pending);
    }

    // ── finalize_data_license ─────────────────────────────────────────────
    // Transition a Pending license to Active (off-chain worker call path).
    finalize_data_license {
        let license_id = insert_pending_license::<T>(20u32);
        let dataset_hash = make_hash::<T>(21u32);
    }: _(RawOrigin::None, license_id, dataset_hash)
    verify {
        let lic = DataLicenses::<T>::get(license_id).expect("license must exist");
        assert_eq!(lic.status, LicenseStatus::Active);
    }

    // ── distribute_compensation ───────────────────────────────────────────
    // Distribute compensation for an Active license.
    // The `_asset_ids` parameter is currently metadata-only; this benchmark
    // measures dispatch overhead with n asset hashes provided.
    distribute_compensation {
        let n in 1 .. 1_000u32;

        let license_id = insert_active_license::<T>(30u32);
        let caller: T::AccountId = whitelisted_caller();

        // Build asset_ids Vec<T::Hash> of length n.
        let asset_ids: sp_std::vec::Vec<T::Hash> = (0..n)
            .map(|i| make_hash::<T>(50_000 + i))
            .collect();
    }: _(RawOrigin::Signed(caller.clone()), license_id, asset_ids)
    verify {
        let lic = DataLicenses::<T>::get(license_id).expect("license must exist");
        assert_eq!(lic.status, LicenseStatus::Active);
    }

    // ── find_matching_assets ──────────────────────────────────────────────
    // Block benchmark: helper iterates DataAssets up to 32 entries.
    // Cost is O(min(n, 32)); range goes up to 10,000 to model realistic load.
    find_matching_assets {
        let n in 1 .. 10_000u32;

        insert_assets::<T>(n);
        let query = default_query();
        let purpose = LicensePurpose::AcademicResearch;
    }: {
        let results = Pallet::<T>::find_matching_assets(&query, &purpose)
            .expect("find_matching_assets should not error");
        // Always returns ≤ 32 results regardless of n.
        assert!(results.len() <= 32);
    }
    verify {}

    // ── register_data_asset ───────────────────────────────────────────────
    // Direct-storage insert of a data asset (models patient self-registration).
    // With n-1 assets already present, this is the n-th insertion.
    register_data_asset {
        let n in 1 .. 10_000u32;

        // Pre-populate n-1 assets.
        insert_assets::<T>(n.saturating_sub(1));

        let owner: T::AccountId = whitelisted_caller();
        let new_hash = make_hash::<T>(99_999u32);
    }: {
        DataAssets::<T>::insert(
            new_hash,
            DataAsset::<T> {
                owner: owner.clone(),
                data_hash: new_hash,
                tier: DataTier::ClinicalData,
            },
        );
    }
    verify {
        assert!(DataAssets::<T>::contains_key(new_hash));
    }

    // ── request_license_many_assets ───────────────────────────────────────
    // Worst-case request: n assets pre-populated in the store, then a new
    // license request is made. Measures whether `request_data_license` itself
    // scales with asset count (it should not – it is O(1)).
    request_license_many_assets {
        let n in 100 .. 10_000u32;

        insert_assets::<T>(n);
        let requester: T::AccountId = whitelisted_caller();
        let license_id = make_hash::<T>(2u32);
    }: request_data_license(
        RawOrigin::Signed(requester.clone()),
        license_id,
        default_query(),
        LicensePurpose::DrugDevelopment,
        default_privacy()
    )
    verify {
        assert!(DataLicenses::<T>::contains_key(license_id));
    }

    impl_benchmark_test_suite!(
        Pallet,
        crate::mock::new_test_ext(),
        crate::mock::Test,
    );
}
