//! # ABENA Treatment Protocol Pallet
//!
//! Encodes evidence-based treatment protocols as on-chain smart contracts:
//! treatment plan adherence, cross-modality safety (drug/herb interactions),
//! automated compliance checking, immutable audit trails, and clinical trial support.
//! Multi-modality (Western + TCM + Ayurveda + Integrative), step-by-step progression,
//! milestone tracking, and adverse event reporting.

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Encode, Decode, DecodeWithMemTracking, MaxEncodedLen};
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
    use codec::{Encode, Decode, DecodeWithMemTracking, MaxEncodedLen};
    use sp_runtime::RuntimeDebug;

    /// Configuration trait for the pallet.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
    }

    // ---------- Spec types: protocol definitions & steps ----------

    /// Clinical condition (e.g. diabetes, hypertension).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct ClinicalCondition {
        pub code: BoundedVec<u8, ConstU32<32>>,
        pub description: BoundedVec<u8, ConstU32<128>>,
    }

    /// Therapeutic modality.
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum TherapeuticModality {
        Western,
        TCM,
        Ayurveda,
        Integrative,
        Other,
    }

    /// Evidence level for protocol (highest to lowest).
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum EvidenceLevel {
        SystematicReview,
        RandomizedControlled,
        CohortStudy,
        CaseControl,
        ExpertOpinion,
        TraditionalKnowledge,
    }

    /// Success criteria (bounded).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct SuccessCriteria {
        pub description: BoundedVec<u8, ConstU32<256>>,
        pub measurable: bool,
    }

    /// Intervention type per step.
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum InterventionType {
        Pharmaceutical,
        Botanical,
        Acupuncture,
        Dietary,
        Lifestyle,
        Surgical,
        Monitoring,
    }

    /// Medication (name, dosage reference).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct Medication {
        pub name: BoundedVec<u8, ConstU32<128>>,
        pub dosage_ref: BoundedVec<u8, ConstU32<64>>,
    }

    /// Herb formula reference.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct HerbFormula {
        pub name: BoundedVec<u8, ConstU32<128>>,
        pub components_ref: BoundedVec<u8, ConstU32<256>>,
    }

    /// Procedure reference.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct Procedure {
        pub code: BoundedVec<u8, ConstU32<32>>,
        pub description: BoundedVec<u8, ConstU32<128>>,
    }

    /// Frequency (e.g. daily, twice weekly).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct Frequency {
        pub times_per_day: u8,
        pub days_per_week: u8,
    }

    /// Prerequisite (e.g. complete step N).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct Prerequisite {
        pub step_number: u32,
        pub condition_met: bool,
    }

    /// Milestone check for step success.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct MilestoneCheck {
        pub metric: BoundedVec<u8, ConstU32<64>>,
        pub target_value: BoundedVec<u8, ConstU32<64>>,
    }

    /// Next-step condition (branch).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct StepCondition {
        pub condition_type: BoundedVec<u8, ConstU32<32>>,
        pub next_step: u32,
    }

    /// Single treatment step in a protocol.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct TreatmentStep {
        pub step_number: u32,
        pub intervention_type: InterventionType,
        pub medication: Option<Medication>,
        pub herb_formula: Option<HerbFormula>,
        pub procedure: Option<Procedure>,
        pub duration_days: u32,
        pub frequency: Frequency,
        pub prerequisites: BoundedVec<Prerequisite, ConstU32<8>>,
        pub success_criteria: Option<MilestoneCheck>,
        pub next_step_conditions: BoundedVec<StepCondition, ConstU32<8>>,
    }

    /// Protocol definition (evidence-based, multi-modality).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct ProtocolDefinition<T: Config> {
        pub protocol_id: T::Hash,
        pub name: BoundedVec<u8, ConstU32<128>>,
        pub condition: ClinicalCondition,
        pub modalities: BoundedVec<TherapeuticModality, ConstU32<8>>,
        pub evidence_level: EvidenceLevel,
        pub duration_days: u32,
        pub success_criteria: SuccessCriteria,
        pub created_by: T::AccountId,
        pub validated_by: BoundedVec<T::AccountId, ConstU32<16>>,
        pub active: bool,
    }

    /// Interaction severity.
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum InteractionSeverity {
        Contraindicated,
        Major,
        Moderate,
        Minor,
    }

    /// Interaction rule (drug-drug, herb-drug).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub struct InteractionRule {
        pub rule_id: u32,
        pub substance_a: BoundedVec<u8, ConstU32<128>>,
        pub substance_b: BoundedVec<u8, ConstU32<128>>,
        pub severity: InteractionSeverity,
        pub mechanism: BoundedVec<u8, ConstU32<256>>,
        pub recommendation: BoundedVec<u8, ConstU32<256>>,
    }

    /// Active treatment execution state.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct TreatmentExecution<T: Config> {
        pub patient: T::AccountId,
        pub protocol_id: T::Hash,
        pub current_step: u32,
        pub started_at: BlockNumberFor<T>,
        pub completed_steps: BoundedVec<u32, ConstU32<64>>,
        pub adherence_log: BoundedVec<(u32, BlockNumberFor<T>), ConstU32<128>>,
        pub status: TreatmentExecutionStatus,
        pub outcome: Option<Outcome<T>>,
    }

    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum TreatmentExecutionStatus {
        Active,
        Completed,
        Modified,
        Cancelled,
    }

    /// Outcome record.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct Outcome<T: Config> {
        pub success: bool,
        pub description: BoundedVec<u8, ConstU32<512>>,
        pub recorded_at: BlockNumberFor<T>,
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

    // ---------- Spec storage ----------

    /// Protocol registry: protocol_id (T::Hash) -> ProtocolDefinition.
    #[pallet::storage]
    #[pallet::getter(fn protocol_registry)]
    pub type ProtocolRegistry<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        ProtocolDefinition<T>,
        OptionQuery,
    >;

    /// Protocol steps: protocol_id -> steps.
    #[pallet::storage]
    #[pallet::getter(fn protocol_steps)]
    pub type ProtocolSteps<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::Hash,
        BoundedVec<TreatmentStep, ConstU32<64>>,
        OptionQuery,
    >;

    /// Active treatments: (patient, protocol_id) -> TreatmentExecution.
    #[pallet::storage]
    #[pallet::getter(fn active_treatment)]
    pub type ActiveTreatments<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        T::Hash,
        TreatmentExecution<T>,
        OptionQuery,
    >;

    /// Interaction database: rule_id -> InteractionRule.
    #[pallet::storage]
    #[pallet::getter(fn interaction_rule)]
    pub type InteractionDatabase<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u32,
        InteractionRule,
        OptionQuery,
    >;

    /// Next interaction rule ID.
    #[pallet::storage]
    #[pallet::getter(fn next_interaction_rule_id)]
    pub type NextInteractionRuleId<T: Config> = StorageValue<_, u32, ValueQuery>;

    /// Outcome tracking: (patient, protocol_id) -> Outcome (final).
    #[pallet::storage]
    #[pallet::getter(fn outcome_tracking)]
    pub type OutcomeTracking<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        T::Hash,
        Outcome<T>,
        OptionQuery,
    >;

    /// Adverse events: (patient, protocol_id) -> list of event descriptions.
    #[pallet::storage]
    pub type AdverseEvents<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        T::Hash,
        BoundedVec<BoundedVec<u8, ConstU32<256>>, ConstU32<32>>,
        ValueQuery,
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
        /// Protocol registered (spec)
        ProtocolRegistered {
            protocol_id: T::Hash,
            name: BoundedVec<u8, ConstU32<128>>,
            evidence_level: EvidenceLevel,
        },
        /// Protocol validated by medical board
        ProtocolValidatedSpec {
            protocol_id: T::Hash,
            validator: T::AccountId,
        },
        /// Treatment initiated
        TreatmentInitiated {
            patient: T::AccountId,
            protocol_id: T::Hash,
            started_at: BlockNumberFor<T>,
        },
        /// Step completion recorded
        StepCompletionRecorded {
            patient: T::AccountId,
            protocol_id: T::Hash,
            step_number: u32,
        },
        /// Milestone evaluated
        MilestoneEvaluated {
            patient: T::AccountId,
            protocol_id: T::Hash,
            step_number: u32,
            met: bool,
        },
        /// Protocol modified (adaptive)
        ProtocolModified {
            patient: T::AccountId,
            protocol_id: T::Hash,
            modifier: T::AccountId,
        },
        /// Treatment completed
        TreatmentCompleted {
            patient: T::AccountId,
            protocol_id: T::Hash,
            success: bool,
        },
        /// Adverse event reported
        AdverseEventReported {
            patient: T::AccountId,
            protocol_id: T::Hash,
            reporter: T::AccountId,
        },
        /// Interaction rule added
        InteractionRuleAdded {
            rule_id: u32,
            severity: InteractionSeverity,
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
        /// Protocol already exists
        ProtocolAlreadyExists,
        /// Step not found or invalid order
        InvalidStep,
        /// Treatment not active
        TreatmentNotActive,
        /// Unauthorized (not creator or validator)
        Unauthorized,
        /// Interaction check failed (contraindication or major)
        InteractionCheckFailed,
        /// Outcome already recorded
        OutcomeAlreadyRecorded,
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
            let contraindication_status = Self::check_protocol_contraindications(&patient, &protocol);
            
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

        // ---------- Spec dispatchables ----------

        /// Register a new treatment protocol (evidence-based definition).
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::register_protocol())]
        pub fn register_protocol(
            origin: OriginFor<T>,
            protocol_id: T::Hash,
            name: BoundedVec<u8, ConstU32<128>>,
            condition: ClinicalCondition,
            modalities: BoundedVec<TherapeuticModality, ConstU32<8>>,
            evidence_level: EvidenceLevel,
            duration_days: u32,
            success_criteria: SuccessCriteria,
            steps: BoundedVec<TreatmentStep, ConstU32<64>>,
        ) -> DispatchResult {
            let created_by = ensure_signed(origin)?;

            ensure!(ProtocolRegistry::<T>::get(&protocol_id).is_none(), Error::<T>::ProtocolAlreadyExists);

            let def = ProtocolDefinition::<T> {
                protocol_id,
                name: name.clone(),
                condition,
                modalities,
                evidence_level,
                duration_days,
                success_criteria,
                created_by: created_by.clone(),
                validated_by: BoundedVec::default(),
                active: true,
            };
            ProtocolRegistry::<T>::insert(&protocol_id, &def);
            ProtocolSteps::<T>::insert(&protocol_id, &steps);

            Self::deposit_event(Event::ProtocolRegistered {
                protocol_id,
                name,
                evidence_level,
            });
            Ok(())
        }

        /// Validate protocol (medical board approval).
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::validate_protocol_spec())]
        pub fn validate_protocol_spec(
            origin: OriginFor<T>,
            protocol_id: T::Hash,
        ) -> DispatchResult {
            let validator = ensure_signed(origin)?;

            let mut def = ProtocolRegistry::<T>::get(&protocol_id).ok_or(Error::<T>::ProtocolNotFound)?;
            def.validated_by.try_push(validator.clone()).map_err(|_| Error::<T>::TooManyTreatments)?;
            ProtocolRegistry::<T>::insert(&protocol_id, &def);

            Self::deposit_event(Event::ProtocolValidatedSpec {
                protocol_id,
                validator,
            });
            Ok(())
        }

        /// Initiate treatment (start patient on protocol).
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::initiate_treatment())]
        pub fn initiate_treatment(
            origin: OriginFor<T>,
            patient: T::AccountId,
            protocol_id: T::Hash,
        ) -> DispatchResult {
            let _provider = ensure_signed(origin)?;

            let def = ProtocolRegistry::<T>::get(&protocol_id).ok_or(Error::<T>::ProtocolNotFound)?;
            ensure!(def.active, Error::<T>::ValidationFailed);
            ensure!(ActiveTreatments::<T>::get(&patient, &protocol_id).is_none(), Error::<T>::ProtocolAlreadyExists);

            let now = <frame_system::Pallet<T>>::block_number();
            let exec = TreatmentExecution::<T> {
                patient: patient.clone(),
                protocol_id,
                current_step: 1,
                started_at: now,
                completed_steps: BoundedVec::default(),
                adherence_log: BoundedVec::default(),
                status: TreatmentExecutionStatus::Active,
                outcome: None,
            };
            ActiveTreatments::<T>::insert(&patient, &protocol_id, &exec);

            Self::deposit_event(Event::TreatmentInitiated {
                patient,
                protocol_id,
                started_at: now,
            });
            Ok(())
        }

        /// Record step completion (adherence).
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::record_step_completion())]
        pub fn record_step_completion(
            origin: OriginFor<T>,
            patient: T::AccountId,
            protocol_id: T::Hash,
            step_number: u32,
        ) -> DispatchResult {
            let _recorder = ensure_signed(origin)?;

            let mut exec = ActiveTreatments::<T>::get(&patient, &protocol_id).ok_or(Error::<T>::ProtocolNotFound)?;
            ensure!(exec.status == TreatmentExecutionStatus::Active, Error::<T>::TreatmentNotActive);

            let steps = ProtocolSteps::<T>::get(&protocol_id).ok_or(Error::<T>::ProtocolNotFound)?;
            let step_exists = steps.iter().any(|s| s.step_number == step_number);
            ensure!(step_exists, Error::<T>::InvalidStep);
            ensure!(step_number == exec.current_step, Error::<T>::InvalidStep);

            let now = <frame_system::Pallet<T>>::block_number();
            exec.completed_steps.try_push(step_number).map_err(|_| Error::<T>::TooManyTreatments)?;
            exec.adherence_log.try_push((step_number, now)).map_err(|_| Error::<T>::TooManyTreatments)?;
            exec.current_step = step_number.saturating_add(1);
            ActiveTreatments::<T>::insert(&patient, &protocol_id, &exec);

            Self::deposit_event(Event::StepCompletionRecorded {
                patient,
                protocol_id,
                step_number,
            });
            Ok(())
        }

        /// Check contraindications (safety). Returns Ok if safe; Err if contraindicated/major.
        #[pallet::call_index(8)]
        #[pallet::weight(T::WeightInfo::check_contraindications())]
        pub fn check_contraindications(
            origin: OriginFor<T>,
            substance_a: BoundedVec<u8, ConstU32<128>>,
            substance_b: BoundedVec<u8, ConstU32<128>>,
        ) -> DispatchResult {
            let _caller = ensure_signed(origin)?;

            for (_, rule) in InteractionDatabase::<T>::iter() {
                let match_a = (rule.substance_a == substance_a && rule.substance_b == substance_b)
                    || (rule.substance_a == substance_b && rule.substance_b == substance_a);
                if match_a && (rule.severity == InteractionSeverity::Contraindicated || rule.severity == InteractionSeverity::Major) {
                    return Err(Error::<T>::InteractionCheckFailed.into());
                }
            }
            Ok(())
        }

        /// Evaluate milestone (step success criteria).
        #[pallet::call_index(9)]
        #[pallet::weight(T::WeightInfo::evaluate_milestone())]
        pub fn evaluate_milestone(
            origin: OriginFor<T>,
            patient: T::AccountId,
            protocol_id: T::Hash,
            step_number: u32,
            met: bool,
        ) -> DispatchResult {
            let _evaluator = ensure_signed(origin)?;

            let _exec = ActiveTreatments::<T>::get(&patient, &protocol_id).ok_or(Error::<T>::ProtocolNotFound)?;

            Self::deposit_event(Event::MilestoneEvaluated {
                patient,
                protocol_id,
                step_number,
                met,
            });
            Ok(())
        }

        /// Modify protocol (adaptive change).
        #[pallet::call_index(10)]
        #[pallet::weight(T::WeightInfo::modify_protocol())]
        pub fn modify_protocol(
            origin: OriginFor<T>,
            patient: T::AccountId,
            protocol_id: T::Hash,
            new_current_step: u32,
        ) -> DispatchResult {
            let modifier = ensure_signed(origin)?;

            let mut exec = ActiveTreatments::<T>::get(&patient, &protocol_id).ok_or(Error::<T>::ProtocolNotFound)?;
            ensure!(exec.status == TreatmentExecutionStatus::Active, Error::<T>::TreatmentNotActive);

            exec.current_step = new_current_step;
            exec.status = TreatmentExecutionStatus::Active;
            ActiveTreatments::<T>::insert(&patient, &protocol_id, &exec);

            Self::deposit_event(Event::ProtocolModified {
                patient,
                protocol_id,
                modifier,
            });
            Ok(())
        }

        /// Complete treatment (record outcome).
        #[pallet::call_index(11)]
        #[pallet::weight(T::WeightInfo::complete_treatment())]
        pub fn complete_treatment(
            origin: OriginFor<T>,
            patient: T::AccountId,
            protocol_id: T::Hash,
            success: bool,
            description: BoundedVec<u8, ConstU32<512>>,
        ) -> DispatchResult {
            let _completer = ensure_signed(origin)?;

            let mut exec = ActiveTreatments::<T>::get(&patient, &protocol_id).ok_or(Error::<T>::ProtocolNotFound)?;
            ensure!(exec.outcome.is_none(), Error::<T>::OutcomeAlreadyRecorded);

            let now = <frame_system::Pallet<T>>::block_number();
            let outcome = Outcome::<T> {
                success,
                description: description.clone(),
                recorded_at: now,
            };
            exec.outcome = Some(outcome.clone());
            exec.status = TreatmentExecutionStatus::Completed;
            ActiveTreatments::<T>::insert(&patient, &protocol_id, &exec);
            OutcomeTracking::<T>::insert(&patient, &protocol_id, &outcome);

            Self::deposit_event(Event::TreatmentCompleted {
                patient,
                protocol_id,
                success,
            });
            Ok(())
        }

        /// Report adverse event.
        #[pallet::call_index(12)]
        #[pallet::weight(T::WeightInfo::report_adverse_event())]
        pub fn report_adverse_event(
            origin: OriginFor<T>,
            patient: T::AccountId,
            protocol_id: T::Hash,
            description: BoundedVec<u8, ConstU32<256>>,
        ) -> DispatchResult {
            let reporter = ensure_signed(origin)?;

            AdverseEvents::<T>::mutate(&patient, &protocol_id, |events| {
                let _ = events.try_push(description);
            });

            Self::deposit_event(Event::AdverseEventReported {
                patient,
                protocol_id,
                reporter,
            });
            Ok(())
        }

        /// Add interaction rule (root or authorized).
        #[pallet::call_index(13)]
        #[pallet::weight(T::WeightInfo::add_interaction_rule())]
        pub fn add_interaction_rule(
            origin: OriginFor<T>,
            substance_a: BoundedVec<u8, ConstU32<128>>,
            substance_b: BoundedVec<u8, ConstU32<128>>,
            severity: InteractionSeverity,
            mechanism: BoundedVec<u8, ConstU32<256>>,
            recommendation: BoundedVec<u8, ConstU32<256>>,
        ) -> DispatchResult {
            ensure_root(origin)?;

            let id = NextInteractionRuleId::<T>::get();
            NextInteractionRuleId::<T>::put(id.saturating_add(1));
            let rule = InteractionRule {
                rule_id: id,
                substance_a,
                substance_b,
                severity,
                mechanism,
                recommendation,
            };
            InteractionDatabase::<T>::insert(id, &rule);

            Self::deposit_event(Event::InteractionRuleAdded {
                rule_id: id,
                severity,
            });
            Ok(())
        }

        /// Query interaction (read-only; no state change). Call from off-chain or use storage read.
        #[pallet::call_index(14)]
        #[pallet::weight(T::WeightInfo::query_interaction())]
        pub fn query_interaction(
            origin: OriginFor<T>,
            substance_a: BoundedVec<u8, ConstU32<128>>,
            substance_b: BoundedVec<u8, ConstU32<128>>,
        ) -> DispatchResult {
            let _caller = ensure_signed(origin)?;

            for (_, rule) in InteractionDatabase::<T>::iter() {
                let match_ab = (rule.substance_a == substance_a && rule.substance_b == substance_b)
                    || (rule.substance_a == substance_b && rule.substance_b == substance_a);
                if match_ab {
                    if rule.severity == InteractionSeverity::Contraindicated || rule.severity == InteractionSeverity::Major {
                        return Err(Error::<T>::InteractionCheckFailed.into());
                    }
                }
            }
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

        /// Check for contraindications (protocol vs patient)
        fn check_protocol_contraindications(
            _patient: &T::AccountId,
            _protocol: &TreatmentProtocol<T>,
        ) -> ContraindicationStatus {
            // Simplified contraindication check
            // In production, cross-reference with patient allergies, medications, conditions
            ContraindicationStatus {
                has_contraindications: false,
                reasons: BoundedVec::default(),
            }
        }
    }

/// Weight information for extrinsics
pub trait WeightInfo {
    fn create_protocol() -> Weight;
    fn validate_protocol() -> Weight;
    fn update_protocol() -> Weight;
    fn register_guideline() -> Weight;
    fn register_protocol() -> Weight;
    fn validate_protocol_spec() -> Weight;
    fn initiate_treatment() -> Weight;
    fn record_step_completion() -> Weight;
    fn check_contraindications() -> Weight;
    fn evaluate_milestone() -> Weight;
    fn modify_protocol() -> Weight;
    fn complete_treatment() -> Weight;
    fn report_adverse_event() -> Weight;
    fn add_interaction_rule() -> Weight;
    fn query_interaction() -> Weight;
}

/// Protocol ID type
pub type ProtocolId = u64;

/// Guideline ID type
pub type GuidelineId = u32;

/// Treatment protocol
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
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
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
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
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
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
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
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
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
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

/// Clinical guideline (manual Debug impl to avoid requiring T: Debug)
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, TypeInfo, MaxEncodedLen)]
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

impl<T: frame_system::Config> core::fmt::Debug for ClinicalGuideline<T> {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.debug_struct("ClinicalGuideline")
            .field("name", &self.name)
            .field("version", &self.version)
            .field("content", &self.content)
            .field("registered_at", &self.registered_at)
            .finish()
    }
}

/// Contraindication status
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub struct ContraindicationStatus {
    /// Whether contraindications were detected
    pub has_contraindications: bool,
    /// Reasons for contraindications
    pub reasons: BoundedVec<u8, ConstU32<1024>>,
}
}

pub use pallet::*;
