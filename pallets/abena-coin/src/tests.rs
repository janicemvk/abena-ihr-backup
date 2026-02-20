//! Tests for ABENA Coin pallet

use crate::mock::*;
use crate::*;
use frame_support::{assert_err, assert_ok};

#[test]
fn mint_works() {
    new_test_ext().execute_with(|| {
        let account = 1u64;
        let amount = 1000u128;

        assert_ok!(AbenaCoin::mint(
            RuntimeOrigin::root(),
            account,
            amount
        ));

        assert_eq!(AbenaCoin::balances(account), amount);
        assert_eq!(AbenaCoin::total_supply(), amount);
    });
}

#[test]
fn transfer_works() {
    new_test_ext().execute_with(|| {
        let from = 1u64;
        let to = 2u64;
        let amount = 1000u128;

        assert_ok!(AbenaCoin::mint(
            RuntimeOrigin::root(),
            from,
            amount
        ));

        assert_ok!(AbenaCoin::transfer(
            RuntimeOrigin::signed(from),
            to,
            500u128
        ));

        assert_eq!(AbenaCoin::balances(from), 500u128);
        assert_eq!(AbenaCoin::balances(to), 500u128);
    });
}

#[test]
fn burn_works() {
    new_test_ext().execute_with(|| {
        let account = 1u64;
        let amount = 1000u128;

        assert_ok!(AbenaCoin::mint(
            RuntimeOrigin::root(),
            account,
            amount
        ));

        assert_ok!(AbenaCoin::burn(
            RuntimeOrigin::signed(account),
            300u128
        ));

        assert_eq!(AbenaCoin::balances(account), 700u128);
        assert_eq!(AbenaCoin::total_supply(), 700u128);
    });
}

#[test]
fn transfer_insufficient_balance_fails() {
    new_test_ext().execute_with(|| {
        let from = 1u64;
        let to = 2u64;

        assert_ok!(AbenaCoin::mint(
            RuntimeOrigin::root(),
            from,
            100u128
        ));

        assert_err!(
            AbenaCoin::transfer(
                RuntimeOrigin::signed(from),
                to,
                200u128
            ),
            Error::<Test>::InsufficientBalance
        );
    });
}

#[test]
fn grant_reward_works() {
    new_test_ext().execute_with(|| {
        let account = 1u64;
        let reward_type = RewardType::HealthRecordCreated;
        let amount = 100u128;

        assert_ok!(AbenaCoin::grant_reward(
            RuntimeOrigin::root(),
            account,
            reward_type.clone(),
            amount
        ));

        assert_eq!(AbenaCoin::balances(account), amount);
        assert_eq!(AbenaCoin::total_supply(), amount);

        let history = AbenaCoin::reward_history(account, reward_type);
        assert_eq!(history.len(), 1);
        assert_eq!(history[0].amount, amount);
    });
}

#[test]
fn claim_achievement_works() {
    new_test_ext().execute_with(|| {
        let account = 1u64;
        let achievement = AchievementType::HealthRecordCreator;

        assert_ok!(AbenaCoin::claim_achievement(
            RuntimeOrigin::signed(account),
            achievement.clone()
        ));

        let achievements = AbenaCoin::achievements(account);
        assert_eq!(achievements.total_achievements, 1);
        assert!(achievements.unlocked_achievements.contains(&achievement));
        assert!(AbenaCoin::balances(account) > 0); // Should have received reward
    });
}

#[test]
fn cannot_claim_achievement_twice() {
    new_test_ext().execute_with(|| {
        let account = 1u64;
        let achievement = AchievementType::HealthRecordCreator;

        assert_ok!(AbenaCoin::claim_achievement(
            RuntimeOrigin::signed(account),
            achievement.clone()
        ));

        assert_err!(
            AbenaCoin::claim_achievement(
                RuntimeOrigin::signed(account),
                achievement
            ),
            Error::<Test>::AchievementAlreadyUnlocked
        );
    });
}

