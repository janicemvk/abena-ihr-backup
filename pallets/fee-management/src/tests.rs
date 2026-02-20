//! Tests for fee management pallet

use crate::{mock::*, *};
use frame_support::{assert_noop, assert_ok};

#[test]
fn create_subscription_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1),
            1,
            SubscriptionPlan::Basic,
            1000
        ));
    });
}

#[test]
fn renew_subscription_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1),
            1,
            SubscriptionPlan::Basic,
            1000
        ));
        assert_ok!(FeeManagement::renew_subscription(
            RuntimeOrigin::signed(1),
            500
        ));
    });
}

#[test]
fn cancel_subscription_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::create_subscription(
            RuntimeOrigin::signed(1),
            1,
            SubscriptionPlan::Basic,
            1000
        ));
        assert_ok!(FeeManagement::cancel_subscription(RuntimeOrigin::signed(1)));
    });
}

#[test]
fn set_rate_limit_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::set_rate_limit(
            RuntimeOrigin::root(),
            AccountType::Patient,
            100,
            100
        ));
    });
}

#[test]
fn record_usage_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::record_usage(
            RuntimeOrigin::root(),
            1,
            OperationType::Read,
            10
        ));
    });
}

#[test]
fn distribute_validator_reward_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FeeManagement::distribute_validator_reward(
            RuntimeOrigin::root(),
            1,
            1000
        ));
    });
}

