//! # ABENA Data Separation Pallet
//!
//! Patient health data anonymization and data sovereignty for the ABENA marketplace.
//! Implements three-tier data separation, cryptographic pseudonyms, k-anonymity,
//! differential privacy attestation, and data licensing with ABENA Coin compensation.
//!
//! - **Tier 1**: Direct identifiers (name, SSN, address, etc.) — never shared.
//! - **Tier 2**: Quasi-identifiers (age, gender, zip, dates) — transformed before sharing.
//! - **Tier 3**: Clinical data (symptoms, diagnoses, labs, treatments) — shareable with consent.

#![cfg_attr(not(feature = "std"), no_std)]

#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;

pub mod weights;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{
        pallet_prelude::*,
        traits::{ConstU32, Currency, ExistenceRequirement, ReservableCurrency},
    };
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;
    use sp_core::H256;
    use codec::{Encode, Decode, DecodeWithMemTracking, MaxEncodedLen};
    use scale_info::TypeInfo;
    use sp_runtime::RuntimeDebug;
    use sp_runtime::traits::{BlakeTwo256, CheckedDiv, Hash, SaturatedConversion, Zero};

    use crate::WeightInfo;

    /// Data tier: what kind of data and sharing policy.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum DataTier {
        /// Direct identifiers — never shared.
        DirectIdentifiers,
        /// Quasi-identifiers — transformed before sharing.
        QuasiIdentifiers,
        /// Clinical data — shareable with consent.
        ClinicalData,
    }

    /// Level of anonymization applied (k-anonymity, l-diversity, differential privacy).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum AnonymizationLevel {
        KAnonymity(u32),
        LDiversity(u32),
        /// Epsilon in fixed-point: epsilon_micro = epsilon * 1_000_000 (no f64 on-chain).
        DifferentialPrivacy(u32),
        Full,
    }

    /// Purpose for which data is licensed.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum LicensePurpose {
        DrugDevelopment,
        ClinicalTrial,
        InsuranceActuary,
        AgriculturalResearch,
        CannabisResearch,
        AcademicResearch,
        Other(BoundedVec<u8, ConstU32<128>>),
    }

    /// Clinical condition filter (e.g. "Diabetes", "Hypertension").
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct ClinicalCondition {
        pub code: BoundedVec<u8, ConstU32<64>>,
    }

    /// Demographic filter (age range, gender, etc.).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct DemographicFilter {
        pub age_min: Option<u8>,
        pub age_max: Option<u8>,
        pub gender_allowed: BoundedVec<u8, ConstU32<32>>,
    }

    /// Data field requested in a query.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct DataField {
        pub name: BoundedVec<u8, ConstU32<64>>,
    }

    /// What data a licensee wants (conditions, demographics, fields, min size).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct DataQuery {
        pub conditions: BoundedVec<ClinicalCondition, ConstU32<32>>,
        pub demographics: DemographicFilter,
        pub data_fields: BoundedVec<DataField, ConstU32<32>>,
        pub min_records: u32,
    }

    /// Privacy guarantees for a license (k, l-diversity, epsilon, no re-identification).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct PrivacyGuarantee {
        pub k_anonymity: Option<u32>,
        pub l_diversity: Option<u32>,
        /// Epsilon * 1_000_000 (fixed-point; no f64 on-chain).
        pub differential_privacy_epsilon_micro: Option<u32>,
        pub no_reidentification_clause: bool,
    }

    /// Data type for pricing (base price per record in ABENA Coins).
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum DataType {
        BasicVitals,
        LabResults,
        GeneticData,
        LongitudinalData,
        QuantumAnalyzed,
        RareDisease,
    }

    /// Base prices in ABENA Coins per record (configurable via Config).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct DataPricing {
        pub basic_vitals: u128,
        pub lab_results: u128,
        pub genetic_data: u128,
        pub longitudinal_data: u128,
        pub quantum_analyzed_data: u128,
        pub rare_disease_data: u128,
    }

    /// Type of data misuse for violation reporting.
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum DataViolation {
        UnauthorizedReidentification,
        PurposeMisuse,
        UnauthorizedRedistribution,
        PrivacyGuaranteeViolation,
    }

    impl DataPricing {
        /// Base prices (ABENA Coins per record). Use for default config.
        pub fn default_prices() -> Self {
            Self {
                basic_vitals: 10,
                lab_results: 50,
                genetic_data: 500,
                longitudinal_data: 200,
                quantum_analyzed_data: 1_000,
                rare_disease_data: 5_000,
            }
        }

        /// Calculate compensation: base_price * rarity_multiplier_micro / 1_000_000.
        /// No f64 on-chain: rarity_multiplier_micro = 1_000_000 means 1.0.
        #[inline]
        pub fn calculate_compensation(
            &self,
            data_type: DataType,
            rarity_multiplier_micro: u32,
        ) -> u128 {
            let base = match data_type {
                DataType::BasicVitals => self.basic_vitals,
                DataType::LabResults => self.lab_results,
                DataType::GeneticData => self.genetic_data,
                DataType::LongitudinalData => self.longitudinal_data,
                DataType::QuantumAnalyzed => self.quantum_analyzed_data,
                DataType::RareDisease => self.rare_disease_data,
            };
            base.saturating_mul(rarity_multiplier_micro as u128) / 1_000_000u128
        }
    }

    /// Cryptographic pseudonym linking to patient only via chain state (no PII on-chain).
    pub type DataPseudonym = H256;

    /// Unique identifier for a registered data asset (32 bytes, from generate_asset_id).
    pub type DataAssetId = [u8; 32];

    /// Identifier for a quasi-identifier group (used for k-anonymity).
    pub type QuasiGroupId = H256;

    /// License agreement identifier.
    pub type LicenseId = u64;

    #[pallet::config]
    pub trait Config: frame_system::Config + pallet_patient_identity::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// Weight information for extrinsics.
        type WeightInfo: WeightInfo;
        /// Currency for escrow (ABENA Coins or Balances); must implement ReservableCurrency.
        type Currency: ReservableCurrency<Self::AccountId>;
        /// Minimum k for k-anonymity (e.g. 2, 5, 10).
        #[pallet::constant]
        type MinKAnonymity: Get<u32>;
        /// Maximum number of data assets per patient.
        #[pallet::constant]
        type MaxDataAssetsPerPatient: Get<u32>;
        /// Maximum assets to scan when finding matching data (bounds weight).
        #[pallet::constant]
        type MaxAssetsToScan: Get<u32>;
        /// Base data pricing (ABENA Coins per record by data type).
        #[pallet::constant]
        type DataPricing: Get<DataPricing>;
        /// Additional penalty (ABENA Coins) when a violation is confirmed (e.g. 1M).
        #[pallet::constant]
        type ViolationPenalty: Get<u128>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Balance type alias.
    pub type BalanceOf<T> =
        <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    /// Data asset registered by patient (patient identity only via pseudonym on-chain).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct DataAsset<T: Config> {
        /// Unique identifier (32 bytes).
        pub asset_id: [u8; 32],
        /// Patient pseudonym — NOT real identity.
        pub patient_pseudonym: [u8; 32],
        pub data_tier: DataTier,
        /// Hash of actual data (stored off-chain).
        pub data_hash: [u8; 32],
        pub anonymization_level: AnonymizationLevel,
        pub consent_expires: Option<u64>,
        /// ABENA Coins earned from this data.
        pub compensation_earned: u128,
        /// Minimum ABENA Coins patient requires to share this data.
        pub min_compensation: u128,
        /// Owner account (for authorization; not exposed in marketplace).
        pub owner: T::AccountId,
        pub created_at: BlockNumberFor<T>,
        /// Quasi-group for k-anonymity (optional).
        pub quasi_group_id: Option<QuasiGroupId>,
    }

    /// Patient anonymization preferences.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct AnonymizationPrefs {
        pub k_min: u32,
        pub l_diversity_min: u32,
        pub allow_differential_privacy: bool,
    }

    /// Data licensing agreement.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct DataLicense<T: Config> {
        pub license_id: [u8; 32],
        pub licensee: T::AccountId,
        pub data_query: DataQuery,
        pub purpose: LicensePurpose,
        /// ABENA Coins per record.
        pub price_per_record: u128,
        pub duration: u64,
        pub privacy_guarantees: BoundedVec<PrivacyGuarantee, ConstU32<8>>,
        pub created_at: BlockNumberFor<T>,
    }

    /// Attestation that differential privacy was applied (e.g. Laplace noise).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct DPAttestation {
        pub epsilon_micro: u32,
        pub applied: bool,
    }

    /// Registered shareable data assets, keyed by asset_id ([u8; 32]). Tier 1 is never stored as shareable.
    #[pallet::storage]
    #[pallet::getter(fn data_assets)]
    pub type DataAssets<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        DataAssetId,
        DataAsset<T>,
        OptionQuery,
    >;

    /// Patient -> list of their data asset ids (bounded).
    #[pallet::storage]
    pub type PatientDataAssets<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BoundedVec<DataAssetId, ConstU32<64>>,
        ValueQuery,
    >;

    /// Allowed license purposes per patient (set when registering data assets).
    #[pallet::storage]
    #[pallet::getter(fn allowed_purposes)]
    pub type AllowedPurposes<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BoundedVec<LicensePurpose, ConstU32<16>>,
        ValueQuery,
    >;

    /// Registered commercial entities (licensees must register first).
    #[pallet::storage]
    #[pallet::getter(fn commercial_entities)]
    pub type CommercialEntities<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        (),
        OptionQuery,
    >;

    /// Enumerable index: position -> asset_id (for find_matching_data_assets).
    #[pallet::storage]
    pub type AllAssetIds<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u64,
        DataAssetId,
        OptionQuery,
    >;

    /// Number of registered assets (used as upper bound for iteration).
    #[pallet::storage]
    #[pallet::getter(fn asset_count)]
    pub type AssetCount<T: Config> = StorageValue<_, u64, ValueQuery>;

    /// Data licenses keyed by license_id ([u8; 32]) for request_data_license flow.
    #[pallet::storage]
    #[pallet::getter(fn data_licenses)]
    pub type DataLicenses<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        [u8; 32],
        DataLicense<T>,
        OptionQuery,
    >;

    /// Assets covered by each data license (key = license_id).
    #[pallet::storage]
    #[pallet::getter(fn data_license_assets)]
    pub type DataLicenseAssets<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        [u8; 32],
        BoundedVec<DataAssetId, ConstU32<256>>,
        ValueQuery,
    >;

    /// License ids awaiting off-chain worker (anonymization + finalization).
    #[pallet::storage]
    #[pallet::getter(fn pending_license_ids)]
    pub type PendingLicenseIds<T: Config> = StorageValue<
        _,
        BoundedVec<[u8; 32], ConstU32<32>>,
        ValueQuery,
    >;

    /// Finalized licenses: license_id -> (dataset_hash, record_count).
    #[pallet::storage]
    #[pallet::getter(fn license_finalized)]
    pub type LicenseFinalized<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        [u8; 32],
        ([u8; 32], u32),
        OptionQuery,
    >;

    /// Escrow per data license (licensee, amount reserved) for violation penalty distribution.
    #[pallet::storage]
    #[pallet::getter(fn license_escrow)]
    pub type LicenseEscrow<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        [u8; 32],
        (T::AccountId, u128),
        OptionQuery,
    >;

    /// Reported violation per license (reporter, violation, evidence_hash). Off-chain arbitration can confirm.
    #[pallet::storage]
    #[pallet::getter(fn violation_reports)]
    pub type ViolationReports<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        [u8; 32],
        (T::AccountId, DataViolation, [u8; 32], BlockNumberFor<T>),
        OptionQuery,
    >;

    /// Banned entities (licensees that violated; cannot request new licenses).
    #[pallet::storage]
    #[pallet::getter(fn banned_entities)]
    pub type BannedEntities<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        (),
        OptionQuery,
    >;

    /// Pseudonym -> patient account (only for authorized lookup; pseudonym is the public handle).
    #[pallet::storage]
    #[pallet::getter(fn pseudonym_to_patient)]
    pub type PseudonymToPatient<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        DataPseudonym,
        T::AccountId,
        OptionQuery,
    >;

    /// Anonymization preferences per patient (k, l-diversity, DP consent).
    #[pallet::storage]
    #[pallet::getter(fn anonymization_preferences)]
    pub type AnonymizationPreferences<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        AnonymizationPrefs,
        OptionQuery,
    >;

    /// Quasi-identifier group -> number of patients in that group (for k-anonymity).
    #[pallet::storage]
    #[pallet::getter(fn quasi_group_count)]
    pub type QuasiGroupCount<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        QuasiGroupId,
        u32,
        ValueQuery,
    >;

    /// Active data licenses (licensee, terms, linked assets/cohort).
    #[pallet::storage]
    #[pallet::getter(fn licenses)]
    pub type Licenses<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        LicenseId,
        DataLicense<T>,
        OptionQuery,
    >;

    /// Next license id.
    #[pallet::storage]
    #[pallet::getter(fn next_license_id)]
    pub type NextLicenseId<T: Config> = StorageValue<_, LicenseId, ValueQuery>;

    /// Asset ids covered by each license (for compensation and verification).
    #[pallet::storage]
    #[pallet::getter(fn license_asset_ids)]
    pub type LicenseAssetIds<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        LicenseId,
        BoundedVec<DataAssetId, ConstU32<64>>,
        ValueQuery,
    >;

    /// Data usage log for compensation: (license_id, patient) -> usage count or flag.
    #[pallet::storage]
    pub type DataUsage<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        LicenseId,
        Blake2_128Concat,
        T::AccountId,
        u32,
        ValueQuery,
    >;

    /// Attestation that differential privacy was applied (e.g. epsilon, dataset id).
    #[pallet::storage]
    pub type DifferentialPrivacyAttestations<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        LicenseId,
        Blake2_128Concat,
        QuasiGroupId,
        DPAttestation,
        OptionQuery,
    >;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Data asset registered [patient, asset_id]
        DataAssetRegistered {
            patient: T::AccountId,
            asset_id: DataAssetId,
        },
        /// Anonymization preferences updated [patient]
        AnonymizationPreferencesSet { patient: T::AccountId },
        /// Data licensed [license_id, licensee, asset_count]
        DataLicensed {
            license_id: LicenseId,
            licensee: T::AccountId,
            asset_count: u32,
        },
        /// Compensation calculated [license_id, patient, amount_units]
        CompensationCalculated {
            license_id: LicenseId,
            patient: T::AccountId,
            amount_units: u128,
        },
        /// Privacy guarantees verified [license_id, k_satisfied, l_diversity_satisfied]
        PrivacyGuaranteesVerified {
            license_id: LicenseId,
            k_satisfied: bool,
            l_diversity_satisfied: bool,
        },
        /// Data license requested [licensee, license_id, matching_asset_count]
        DataLicenseRequested {
            licensee: T::AccountId,
            license_id: [u8; 32],
            matching_asset_count: u32,
        },
        /// Commercial entity registered [account]
        CommercialEntityRegistered { account: T::AccountId },
        /// Data license finalized by off-chain worker [license_id, dataset_hash, record_count]
        DataLicenseFinalized {
            license_id: [u8; 32],
            dataset_hash: [u8; 32],
            record_count: u32,
        },
        /// Data violation reported [license_id, reporter, violation]
        ViolationReported {
            license_id: [u8; 32],
            reporter: T::AccountId,
            violation: DataViolation,
        },
        /// Violation confirmed; licensee penalized and banned [license_id, licensee, amount_distributed]
        ViolationConfirmedAndPenalized {
            license_id: [u8; 32],
            licensee: T::AccountId,
            amount_distributed: u128,
        },
    }

    #[pallet::error]
    pub enum Error<T> {
        /// Data asset not found.
        DataAssetNotFound,
        /// Not authorized (e.g. not the patient).
        NotAuthorized,
        /// Patient identity not found (must register in patient-identity pallet first).
        PatientNotFound,
        /// Tier 1 (direct identifiers) cannot be registered as shareable.
        Tier1CannotBeShared,
        /// K-anonymity threshold not met for this group.
        KAnonymityNotSatisfied,
        /// L-diversity threshold not met.
        LDiversityNotSatisfied,
        /// Too many data assets for this patient.
        TooManyDataAssets,
        /// Pseudonym already in use.
        PseudonymAlreadyUsed,
        /// Invalid preference (e.g. k below minimum).
        InvalidPreference,
        /// License not found.
        LicenseNotFound,
        /// Too many allowed purposes.
        TooManyAllowedPurposes,
        /// Licensee is not a registered commercial entity.
        NotRegisteredEntity,
        /// Not enough matching data records for the query.
        InsufficientDataRecords,
        /// Insufficient ABENA Coins for the license.
        InsufficientFunds,
        /// License already finalized.
        LicenseAlreadyFinalized,
        /// Invalid unsigned finalize (e.g. license not pending).
        InvalidUnsignedFinalize,
        /// Entity is banned from the data marketplace.
        EntityBanned,
        /// No violation report found for this license (cannot confirm).
        NoViolationReport,
    }

    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Register a shareable data asset (Tier 2 or Tier 3 only).
        /// Requires patient to be registered in the patient-identity pallet.
        /// Generates cryptographic pseudonym and asset_id from (patient, data_hash); patient identity not exposed on-chain.
        #[pallet::call_index(0)]
        #[pallet::weight(<T as Config>::WeightInfo::register_data_asset())]
        pub fn register_data_asset(
            origin: OriginFor<T>,
            data_hash: [u8; 32],
            data_tier: DataTier,
            anonymization_preferences: AnonymizationLevel,
            allowed_purposes: Vec<LicensePurpose>,
            min_compensation: u128,
            consent_duration: Option<u64>,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            ensure!(
                pallet_patient_identity::PatientIdentities::<T>::contains_key(&patient),
                Error::<T>::PatientNotFound
            );

            ensure!(data_tier != DataTier::DirectIdentifiers, Error::<T>::Tier1CannotBeShared);

            let mut patient_assets = PatientDataAssets::<T>::get(&patient);
            let max_assets = T::MaxDataAssetsPerPatient::get();
            ensure!(patient_assets.len() < max_assets as usize, Error::<T>::TooManyDataAssets);

            let asset_id = Self::generate_asset_id(&patient, &data_hash);
            let patient_pseudonym = Self::generate_pseudonym(&patient, &data_hash);

            let pseudonym_h256 = H256::from_slice(&asset_id);
            ensure!(
                !PseudonymToPatient::<T>::contains_key(&pseudonym_h256),
                Error::<T>::PseudonymAlreadyUsed
            );
            PseudonymToPatient::<T>::insert(&pseudonym_h256, &patient);

            let allowed_bounded = BoundedVec::try_from(allowed_purposes)
                .map_err(|_| Error::<T>::TooManyAllowedPurposes)?;

            let asset = DataAsset {
                asset_id,
                patient_pseudonym,
                data_tier: data_tier.clone(),
                data_hash,
                anonymization_level: anonymization_preferences,
                consent_expires: consent_duration,
                compensation_earned: 0,
                min_compensation,
                owner: patient.clone(),
                created_at: <frame_system::Pallet<T>>::block_number(),
                quasi_group_id: None,
            };

            DataAssets::<T>::insert(asset.asset_id, &asset);
            patient_assets.try_push(asset.asset_id).map_err(|_| Error::<T>::TooManyDataAssets)?;
            PatientDataAssets::<T>::insert(&patient, patient_assets);
            AllowedPurposes::<T>::insert(&patient, allowed_bounded);

            let count = AssetCount::<T>::get();
            AllAssetIds::<T>::insert(count, asset.asset_id);
            AssetCount::<T>::put(count.saturating_add(1));

            Self::deposit_event(Event::DataAssetRegistered {
                patient,
                asset_id: asset.asset_id,
            });
            Ok(())
        }

        /// Set anonymization preferences (k, l-diversity, allow differential privacy).
        #[pallet::call_index(1)]
        #[pallet::weight(<T as Config>::WeightInfo::set_anonymization_preferences())]
        pub fn set_anonymization_preferences(
            origin: OriginFor<T>,
            k_min: u32,
            l_diversity_min: u32,
            allow_differential_privacy: bool,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            let min_k = T::MinKAnonymity::get();
            ensure!(k_min >= min_k, Error::<T>::InvalidPreference);

            let prefs = AnonymizationPrefs {
                k_min,
                l_diversity_min,
                allow_differential_privacy,
            };
            AnonymizationPreferences::<T>::insert(&patient, prefs);
            Self::deposit_event(Event::AnonymizationPreferencesSet { patient });
            Ok(())
        }

        /// License data: commercial entity requests access (query, purpose, price, duration, privacy guarantees).
        /// Optionally references specific asset ids that match the query; checks k-anonymity before granting.
        #[pallet::call_index(2)]
        #[pallet::weight(<T as Config>::WeightInfo::license_data())]
        pub fn license_data(
            origin: OriginFor<T>,
            data_query: DataQuery,
            purpose: LicensePurpose,
            price_per_record: u128,
            duration: u64,
            privacy_guarantees: BoundedVec<PrivacyGuarantee, ConstU32<8>>,
            asset_ids: Vec<DataAssetId>,
        ) -> DispatchResult {
            let licensee = ensure_signed(origin)?;

            let mut quasi_groups = sp_std::collections::btree_set::BTreeSet::<QuasiGroupId>::new();
            for id in asset_ids.iter().take(64) {
                if let Some(asset) = DataAssets::<T>::get(*id) {
                    if let Some(gid) = asset.quasi_group_id {
                        quasi_groups.insert(gid);
                    }
                }
            }

            let min_k = T::MinKAnonymity::get();
            for gid in quasi_groups.iter() {
                let count = QuasiGroupCount::<T>::get(gid);
                ensure!(count >= min_k, Error::<T>::KAnonymityNotSatisfied);
            }

            let license_id = NextLicenseId::<T>::get();
            NextLicenseId::<T>::put(license_id.saturating_add(1));

            let lh = BlakeTwo256::hash_of(&license_id);
            let mut license_id_bytes = [0u8; 32];
            license_id_bytes.copy_from_slice(lh.as_ref());
            let license = DataLicense {
                license_id: license_id_bytes,
                licensee: licensee.clone(),
                data_query,
                purpose,
                price_per_record,
                duration,
                privacy_guarantees,
                created_at: <frame_system::Pallet<T>>::block_number(),
            };
            Licenses::<T>::insert(license_id, &license);

            // Store which assets (by [u8; 32]) this license covers (for compensation lookups).
            let mut bounded_assets = BoundedVec::default();
            for id in asset_ids.iter().take(64) {
                let _ = bounded_assets.try_push(*id);
            }
            LicenseAssetIds::<T>::insert(license_id, bounded_assets.clone());

            Self::deposit_event(Event::DataLicensed {
                license_id,
                licensee,
                asset_count: bounded_assets.len() as u32,
            });
            Ok(())
        }

        /// Calculate compensation for a patient for a given license (records usage; payout is via ABENA Coin in runtime).
        #[pallet::call_index(3)]
        #[pallet::weight(<T as Config>::WeightInfo::calculate_compensation())]
        pub fn calculate_compensation(
            origin: OriginFor<T>,
            license_id: LicenseId,
            patient: T::AccountId,
        ) -> DispatchResult {
            let _caller = ensure_signed(origin)?;

            let license = Licenses::<T>::get(license_id).ok_or(Error::<T>::LicenseNotFound)?;
            let mut usage = DataUsage::<T>::get(license_id, &patient);
            usage = usage.saturating_add(1);
            DataUsage::<T>::insert(license_id, &patient, usage);

            let amount = license.price_per_record;
            Self::deposit_event(Event::CompensationCalculated {
                license_id,
                patient,
                amount_units: amount,
            });
            Ok(())
        }

        /// Verify that privacy guarantees (k-anonymity, l-diversity) are satisfied for a license.
        #[pallet::call_index(4)]
        #[pallet::weight(<T as Config>::WeightInfo::verify_privacy_guarantees())]
        pub fn verify_privacy_guarantees(
            origin: OriginFor<T>,
            license_id: LicenseId,
        ) -> DispatchResult {
            let _caller = ensure_signed(origin)?;

            let license = Licenses::<T>::get(license_id).ok_or(Error::<T>::LicenseNotFound)?;
            let min_k = T::MinKAnonymity::get();

            let mut k_satisfied = true;
            let mut l_diversity_satisfied = true;

            let asset_ids = LicenseAssetIds::<T>::get(license_id);
            for asset_id in asset_ids.iter() {
                if let Some(asset) = DataAssets::<T>::get(asset_id) {
                    if let Some(gid) = asset.quasi_group_id {
                        let count = QuasiGroupCount::<T>::get(&gid);
                        if count < min_k {
                            k_satisfied = false;
                        }
                    }
                }
            }

            // L-diversity: we would need to store sensitive-value diversity per group; simplified here.
            Self::deposit_event(Event::PrivacyGuaranteesVerified {
                license_id,
                k_satisfied,
                l_diversity_satisfied,
            });
            Ok(())
        }

        /// Register the caller as a commercial entity (required before requesting data licenses).
        #[pallet::call_index(5)]
        #[pallet::weight(<T as Config>::WeightInfo::register_commercial_entity())]
        pub fn register_commercial_entity(origin: OriginFor<T>) -> DispatchResult {
            let account = ensure_signed(origin)?;
            ensure!(
                !BannedEntities::<T>::contains_key(&account),
                Error::<T>::EntityBanned
            );
            CommercialEntities::<T>::insert(&account, ());
            Self::deposit_event(Event::CommercialEntityRegistered { account });
            Ok(())
        }

        /// Request a data license: find matching assets, escrow payment, create license.
        /// Off-chain workers can then prepare the anonymized dataset.
        #[pallet::call_index(11)]
        #[pallet::weight(<T as Config>::WeightInfo::request_data_license())]
        pub fn request_data_license(
            origin: OriginFor<T>,
            data_query: DataQuery,
            purpose: LicensePurpose,
            price_per_record: u128,
            duration: u64,
            privacy_guarantees: BoundedVec<PrivacyGuarantee, ConstU32<8>>,
        ) -> DispatchResult {
            let licensee = ensure_signed(origin)?;

            ensure!(
                CommercialEntities::<T>::contains_key(&licensee),
                Error::<T>::NotRegisteredEntity
            );
            ensure!(
                !BannedEntities::<T>::contains_key(&licensee),
                Error::<T>::EntityBanned
            );

            let matching_assets = Self::find_matching_data_assets(
                &data_query,
                &purpose,
                privacy_guarantees.as_ref(),
            )?;

            ensure!(
                matching_assets.len() >= data_query.min_records as usize,
                Error::<T>::InsufficientDataRecords
            );

            let total_cost_u128 = price_per_record.saturating_mul(matching_assets.len() as u128);
            let total_cost: BalanceOf<T> = total_cost_u128.saturated_into();

            ensure!(
                T::Currency::free_balance(&licensee) >= total_cost,
                Error::<T>::InsufficientFunds
            );

            let license_id = Self::generate_license_id(&licensee, &data_query);

            let license = DataLicense {
                license_id,
                licensee: licensee.clone(),
                data_query,
                purpose,
                price_per_record,
                duration,
                privacy_guarantees,
                created_at: <frame_system::Pallet<T>>::block_number(),
            };

            T::Currency::reserve(&licensee, total_cost)
                .map_err(|_| Error::<T>::InsufficientFunds)?;

            DataLicenses::<T>::insert(license.license_id, &license);
            DataLicenseAssets::<T>::insert(license.license_id, matching_assets.clone());
            LicenseEscrow::<T>::insert(license.license_id, (licensee.clone(), total_cost_u128));

            PendingLicenseIds::<T>::mutate(|pending| {
                let _ = pending.try_push(license.license_id);
            });

            Self::deposit_event(Event::DataLicenseRequested {
                licensee: licensee.clone(),
                license_id: license.license_id,
                matching_asset_count: matching_assets.len() as u32,
            });
            Ok(())
        }

        /// Finalize a data license (unsigned). Called by the off-chain worker after preparing
        /// the anonymized dataset. Records dataset_hash and record_count; removes license from pending.
        #[pallet::call_index(12)]
        #[pallet::weight(<T as Config>::WeightInfo::finalize_data_license())]
        pub fn finalize_data_license(
            origin: OriginFor<T>,
            license_id: [u8; 32],
            dataset_hash: [u8; 32],
            record_count: u32,
        ) -> DispatchResult {
            ensure_none(origin)?;

            let license = DataLicenses::<T>::get(license_id).ok_or(Error::<T>::LicenseNotFound)?;
            ensure!(
                !LicenseFinalized::<T>::contains_key(license_id),
                Error::<T>::LicenseAlreadyFinalized
            );

            LicenseFinalized::<T>::insert(license_id, (dataset_hash, record_count));

            PendingLicenseIds::<T>::mutate(|pending| {
                if let Some(pos) = pending.iter().position(|id| *id == license_id) {
                    pending.remove(pos);
                }
            });

            Self::deposit_event(Event::DataLicenseFinalized {
                license_id,
                dataset_hash,
                record_count,
            });
            Ok(())
        }

        /// Report a data violation (unauthorized re-identification, purpose misuse, etc.).
        /// Off-chain arbitration should confirm before penalties are applied.
        #[pallet::call_index(15)]
        #[pallet::weight(<T as Config>::WeightInfo::report_data_violation())]
        pub fn report_data_violation(
            origin: OriginFor<T>,
            license_id: [u8; 32],
            violation: DataViolation,
            evidence_hash: [u8; 32],
        ) -> DispatchResult {
            let reporter = ensure_signed(origin)?;

            let license = DataLicenses::<T>::get(license_id).ok_or(Error::<T>::LicenseNotFound)?;

            ViolationReports::<T>::insert(
                license_id,
                (reporter.clone(), violation, evidence_hash, <frame_system::Pallet<T>>::block_number()),
            );

            Self::deposit_event(Event::ViolationReported {
                license_id,
                reporter,
                violation,
            });
            Ok(())
        }

        /// Confirm a reported violation and apply penalties (root/governance only).
        /// Unreserves escrow and distributes to affected patients; optionally slashes additional
        /// penalty; bans the licensee from future licenses.
        #[pallet::call_index(16)]
        #[pallet::weight(<T as Config>::WeightInfo::confirm_violation_and_penalize())]
        pub fn confirm_violation_and_penalize(
            origin: OriginFor<T>,
            license_id: [u8; 32],
        ) -> DispatchResult {
            ensure_root(origin)?;

            let license = DataLicenses::<T>::get(license_id).ok_or(Error::<T>::LicenseNotFound)?;
            let (licensee, escrow_amount_u128) =
                LicenseEscrow::<T>::get(license_id).ok_or(Error::<T>::LicenseNotFound)?;
            ViolationReports::<T>::get(license_id).ok_or(Error::<T>::NoViolationReport)?;

            let escrow_amount: BalanceOf<T> = escrow_amount_u128.saturated_into();

            let asset_ids = DataLicenseAssets::<T>::get(license_id);
            let mut owners: sp_std::vec::Vec<T::AccountId> = sp_std::vec::Vec::new();
            for aid in asset_ids.iter() {
                if let Some(asset) = DataAssets::<T>::get(aid) {
                    if !owners.contains(&asset.owner) {
                        owners.push(asset.owner.clone());
                    }
                }
            }

            let _ = T::Currency::unreserve(&licensee, escrow_amount);
            let count = owners.len().max(1) as u128;
            let count_balance: BalanceOf<T> = count.saturated_into();
            let per_patient = escrow_amount.checked_div(&count_balance).unwrap_or_else(Zero::zero);
            for owner in &owners {
                let _ = T::Currency::transfer(
                    &licensee,
                    owner,
                    per_patient,
                    ExistenceRequirement::KeepAlive,
                );
            }

            let penalty: BalanceOf<T> = T::ViolationPenalty::get().saturated_into();
            let free = T::Currency::free_balance(&licensee);
            let to_slash = sp_std::cmp::min(penalty, free);
            if to_slash > Zero::zero() && !owners.is_empty() {
                let per_patient_penalty = to_slash.checked_div(&count_balance).unwrap_or_else(Zero::zero);
                for owner in &owners {
                    let _ = T::Currency::transfer(
                        &licensee,
                        owner,
                        per_patient_penalty,
                        ExistenceRequirement::AllowDeath,
                    );
                }
            }

            BannedEntities::<T>::insert(&licensee, ());
            CommercialEntities::<T>::remove(&licensee);
            ViolationReports::<T>::remove(license_id);
            LicenseEscrow::<T>::remove(license_id);

            Self::deposit_event(Event::ViolationConfirmedAndPenalized {
                license_id,
                licensee: licensee.clone(),
                amount_distributed: escrow_amount_u128,
            });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        /// Generate a deterministic, cryptographically secure asset id from (patient, data_hash).
        pub fn generate_asset_id(patient: &T::AccountId, data_hash: &[u8; 32]) -> [u8; 32] {
            let enc = (patient.encode(), data_hash);
            let h = BlakeTwo256::hash_of(&enc);
            let mut out = [0u8; 32];
            out.copy_from_slice(h.as_ref());
            out
        }

        /// Generate a deterministic, non-reversible pseudonym from (patient, data_hash).
        pub fn generate_pseudonym(patient: &T::AccountId, data_hash: &[u8; 32]) -> [u8; 32] {
            let enc = (patient.encode(), b"pseudonym", data_hash);
            let h = BlakeTwo256::hash_of(&enc);
            let mut out = [0u8; 32];
            out.copy_from_slice(h.as_ref());
            out
        }

        /// Check if a quasi-group meets k-anonymity.
        pub fn group_meets_k_anonymity(group_id: QuasiGroupId) -> bool {
            let count = QuasiGroupCount::<T>::get(&group_id);
            count >= T::MinKAnonymity::get()
        }

        /// Generate deterministic license_id from (licensee, data_query).
        pub fn generate_license_id(licensee: &T::AccountId, data_query: &DataQuery) -> [u8; 32] {
            let enc = (licensee.encode(), data_query.encode());
            let h = BlakeTwo256::hash_of(&enc);
            let mut out = [0u8; 32];
            out.copy_from_slice(h.as_ref());
            out
        }

        /// Find data assets matching query and purpose (bounded iteration for weight).
        pub fn find_matching_data_assets(
            data_query: &DataQuery,
            purpose: &LicensePurpose,
            _privacy_guarantees: &[PrivacyGuarantee],
        ) -> Result<BoundedVec<DataAssetId, ConstU32<256>>, DispatchError> {
            let max_scan = T::MaxAssetsToScan::get() as u64;
            let count = AssetCount::<T>::get().min(max_scan);
            let mut matching = BoundedVec::default();
            for i in 0..count {
                if let Some(asset_id) = AllAssetIds::<T>::get(i) {
                    if let Some(asset) = DataAssets::<T>::get(asset_id) {
                        if asset.data_tier == DataTier::DirectIdentifiers {
                            continue;
                        }
                        let allowed = AllowedPurposes::<T>::get(&asset.owner);
                        if allowed.iter().any(|p| p == purpose) {
                            let _ = matching.try_push(asset_id);
                        }
                    }
                }
            }
            Ok(matching)
        }
    }
}

/// Weight info for the pallet.
pub trait WeightInfo {
    fn register_data_asset() -> frame_support::weights::Weight;
    fn set_anonymization_preferences() -> frame_support::weights::Weight;
    fn license_data() -> frame_support::weights::Weight;
    fn calculate_compensation() -> frame_support::weights::Weight;
    fn verify_privacy_guarantees() -> frame_support::weights::Weight;
    fn register_commercial_entity() -> frame_support::weights::Weight;
    fn request_data_license() -> frame_support::weights::Weight;
    fn finalize_data_license() -> frame_support::weights::Weight;
    fn report_data_violation() -> frame_support::weights::Weight;
    fn confirm_violation_and_penalize() -> frame_support::weights::Weight;
}

pub use pallet::*;
