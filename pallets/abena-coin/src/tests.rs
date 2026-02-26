//! Comprehensive test suite for pallet-abena-coin.
//!
//! Coverage:
//!   - Token basics: mint, burn, transfer, approve, transfer_from
//!   - Staking: all four tiers, partial unstake, tier recalculation
//!   - Vesting: schedule creation, cliff enforcement, proportional release
//!   - Patient rewards: pool funding and distribution
//!   - Gamification (legacy): claim_achievement, grant_reward
//!   - Gamification (new): create_achievement, verify_achievement, claim_gamification_achievement
//!   - Streak tracking and bonuses
//!   - Referral system
//!   - Seasonal multipliers
//!   - Fee abstraction: pay_on_behalf
//!   - Governance: proposals, voting, conviction, delegation, execution
//!   - Treasury: collect, allocate, grant lifecycle
//!   - Integration and edge-case tests

use crate::mock::*;
use crate::pallet::{
    AchievementCategory, AchievementDefinitions, AchievementType, Error, Event,
    PatientAchievements, ProposalStatus, ProposalType, Proposals, RewardHistory,
    RewardType, SeasonalMultiplier, StakingTier, StreakTracking, StreakType,
    VoteDirection, Votes, VerificationMethod,
};
use frame_support::{assert_err, assert_ok, BoundedVec, traits::ConstU32};

/// Mint tokens into the abena-coin internal ledger for `account`.
fn mint(account: u64, amount: u128) {
    assert_ok!(AbenaCoin::mint(RuntimeOrigin::root(), account, amount));
}

/// Advance the chain to `n`.
fn set_block(n: u64) {
    System::set_block_number(n);
}

/// Build a short bounded name for achievements.
fn name(s: &str) -> BoundedVec<u8, ConstU32<64>> {
    BoundedVec::try_from(s.as_bytes().to_vec()).expect("name too long")
}

/// Build a short bounded description.
fn desc(s: &str) -> BoundedVec<u8, ConstU32<128>> {
    BoundedVec::try_from(s.as_bytes().to_vec()).expect("desc too long")
}

// ──────────────────────────────────────────────────────────────────────────────
// TOKEN BASICS — mint / burn
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn mint_succeeds_for_root() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 1_000);
        assert_eq!(AbenaCoin::balances(ALICE), 1_000);
        assert_eq!(AbenaCoin::total_supply(), 1_000);
    });
}

#[test]
fn mint_updates_both_balance_and_supply() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 600);
        mint(BOB, 400);
        assert_eq!(AbenaCoin::total_supply(), 1_000);
    });
}

#[test]
fn mint_fails_for_non_root() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::mint(RuntimeOrigin::signed(ALICE), BOB, 100),
            frame_support::error::BadOrigin
        );
    });
}

#[test]
fn mint_fails_for_zero_amount() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::mint(RuntimeOrigin::root(), ALICE, 0),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn mint_respects_supply_cap() {
    new_test_ext().execute_with(|| {
        // Mint right up to the cap first
        assert_ok!(AbenaCoin::mint(RuntimeOrigin::root(), ALICE, SUPPLY_CAP));
        // One more token would exceed cap
        assert_err!(
            AbenaCoin::mint(RuntimeOrigin::root(), BOB, 1),
            Error::<Test>::SupplyCapExceeded
        );
    });
}

#[test]
fn mint_emits_coins_minted_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(AbenaCoin::mint(RuntimeOrigin::root(), ALICE, 500));
        System::assert_last_event(
            Event::<Test>::CoinsMinted { account: ALICE, amount: 500 }.into(),
        );
    });
}

#[test]
fn burn_reduces_balance_and_supply() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 1_000);
        assert_ok!(AbenaCoin::burn(RuntimeOrigin::signed(ALICE), 300));
        assert_eq!(AbenaCoin::balances(ALICE), 700);
        assert_eq!(AbenaCoin::total_supply(), 700);
    });
}

#[test]
fn burn_entire_balance() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 500);
        assert_ok!(AbenaCoin::burn(RuntimeOrigin::signed(ALICE), 500));
        assert_eq!(AbenaCoin::balances(ALICE), 0);
        assert_eq!(AbenaCoin::total_supply(), 0);
    });
}

#[test]
fn burn_fails_for_insufficient_balance() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 100);
        assert_err!(
            AbenaCoin::burn(RuntimeOrigin::signed(ALICE), 200),
            Error::<Test>::InsufficientBalance
        );
    });
}

#[test]
fn burn_fails_for_zero_amount() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 100);
        assert_err!(
            AbenaCoin::burn(RuntimeOrigin::signed(ALICE), 0),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn burn_emits_coins_burned_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        mint(ALICE, 200);
        assert_ok!(AbenaCoin::burn(RuntimeOrigin::signed(ALICE), 50));
        System::assert_last_event(
            Event::<Test>::CoinsBurned { account: ALICE, amount: 50 }.into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// TRANSFERS
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn transfer_moves_tokens_between_accounts() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 1_000);
        assert_ok!(AbenaCoin::transfer(RuntimeOrigin::signed(ALICE), BOB, 400));
        assert_eq!(AbenaCoin::balances(ALICE), 600);
        assert_eq!(AbenaCoin::balances(BOB), 400);
    });
}

#[test]
fn transfer_fails_insufficient_balance() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 100);
        assert_err!(
            AbenaCoin::transfer(RuntimeOrigin::signed(ALICE), BOB, 200),
            Error::<Test>::InsufficientBalance
        );
    });
}

#[test]
fn transfer_fails_to_self() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 500);
        assert_err!(
            AbenaCoin::transfer(RuntimeOrigin::signed(ALICE), ALICE, 100),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn transfer_fails_zero_amount() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 500);
        assert_err!(
            AbenaCoin::transfer(RuntimeOrigin::signed(ALICE), BOB, 0),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn transfer_emits_coins_transferred_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        mint(ALICE, 500);
        assert_ok!(AbenaCoin::transfer(RuntimeOrigin::signed(ALICE), BOB, 200));
        System::assert_last_event(
            Event::<Test>::CoinsTransferred { from: ALICE, to: BOB, amount: 200 }.into(),
        );
    });
}

#[test]
fn transfer_entire_balance() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 777);
        assert_ok!(AbenaCoin::transfer(RuntimeOrigin::signed(ALICE), BOB, 777));
        assert_eq!(AbenaCoin::balances(ALICE), 0);
        assert_eq!(AbenaCoin::balances(BOB), 777);
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// APPROVE / TRANSFER_FROM (ERC-20 delegation)
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn approve_sets_allowance() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::approve(RuntimeOrigin::signed(ALICE), BOB, 300));
        assert_eq!(AbenaCoin::allowance(ALICE, BOB), 300);
    });
}

#[test]
fn approve_overwrites_previous_allowance() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::approve(RuntimeOrigin::signed(ALICE), BOB, 300));
        assert_ok!(AbenaCoin::approve(RuntimeOrigin::signed(ALICE), BOB, 100));
        assert_eq!(AbenaCoin::allowance(ALICE, BOB), 100);
    });
}

#[test]
fn approve_emits_approved_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(AbenaCoin::approve(RuntimeOrigin::signed(ALICE), BOB, 500));
        System::assert_last_event(
            Event::<Test>::Approved { owner: ALICE, spender: BOB, amount: 500 }.into(),
        );
    });
}

#[test]
fn approve_max_allowance() {
    new_test_ext().execute_with(|| {
        let max: u128 = u128::MAX;
        assert_ok!(AbenaCoin::approve(RuntimeOrigin::signed(ALICE), BOB, max));
        assert_eq!(AbenaCoin::allowance(ALICE, BOB), max);
    });
}

#[test]
fn transfer_from_spends_on_behalf() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 1_000);
        assert_ok!(AbenaCoin::approve(RuntimeOrigin::signed(ALICE), BOB, 400));
        assert_ok!(AbenaCoin::transfer_from(
            RuntimeOrigin::signed(BOB),
            ALICE,
            CHARLIE,
            300
        ));
        assert_eq!(AbenaCoin::balances(ALICE), 700);
        assert_eq!(AbenaCoin::balances(CHARLIE), 300);
        assert_eq!(AbenaCoin::allowance(ALICE, BOB), 100); // 400 - 300
    });
}

#[test]
fn transfer_from_fails_insufficient_allowance() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 1_000);
        assert_ok!(AbenaCoin::approve(RuntimeOrigin::signed(ALICE), BOB, 50));
        assert_err!(
            AbenaCoin::transfer_from(RuntimeOrigin::signed(BOB), ALICE, CHARLIE, 200),
            Error::<Test>::InsufficientAllowance
        );
    });
}

#[test]
fn transfer_from_fails_insufficient_owner_balance() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 100);
        assert_ok!(AbenaCoin::approve(RuntimeOrigin::signed(ALICE), BOB, 500));
        assert_err!(
            AbenaCoin::transfer_from(RuntimeOrigin::signed(BOB), ALICE, CHARLIE, 200),
            Error::<Test>::InsufficientBalance
        );
    });
}

#[test]
fn transfer_from_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        mint(ALICE, 500);
        assert_ok!(AbenaCoin::approve(RuntimeOrigin::signed(ALICE), BOB, 200));
        assert_ok!(AbenaCoin::transfer_from(
            RuntimeOrigin::signed(BOB),
            ALICE,
            CHARLIE,
            100
        ));
        System::assert_last_event(
            Event::<Test>::TransferFrom {
                owner: ALICE,
                spender: BOB,
                to: CHARLIE,
                amount: 100,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// STAKING
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn stake_bronze_tier() {
    new_test_ext().execute_with(|| {
        mint(ALICE, BRONZE_MIN);
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(ALICE), BRONZE_MIN));
        assert_eq!(AbenaCoin::balances(ALICE), 0);
        assert_eq!(AbenaCoin::staked_balance(ALICE), BRONZE_MIN);
        assert_eq!(AbenaCoin::staking_tier(ALICE), Some(StakingTier::Bronze));
    });
}

#[test]
fn stake_silver_tier() {
    new_test_ext().execute_with(|| {
        mint(ALICE, SILVER_MIN);
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(ALICE), SILVER_MIN));
        assert_eq!(AbenaCoin::staking_tier(ALICE), Some(StakingTier::Silver));
    });
}

#[test]
fn stake_gold_tier() {
    new_test_ext().execute_with(|| {
        mint(ALICE, GOLD_MIN);
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(ALICE), GOLD_MIN));
        assert_eq!(AbenaCoin::staking_tier(ALICE), Some(StakingTier::Gold));
    });
}

#[test]
fn stake_platinum_tier() {
    new_test_ext().execute_with(|| {
        mint(ALICE, PLATINUM_MIN);
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(ALICE), PLATINUM_MIN));
        assert_eq!(AbenaCoin::staking_tier(ALICE), Some(StakingTier::Platinum));
    });
}

#[test]
fn stake_fails_below_bronze_minimum() {
    new_test_ext().execute_with(|| {
        let below_min = BRONZE_MIN - 1;
        mint(ALICE, BRONZE_MIN);
        assert_err!(
            AbenaCoin::stake(RuntimeOrigin::signed(ALICE), below_min),
            Error::<Test>::StakeBelowMinimum
        );
    });
}

#[test]
fn stake_fails_insufficient_balance() {
    new_test_ext().execute_with(|| {
        mint(ALICE, BRONZE_MIN - 1);
        assert_err!(
            AbenaCoin::stake(RuntimeOrigin::signed(ALICE), BRONZE_MIN),
            Error::<Test>::InsufficientBalance
        );
    });
}

#[test]
fn stake_emits_staked_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        mint(ALICE, BRONZE_MIN);
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(ALICE), BRONZE_MIN));
        System::assert_last_event(
            Event::<Test>::Staked {
                account: ALICE,
                amount: BRONZE_MIN,
                tier: StakingTier::Bronze,
            }
            .into(),
        );
    });
}

#[test]
fn unstake_returns_tokens_to_balance() {
    new_test_ext().execute_with(|| {
        mint(ALICE, BRONZE_MIN);
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(ALICE), BRONZE_MIN));
        assert_ok!(AbenaCoin::unstake(RuntimeOrigin::signed(ALICE), BRONZE_MIN));
        assert_eq!(AbenaCoin::balances(ALICE), BRONZE_MIN);
        assert_eq!(AbenaCoin::staked_balance(ALICE), 0);
        assert_eq!(AbenaCoin::staking_tier(ALICE), None);
    });
}

#[test]
fn unstake_partial_recalculates_tier() {
    new_test_ext().execute_with(|| {
        // Stake at Gold level
        mint(ALICE, GOLD_MIN);
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(ALICE), GOLD_MIN));
        assert_eq!(AbenaCoin::staking_tier(ALICE), Some(StakingTier::Gold));

        // Unstake so remaining balance falls into Silver tier
        let unstake_amount = GOLD_MIN - SILVER_MIN;
        assert_ok!(AbenaCoin::unstake(RuntimeOrigin::signed(ALICE), unstake_amount));
        assert_eq!(AbenaCoin::staking_tier(ALICE), Some(StakingTier::Silver));
        assert_eq!(AbenaCoin::staked_balance(ALICE), SILVER_MIN);
    });
}

#[test]
fn unstake_fails_if_nothing_staked() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::unstake(RuntimeOrigin::signed(ALICE), BRONZE_MIN),
            Error::<Test>::InsufficientStaked
        );
    });
}

#[test]
fn unstake_fails_for_zero_amount() {
    new_test_ext().execute_with(|| {
        mint(ALICE, BRONZE_MIN);
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(ALICE), BRONZE_MIN));
        assert_err!(
            AbenaCoin::unstake(RuntimeOrigin::signed(ALICE), 0),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn unstake_emits_unstaked_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        mint(ALICE, BRONZE_MIN);
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(ALICE), BRONZE_MIN));
        assert_ok!(AbenaCoin::unstake(RuntimeOrigin::signed(ALICE), BRONZE_MIN));
        System::assert_last_event(
            Event::<Test>::Unstaked { account: ALICE, amount: BRONZE_MIN }.into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// VESTING
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn add_vesting_schedule_requires_root() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::add_vesting_schedule(
                RuntimeOrigin::signed(ALICE),
                ALICE,
                1_000,
                0u64.into(),
                10u64.into(),
                100u64.into(),
            ),
            frame_support::error::BadOrigin
        );
    });
}

#[test]
fn add_vesting_schedule_fails_zero_amount() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::add_vesting_schedule(
                RuntimeOrigin::root(),
                ALICE,
                0,
                0u64.into(),
                10u64.into(),
                100u64.into(),
            ),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn add_vesting_schedule_fails_zero_duration() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::add_vesting_schedule(
                RuntimeOrigin::root(),
                ALICE,
                1_000,
                0u64.into(),
                0u64.into(),
                0u64.into(),
            ),
            Error::<Test>::InvalidVestingSchedule
        );
    });
}

#[test]
fn claim_vested_tokens_fails_before_cliff() {
    new_test_ext().execute_with(|| {
        set_block(0);
        // Schedule: start=0, cliff=10, duration=100, total=1000
        assert_ok!(AbenaCoin::add_vesting_schedule(
            RuntimeOrigin::root(),
            ALICE,
            1_000,
            0u64.into(),
            10u64.into(),
            100u64.into(),
        ));
        // At block 5 the cliff hasn't been reached
        set_block(5);
        assert_err!(
            AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)),
            Error::<Test>::NothingToVest
        );
    });
}

#[test]
fn claim_vested_tokens_releases_proportional_amount() {
    new_test_ext().execute_with(|| {
        set_block(0);
        // release_per_block = 1000 / 100 = 10
        assert_ok!(AbenaCoin::add_vesting_schedule(
            RuntimeOrigin::root(),
            ALICE,
            1_000,
            0u64.into(),  // start_block
            10u64.into(), // cliff_duration
            100u64.into(),// vesting_duration
        ));
        // At block 20: cliff_end=10, blocks_elapsed=10 → releasable = 10*10 = 100
        set_block(20);
        assert_ok!(AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)));
        assert_eq!(AbenaCoin::balances(ALICE), 100);
    });
}

#[test]
fn claim_vested_tokens_caps_at_total_amount() {
    new_test_ext().execute_with(|| {
        set_block(0);
        assert_ok!(AbenaCoin::add_vesting_schedule(
            RuntimeOrigin::root(),
            ALICE,
            1_000,
            0u64.into(),
            10u64.into(),
            100u64.into(),
        ));
        // Well past vesting end (block 200)
        set_block(200);
        assert_ok!(AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)));
        // Should receive the full 1000 (capped, not more)
        assert_eq!(AbenaCoin::balances(ALICE), 1_000);
    });
}

#[test]
fn claim_vested_tokens_fails_if_already_fully_claimed() {
    new_test_ext().execute_with(|| {
        set_block(0);
        assert_ok!(AbenaCoin::add_vesting_schedule(
            RuntimeOrigin::root(),
            ALICE,
            1_000,
            0u64.into(),
            10u64.into(),
            100u64.into(),
        ));
        set_block(200);
        assert_ok!(AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)));
        // All released; nothing left
        assert_err!(
            AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)),
            Error::<Test>::NothingToVest
        );
    });
}

#[test]
fn claim_vested_tokens_fails_for_no_schedule() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)),
            Error::<Test>::NoVestingSchedule
        );
    });
}

#[test]
fn claim_vested_tokens_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(0);
        assert_ok!(AbenaCoin::add_vesting_schedule(
            RuntimeOrigin::root(),
            ALICE,
            1_000,
            0u64.into(),
            0u64.into(),  // immediate cliff
            100u64.into(),
        ));
        set_block(10);
        assert_ok!(AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)));
        // 10 blocks * 10 per block = 100
        System::assert_last_event(
            Event::<Test>::VestedTokensClaimed { account: ALICE, amount: 100 }.into(),
        );
    });
}

#[test]
fn vesting_with_immediate_cliff() {
    new_test_ext().execute_with(|| {
        set_block(1);
        // cliff_duration = 0 means tokens are available from start_block
        assert_ok!(AbenaCoin::add_vesting_schedule(
            RuntimeOrigin::root(),
            ALICE,
            500,
            1u64.into(),  // start_block
            0u64.into(),  // no cliff
            50u64.into(), // vesting_duration: 50 blocks, 10 per block
        ));
        set_block(6);
        assert_ok!(AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)));
        // blocks_elapsed = 6 - 1 = 5, release = 5 * (500/50) = 50
        assert_eq!(AbenaCoin::balances(ALICE), 50);
    });
}

#[test]
fn too_many_vesting_schedules_fails() {
    new_test_ext().execute_with(|| {
        for _ in 0..10 {
            assert_ok!(AbenaCoin::add_vesting_schedule(
                RuntimeOrigin::root(),
                ALICE,
                100,
                0u64.into(),
                0u64.into(),
                10u64.into(),
            ));
        }
        assert_err!(
            AbenaCoin::add_vesting_schedule(
                RuntimeOrigin::root(),
                ALICE,
                100,
                0u64.into(),
                0u64.into(),
                10u64.into(),
            ),
            Error::<Test>::TooManyVestingSchedules
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// PATIENT REWARD POOL
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn fund_reward_pool_increases_pool() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::fund_reward_pool(RuntimeOrigin::root(), 50_000));
        assert_eq!(AbenaCoin::reward_pool(), 50_000);
    });
}

#[test]
fn distribute_patient_reward_transfers_from_pool() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::fund_reward_pool(RuntimeOrigin::root(), 10_000));
        assert_ok!(AbenaCoin::distribute_patient_reward(
            RuntimeOrigin::root(),
            ALICE,
            1_000
        ));
        assert_eq!(AbenaCoin::reward_pool(), 9_000);
        assert_eq!(AbenaCoin::balances(ALICE), 1_000);
        assert_eq!(AbenaCoin::lifetime_earnings(ALICE), 1_000);
    });
}

#[test]
fn distribute_patient_reward_fails_when_pool_exhausted() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::fund_reward_pool(RuntimeOrigin::root(), 100));
        assert_err!(
            AbenaCoin::distribute_patient_reward(RuntimeOrigin::root(), ALICE, 200),
            Error::<Test>::RewardPoolExhausted
        );
    });
}

#[test]
fn distribute_patient_reward_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(AbenaCoin::fund_reward_pool(RuntimeOrigin::root(), 5_000));
        assert_ok!(AbenaCoin::distribute_patient_reward(
            RuntimeOrigin::root(),
            ALICE,
            250
        ));
        System::assert_last_event(
            Event::<Test>::PatientRewardDistributed { account: ALICE, amount: 250 }.into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// LEGACY GAMIFICATION — claim_achievement / grant_reward
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn claim_achievement_unlocks_and_grants_reward() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::claim_achievement(
            RuntimeOrigin::signed(ALICE),
            AchievementType::HealthRecordCreator
        ));
        let record = AbenaCoin::achievements(ALICE);
        assert_eq!(record.total_achievements, 1);
        assert!(record.unlocked_achievements.contains(&AchievementType::HealthRecordCreator));
        assert!(AbenaCoin::balances(ALICE) > 0);
    });
}

#[test]
fn claim_achievement_fails_when_already_unlocked() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::claim_achievement(
            RuntimeOrigin::signed(ALICE),
            AchievementType::HealthRecordCreator
        ));
        assert_err!(
            AbenaCoin::claim_achievement(
                RuntimeOrigin::signed(ALICE),
                AchievementType::HealthRecordCreator
            ),
            Error::<Test>::AchievementAlreadyUnlocked
        );
    });
}

#[test]
fn grant_reward_mints_tokens_and_records_history() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::grant_reward(
            RuntimeOrigin::root(),
            ALICE,
            RewardType::DataShared,
            500
        ));
        assert_eq!(AbenaCoin::balances(ALICE), 500);
        let history = RewardHistory::<Test>::get(ALICE, RewardType::DataShared)
            .unwrap_or_default();
        assert_eq!(history.len(), 1);
        assert_eq!(history[0].amount, 500);
    });
}

#[test]
fn grant_reward_emits_reward_granted_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(AbenaCoin::grant_reward(
            RuntimeOrigin::root(),
            ALICE,
            RewardType::QuantumContribution,
            200
        ));
        System::assert_last_event(
            Event::<Test>::RewardGranted {
                account: ALICE,
                reward_type: RewardType::QuantumContribution,
                amount: 200,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// GAMIFICATION MODULE — create_achievement / verify / claim_gamification_achievement
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn create_achievement_requires_root() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::create_achievement(
                RuntimeOrigin::signed(ALICE),
                AchievementCategory::Wellness,
                name("Test"),
                desc("A test achievement"),
                100,
                false,
                BoundedVec::default(),
                VerificationMethod::SelfReported,
            ),
            frame_support::error::BadOrigin
        );
    });
}

#[test]
fn create_achievement_fails_for_empty_name() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::create_achievement(
                RuntimeOrigin::root(),
                AchievementCategory::Wellness,
                BoundedVec::default(), // empty name
                desc("desc"),
                100,
                false,
                BoundedVec::default(),
                VerificationMethod::SelfReported,
            ),
            Error::<Test>::InvalidAchievementDefinition
        );
    });
}

#[test]
fn create_achievement_fails_for_zero_reward() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::create_achievement(
                RuntimeOrigin::root(),
                AchievementCategory::Wellness,
                name("No reward"),
                desc("desc"),
                0, // zero base_reward
                false,
                BoundedVec::default(),
                VerificationMethod::SelfReported,
            ),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn create_achievement_assigns_sequential_ids() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::create_achievement(
            RuntimeOrigin::root(),
            AchievementCategory::Engagement,
            name("First"),
            desc("d"),
            50,
            false,
            BoundedVec::default(),
            VerificationMethod::SelfReported,
        ));
        assert_ok!(AbenaCoin::create_achievement(
            RuntimeOrigin::root(),
            AchievementCategory::Engagement,
            name("Second"),
            desc("d"),
            75,
            false,
            BoundedVec::default(),
            VerificationMethod::SelfReported,
        ));
        assert_eq!(AbenaCoin::next_achievement_id(), 2);
        assert!(AchievementDefinitions::<Test>::get(0).is_some());
        assert!(AchievementDefinitions::<Test>::get(1).is_some());
    });
}

#[test]
fn create_achievement_emits_achievement_created_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(AbenaCoin::create_achievement(
            RuntimeOrigin::root(),
            AchievementCategory::Community,
            name("Community Star"),
            desc("Help others"),
            300,
            true,
            BoundedVec::default(),
            VerificationMethod::SelfReported,
        ));
        System::assert_last_event(
            Event::<Test>::AchievementCreated {
                achievement_id: 0,
                category: AchievementCategory::Community,
                base_reward: 300,
            }
            .into(),
        );
    });
}

fn create_self_reported_achievement(repeatable: bool) -> u32 {
    assert_ok!(AbenaCoin::create_achievement(
        RuntimeOrigin::root(),
        AchievementCategory::Wellness,
        name("Daily Steps"),
        desc("Walk 10k steps"),
        100,
        repeatable,
        BoundedVec::default(),
        VerificationMethod::SelfReported,
    ));
    0u32 // first achievement id
}

fn create_provider_verified_achievement(repeatable: bool) -> u32 {
    assert_ok!(AbenaCoin::create_achievement(
        RuntimeOrigin::root(),
        AchievementCategory::ClinicalOutcome,
        name("Lab Target Met"),
        desc("Provider verified"),
        200,
        repeatable,
        BoundedVec::default(),
        VerificationMethod::ProviderVerified,
    ));
    0u32
}

#[test]
fn claim_gamification_achievement_self_reported_works() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let id = create_self_reported_achievement(true);
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(ALICE),
            id
        ));
        assert!(AbenaCoin::balances(ALICE) >= 100);
        assert_eq!(AbenaCoin::leaderboard_scores(ALICE) as u128, AbenaCoin::balances(ALICE));
    });
}

#[test]
fn claim_gamification_achievement_fails_for_non_existent() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::claim_gamification_achievement(RuntimeOrigin::signed(ALICE), 999),
            Error::<Test>::AchievementNotFound
        );
    });
}

#[test]
fn claim_gamification_non_repeatable_fails_on_second_claim() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let id = create_self_reported_achievement(false);
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(ALICE),
            id
        ));
        set_block(20); // past cooldown
        assert_err!(
            AbenaCoin::claim_gamification_achievement(RuntimeOrigin::signed(ALICE), id),
            Error::<Test>::AchievementAlreadyClaimed
        );
    });
}

#[test]
fn self_report_is_rate_limited() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let id = create_self_reported_achievement(true);
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(ALICE),
            id
        ));
        // Same block — cooldown not elapsed
        assert_err!(
            AbenaCoin::claim_gamification_achievement(RuntimeOrigin::signed(ALICE), id),
            Error::<Test>::SelfReportRateLimited
        );
    });
}

#[test]
fn repeatable_self_reported_allowed_after_cooldown() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let id = create_self_reported_achievement(true);
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(ALICE),
            id
        ));
        // SelfReportCooldownBlocks = 10; advance past it
        set_block(12);
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(ALICE),
            id
        ));
        let status = PatientAchievements::<Test>::get(ALICE, id).unwrap();
        assert_eq!(status.claim_count, 2);
    });
}

#[test]
fn provider_verified_achievement_requires_verify_first() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let id = create_provider_verified_achievement(false);
        // No verify_achievement call → AchievementNotVerified
        assert_err!(
            AbenaCoin::claim_gamification_achievement(RuntimeOrigin::signed(ALICE), id),
            Error::<Test>::AchievementNotVerified
        );
    });
}

#[test]
fn verify_achievement_then_claim_works() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let id = create_provider_verified_achievement(false);
        assert_ok!(AbenaCoin::verify_achievement(
            RuntimeOrigin::root(),
            ALICE,
            id
        ));
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(ALICE),
            id
        ));
        assert!(AbenaCoin::balances(ALICE) >= 200);
    });
}

#[test]
fn verify_achievement_emits_achievement_verified_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let id = create_provider_verified_achievement(false);
        assert_ok!(AbenaCoin::verify_achievement(RuntimeOrigin::root(), ALICE, id));
        System::assert_last_event(
            Event::<Test>::AchievementVerified { account: ALICE, achievement_id: id }.into(),
        );
    });
}

#[test]
fn claim_gamification_achievement_emits_claimed_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let id = create_self_reported_achievement(false);
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(ALICE),
            id
        ));
        // Event contains multiplier_mille = 1000 (no streak bonus yet)
        System::assert_last_event(
            Event::<Test>::GamificationAchievementClaimed {
                account: ALICE,
                achievement_id: id,
                amount: 100,
                multiplier_mille: 1000,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// STREAK BONUSES
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn award_streak_bonus_mints_tokens() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::award_streak_bonus(
            RuntimeOrigin::root(),
            ALICE,
            StreakType::DailyLogin,
            500
        ));
        assert_eq!(AbenaCoin::balances(ALICE), 500);
        assert_eq!(AbenaCoin::lifetime_earnings(ALICE), 500);
    });
}

#[test]
fn award_streak_bonus_requires_root() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::award_streak_bonus(
                RuntimeOrigin::signed(ALICE),
                ALICE,
                StreakType::DailyLogin,
                100
            ),
            frame_support::error::BadOrigin
        );
    });
}

#[test]
fn award_streak_bonus_fails_for_zero_amount() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::award_streak_bonus(
                RuntimeOrigin::root(),
                ALICE,
                StreakType::DailyLogin,
                0
            ),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn update_streak_increments_current_streak() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(AbenaCoin::update_streak(
            RuntimeOrigin::signed(ALICE),
            StreakType::WellnessActivity
        ));
        let info = StreakTracking::<Test>::get(ALICE, StreakType::WellnessActivity).unwrap();
        assert_eq!(info.current_streak, 1);

        // Within one day (7200 blocks): streak should continue
        set_block(100);
        assert_ok!(AbenaCoin::update_streak(
            RuntimeOrigin::signed(ALICE),
            StreakType::WellnessActivity
        ));
        let info2 = StreakTracking::<Test>::get(ALICE, StreakType::WellnessActivity).unwrap();
        assert_eq!(info2.current_streak, 2);
    });
}

#[test]
fn update_streak_resets_after_long_gap() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(AbenaCoin::update_streak(
            RuntimeOrigin::signed(ALICE),
            StreakType::DailyLogin
        ));
        // Gap > 2 days (14400 + 1 blocks) resets streak
        set_block(1 + 7200 * 3);
        assert_ok!(AbenaCoin::update_streak(
            RuntimeOrigin::signed(ALICE),
            StreakType::DailyLogin
        ));
        let info = StreakTracking::<Test>::get(ALICE, StreakType::DailyLogin).unwrap();
        assert_eq!(info.current_streak, 1);
    });
}

#[test]
fn streak_bonus_multiplier_at_7_day_increases_reward() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let id = create_self_reported_achievement(false);

        // Simulate a 7-day streak using StreakTracking directly
        StreakTracking::<Test>::insert(
            ALICE,
            StreakType::DailyLogin,
            crate::pallet::StreakInfo::<Test> {
                current_streak: 7,
                longest_streak: 7,
                last_activity_block: 0u64.into(),
            },
        );

        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(ALICE),
            id
        ));
        // With 7-day streak: multiplier = 1000 + 500 = 1500 → reward = 100 * 1500/1000 = 150
        assert_eq!(AbenaCoin::balances(ALICE), 150);
    });
}

#[test]
fn streak_bonus_multiplier_at_30_days() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let id = create_self_reported_achievement(false);
        StreakTracking::<Test>::insert(
            ALICE,
            StreakType::DailyLogin,
            crate::pallet::StreakInfo::<Test> {
                current_streak: 30,
                longest_streak: 30,
                last_activity_block: 0u64.into(),
            },
        );
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(ALICE),
            id
        ));
        // 30-day streak: +1000 mille → multiplier = 2000 → 100 * 2000/1000 = 200
        assert_eq!(AbenaCoin::balances(ALICE), 200);
    });
}

#[test]
fn streak_bonus_multiplier_at_90_days() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let id = create_self_reported_achievement(false);
        StreakTracking::<Test>::insert(
            ALICE,
            StreakType::DailyLogin,
            crate::pallet::StreakInfo::<Test> {
                current_streak: 90,
                longest_streak: 90,
                last_activity_block: 0u64.into(),
            },
        );
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(ALICE),
            id
        ));
        // 90-day streak: +2000 mille → multiplier = 3000 → 100 * 3000/1000 = 300
        assert_eq!(AbenaCoin::balances(ALICE), 300);
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// REFERRAL SYSTEM
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn register_referral_works() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(AbenaCoin::register_referral(RuntimeOrigin::signed(BOB), ALICE));
        let children = AbenaCoin::referral_children(ALICE).unwrap_or_default();
        assert!(children.contains(&BOB));
        assert_eq!(AbenaCoin::referrer_of(BOB), Some(ALICE));
    });
}

#[test]
fn register_referral_fails_for_self() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::register_referral(RuntimeOrigin::signed(ALICE), ALICE),
            Error::<Test>::CannotReferSelf
        );
    });
}

#[test]
fn register_referral_fails_when_already_set() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::register_referral(RuntimeOrigin::signed(BOB), ALICE));
        assert_err!(
            AbenaCoin::register_referral(RuntimeOrigin::signed(BOB), CHARLIE),
            Error::<Test>::ReferrerAlreadySet
        );
    });
}

#[test]
fn referral_bonus_distributed_on_achievement_claim() {
    new_test_ext().execute_with(|| {
        set_block(1);
        // BOB registers with ALICE as referrer
        assert_ok!(AbenaCoin::register_referral(RuntimeOrigin::signed(BOB), ALICE));
        let id = create_self_reported_achievement(false);
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(BOB),
            id
        ));
        // ALICE should have received a 20 ABENA referral bonus
        let referral_bonus: u128 = 20_000_000_000_000_000_000u128; // 20 * 10^18
        assert_eq!(AbenaCoin::balances(ALICE), referral_bonus);
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SEASONAL MULTIPLIER
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn set_seasonal_multiplier_requires_root() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::set_seasonal_multiplier(
                RuntimeOrigin::signed(ALICE),
                1u64.into(),
                100u64.into(),
                2000
            ),
            frame_support::error::BadOrigin
        );
    });
}

#[test]
fn set_seasonal_multiplier_stores_value() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(AbenaCoin::set_seasonal_multiplier(
            RuntimeOrigin::root(),
            1u64.into(),
            100u64.into(),
            2000
        ));
        assert!(SeasonalMultiplier::<Test>::get().is_some());
    });
}

#[test]
fn seasonal_multiplier_doubles_achievement_reward() {
    new_test_ext().execute_with(|| {
        set_block(10);
        // 2x seasonal multiplier active during blocks 1–100
        assert_ok!(AbenaCoin::set_seasonal_multiplier(
            RuntimeOrigin::root(),
            1u64.into(),
            100u64.into(),
            2000 // 2x
        ));
        let id = create_self_reported_achievement(false);
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(ALICE),
            id
        ));
        // base_reward=100, multiplier=1000 (no streak), seasonal=2000 → effective=2000
        // reward = 100 * 2000 / 1000 = 200
        assert_eq!(AbenaCoin::balances(ALICE), 200);
    });
}

#[test]
fn set_seasonal_multiplier_out_of_range_fails() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::set_seasonal_multiplier(
                RuntimeOrigin::root(),
                1u64.into(),
                100u64.into(),
                6000 // > 5000 (max)
            ),
            Error::<Test>::InvalidAchievementDefinition
        );
        assert_err!(
            AbenaCoin::set_seasonal_multiplier(
                RuntimeOrigin::root(),
                1u64.into(),
                100u64.into(),
                500 // < 1000 (min)
            ),
            Error::<Test>::InvalidAchievementDefinition
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// FEE ABSTRACTION
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn pay_on_behalf_transfers_tokens_to_patient() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 1_000);
        assert_ok!(AbenaCoin::pay_on_behalf(
            RuntimeOrigin::signed(ALICE),
            BOB,
            300
        ));
        assert_eq!(AbenaCoin::balances(ALICE), 700);
        assert_eq!(AbenaCoin::balances(BOB), 300);
    });
}

#[test]
fn pay_on_behalf_fails_insufficient_balance() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 100);
        assert_err!(
            AbenaCoin::pay_on_behalf(RuntimeOrigin::signed(ALICE), BOB, 500),
            Error::<Test>::InsufficientBalance
        );
    });
}

#[test]
fn pay_on_behalf_emits_fee_paid_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        mint(ALICE, 500);
        assert_ok!(AbenaCoin::pay_on_behalf(RuntimeOrigin::signed(ALICE), BOB, 50));
        System::assert_last_event(
            Event::<Test>::FeePaidOnBehalf {
                payer: ALICE,
                patient: BOB,
                amount: 50,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// GOVERNANCE — vote (legacy)
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn vote_records_voting_power_equal_to_balance() {
    new_test_ext().execute_with(|| {
        set_block(1);
        mint(ALICE, 1_500);
        assert_ok!(AbenaCoin::vote(RuntimeOrigin::signed(ALICE), 42));
        System::assert_last_event(
            Event::<Test>::Voted {
                account: ALICE,
                proposal_id: 42,
                voting_power: 1_500,
            }
            .into(),
        );
    });
}

#[test]
fn vote_fails_with_zero_balance() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::vote(RuntimeOrigin::signed(ALICE), 1),
            Error::<Test>::InsufficientBalance
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// GOVERNANCE — submit_proposal / vote_on_proposal / execute_proposal
// ──────────────────────────────────────────────────────────────────────────────

fn setup_proposer(account: u64, balance: u128) {
    mint(account, balance);
}

#[test]
fn submit_proposal_requires_min_deposit() {
    new_test_ext().execute_with(|| {
        setup_proposer(ALICE, 50); // below MinProposalDeposit (100)
        assert_err!(
            AbenaCoin::submit_proposal(
                RuntimeOrigin::signed(ALICE),
                ProposalType::ParameterChange,
                Default::default(),
                None,
                None,
            ),
            Error::<Test>::InsufficientProposalDeposit
        );
    });
}

#[test]
fn submit_proposal_deducts_deposit_and_creates_proposal() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_proposer(ALICE, 500);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            ProposalType::ParameterChange,
            Default::default(),
            None,
            None,
        ));
        assert_eq!(AbenaCoin::balances(ALICE), 400); // 500 - 100 deposit
        let prop = Proposals::<Test>::get(0).unwrap();
        assert_eq!(prop.status, ProposalStatus::Active);
        assert_eq!(prop.voting_period_end, 11u64); // block 1 + period 10
    });
}

#[test]
fn submit_proposal_emits_proposal_submitted_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_proposer(ALICE, 300);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            ProposalType::TreasurySpend,
            Default::default(),
            None,
            None,
        ));
        System::assert_last_event(
            Event::<Test>::ProposalSubmitted {
                proposal_id: 0,
                proposer: ALICE,
                proposal_type: ProposalType::TreasurySpend,
                voting_period_end: 11,
            }
            .into(),
        );
    });
}

#[test]
fn vote_on_proposal_records_yes_vote() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_proposer(ALICE, 500);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            ProposalType::ParameterChange,
            Default::default(),
            None,
            None,
        ));
        // BOB votes Yes with 1000 tokens (no conviction)
        mint(BOB, 1_000);
        assert_ok!(AbenaCoin::vote_on_proposal(
            RuntimeOrigin::signed(BOB),
            0,
            VoteDirection::Yes,
            1_000,
            0u64.into(),
        ));
        let vote = Votes::<Test>::get(0, BOB).unwrap();
        assert_eq!(vote.direction, VoteDirection::Yes);
        assert_eq!(vote.voting_power, 1_000);
    });
}

#[test]
fn vote_on_proposal_fails_for_non_existent_proposal() {
    new_test_ext().execute_with(|| {
        set_block(1);
        mint(ALICE, 500);
        assert_err!(
            AbenaCoin::vote_on_proposal(
                RuntimeOrigin::signed(ALICE),
                999,
                VoteDirection::Yes,
                100,
                0u64.into(),
            ),
            Error::<Test>::ProposalNotFound
        );
    });
}

#[test]
fn vote_on_proposal_fails_after_voting_period() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_proposer(ALICE, 500);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            ProposalType::ParameterChange,
            Default::default(),
            None,
            None,
        ));
        // Advance past voting period (period=10, voting_period_end=11)
        set_block(12);
        mint(BOB, 500);
        assert_err!(
            AbenaCoin::vote_on_proposal(
                RuntimeOrigin::signed(BOB),
                0,
                VoteDirection::Yes,
                100,
                0u64.into(),
            ),
            Error::<Test>::VotingPeriodEnded
        );
    });
}

#[test]
fn vote_on_proposal_fails_for_double_voting() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_proposer(ALICE, 500);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            ProposalType::ParameterChange,
            Default::default(),
            None,
            None,
        ));
        mint(BOB, 500);
        assert_ok!(AbenaCoin::vote_on_proposal(
            RuntimeOrigin::signed(BOB),
            0,
            VoteDirection::Yes,
            200,
            0u64.into(),
        ));
        assert_err!(
            AbenaCoin::vote_on_proposal(
                RuntimeOrigin::signed(BOB),
                0,
                VoteDirection::Yes,
                200,
                0u64.into(),
            ),
            Error::<Test>::AlreadyVoted
        );
    });
}

#[test]
fn execute_proposal_fails_before_voting_period_ends() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_proposer(ALICE, 500);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            ProposalType::ParameterChange,
            Default::default(),
            None,
            None,
        ));
        // Still within voting period
        set_block(5);
        assert_err!(
            AbenaCoin::execute_proposal(RuntimeOrigin::signed(CHARLIE), 0),
            Error::<Test>::VotingPeriodEnded
        );
    });
}

#[test]
fn execute_proposal_fails_without_quorum() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_proposer(ALICE, 500);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            ProposalType::ParameterChange,
            Default::default(),
            None,
            None,
        ));
        // No votes cast
        set_block(12);
        assert_err!(
            AbenaCoin::execute_proposal(RuntimeOrigin::signed(CHARLIE), 0),
            Error::<Test>::ProposalDidNotPass
        );
    });
}

#[test]
fn execute_proposal_fails_without_majority() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_proposer(ALICE, 500);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            ProposalType::ParameterChange,
            Default::default(),
            None,
            None,
        ));
        // BOB votes Yes, CHARLIE votes No with equal weight → no majority
        mint(BOB, 100);
        mint(CHARLIE, 100);
        assert_ok!(AbenaCoin::vote_on_proposal(
            RuntimeOrigin::signed(BOB),
            0,
            VoteDirection::Yes,
            100,
            0u64.into(),
        ));
        assert_ok!(AbenaCoin::vote_on_proposal(
            RuntimeOrigin::signed(CHARLIE),
            0,
            VoteDirection::No,
            100,
            0u64.into(),
        ));
        set_block(12);
        assert_err!(
            AbenaCoin::execute_proposal(RuntimeOrigin::signed(DAVE), 0),
            Error::<Test>::ProposalDidNotPass
        );
    });
}

#[test]
fn execute_proposal_succeeds_with_majority_yes_votes() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_proposer(ALICE, 500);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            ProposalType::ParameterChange,
            Default::default(),
            None,
            None,
        ));
        // Mint enough for quorum: TotalSupply after mint+deposit ~ 500+100+1
        // MinQuorumPermille=1 → quorum = supply * 1/1000
        mint(BOB, 1_000);
        assert_ok!(AbenaCoin::vote_on_proposal(
            RuntimeOrigin::signed(BOB),
            0,
            VoteDirection::Yes,
            1_000,
            0u64.into(),
        ));
        set_block(12);
        assert_ok!(AbenaCoin::execute_proposal(RuntimeOrigin::signed(CHARLIE), 0));
        let prop = Proposals::<Test>::get(0).unwrap();
        assert_eq!(prop.status, ProposalStatus::Executed);
        // Proposer's deposit refunded
        assert_eq!(AbenaCoin::balances(ALICE), 500); // 400 + 100 refund
    });
}

#[test]
fn execute_proposal_emits_proposal_executed_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_proposer(ALICE, 200);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            ProposalType::ParameterChange,
            Default::default(),
            None,
            None,
        ));
        mint(BOB, 1_000);
        assert_ok!(AbenaCoin::vote_on_proposal(
            RuntimeOrigin::signed(BOB),
            0,
            VoteDirection::Yes,
            1_000,
            0u64.into(),
        ));
        set_block(12);
        assert_ok!(AbenaCoin::execute_proposal(RuntimeOrigin::signed(CHARLIE), 0));
        System::assert_last_event(
            Event::<Test>::ProposalExecuted { proposal_id: 0, executor: CHARLIE }.into(),
        );
    });
}

#[test]
fn delegate_votes_and_vote_uses_delegates_balance() {
    new_test_ext().execute_with(|| {
        set_block(1);
        setup_proposer(ALICE, 500);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            ProposalType::ParameterChange,
            Default::default(),
            None,
            None,
        ));
        // BOB delegates to CHARLIE; CHARLIE has 800 tokens
        mint(BOB, 100);
        mint(CHARLIE, 800);
        assert_ok!(AbenaCoin::delegate_votes(RuntimeOrigin::signed(BOB), CHARLIE));
        // BOB votes, but the balance check uses CHARLIE's balance
        assert_ok!(AbenaCoin::vote_on_proposal(
            RuntimeOrigin::signed(BOB),
            0,
            VoteDirection::Yes,
            800, // votes using CHARLIE's balance
            0u64.into(),
        ));
        let vote = Votes::<Test>::get(0, BOB).unwrap();
        assert_eq!(vote.voting_power, 800);
    });
}

#[test]
fn delegate_votes_to_self_fails() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::delegate_votes(RuntimeOrigin::signed(ALICE), ALICE),
            Error::<Test>::CannotDelegateToSelf
        );
    });
}

#[test]
fn update_voting_parameters_requires_root() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::update_voting_parameters(
                RuntimeOrigin::signed(ALICE),
                100,
                600,
                20u64.into()
            ),
            frame_support::error::BadOrigin
        );
    });
}

#[test]
fn update_voting_parameters_stores_new_values() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::update_voting_parameters(
            RuntimeOrigin::root(),
            50,
            600,
            20u64.into()
        ));
        let params = AbenaCoin::voting_parameters().unwrap();
        assert_eq!(params.min_quorum_permille, 50);
        assert_eq!(params.approval_threshold_permille, 600);
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// TREASURY
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn collect_to_treasury_moves_tokens() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 1_000);
        assert_ok!(AbenaCoin::collect_to_treasury(RuntimeOrigin::signed(ALICE), 200));
        assert_eq!(AbenaCoin::balances(ALICE), 800);
        assert_eq!(AbenaCoin::treasury_balance(), 200);
    });
}

#[test]
fn collect_to_treasury_fails_insufficient_balance() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 50);
        assert_err!(
            AbenaCoin::collect_to_treasury(RuntimeOrigin::signed(ALICE), 200),
            Error::<Test>::InsufficientBalance
        );
    });
}

#[test]
fn treasury_allocate_to_reward_pool() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 1_000);
        assert_ok!(AbenaCoin::collect_to_treasury(RuntimeOrigin::signed(ALICE), 500));
        let pool_before = AbenaCoin::reward_pool();
        assert_ok!(AbenaCoin::treasury_allocate(
            RuntimeOrigin::root(),
            crate::pallet::TreasuryAllocationCategory::PatientRewardPool,
            300
        ));
        assert_eq!(AbenaCoin::treasury_balance(), 200);
        assert_eq!(AbenaCoin::reward_pool(), pool_before + 300);
    });
}

#[test]
fn treasury_allocate_fails_if_insufficient_treasury() {
    new_test_ext().execute_with(|| {
        // Treasury is empty
        assert_err!(
            AbenaCoin::treasury_allocate(
                RuntimeOrigin::root(),
                crate::pallet::TreasuryAllocationCategory::Development,
                100
            ),
            Error::<Test>::InsufficientTreasuryBalance
        );
    });
}

#[test]
fn claim_treasury_grant_workflow() {
    new_test_ext().execute_with(|| {
        set_block(1);
        // Fund the treasury
        mint(ALICE, 5_000);
        assert_ok!(AbenaCoin::collect_to_treasury(RuntimeOrigin::signed(ALICE), 2_000));
        // ALICE submits a treasury-spend proposal with BOB as beneficiary
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            ProposalType::TreasurySpend,
            Default::default(),
            Some(500u128),
            Some(BOB),
        ));
        // Vote and execute
        mint(CHARLIE, 1_000);
        assert_ok!(AbenaCoin::vote_on_proposal(
            RuntimeOrigin::signed(CHARLIE),
            0,
            VoteDirection::Yes,
            1_000,
            0u64.into(),
        ));
        set_block(12);
        assert_ok!(AbenaCoin::execute_proposal(RuntimeOrigin::signed(DAVE), 0));
        // BOB can now claim the approved grant
        assert_ok!(AbenaCoin::claim_treasury_grant(RuntimeOrigin::signed(BOB), 0));
        assert_eq!(AbenaCoin::balances(BOB), 500);
    });
}

#[test]
fn claim_treasury_grant_fails_without_approval() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AbenaCoin::claim_treasury_grant(RuntimeOrigin::signed(BOB), 0),
            Error::<Test>::NoGrantToClaim
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// INTEGRATION TESTS
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn integration_complete_token_lifecycle() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // 1. Mint tokens
        mint(ALICE, BRONZE_MIN * 2);

        // 2. Transfer some to BOB
        assert_ok!(AbenaCoin::transfer(
            RuntimeOrigin::signed(ALICE),
            BOB,
            BRONZE_MIN
        ));

        // 3. ALICE stakes (Bronze)
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(ALICE), BRONZE_MIN));
        assert_eq!(AbenaCoin::staking_tier(ALICE), Some(StakingTier::Bronze));

        // 4. Earn gamification reward
        let id = create_self_reported_achievement(false);
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(BOB),
            id
        ));

        // 5. BOB participates in governance
        mint(CHARLIE, 500);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(CHARLIE),
            ProposalType::FeatureActivation,
            Default::default(),
            None,
            None,
        ));
        // BOB must vote with enough tokens to meet quorum against the large BRONZE_MIN supply.
        assert_ok!(AbenaCoin::vote_on_proposal(
            RuntimeOrigin::signed(BOB),
            0,
            VoteDirection::Yes,
            BRONZE_MIN,
            0u64.into(),
        ));
        set_block(12);
        assert_ok!(AbenaCoin::execute_proposal(RuntimeOrigin::signed(ALICE), 0));
    });
}

#[test]
fn integration_vesting_workflow() {
    new_test_ext().execute_with(|| {
        set_block(0);
        // Create a vesting schedule: 1000 tokens over 100 blocks after a 10-block cliff
        assert_ok!(AbenaCoin::add_vesting_schedule(
            RuntimeOrigin::root(),
            ALICE,
            1_000,
            0u64.into(),
            10u64.into(),
            100u64.into(),
        ));

        // Before cliff — nothing to claim
        set_block(9);
        assert_err!(
            AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)),
            Error::<Test>::NothingToVest
        );

        // At cliff + 40 blocks elapsed → 40 * 10 = 400 released
        set_block(50);
        assert_ok!(AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)));
        assert_eq!(AbenaCoin::balances(ALICE), 400);

        // Claim again at block 80 → 30 more blocks * 10 = 300 additional
        set_block(80);
        assert_ok!(AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)));
        assert_eq!(AbenaCoin::balances(ALICE), 700);

        // Fully vested
        set_block(200);
        assert_ok!(AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)));
        assert_eq!(AbenaCoin::balances(ALICE), 1_000);

        // Nothing more to claim
        assert_err!(
            AbenaCoin::claim_vested_tokens(RuntimeOrigin::signed(ALICE)),
            Error::<Test>::NothingToVest
        );
    });
}

#[test]
fn integration_gamification_workflow() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // Governance creates an achievement
        assert_ok!(AbenaCoin::create_achievement(
            RuntimeOrigin::root(),
            AchievementCategory::DataContribution,
            name("Data Hero"),
            desc("Share genomic data for research"),
            500,
            true,
            BoundedVec::default(),
            VerificationMethod::SelfReported,
        ));
        let id = 0u32;

        // Patient registers a referral first so bonus flows on claim
        assert_ok!(AbenaCoin::register_referral(RuntimeOrigin::signed(ALICE), BOB));

        // Patient claims achievement (self-reported)
        assert_ok!(AbenaCoin::claim_gamification_achievement(
            RuntimeOrigin::signed(ALICE),
            id
        ));
        let alice_balance_1 = AbenaCoin::balances(ALICE);
        assert!(alice_balance_1 >= 500, "Expected at least base reward");

        // BOB received referral bonus
        let referral_bonus: u128 = 20_000_000_000_000_000_000u128;
        assert_eq!(AbenaCoin::balances(BOB), referral_bonus);

        // Award a streak bonus
        assert_ok!(AbenaCoin::award_streak_bonus(
            RuntimeOrigin::root(),
            ALICE,
            StreakType::WellnessActivity,
            1_000
        ));
        assert_eq!(AbenaCoin::balances(ALICE), alice_balance_1 + 1_000);
        assert_eq!(AbenaCoin::lifetime_earnings(ALICE), alice_balance_1 + 1_000);
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// EDGE CASES
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn arithmetic_overflow_protected_in_supply() {
    new_test_ext().execute_with(|| {
        // Minting near supply cap should succeed; one over should fail
        assert_ok!(AbenaCoin::mint(RuntimeOrigin::root(), ALICE, SUPPLY_CAP));
        assert_err!(
            AbenaCoin::mint(RuntimeOrigin::root(), BOB, 1),
            Error::<Test>::SupplyCapExceeded
        );
    });
}

#[test]
fn burn_then_mint_restores_supply() {
    new_test_ext().execute_with(|| {
        mint(ALICE, 1_000);
        assert_ok!(AbenaCoin::burn(RuntimeOrigin::signed(ALICE), 500));
        assert_eq!(AbenaCoin::total_supply(), 500);
        mint(ALICE, 200);
        assert_eq!(AbenaCoin::total_supply(), 700);
    });
}

#[test]
fn multiple_approvals_independent_per_spender() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::approve(RuntimeOrigin::signed(ALICE), BOB, 100));
        assert_ok!(AbenaCoin::approve(RuntimeOrigin::signed(ALICE), CHARLIE, 300));
        assert_eq!(AbenaCoin::allowance(ALICE, BOB), 100);
        assert_eq!(AbenaCoin::allowance(ALICE, CHARLIE), 300);
    });
}

#[test]
fn zero_balance_cannot_submit_governance_proposal() {
    new_test_ext().execute_with(|| {
        // ALICE has no abena-coin balance at all
        assert_err!(
            AbenaCoin::submit_proposal(
                RuntimeOrigin::signed(ALICE),
                ProposalType::ParameterChange,
                Default::default(),
                None,
                None,
            ),
            Error::<Test>::InsufficientProposalDeposit
        );
    });
}

#[test]
fn concurrent_staking_and_transfer_do_not_interfere() {
    new_test_ext().execute_with(|| {
        mint(ALICE, BRONZE_MIN * 3);
        // Stake and transfer from separate balances
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(ALICE), BRONZE_MIN));
        assert_ok!(AbenaCoin::transfer(RuntimeOrigin::signed(ALICE), BOB, BRONZE_MIN));
        // ALICE has BRONZE_MIN remaining liquid
        assert_eq!(AbenaCoin::balances(ALICE), BRONZE_MIN);
        assert_eq!(AbenaCoin::staked_balance(ALICE), BRONZE_MIN);
    });
}

#[test]
fn reward_pool_depletion_stops_distribution() {
    new_test_ext().execute_with(|| {
        assert_ok!(AbenaCoin::fund_reward_pool(RuntimeOrigin::root(), 100));
        assert_ok!(AbenaCoin::distribute_patient_reward(
            RuntimeOrigin::root(),
            ALICE,
            100
        ));
        assert_err!(
            AbenaCoin::distribute_patient_reward(RuntimeOrigin::root(), BOB, 1),
            Error::<Test>::RewardPoolExhausted
        );
    });
}

#[test]
fn proposal_id_increments_for_each_submission() {
    new_test_ext().execute_with(|| {
        set_block(1);
        for _ in 0..3 {
            mint(ALICE, 200);
        }
        mint(ALICE, 600); // 3 * 200 for three deposits
        for expected_id in 0..3u32 {
            let before = AbenaCoin::next_proposal_id();
            assert_eq!(before, expected_id);
            assert_ok!(AbenaCoin::submit_proposal(
                RuntimeOrigin::signed(ALICE),
                ProposalType::ParameterChange,
                Default::default(),
                None,
                None,
            ));
        }
        assert_eq!(AbenaCoin::next_proposal_id(), 3);
    });
}
