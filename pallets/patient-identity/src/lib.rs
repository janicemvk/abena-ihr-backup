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
        DIDDocument<T>,
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
    /// Maps (patient_id, provider_id) to consent details
    #[pallet::storage]
    #[pallet::getter(fn consent_records)]
    pub type ConsentRecords<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        T::AccountId,
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
        /// Patient DID was registered
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
        /// Consent was granted
        ConsentGranted {
            patient: T::AccountId,
            provider: T::AccountId,
            scope: ConsentScope,
        },
        /// Consent was revoked
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
        /// Register a patient DID
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::register_did())]
        pub fn register_did(
            origin: OriginFor<T>,
            did: Vec<u8>,
            public_keys: Vec<PublicKey>,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            // Validate DID format (basic validation)
            ensure!(did.len() > 0, Error::<T>::InvalidDIDFormat);

            // Convert to BoundedVec (clone did first for event)
            let did_bounded = BoundedVec::try_from(did.clone())
                .map_err(|_| Error::<T>::DataTooLarge)?;
            let public_keys_bounded = BoundedVec::try_from(public_keys)
                .map_err(|_| Error::<T>::DataTooLarge)?;

            let did_doc = DIDDocument {
                did: did_bounded,
                public_keys: public_keys_bounded,
                created_at: <frame_system::Pallet<T>>::block_number(),
                updated_at: <frame_system::Pallet<T>>::block_number(),
            };

            PatientDIDs::<T>::insert(&patient, did_doc);

            Self::deposit_event(Event::DIDRegistered {
                patient,
                did,
            });

            Ok(())
        }

        /// Update patient DID
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::update_did())]
        pub fn update_did(
            origin: OriginFor<T>,
            public_keys: Vec<PublicKey>,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            let mut did_doc = PatientDIDs::<T>::get(&patient)
                .ok_or(Error::<T>::DIDNotFound)?;

            // Convert public_keys to BoundedVec
            let public_keys_bounded = BoundedVec::try_from(public_keys)
                .map_err(|_| Error::<T>::DataTooLarge)?;
            did_doc.public_keys = public_keys_bounded;
            did_doc.updated_at = <frame_system::Pallet<T>>::block_number();

            PatientDIDs::<T>::insert(&patient, did_doc);

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

        /// Grant consent to a provider
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::grant_consent())]
        pub fn grant_consent(
            origin: OriginFor<T>,
            provider: T::AccountId,
            scope: ConsentScope,
            expires_at: Option<BlockNumberFor<T>>,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            let consent = ConsentRecord {
                patient: patient.clone(),
                provider: provider.clone(),
                scope: scope.clone(),
                granted_at: <frame_system::Pallet<T>>::block_number(),
                expires_at,
                revoked: false,
            };

            ConsentRecords::<T>::insert(&patient, &provider, consent);

            Self::deposit_event(Event::ConsentGranted {
                patient,
                provider,
                scope,
            });

            Ok(())
        }

        /// Revoke consent
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::revoke_consent())]
        pub fn revoke_consent(
            origin: OriginFor<T>,
            provider: T::AccountId,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            let mut consent = ConsentRecords::<T>::get(&patient, &provider)
                .ok_or(Error::<T>::ConsentNotFound)?;

            consent.revoked = true;

            ConsentRecords::<T>::insert(&patient, &provider, consent);

            Self::deposit_event(Event::ConsentRevoked {
                patient,
                provider,
            });

            Ok(())
        }

        /// Issue cross-provider authentication token
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::issue_auth_token())]
        pub fn issue_auth_token(
            origin: OriginFor<T>,
            provider: T::AccountId,
            token_hash: H256,
            expires_at: BlockNumberFor<T>,
        ) -> DispatchResult {
            let patient = ensure_signed(origin)?;

            // Verify consent exists
            let consent = ConsentRecords::<T>::get(&patient, &provider)
                .ok_or(Error::<T>::ConsentNotFound)?;

            ensure!(!consent.revoked, Error::<T>::Unauthorized);

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
        #[pallet::call_index(6)]
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

            // Verify consent is still valid
            let consent = ConsentRecords::<T>::get(&token_data.patient, &token_data.provider)
                .ok_or(Error::<T>::Unauthorized)?;

            ensure!(!consent.revoked, Error::<T>::Unauthorized);

            Ok(())
        }
    }

/// Weight information for extrinsics
pub trait WeightInfo {
    fn register_did() -> Weight;
    fn update_did() -> Weight;
    fn issue_zk_credential() -> Weight;
    fn grant_consent() -> Weight;
    fn revoke_consent() -> Weight;
    fn issue_auth_token() -> Weight;
    fn verify_auth_token() -> Weight;
}

/// DID Document structure
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct DIDDocument<T: frame_system::Config> {
    /// Decentralized Identifier string
    pub did: BoundedVec<u8, ConstU32<256>>,
    /// Public keys associated with the DID
    pub public_keys: BoundedVec<PublicKey, ConstU32<10>>,
    /// Block number when DID was created
    pub created_at: frame_system::pallet_prelude::BlockNumberFor<T>,
    /// Block number when DID was last updated
    pub updated_at: frame_system::pallet_prelude::BlockNumberFor<T>,
}

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

/// Consent record
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct ConsentRecord<T: frame_system::Config> {
    /// Patient account ID
    pub patient: T::AccountId,
    /// Provider account ID
    pub provider: T::AccountId,
    /// Scope of consent
    pub scope: ConsentScope,
    /// Block number when consent was granted
    pub granted_at: frame_system::pallet_prelude::BlockNumberFor<T>,
    /// Block number when consent expires (None = never expires)
    pub expires_at: Option<frame_system::pallet_prelude::BlockNumberFor<T>>,
    /// Whether consent has been revoked
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
