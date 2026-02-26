//! Benchmarks for pallet-treatment-protocol.
//!
//! Targets:
//!   register_protocol        – baseline: register a new protocol with 1 step
//!   register_protocol_steps  – worst-case: register protocol with s steps (linear)
//!   initiate_treatment       – start a patient on an existing protocol
//!   add_interaction_rule     – add one interaction rule (Root call)
//!   check_contraindications  – worst-case: iterate r rules, no match (linear)
//!   evaluate_milestone       – evaluate a milestone on an active treatment
//!   record_step_completion   – record completion of a treatment step
//!   complete_treatment       – finalize a running treatment
//!   report_adverse_event     – report adverse event on active treatment

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_system::RawOrigin;
use sp_runtime::traits::Hash as HashTrait;

const SEED: u32 = 0;

fn make_hash<T: Config>(seed: u32) -> T::Hash {
    let mut b = [0u8; 32];
    b[0..4].copy_from_slice(&seed.to_le_bytes());
    T::Hashing::hash(&b)
}

fn bounded_str(s: &[u8]) -> BoundedVec<u8, ConstU32<128>> {
    BoundedVec::truncate_from(s.to_vec())
}

fn bounded_str_256(s: &[u8]) -> BoundedVec<u8, ConstU32<256>> {
    BoundedVec::truncate_from(s.to_vec())
}

fn bounded_str_512(s: &[u8]) -> BoundedVec<u8, ConstU32<512>> {
    BoundedVec::truncate_from(s.to_vec())
}

fn condition() -> ClinicalCondition {
    ClinicalCondition {
        code: BoundedVec::truncate_from(b"T2DM".to_vec()),
        description: BoundedVec::truncate_from(b"Type-2 Diabetes Mellitus".to_vec()),
    }
}

fn success_criteria() -> SuccessCriteria {
    SuccessCriteria {
        description: BoundedVec::truncate_from(b"HbA1c < 7%".to_vec()),
        measurable: true,
    }
}

fn one_step() -> TreatmentStep {
    TreatmentStep {
        step_number: 1,
        intervention_type: InterventionType::Pharmaceutical,
        medication: Some(Medication {
            name: BoundedVec::truncate_from(b"Metformin".to_vec()),
            dosage_ref: BoundedVec::truncate_from(b"500mg".to_vec()),
        }),
        herb_formula: None,
        procedure: None,
        duration_days: 90,
        frequency: Frequency { times_per_day: 2, days_per_week: 7 },
        prerequisites: BoundedVec::default(),
        success_criteria: None,
        next_step_conditions: BoundedVec::default(),
    }
}

/// Register a protocol and return its ID.
fn register_protocol_helper<T: Config>(
    caller: T::AccountId,
    seed: u32,
) -> Result<T::Hash, sp_runtime::DispatchError> {
    let protocol_id = make_hash::<T>(seed);
    let steps: BoundedVec<TreatmentStep, ConstU32<64>> =
        BoundedVec::truncate_from(sp_std::vec![one_step()]);
    Pallet::<T>::register_protocol(
        RawOrigin::Signed(caller).into(),
        protocol_id,
        BoundedVec::truncate_from(b"Diabetes Protocol".to_vec()),
        condition(),
        BoundedVec::truncate_from(sp_std::vec![TherapeuticModality::Western]),
        EvidenceLevel::RandomizedControlled,
        180,
        success_criteria(),
        steps,
    )?;
    Ok(protocol_id)
}

/// Insert an active treatment directly into storage.
fn insert_active_treatment<T: Config>(patient: T::AccountId, protocol_id: T::Hash) {
    let now: frame_system::pallet_prelude::BlockNumberFor<T> = 1u32.into();
    ActiveTreatments::<T>::insert(
        &patient,
        &protocol_id,
        TreatmentExecution::<T> {
            patient: patient.clone(),
            protocol_id,
            current_step: 1,
            started_at: now,
            completed_steps: BoundedVec::default(),
            adherence_log: BoundedVec::default(),
            status: TreatmentExecutionStatus::Active,
            outcome: None,
        },
    );
}

benchmarks! {

    // ── register_protocol ─────────────────────────────────────────────────
    // Baseline: register a fresh protocol with a single step.
    register_protocol {
        let caller: T::AccountId = whitelisted_caller();
        let protocol_id = make_hash::<T>(1u32);
        let steps: BoundedVec<TreatmentStep, ConstU32<64>> =
            BoundedVec::truncate_from(sp_std::vec![one_step()]);
    }: _(
        RawOrigin::Signed(caller.clone()),
        protocol_id,
        BoundedVec::truncate_from(b"Protocol Alpha".to_vec()),
        condition(),
        BoundedVec::truncate_from(sp_std::vec![TherapeuticModality::Western]),
        EvidenceLevel::RandomizedControlled,
        90,
        success_criteria(),
        steps
    )
    verify {
        assert!(ProtocolRegistry::<T>::contains_key(protocol_id));
    }

    // ── register_protocol_steps ───────────────────────────────────────────
    // Worst-case: register protocol with s steps (1..64); cost is O(s) for
    // encoding/writing the BoundedVec.
    register_protocol_steps {
        let s in 1 .. 64u32;

        let caller: T::AccountId = whitelisted_caller();
        let protocol_id = make_hash::<T>(2u32);
        let mut step_vec = sp_std::vec::Vec::with_capacity(s as usize);
        for i in 0..s {
            let mut step = one_step();
            step.step_number = i + 1;
            step_vec.push(step);
        }
        let steps: BoundedVec<TreatmentStep, ConstU32<64>> =
            BoundedVec::truncate_from(step_vec);
    }: register_protocol(
        RawOrigin::Signed(caller.clone()),
        protocol_id,
        BoundedVec::truncate_from(b"Big Protocol".to_vec()),
        condition(),
        BoundedVec::truncate_from(sp_std::vec![TherapeuticModality::Integrative]),
        EvidenceLevel::CohortStudy,
        365,
        success_criteria(),
        steps
    )
    verify {
        assert!(ProtocolRegistry::<T>::contains_key(protocol_id));
    }

    // ── initiate_treatment ────────────────────────────────────────────────
    // Start a patient on an already-registered protocol.
    initiate_treatment {
        let provider: T::AccountId = whitelisted_caller();
        let patient: T::AccountId  = account("patient", 0, SEED);
        let protocol_id = register_protocol_helper::<T>(provider.clone(), 10u32)?;
    }: _(RawOrigin::Signed(provider.clone()), patient.clone(), protocol_id)
    verify {
        assert!(ActiveTreatments::<T>::contains_key(&patient, protocol_id));
    }

    // ── add_interaction_rule ──────────────────────────────────────────────
    // Root call; measures a single storage insert.
    add_interaction_rule {
        let substance_a = bounded_str(b"Warfarin");
        let substance_b = bounded_str(b"Ginkgo");
    }: _(
        RawOrigin::Root,
        substance_a.clone(),
        substance_b.clone(),
        InteractionSeverity::Contraindicated,
        bounded_str_256(b"Pharmacodynamic interaction"),
        bounded_str_256(b"Avoid combination")
    )
    verify {
        assert!(NextInteractionRuleId::<T>::get() > 0);
    }

    // ── check_contraindications ───────────────────────────────────────────
    // Worst-case: r rules in the database; queried substances match NONE of them.
    // Uses query_interaction extrinsic which iterates all rules (O(r)).
    check_contraindications {
        let r in 1 .. 200u32;

        // Populate r rules between distinct substance pairs.
        // Build unique names by encoding the index directly into a fixed-width buffer.
        for i in 0..r {
            let mut name_a = [b'A'; 8]; // "DrugXXXX"
            let ib = i.to_le_bytes();
            name_a[4] = ib[0]; name_a[5] = ib[1]; name_a[6] = ib[2]; name_a[7] = ib[3];
            let mut name_b = [b'H'; 8]; // "HerbXXXX"
            name_b[4] = ib[0]; name_b[5] = ib[1]; name_b[6] = ib[2]; name_b[7] = ib[3];
            let sub_a: BoundedVec<u8, ConstU32<128>> =
                BoundedVec::truncate_from(name_a.to_vec());
            let sub_b: BoundedVec<u8, ConstU32<128>> =
                BoundedVec::truncate_from(name_b.to_vec());
            InteractionDatabase::<T>::insert(
                i,
                InteractionRule {
                    rule_id: i,
                    substance_a: sub_a,
                    substance_b: sub_b,
                    severity: InteractionSeverity::Moderate,
                    mechanism: bounded_str_256(b"Unknown"),
                    recommendation: bounded_str_256(b"Monitor"),
                },
            );
        }
        NextInteractionRuleId::<T>::put(r);

        let caller: T::AccountId = whitelisted_caller();
        // Substances that will NOT match any stored rule → full iteration.
        let no_match_a = bounded_str(b"SafeDrugA");
        let no_match_b = bounded_str(b"SafeDrugB");
    }: query_interaction(RawOrigin::Signed(caller.clone()), no_match_a.clone(), no_match_b.clone())
    verify {
        // If Ok(()), no contraindication was found (expected).
    }

    // ── evaluate_milestone ────────────────────────────────────────────────
    // Complex protocol: active treatment with n completed steps logged.
    evaluate_milestone {
        let n in 1 .. 64u32;

        let provider: T::AccountId = whitelisted_caller();
        let patient: T::AccountId  = account("patient", 0, SEED);
        let protocol_id = register_protocol_helper::<T>(provider.clone(), 20u32)?;
        insert_active_treatment::<T>(patient.clone(), protocol_id);

        // Log n completed steps (to simulate adherence_log size).
        ActiveTreatments::<T>::mutate(&patient, &protocol_id, |exec| {
            if let Some(ref mut ex) = exec {
                for i in 0..n {
                    let _ = ex.completed_steps.try_push(i + 1);
                }
            }
        });
    }: _(RawOrigin::Signed(provider.clone()), patient.clone(), protocol_id, n, true)
    verify {
        // MilestoneEvaluated event was deposited.
    }

    // ── record_step_completion ────────────────────────────────────────────
    // Mark the current step complete and advance the treatment.
    record_step_completion {
        let provider: T::AccountId = whitelisted_caller();
        let patient: T::AccountId  = account("patient", 0, SEED);
        let protocol_id = register_protocol_helper::<T>(provider.clone(), 30u32)?;
        Pallet::<T>::initiate_treatment(
            RawOrigin::Signed(provider.clone()).into(),
            patient.clone(),
            protocol_id,
        )?;
    }: _(
        RawOrigin::Signed(provider.clone()),
        patient.clone(),
        protocol_id,
        1u32
    )
    verify {
        let exec = ActiveTreatments::<T>::get(&patient, protocol_id)
            .expect("treatment must exist");
        assert!(exec.completed_steps.contains(&1u32));
    }

    // ── complete_treatment ────────────────────────────────────────────────
    // Finalize an active treatment and record the final outcome.
    complete_treatment {
        let provider: T::AccountId = whitelisted_caller();
        let patient: T::AccountId  = account("patient", 0, SEED);
        let protocol_id = register_protocol_helper::<T>(provider.clone(), 40u32)?;
        insert_active_treatment::<T>(patient.clone(), protocol_id);
    }: _(
        RawOrigin::Signed(provider.clone()),
        patient.clone(),
        protocol_id,
        true,
        bounded_str_512(b"Treatment successful")
    )
    verify {
        let exec = ActiveTreatments::<T>::get(&patient, protocol_id)
            .expect("treatment must still be in storage");
        assert_eq!(exec.status, TreatmentExecutionStatus::Completed);
    }

    // ── report_adverse_event ──────────────────────────────────────────────
    // Report an adverse event on an active treatment.
    report_adverse_event {
        let provider: T::AccountId = whitelisted_caller();
        let patient: T::AccountId  = account("patient", 0, SEED);
        let protocol_id = register_protocol_helper::<T>(provider.clone(), 50u32)?;
        insert_active_treatment::<T>(patient.clone(), protocol_id);
        let description: BoundedVec<u8, ConstU32<256>> =
            BoundedVec::truncate_from(b"Nausea and dizziness".to_vec());
    }: _(
        RawOrigin::Signed(provider.clone()),
        patient.clone(),
        protocol_id,
        description
    )
    verify {
        // AdverseEventReported event emitted.
    }

    impl_benchmark_test_suite!(
        Pallet,
        crate::mock::new_test_ext(),
        crate::mock::Test,
    );
}
