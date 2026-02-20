//! # Treatment Protocol Pallet
//!
//! A pallet for managing treatment protocols as smart contracts,
//! with automated compliance checking and cross-modality coordination.

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
    use sp_runtime::RuntimeDebug;    /// Configuration trait for the pallet.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Treatment protocols
    /// Maps (patient_id, protocol_id) to treatment protocol
    #[pallet::storage]
    #[pallet::getter(fn treatment_protocols)]
    pub type TreatmentProtocols<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        ProtocolId,
        TreatmentProtocol<T>,
        OptionQuery,
    >;

    /// Clinical guidelines registry
    /// Maps guideline_id to guideline definition
    #[pallet::storage]
    pub type ClinicalGuidelines<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        GuidelineId,
        ClinicalGuideline<T>,
        OptionQuery,
    >;

    /// Contraindication checks
    /// Maps (patient_id, protocol_id) to contraindication status
    #[pallet::storage]
    pub type Contraindications<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        ProtocolId,
        ContraindicationStatus,
        OptionQuery,
    >;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Treatment protocol was created
        ProtocolCreated {
            patient: T::AccountId,
            protocol_id: ProtocolId,
            provider: T::AccountId,
        },
        /// Protocol compliance was validated
        ProtocolValidated {
            patient: T::AccountId,
            protocol_id: ProtocolId,
            compliant: bool,
        },
        /// Contraindication was detected
        ContraindicationDetected {
            patient: T::AccountId,
            protocol_id: ProtocolId,
            contraindication: Vec<u8>,
        },
        /// Treatment protocol was updated
        ProtocolUpdated {
            patient: T::AccountId,
            protocol_id: ProtocolId,
        },
    }

    /// Errors that can occur in this pallet
    #[pallet::error]
    pub enum Error<T> {
        /// Protocol not found
        ProtocolNotFound,
        /// Protocol validation failed
        ValidationFailed,
        /// Contraindication detected
        ContraindicationDetected,
        /// Guideline not found
        GuidelineNotFound,
        /// Too many treatments (exceeds BoundedVec limit)
        TooManyTreatments,
    }

    /// Hooks for the pallet
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    /// Extrinsics for the pallet
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a treatment protocol
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::create_protocol())]
        pub fn create_protocol(
            origin: OriginFor<T>,
            patient: T::AccountId,
            protocol_id: ProtocolId,
            treatments: Vec<Treatment>,
            guideline_id: Option<GuidelineId>,
        ) -> DispatchResult {
            let provider = ensure_signed(origin)?;

            // Validate against clinical guidelines if provided
            if let Some(gid) = guideline_id {
                ClinicalGuidelines::<T>::get(&gid)
                    .ok_or(Error::<T>::GuidelineNotFound)?;
            }

            // Convert treatments to BoundedVec
            let treatments_bounded = BoundedVec::try_from(treatments)
                .map_err(|_| Error::<T>::TooManyTreatments)?;

            let protocol = TreatmentProtocol {
                patient: patient.clone(),
                protocol_id,
                provider: provider.clone(),
                treatments: treatments_bounded,
                guideline_id,
                created_at: <frame_system::Pallet<T>>::block_number(),
                status: ProtocolStatus::Active,
            };

            TreatmentProtocols::<T>::insert(&patient, &protocol_id, protocol);

            Self::deposit_event(Event::ProtocolCreated {
                patient,
                protocol_id,
                provider,
            });

            Ok(())
        }

        /// Validate protocol compliance
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::validate_protocol())]
        pub fn validate_protocol(
            origin: OriginFor<T>,
            patient: T::AccountId,
            protocol_id: ProtocolId,
        ) -> DispatchResult {
            let _validator = ensure_signed(origin)?;

            let protocol = TreatmentProtocols::<T>::get(&patient, &protocol_id)
                .ok_or(Error::<T>::ProtocolNotFound)?;

            // Check compliance (simplified - in production, implement full validation)
            let compliant = Self::check_compliance(&protocol);

            // Check for contraindications
            let contraindication_status = Self::check_contraindications(&patient, &protocol);
            
            if contraindication_status.has_contraindications {
                Contraindications::<T>::insert(&patient, &protocol_id, contraindication_status.clone());
                
                Self::deposit_event(Event::ContraindicationDetected {
                    patient: patient.clone(),
                    protocol_id,
                    contraindication: contraindication_status.reasons.to_vec(),
                });
                
                return Err(Error::<T>::ContraindicationDetected.into());
            }

            Self::deposit_event(Event::ProtocolValidated {
                patient,
                protocol_id,
                compliant,
            });

            Ok(())
        }

        /// Update treatment protocol
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::update_protocol())]
        pub fn update_protocol(
            origin: OriginFor<T>,
            patient: T::AccountId,
            protocol_id: ProtocolId,
            treatments: Vec<Treatment>,
        ) -> DispatchResult {
            let provider = ensure_signed(origin)?;

            let mut protocol = TreatmentProtocols::<T>::get(&patient, &protocol_id)
                .ok_or(Error::<T>::ProtocolNotFound)?;

            // Convert treatments to BoundedVec
            let treatments_bounded = BoundedVec::try_from(treatments)
                .map_err(|_| Error::<T>::TooManyTreatments)?;
            protocol.treatments = treatments_bounded;
            protocol.status = ProtocolStatus::Updated;

            TreatmentProtocols::<T>::insert(&patient, &protocol_id, protocol);

            Self::deposit_event(Event::ProtocolUpdated {
                patient,
                protocol_id,
            });

            Ok(())
        }

        /// Register a clinical guideline
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::register_guideline())]
        pub fn register_guideline(
            origin: OriginFor<T>,
            guideline_id: GuidelineId,
            guideline: ClinicalGuideline<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;

            ClinicalGuidelines::<T>::insert(&guideline_id, guideline);

            Ok(())
        }
    }


/// Helper functions
    impl<T: Config> Pallet<T> {
        /// Check protocol compliance
        fn check_compliance(protocol: &TreatmentProtocol<T>) -> bool {
            // Simplified compliance check
            // In production, implement full guideline validation
            !protocol.treatments.is_empty()
        }

        /// Check for contraindications
        fn check_contraindications(
            patient: &T::AccountId,
            protocol: &TreatmentProtocol<T>,
        ) -> ContraindicationStatus {
            // Simplified contraindication check
            // In production, cross-reference with patient allergies, medications, conditions
            ContraindicationStatus {
                has_contraindications: false,
                reasons: BoundedVec::default(),
            }
        }

/// Weight information for extrinsics
pub trait WeightInfo {
    fn create_protocol() -> Weight;
    fn validate_protocol() -> Weight;
    fn update_protocol() -> Weight;
    fn register_guideline() -> Weight;
}

/// Protocol ID type
pub type ProtocolId = u64;

/// Guideline ID type
pub type GuidelineId = u32;

/// Treatment protocol
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct TreatmentProtocol<T: frame_system::Config> {
    /// Patient account ID
    pub patient: T::AccountId,
    /// Protocol identifier
    pub protocol_id: ProtocolId,
    /// Provider who created the protocol
    pub provider: T::AccountId,
    /// List of treatments
    pub treatments: BoundedVec<Treatment, ConstU32<100>>,
    /// Clinical guideline ID (if applicable)
    pub guideline_id: Option<GuidelineId>,
    /// Block number when protocol was created
    pub created_at: BlockNumberFor<T>,
    /// Current status
    pub status: ProtocolStatus,
}

/// Treatment definition
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct Treatment {
    /// Treatment type
    pub treatment_type: TreatmentType,
    /// Treatment details (encoded)
    pub details: BoundedVec<u8, ConstU32<4096>>,
    /// Modality (Western, TCM, Ayurveda, etc.)
    pub modality: Modality,
    /// Dosage/frequency information
    pub dosage: BoundedVec<u8, ConstU32<512>>,
}

/// Treatment type
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum TreatmentType {
    /// Medication
    Medication,
    /// Procedure
    Procedure,
    /// Therapy
    Therapy,
    /// Lifestyle modification
    Lifestyle,
    /// Other
    Other(BoundedVec<u8, ConstU32<256>>),
}

/// Treatment modality
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum Modality {
    /// Western medicine
    Western,
    /// Traditional Chinese Medicine
    TCM,
    /// Ayurveda
    Ayurveda,
    /// Integrative
    Integrative,
    /// Other
    Other(BoundedVec<u8, ConstU32<256>>),
}

/// Protocol status
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum ProtocolStatus {
    /// Protocol is active
    Active,
    /// Protocol was updated
    Updated,
    /// Protocol is completed
    Completed,
    /// Protocol was cancelled
    Cancelled,
}

/// Clinical guideline
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct ClinicalGuideline<T: frame_system::Config> {
    /// Guideline name
    pub name: BoundedVec<u8, ConstU32<256>>,
    /// Guideline version
    pub version: BoundedVec<u8, ConstU32<64>>,
    /// Guideline content (encoded)
    pub content: BoundedVec<u8, ConstU32<8192>>,
    /// Block number when guideline was registered
    pub registered_at: BlockNumberFor<T>,
}

/// Contraindication status
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct ContraindicationStatus {
    /// Whether contraindications were detected
    pub has_contraindications: bool,
    /// Reasons for contraindications
    pub reasons: BoundedVec<u8, ConstU32<1024>>,
}
}

pub use pallet::*;
