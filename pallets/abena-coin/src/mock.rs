//! Mock runtime for pallet-abena-coin tests.
//!
//! Uses pallet_balances to satisfy the Currency trait bound.
//! The abena-coin pallet maintains its own `Balances` StorageMap (separate from
//! pallet_balances AccountData); pallet_balances only provides the `BalanceOf<T> = u128` type.

use crate as pallet_abena_coin;
use frame_support::{
    parameter_types,
    traits::{ConstU128, ConstU16, ConstU32, ConstU64},
    PalletId,
};
use frame_system as system;
use sp_core::H256;
use sp_runtime::{
    traits::{BlakeTwo256, IdentityLookup},
    BuildStorage,
};

type Block = frame_system::mocking::MockBlock<Test>;

frame_support::construct_runtime!(
    pub enum Test {
        System: frame_system,
        Balances: pallet_balances,
        AbenaCoin: pallet_abena_coin,
    }
);

parameter_types! {
    pub const AbenaCoinPalletId: PalletId = PalletId(*b"abn/coin");
    /// Minimum deposit to submit a governance proposal (in raw ABENA units).
    pub const TestMinProposalDeposit: u128 = 100;
    /// Voting period in blocks.
    pub const TestVotingPeriodBlocks: u64 = 10;
}

impl system::Config for Test {
    type BaseCallFilter = frame_support::traits::Everything;
    type BlockWeights = ();
    type BlockLength = ();
    type DbWeight = ();
    type RuntimeOrigin = RuntimeOrigin;
    type RuntimeCall = RuntimeCall;
    type Nonce = u64;
    type Hash = H256;
    type Hashing = BlakeTwo256;
    type AccountId = u64;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
    type RuntimeEvent = RuntimeEvent;
    type BlockHashCount = ConstU64<250>;
    type Version = ();
    type PalletInfo = PalletInfo;
    type AccountData = pallet_balances::AccountData<u128>;
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type SS58Prefix = ConstU16<42>;
    type OnSetCode = ();
    type MaxConsumers = ConstU32<16>;
    type RuntimeTask = ();
    type SingleBlockMigrations = ();
    type MultiBlockMigrator = ();
    type PreInherents = ();
    type PostInherents = ();
    type PostTransactions = ();
}

impl pallet_balances::Config for Test {
    type MaxLocks = ConstU32<50>;
    type MaxReserves = ();
    type ReserveIdentifier = [u8; 8];
    type Balance = u128;
    type RuntimeEvent = RuntimeEvent;
    type DustRemoval = ();
    type ExistentialDeposit = ConstU128<1>;
    type AccountStore = System;
    type WeightInfo = ();
    type FreezeIdentifier = RuntimeFreezeReason;
    type MaxFreezes = ConstU32<0>;
    type RuntimeHoldReason = RuntimeHoldReason;
    type RuntimeFreezeReason = RuntimeFreezeReason;
}

/// Blanket WeightInfo implementation for the test environment.
/// All weights return zero — we measure correctness, not weight, in unit tests.
impl crate::WeightInfo for () {
    fn mint()                       -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn burn()                       -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn transfer()                   -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn grant_reward()               -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn claim_achievement()          -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn approve()                    -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn transfer_from()              -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn stake()                      -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn unstake()                    -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn claim_vested_tokens()        -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn distribute_patient_reward()  -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn vote()                       -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn pay_on_behalf()              -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn add_vesting_schedule()       -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn fund_reward_pool()           -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn create_achievement()         -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn claim_gamification_achievement() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn verify_achievement()         -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn award_streak_bonus()         -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn update_streak()              -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn register_referral()          -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn set_seasonal_multiplier()    -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn submit_proposal()            -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn vote_on_proposal()           -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn delegate_votes()             -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn execute_proposal()           -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn treasury_allocate()          -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn claim_treasury_grant()       -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn collect_to_treasury()        -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn update_voting_parameters()   -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
}

impl pallet_abena_coin::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type PalletId = AbenaCoinPalletId;
    type Currency = Balances;
    type WeightInfo = ();
    /// Up to 10 vesting schedules per account.
    type MaxVestingSchedules = ConstU32<10>;
    /// Up to 100 referrals per referrer.
    type MaxReferralsPerAccount = ConstU32<100>;
    /// Self-reported achievements are rate-limited: one claim per 10 blocks.
    type SelfReportCooldownBlocks = ConstU64<10>;
    /// Submitting a proposal requires at least 100 ABENA in the pallet ledger.
    type MinProposalDeposit = TestMinProposalDeposit;
    /// Voting period is 10 blocks.
    type VotingPeriodBlocks = TestVotingPeriodBlocks;
    /// 0.1% quorum — easy to meet in tests without minting enormous supply.
    type MinQuorumPermille = ConstU32<1>;
    /// Simple majority (50%) threshold.
    type ApprovalThresholdPermille = ConstU32<500>;
    /// Audit trail holds up to 200 spending records.
    type MaxSpendingHistoryEntries = ConstU32<200>;
}

// ──────────────────────────────────────────────────────────────────────────────
// Test accounts
// ──────────────────────────────────────────────────────────────────────────────

pub const ALICE: u64 = 1;
pub const BOB: u64 = 2;
pub const CHARLIE: u64 = 3;
pub const DAVE: u64 = 4;
pub const EVE: u64 = 5;

// ──────────────────────────────────────────────────────────────────────────────
// Token amount helpers
// ──────────────────────────────────────────────────────────────────────────────

/// 10^18 — one ABENA in raw units (18 decimal places).
pub const TEN_18: u128 = 1_000_000_000_000_000_000u128;

/// Staking tier minimums (raw units with 18-decimal precision).
pub const BRONZE_MIN: u128 = 100_000 * TEN_18;
pub const SILVER_MIN: u128 = 500_000 * TEN_18;
pub const GOLD_MIN: u128 = 1_000_000 * TEN_18;
pub const PLATINUM_MIN: u128 = 5_000_000 * TEN_18;

/// Total supply cap: 1 billion ABENA.
pub const SUPPLY_CAP: u128 = 1_000_000_000 * TEN_18;

// ──────────────────────────────────────────────────────────────────────────────
// Genesis / test environment
// ──────────────────────────────────────────────────────────────────────────────

/// Builds a test externalities environment.
///
/// The abena-coin pallet's own internal `Balances` ledger starts empty.
/// Tests must call `AbenaCoin::mint(Root, account, amount)` to fund accounts
/// before testing transfers, staking, proposals, etc.
///
/// Block number is set to 1 so that `System::assert_has_event` works
/// (FRAME only stores events when block_number > 0).
pub fn new_test_ext() -> sp_io::TestExternalities {
    let mut ext: sp_io::TestExternalities = RuntimeGenesisConfig::default()
        .build_storage()
        .unwrap()
        .into();
    ext.execute_with(|| System::set_block_number(1));
    ext
}
