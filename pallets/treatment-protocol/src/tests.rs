//! Comprehensive test suite for pallet-treatment-protocol.
//!
//! Covers both the **legacy** API (create_protocol / validate_protocol / update_protocol /
//! register_guideline) and the **spec** API (register_protocol / validate_protocol_spec /
//! initiate_treatment / record_step_completion / check_contraindications /
//! evaluate_milestone / modify_protocol / complete_treatment /
//! report_adverse_event / add_interaction_rule / query_interaction).
//!
//! Storage key:
//!   Legacy  → TreatmentProtocols / ClinicalGuidelines / Contraindications
//!   Spec    → ProtocolRegistry / ProtocolSteps / ActiveTreatments /
//!             InteractionDatabase / OutcomeTracking / AdverseEvents

use crate::mock::*;
use crate::{
    ActiveTreatments, AdverseEvents, ClinicalCondition, EvidenceLevel, Error, Event,
    Frequency, HerbFormula, InteractionDatabase, InteractionSeverity,
    InterventionType, Medication, MilestoneCheck, NextInteractionRuleId,
    OutcomeTracking, Prerequisite, ProtocolRegistry,
    ProtocolSteps, SuccessCriteria, TherapeuticModality, Treatment,
    TreatmentExecutionStatus, TreatmentStep, TreatmentType,
    TreatmentProtocols, ClinicalGuideline, Modality, ProtocolStatus,
};
use frame_support::{assert_err, assert_ok, BoundedVec, traits::ConstU32};
use sp_core::H256;

// ──────────────────────────────────────────────────────────────────────────────
// Builder helpers
// ──────────────────────────────────────────────────────────────────────────────

fn pid(n: u8) -> H256 {
    H256::from([n; 32])
}

fn bvec32(s: &[u8]) -> BoundedVec<u8, ConstU32<32>> {
    BoundedVec::try_from(s.to_vec()).unwrap()
}
fn bvec64(s: &[u8]) -> BoundedVec<u8, ConstU32<64>> {
    BoundedVec::try_from(s.to_vec()).unwrap()
}
fn bvec128(s: &[u8]) -> BoundedVec<u8, ConstU32<128>> {
    BoundedVec::try_from(s.to_vec()).unwrap()
}
fn bvec256(s: &[u8]) -> BoundedVec<u8, ConstU32<256>> {
    BoundedVec::try_from(s.to_vec()).unwrap()
}
fn bvec512(s: &[u8]) -> BoundedVec<u8, ConstU32<512>> {
    BoundedVec::try_from(s.to_vec()).unwrap()
}

fn condition(code: &[u8]) -> ClinicalCondition {
    ClinicalCondition {
        code: bvec32(code),
        description: bvec128(b"Test condition"),
    }
}

fn criteria(desc: &[u8]) -> SuccessCriteria {
    SuccessCriteria {
        description: bvec256(desc),
        measurable: true,
    }
}

fn single_modality(m: TherapeuticModality) -> BoundedVec<TherapeuticModality, ConstU32<8>> {
    BoundedVec::try_from(vec![m]).unwrap()
}

fn multi_modality(ms: &[TherapeuticModality]) -> BoundedVec<TherapeuticModality, ConstU32<8>> {
    BoundedVec::try_from(ms.to_vec()).unwrap()
}

fn make_step(n: u32, itype: InterventionType) -> TreatmentStep {
    TreatmentStep {
        step_number: n,
        intervention_type: itype,
        medication: None,
        herb_formula: None,
        procedure: None,
        duration_days: 7,
        frequency: Frequency { times_per_day: 1, days_per_week: 7 },
        prerequisites: BoundedVec::default(),
        success_criteria: None,
        next_step_conditions: BoundedVec::default(),
    }
}

fn steps(nums: &[(u32, InterventionType)]) -> BoundedVec<TreatmentStep, ConstU32<64>> {
    let v: Vec<TreatmentStep> = nums.iter().map(|(n, t)| make_step(*n, *t)).collect();
    BoundedVec::try_from(v).unwrap()
}

fn one_step() -> BoundedVec<TreatmentStep, ConstU32<64>> {
    steps(&[(1, InterventionType::Monitoring)])
}

fn substance(s: &[u8]) -> BoundedVec<u8, ConstU32<128>> {
    bvec128(s)
}

fn set_block(n: u64) {
    System::set_block_number(n);
}

/// Register a spec protocol with id `pid(n)`, created by `creator`, a single step.
fn register(creator: u64, id: H256, ev: EvidenceLevel) {
    assert_ok!(TreatmentProtocol::register_protocol(
        RuntimeOrigin::signed(creator),
        id,
        bvec128(b"Test Protocol"),
        condition(b"COND"),
        single_modality(TherapeuticModality::Western),
        ev,
        90,
        criteria(b"Improve outcome"),
        one_step(),
    ));
}

/// Register + initiate a spec treatment for `patient`.
fn start_treatment(creator: u64, patient: u64, id: H256) {
    register(creator, id, EvidenceLevel::ExpertOpinion);
    assert_ok!(TreatmentProtocol::initiate_treatment(
        RuntimeOrigin::signed(creator),
        patient,
        id,
    ));
}

/// Add a Warfarin + Ginkgo Contraindicated rule.
fn add_warfarin_ginkgo_rule() {
    assert_ok!(TreatmentProtocol::add_interaction_rule(
        RuntimeOrigin::root(),
        substance(b"Warfarin"),
        substance(b"Ginkgo"),
        InteractionSeverity::Contraindicated,
        bvec256(b"Anticoagulant potentiation"),
        bvec256(b"Do not combine - serious bleeding risk"),
    ));
}

/// Make a legacy Treatment item.
fn legacy_treatment(m: Modality) -> Treatment {
    Treatment {
        treatment_type: TreatmentType::Medication,
        details: BoundedVec::try_from(b"Details".to_vec()).unwrap(),
        modality: m,
        dosage: bvec512(b"500mg once daily"),
    }
}

// ──────────────────────────────────────────────────────────────────────────────
// LEGACY API — create_protocol / validate_protocol / update_protocol
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn legacy_create_protocol_stores_entry() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let treatments = vec![legacy_treatment(Modality::Western)];
        assert_ok!(TreatmentProtocol::create_protocol(
            RuntimeOrigin::signed(ALICE),
            BOB,
            42u64,
            treatments,
            None,
        ));
        let p = TreatmentProtocols::<Test>::get(BOB, 42u64).unwrap();
        assert_eq!(p.provider, ALICE);
        assert_eq!(p.patient, BOB);
        assert_eq!(p.treatments.len(), 1);
        assert_eq!(p.status, ProtocolStatus::Active);
    });
}

#[test]
fn legacy_create_protocol_fails_for_missing_guideline() {
    new_test_ext().execute_with(|| {
        assert_err!(
            TreatmentProtocol::create_protocol(
                RuntimeOrigin::signed(ALICE),
                BOB,
                1u64,
                vec![legacy_treatment(Modality::TCM)],
                Some(999u32), // guideline doesn't exist
            ),
            Error::<Test>::GuidelineNotFound
        );
    });
}

#[test]
fn legacy_create_protocol_emits_protocol_created_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(TreatmentProtocol::create_protocol(
            RuntimeOrigin::signed(ALICE),
            BOB,
            10u64,
            vec![legacy_treatment(Modality::Integrative)],
            None,
        ));
        System::assert_has_event(
            Event::<Test>::ProtocolCreated {
                patient: BOB,
                protocol_id: 10u64,
                provider: ALICE,
            }
            .into(),
        );
    });
}

#[test]
fn legacy_validate_protocol_emits_validated_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(TreatmentProtocol::create_protocol(
            RuntimeOrigin::signed(ALICE),
            BOB,
            20u64,
            vec![legacy_treatment(Modality::Western)],
            None,
        ));
        assert_ok!(TreatmentProtocol::validate_protocol(
            RuntimeOrigin::signed(CHARLIE),
            BOB,
            20u64,
        ));
        System::assert_has_event(
            Event::<Test>::ProtocolValidated {
                patient: BOB,
                protocol_id: 20u64,
                compliant: true, // treatments list non-empty
            }
            .into(),
        );
    });
}

#[test]
fn legacy_validate_protocol_compliant_false_for_empty_treatments() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(TreatmentProtocol::create_protocol(
            RuntimeOrigin::signed(ALICE),
            BOB,
            21u64,
            vec![], // no treatments
            None,
        ));
        assert_ok!(TreatmentProtocol::validate_protocol(
            RuntimeOrigin::signed(CHARLIE),
            BOB,
            21u64,
        ));
        System::assert_has_event(
            Event::<Test>::ProtocolValidated {
                patient: BOB,
                protocol_id: 21u64,
                compliant: false,
            }
            .into(),
        );
    });
}

#[test]
fn legacy_validate_protocol_fails_for_missing_protocol() {
    new_test_ext().execute_with(|| {
        assert_err!(
            TreatmentProtocol::validate_protocol(RuntimeOrigin::signed(CHARLIE), BOB, 999u64),
            Error::<Test>::ProtocolNotFound
        );
    });
}

#[test]
fn legacy_update_protocol_changes_treatments() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(TreatmentProtocol::create_protocol(
            RuntimeOrigin::signed(ALICE),
            BOB,
            30u64,
            vec![legacy_treatment(Modality::Western)],
            None,
        ));
        assert_ok!(TreatmentProtocol::update_protocol(
            RuntimeOrigin::signed(ALICE),
            BOB,
            30u64,
            vec![
                legacy_treatment(Modality::Western),
                legacy_treatment(Modality::TCM),
            ],
        ));
        let p = TreatmentProtocols::<Test>::get(BOB, 30u64).unwrap();
        assert_eq!(p.treatments.len(), 2);
        assert_eq!(p.status, ProtocolStatus::Updated);
    });
}

#[test]
fn legacy_register_guideline_requires_root() {
    new_test_ext().execute_with(|| {
        let gl = ClinicalGuideline::<Test> {
            name: bvec256(b"ADA Guidelines"),
            version: bvec64(b"2024"),
            content: BoundedVec::default(),
            registered_at: 0u64,
        };
        assert_err!(
            TreatmentProtocol::register_guideline(
                RuntimeOrigin::signed(ALICE),
                1u32,
                gl.clone(),
            ),
            frame_support::error::BadOrigin
        );
        assert_ok!(TreatmentProtocol::register_guideline(RuntimeOrigin::root(), 1u32, gl));
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — register_protocol
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn register_protocol_stores_definition() {
    new_test_ext().execute_with(|| {
        set_block(1);
        register(ALICE, pid(1), EvidenceLevel::RandomizedControlled);
        let def = ProtocolRegistry::<Test>::get(pid(1)).unwrap();
        assert_eq!(def.created_by, ALICE);
        assert!(def.active);
        assert_eq!(def.validated_by.len(), 0);
        assert_eq!(def.evidence_level, EvidenceLevel::RandomizedControlled);
    });
}

#[test]
fn register_protocol_stores_treatment_steps() {
    new_test_ext().execute_with(|| {
        let s = steps(&[
            (1, InterventionType::Pharmaceutical),
            (2, InterventionType::Botanical),
            (3, InterventionType::Dietary),
        ]);
        assert_ok!(TreatmentProtocol::register_protocol(
            RuntimeOrigin::signed(ALICE),
            pid(2),
            bvec128(b"Diabetes Protocol"),
            condition(b"T2DM"),
            single_modality(TherapeuticModality::Western),
            EvidenceLevel::RandomizedControlled,
            180,
            criteria(b"HbA1c < 7%"),
            s,
        ));
        let stored_steps = ProtocolSteps::<Test>::get(pid(2)).unwrap();
        assert_eq!(stored_steps.len(), 3);
        assert_eq!(stored_steps[0].step_number, 1);
        assert_eq!(stored_steps[2].step_number, 3);
    });
}

#[test]
fn register_protocol_fails_on_duplicate() {
    new_test_ext().execute_with(|| {
        register(ALICE, pid(3), EvidenceLevel::ExpertOpinion);
        assert_err!(
            TreatmentProtocol::register_protocol(
                RuntimeOrigin::signed(BOB),
                pid(3),
                bvec128(b"Duplicate"),
                condition(b"DUP"),
                single_modality(TherapeuticModality::TCM),
                EvidenceLevel::CohortStudy,
                30,
                criteria(b"..."),
                one_step(),
            ),
            Error::<Test>::ProtocolAlreadyExists
        );
    });
}

#[test]
fn register_protocol_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(TreatmentProtocol::register_protocol(
            RuntimeOrigin::signed(ALICE),
            pid(4),
            bvec128(b"Hypertension Protocol"),
            condition(b"HTN"),
            single_modality(TherapeuticModality::Integrative),
            EvidenceLevel::SystematicReview,
            365,
            criteria(b"BP < 130/80"),
            one_step(),
        ));
        System::assert_last_event(
            Event::<Test>::ProtocolRegistered {
                protocol_id: pid(4),
                name: bvec128(b"Hypertension Protocol"),
                evidence_level: EvidenceLevel::SystematicReview,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — validate_protocol_spec (evidence levels + multiple validators)
// ──────────────────────────────────────────────────────────────────────────────

macro_rules! evidence_level_test {
    ($fn_name:ident, $level:expr, $pid_byte:expr) => {
        #[test]
        fn $fn_name() {
            new_test_ext().execute_with(|| {
                register(ALICE, pid($pid_byte), $level);
                let def = ProtocolRegistry::<Test>::get(pid($pid_byte)).unwrap();
                assert_eq!(def.evidence_level, $level);
            });
        }
    };
}

evidence_level_test!(evidence_systematic_review, EvidenceLevel::SystematicReview, 10);
evidence_level_test!(evidence_randomized_controlled, EvidenceLevel::RandomizedControlled, 11);
evidence_level_test!(evidence_cohort_study, EvidenceLevel::CohortStudy, 12);
evidence_level_test!(evidence_case_control, EvidenceLevel::CaseControl, 13);
evidence_level_test!(evidence_expert_opinion, EvidenceLevel::ExpertOpinion, 14);
evidence_level_test!(evidence_traditional_knowledge, EvidenceLevel::TraditionalKnowledge, 15);

#[test]
fn validate_protocol_spec_adds_validator_to_list() {
    new_test_ext().execute_with(|| {
        register(ALICE, pid(20), EvidenceLevel::SystematicReview);
        assert_ok!(TreatmentProtocol::validate_protocol_spec(
            RuntimeOrigin::signed(CHARLIE),
            pid(20),
        ));
        let def = ProtocolRegistry::<Test>::get(pid(20)).unwrap();
        assert_eq!(def.validated_by.len(), 1);
        assert!(def.validated_by.contains(&CHARLIE));
    });
}

#[test]
fn validate_protocol_spec_multiple_validators() {
    new_test_ext().execute_with(|| {
        register(ALICE, pid(21), EvidenceLevel::RandomizedControlled);
        assert_ok!(TreatmentProtocol::validate_protocol_spec(
            RuntimeOrigin::signed(CHARLIE),
            pid(21),
        ));
        assert_ok!(TreatmentProtocol::validate_protocol_spec(
            RuntimeOrigin::signed(DAVE),
            pid(21),
        ));
        let def = ProtocolRegistry::<Test>::get(pid(21)).unwrap();
        assert_eq!(def.validated_by.len(), 2);
        assert!(def.validated_by.contains(&CHARLIE));
        assert!(def.validated_by.contains(&DAVE));
    });
}

#[test]
fn validate_protocol_spec_fails_for_non_existent_protocol() {
    new_test_ext().execute_with(|| {
        assert_err!(
            TreatmentProtocol::validate_protocol_spec(RuntimeOrigin::signed(CHARLIE), pid(99)),
            Error::<Test>::ProtocolNotFound
        );
    });
}

#[test]
fn validate_protocol_spec_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        register(ALICE, pid(22), EvidenceLevel::CohortStudy);
        assert_ok!(TreatmentProtocol::validate_protocol_spec(
            RuntimeOrigin::signed(CHARLIE),
            pid(22),
        ));
        System::assert_last_event(
            Event::<Test>::ProtocolValidatedSpec {
                protocol_id: pid(22),
                validator: CHARLIE,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — initiate_treatment
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn initiate_treatment_creates_execution_record() {
    new_test_ext().execute_with(|| {
        set_block(5);
        start_treatment(ALICE, BOB, pid(30));
        let exec = ActiveTreatments::<Test>::get(BOB, pid(30)).unwrap();
        assert_eq!(exec.patient, BOB);
        assert_eq!(exec.protocol_id, pid(30));
        assert_eq!(exec.current_step, 1);
        assert_eq!(exec.started_at, 5u64);
        assert_eq!(exec.status, TreatmentExecutionStatus::Active);
        assert!(exec.outcome.is_none());
        assert!(exec.completed_steps.is_empty());
    });
}

#[test]
fn initiate_treatment_sets_start_timestamp() {
    new_test_ext().execute_with(|| {
        set_block(42);
        start_treatment(ALICE, BOB, pid(31));
        let exec = ActiveTreatments::<Test>::get(BOB, pid(31)).unwrap();
        assert_eq!(exec.started_at, 42u64);
    });
}

#[test]
fn initiate_treatment_fails_for_non_existent_protocol() {
    new_test_ext().execute_with(|| {
        assert_err!(
            TreatmentProtocol::initiate_treatment(RuntimeOrigin::signed(ALICE), BOB, pid(99)),
            Error::<Test>::ProtocolNotFound
        );
    });
}

#[test]
fn initiate_treatment_fails_if_already_active() {
    new_test_ext().execute_with(|| {
        start_treatment(ALICE, BOB, pid(32));
        assert_err!(
            TreatmentProtocol::initiate_treatment(RuntimeOrigin::signed(ALICE), BOB, pid(32)),
            Error::<Test>::ProtocolAlreadyExists
        );
    });
}

#[test]
fn initiate_treatment_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(7);
        register(ALICE, pid(33), EvidenceLevel::ExpertOpinion);
        assert_ok!(TreatmentProtocol::initiate_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(33),
        ));
        System::assert_last_event(
            Event::<Test>::TreatmentInitiated {
                patient: BOB,
                protocol_id: pid(33),
                started_at: 7u64,
            }
            .into(),
        );
    });
}

#[test]
fn initiate_treatment_different_patients_same_protocol() {
    new_test_ext().execute_with(|| {
        register(ALICE, pid(34), EvidenceLevel::ExpertOpinion);
        assert_ok!(TreatmentProtocol::initiate_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(34),
        ));
        assert_ok!(TreatmentProtocol::initiate_treatment(
            RuntimeOrigin::signed(ALICE),
            CHARLIE,
            pid(34),
        ));
        assert!(ActiveTreatments::<Test>::get(BOB, pid(34)).is_some());
        assert!(ActiveTreatments::<Test>::get(CHARLIE, pid(34)).is_some());
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — record_step_completion
// ──────────────────────────────────────────────────────────────────────────────

/// Register a 3-step protocol and start it for BOB.
fn setup_3step_treatment(id: H256) {
    let s = steps(&[
        (1, InterventionType::Pharmaceutical),
        (2, InterventionType::Dietary),
        (3, InterventionType::Lifestyle),
    ]);
    assert_ok!(TreatmentProtocol::register_protocol(
        RuntimeOrigin::signed(ALICE),
        id,
        bvec128(b"3-Step Protocol"),
        condition(b"COND"),
        single_modality(TherapeuticModality::Western),
        EvidenceLevel::ExpertOpinion,
        90,
        criteria(b"Improve"),
        s,
    ));
    assert_ok!(TreatmentProtocol::initiate_treatment(
        RuntimeOrigin::signed(ALICE),
        BOB,
        id,
    ));
}

#[test]
fn record_step_completion_logs_step_and_advances() {
    new_test_ext().execute_with(|| {
        setup_3step_treatment(pid(40));
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(40),
            1,
        ));
        let exec = ActiveTreatments::<Test>::get(BOB, pid(40)).unwrap();
        assert_eq!(exec.completed_steps.len(), 1);
        assert_eq!(exec.completed_steps[0], 1);
        assert_eq!(exec.current_step, 2);
        assert_eq!(exec.adherence_log.len(), 1);
    });
}

#[test]
fn record_step_completion_sequential_steps() {
    new_test_ext().execute_with(|| {
        setup_3step_treatment(pid(41));
        for step in 1u32..=3 {
            assert_ok!(TreatmentProtocol::record_step_completion(
                RuntimeOrigin::signed(ALICE),
                BOB,
                pid(41),
                step,
            ));
        }
        let exec = ActiveTreatments::<Test>::get(BOB, pid(41)).unwrap();
        assert_eq!(exec.completed_steps.len(), 3);
        assert_eq!(exec.current_step, 4);
    });
}

#[test]
fn record_step_completion_fails_wrong_step_order() {
    new_test_ext().execute_with(|| {
        setup_3step_treatment(pid(42));
        // current_step is 1; trying to record step 2 should fail
        assert_err!(
            TreatmentProtocol::record_step_completion(
                RuntimeOrigin::signed(ALICE),
                BOB,
                pid(42),
                2,
            ),
            Error::<Test>::InvalidStep
        );
    });
}

#[test]
fn record_step_completion_fails_for_non_existent_step() {
    new_test_ext().execute_with(|| {
        setup_3step_treatment(pid(43));
        // Protocol only has steps 1, 2, 3 but current_step=1
        // Step 99 doesn't exist in ProtocolSteps
        // First we need to artificially set current_step to 99 via modify_protocol
        assert_ok!(TreatmentProtocol::modify_protocol(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(43),
            99,
        ));
        assert_err!(
            TreatmentProtocol::record_step_completion(
                RuntimeOrigin::signed(ALICE),
                BOB,
                pid(43),
                99,
            ),
            Error::<Test>::InvalidStep
        );
    });
}

#[test]
fn record_step_completion_fails_for_no_treatment() {
    new_test_ext().execute_with(|| {
        assert_err!(
            TreatmentProtocol::record_step_completion(
                RuntimeOrigin::signed(ALICE),
                BOB,
                pid(200),
                1,
            ),
            Error::<Test>::ProtocolNotFound
        );
    });
}

#[test]
fn record_step_completion_fails_on_inactive_treatment() {
    new_test_ext().execute_with(|| {
        setup_3step_treatment(pid(44));
        // Complete the treatment first
        assert_ok!(TreatmentProtocol::complete_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(44),
            true,
            bvec512(b"Success"),
        ));
        // Now try to record a step — treatment is Completed, not Active
        assert_err!(
            TreatmentProtocol::record_step_completion(
                RuntimeOrigin::signed(ALICE),
                BOB,
                pid(44),
                1,
            ),
            Error::<Test>::TreatmentNotActive
        );
    });
}

#[test]
fn record_step_completion_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(3);
        setup_3step_treatment(pid(45));
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(45),
            1,
        ));
        System::assert_last_event(
            Event::<Test>::StepCompletionRecorded {
                patient: BOB,
                protocol_id: pid(45),
                step_number: 1,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — check_contraindications / query_interaction / add_interaction_rule
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn add_interaction_rule_requires_root() {
    new_test_ext().execute_with(|| {
        assert_err!(
            TreatmentProtocol::add_interaction_rule(
                RuntimeOrigin::signed(ALICE),
                substance(b"DrugA"),
                substance(b"DrugB"),
                InteractionSeverity::Major,
                bvec256(b"Mechanism"),
                bvec256(b"Recommendation"),
            ),
            frame_support::error::BadOrigin
        );
    });
}

#[test]
fn add_interaction_rule_stores_and_increments_id() {
    new_test_ext().execute_with(|| {
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            substance(b"MetforminX"),
            substance(b"LicoriceRoot"),
            InteractionSeverity::Major,
            bvec256(b"Additive glucose lowering"),
            bvec256(b"Monitor glucose closely"),
        ));
        assert_eq!(NextInteractionRuleId::<Test>::get(), 1);
        let rule = InteractionDatabase::<Test>::get(0).unwrap();
        assert_eq!(rule.severity, InteractionSeverity::Major);
    });
}

#[test]
fn add_interaction_rule_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            substance(b"Aspirin"),
            substance(b"Ginger"),
            InteractionSeverity::Moderate,
            bvec256(b"Antiplatelet additive"),
            bvec256(b"Monitor bleeding risk"),
        ));
        System::assert_last_event(
            Event::<Test>::InteractionRuleAdded {
                rule_id: 0,
                severity: InteractionSeverity::Moderate,
            }
            .into(),
        );
    });
}

#[test]
fn check_contraindications_ok_with_no_rules() {
    new_test_ext().execute_with(|| {
        assert_ok!(TreatmentProtocol::check_contraindications(
            RuntimeOrigin::signed(ALICE),
            substance(b"Metformin"),
            substance(b"LicoriceRoot"),
        ));
    });
}

#[test]
fn check_contraindications_fails_for_contraindicated_pair() {
    new_test_ext().execute_with(|| {
        add_warfarin_ginkgo_rule();
        assert_err!(
            TreatmentProtocol::check_contraindications(
                RuntimeOrigin::signed(ALICE),
                substance(b"Warfarin"),
                substance(b"Ginkgo"),
            ),
            Error::<Test>::InteractionCheckFailed
        );
    });
}

#[test]
fn check_contraindications_fails_for_major_pair() {
    new_test_ext().execute_with(|| {
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            substance(b"Metformin"),
            substance(b"LicoriceRoot"),
            InteractionSeverity::Major,
            bvec256(b"Additive glucose lowering"),
            bvec256(b"Monitor glucose closely"),
        ));
        assert_err!(
            TreatmentProtocol::check_contraindications(
                RuntimeOrigin::signed(ALICE),
                substance(b"Metformin"),
                substance(b"LicoriceRoot"),
            ),
            Error::<Test>::InteractionCheckFailed
        );
    });
}

#[test]
fn check_contraindications_passes_for_moderate_severity() {
    new_test_ext().execute_with(|| {
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            substance(b"Aspirin"),
            substance(b"Ginger"),
            InteractionSeverity::Moderate,
            bvec256(b"Antiplatelet additive"),
            bvec256(b"Monitor bleeding"),
        ));
        // Moderate does NOT block — returns Ok
        assert_ok!(TreatmentProtocol::check_contraindications(
            RuntimeOrigin::signed(ALICE),
            substance(b"Aspirin"),
            substance(b"Ginger"),
        ));
    });
}

#[test]
fn check_contraindications_passes_for_minor_severity() {
    new_test_ext().execute_with(|| {
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            substance(b"IbuprofenX"),
            substance(b"ChamomileX"),
            InteractionSeverity::Minor,
            bvec256(b"Mild potentiation"),
            bvec256(b"No special precaution"),
        ));
        assert_ok!(TreatmentProtocol::check_contraindications(
            RuntimeOrigin::signed(ALICE),
            substance(b"IbuprofenX"),
            substance(b"ChamomileX"),
        ));
    });
}

#[test]
fn check_contraindications_bidirectional_matching() {
    new_test_ext().execute_with(|| {
        add_warfarin_ginkgo_rule();
        // Reversed order should also fail
        assert_err!(
            TreatmentProtocol::check_contraindications(
                RuntimeOrigin::signed(ALICE),
                substance(b"Ginkgo"),
                substance(b"Warfarin"),
            ),
            Error::<Test>::InteractionCheckFailed
        );
    });
}

#[test]
fn interaction_database_warfarin_ginkgo_contraindicated() {
    new_test_ext().execute_with(|| {
        add_warfarin_ginkgo_rule();
        let rule = InteractionDatabase::<Test>::get(0).unwrap();
        assert_eq!(rule.substance_a, substance(b"Warfarin"));
        assert_eq!(rule.substance_b, substance(b"Ginkgo"));
        assert_eq!(rule.severity, InteractionSeverity::Contraindicated);
    });
}

#[test]
fn interaction_database_metformin_licorice_major() {
    new_test_ext().execute_with(|| {
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            substance(b"Metformin"),
            substance(b"LicoriceRoot"),
            InteractionSeverity::Major,
            bvec256(b"Additive glucose lowering"),
            bvec256(b"Monitor glucose closely"),
        ));
        let rule = InteractionDatabase::<Test>::get(0).unwrap();
        assert_eq!(rule.severity, InteractionSeverity::Major);
    });
}

#[test]
fn interaction_database_aspirin_ginger_moderate() {
    new_test_ext().execute_with(|| {
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            substance(b"Aspirin"),
            substance(b"Ginger"),
            InteractionSeverity::Moderate,
            bvec256(b"Antiplatelet additive"),
            bvec256(b"Monitor bleeding"),
        ));
        let rule = InteractionDatabase::<Test>::get(0).unwrap();
        assert_eq!(rule.severity, InteractionSeverity::Moderate);
        assert_eq!(rule.recommendation, bvec256(b"Monitor bleeding"));
    });
}

#[test]
fn query_interaction_returns_err_for_contraindicated() {
    new_test_ext().execute_with(|| {
        add_warfarin_ginkgo_rule();
        assert_err!(
            TreatmentProtocol::query_interaction(
                RuntimeOrigin::signed(ALICE),
                substance(b"Warfarin"),
                substance(b"Ginkgo"),
            ),
            Error::<Test>::InteractionCheckFailed
        );
    });
}

#[test]
fn query_interaction_returns_ok_for_moderate() {
    new_test_ext().execute_with(|| {
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            substance(b"Aspirin"),
            substance(b"Ginger"),
            InteractionSeverity::Moderate,
            bvec256(b"Mechanism"),
            bvec256(b"Recommendation"),
        ));
        assert_ok!(TreatmentProtocol::query_interaction(
            RuntimeOrigin::signed(ALICE),
            substance(b"Aspirin"),
            substance(b"Ginger"),
        ));
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — evaluate_milestone
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn evaluate_milestone_met_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(2);
        start_treatment(ALICE, BOB, pid(50));
        assert_ok!(TreatmentProtocol::evaluate_milestone(
            RuntimeOrigin::signed(CHARLIE),
            BOB,
            pid(50),
            1,
            true,
        ));
        System::assert_last_event(
            Event::<Test>::MilestoneEvaluated {
                patient: BOB,
                protocol_id: pid(50),
                step_number: 1,
                met: true,
            }
            .into(),
        );
    });
}

#[test]
fn evaluate_milestone_not_met_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(2);
        start_treatment(ALICE, BOB, pid(51));
        assert_ok!(TreatmentProtocol::evaluate_milestone(
            RuntimeOrigin::signed(CHARLIE),
            BOB,
            pid(51),
            1,
            false,
        ));
        System::assert_last_event(
            Event::<Test>::MilestoneEvaluated {
                patient: BOB,
                protocol_id: pid(51),
                step_number: 1,
                met: false,
            }
            .into(),
        );
    });
}

#[test]
fn evaluate_milestone_fails_for_no_treatment() {
    new_test_ext().execute_with(|| {
        assert_err!(
            TreatmentProtocol::evaluate_milestone(
                RuntimeOrigin::signed(CHARLIE),
                BOB,
                pid(200),
                1,
                true,
            ),
            Error::<Test>::ProtocolNotFound
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — modify_protocol
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn modify_protocol_changes_current_step() {
    new_test_ext().execute_with(|| {
        start_treatment(ALICE, BOB, pid(60));
        assert_ok!(TreatmentProtocol::modify_protocol(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(60),
            5,
        ));
        let exec = ActiveTreatments::<Test>::get(BOB, pid(60)).unwrap();
        assert_eq!(exec.current_step, 5);
        assert_eq!(exec.status, TreatmentExecutionStatus::Active);
    });
}

#[test]
fn modify_protocol_fails_for_no_treatment() {
    new_test_ext().execute_with(|| {
        assert_err!(
            TreatmentProtocol::modify_protocol(RuntimeOrigin::signed(ALICE), BOB, pid(200), 3),
            Error::<Test>::ProtocolNotFound
        );
    });
}

#[test]
fn modify_protocol_fails_when_treatment_completed() {
    new_test_ext().execute_with(|| {
        start_treatment(ALICE, BOB, pid(61));
        assert_ok!(TreatmentProtocol::complete_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(61),
            true,
            bvec512(b"Success"),
        ));
        assert_err!(
            TreatmentProtocol::modify_protocol(RuntimeOrigin::signed(ALICE), BOB, pid(61), 2),
            Error::<Test>::TreatmentNotActive
        );
    });
}

#[test]
fn modify_protocol_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        start_treatment(ALICE, BOB, pid(62));
        assert_ok!(TreatmentProtocol::modify_protocol(
            RuntimeOrigin::signed(CHARLIE),
            BOB,
            pid(62),
            3,
        ));
        System::assert_last_event(
            Event::<Test>::ProtocolModified {
                patient: BOB,
                protocol_id: pid(62),
                modifier: CHARLIE,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — complete_treatment
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn complete_treatment_sets_outcome_and_status() {
    new_test_ext().execute_with(|| {
        set_block(100);
        start_treatment(ALICE, BOB, pid(70));
        assert_ok!(TreatmentProtocol::complete_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(70),
            true,
            bvec512(b"HbA1c normalised"),
        ));
        let exec = ActiveTreatments::<Test>::get(BOB, pid(70)).unwrap();
        assert_eq!(exec.status, TreatmentExecutionStatus::Completed);
        let outcome = exec.outcome.unwrap();
        assert!(outcome.success);
        assert_eq!(outcome.recorded_at, 100u64);
    });
}

#[test]
fn complete_treatment_stores_in_outcome_tracking() {
    new_test_ext().execute_with(|| {
        start_treatment(ALICE, BOB, pid(71));
        assert_ok!(TreatmentProtocol::complete_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(71),
            false,
            bvec512(b"Insufficient response"),
        ));
        let outcome = OutcomeTracking::<Test>::get(BOB, pid(71)).unwrap();
        assert!(!outcome.success);
    });
}

#[test]
fn complete_treatment_fails_if_outcome_already_recorded() {
    new_test_ext().execute_with(|| {
        start_treatment(ALICE, BOB, pid(72));
        assert_ok!(TreatmentProtocol::complete_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(72),
            true,
            bvec512(b"First outcome"),
        ));
        assert_err!(
            TreatmentProtocol::complete_treatment(
                RuntimeOrigin::signed(ALICE),
                BOB,
                pid(72),
                false,
                bvec512(b"Duplicate"),
            ),
            Error::<Test>::OutcomeAlreadyRecorded
        );
    });
}

#[test]
fn complete_treatment_emits_event_with_success_flag() {
    new_test_ext().execute_with(|| {
        set_block(1);
        start_treatment(ALICE, BOB, pid(73));
        assert_ok!(TreatmentProtocol::complete_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(73),
            true,
            bvec512(b"Great outcome"),
        ));
        System::assert_last_event(
            Event::<Test>::TreatmentCompleted {
                patient: BOB,
                protocol_id: pid(73),
                success: true,
            }
            .into(),
        );
    });
}

#[test]
fn complete_treatment_failure_outcome_in_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        start_treatment(ALICE, BOB, pid(74));
        assert_ok!(TreatmentProtocol::complete_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(74),
            false,
            bvec512(b"No improvement"),
        ));
        System::assert_last_event(
            Event::<Test>::TreatmentCompleted {
                patient: BOB,
                protocol_id: pid(74),
                success: false,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — report_adverse_event
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn report_adverse_event_stores_description() {
    new_test_ext().execute_with(|| {
        start_treatment(ALICE, BOB, pid(80));
        assert_ok!(TreatmentProtocol::report_adverse_event(
            RuntimeOrigin::signed(CHARLIE),
            BOB,
            pid(80),
            bvec256(b"Nausea and vomiting"),
        ));
        let events = AdverseEvents::<Test>::get(BOB, pid(80));
        assert_eq!(events.len(), 1);
    });
}

#[test]
fn report_adverse_event_accumulates_multiple_events() {
    new_test_ext().execute_with(|| {
        start_treatment(ALICE, BOB, pid(81));
        for msg in [b"Nausea".as_ref(), b"Rash".as_ref(), b"Dizziness".as_ref()] {
            assert_ok!(TreatmentProtocol::report_adverse_event(
                RuntimeOrigin::signed(CHARLIE),
                BOB,
                pid(81),
                bvec256(msg),
            ));
        }
        let events = AdverseEvents::<Test>::get(BOB, pid(81));
        assert_eq!(events.len(), 3);
    });
}

#[test]
fn report_adverse_event_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        start_treatment(ALICE, BOB, pid(82));
        assert_ok!(TreatmentProtocol::report_adverse_event(
            RuntimeOrigin::signed(CHARLIE),
            BOB,
            pid(82),
            bvec256(b"Severe headache"),
        ));
        System::assert_last_event(
            Event::<Test>::AdverseEventReported {
                patient: BOB,
                protocol_id: pid(82),
                reporter: CHARLIE,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// MODALITY COMBINATION TESTS
// ──────────────────────────────────────────────────────────────────────────────

macro_rules! modality_test {
    ($fn_name:ident, $modalities:expr, $pid_byte:expr) => {
        #[test]
        fn $fn_name() {
            new_test_ext().execute_with(|| {
                let m: BoundedVec<TherapeuticModality, ConstU32<8>> = $modalities;
                assert_ok!(TreatmentProtocol::register_protocol(
                    RuntimeOrigin::signed(ALICE),
                    pid($pid_byte),
                    bvec128(b"Protocol"),
                    condition(b"COND"),
                    m.clone(),
                    EvidenceLevel::ExpertOpinion,
                    30,
                    criteria(b"Improve"),
                    one_step(),
                ));
                let def = ProtocolRegistry::<Test>::get(pid($pid_byte)).unwrap();
                assert_eq!(def.modalities, m);
            });
        }
    };
}

modality_test!(modality_western_only, single_modality(TherapeuticModality::Western), 120);
modality_test!(modality_tcm_only, single_modality(TherapeuticModality::TCM), 121);
modality_test!(modality_ayurveda_only, single_modality(TherapeuticModality::Ayurveda), 122);
modality_test!(modality_integrative, single_modality(TherapeuticModality::Integrative), 123);
modality_test!(
    modality_western_and_tcm,
    multi_modality(&[TherapeuticModality::Western, TherapeuticModality::TCM]),
    124
);
modality_test!(
    modality_western_and_ayurveda,
    multi_modality(&[TherapeuticModality::Western, TherapeuticModality::Ayurveda]),
    125
);
modality_test!(
    modality_western_tcm_ayurveda,
    multi_modality(&[
        TherapeuticModality::Western,
        TherapeuticModality::TCM,
        TherapeuticModality::Ayurveda
    ]),
    126
);

// ──────────────────────────────────────────────────────────────────────────────
// INTERVENTION TYPE TESTS
// ──────────────────────────────────────────────────────────────────────────────

macro_rules! intervention_test {
    ($fn_name:ident, $itype:expr, $pid_byte:expr) => {
        #[test]
        fn $fn_name() {
            new_test_ext().execute_with(|| {
                let s = steps(&[(1, $itype)]);
                assert_ok!(TreatmentProtocol::register_protocol(
                    RuntimeOrigin::signed(ALICE),
                    pid($pid_byte),
                    bvec128(b"Protocol"),
                    condition(b"COND"),
                    single_modality(TherapeuticModality::Western),
                    EvidenceLevel::ExpertOpinion,
                    30,
                    criteria(b"Improve"),
                    s,
                ));
                let stored = ProtocolSteps::<Test>::get(pid($pid_byte)).unwrap();
                assert_eq!(stored[0].intervention_type, $itype);
            });
        }
    };
}

intervention_test!(intervention_pharmaceutical, InterventionType::Pharmaceutical, 130);
intervention_test!(intervention_botanical, InterventionType::Botanical, 131);
intervention_test!(intervention_acupuncture, InterventionType::Acupuncture, 132);
intervention_test!(intervention_dietary, InterventionType::Dietary, 133);
intervention_test!(intervention_lifestyle, InterventionType::Lifestyle, 134);
intervention_test!(intervention_surgical, InterventionType::Surgical, 135);
intervention_test!(intervention_monitoring, InterventionType::Monitoring, 136);

// ──────────────────────────────────────────────────────────────────────────────
// INTEGRATION TESTS
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn integration_diabetes_protocol_full_workflow() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // 1. Register a 3-step integrative diabetes protocol
        let s = steps(&[
            (1, InterventionType::Pharmaceutical), // Metformin
            (2, InterventionType::Botanical),       // TCM herbs
            (3, InterventionType::Lifestyle),       // Diet & exercise
        ]);
        assert_ok!(TreatmentProtocol::register_protocol(
            RuntimeOrigin::signed(ALICE),
            pid(150),
            bvec128(b"ABENA Diabetes Protocol"),
            condition(b"T2DM"),
            multi_modality(&[TherapeuticModality::Western, TherapeuticModality::TCM]),
            EvidenceLevel::RandomizedControlled,
            180,
            criteria(b"HbA1c < 7%"),
            s,
        ));

        // 2. Medical board validates
        assert_ok!(TreatmentProtocol::validate_protocol_spec(
            RuntimeOrigin::signed(CHARLIE),
            pid(150),
        ));

        // 3. Initiate treatment for patient BOB
        set_block(10);
        assert_ok!(TreatmentProtocol::initiate_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(150),
        ));

        // 4. Complete each step sequentially
        set_block(20);
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(150),
            1,
        ));
        set_block(40);
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(150),
            2,
        ));
        set_block(60);
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(150),
            3,
        ));

        // 5. Evaluate the final milestone
        assert_ok!(TreatmentProtocol::evaluate_milestone(
            RuntimeOrigin::signed(CHARLIE),
            BOB,
            pid(150),
            3,
            true, // HbA1c target met
        ));

        // 6. Complete treatment with success
        set_block(90);
        assert_ok!(TreatmentProtocol::complete_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(150),
            true,
            bvec512(b"HbA1c 6.5% achieved"),
        ));

        let exec = ActiveTreatments::<Test>::get(BOB, pid(150)).unwrap();
        assert_eq!(exec.status, TreatmentExecutionStatus::Completed);
        assert_eq!(exec.completed_steps.len(), 3);
        assert!(exec.outcome.unwrap().success);
    });
}

#[test]
fn integration_multi_step_branching_via_modify() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // Protocol with steps 1, 2, 3 (representing a branch)
        let s = steps(&[
            (1, InterventionType::Monitoring),
            (2, InterventionType::Pharmaceutical),
            (3, InterventionType::Lifestyle),
        ]);
        assert_ok!(TreatmentProtocol::register_protocol(
            RuntimeOrigin::signed(ALICE),
            pid(151),
            bvec128(b"Branching Protocol"),
            condition(b"HTN"),
            single_modality(TherapeuticModality::Western),
            EvidenceLevel::ExpertOpinion,
            60,
            criteria(b"BP controlled"),
            s,
        ));
        assert_ok!(TreatmentProtocol::initiate_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(151),
        ));

        // Complete step 1
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(151),
            1,
        ));

        // Milestone not met → skip step 2, jump to step 3 via modify
        assert_ok!(TreatmentProtocol::evaluate_milestone(
            RuntimeOrigin::signed(CHARLIE),
            BOB,
            pid(151),
            1,
            false, // target not met
        ));
        assert_ok!(TreatmentProtocol::modify_protocol(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(151),
            3, // skip to step 3
        ));

        let exec = ActiveTreatments::<Test>::get(BOB, pid(151)).unwrap();
        assert_eq!(exec.current_step, 3);
    });
}

#[test]
fn integration_adverse_event_reported_during_treatment() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_3step_treatment(pid(152));

        // Record step 1
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(152),
            1,
        ));

        // Step 2 causes adverse event
        assert_ok!(TreatmentProtocol::report_adverse_event(
            RuntimeOrigin::signed(CHARLIE),
            BOB,
            pid(152),
            bvec256(b"Severe dizziness during herbal treatment"),
        ));

        // Event logged, treatment still active
        let exec = ActiveTreatments::<Test>::get(BOB, pid(152)).unwrap();
        assert_eq!(exec.status, TreatmentExecutionStatus::Active);
        assert_eq!(AdverseEvents::<Test>::get(BOB, pid(152)).len(), 1);
    });
}

#[test]
fn integration_cross_modality_safety_check_before_initiation() {
    new_test_ext().execute_with(|| {
        // Add safety rules to the interaction database
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            substance(b"Warfarin"),
            substance(b"Ginkgo"),
            InteractionSeverity::Contraindicated,
            bvec256(b"Anticoagulant potentiation"),
            bvec256(b"Do not combine"),
        ));

        // Safety check: Warfarin + Ginkgo is blocked
        assert_err!(
            TreatmentProtocol::check_contraindications(
                RuntimeOrigin::signed(ALICE),
                substance(b"Warfarin"),
                substance(b"Ginkgo"),
            ),
            Error::<Test>::InteractionCheckFailed
        );

        // Safety check: Warfarin + Metformin is allowed (no rule)
        assert_ok!(TreatmentProtocol::check_contraindications(
            RuntimeOrigin::signed(ALICE),
            substance(b"Warfarin"),
            substance(b"Metformin"),
        ));
    });
}

#[test]
fn integration_patient_on_concurrent_protocols() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // Register two separate protocols
        register(ALICE, pid(153), EvidenceLevel::ExpertOpinion);
        register(CHARLIE, pid(154), EvidenceLevel::CohortStudy);

        // Start BOB on both simultaneously
        assert_ok!(TreatmentProtocol::initiate_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(153),
        ));
        assert_ok!(TreatmentProtocol::initiate_treatment(
            RuntimeOrigin::signed(CHARLIE),
            BOB,
            pid(154),
        ));

        assert!(ActiveTreatments::<Test>::get(BOB, pid(153)).is_some());
        assert!(ActiveTreatments::<Test>::get(BOB, pid(154)).is_some());
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// EDGE CASES
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn edge_case_protocol_with_many_steps() {
    new_test_ext().execute_with(|| {
        // Create a protocol with 10 steps (up to 64 allowed)
        let many_steps: Vec<TreatmentStep> = (1u32..=10)
            .map(|n| make_step(n, InterventionType::Monitoring))
            .collect();
        let s = BoundedVec::try_from(many_steps).unwrap();
        assert_ok!(TreatmentProtocol::register_protocol(
            RuntimeOrigin::signed(ALICE),
            pid(160),
            bvec128(b"Multi-Step Protocol"),
            condition(b"COND"),
            single_modality(TherapeuticModality::Western),
            EvidenceLevel::ExpertOpinion,
            365,
            criteria(b"Full remission"),
            s,
        ));
        let stored = ProtocolSteps::<Test>::get(pid(160)).unwrap();
        assert_eq!(stored.len(), 10);
    });
}

#[test]
fn edge_case_multiple_interaction_rules_all_checked() {
    new_test_ext().execute_with(|| {
        // Add several rules with different severities
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            substance(b"DrugA"),
            substance(b"HerbA"),
            InteractionSeverity::Minor,
            bvec256(b"Mech"),
            bvec256(b"Rec"),
        ));
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            substance(b"DrugB"),
            substance(b"HerbB"),
            InteractionSeverity::Moderate,
            bvec256(b"Mech"),
            bvec256(b"Rec"),
        ));
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            substance(b"DrugC"),
            substance(b"HerbC"),
            InteractionSeverity::Major,
            bvec256(b"Mech"),
            bvec256(b"Rec"),
        ));
        assert_eq!(NextInteractionRuleId::<Test>::get(), 3);
        // Only DrugC + HerbC is blocked
        assert_ok!(TreatmentProtocol::check_contraindications(
            RuntimeOrigin::signed(ALICE),
            substance(b"DrugA"),
            substance(b"HerbA"),
        ));
        assert_ok!(TreatmentProtocol::check_contraindications(
            RuntimeOrigin::signed(ALICE),
            substance(b"DrugB"),
            substance(b"HerbB"),
        ));
        assert_err!(
            TreatmentProtocol::check_contraindications(
                RuntimeOrigin::signed(ALICE),
                substance(b"DrugC"),
                substance(b"HerbC"),
            ),
            Error::<Test>::InteractionCheckFailed
        );
    });
}

#[test]
fn edge_case_emergency_override_via_modify_to_step_1() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_3step_treatment(pid(161));

        // Advance several steps
        for s in 1u32..=2 {
            assert_ok!(TreatmentProtocol::record_step_completion(
                RuntimeOrigin::signed(ALICE),
                BOB,
                pid(161),
                s,
            ));
        }

        // Emergency: reset to step 1 via modify_protocol
        assert_ok!(TreatmentProtocol::modify_protocol(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(161),
            1,
        ));
        let exec = ActiveTreatments::<Test>::get(BOB, pid(161)).unwrap();
        assert_eq!(exec.current_step, 1);
        assert_eq!(exec.status, TreatmentExecutionStatus::Active);
    });
}

#[test]
fn edge_case_adherence_log_captures_timestamp() {
    new_test_ext().execute_with(|| {
        setup_3step_treatment(pid(162));
        set_block(77);
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(162),
            1,
        ));
        let exec = ActiveTreatments::<Test>::get(BOB, pid(162)).unwrap();
        let (step_num, block_num) = exec.adherence_log[0];
        assert_eq!(step_num, 1);
        assert_eq!(block_num, 77u64);
    });
}

#[test]
fn edge_case_treatment_outcome_success_and_failure_both_stored() {
    new_test_ext().execute_with(|| {
        // Create two protocols so both outcomes can be tested independently
        start_treatment(ALICE, BOB, pid(163));
        start_treatment(ALICE, CHARLIE, pid(164));

        assert_ok!(TreatmentProtocol::complete_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            pid(163),
            true,
            bvec512(b"Success"),
        ));
        assert_ok!(TreatmentProtocol::complete_treatment(
            RuntimeOrigin::signed(ALICE),
            CHARLIE,
            pid(164),
            false,
            bvec512(b"Failure"),
        ));

        assert!(OutcomeTracking::<Test>::get(BOB, pid(163)).unwrap().success);
        assert!(!OutcomeTracking::<Test>::get(CHARLIE, pid(164)).unwrap().success);
    });
}

#[test]
fn edge_case_step_with_medication_stored_correctly() {
    new_test_ext().execute_with(|| {
        let med_step = TreatmentStep {
            step_number: 1,
            intervention_type: InterventionType::Pharmaceutical,
            medication: Some(Medication {
                name: bvec128(b"Metformin 500mg"),
                dosage_ref: bvec64(b"500mg-BID"),
            }),
            herb_formula: None,
            procedure: None,
            duration_days: 30,
            frequency: Frequency { times_per_day: 2, days_per_week: 7 },
            prerequisites: BoundedVec::default(),
            success_criteria: Some(MilestoneCheck {
                metric: bvec64(b"HbA1c"),
                target_value: bvec64(b"<7%"),
            }),
            next_step_conditions: BoundedVec::default(),
        };
        let s = BoundedVec::try_from(vec![med_step]).unwrap();
        assert_ok!(TreatmentProtocol::register_protocol(
            RuntimeOrigin::signed(ALICE),
            pid(165),
            bvec128(b"Metformin Protocol"),
            condition(b"T2DM"),
            single_modality(TherapeuticModality::Western),
            EvidenceLevel::RandomizedControlled,
            90,
            criteria(b"HbA1c < 7%"),
            s,
        ));
        let stored = ProtocolSteps::<Test>::get(pid(165)).unwrap();
        let med = stored[0].medication.as_ref().unwrap();
        assert_eq!(med.name, bvec128(b"Metformin 500mg"));
        assert_eq!(stored[0].success_criteria.as_ref().unwrap().metric, bvec64(b"HbA1c"));
    });
}

#[test]
fn edge_case_herb_formula_stored_in_botanical_step() {
    new_test_ext().execute_with(|| {
        let herb_step = TreatmentStep {
            step_number: 1,
            intervention_type: InterventionType::Botanical,
            medication: None,
            herb_formula: Some(HerbFormula {
                name: bvec128(b"Huang Qi Formula"),
                components_ref: bvec256(b"Astragalus+Licorice+Ginger"),
            }),
            procedure: None,
            duration_days: 28,
            frequency: Frequency { times_per_day: 3, days_per_week: 7 },
            prerequisites: BoundedVec::default(),
            success_criteria: None,
            next_step_conditions: BoundedVec::default(),
        };
        let s = BoundedVec::try_from(vec![herb_step]).unwrap();
        assert_ok!(TreatmentProtocol::register_protocol(
            RuntimeOrigin::signed(ALICE),
            pid(166),
            bvec128(b"TCM Immune Protocol"),
            condition(b"IMMUNO"),
            single_modality(TherapeuticModality::TCM),
            EvidenceLevel::TraditionalKnowledge,
            28,
            criteria(b"Symptom reduction"),
            s,
        ));
        let stored = ProtocolSteps::<Test>::get(pid(166)).unwrap();
        let herb = stored[0].herb_formula.as_ref().unwrap();
        assert_eq!(herb.name, bvec128(b"Huang Qi Formula"));
    });
}

#[test]
fn edge_case_protocol_with_prerequisite_step() {
    new_test_ext().execute_with(|| {
        let prereq_step = TreatmentStep {
            step_number: 2,
            intervention_type: InterventionType::Monitoring,
            medication: None,
            herb_formula: None,
            procedure: None,
            duration_days: 7,
            frequency: Frequency { times_per_day: 1, days_per_week: 7 },
            prerequisites: BoundedVec::try_from(vec![Prerequisite {
                step_number: 1,
                condition_met: true,
            }]).unwrap(),
            success_criteria: None,
            next_step_conditions: BoundedVec::default(),
        };
        let base_step = make_step(1, InterventionType::Pharmaceutical);
        let s = BoundedVec::try_from(vec![base_step, prereq_step]).unwrap();
        assert_ok!(TreatmentProtocol::register_protocol(
            RuntimeOrigin::signed(ALICE),
            pid(167),
            bvec128(b"Prereq Protocol"),
            condition(b"COND"),
            single_modality(TherapeuticModality::Western),
            EvidenceLevel::ExpertOpinion,
            14,
            criteria(b"Stable"),
            s,
        ));
        let stored = ProtocolSteps::<Test>::get(pid(167)).unwrap();
        assert_eq!(stored[1].prerequisites.len(), 1);
        assert_eq!(stored[1].prerequisites[0].step_number, 1);
    });
}
