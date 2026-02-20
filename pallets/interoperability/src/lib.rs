//! # Interoperability Pallet
//!
//! A pallet for HL7 FHIR data bridges, cross-chain health data exchange,
//! insurance claim verification, and pharmacy/lab integrations.

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
    use codec::MaxEncodedLen;
    use sp_runtime::BoundedVec;    /// Configuration trait for the pallet.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// FHIR resource mappings
    /// Maps (patient_id, resource_type) to FHIR resource hash
    #[pallet::storage]
    pub type FHIRResources<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        FHIRResourceType,
        FHIRResourceMapping<T>,
        OptionQuery,
    >;

    /// Cross-chain data exchange records
    #[pallet::storage]
    pub type CrossChainExchanges<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        ExchangeId,
        CrossChainExchange<T>,
        OptionQuery,
    >;

    /// Insurance claim verifications
    #[pallet::storage]
    pub type InsuranceClaims<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        ClaimId,
        InsuranceClaim<T>,
        OptionQuery,
    >;

    /// Pharmacy integrations
    #[pallet::storage]
    pub type PharmacyIntegrations<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        PharmacyId,
        PharmacyIntegration<T>,
        OptionQuery,
    >;

    /// Lab integrations
    #[pallet::storage]
    pub type LabIntegrations<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        LabId,
        LabIntegration<T>,
        OptionQuery,
    >;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// FHIR resource was mapped
        FHIRResourceMapped {
            patient: T::AccountId,
            resource_type: FHIRResourceType,
            resource_hash: H256,
        },
        /// Cross-chain exchange initiated
        CrossChainExchangeInitiated {
            exchange_id: ExchangeId,
            source_chain: Vec<u8>,
            target_chain: Vec<u8>,
        },
        /// Insurance claim verified
        InsuranceClaimVerified {
            claim_id: ClaimId,
            patient: T::AccountId,
            verified: bool,
        },
        /// Pharmacy integration registered
        PharmacyIntegrationRegistered {
            pharmacy_id: PharmacyId,
            pharmacy_name: Vec<u8>,
        },
        /// Lab integration registered
        LabIntegrationRegistered {
            lab_id: LabId,
            lab_name: Vec<u8>,
        },
    }

    /// Errors that can occur in this pallet
    #[pallet::error]
    pub enum Error<T> {
        /// Resource not found
        ResourceNotFound,
        /// Invalid FHIR format
        InvalidFHIRFormat,
        /// Exchange not found
        ExchangeNotFound,
        /// Claim not found
        ClaimNotFound,
        /// Data too large for bounded vector
        DataTooLarge,
    }

    /// Hooks for the pallet
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    /// Extrinsics for the pallet
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Map FHIR resource to blockchain
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::map_fhir_resource())]
        pub fn map_fhir_resource(
            origin: OriginFor<T>,
            patient: T::AccountId,
            resource_type: FHIRResourceType,
            fhir_resource_hash: H256,
            blockchain_record_id: Vec<u8>,
        ) -> DispatchResult {
            let _mapper = ensure_signed(origin)?;

            // Convert blockchain_record_id to BoundedVec
            let blockchain_record_id_bounded = BoundedVec::try_from(blockchain_record_id)
                .map_err(|_| Error::<T>::DataTooLarge)?;

            let mapping = FHIRResourceMapping {
                fhir_resource_hash,
                blockchain_record_id: blockchain_record_id_bounded,
                mapped_at: <frame_system::Pallet<T>>::block_number(),
            };

            FHIRResources::<T>::insert(&patient, &resource_type, mapping);

            Self::deposit_event(Event::FHIRResourceMapped {
                patient,
                resource_type,
                resource_hash: fhir_resource_hash,
            });

            Ok(())
        }

        /// Initiate cross-chain data exchange
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::initiate_cross_chain_exchange())]
        pub fn initiate_cross_chain_exchange(
            origin: OriginFor<T>,
            exchange_id: ExchangeId,
            source_chain: Vec<u8>,
            target_chain: Vec<u8>,
            data_hash: H256,
        ) -> DispatchResult {
            let _initiator = ensure_signed(origin)?;

            // Convert chains to BoundedVec (clone first for event)
            let source_chain_bounded = BoundedVec::try_from(source_chain.clone())
                .map_err(|_| Error::<T>::DataTooLarge)?;
            let target_chain_bounded = BoundedVec::try_from(target_chain.clone())
                .map_err(|_| Error::<T>::DataTooLarge)?;

            let exchange = CrossChainExchange {
                exchange_id,
                source_chain: source_chain_bounded,
                target_chain: target_chain_bounded,
                data_hash,
                initiated_at: <frame_system::Pallet<T>>::block_number(),
                status: ExchangeStatus::Pending,
            };

            CrossChainExchanges::<T>::insert(&exchange_id, exchange);

            Self::deposit_event(Event::CrossChainExchangeInitiated {
                exchange_id,
                source_chain,
                target_chain,
            });

            Ok(())
        }

        /// Verify insurance claim
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::verify_insurance_claim())]
        pub fn verify_insurance_claim(
            origin: OriginFor<T>,
            claim_id: ClaimId,
            patient: T::AccountId,
            claim_data_hash: H256,
        ) -> DispatchResult {
            let verifier = ensure_signed(origin)?;

            // Simplified verification (in production, implement full claim validation)
            let verified = true;

            let claim = InsuranceClaim {
                claim_id,
                patient: patient.clone(),
                claim_data_hash,
                verified,
                verified_at: <frame_system::Pallet<T>>::block_number(),
                verifier: verifier.clone(),
            };

            InsuranceClaims::<T>::insert(&claim_id, claim);

            Self::deposit_event(Event::InsuranceClaimVerified {
                claim_id,
                patient,
                verified,
            });

            Ok(())
        }

        /// Register pharmacy integration
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::register_pharmacy())]
        pub fn register_pharmacy(
            origin: OriginFor<T>,
            pharmacy_id: PharmacyId,
            pharmacy_name: Vec<u8>,
            endpoint: Vec<u8>,
        ) -> DispatchResult {
            let _registrar = ensure_signed(origin)?;

            // Convert to BoundedVec
            let pharmacy_name_bounded = BoundedVec::try_from(pharmacy_name)
                .map_err(|_| Error::<T>::DataTooLarge)?;
            let endpoint_bounded = BoundedVec::try_from(endpoint)
                .map_err(|_| Error::<T>::DataTooLarge)?;

            let integration = PharmacyIntegration {
                pharmacy_id,
                pharmacy_name: pharmacy_name_bounded,
                endpoint: endpoint_bounded,
                registered_at: <frame_system::Pallet<T>>::block_number(),
                active: true,
            };

            PharmacyIntegrations::<T>::insert(&pharmacy_id, integration);

            Self::deposit_event(Event::PharmacyIntegrationRegistered {
                pharmacy_id,
                pharmacy_name: pharmacy_name_bounded.clone().into(),
            });

            Ok(())
        }

        /// Register lab integration
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::register_lab())]
        pub fn register_lab(
            origin: OriginFor<T>,
            lab_id: LabId,
            lab_name: Vec<u8>,
            endpoint: Vec<u8>,
        ) -> DispatchResult {
            let _registrar = ensure_signed(origin)?;

            // Convert to BoundedVec
            let lab_name_bounded = BoundedVec::try_from(lab_name)
                .map_err(|_| Error::<T>::DataTooLarge)?;
            let endpoint_bounded = BoundedVec::try_from(endpoint)
                .map_err(|_| Error::<T>::DataTooLarge)?;

            let integration = LabIntegration {
                lab_id,
                lab_name: lab_name_bounded,
                endpoint: endpoint_bounded,
                registered_at: <frame_system::Pallet<T>>::block_number(),
                active: true,
            };

            LabIntegrations::<T>::insert(&lab_id, integration);

            Self::deposit_event(Event::LabIntegrationRegistered {
                lab_id,
                lab_name: lab_name_bounded.clone().into(),
            });

            Ok(())
        }
    }

/// Weight information for extrinsics
pub trait WeightInfo {
    fn map_fhir_resource() -> Weight;
    fn initiate_cross_chain_exchange() -> Weight;
    fn verify_insurance_claim() -> Weight;
    fn register_pharmacy() -> Weight;
    fn register_lab() -> Weight;
}

/// Exchange ID type
pub type ExchangeId = u64;

/// Claim ID type
pub type ClaimId = u64;

/// Pharmacy ID type
pub type PharmacyId = u32;

/// Lab ID type
pub type LabId = u32;

/// FHIR resource type
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum FHIRResourceType {
    /// Patient resource
    Patient,
    /// Observation resource
    Observation,
    /// Medication resource
    Medication,
    /// Condition resource
    Condition,
    /// Procedure resource
    Procedure,
    /// Other resource type
    Other(BoundedVec<u8, ConstU32<256>>),
}

/// FHIR resource mapping
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct FHIRResourceMapping<T: frame_system::Config> {
    /// Hash of the FHIR resource
    pub fhir_resource_hash: sp_core::H256,
    /// Blockchain record ID
    pub blockchain_record_id: BoundedVec<u8, ConstU32<256>>,
    /// Block number when mapped
    pub mapped_at: BlockNumberFor<T>,
}

/// Cross-chain exchange
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct CrossChainExchange<T: frame_system::Config> {
    /// Exchange identifier
    pub exchange_id: ExchangeId,
    /// Source chain identifier
    pub source_chain: BoundedVec<u8, ConstU32<64>>,
    /// Target chain identifier
    pub target_chain: BoundedVec<u8, ConstU32<64>>,
    /// Hash of data being exchanged
    pub data_hash: sp_core::H256,
    /// Block number when exchange was initiated
    pub initiated_at: BlockNumberFor<T>,
    /// Exchange status
    pub status: ExchangeStatus,
}

/// Exchange status
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum ExchangeStatus {
    /// Exchange is pending
    Pending,
    /// Exchange is completed
    Completed,
    /// Exchange failed
    Failed,
}

/// Insurance claim
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct InsuranceClaim<T: frame_system::Config> {
    /// Claim identifier
    pub claim_id: ClaimId,
    /// Patient account ID
    pub patient: T::AccountId,
    /// Hash of claim data
    pub claim_data_hash: sp_core::H256,
    /// Whether claim was verified
    pub verified: bool,
    /// Block number when verified
    pub verified_at: BlockNumberFor<T>,
    /// Account that verified the claim
    pub verifier: T::AccountId,
}

/// Pharmacy integration
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct PharmacyIntegration<T: frame_system::Config> {
    /// Pharmacy identifier
    pub pharmacy_id: PharmacyId,
    /// Pharmacy name
    pub pharmacy_name: BoundedVec<u8, ConstU32<128>>,
    /// Integration endpoint
    pub endpoint: BoundedVec<u8, ConstU32<256>>,
    /// Block number when registered
    pub registered_at: BlockNumberFor<T>,
    /// Whether integration is active
    pub active: bool,
}

/// Lab integration
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct LabIntegration<T: frame_system::Config> {
    /// Lab identifier
    pub lab_id: LabId,
    /// Lab name
    pub lab_name: BoundedVec<u8, ConstU32<128>>,
    /// Integration endpoint
    pub endpoint: BoundedVec<u8, ConstU32<256>>,
    /// Block number when registered
    pub registered_at: BlockNumberFor<T>,
    /// Whether integration is active
    pub active: bool,
}
}

pub use pallet::*;
