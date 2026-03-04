//! Benchmarks for the ABENA Fee Management pallet.

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_system::RawOrigin;

const SEED: u32 = 0;

benchmarks! {

    create_subscription {
        let caller: T::AccountId = whitelisted_caller();
    }: _(
        RawOrigin::Signed(caller.clone()),
        1u64,
        SubscriptionPlan::Professional,
        1_000u32.into()
    )
    verify {
        assert!(InstitutionSubscriptions::<T>::contains_key(&caller));
    }

    renew_subscription {
        let caller: T::AccountId = whitelisted_caller();
        Pallet::<T>::create_subscription(
            RawOrigin::Signed(caller.clone()).into(),
            1u64,
            SubscriptionPlan::Basic,
            100u32.into(),
        )?;
    }: _(RawOrigin::Signed(caller.clone()), 200u32.into())
    verify {
        let sub = InstitutionSubscriptions::<T>::get(&caller).unwrap();
        assert_eq!(sub.status, SubscriptionStatus::Active);
    }

    cancel_subscription {
        let caller: T::AccountId = whitelisted_caller();
        Pallet::<T>::create_subscription(
            RawOrigin::Signed(caller.clone()).into(),
            1u64,
            SubscriptionPlan::Basic,
            100u32.into(),
        )?;
    }: _(RawOrigin::Signed(caller.clone()))
    verify {
        assert!(!InstitutionSubscriptions::<T>::contains_key(&caller));
    }

    set_rate_limit {
        let account_type = AccountType::Institution;
    }: _(RawOrigin::Root, account_type, 500u32, 100u32.into())
    verify {
        assert_eq!(RateLimits::<T>::get(account_type).max_requests, 500);
    }

    record_usage {
        let target: T::AccountId = account("target", 0, SEED);
    }: _(RawOrigin::Root, target.clone(), OperationType::Read, 10u32)
    verify {
        let current = frame_system::Pallet::<T>::block_number();
        assert!(UsageRecords::<T>::contains_key(&target, current));
    }

    check_rate_limit {
        let caller: T::AccountId = whitelisted_caller();
        // Set a generous limit so it passes
        Pallet::<T>::set_rate_limit(
            RawOrigin::Root.into(),
            AccountType::Patient,
            10_000u32,
            1_000u32.into(),
        )?;
    }: _(RawOrigin::Signed(caller.clone()), AccountType::Patient)
    verify {}

    distribute_validator_reward {
        let validator: T::AccountId = account("validator", 0, SEED);
        let amount: BalanceOf<T> = 1_000u32.into();
    }: _(RawOrigin::Root, validator.clone(), amount)
    verify {
        assert_eq!(ValidatorRewards::<T>::get(&validator), amount);
    }

    claim_validator_rewards {
        let validator: T::AccountId = whitelisted_caller();
        let amount: BalanceOf<T> = 5_000u32.into();
        Pallet::<T>::distribute_validator_reward(
            RawOrigin::Root.into(),
            validator.clone(),
            amount,
        )?;
    }: _(RawOrigin::Signed(validator.clone()))
    verify {
        use frame_support::traits::Zero;
        assert!(ValidatorRewards::<T>::get(&validator).is_zero());
    }

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}
