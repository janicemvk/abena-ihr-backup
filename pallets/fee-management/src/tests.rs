//! Comprehensive tests for the ABENA Fee Management pallet.

use crate::{mock::*, *};
use frame_support::{assert_err, assert_ok};

// ── create_subscription ──────────────────────────────────────────────────────

#[test]
fn create_subscription_basic_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1), 1u64, SubscriptionPlan::Basic, 1_000
        ));
        assert!(InstitutionSubscriptions::<Test>::contains_key(1u64));
    });
}

#[test]
fn create_subscription_professional_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1), 2u64, SubscriptionPlan::Professional, 500
        ));
        let sub = InstitutionSubscriptions::<Test>::get(1u64).unwrap();
        assert_eq!(sub.plan, SubscriptionPlan::Professional);
    });
}

#[test]
fn create_subscription_enterprise_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1), 3u64, SubscriptionPlan::Enterprise, 100
        ));
        assert_eq!(
            InstitutionSubscriptions::<Test>::get(1u64).unwrap().plan,
            SubscriptionPlan::Enterprise
        );
    });
}

#[test]
fn create_subscription_fails_if_already_exists() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1), 1u64, SubscriptionPlan::Basic, 100
        ));
        assert_err!(
            FeeManagement::create_subscription(
                RuntimeOrigin::signed(1), 2u64, SubscriptionPlan::Professional, 100
            ),
            Error::<Test>::SubscriptionAlreadyExists
        );
    });
}

#[test]
fn create_subscription_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1), 42u64, SubscriptionPlan::Basic, 100
        ));
        System::assert_has_event(RuntimeEvent::FeeManagement(
            Event::SubscriptionCreated {
                institution: 1,
                subscription_id: 42,
                plan: SubscriptionPlan::Basic,
            }
        ));
    });
}

#[test]
fn create_subscription_sets_active_status() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1), 1u64, SubscriptionPlan::Basic, 100
        ));
        let sub = InstitutionSubscriptions::<Test>::get(1u64).unwrap();
        assert_eq!(sub.status, SubscriptionStatus::Active);
    });
}

// ── renew_subscription ───────────────────────────────────────────────────────

#[test]
fn renew_subscription_extends_end_block() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1), 1u64, SubscriptionPlan::Basic, 100
        ));
        let original_end = InstitutionSubscriptions::<Test>::get(1u64).unwrap().end_block;
        assert_ok!(FeeManagement::renew_subscription(RuntimeOrigin::signed(1), 200));
        let new_end = InstitutionSubscriptions::<Test>::get(1u64).unwrap().end_block;
        assert!(new_end > original_end);
    });
}

#[test]
fn renew_subscription_fails_if_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            FeeManagement::renew_subscription(RuntimeOrigin::signed(99), 100),
            Error::<Test>::SubscriptionNotFound
        );
    });
}

#[test]
fn renew_subscription_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1), 1u64, SubscriptionPlan::Basic, 100
        ));
        assert_ok!(FeeManagement::renew_subscription(RuntimeOrigin::signed(1), 100));
        System::assert_has_event(RuntimeEvent::FeeManagement(
            Event::SubscriptionRenewed { institution: 1, subscription_id: 1 }
        ));
    });
}

// ── cancel_subscription ──────────────────────────────────────────────────────

#[test]
fn cancel_subscription_removes_entry() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1), 1u64, SubscriptionPlan::Basic, 100
        ));
        assert_ok!(FeeManagement::cancel_subscription(RuntimeOrigin::signed(1)));
        assert!(!InstitutionSubscriptions::<Test>::contains_key(1u64));
    });
}

#[test]
fn cancel_subscription_fails_if_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            FeeManagement::cancel_subscription(RuntimeOrigin::signed(99)),
            Error::<Test>::SubscriptionNotFound
        );
    });
}

#[test]
fn cancel_subscription_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1), 5u64, SubscriptionPlan::Professional, 50
        ));
        assert_ok!(FeeManagement::cancel_subscription(RuntimeOrigin::signed(1)));
        System::assert_has_event(RuntimeEvent::FeeManagement(
            Event::SubscriptionCancelled { institution: 1, subscription_id: 5 }
        ));
    });
}

// ── set_rate_limit ───────────────────────────────────────────────────────────

#[test]
fn set_rate_limit_requires_root() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::set_rate_limit(
            RuntimeOrigin::root(), AccountType::Patient, 100, 10
        ));
        let rl = RateLimits::<Test>::get(AccountType::Patient);
        assert_eq!(rl.max_requests, 100);
    });
}

#[test]
fn set_rate_limit_fails_for_non_root() {
    new_test_ext().execute_with(|| {
        assert!(FeeManagement::set_rate_limit(
            RuntimeOrigin::signed(1), AccountType::Patient, 100, 10
        ).is_err());
    });
}

#[test]
fn set_rate_limit_all_account_types() {
    new_test_ext().execute_with(|| {
        for (atype, max) in [
            (AccountType::Patient, 50u32),
            (AccountType::Provider, 200),
            (AccountType::Institution, 1000),
        ] {
            assert_ok!(FeeManagement::set_rate_limit(
                RuntimeOrigin::root(), atype, max, 100
            ));
            assert_eq!(RateLimits::<Test>::get(atype).max_requests, max);
        }
    });
}

#[test]
fn set_rate_limit_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::set_rate_limit(
            RuntimeOrigin::root(), AccountType::Institution, 500, 50
        ));
        System::assert_has_event(RuntimeEvent::FeeManagement(
            Event::RateLimitUpdated {
                account_type: AccountType::Institution,
                rate_limit: RateLimit { max_requests: 500, time_window_blocks: 50 },
            }
        ));
    });
}

// ── record_usage ─────────────────────────────────────────────────────────────

#[test]
fn record_usage_stores_read_operations() {
    new_test_ext().execute_with(|| {
        System::set_block_number(5);
        assert_ok!(FeeManagement::record_usage(
            RuntimeOrigin::root(), 1, OperationType::Read, 10
        ));
        let rec = UsageRecords::<Test>::get(1u64, 5u64).unwrap();
        assert_eq!(rec.operations_by_type.reads, 10);
        assert_eq!(rec.total_operations, 10);
    });
}

#[test]
fn record_usage_stores_write_operations() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        assert_ok!(FeeManagement::record_usage(
            RuntimeOrigin::root(), 1, OperationType::Write, 5
        ));
        let rec = UsageRecords::<Test>::get(1u64, 1u64).unwrap();
        assert_eq!(rec.operations_by_type.writes, 5);
    });
}

#[test]
fn record_usage_stores_query_operations() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        assert_ok!(FeeManagement::record_usage(
            RuntimeOrigin::root(), 1, OperationType::Query, 3
        ));
        let rec = UsageRecords::<Test>::get(1u64, 1u64).unwrap();
        assert_eq!(rec.operations_by_type.queries, 3);
    });
}

#[test]
fn record_usage_accumulates_on_same_block() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        assert_ok!(FeeManagement::record_usage(RuntimeOrigin::root(), 1, OperationType::Read, 3));
        assert_ok!(FeeManagement::record_usage(RuntimeOrigin::root(), 1, OperationType::Read, 7));
        let rec = UsageRecords::<Test>::get(1u64, 1u64).unwrap();
        assert_eq!(rec.total_operations, 10);
        assert_eq!(rec.operations_by_type.reads, 10);
    });
}

#[test]
fn record_usage_fails_for_non_root() {
    new_test_ext().execute_with(|| {
        assert!(FeeManagement::record_usage(
            RuntimeOrigin::signed(1), 1, OperationType::Read, 1
        ).is_err());
    });
}

#[test]
fn record_usage_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::record_usage(
            RuntimeOrigin::root(), 2, OperationType::Write, 8
        ));
        System::assert_has_event(RuntimeEvent::FeeManagement(
            Event::UsageRecorded { account: 2, operation_type: OperationType::Write, count: 8 }
        ));
    });
}

// ── distribute_validator_reward ──────────────────────────────────────────────

#[test]
fn distribute_validator_reward_accumulates() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::distribute_validator_reward(
            RuntimeOrigin::root(), 2, 5_000
        ));
        assert_ok!(FeeManagement::distribute_validator_reward(
            RuntimeOrigin::root(), 2, 3_000
        ));
        assert_eq!(ValidatorRewards::<Test>::get(2u64), 8_000);
    });
}

#[test]
fn distribute_validator_reward_fails_for_non_root() {
    new_test_ext().execute_with(|| {
        assert!(FeeManagement::distribute_validator_reward(
            RuntimeOrigin::signed(1), 2, 1_000
        ).is_err());
    });
}

#[test]
fn distribute_validator_reward_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::distribute_validator_reward(
            RuntimeOrigin::root(), 3, 10_000
        ));
        System::assert_has_event(RuntimeEvent::FeeManagement(
            Event::ValidatorRewardDistributed { validator: 3, amount: 10_000 }
        ));
    });
}

#[test]
fn distribute_validator_reward_updates_total() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::distribute_validator_reward(RuntimeOrigin::root(), 1, 100));
        assert_ok!(FeeManagement::distribute_validator_reward(RuntimeOrigin::root(), 2, 200));
        assert_eq!(TotalRewardsDistributed::<Test>::get(), 300);
    });
}

// ── claim_validator_rewards ──────────────────────────────────────────────────

#[test]
fn claim_validator_rewards_mints_tokens() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::distribute_validator_reward(
            RuntimeOrigin::root(), 1, 50_000
        ));
        assert_ok!(FeeManagement::claim_validator_rewards(RuntimeOrigin::signed(1)));
        // After claim, the stored reward should be zero
        assert_eq!(ValidatorRewards::<Test>::get(1u64), 0);
    });
}

#[test]
fn claim_validator_rewards_zero_is_noop() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::claim_validator_rewards(RuntimeOrigin::signed(1)));
        assert_eq!(ValidatorRewards::<Test>::get(1u64), 0);
    });
}

// ── integration ──────────────────────────────────────────────────────────────

#[test]
fn integration_subscription_with_rate_limiting() {
    new_test_ext().execute_with(|| {
        // Create subscription
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1), 1u64, SubscriptionPlan::Enterprise, 1_000
        ));
        // Set rate limit for institutions
        assert_ok!(FeeManagement::set_rate_limit(
            RuntimeOrigin::root(), AccountType::Institution, 1000, 100
        ));
        // Record usage
        assert_ok!(FeeManagement::record_usage(
            RuntimeOrigin::root(), 1, OperationType::Read, 50
        ));
        // Renew
        assert_ok!(FeeManagement::renew_subscription(RuntimeOrigin::signed(1), 500));
        let sub = InstitutionSubscriptions::<Test>::get(1u64).unwrap();
        assert_eq!(sub.status, SubscriptionStatus::Active);
    });
}

#[test]
fn integration_validator_reward_lifecycle() {
    new_test_ext().execute_with(|| {
        // Distribute rewards to multiple validators
        assert_ok!(FeeManagement::distribute_validator_reward(RuntimeOrigin::root(), 1, 10_000));
        assert_ok!(FeeManagement::distribute_validator_reward(RuntimeOrigin::root(), 2, 20_000));
        assert_ok!(FeeManagement::distribute_validator_reward(RuntimeOrigin::root(), 3, 30_000));
        assert_eq!(TotalRewardsDistributed::<Test>::get(), 60_000);
        // Validators claim
        assert_ok!(FeeManagement::claim_validator_rewards(RuntimeOrigin::signed(1)));
        assert_ok!(FeeManagement::claim_validator_rewards(RuntimeOrigin::signed(2)));
        assert_eq!(ValidatorRewards::<Test>::get(1u64), 0);
        assert_eq!(ValidatorRewards::<Test>::get(2u64), 0);
        // Validator 3 not yet claimed
        assert_eq!(ValidatorRewards::<Test>::get(3u64), 30_000);
    });
}
