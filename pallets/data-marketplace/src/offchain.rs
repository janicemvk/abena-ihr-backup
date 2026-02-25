//! Data Marketplace off-chain worker: anonymization and dataset preparation.
//!
//! Runs every N blocks; processes pending data licenses: finds matching assets,
//! (optionally fetches from IPFS and applies k-anonymity / l-diversity / differential
//! privacy), then submits finalize_data_license and distribute_compensation as
//! unsigned transactions.

use frame_system::offchain::{SendTransactionTypes, SubmitTransaction};
use frame_system::pallet_prelude::BlockNumberFor;
use sp_runtime::traits::{Hash, SaturatedConversion};
use sp_std::vec::Vec;

use crate::{Call, DataLicenses, LicenseStatus, Pallet};

const OFFCHAIN_WORKER_INTERVAL: u32 = 10;
const MAX_CONCURRENT_JOBS: u32 = 5;

/// Entry point for the data marketplace off-chain worker.
pub fn offchain_worker<T>(block_number: BlockNumberFor<T>)
where
    T: crate::pallet::Config + SendTransactionTypes<Call<T>>,
    <T as frame_system::Config>::Hash: Copy,
{
    let block_num: u32 = block_number.saturated_into();
    if block_num % OFFCHAIN_WORKER_INTERVAL != 0 {
        return;
    }

    let _ = process_pending_licenses::<T>();
}

fn process_pending_licenses<T>() -> Result<(), &'static str>
where
    T: crate::pallet::Config + SendTransactionTypes<Call<T>>,
    <T as frame_system::Config>::Hash: Copy,
{
    let pending = get_pending_license_ids::<T>()?;
    if pending.is_empty() {
        return Ok(());
    }

    for license_id in pending.into_iter().take(MAX_CONCURRENT_JOBS as usize) {
        if process_single_license::<T>(license_id).is_err() {
            continue;
        }
    }
    Ok(())
}

fn get_pending_license_ids<T: crate::pallet::Config>() -> Result<Vec<T::Hash>, &'static str>
where
    <T as frame_system::Config>::Hash: Copy,
{
    let mut out = Vec::new();
    for (id, license) in DataLicenses::<T>::iter() {
        if license.status == LicenseStatus::Pending {
            out.push(id);
        }
    }
    Ok(out)
}

fn process_single_license<T>(
    license_id: T::Hash,
) -> Result<(), &'static str>
where
    T: crate::pallet::Config + SendTransactionTypes<Call<T>>,
    <T as frame_system::Config>::Hash: Copy,
{
    let license = DataLicenses::<T>::get(&license_id).ok_or("License not found")?;
    if license.status != LicenseStatus::Pending {
        return Ok(());
    }

    let matching_assets = Pallet::<T>::find_matching_assets(
        &license.data_query,
        &license.purpose,
    ).map_err(|_| "No matching assets")?;

    if matching_assets.is_empty() {
        return Err("No matching assets");
    }

    // In a full implementation: fetch from IPFS, anonymize (k-anonymity, l-diversity, DP),
    // store result to IPFS, then use dataset_cid hash as dataset_hash.
    // Here we use a deterministic hash of license_id for the "dataset" result.
    let dataset_hash = T::Hashing::hash_of(&(b"dataset", license_id));

    let call = Call::<T>::finalize_data_license {
        license_id,
        dataset_hash,
    };
    SubmitTransaction::<T, Call<T>>::submit_unsigned_transaction(call.into())
        .map_err(|_| "Submit finalize failed")?;

    let comp_call = Call::<T>::distribute_compensation {
        license_id,
        asset_ids: matching_assets,
    };
    let _ = SubmitTransaction::<T, Call<T>>::submit_unsigned_transaction(comp_call.into());

    Ok(())
}
