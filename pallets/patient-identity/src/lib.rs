//! # Patient Identity Pallet
//!
//! A pallet for managing patient decentralized identifiers (DIDs),
//! zero-knowledge proofs for identity verification, and consent management.

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
        traits::{Currency, ReservableCurrency},
        traits::ConstU32,
    };
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;
    use sp_core::H256;
    use sp_runtime::BoundedVec;    /// Configuration trait for the pallet.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// The pallet ID for reserving funds
        type PalletId: Get<frame_support::PalletId>;
        /// The currency type for deposits
        type Currency: Currency<Self::AccountId> + ReservableCurrency<Self::AccountId>;
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Patient DID registry
    /// Maps account ID to their DID document
    #[pallet::storage]
    #[pallet::getter(fn patient_dids)]
    pub type PatientDIDs<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        PatientDID<T>,
        OptionQuery,
    >;

    /// Provider access registry
    /// Maps (patient_id, provider_id) to access permissions
    #[pallet::storage]
    pub type ProviderAccess<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        T::AccountId,
        ProviderAccessRecord<T>,
        OptionQuery,
    >;

    /// Zero-knowledge proof credentials
    /// Maps (patient_id, credential_type) to proof metadata
    #[pallet::storage]
    pub type ZKCredentials<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        CredentialType,
        ZKProofMetadata<T>,
        OptionQuery,
    >;

    /// Patient consent records
    /// Maps (patient_id, modality) to consent details per therapeutic modality
    #[pallet::storage]
    #[pallet::getter(fn consent_records)]
    pub type ConsentRecords<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        TherapeuticModality,
        ConsentRecord<T>,
        OptionQuery,
    >;

    /// Cross-provider authentication tokens
    #[pallet::storage]
    pub type AuthTokens<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        H256,
        AuthTokenData<T>,
        OptionQuery,
    >;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Patient was registered
        PatientRegistered {
            patient: T::AccountId,
            did: Vec<u8>,
            metadata_hash: H256,
        },
        /// Patient DID was registered (backward compatibility)
        DIDRegistered {
            patient: T::AccountId,
            did: Vec<u8>,
        },
        /// DID was updated
        DIDUpdated {
            patient: T::AccountId,
        },
        /// Zero-knowledge credential was issued
        ZKCredentialIssued {
            patient: T::AccountId,
            credential_type: CredentialType,
        },
        /// Consent was updated for a modality
        ConsentUpdated {
            patient: T::AccountId,
            modality: TherapeuticModality,
            granted: bool,
        },
        /// Provider access was granted
        ProviderAccessGranted {
            patient: T::AccountId,
            provider: T::AccountId,
            scope: ConsentScope,
        },
        /// Provider access was revoked
        ProviderAccessRevoked {
            patient: T::AccountId,
            provider: T::AccountId,
        },
        /// Emergency access was granted
        EmergencyAccessGranted {
            patient: T::AccountId,
            requester: T::AccountId,
            reason: Vec<u8>,
            expires_at: BlockNumberFor<T>,
        },
        /// Consent was granted (backward compatibility)
        ConsentGranted {
            patient: T::AccountId,
            provider: T::AccountId,
            scope: ConsentScope,
        },
        /// Consent was revoked (backward compatibility)
        ConsentRevoked {
            patient: T::AccountId,
            provider: T::AccountId,
        },
        /// Authentication token was issued
        AuthTokenIssued {
            patient: T::AccountId,
            provider: T::AccountId,
            token_hash: H256,
        },
    }

    /// Errors that can occur in this pallet
    #[pallet::error]
    pub enum Error<T> {
        /// DID not found
        DIDNotFound,
        /// Invalid DID format
        InvalidDIDFormat,
        /// Consent already exists
        ConsentAlreadyExists,
        /// Consent not found
        ConsentNotFound,
        /// Invalid authentication token
        InvalidAuthToken,
        /// Data too large for bounded vector
        DataTooLarge,
        /// Unauthorized access
        Unauthorized,
    }

    /// Hooks for the pallet
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    /// Extrinsics for the pallet
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Register a patient (creates DID)
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::register_patient())]
        pub fn register_patient(
            origin: OriginFor<T>,
            did: Vec<u8>,
            public_keys: Vec<PublicKey>,
            metadata_hash: H256,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            // Validate DID format (basic validation)
            ensure!(did.len() > 0, Error::<T>::InvalidDIDFormat);

            // Ensure patient not already registered
            ensure!(
                !PatientDIDs::<T>::contains_key(&patient),
                Error::<T>::DIDNotFound // Reuse error for "already exists"
            );

            // Convert to BoundedVec (clone did first for event)
            let did_bounded = BoundedVec::try_from(did.clone())
                .map_err(|_| Error::<T>::DataTooLarge)?;
            let public_keys_bounded = BoundedVec::try_from(public_keys)
                .map_err(|_| Error::<T>::DataTooLarge)?;

            let patient_did = PatientDID {
                did: did_bounded,
                public_keys: public_keys_bounded,
                metadata_hash,
                created_at: <frame_system::Pallet<T>>::block_number(),
                updated_at: <frame_system::Pallet<T>>::block_number(),
            };

            PatientDIDs::<T>::insert(&patient, patient_did);

            Self::deposit_event(Event::PatientRegistered {
                patient,
                did,
                metadata_hash,
            });

            Ok(())
        }

        /// Register a patient DID (alias for backward compatibility)
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::register_did())]
        pub fn register_did(
            origin: OriginFor<T>,
            did: Vec<u8>,
            public_keys: Vec<PublicKey>,
        ) -> DispatchResult {
            // Use default metadata hash (zero hash) for backward compatibility
            Self::register_patient(origin, did, public_keys, H256::default())
        }

        /// Update patient DID
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::update_did())]
        pub fn update_did(
            origin: OriginFor<T>,
            public_keys: Vec<PublicKey>,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            let mut patient_did = PatientDIDs::<T>::get(&patient)
                .ok_or(Error::<T>::DIDNotFound)?;

            // Convert public_keys to BoundedVec
            let public_keys_bounded = BoundedVec::try_from(public_keys)
                .map_err(|_| Error::<T>::DataTooLarge)?;
            patient_did.public_keys = public_keys_bounded;
            patient_did.updated_at = <frame_system::Pallet<T>>::block_number();

            PatientDIDs::<T>::insert(&patient, patient_did);

            Self::deposit_event(Event::DIDUpdated { patient });

            Ok(())
        }

        /// Issue zero-knowledge proof credential
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::issue_zk_credential())]
        pub fn issue_zk_credential(
            origin: OriginFor<T>,
            patient: T::AccountId,
            credential_type: CredentialType,
            proof_hash: H256,
        ) -> DispatchResult {
            let issuer = ensure_signed(origin)?;

            // Verify issuer has permission (simplified - in production, add proper checks)
            ensure!(
                PatientDIDs::<T>::contains_key(&patient),
                Error::<T>::DIDNotFound
            );

            let metadata = ZKProofMetadata {
                proof_hash,
                issuer: issuer.clone(),
                issued_at: <frame_system::Pallet<T>>::block_number(),
                expires_at: None,
            };

            ZKCredentials::<T>::insert(&patient, &credential_type, metadata);

            Self::deposit_event(Event::ZKCredentialIssued {
                patient,
                credential_type,
            });

            Ok(())
        }

        /// Update consent for specific therapeutic modality
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::update_consent())]
        pub fn update_consent(
            origin: OriginFor<T>,
            modality: TherapeuticModality,
            granted: bool,
            expires_at: Option<BlockNumberFor<T>>,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            // Ensure patient is registered
            ensure!(
                PatientDIDs::<T>::contains_key(&patient),
                Error::<T>::DIDNotFound
            );

            let consent = ConsentRecord {
                patient: patient.clone(),
                modality,
                granted,
                granted_at: <frame_system::Pallet<T>>::block_number(),
                expires_at,
                revoked: !granted,
            };

            ConsentRecords::<T>::insert(&patient, &modality, consent.clone());

            Self::deposit_event(Event::ConsentUpdated {
                patient,
                modality,
                granted,
            });

            Ok(())
        }

        /// Grant consent to a provider (backward compatibility)
        #[pallet::call_index(8)]
        #[pallet::weight(T::WeightInfo::grant_consent())]
        pub fn grant_consent(
            origin: OriginFor<T>,
            provider: T::AccountId,
            scope: ConsentScope,
            expires_at: Option<BlockNumberFor<T>>,
        ) -> DispatchResult {
            // This is kept for backward compatibility
            // In the new model, use grant_provider_access instead
            Self::grant_provider_access(origin, provider, scope, expires_at)
        }

        /// Grant provider access to patient records
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::grant_provider_access())]
        pub fn grant_provider_access(
            origin: OriginFor<T>,
            provider: T::AccountId,
            scope: ConsentScope,
            expires_at: Option<BlockNumberFor<T>>,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            // Ensure patient is registered
            ensure!(
                PatientDIDs::<T>::contains_key(&patient),
                Error::<T>::DIDNotFound
            );

            let access_record = ProviderAccessRecord {
                patient: patient.clone(),
                provider: provider.clone(),
                scope: scope.clone(),
                granted_at: <frame_system::Pallet<T>>::block_number(),
                expires_at,
                revoked: false,
            };

            ProviderAccess::<T>::insert(&patient, &provider, access_record);

            Self::deposit_event(Event::ProviderAccessGranted {
                patient,
                provider,
                scope,
            });

            Ok(())
        }

        /// Revoke provider access
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::revoke_provider_access())]
        pub fn revoke_provider_access(
            origin: OriginFor<T>,
            provider: T::AccountId,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            let mut access_record = ProviderAccess::<T>::get(&patient, &provider)
                .ok_or(Error::<T>::ConsentNotFound)?;

            access_record.revoked = true;

            ProviderAccess::<T>::insert(&patient, &provider, access_record);

            Self::deposit_event(Event::ProviderAccessRevoked {
                patient,
                provider,
            });

            Ok(())
        }

        /// Emergency access override
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::emergency_access())]
        pub fn emergency_access(
            origin: OriginFor<T>,
            patient: T::AccountId,
            reason: Vec<u8>,
            duration_blocks: BlockNumberFor<T>,
        ) -> DispatchResult {
            let requester = ensure_signed(origin)?;

            // In production, verify requester has emergency access authority
            // For now, we'll allow any signed account (can be restricted later)

            // Ensure patient is registered
            ensure!(
                PatientDIDs::<T>::contains_key(&patient),
                Error::<T>::DIDNotFound
            );

            let reason_bounded = BoundedVec::try_from(reason)
                .map_err(|_| Error::<T>::DataTooLarge)?;

            let current_block = <frame_system::Pallet<T>>::block_number();
            let expires_at = current_block + duration_blocks;

            // Grant temporary emergency access
            let emergency_access = ProviderAccessRecord {
                patient: patient.clone(),
                provider: requester.clone(),
                scope: ConsentScope::FullAccess,
                granted_at: current_block,
                expires_at: Some(expires_at),
                revoked: false,
            };

            ProviderAccess::<T>::insert(&patient, &requester, emergency_access);

            Self::deposit_event(Event::EmergencyAccessGranted {
                patient,
                requester,
                reason: reason_bounded.to_vec(),
                expires_at,
            });

            Ok(())
        }

        /// Revoke consent (backward compatibility)
        #[pallet::call_index(9)]
        #[pallet::weight(T::WeightInfo::revoke_consent())]
        pub fn revoke_consent(
            origin: OriginFor<T>,
            provider: T::AccountId,
        ) -> DispatchResult {
            Self::revoke_provider_access(origin, provider)
        }

        /// Issue cross-provider authentication token
        #[pallet::call_index(10)]
        #[pallet::weight(T::WeightInfo::issue_auth_token())]
        pub fn issue_auth_token(
            origin: OriginFor<T>,
            provider: T::AccountId,
            token_hash: H256,
            expires_at: BlockNumberFor<T>,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            // Verify provider access exists
            let access = ProviderAccess::<T>::get(&patient, &provider)
                .ok_or(Error::<T>::ConsentNotFound)?;

            ensure!(!access.revoked, Error::<T>::Unauthorized);

            let token_data = AuthTokenData {
                patient: patient.clone(),
                provider: provider.clone(),
                issued_at: <frame_system::Pallet<T>>::block_number(),
                expires_at,
            };

            AuthTokens::<T>::insert(&token_hash, token_data);

            Self::deposit_event(Event::AuthTokenIssued {
                patient,
                provider,
                token_hash,
            });

            Ok(())
        }

        /// Verify authentication token
        #[pallet::call_index(11)]
        #[pallet::weight(T::WeightInfo::verify_auth_token())]
        pub fn verify_auth_token(
            origin: OriginFor<T>,
            token_hash: H256,
        ) -> DispatchResult {
            let _verifier = ensure_signed(origin)?;

            let token_data = AuthTokens::<T>::get(&token_hash)
                .ok_or(Error::<T>::InvalidAuthToken)?;

            // Check if token expired
            let current_block = <frame_system::Pallet<T>>::block_number();
            ensure!(
                current_block < token_data.expires_at,
                Error::<T>::InvalidAuthToken
            );

            // Verify provider access is still valid
            let access = ProviderAccess::<T>::get(&token_data.patient, &token_data.provider)
                .ok_or(Error::<T>::Unauthorized)?;

            ensure!(!access.revoked, Error::<T>::Unauthorized);

            // Check if access expired
            if let Some(expires_at) = access.expires_at {
                ensure!(
                    current_block < expires_at,
                    Error::<T>::Unauthorized
                );
            }

            Ok(())
        }
    }

/// Weight information for extrinsics
pub trait WeightInfo {
    fn register_patient() -> Weight;
    fn register_did() -> Weight;
    fn update_did() -> Weight;
    fn issue_zk_credential() -> Weight;
    fn update_consent() -> Weight;
    fn grant_provider_access() -> Weight;
    fn revoke_provider_access() -> Weight;
    fn emergency_access() -> Weight;
    fn grant_consent() -> Weight;
    fn revoke_consent() -> Weight;
    fn issue_auth_token() -> Weight;
    fn verify_auth_token() -> Weight;
}

/// Patient DID structure
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct PatientDID<T: frame_system::Config> {
    /// Decentralized Identifier string
    pub did: BoundedVec<u8, ConstU32<256>>,
    /// Public keys associated with the DID (quantum-resistant ready - ed25519 for now)
    pub public_keys: BoundedVec<PublicKey, ConstU32<10>>,
    /// Hash of patient metadata (NOT actual PHI data)
    pub metadata_hash: H256,
    /// Block number when DID was created
    pub created_at: frame_system::pallet_prelude::BlockNumberFor<T>,
    /// Block number when DID was last updated
    pub updated_at: frame_system::pallet_prelude::BlockNumberFor<T>,
}

/// DID Document structure (backward compatibility alias)
pub type DIDDocument<T> = PatientDID<T>;

/// Public key structure for DID
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct PublicKey {
    /// Key type (e.g., "Ed25519", "Secp256k1")
    pub key_type: BoundedVec<u8, ConstU32<64>>,
    /// Public key bytes
    pub public_key: BoundedVec<u8, ConstU32<512>>,
    /// Key ID
    pub key_id: BoundedVec<u8, ConstU32<128>>,
}

/// Zero-knowledge proof metadata
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct ZKProofMetadata<T: frame_system::Config> {
    /// Hash of the zero-knowledge proof
    pub proof_hash: sp_core::H256,
    /// Account that issued the credential
    pub issuer: T::AccountId,
    /// Block number when credential was issued
    pub issued_at: frame_system::pallet_prelude::BlockNumberFor<T>,
    /// Block number when credential expires (None = never expires)
    pub expires_at: Option<frame_system::pallet_prelude::BlockNumberFor<T>>,
}

/// Credential types for zero-knowledge proofs
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum CredentialType {
    /// Age verification (over 18, over 21, etc.)
    AgeVerification,
    /// Medical license verification
    MedicalLicense,
    /// Insurance eligibility
    InsuranceEligibility,
    /// Provider credential
    ProviderCredential,
    /// Custom credential type
    Custom(BoundedVec<u8, ConstU32<256>>),
}

/// Consent scope
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum ConsentScope {
    /// Read-only access to health records
    ReadRecords,
    /// Write access to health records
    WriteRecords,
    /// Access to specific record types
    SpecificRecords(BoundedVec<RecordType, ConstU32<50>>),
    /// Full access
    FullAccess,
}

/// Record types
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum RecordType {
    /// Lab results
    LabResults,
    /// Imaging
    Imaging,
    /// Medications
    Medications,
    /// Diagnoses
    Diagnoses,
    /// Vitals
    Vitals,
}

/// Therapeutic modality types
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen, Copy)]
pub enum TherapeuticModality {
    /// Western Medicine
    WesternMedicine,
    /// Traditional Chinese Medicine (TCM)
    TCM,
    /// Ayurveda
    Ayurveda,
    /// Homeopathy
    Homeopathy,
    /// Other therapeutic modality
    Other,
}

/// Consent record per therapeutic modality
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct ConsentRecord<T: frame_system::Config> {
    /// Patient account ID
    pub patient: T::AccountId,
    /// Therapeutic modality
    pub modality: TherapeuticModality,
    /// Whether consent is granted
    pub granted: bool,
    /// Block number when consent was granted/updated
    pub granted_at: frame_system::pallet_prelude::BlockNumberFor<T>,
    /// Block number when consent expires (None = never expires)
    pub expires_at: Option<frame_system::pallet_prelude::BlockNumberFor<T>>,
    /// Whether consent has been revoked
    pub revoked: bool,
}

/// Provider access record
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct ProviderAccessRecord<T: frame_system::Config> {
    /// Patient account ID
    pub patient: T::AccountId,
    /// Provider account ID
    pub provider: T::AccountId,
    /// Scope of access
    pub scope: ConsentScope,
    /// Block number when access was granted
    pub granted_at: frame_system::pallet_prelude::BlockNumberFor<T>,
    /// Block number when access expires (None = never expires)
    pub expires_at: Option<frame_system::pallet_prelude::BlockNumberFor<T>>,
    /// Whether access has been revoked
    pub revoked: bool,
}

/// Authentication token data
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct AuthTokenData<T: frame_system::Config> {
    /// Patient account ID
    pub patient: T::AccountId,
    /// Provider account ID
    pub provider: T::AccountId,
    /// Block number when token was issued
    pub issued_at: BlockNumberFor<T>,
    /// Block number when token expires
    pub expires_at: frame_system::pallet_prelude::BlockNumberFor<T>,
}
}

pub use pallet::*;
