//! Benchmarks for consortium governance pallet

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_system::RawOrigin;
use sp_runtime::BoundedVec;

const SEED: u32 = 0;

benchmarks! {
    register_consortium_member {
        let org_id = T::Hash::default();
        let rep: T::AccountId = account("rep", 0, SEED);
        let reps = BoundedVec::try_from(vec![rep]).unwrap();
    }: _(RawOrigin::Root, org_id, OrgType::Hospital, 10u32, reps)
    verify {
        assert!(ConsortiumMembers::<T>::contains_key(&org_id));
    }

    remove_consortium_member {
        let org_id = T::Hash::default();
        let rep: T::AccountId = account("rep", 0, SEED);
        let reps = BoundedVec::try_from(vec![rep]).unwrap();
        Pallet::<T>::register_consortium_member(
            RawOrigin::Root.into(),
            org_id,
            OrgType::Hospital,
            10u32,
            reps,
        ).unwrap();
    }: _(RawOrigin::Root, org_id)
    verify {
        assert!(!ConsortiumMembers::<T>::contains_key(&org_id));
    }

    propose {
        let org_id = T::Hash::default();
        let rep: T::AccountId = whitelisted_caller();
        let reps = BoundedVec::try_from(vec![rep.clone()]).unwrap();
        Pallet::<T>::register_consortium_member(
            RawOrigin::Root.into(),
            org_id,
            OrgType::Hospital,
            10u32,
            reps,
        ).unwrap();
        let call =
            frame_system::Call::<T>::remark { remark: vec![0u8; 32] }.into();
        let call_bounded = BoundedVec::<u8, crate::MaxProposalCallLen>::try_from(
            codec::Encode::encode(&call),
        )
        .unwrap();
    }: _(RawOrigin::Signed(rep), call_bounded, ProposalPriority::Normal)
    verify {
        assert!(Proposals::<T>::get(0).is_some());
    }

    vote {
        let org_id = T::Hash::default();
        let rep: T::AccountId = whitelisted_caller();
        let reps = BoundedVec::try_from(vec![rep.clone()]).unwrap();
        Pallet::<T>::register_consortium_member(
            RawOrigin::Root.into(),
            org_id,
            OrgType::Hospital,
            10u32,
            reps,
        ).unwrap();
        let call = frame_system::Call::<T>::remark { remark: vec![0u8; 32] }
            .into();
        let call_bounded = BoundedVec::<u8, crate::MaxProposalCallLen>::try_from(
            codec::Encode::encode(&call),
        )
        .unwrap();
        Pallet::<T>::propose(RawOrigin::Signed(rep.clone()).into(), call_bounded, ProposalPriority::Normal)
            .unwrap();
    }: _(RawOrigin::Signed(rep), 0u64, true)
    verify {
        assert!(Votes::<T>::get(0u64, &rep).is_some());
    }

    close_and_execute {
        let org_id = T::Hash::default();
        let rep: T::AccountId = whitelisted_caller();
        let reps = BoundedVec::try_from(vec![rep.clone()]).unwrap();
        Pallet::<T>::register_consortium_member(
            RawOrigin::Root.into(),
            org_id,
            OrgType::Hospital,
            10u32,
            reps,
        ).unwrap();
        let call = frame_system::Call::<T>::remark { remark: vec![0u8; 32] }
            .into();
        let call_bounded = BoundedVec::<u8, crate::MaxProposalCallLen>::try_from(
            codec::Encode::encode(&call),
        )
        .unwrap();
        Pallet::<T>::propose(RawOrigin::Signed(rep.clone()).into(), call_bounded, ProposalPriority::Normal)
            .unwrap();
        Pallet::<T>::vote(RawOrigin::Signed(rep).into(), 0u64, true).unwrap();
        frame_system::Pallet::<T>::set_block_number(T::VotingPeriod::get().into() + 1u32.into());
    }: _(RawOrigin::Signed(account("closer", 1, SEED)), 0u64)
    verify {
        let p = Proposals::<T>::get(0).unwrap();
        assert!(matches!(p.status, ProposalStatus::Executed));
    }

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}
