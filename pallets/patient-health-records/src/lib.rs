//! # ABENA Patient Health Records Pallet
//!
//! Encrypted, on-chain health record metadata and access control for the ABENA IHR.
//! Uses quantum-resistant encryption options (e.g. Kyber, Dilithium) for future-proof
//! security. Stores encrypted payloads and permissions; full record hashes are in
//! the Health Record Hash pallet with IPFS for off-chain storage.

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
    use sp_std::vec::Vec;
    use sp_core::H256;
    use super::{EncryptedHealthRecord, PermissionLevel, EncryptionMetadataRecord, EncryptionAlgorithm};
    use crate::WeightInfo;

    /// Configuration trait for the pallet.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// The pallet ID for reserving funds
        type PalletId: Get<frame_support::PalletId>;
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Storage for patient health records
    /// Maps patient ID to their encrypted health record
    #[pallet::storage]
    #[pallet::getter(fn health_records)]
    pub type HealthRecords<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        EncryptedHealthRecord<T>,
        OptionQuery,
    >;

    /// Access control list for health records
    /// Maps (patient_id, authorized_account) to permission level
    #[pallet::storage]
    #[pallet::getter(fn access_permissions)]
    pub type AccessPermissions<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId, // Patient ID
        Blake2_128Concat,
        T::AccountId, // Authorized account
        PermissionLevel,
        OptionQuery,
    >;

    /// Quantum-resistant encryption metadata
    /// Stores encryption parameters and algorithm identifiers
    #[pallet::storage]
    #[pallet::getter(fn encryption_metadata)]
    pub type EncryptionMetadata<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        EncryptionMetadataRecord,
        OptionQuery,
    >;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// A new health record was created
        HealthRecordCreated {
            patient: T::AccountId,
        },
        /// A health record was updated
        HealthRecordUpdated {
            patient: T::AccountId,
        },
        /// Access permission was granted
        AccessGranted {
            patient: T::AccountId,
            authorized_account: T::AccountId,
            permission: PermissionLevel,
        },
        /// Access permission was revoked
        AccessRevoked {
            patient: T::AccountId,
            authorized_account: T::AccountId,
        },
        /// Encryption metadata was updated
        EncryptionMetadataUpdated {
            patient: T::AccountId,
        },
    }

    /// Errors that can occur in this pallet
    #[pallet::error]
    pub enum Error<T> {
        /// Health record does not exist
        RecordNotFound,
        /// Unauthorized access attempt
        UnauthorizedAccess,
        /// Invalid encryption metadata
        InvalidEncryptionMetadata,
        /// Insufficient deposit
        InsufficientDeposit,
        /// Record already exists
        RecordAlreadyExists,
        /// Data too large for BoundedVec
        DataTooLarge,
    }

    /// Hooks for the pallet
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    /// Extrinsics for the pallet
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new encrypted health record
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::create_health_record())]
        pub fn create_health_record(
            origin: OriginFor<T>,
            encrypted_data: Vec<u8>,
            encryption_metadata: EncryptionMetadataRecord,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            // Ensure record doesn't already exist
            ensure!(
                !HealthRecords::<T>::contains_key(&patient),
                Error::<T>::RecordAlreadyExists
            );

            // Validate encryption metadata
            ensure!(
                encryption_metadata.algorithm != EncryptionAlgorithm::Unknown,
                Error::<T>::InvalidEncryptionMetadata
            );

            // Convert Vec to BoundedVec
            let data = BoundedVec::try_from(encrypted_data)
                .map_err(|_| Error::<T>::DataTooLarge)?;

            // Create encrypted record
            let record = EncryptedHealthRecord {
                data,
                created_at: <frame_system::Pallet<T>>::block_number(),
                updated_at: <frame_system::Pallet<T>>::block_number(),
            };

            HealthRecords::<T>::insert(&patient, record.clone());
            EncryptionMetadata::<T>::insert(&patient, encryption_metadata.clone());

            Self::deposit_event(Event::HealthRecordCreated {
                patient: patient.clone(),
            });

            Ok(())
        }

        /// Update an existing health record
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::update_health_record())]
        pub fn update_health_record(
            origin: OriginFor<T>,
            patient: T::AccountId,
            encrypted_data: Vec<u8>,
        ) -> DispatchResult {
            let updater = ensure_signed(origin)?;

            // Check if record exists
            let mut record = HealthRecords::<T>::get(&patient)
                .ok_or(Error::<T>::RecordNotFound)?;

            // Check authorization: patient or authorized account
            ensure!(
                updater == patient || Self::has_permission(&patient, &updater, PermissionLevel::Write),
                Error::<T>::UnauthorizedAccess
            );

            // Convert Vec to BoundedVec
            let data = BoundedVec::try_from(encrypted_data)
                .map_err(|_| Error::<T>::DataTooLarge)?;

            // Update record
            record.data = data;
            record.updated_at = <frame_system::Pallet<T>>::block_number();

            HealthRecords::<T>::insert(&patient, record);

            Self::deposit_event(Event::HealthRecordUpdated { patient });

            Ok(())
        }

        /// Grant access to a health record
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::grant_access())]
        pub fn grant_access(
            origin: OriginFor<T>,
            authorized_account: T::AccountId,
            permission: PermissionLevel,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            // Ensure record exists
            ensure!(
                HealthRecords::<T>::contains_key(&patient),
                Error::<T>::RecordNotFound
            );

            AccessPermissions::<T>::insert(&patient, &authorized_account, permission.clone());

            Self::deposit_event(Event::AccessGranted {
                patient,
                authorized_account,
                permission,
            });

            Ok(())
        }

        /// Revoke access to a health record
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::revoke_access())]
        pub fn revoke_access(
            origin: OriginFor<T>,
            authorized_account: T::AccountId,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            AccessPermissions::<T>::remove(&patient, &authorized_account);

            Self::deposit_event(Event::AccessRevoked {
                patient,
                authorized_account,
            });

            Ok(())
        }

        /// Update encryption metadata (for migration to new quantum-resistant algorithms)
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::update_encryption_metadata())]
        pub fn update_encryption_metadata(
            origin: OriginFor<T>,
            metadata: EncryptionMetadataRecord,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            // Ensure record exists
            ensure!(
                HealthRecords::<T>::contains_key(&patient),
                Error::<T>::RecordNotFound
            );

            // Validate new metadata
            ensure!(
                metadata.algorithm != EncryptionAlgorithm::Unknown,
                Error::<T>::InvalidEncryptionMetadata
            );

            EncryptionMetadata::<T>::insert(&patient, metadata.clone());

            Self::deposit_event(Event::EncryptionMetadataUpdated { patient });

            Ok(())
        }
    }


    /// Helper function to check access permissions
    impl<T: Config> Pallet<T> {
        pub fn has_permission(
            patient: &T::AccountId,
            account: &T::AccountId,
            required_level: PermissionLevel,
        ) -> bool {
            if patient == account {
                return true; // Patient always has full access
            }

            if let Some(permission) = AccessPermissions::<T>::get(patient, account) {
                match (permission, required_level) {
                    (PermissionLevel::Read, PermissionLevel::Read) => true,
                    (PermissionLevel::Write, _) => true,
                    (PermissionLevel::Full, _) => true,
                    _ => false,
                }
            } else {
                false
            }
        }
    }
}

/// Weight information for extrinsics
pub trait WeightInfo {
    fn create_health_record() -> Weight;
    fn update_health_record() -> Weight;
    fn grant_access() -> Weight;
    fn revoke_access() -> Weight;
    fn update_encryption_metadata() -> Weight;
}

/// Encrypted health record structure
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct EncryptedHealthRecord<T: frame_system::Config> {
    /// Encrypted health data (using quantum-resistant encryption)
    pub data: BoundedVec<u8, ConstU32<4096>>,
    /// Block number when record was created
    pub created_at: BlockNumberFor<T>,
    /// Block number when record was last updated
    pub updated_at: BlockNumberFor<T>,
}

/// Permission levels for accessing health records
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum PermissionLevel {
    /// Read-only access
    Read,
    /// Read and write access
    Write,
    /// Full access including deletion
    Full,
}

/// Encryption algorithm identifiers for quantum-resistant encryption
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum EncryptionAlgorithm {
    /// Unknown/unspecified algorithm
    Unknown,
    /// CRYSTALS-Kyber (Post-quantum key encapsulation)
    Kyber,
    /// CRYSTALS-Dilithium (Post-quantum digital signatures)
    Dilithium,
    /// SPHINCS+ (Post-quantum hash-based signatures)
    SphincsPlus,
    /// NTRU (Post-quantum lattice-based encryption)
    Ntru,
}

/// Encryption metadata record
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct EncryptionMetadataRecord {
    /// Encryption algorithm used
    pub algorithm: EncryptionAlgorithm,
    /// Algorithm version/parameters
    pub parameters: BoundedVec<u8, ConstU32<256>>,
    /// Key derivation function identifier
    pub kdf: BoundedVec<u8, ConstU32<128>>,
    /// Additional metadata
    pub metadata: BoundedVec<u8, ConstU32<512>>,
}

pub use pallet::*;
