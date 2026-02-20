//! # Health Record Hash Pallet
//!
//! A pallet for storing cryptographic hashes of medical records,
//! providing immutable audit trails and version control.

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Encode, Decode, MaxEncodedLen};
use scale_info::TypeInfo;
use sp_runtime::RuntimeDebug;
use frame_system::pallet_prelude::BlockNumberFor;
use frame_support::weights::Weight;
use sp_runtime::BoundedVec;
use frame_support::traits::ConstU32;


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
        traits::ConstU32,
    };
    use frame_system::pallet_prelude::*;
    use scale_info::TypeInfo;
    use sp_std::vec::Vec;
    use sp_core::H256;
    use codec::MaxEncodedLen;    /// Configuration trait for the pallet.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Health record hashes
    /// Maps (patient_id, record_id) to record hash entry
    #[pallet::storage]
    #[pallet::getter(fn record_hashes)]
    pub type RecordHashes<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        RecordId,
        RecordHashEntry<T>,
        OptionQuery,
    >;

    /// Record version history
    /// Maps (patient_id, record_id) to version list
    #[pallet::storage]
    pub type RecordVersions<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        RecordId,
        BoundedVec<RecordVersion<T>, ConstU32<100>>,
        ValueQuery,
    >;

    /// Multi-signature access controls
    /// Maps (patient_id, record_id) to required signatures
    #[pallet::storage]
    pub type MultiSigRequirements<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        RecordId,
        MultiSigConfig<T>,
        OptionQuery,
    >;

    /// Audit log entries
    /// Maps (patient_id, record_id) to audit log
    #[pallet::storage]
    pub type AuditLogs<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        RecordId,
        BoundedVec<AuditLogEntry<T>, ConstU32<1000>>,
        ValueQuery,
    >;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Record hash was recorded
        RecordHashRecorded {
            patient: T::AccountId,
            record_id: RecordId,
            record_hash: H256,
            provider: T::AccountId,
        },
        /// Record hash was updated
        RecordHashUpdated {
            patient: T::AccountId,
            record_id: RecordId,
            new_hash: H256,
            version: u32,
        },
        /// Multi-signature requirement was set
        MultiSigRequirementSet {
            patient: T::AccountId,
            record_id: RecordId,
            required_signatures: u32,
        },
        /// Audit log entry was created
        AuditLogCreated {
            patient: T::AccountId,
            record_id: RecordId,
            action: AuditAction,
        },
    }

    /// Errors that can occur in this pallet
    #[pallet::error]
    pub enum Error<T> {
        /// Record not found
        RecordNotFound,
        /// Invalid hash format
        InvalidHash,
        /// Insufficient signatures for multi-sig requirement
        InsufficientSignatures,
        /// Unauthorized access
        Unauthorized,
        /// Too many signers (exceeds BoundedVec limit)
        TooManySigners,
    }

    /// Hooks for the pallet
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    /// Extrinsics for the pallet
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Record a health record hash
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::record_hash())]
        pub fn record_hash(
            origin: OriginFor<T>,
            patient: T::AccountId,
            record_id: RecordId,
            record_hash: H256,
            record_type: RecordType,
            ipfs_cid: Option<Vec<u8>>,
        ) -> DispatchResult {
            let provider = ensure_signed(origin)?;

            // Check authorization (simplified - in production, check consent)
            // For now, allow provider to record hash

            let ipfs_cid_bounded = ipfs_cid.map(|cid| {
                BoundedVec::try_from(cid).unwrap_or_default()
            });
            
            let entry = RecordHashEntry {
                record_hash,
                record_type,
                provider: provider.clone(),
                created_at: <frame_system::Pallet<T>>::block_number(),
                ipfs_cid: ipfs_cid_bounded,
                version: 1,
            };

            RecordHashes::<T>::insert(&patient, &record_id, entry.clone());

            // Initialize version history
            let version = RecordVersion {
                hash: record_hash,
                version: 1,
                created_at: <frame_system::Pallet<T>>::block_number(),
                provider: provider.clone(),
            };
            RecordVersions::<T>::mutate(&patient, &record_id, |versions| {
                let _ = versions.try_push(version);
            });

            // Create audit log entry
            Self::add_audit_log(
                &patient,
                &record_id,
                AuditAction::RecordCreated,
                &provider,
            );

            Self::deposit_event(Event::RecordHashRecorded {
                patient,
                record_id,
                record_hash,
                provider,
            });

            Ok(())
        }

        /// Update a health record hash (creates new version)
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::update_hash())]
        pub fn update_hash(
            origin: OriginFor<T>,
            patient: T::AccountId,
            record_id: RecordId,
            new_hash: H256,
            ipfs_cid: Option<Vec<u8>>,
        ) -> DispatchResult {
            let provider = ensure_signed(origin)?;

            let mut entry = RecordHashes::<T>::get(&patient, &record_id)
                .ok_or(Error::<T>::RecordNotFound)?;

            // Check multi-signature requirements if set
            if let Some(multi_sig) = MultiSigRequirements::<T>::get(&patient, &record_id) {
                // In production, verify signatures here
                // For now, simplified check
            }

            // Increment version
            entry.version += 1;
            entry.record_hash = new_hash;
            entry.ipfs_cid = ipfs_cid.map(|cid| {
                BoundedVec::try_from(cid).unwrap_or_default()
            });
            entry.created_at = <frame_system::Pallet<T>>::block_number();

            RecordHashes::<T>::insert(&patient, &record_id, entry.clone());

            // Add to version history
            let version = RecordVersion {
                hash: new_hash,
                version: entry.version,
                created_at: <frame_system::Pallet<T>>::block_number(),
                provider: provider.clone(),
            };
            RecordVersions::<T>::mutate(&patient, &record_id, |versions| {
                let _ = versions.try_push(version);
            });

            // Create audit log entry
            Self::add_audit_log(
                &patient,
                &record_id,
                AuditAction::RecordUpdated,
                &provider,
            );

            Self::deposit_event(Event::RecordHashUpdated {
                patient,
                record_id,
                new_hash,
                version: entry.version,
            });

            Ok(())
        }

        /// Set multi-signature requirement for a record
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::set_multi_sig())]
        pub fn set_multi_sig_requirement(
            origin: OriginFor<T>,
            patient: T::AccountId,
            record_id: RecordId,
            required_signatures: u32,
            authorized_signers: Vec<T::AccountId>,
        ) -> DispatchResult {
            let _caller = ensure_signed(origin)?;

            // Only patient or authorized provider can set multi-sig
            // Simplified check for now

            // Convert authorized_signers to BoundedVec
            let authorized_signers_bounded = BoundedVec::try_from(authorized_signers)
                .map_err(|_| Error::<T>::TooManySigners)?;

            let config = MultiSigConfig {
                required_signatures,
                authorized_signers: authorized_signers_bounded,
            };

            MultiSigRequirements::<T>::insert(&patient, &record_id, config);

            Self::deposit_event(Event::MultiSigRequirementSet {
                patient,
                record_id,
                required_signatures,
            });

            Ok(())
        }
    }


/// Helper functions
    impl<T: Config> Pallet<T> {
        /// Add audit log entry
        fn add_audit_log(
            patient: &T::AccountId,
            record_id: &RecordId,
            action: AuditAction,
            actor: &T::AccountId,
        ) {
            let log_entry = AuditLogEntry {
                action: action.clone(),
                actor: actor.clone(),
                timestamp: <frame_system::Pallet<T>>::block_number(),
            };

            AuditLogs::<T>::mutate(patient, record_id, |logs| {
                let _ = logs.try_push(log_entry);
            });

            Self::deposit_event(Event::AuditLogCreated {
                patient: patient.clone(),
                record_id: record_id.clone(),
                action: action.clone(),
            });
        }
    }

/// Weight information for extrinsics
pub trait WeightInfo {
    fn record_hash() -> Weight;
    fn update_hash() -> Weight;
    fn set_multi_sig() -> Weight;
}

/// Record ID type
pub type RecordId = u64;

/// Record hash entry
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct RecordHashEntry<T: frame_system::Config> {
    /// Cryptographic hash of the record
    pub record_hash: sp_core::H256,
    /// Type of record
    pub record_type: RecordType,
    /// Provider who created/updated the record
    pub provider: T::AccountId,
    /// Block number when created/updated
    pub created_at: BlockNumberFor<T>,
    /// IPFS CID if record is stored off-chain
    pub ipfs_cid: Option<BoundedVec<u8, ConstU32<256>>>,
    /// Version number
    pub version: u32,
}

/// Record type
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum RecordType {
    /// Clinical encounter
    ClinicalEncounter,
    /// Lab results
    LabResults,
    /// Imaging study
    Imaging,
    /// Medication record
    Medication,
    /// Diagnosis
    Diagnosis,
    /// Vital signs
    Vitals,
    /// Treatment plan
    TreatmentPlan,
    /// Other
    Other(BoundedVec<u8, ConstU32<256>>),
}

/// Record version
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct RecordVersion<T: frame_system::Config> {
    /// Hash of this version
    pub hash: sp_core::H256,
    /// Version number
    pub version: u32,
    /// Block number when version was created
    pub created_at: BlockNumberFor<T>,
    /// Provider who created this version
    pub provider: T::AccountId,
}

/// Multi-signature configuration
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct MultiSigConfig<T: frame_system::Config> {
    /// Number of signatures required
    pub required_signatures: u32,
    /// List of authorized signers
    pub authorized_signers: BoundedVec<T::AccountId, ConstU32<100>>,
}

/// Audit action types
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum AuditAction {
    /// Record was created
    RecordCreated,
    /// Record was updated
    RecordUpdated,
    /// Record was accessed
    RecordAccessed,
    /// Record was deleted
    RecordDeleted,
    /// Access was granted
    AccessGranted,
    /// Access was revoked
    AccessRevoked,
}

/// Audit log entry
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct AuditLogEntry<T: frame_system::Config> {
    /// Action performed
    pub action: AuditAction,
    /// Account that performed the action
    pub actor: T::AccountId,
    /// Block number when action occurred
    pub timestamp: BlockNumberFor<T>,
}
}

pub use pallet::*;
