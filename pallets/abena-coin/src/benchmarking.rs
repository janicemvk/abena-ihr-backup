//! Benchmarking for ABENA Coin pallet

use super::*;
use frame_benchmarking::{benchmarks, whitelisted_caller};
use frame_system::RawOrigin;

benchmarks! {
    mint {
        let caller: T::AccountId = whitelisted_caller();
        let amount = 1000u128.into();
    }: _(RawOrigin::Root, caller.clone(), amount)
    verify {
        assert!(Balances::<T>::contains_key(&caller));
    }

    burn {
        let caller: T::AccountId = whitelisted_caller();
        let amount = 1000u128.into();
        Pallet::<T>::mint(RawOrigin::Root.into(), caller.clone(), amount)?;
    }: _(RawOrigin::Signed(caller.clone()), amount)
    verify {
        assert_eq!(Balances::<T>::get(&caller), Zero::zero());
    }

    transfer {
        let from: T::AccountId = whitelisted_caller();
        let to: T::AccountId = frame_benchmarking::account("to", 0, 0);
        let amount = 1000u128.into();
        Pallet::<T>::mint(RawOrigin::Root.into(), from.clone(), amount)?;
    }: _(RawOrigin::Signed(from.clone()), to, amount)
    verify {
        assert_eq!(Balances::<T>::get(&from), Zero::zero());
    }

    grant_reward {
        let account: T::AccountId = whitelisted_caller();
        let reward_type = RewardType::HealthRecordCreated;
        let amount = 100u128.into();
    }: _(RawOrigin::Root, account.clone(), reward_type, amount)
    verify {
        assert!(Balances::<T>::contains_key(&account));
    }

    claim_achievement {
        let caller: T::AccountId = whitelisted_caller();
        let achievement = AchievementType::HealthRecordCreator;
    }: _(RawOrigin::Signed(caller.clone()), achievement)
    verify {
        assert!(Achievements::<T>::contains_key(&caller));
    }

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}

