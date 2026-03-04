//! Benchmarks for the ABENA Governance pallet.

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_system::RawOrigin;

const SEED: u32 = 0;

benchmarks! {

    // ── create_guideline_proposal ────────────────────────────────────────────
    create_guideline_proposal {
        let caller: T::AccountId = whitelisted_caller();
        let content = vec![b'A'; 256];
    }: _(
        RawOrigin::Signed(caller.clone()),
        1u64,
        content,
        100u32.into()
    )
    verify {
        assert!(GuidelineProposals::<T>::contains_key(1u64));
    }

    // ── create_protocol_proposal ─────────────────────────────────────────────
    create_protocol_proposal {
        let caller: T::AccountId = whitelisted_caller();
        let content = vec![b'P'; 256];
    }: _(
        RawOrigin::Signed(caller.clone()),
        2u64,
        content,
        100u32.into()
    )
    verify {
        assert!(ProtocolProposals::<T>::contains_key(2u64));
    }

    // ── cast_vote ────────────────────────────────────────────────────────────
    cast_vote {
        let caller: T::AccountId   = whitelisted_caller();
        let voter: T::AccountId    = account("voter", 0, SEED);
        let voter_key              = voter.clone();

        Pallet::<T>::create_guideline_proposal(
            RawOrigin::Signed(caller.clone()).into(),
            10u64,
            b"Clinical guideline benchmark".to_vec(),
            1_000u32.into(),
        )?;
    }: _(RawOrigin::Signed(voter), 10u64, Vote::Approve)
    verify {
        assert!(Votes::<T>::contains_key(10u64, &voter_key));
    }

    // ── execute_emergency_intervention ───────────────────────────────────────
    execute_emergency_intervention {
        let executor: T::AccountId = whitelisted_caller();
        let reason = vec![b'R'; 128];
    }: _(
        RawOrigin::Signed(executor.clone()),
        1u64,
        EmergencyInterventionType::SuspendProtocol,
        reason
    )
    verify {
        assert!(EmergencyInterventions::<T>::contains_key(1u64));
    }

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}
