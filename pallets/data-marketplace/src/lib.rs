//! # ABENA Data Marketplace Pallet
//!
//! Patient-controlled health data licensing with privacy-preserving anonymization.
//! Off-chain worker handles dataset preparation, anonymization (k-anonymity, l-diversity,
//! differential privacy), IPFS fetch/store, and submits finalize + compensation via unsigned tx.

#![cfg_attr(not(feature = "std"), no_std)]

#[cfg(test)]
mod mock;
#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;

mod anonymization;
mod offchain;
mod pricing;
mod privacy;
mod types;

pub use pallet::*;
pub use types::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_support::traits::ConstU32;
    use frame_system::pallet_prelude::*;
    use sp_runtime::{
        transaction_validity::{InvalidTransaction, TransactionValidity, ValidTransaction},
        traits::ValidateUnsigned,
    };
    use sp_std::vec::Vec;

    use crate::types::{LicensePurpose, PrivacyGuarantee, DataField, ClinicalCondition, DemographicFilter, DataTier};

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type WeightInfo: crate::WeightInfo;
    }

    /// License lifecycle status.
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum LicenseStatus {
        Pending,
        Active,
        Expired,
    }

    /// Data query (bounded).
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct DataQuery {
        pub fields: BoundedVec<DataField, ConstU32<16>>,
        pub condition: Option<ClinicalCondition>,
        pub demographic: Option<DemographicFilter>,
    }

    /// Data license (request + result).
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct DataLicense<T: Config> {
        pub license_id: T::Hash,
        pub requester: T::AccountId,
        pub data_query: DataQuery,
        pub purpose: LicensePurpose,
        pub privacy_guarantees: PrivacyGuarantee,
        pub status: LicenseStatus,
        pub dataset_hash: Option<T::Hash>,
    }

    /// Data asset (metadata; content referenced by data_hash).
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct DataAsset<T: Config> {
        pub owner: T::AccountId,
        pub data_hash: T::Hash,
        pub tier: DataTier,
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Data assets (patient data metadata); content off-chain / IPFS.
    #[pallet::storage]
    #[pallet::getter(fn data_asset)]
    pub type DataAssets<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        DataAsset<T>,
        OptionQuery,
    >;

    /// Data licenses (requests and approved licenses).
    #[pallet::storage]
    #[pallet::getter(fn data_license)]
    pub type DataLicenses<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        DataLicense<T>,
        OptionQuery,
    >;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        DataLicenseRequested { license_id: T::Hash, requester: T::AccountId },
        DataLicenseFinalized { license_id: T::Hash, dataset_hash: T::Hash },
        CompensationDistributed { license_id: T::Hash },
    }

    #[pallet::error]
    pub enum Error<T> {
        LicenseNotFound,
        InvalidStatus,
        AssetNotFound,
    }

    #[pallet::validate_unsigned]
    impl<T: Config> ValidateUnsigned for Pallet<T> {
        type Call = Call<T>;
        fn validate_unsigned(
            _source: sp_runtime::transaction_validity::TransactionSource,
            call: &Self::Call,
        ) -> TransactionValidity {
            match call {
                Call::finalize_data_license { license_id, .. } => {
                    if let Some(license) = DataLicenses::<T>::get(license_id) {
                        if license.status == LicenseStatus::Pending {
                            return ValidTransaction::with_tag_prefix("DataMarketplace")
                                .priority(100u64)
                                .and_provides((b"dm_finalize", license_id).encode())
                                .longevity(64)
                                .propagate(true)
                                .build();
                        }
                    }
                    Err(InvalidTransaction::Call.into())
                }
                Call::distribute_compensation { license_id, .. } => {
                    if let Some(license) = DataLicenses::<T>::get(license_id) {
                        if license.status == LicenseStatus::Active {
                            return ValidTransaction::with_tag_prefix("DataMarketplace")
                                .priority(90u64)
                                .and_provides((b"dm_comp", license_id).encode())
                                .longevity(64)
                                .propagate(true)
                                .build();
                        }
                    }
                    Err(InvalidTransaction::Call.into())
                }
                _ => Err(InvalidTransaction::Call.into()),
            }
        }
    }

    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T>
    where
        T: frame_system::offchain::SendTransactionTypes<Call<T>>,
    {
        fn offchain_worker(block_number: BlockNumberFor<T>) {
            crate::offchain::offchain_worker::<T>(block_number);
        }
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Request a data license (creates pending license for off-chain worker to process).
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::from_parts(50_000_000, 0))]
        pub fn request_data_license(
            origin: OriginFor<T>,
            license_id: T::Hash,
            data_query: DataQuery,
            purpose: LicensePurpose,
            privacy_guarantees: PrivacyGuarantee,
        ) -> DispatchResult {
            let requester = ensure_signed(origin)?;
            ensure!(DataLicenses::<T>::get(&license_id).is_none(), crate::Error::<T>::InvalidStatus);

            let license = DataLicense::<T> {
                license_id,
                requester: requester.clone(),
                data_query,
                purpose,
                privacy_guarantees,
                status: LicenseStatus::Pending,
                dataset_hash: None,
            };
            DataLicenses::<T>::insert(&license_id, &license);
            Self::deposit_event(Event::DataLicenseRequested {
                license_id,
                requester,
            });
            Ok(())
        }

        /// Finalize a data license (called by off-chain worker via unsigned tx).
        #[pallet::call_index(1)]
        #[pallet::weight(Weight::from_parts(40_000_000, 0))]
        pub fn finalize_data_license(
            origin: OriginFor<T>,
            license_id: T::Hash,
            dataset_hash: T::Hash,
        ) -> DispatchResult {
            ensure_none(origin)?;

            let mut license = DataLicenses::<T>::get(&license_id).ok_or(Error::<T>::LicenseNotFound)?;
            ensure!(license.status == LicenseStatus::Pending, Error::<T>::InvalidStatus);

            license.status = LicenseStatus::Active;
            license.dataset_hash = Some(dataset_hash);
            DataLicenses::<T>::insert(&license_id, &license);

            Self::deposit_event(Event::DataLicenseFinalized {
                license_id,
                dataset_hash,
            });
            Ok(())
        }

        /// Distribute compensation to data owners (called by off-chain worker or root).
        #[pallet::call_index(2)]
        #[pallet::weight(Weight::from_parts(60_000_000, 0))]
        pub fn distribute_compensation(
            origin: OriginFor<T>,
            license_id: T::Hash,
            _asset_ids: Vec<T::Hash>,
        ) -> DispatchResult {
            if ensure_signed(origin.clone()).is_ok() {
                let _ = ensure_signed(origin)?;
            } else {
                ensure_none(origin)?;
            }

            let license = DataLicenses::<T>::get(&license_id).ok_or(Error::<T>::LicenseNotFound)?;
            ensure!(license.status == LicenseStatus::Active, Error::<T>::InvalidStatus);

            Self::deposit_event(Event::CompensationDistributed { license_id });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        /// Find asset IDs matching the license query (simplified: return first N assets).
        pub fn find_matching_assets(
            _query: &DataQuery,
            _purpose: &LicensePurpose,
        ) -> Result<Vec<T::Hash>, &'static str> {
            let mut out = Vec::new();
            for (hash, _) in DataAssets::<T>::iter() {
                out.push(hash);
                if out.len() >= 32 {
                    break;
                }
            }
            Ok(out)
        }
    }
}

pub trait WeightInfo {
    fn request_data_license() -> frame_support::weights::Weight;
    fn finalize_data_license() -> frame_support::weights::Weight;
    fn distribute_compensation() -> frame_support::weights::Weight;
}

impl WeightInfo for () {
    fn request_data_license() -> frame_support::weights::Weight {
        frame_support::weights::Weight::from_parts(50_000_000, 0)
    }
    fn finalize_data_license() -> frame_support::weights::Weight {
        frame_support::weights::Weight::from_parts(40_000_000, 0)
    }
    fn distribute_compensation() -> frame_support::weights::Weight {
        frame_support::weights::Weight::from_parts(60_000_000, 0)
    }
}
