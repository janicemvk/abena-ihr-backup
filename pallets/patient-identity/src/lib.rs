//! ABENA Patient Identity Pallet
//!
//! Manages decentralized patient identities for the ABENA Integrative Health Record system.
//! Provides quantum-resistant identity management, consent tracking, and access control
//! for multi-modality healthcare (Western, TCM, Ayurveda, etc.)

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Encode, Decode, MaxEncodedLen};
use scale_info::TypeInfo;
use sp_runtime::RuntimeDebug;
use frame_system::pallet_prelude::BlockNumberFor;
use frame_support::weights::Weight;

#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
pub mod weights;

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;
    use sp_core::H256;
    use sp_runtime::traits::UniqueSaturatedInto;
    use crate::WeightInfo;
    
    /// Therapeutic modalities supported in ABENA
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum TherapeuticModality {
        /// Western Medicine
        WesternMedicine,
        /// Traditional Chinese Medicine
        TraditionalChineseMedicine,
        /// Ayurveda
        Ayurveda,
        /// Homeopathy
        Homeopathy,
        /// Naturopathy
        Naturopathy,
        /// Other therapeutic modality
        Other,
    }
    
    /// Patient consent record for a specific modality
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct ConsentRecord {
        /// Therapeutic modality
        pub modality: TherapeuticModality,
        /// Whether consent is granted
        pub granted: bool,
        /// Timestamp when consent was granted/updated
        pub granted_at: u64,
        /// Optional expiration timestamp
        pub expires_at: Option<u64>,
    }
    
    /// Patient Decentralized Identifier (DID)
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct PatientDID<T: Config> {
        /// Unique patient identifier
        pub patient_account: T::AccountId,
        /// Public key for verification (quantum-resistant in production - ed25519 for now)
        pub public_key: [u8; 32],
        /// Hash of patient metadata (name, DOB, etc. - NOT stored on-chain)
        pub metadata_hash: [u8; 32],
        /// Creation timestamp
        pub created_at: u64,
        /// Last updated timestamp
        pub updated_at: u64,
        /// Emergency contact account (can override access)
        pub emergency_contact: Option<T::AccountId>,
        /// Is this identity active?
        pub active: bool,
    }
    
    /// Provider access record
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct ProviderAccess<T: Config> {
        /// Provider account ID
        pub provider_account: T::AccountId,
        /// Timestamp when access was granted
        pub granted_at: u64,
        /// Optional expiration timestamp
        pub expires_at: Option<u64>,
        /// Level of access granted
        pub access_level: AccessLevel,
    }
    
    /// Access levels for providers
    #[derive(Encode, Decode, Clone, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum AccessLevel {
        /// Read-only access
        Read,
        /// Read and write access
        ReadWrite,
        /// Emergency access (full access)
        Emergency,
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        
        /// Maximum number of providers that can access a single patient
        #[pallet::constant]
        type MaxProvidersPerPatient: Get<u32>;
        
        /// Maximum number of consent records per patient
        #[pallet::constant]
        type MaxConsentRecords: Get<u32>;
        
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
    }

    /// Storage for patient DIDs
    #[pallet::storage]
    #[pallet::getter(fn patient_identity)]
    pub type PatientIdentities<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        PatientDID<T>,
        OptionQuery,
    >;
    
    /// Storage for provider access permissions
    #[pallet::storage]
    #[pallet::getter(fn provider_access)]
    pub type ProviderAccessList<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId, // Patient account
        Blake2_128Concat,
        T::AccountId, // Provider account
        ProviderAccess<T>,
        OptionQuery,
    >;
    
    /// Storage for consent records
    #[pallet::storage]
    #[pallet::getter(fn consent_records)]
    pub type ConsentRecords<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId, // Patient account
        Blake2_128Concat,
        TherapeuticModality,
        ConsentRecord,
        OptionQuery,
    >;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Patient DID created [patient_account, metadata_hash]
        PatientRegistered {
            patient: T::AccountId,
            metadata_hash: [u8; 32],
        },
        /// Consent updated [patient_account, modality, granted]
        ConsentUpdated {
            patient: T::AccountId,
            modality: TherapeuticModality,
            granted: bool,
        },
        /// Provider access granted [patient_account, provider_account, access_level]
        ProviderAccessGranted {
            patient: T::AccountId,
            provider: T::AccountId,
            access_level: AccessLevel,
        },
        /// Provider access revoked [patient_account, provider_account]
        ProviderAccessRevoked {
            patient: T::AccountId,
            provider: T::AccountId,
        },
        /// Emergency access activated [patient_account, provider_account]
        EmergencyAccessActivated {
            patient: T::AccountId,
            provider: T::AccountId,
        },
        /// Patient identity deactivated [patient_account]
        PatientDeactivated {
            patient: T::AccountId,
        },
    }

    #[pallet::error]
    pub enum Error<T> {
        /// Patient already registered
        PatientAlreadyExists,
        /// Patient does not exist
        PatientNotFound,
        /// Not authorized to perform this action
        NotAuthorized,
        /// Invalid public key
        InvalidPublicKey,
        /// Consent already exists for this modality
        ConsentAlreadyExists,
        /// Consent not found
        ConsentNotFound,
        /// Provider access already granted
        ProviderAccessAlreadyGranted,
        /// Provider access not found
        ProviderAccessNotFound,
        /// Maximum number of providers reached
        TooManyProviders,
        /// Maximum number of consent records reached
        TooManyConsentRecords,
        /// Patient identity is deactivated
        PatientDeactivated,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        
        /// Register a new patient with a decentralized identifier
        ///
        /// Parameters:
        /// - `public_key`: Patient's public key (32 bytes, ed25519 for now, quantum-resistant ready)
        /// - `metadata_hash`: Hash of patient metadata (NOT actual PHI data)
        /// - `emergency_contact`: Optional emergency contact account
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::register_patient())]
        pub fn register_patient(
            origin: OriginFor<T>,
            public_key: [u8; 32],
            metadata_hash: [u8; 32],
            emergency_contact: Option<T::AccountId>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            
            // Ensure patient doesn't already exist
            ensure!(
                !PatientIdentities::<T>::contains_key(&who),
                Error::<T>::PatientAlreadyExists
            );
            
            // Validate public key (basic check - enhance for quantum-resistant later)
            ensure!(
                public_key != [0u8; 32],
                Error::<T>::InvalidPublicKey
            );
            
            // Get current timestamp
            let now = Self::current_timestamp();
            
            // Create patient DID
            let patient_did = PatientDID {
                patient_account: who.clone(),
                public_key,
                metadata_hash,
                created_at: now,
                updated_at: now,
                emergency_contact,
                active: true,
            };
            
            // Store patient DID
            PatientIdentities::<T>::insert(&who, patient_did);
            
            // Emit event
            Self::deposit_event(Event::PatientRegistered {
                patient: who,
                metadata_hash,
            });
            
            Ok(())
        }
        
        /// Update consent for a specific therapeutic modality
        ///
        /// Parameters:
        /// - `modality`: The therapeutic modality
        /// - `granted`: Whether consent is granted (true) or revoked (false)
        /// - `expires_at`: Optional expiration timestamp
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::update_consent())]
        pub fn update_consent(
            origin: OriginFor<T>,
            modality: TherapeuticModality,
            granted: bool,
            expires_at: Option<u64>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            
            // Ensure patient exists
            let patient = PatientIdentities::<T>::get(&who)
                .ok_or(Error::<T>::PatientNotFound)?;
            
            // Ensure patient is active
            ensure!(patient.active, Error::<T>::PatientDeactivated);
            
            // Check maximum consent records limit
            let consent_count = ConsentRecords::<T>::iter_prefix(&who).count() as u32;
            ensure!(
                consent_count < T::MaxConsentRecords::get(),
                Error::<T>::TooManyConsentRecords
            );
            
            let now = Self::current_timestamp();
            
            // Create consent record
            let consent = ConsentRecord {
                modality: modality.clone(),
                granted,
                granted_at: now,
                expires_at,
            };
            
            // Store consent
            ConsentRecords::<T>::insert(&who, &modality, consent);
            
            // Emit event
            Self::deposit_event(Event::ConsentUpdated {
                patient: who,
                modality,
                granted,
            });
            
            Ok(())
        }
        
        /// Grant provider access to patient records
        ///
        /// Parameters:
        /// - `provider`: The provider's account ID
        /// - `access_level`: Level of access to grant
        /// - `expires_at`: Optional expiration timestamp
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::grant_provider_access())]
        pub fn grant_provider_access(
            origin: OriginFor<T>,
            provider: T::AccountId,
            access_level: AccessLevel,
            expires_at: Option<u64>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            
            // Ensure patient exists
            let patient = PatientIdentities::<T>::get(&who)
                .ok_or(Error::<T>::PatientNotFound)?;
            
            // Ensure patient is active
            ensure!(patient.active, Error::<T>::PatientDeactivated);
            
            // Ensure access doesn't already exist
            ensure!(
                !ProviderAccessList::<T>::contains_key(&who, &provider),
                Error::<T>::ProviderAccessAlreadyGranted
            );
            
            // Check maximum providers limit
            let provider_count = ProviderAccessList::<T>::iter_prefix(&who).count() as u32;
            ensure!(
                provider_count < T::MaxProvidersPerPatient::get(),
                Error::<T>::TooManyProviders
            );
            
            let now = Self::current_timestamp();
            
            // Create provider access record
            let access = ProviderAccess {
                provider_account: provider.clone(),
                granted_at: now,
                expires_at,
                access_level: access_level.clone(),
            };
            
            // Store provider access
            ProviderAccessList::<T>::insert(&who, &provider, access);
            
            // Emit event
            Self::deposit_event(Event::ProviderAccessGranted {
                patient: who,
                provider,
                access_level,
            });
            
            Ok(())
        }
        
        /// Revoke provider access to patient records
        ///
        /// Parameters:
        /// - `provider`: The provider's account ID to revoke
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::revoke_provider_access())]
        pub fn revoke_provider_access(
            origin: OriginFor<T>,
            provider: T::AccountId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            
            // Ensure patient exists
            ensure!(
                PatientIdentities::<T>::contains_key(&who),
                Error::<T>::PatientNotFound
            );
            
            // Ensure access exists
            ensure!(
                ProviderAccessList::<T>::contains_key(&who, &provider),
                Error::<T>::ProviderAccessNotFound
            );
            
            // Remove provider access
            ProviderAccessList::<T>::remove(&who, &provider);
            
            // Emit event
            Self::deposit_event(Event::ProviderAccessRevoked {
                patient: who,
                provider,
            });
            
            Ok(())
        }
        
        /// Emergency access override (can be called by emergency contact or authorized personnel)
        ///
        /// Parameters:
        /// - `patient`: The patient account to access
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::emergency_access())]
        pub fn emergency_access(
            origin: OriginFor<T>,
            patient: T::AccountId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            
            // Get patient DID
            let patient_did = PatientIdentities::<T>::get(&patient)
                .ok_or(Error::<T>::PatientNotFound)?;
            
            // Verify caller is emergency contact
            ensure!(
                patient_did.emergency_contact == Some(who.clone()),
                Error::<T>::NotAuthorized
            );
            
            let now = Self::current_timestamp();
            
            // Grant emergency access (24 hour expiration)
            let access = ProviderAccess {
                provider_account: who.clone(),
                granted_at: now,
                expires_at: Some(now + 86400), // 24 hours in seconds
                access_level: AccessLevel::Emergency,
            };
            
            ProviderAccessList::<T>::insert(&patient, &who, access);
            
            // Emit event
            Self::deposit_event(Event::EmergencyAccessActivated {
                patient,
                provider: who,
            });
            
            Ok(())
        }
        
        /// Deactivate patient identity (soft delete - preserves audit trail)
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::deactivate_patient())]
        pub fn deactivate_patient(
            origin: OriginFor<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            
            // Get patient DID
            let mut patient_did = PatientIdentities::<T>::get(&who)
                .ok_or(Error::<T>::PatientNotFound)?;
            
            // Deactivate
            patient_did.active = false;
            patient_did.updated_at = Self::current_timestamp();
            
            // Update storage
            PatientIdentities::<T>::insert(&who, patient_did);
            
            // Emit event
            Self::deposit_event(Event::PatientDeactivated {
                patient: who,
            });
            
            Ok(())
        }
    }
    
    impl<T: Config> Pallet<T> {
        /// Get current timestamp (uses block number converted to timestamp)
        /// In production, integrate with pallet_timestamp for accurate timestamps
        fn current_timestamp() -> u64 {
            // Convert block number to approximate timestamp
            // Assuming 6 second block time: block_number * 6
            let block_number = <frame_system::Pallet<T>>::block_number();
            // Use block number as base timestamp (can be enhanced with actual timestamp pallet)
            // Convert BlockNumber to u64 for timestamp calculation
            let block_u64: u64 = block_number.unique_saturated_into();
            block_u64 * 6
        }
        
        /// Verify if a provider has access to a patient's records
        pub fn verify_provider_access(
            patient: &T::AccountId,
            provider: &T::AccountId,
        ) -> bool {
            if let Some(access) = ProviderAccessList::<T>::get(patient, provider) {
                // Check if access hasn't expired
                let now = Self::current_timestamp();
                if let Some(expires_at) = access.expires_at {
                    if now > expires_at {
                        return false;
                    }
                }
                true
            } else {
                false
            }
        }
        
        /// Verify if patient has granted consent for a specific modality
        pub fn verify_consent(
            patient: &T::AccountId,
            modality: &TherapeuticModality,
        ) -> bool {
            if let Some(consent) = ConsentRecords::<T>::get(patient, modality) {
                if !consent.granted {
                    return false;
                }
                
                // Check if consent hasn't expired
                let now = Self::current_timestamp();
                if let Some(expires_at) = consent.expires_at {
                    if now > expires_at {
                        return false;
                    }
                }
                true
            } else {
                false
            }
        }
}

/// Weight information for extrinsics
pub trait WeightInfo {
    fn register_patient() -> Weight;
    fn update_consent() -> Weight;
    fn grant_provider_access() -> Weight;
    fn revoke_provider_access() -> Weight;
    fn emergency_access() -> Weight;
    fn deactivate_patient() -> Weight;
}
