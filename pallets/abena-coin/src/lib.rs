//! # ABENA Coin Pallet
//!
//! Native utility token for the ABENA healthcare blockchain.
//!
//! **Token fundamentals**: ABENA Coin, symbol ABENA, 18 decimals, total supply 1 billion.
//! Used for healthcare data marketplace, gamification, staking, and governance.
//!
//! **Features**: Fungible (ERC-20 style), mint/burn, approve/transfer_from, staking for
//! commercial entities (tiers), patient reward distribution, fee abstraction (pay_on_behalf),
//! vesting (team/investors), governance voting weight, gamification rewards and achievements.

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Encode, Decode, DecodeWithMemTracking, MaxEncodedLen};
use scale_info::TypeInfo;
use sp_runtime::RuntimeDebug;
use frame_system::pallet_prelude::BlockNumberFor;
use frame_support::weights::Weight;
use sp_runtime::BoundedVec;
use frame_support::traits::ConstU32;


#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
pub mod weights;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{
        pallet_prelude::*,
        traits::{Currency, ReservableCurrency, ExistenceRequirement},
        traits::ConstU32,
        RuntimeDebugNoBound,
    };
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;
    use sp_runtime::traits::{Zero, CheckedAdd, CheckedDiv, Saturating};
    use sp_runtime::SaturatedConversion;
    use codec::{Encode, Decode, DecodeWithMemTracking, MaxEncodedLen};
    use scale_info::TypeInfo;
    use sp_runtime::RuntimeDebug;

    use crate::WeightInfo;
    /// Balance type alias
    pub type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    /// Reward types for gamification
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum RewardType {
        /// Reward for creating health records
        HealthRecordCreated,
        /// Reward for updating health records
        HealthRecordUpdated,
        /// Reward for sharing data for research
        DataShared,
        /// Reward for quantum computing contributions
        QuantumContribution,
    /// Reward for platform participation
    PlatformParticipation,
    /// Reward for wellness goal (e.g. steps, sleep, mindfulness)
    WellnessGoalReached,
    /// Reward for care plan adherence
    CarePlanAdherence,
}

    /// Achievement types
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum AchievementType {
        /// Created first health record
        HealthRecordCreator,
        /// Active user (logged in regularly)
        ActiveUser,
        /// Contributed data for research
        DataContributor,
        /// Contributed to quantum computing research
        QuantumResearcher,
        /// Wellness streak (e.g. 7-day logging)
        WellnessStreak,
        /// Integrative care plan completed
        IntegrativeCareComplete,
    }

/// Achievement record for a user
#[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct AchievementRecord<T: Config> {
        /// List of unlocked achievements
        pub unlocked_achievements: BoundedVec<AchievementType, ConstU32<50>>,
        /// Total number of achievements
        pub total_achievements: u32,
        /// Last achievement unlock timestamp
        pub last_unlock: Option<BlockNumberFor<T>>,
    }

    impl<T: Config> Default for AchievementRecord<T> {
        fn default() -> Self {
            Self {
                unlocked_achievements: BoundedVec::default(),
                total_achievements: 0,
                last_unlock: None,
            }
        }
    }

    /// Reward entry in history
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct RewardEntry<T: Config> {
        /// Amount rewarded
        pub amount: BalanceOf<T>,
        /// Block number when reward was granted
        pub block_number: BlockNumberFor<T>,
    }

    /// Vesting schedule for team/investors (linear release after cliff).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct VestingSchedule<T: Config> {
        pub total_amount: BalanceOf<T>,
        pub released_amount: BalanceOf<T>,
        pub start_block: BlockNumberFor<T>,
        pub cliff_duration: BlockNumberFor<T>,
        pub vesting_duration: BlockNumberFor<T>,
        pub release_per_block: BalanceOf<T>,
    }

    /// Commercial entity staking tier (min: Bronze 100K, Silver 500K, Gold 1M, Platinum 5M ABENA).
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum StakingTier {
        Bronze,
        Silver,
        Gold,
        Platinum,
    }

    // ---------- Gamification module types ----------

    /// Category of achievement for wellness, engagement, and clinical outcomes.
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum AchievementCategory {
        Wellness,
        Engagement,
        ClinicalOutcome,
        DataContribution,
        Community,
    }

    /// How achievement completion is verified (anti-gaming: higher trust = less rate limiting).
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum VerificationMethod {
        SelfReported,
        DeviceVerified,
        ProviderVerified,
        QuantumVerified,
        BlockchainVerified,
    }

    /// Requirement threshold for an achievement (bounded, no dynamic logic).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebugNoBound, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub enum AchievementRequirement<T: Config> {
        StepsCount(u32),
        StreakDays(u32),
        VisitsCount(u32),
        DataShared(bool),
        ReferralCount(u32),
        TenureBlocks(BlockNumberFor<T>),
        Custom(u32),
    }

    /// Bounded list of requirements (all must be met).
    pub type AchievementRequirements<T> = BoundedVec<AchievementRequirement<T>, ConstU32<8>>;

    /// Achievement definition (governance-created).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebugNoBound, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct AchievementDefinition<T: Config> {
        pub achievement_id: u32,
        pub category: AchievementCategory,
        pub name: BoundedVec<u8, ConstU32<64>>,
        pub description: BoundedVec<u8, ConstU32<128>>,
        pub base_reward: BalanceOf<T>,
        pub repeatable: bool,
        pub requirements: AchievementRequirements<T>,
        pub verification_method: VerificationMethod,
    }

    /// Completion status for a patient's achievement (repeatable = claim count).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct CompletionStatus<T: Config> {
        pub completed_at: BlockNumberFor<T>,
        pub claim_count: u32,
        pub verified: bool,
    }

    /// Streak type for multiplier calculation.
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum StreakType {
        DailyLogin,
        MedicationAdherence,
        WellnessActivity,
    }

    /// Current and longest streak per type (blocks or days represented as block intervals).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct StreakInfo<T: Config> {
        pub current_streak: u32,
        pub longest_streak: u32,
        pub last_activity_block: BlockNumberFor<T>,
    }

    // ---------- Treasury & Governance types ----------

    /// Type of governance proposal.
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum ProposalType {
        TreasurySpend,
        ParameterChange,
        FeatureActivation,
        EntityApproval,
        EmergencyAction,
    }

    /// Lifecycle status of a proposal.
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum ProposalStatus {
        Active,
        Passed,
        Rejected,
        Executed,
        Cancelled,
    }

    /// Governance proposal (treasury spend, parameter change, etc.).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct Proposal<T: Config> {
        pub proposal_id: u32,
        pub proposer: T::AccountId,
        pub proposal_type: ProposalType,
        pub description_hash: T::Hash,
        pub requested_amount: Option<BalanceOf<T>>,
        pub beneficiary: Option<T::AccountId>,
        pub voting_period_end: BlockNumberFor<T>,
        pub yes_votes: BalanceOf<T>,
        pub no_votes: BalanceOf<T>,
        pub status: ProposalStatus,
        pub created_at: BlockNumberFor<T>,
    }

    /// Vote direction and optional conviction (locked balance for weight).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum VoteDirection {
        Yes,
        No,
    }

    /// A vote on a proposal (1 ABENA = 1 vote; conviction multiplies weight).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct VoteRecord<T: Config> {
        pub direction: VoteDirection,
        pub voting_power: BalanceOf<T>,
        pub conviction_blocks: BlockNumberFor<T>,
    }

    /// Treasury allocation category for transparent spending.
    #[derive(Clone, Copy, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum TreasuryAllocationCategory {
        PatientRewardPool,
        Development,
        Marketing,
        EmergencyReserve,
        CommunityGrant,
    }

    /// Single entry in the spending audit trail.
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct SpendingRecord<T: Config> {
        pub proposal_id: u32,
        pub beneficiary: T::AccountId,
        pub amount: BalanceOf<T>,
        pub category: TreasuryAllocationCategory,
        pub block: BlockNumberFor<T>,
    }

    /// Configuration trait for the pallet.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// The pallet ID for reserving funds
        type PalletId: Get<frame_support::PalletId>;
        /// The currency type for ABENA Coin
        type Currency: Currency<Self::AccountId> + ReservableCurrency<Self::AccountId>;
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
        /// Maximum number of vesting schedules per account
        #[pallet::constant]
        type MaxVestingSchedules: Get<u32>;
        /// Maximum referrals per account (for referral tree)
        #[pallet::constant]
        type MaxReferralsPerAccount: Get<u32>;
        /// Cooldown in blocks for self-reported achievements (anti-gaming)
        #[pallet::constant]
        type SelfReportCooldownBlocks: Get<BlockNumberFor<Self>>;
        /// Minimum deposit to submit a proposal (anti-spam)
        #[pallet::constant]
        type MinProposalDeposit: Get<BalanceOf<Self>>;
        /// Voting period in blocks
        #[pallet::constant]
        type VotingPeriodBlocks: Get<BlockNumberFor<Self>>;
        /// Minimum quorum in permille (e.g. 100 = 10% of eligible votes must participate)
        #[pallet::constant]
        type MinQuorumPermille: Get<u32>;
        /// Required approval threshold in permille (e.g. 500 = majority)
        #[pallet::constant]
        type ApprovalThresholdPermille: Get<u32>;
        /// Max entries in spending history (audit trail)
        #[pallet::constant]
        type MaxSpendingHistoryEntries: Get<u32>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Total supply of ABENA Coin
    #[pallet::storage]
    #[pallet::getter(fn total_supply)]
    pub type TotalSupply<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    /// User balances of ABENA Coin
    #[pallet::storage]
    #[pallet::getter(fn balances)]
    pub type Balances<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BalanceOf<T>,
        ValueQuery,
    >;

    /// Gamification achievements and rewards
    #[pallet::storage]
    #[pallet::getter(fn achievements)]
    pub type Achievements<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        AchievementRecord<T>,
        ValueQuery,
    >;

    /// Reward history for tracking gamification activities
    #[pallet::storage]
    pub type RewardHistory<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        RewardType,
        BoundedVec<RewardEntry<T>, ConstU32<1000>>,
        OptionQuery,
    >;

    /// Allowances: owner -> spender -> amount (ERC-20 style delegated spending)
    #[pallet::storage]
    #[pallet::getter(fn allowance)]
    pub type Allowances<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        T::AccountId,
        BalanceOf<T>,
        ValueQuery,
    >;

    /// Staked balances (tokens locked for commercial entity privileges)
    #[pallet::storage]
    #[pallet::getter(fn staked_balance)]
    pub type StakedBalances<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BalanceOf<T>,
        ValueQuery,
    >;

    /// Staking tier per account (Bronze/Silver/Gold/Platinum)
    #[pallet::storage]
    #[pallet::getter(fn staking_tier)]
    pub type StakingTiers<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        StakingTier,
        OptionQuery,
    >;

    /// Vesting schedules per account (team/investors)
    #[pallet::storage]
    #[pallet::getter(fn vesting_schedules)]
    pub type VestingSchedules<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BoundedVec<VestingSchedule<T>, ConstU32<10>>,
        OptionQuery,
    >;

    /// Remaining tokens in the patient rewards pool (40% of supply, released over 10 years)
    #[pallet::storage]
    #[pallet::getter(fn reward_pool)]
    pub type RewardPool<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    /// Lifetime patient earnings (for gamification / multipliers)
    #[pallet::storage]
    #[pallet::getter(fn lifetime_earnings)]
    pub type LifetimeEarnings<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BalanceOf<T>,
        ValueQuery,
    >;

    // ---------- Gamification module storage ----------

    /// Next achievement ID (incremented on create_achievement).
    #[pallet::storage]
    #[pallet::getter(fn next_achievement_id)]
    pub type NextAchievementId<T: Config> = StorageValue<_, u32, ValueQuery>;

    /// Achievement definitions by ID (governance-created).
    #[pallet::storage]
    #[pallet::getter(fn achievement_definitions)]
    pub type AchievementDefinitions<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u32,
        AchievementDefinition<T>,
        OptionQuery,
    >;

    /// Patient completion status per achievement (patient, achievement_id) -> CompletionStatus.
    #[pallet::storage]
    #[pallet::getter(fn patient_achievements)]
    pub type PatientAchievements<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        u32,
        CompletionStatus<T>,
        OptionQuery,
    >;

    /// Leaderboard: account -> total gamification score (updated on claim).
    #[pallet::storage]
    #[pallet::getter(fn leaderboard_scores)]
    pub type LeaderboardScores<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        u64,
        ValueQuery,
    >;

    /// Streak tracking per (patient, streak_type).
    #[pallet::storage]
    #[pallet::getter(fn streak_tracking)]
    pub type StreakTracking<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        StreakType,
        StreakInfo<T>,
        OptionQuery,
    >;

    /// Referral tree: referrer -> list of referred accounts.
    #[pallet::storage]
    #[pallet::getter(fn referral_children)]
    pub type ReferralChildren<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BoundedVec<T::AccountId, ConstU32<100>>,
        OptionQuery,
    >;

    /// Who referred this account (for referral bonus).
    #[pallet::storage]
    #[pallet::getter(fn referrer_of)]
    pub type ReferrerOf<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        T::AccountId,
        OptionQuery,
    >;

    /// Last block a self-reported achievement was claimed (rate limiting).
    #[pallet::storage]
    pub type SelfReportLastClaim<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        u32,
        BlockNumberFor<T>,
        OptionQuery,
    >;

    /// Optional seasonal multiplier: (start_block, end_block, multiplier_per_mille) e.g. 2000 = 2x.
    #[pallet::storage]
    #[pallet::getter(fn seasonal_multiplier)]
    pub type SeasonalMultiplier<T: Config> = StorageValue<
        _,
        (BlockNumberFor<T>, BlockNumberFor<T>, u32),
        OptionQuery,
    >;

    // ---------- Treasury & Governance storage ----------

    /// Treasury balance (protocol revenue: marketplace fees, subscriptions, etc.).
    #[pallet::storage]
    #[pallet::getter(fn treasury_balance)]
    pub type TreasuryBalance<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    /// Next proposal ID.
    #[pallet::storage]
    #[pallet::getter(fn next_proposal_id)]
    pub type NextProposalId<T: Config> = StorageValue<_, u32, ValueQuery>;

    /// Governance proposals by ID.
    #[pallet::storage]
    #[pallet::getter(fn proposals)]
    pub type Proposals<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u32,
        Proposal<T>,
        OptionQuery,
    >;

    /// Votes: (proposal_id, voter) -> VoteRecord.
    #[pallet::storage]
    #[pallet::getter(fn votes)]
    pub type Votes<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        u32,
        Blake2_128Concat,
        T::AccountId,
        VoteRecord<T>,
        OptionQuery,
    >;

    /// Delegated voting power: delegator -> delegate.
    #[pallet::storage]
    #[pallet::getter(fn delegated_to)]
    pub type DelegatedVotes<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        T::AccountId,
        OptionQuery,
    >;

    /// Proposal deposit (proposal_id -> (proposer, amount)) for refund on execute/cancel.
    #[pallet::storage]
    pub type ProposalDeposits<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        u32,
        (T::AccountId, BalanceOf<T>),
        OptionQuery,
    >;

    /// Spending history (audit trail). Bounded ring buffer or single value count.
    #[pallet::storage]
    #[pallet::getter(fn spending_history)]
    pub type SpendingHistory<T: Config> = StorageValue<
        _,
        BoundedVec<SpendingRecord<T>, ConstU32<200>>,
        ValueQuery,
    >;

    /// Approved grants: (beneficiary, proposal_id) -> amount (claimable).
    #[pallet::storage]
    #[pallet::getter(fn approved_grants)]
    pub type ApprovedGrants<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        u32,
        BalanceOf<T>,
        OptionQuery,
    >;

    /// Voting parameters (updatable by governance). None = use Config constants.
    #[pallet::storage]
    #[pallet::getter(fn voting_parameters)]
    pub type VotingParameters<T: Config> = StorageValue<_, VotingParams<T>, OptionQuery>;

    /// VotingParams: optional overrides (use default from Config if not set).
    #[derive(Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct VotingParams<T: Config> {
        pub min_quorum_permille: u32,
        pub approval_threshold_permille: u32,
        pub voting_period_blocks: BlockNumberFor<T>,
    }

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// ABENA Coins were minted
        CoinsMinted {
            account: T::AccountId,
            amount: BalanceOf<T>,
        },
        /// ABENA Coins were burned
        CoinsBurned {
            account: T::AccountId,
            amount: BalanceOf<T>,
        },
        /// Coins were transferred
        CoinsTransferred {
            from: T::AccountId,
            to: T::AccountId,
            amount: BalanceOf<T>,
        },
        /// Reward was granted
        RewardGranted {
            account: T::AccountId,
            reward_type: RewardType,
            amount: BalanceOf<T>,
        },
        /// Achievement unlocked
        AchievementUnlocked {
            account: T::AccountId,
            achievement: AchievementType,
        },
        /// Allowance set (owner, spender, amount)
        Approved {
            owner: T::AccountId,
            spender: T::AccountId,
            amount: BalanceOf<T>,
        },
        /// Spent on behalf via allowance
        TransferFrom {
            owner: T::AccountId,
            spender: T::AccountId,
            to: T::AccountId,
            amount: BalanceOf<T>,
        },
        /// Tokens staked for commercial tier
        Staked {
            account: T::AccountId,
            amount: BalanceOf<T>,
            tier: StakingTier,
        },
        /// Tokens unstaked
        Unstaked {
            account: T::AccountId,
            amount: BalanceOf<T>,
        },
        /// Vested tokens claimed
        VestedTokensClaimed {
            account: T::AccountId,
            amount: BalanceOf<T>,
        },
        /// Patient reward distributed from pool
        PatientRewardDistributed {
            account: T::AccountId,
            amount: BalanceOf<T>,
        },
        /// Governance vote cast (voting power = balance)
        Voted {
            account: T::AccountId,
            proposal_id: u32,
            voting_power: BalanceOf<T>,
        },
        /// Fee paid on behalf of patient (fee abstraction)
        FeePaidOnBehalf {
            payer: T::AccountId,
            patient: T::AccountId,
            amount: BalanceOf<T>,
        },
        /// New achievement definition created (governance)
        AchievementCreated {
            achievement_id: u32,
            category: AchievementCategory,
            base_reward: BalanceOf<T>,
        },
        /// Patient claimed a gamification achievement
        GamificationAchievementClaimed {
            account: T::AccountId,
            achievement_id: u32,
            amount: BalanceOf<T>,
            multiplier_mille: u32,
        },
        /// Achievement verified by provider/system
        AchievementVerified {
            account: T::AccountId,
            achievement_id: u32,
        },
        /// Streak bonus awarded
        StreakBonusAwarded {
            account: T::AccountId,
            streak_type: StreakType,
            streak_length: u32,
            bonus: BalanceOf<T>,
        },
        /// Referral bonus distributed
        ReferralBonusDistributed {
            referrer: T::AccountId,
            referred: T::AccountId,
            amount: BalanceOf<T>,
        },
        /// Referral link registered
        ReferralRegistered {
            referrer: T::AccountId,
            referred: T::AccountId,
        },
        /// Seasonal multiplier active
        SeasonalMultiplierSet {
            start_block: BlockNumberFor<T>,
            end_block: BlockNumberFor<T>,
            multiplier_mille: u32,
        },
        /// Proposal submitted
        ProposalSubmitted {
            proposal_id: u32,
            proposer: T::AccountId,
            proposal_type: ProposalType,
            voting_period_end: BlockNumberFor<T>,
        },
        /// Vote cast on proposal
        VotedOnProposal {
            proposal_id: u32,
            voter: T::AccountId,
            direction: VoteDirection,
            voting_power: BalanceOf<T>,
        },
        /// Voting power delegated
        VotesDelegated {
            delegator: T::AccountId,
            delegate: T::AccountId,
        },
        /// Proposal passed and ready for execution
        ProposalPassed {
            proposal_id: u32,
        },
        /// Proposal rejected
        ProposalRejected {
            proposal_id: u32,
        },
        /// Proposal executed (treasury spend / parameter change applied)
        ProposalExecuted {
            proposal_id: u32,
            executor: T::AccountId,
        },
        /// Treasury received funds (protocol revenue)
        TreasuryCollected {
            from: T::AccountId,
            amount: BalanceOf<T>,
        },
        /// Treasury allocated to category (e.g. reward pool, dev fund)
        TreasuryAllocated {
            category: TreasuryAllocationCategory,
            amount: BalanceOf<T>,
        },
        /// Grant claimed by beneficiary
        TreasuryGrantClaimed {
            beneficiary: T::AccountId,
            proposal_id: u32,
            amount: BalanceOf<T>,
        },
        /// Voting parameters updated
        VotingParametersUpdated {
            min_quorum_permille: u32,
            approval_threshold_permille: u32,
        },
    }

    /// Errors that can occur in this pallet
    #[pallet::error]
    pub enum Error<T> {
        /// Insufficient balance
        InsufficientBalance,
        /// Transfer amount is zero
        ZeroAmount,
        /// Account does not exist
        AccountNotFound,
        /// Invalid reward type
        InvalidRewardType,
        /// Achievement already unlocked
        AchievementAlreadyUnlocked,
        /// Achievement limit reached
        AchievementLimitReached,
        /// Reward history limit reached
        RewardHistoryLimitReached,
        /// Allowance exceeded
        AllowanceExceeded,
        /// Insufficient allowance
        InsufficientAllowance,
        /// No vesting schedule found
        NoVestingSchedule,
        /// Nothing to vest at this block
        NothingToVest,
        /// Insufficient staked balance
        InsufficientStaked,
        /// Stake below minimum (100,000 ABENA)
        StakeBelowMinimum,
        /// Invalid vesting schedule (e.g. release_per_block zero or duration mismatch)
        InvalidVestingSchedule,
        /// Patient reward pool exhausted
        RewardPoolExhausted,
        /// Total supply cap exceeded (1 billion ABENA)
        SupplyCapExceeded,
        /// Too many vesting schedules for account
        TooManyVestingSchedules,
        /// Achievement definition not found
        AchievementNotFound,
        /// Achievement not repeatable and already claimed
        AchievementAlreadyClaimed,
        /// Achievement not verified (verification required)
        AchievementNotVerified,
        /// Self-report rate limit: cooldown not elapsed
        SelfReportRateLimited,
        /// Referrer already set (can only set once)
        ReferrerAlreadySet,
        /// Cannot refer self
        CannotReferSelf,
        /// Referral limit reached for referrer
        ReferralLimitReached,
        /// Invalid achievement definition (e.g. empty name)
        InvalidAchievementDefinition,
        /// Proposal not found
        ProposalNotFound,
        /// Proposal not in Active state
        ProposalNotActive,
        /// Voting period ended
        VotingPeriodEnded,
        /// Deposit below minimum
        InsufficientProposalDeposit,
        /// Already voted on this proposal
        AlreadyVoted,
        /// Cannot delegate to self
        CannotDelegateToSelf,
        /// Treasury balance insufficient
        InsufficientTreasuryBalance,
        /// Proposal did not pass (quorum or approval threshold)
        ProposalDidNotPass,
        /// No grant to claim for this beneficiary and proposal
        NoGrantToClaim,
        /// Quorum or threshold out of range
        InvalidVotingParameters,
    }

    /// Hooks for the pallet
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    /// Extrinsics for the pallet
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Mint new ABENA Coins (typically called by system for rewards)
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::mint())]
        pub fn mint(
            origin: OriginFor<T>,
            to: T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;

            ensure!(amount > Zero::zero(), Error::<T>::ZeroAmount);

            let supply = TotalSupply::<T>::get();
            let new_supply = supply.checked_add(&amount).ok_or(Error::<T>::InsufficientBalance)?;
            ensure!(new_supply <= Self::total_supply_cap(), Error::<T>::SupplyCapExceeded);

            let current_balance = Balances::<T>::get(&to);
            let new_balance = current_balance
                .checked_add(&amount)
                .ok_or(Error::<T>::InsufficientBalance)?;

            Balances::<T>::insert(&to, new_balance);
            TotalSupply::<T>::put(new_supply);

            Self::deposit_event(Event::CoinsMinted {
                account: to,
                amount,
            });

            Ok(())
        }

        /// Burn ABENA Coins
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::burn())]
        pub fn burn(
            origin: OriginFor<T>,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let account = ensure_signed(origin)?;

            ensure!(amount > Zero::zero(), Error::<T>::ZeroAmount);

            let current_balance = Balances::<T>::get(&account);
            ensure!(
                current_balance >= amount,
                Error::<T>::InsufficientBalance
            );

            let new_balance = current_balance - amount;
            Balances::<T>::insert(&account, new_balance);
            TotalSupply::<T>::mutate(|supply| *supply -= amount);

            Self::deposit_event(Event::CoinsBurned {
                account,
                amount,
            });

            Ok(())
        }

        /// Transfer ABENA Coins to another account
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::transfer())]
        pub fn transfer(
            origin: OriginFor<T>,
            to: T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let from = ensure_signed(origin)?;

            ensure!(amount > Zero::zero(), Error::<T>::ZeroAmount);
            ensure!(from != to, Error::<T>::ZeroAmount);

            let from_balance = Balances::<T>::get(&from);
            ensure!(
                from_balance >= amount,
                Error::<T>::InsufficientBalance
            );

            let new_from_balance = from_balance - amount;
            let to_balance = Balances::<T>::get(&to);
            let new_to_balance = to_balance + amount;

            Balances::<T>::insert(&from, new_from_balance);
            Balances::<T>::insert(&to, new_to_balance);

            Self::deposit_event(Event::CoinsTransferred {
                from,
                to,
                amount,
            });

            Ok(())
        }

        /// Grant reward for gamification activities
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::grant_reward())]
        pub fn grant_reward(
            origin: OriginFor<T>,
            account: T::AccountId,
            reward_type: RewardType,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;

            ensure!(amount > Zero::zero(), Error::<T>::ZeroAmount);

            // Mint coins to the account
            Self::mint_internal(&account, amount)?;

            // Record reward history
            let entry = RewardEntry::<T> {
                amount,
                block_number: <frame_system::Pallet<T>>::block_number(),
            };
            RewardHistory::<T>::mutate(&account, &reward_type, |history| {
                match history {
                    Some(ref mut vec) => {
                        let _ = vec.try_push(entry.clone());
                    },
                    None => {
                        let mut new_vec = BoundedVec::default();
                        if new_vec.try_push(entry).is_ok() {
                            *history = Some(new_vec);
                        }
                    }
                }
            });

            // Check for achievements
            Self::check_achievements(&account)?;

            Self::deposit_event(Event::RewardGranted {
                account,
                reward_type,
                amount,
            });

            Ok(())
        }

        /// Claim achievement reward
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::claim_achievement())]
        pub fn claim_achievement(
            origin: OriginFor<T>,
            achievement: AchievementType,
        ) -> DispatchResult {
            let account = ensure_signed(origin)?;

            let mut achievements = Achievements::<T>::get(&account);
            
            // Check if achievement is already unlocked
            if achievements.unlocked_achievements.contains(&achievement) {
                return Err(Error::<T>::AchievementAlreadyUnlocked.into());
            }

            // Unlock achievement
            achievements.unlocked_achievements.try_push(achievement.clone())
                .map_err(|_| Error::<T>::AchievementLimitReached)?;
            achievements.total_achievements += 1;

            // Grant reward for achievement
            let reward_amount = Self::get_achievement_reward(&achievement);
            Self::mint_internal(&account, reward_amount)?;

            Achievements::<T>::insert(&account, achievements);

            Self::deposit_event(Event::AchievementUnlocked {
                account,
                achievement,
            });

            Ok(())
        }

        /// Approve delegated spending (ERC-20 style)
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::approve())]
        pub fn approve(
            origin: OriginFor<T>,
            spender: T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let owner = ensure_signed(origin)?;
            Allowances::<T>::insert(&owner, &spender, amount);
            Self::deposit_event(Event::Approved {
                owner,
                spender,
                amount,
            });
            Ok(())
        }

        /// Transfer tokens on behalf of another account (requires allowance)
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::transfer_from())]
        pub fn transfer_from(
            origin: OriginFor<T>,
            owner: T::AccountId,
            to: T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let spender = ensure_signed(origin)?;
            ensure!(amount > Zero::zero(), Error::<T>::ZeroAmount);

            let allowance = Allowances::<T>::get(&owner, &spender);
            ensure!(allowance >= amount, Error::<T>::InsufficientAllowance);

            let owner_balance = Balances::<T>::get(&owner);
            ensure!(owner_balance >= amount, Error::<T>::InsufficientBalance);

            Allowances::<T>::mutate(&owner, &spender, |a| *a -= amount);
            Balances::<T>::mutate(&owner, |b| *b -= amount);
            Balances::<T>::mutate(&to, |b| *b += amount);

            Self::deposit_event(Event::TransferFrom {
                owner,
                spender,
                to,
                amount,
            });
            Ok(())
        }

        /// Stake tokens for commercial entity tier (min 100,000 ABENA)
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::stake())]
        pub fn stake(
            origin: OriginFor<T>,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let account = ensure_signed(origin)?;
            let min_stake = Self::min_stake_for_tier(StakingTier::Bronze);
            ensure!(amount >= min_stake, Error::<T>::StakeBelowMinimum);

            let balance = Balances::<T>::get(&account);
            ensure!(balance >= amount, Error::<T>::InsufficientBalance);

            Balances::<T>::mutate(&account, |b| *b -= amount);
            let new_staked = StakedBalances::<T>::get(&account).saturating_add(amount);
            StakedBalances::<T>::insert(&account, new_staked);
            let tier = Self::tier_from_stake(new_staked);
            StakingTiers::<T>::insert(&account, tier);

            Self::deposit_event(Event::Staked {
                account,
                amount,
                tier,
            });
            Ok(())
        }

        /// Unstake tokens (no slashing here; data-marketplace handles violations)
        #[pallet::call_index(8)]
        #[pallet::weight(T::WeightInfo::unstake())]
        pub fn unstake(
            origin: OriginFor<T>,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let account = ensure_signed(origin)?;
            ensure!(amount > Zero::zero(), Error::<T>::ZeroAmount);

            let staked = StakedBalances::<T>::get(&account);
            ensure!(staked >= amount, Error::<T>::InsufficientStaked);

            StakedBalances::<T>::mutate(&account, |s| *s -= amount);
            Balances::<T>::mutate(&account, |b| *b += amount);

            let new_staked = staked - amount;
            if new_staked.is_zero() {
                StakingTiers::<T>::remove(&account);
            } else {
                StakingTiers::<T>::insert(&account, Self::tier_from_stake(new_staked));
            }

            Self::deposit_event(Event::Unstaked { account, amount });
            Ok(())
        }

        /// Claim vested tokens according to schedule(s)
        #[pallet::call_index(9)]
        #[pallet::weight(T::WeightInfo::claim_vested_tokens())]
        pub fn claim_vested_tokens(origin: OriginFor<T>) -> DispatchResult {
            let account = ensure_signed(origin)?;
            let mut schedules = VestingSchedules::<T>::get(&account)
                .ok_or(Error::<T>::NoVestingSchedule)?;

            let now = <frame_system::Pallet<T>>::block_number();
            let mut total_claimed = BalanceOf::<T>::zero();

            for schedule in schedules.iter_mut() {
                let cliff_end = schedule.start_block.saturating_add(schedule.cliff_duration);
                if now < cliff_end {
                    continue;
                }
                // vesting_duration runs AFTER the cliff, so end = start + cliff + vesting.
                let vesting_end = cliff_end.saturating_add(schedule.vesting_duration);
                let blocks_elapsed = now.min(vesting_end).saturating_sub(cliff_end);
                let blocks_balance: BalanceOf<T> = blocks_elapsed.saturated_into::<u64>().saturated_into();
                // Compute total tokens releasable so far (cumulative), capped at total_amount.
                let total_releasable = schedule
                    .release_per_block
                    .saturating_mul(blocks_balance)
                    .min(schedule.total_amount);
                // Incremental = cumulative releasable - already released.
                let to_release = total_releasable.saturating_sub(schedule.released_amount);
                if to_release.is_zero() {
                    continue;
                }
                schedule.released_amount = schedule.released_amount.saturating_add(to_release);
                total_claimed = total_claimed.saturating_add(to_release);
            }

            ensure!(!total_claimed.is_zero(), Error::<T>::NothingToVest);

            VestingSchedules::<T>::insert(&account, schedules);
            Balances::<T>::mutate(&account, |b| *b += total_claimed);

            Self::deposit_event(Event::VestedTokensClaimed {
                account,
                amount: total_claimed,
            });
            Ok(())
        }

        /// Distribute patient reward from the reward pool (origin: root or authorized)
        #[pallet::call_index(10)]
        #[pallet::weight(T::WeightInfo::distribute_patient_reward())]
        pub fn distribute_patient_reward(
            origin: OriginFor<T>,
            patient: T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;
            ensure!(amount > Zero::zero(), Error::<T>::ZeroAmount);

            let pool = RewardPool::<T>::get();
            ensure!(pool >= amount, Error::<T>::RewardPoolExhausted);

            RewardPool::<T>::mutate(|p| *p -= amount);
            Balances::<T>::mutate(&patient, |b| *b += amount);
            LifetimeEarnings::<T>::mutate(&patient, |e| *e += amount);

            Self::deposit_event(Event::PatientRewardDistributed {
                account: patient,
                amount,
            });
            Ok(())
        }

        /// Record governance vote (voting power = caller balance; actual proposal in governance pallet)
        #[pallet::call_index(11)]
        #[pallet::weight(T::WeightInfo::vote())]
        pub fn vote(
            origin: OriginFor<T>,
            proposal_id: u32,
        ) -> DispatchResult {
            let account = ensure_signed(origin)?;
            let voting_power = Balances::<T>::get(&account);
            ensure!(voting_power > Zero::zero(), Error::<T>::InsufficientBalance);

            Self::deposit_event(Event::Voted {
                account,
                proposal_id,
                voting_power,
            });
            Ok(())
        }

        /// Fee abstraction: payer pays on behalf of patient (e.g. provider pays gas for patient)
        #[pallet::call_index(12)]
        #[pallet::weight(T::WeightInfo::pay_on_behalf())]
        pub fn pay_on_behalf(
            origin: OriginFor<T>,
            patient: T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let payer = ensure_signed(origin)?;
            ensure!(amount > Zero::zero(), Error::<T>::ZeroAmount);

            let balance = Balances::<T>::get(&payer);
            ensure!(balance >= amount, Error::<T>::InsufficientBalance);

            Balances::<T>::mutate(&payer, |b| *b -= amount);
            Balances::<T>::mutate(&patient, |b| *b += amount);

            Self::deposit_event(Event::FeePaidOnBehalf {
                payer,
                patient,
                amount,
            });
            Ok(())
        }

        /// Add a vesting schedule (root only; for team/investors)
        #[pallet::call_index(13)]
        #[pallet::weight(T::WeightInfo::add_vesting_schedule())]
        pub fn add_vesting_schedule(
            origin: OriginFor<T>,
            account: T::AccountId,
            total_amount: BalanceOf<T>,
            start_block: BlockNumberFor<T>,
            cliff_duration: BlockNumberFor<T>,
            vesting_duration: BlockNumberFor<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;
            ensure!(total_amount > Zero::zero(), Error::<T>::ZeroAmount);
            ensure!(vesting_duration > Zero::zero(), Error::<T>::InvalidVestingSchedule);

            let vesting_balance: BalanceOf<T> = vesting_duration.saturated_into::<u64>().saturated_into();
            let release_per_block = total_amount
                .checked_div(&vesting_balance)
                .ok_or(Error::<T>::InvalidVestingSchedule)?;
            ensure!(!release_per_block.is_zero(), Error::<T>::InvalidVestingSchedule);

            let schedule = VestingSchedule::<T> {
                total_amount,
                released_amount: Zero::zero(),
                start_block,
                cliff_duration,
                vesting_duration,
                release_per_block,
            };

            let max = T::MaxVestingSchedules::get() as usize;
            let mut schedules = VestingSchedules::<T>::get(&account)
                .unwrap_or_else(|| BoundedVec::default());
            ensure!(schedules.len() < max, Error::<T>::TooManyVestingSchedules);
            schedules
                .try_push(schedule)
                .map_err(|_| Error::<T>::TooManyVestingSchedules)?;

            VestingSchedules::<T>::insert(&account, schedules);
            Ok(())
        }

        /// Fund the patient reward pool (root only). Increases TotalSupply and RewardPool.
        #[pallet::call_index(14)]
        #[pallet::weight(T::WeightInfo::fund_reward_pool())]
        pub fn fund_reward_pool(
            origin: OriginFor<T>,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;
            ensure!(amount > Zero::zero(), Error::<T>::ZeroAmount);

            let supply = TotalSupply::<T>::get();
            let new_supply = supply.checked_add(&amount).ok_or(Error::<T>::InsufficientBalance)?;
            ensure!(new_supply <= Self::total_supply_cap(), Error::<T>::SupplyCapExceeded);

            TotalSupply::<T>::put(new_supply);
            RewardPool::<T>::mutate(|p| *p += amount);
            Ok(())
        }

        /// Create a new achievement definition (governance / root).
        #[pallet::call_index(15)]
        #[pallet::weight(T::WeightInfo::create_achievement())]
        pub fn create_achievement(
            origin: OriginFor<T>,
            category: AchievementCategory,
            name: BoundedVec<u8, ConstU32<64>>,
            description: BoundedVec<u8, ConstU32<128>>,
            base_reward: BalanceOf<T>,
            repeatable: bool,
            requirements: BoundedVec<AchievementRequirement<T>, ConstU32<8>>,
            verification_method: VerificationMethod,
        ) -> DispatchResult {
            ensure_root(origin)?;
            ensure!(!name.is_empty(), Error::<T>::InvalidAchievementDefinition);
            ensure!(base_reward > Zero::zero(), Error::<T>::ZeroAmount);

            let id = NextAchievementId::<T>::get();
            let next_id = id.saturating_add(1);
            NextAchievementId::<T>::put(next_id);

            let def = AchievementDefinition::<T> {
                achievement_id: id,
                category,
                name,
                description,
                base_reward,
                repeatable,
                requirements,
                verification_method,
            };
            AchievementDefinitions::<T>::insert(id, def);

            Self::deposit_event(Event::AchievementCreated {
                achievement_id: id,
                category,
                base_reward,
            });
            Ok(())
        }

        /// Claim a gamification achievement (after verification if required).
        #[pallet::call_index(16)]
        #[pallet::weight(T::WeightInfo::claim_gamification_achievement())]
        pub fn claim_gamification_achievement(
            origin: OriginFor<T>,
            achievement_id: u32,
        ) -> DispatchResult {
            let account = ensure_signed(origin)?;

            let def = AchievementDefinitions::<T>::get(achievement_id)
                .ok_or(Error::<T>::AchievementNotFound)?;

            let now = <frame_system::Pallet<T>>::block_number();
            let status = PatientAchievements::<T>::get(&account, achievement_id);

            if !def.repeatable {
                // A status entry may exist because verify_achievement wrote it before the
                // first claim. Only reject if the player has already claimed at least once.
                if let Some(ref st) = status {
                    if st.claim_count > 0 {
                        return Err(Error::<T>::AchievementAlreadyClaimed.into());
                    }
                }
            }

            match def.verification_method {
                VerificationMethod::SelfReported => {
                    let cooldown = T::SelfReportCooldownBlocks::get();
                    if let Some(last) = SelfReportLastClaim::<T>::get(&account, achievement_id) {
                        ensure!(now >= last.saturating_add(cooldown), Error::<T>::SelfReportRateLimited);
                    }
                    SelfReportLastClaim::<T>::insert(&account, achievement_id, now);
                }
                _ => {
                    let st = status.as_ref().ok_or(Error::<T>::AchievementNotVerified)?;
                    ensure!(st.verified, Error::<T>::AchievementNotVerified);
                }
            }

            let multiplier_mille = Self::calculate_multiplier(&account, def.category);
            let reward = def.base_reward.saturating_mul(multiplier_mille.saturated_into())
                .checked_div(&1000u32.saturated_into())
                .unwrap_or_else(Zero::zero);

            Self::mint_internal(&account, reward)?;
            LifetimeEarnings::<T>::mutate(&account, |e| *e += reward);

            let new_count = status.as_ref().map(|s| s.claim_count.saturating_add(1)).unwrap_or(1);
            let verified_next = !def.repeatable && def.verification_method != VerificationMethod::SelfReported;
            PatientAchievements::<T>::insert(&account, achievement_id, CompletionStatus::<T> {
                completed_at: now,
                claim_count: new_count,
                verified: verified_next,
            });

            LeaderboardScores::<T>::mutate(&account, |s| *s += reward.saturated_into::<u64>());

            Self::deposit_event(Event::GamificationAchievementClaimed {
                account: account.clone(),
                achievement_id,
                amount: reward,
                multiplier_mille,
            });

            if let Some(referrer) = ReferrerOf::<T>::get(&account) {
                let bonus = BalanceOf::<T>::saturated_from(20_000_000_000_000_000_000u128); // 20 ABENA
                let _ = Self::distribute_referral_bonus_internal(&referrer, &account, bonus);
            }

            Ok(())
        }

        /// Verify achievement completion (provider / root). Patient can then claim.
        #[pallet::call_index(17)]
        #[pallet::weight(T::WeightInfo::verify_achievement())]
        pub fn verify_achievement(
            origin: OriginFor<T>,
            patient: T::AccountId,
            achievement_id: u32,
        ) -> DispatchResult {
            ensure_root(origin)?;
            AchievementDefinitions::<T>::get(achievement_id)
                .ok_or(Error::<T>::AchievementNotFound)?;

            let now = <frame_system::Pallet<T>>::block_number();
            let status = PatientAchievements::<T>::get(&patient, achievement_id)
                .map(|mut s| {
                    s.verified = true;
                    s.completed_at = now;
                    s
                })
                .unwrap_or(CompletionStatus::<T> {
                    completed_at: now,
                    claim_count: 0,
                    verified: true,
                });
            PatientAchievements::<T>::insert(&patient, achievement_id, status);

            Self::deposit_event(Event::AchievementVerified {
                account: patient,
                achievement_id,
            });
            Ok(())
        }

        /// Award streak bonus (root / automated).
        #[pallet::call_index(18)]
        #[pallet::weight(T::WeightInfo::award_streak_bonus())]
        pub fn award_streak_bonus(
            origin: OriginFor<T>,
            account: T::AccountId,
            streak_type: StreakType,
            bonus: BalanceOf<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;
            ensure!(bonus > Zero::zero(), Error::<T>::ZeroAmount);

            let info = StreakTracking::<T>::get(&account, streak_type)
                .unwrap_or(StreakInfo::<T> {
                    current_streak: 0,
                    longest_streak: 0,
                    last_activity_block: Zero::zero(),
                });
            Self::mint_internal(&account, bonus)?;
            LifetimeEarnings::<T>::mutate(&account, |e| *e += bonus);

            Self::deposit_event(Event::StreakBonusAwarded {
                account,
                streak_type,
                streak_length: info.current_streak.max(info.longest_streak),
                bonus,
            });
            Ok(())
        }

        /// Update streak (e.g. daily login or activity). Called by patient or relayer.
        #[pallet::call_index(19)]
        #[pallet::weight(T::WeightInfo::update_streak())]
        pub fn update_streak(
            origin: OriginFor<T>,
            streak_type: StreakType,
        ) -> DispatchResult {
            let account = ensure_signed(origin)?;
            let now = <frame_system::Pallet<T>>::block_number();

            let mut info = StreakTracking::<T>::get(&account, streak_type)
                .unwrap_or(StreakInfo::<T> {
                    current_streak: 0,
                    longest_streak: 0,
                    last_activity_block: Zero::zero(),
                });

            let blocks_per_day: BlockNumberFor<T> = 7200u32.saturated_into();
            let two: BlockNumberFor<T> = 2u32.saturated_into();
            let gap = now.saturating_sub(info.last_activity_block);
            if gap > blocks_per_day.saturating_mul(two) {
                info.current_streak = 1;
            } else if gap <= blocks_per_day {
                info.current_streak = info.current_streak.saturating_add(1);
            }
            info.longest_streak = info.longest_streak.max(info.current_streak);
            info.last_activity_block = now;
            StreakTracking::<T>::insert(&account, streak_type, info);
            Ok(())
        }

        /// Register referral: referrer invites referred (one-time per referred).
        #[pallet::call_index(20)]
        #[pallet::weight(T::WeightInfo::register_referral())]
        pub fn register_referral(
            origin: OriginFor<T>,
            referrer: T::AccountId,
        ) -> DispatchResult {
            let referred = ensure_signed(origin)?;
            ensure!(referred != referrer, Error::<T>::CannotReferSelf);
            ensure!(ReferrerOf::<T>::get(&referred).is_none(), Error::<T>::ReferrerAlreadySet);

            let max = 100u32;
            let mut children = ReferralChildren::<T>::get(&referrer)
                .unwrap_or_else(|| BoundedVec::default());
            ensure!(children.len() < max as usize, Error::<T>::ReferralLimitReached);
            children.try_push(referred.clone()).map_err(|_| Error::<T>::ReferralLimitReached)?;

            ReferralChildren::<T>::insert(&referrer, children);
            ReferrerOf::<T>::insert(&referred, referrer.clone());

            Self::deposit_event(Event::ReferralRegistered {
                referrer,
                referred,
            });
            Ok(())
        }

        /// Set seasonal multiplier (e.g. double rewards). Root only.
        #[pallet::call_index(21)]
        #[pallet::weight(T::WeightInfo::set_seasonal_multiplier())]
        pub fn set_seasonal_multiplier(
            origin: OriginFor<T>,
            start_block: BlockNumberFor<T>,
            end_block: BlockNumberFor<T>,
            multiplier_mille: u32,
        ) -> DispatchResult {
            ensure_root(origin)?;
            ensure!(multiplier_mille >= 1000 && multiplier_mille <= 5000, Error::<T>::InvalidAchievementDefinition);
            SeasonalMultiplier::<T>::put((start_block, end_block, multiplier_mille));
            Self::deposit_event(Event::SeasonalMultiplierSet {
                start_block,
                end_block,
                multiplier_mille,
            });
            Ok(())
        }

        // ---------- Treasury & Governance calls ----------

        /// Submit a governance proposal (deposit required).
        #[pallet::call_index(22)]
        #[pallet::weight(T::WeightInfo::submit_proposal())]
        pub fn submit_proposal(
            origin: OriginFor<T>,
            proposal_type: ProposalType,
            description_hash: T::Hash,
            requested_amount: Option<BalanceOf<T>>,
            beneficiary: Option<T::AccountId>,
        ) -> DispatchResult {
            let proposer = ensure_signed(origin)?;
            let deposit = T::MinProposalDeposit::get();
            let balance = Balances::<T>::get(&proposer);
            ensure!(balance >= deposit, Error::<T>::InsufficientProposalDeposit);

            let now = <frame_system::Pallet<T>>::block_number();
            let period = T::VotingPeriodBlocks::get();
            let voting_period_end = now.saturating_add(period);

            let id = NextProposalId::<T>::get();
            NextProposalId::<T>::put(id.saturating_add(1));

            Balances::<T>::mutate(&proposer, |b| *b -= deposit);
            ProposalDeposits::<T>::insert(id, (proposer.clone(), deposit));

            let proposal = Proposal::<T> {
                proposal_id: id,
                proposer: proposer.clone(),
                proposal_type,
                description_hash,
                requested_amount,
                beneficiary,
                voting_period_end,
                yes_votes: Zero::zero(),
                no_votes: Zero::zero(),
                status: ProposalStatus::Active,
                created_at: now,
            };
            Proposals::<T>::insert(id, proposal);

            Self::deposit_event(Event::ProposalSubmitted {
                proposal_id: id,
                proposer,
                proposal_type,
                voting_period_end,
            });
            Ok(())
        }

        /// Vote on a proposal (1 ABENA = 1 vote; conviction_blocks locks for extra weight).
        #[pallet::call_index(23)]
        #[pallet::weight(T::WeightInfo::vote_on_proposal())]
        pub fn vote_on_proposal(
            origin: OriginFor<T>,
            proposal_id: u32,
            direction: VoteDirection,
            voting_power: BalanceOf<T>,
            conviction_blocks: BlockNumberFor<T>,
        ) -> DispatchResult {
            let voter = ensure_signed(origin)?;
            ensure!(voting_power > Zero::zero(), Error::<T>::ZeroAmount);

            let mut prop = Proposals::<T>::get(proposal_id).ok_or(Error::<T>::ProposalNotFound)?;
            ensure!(prop.status == ProposalStatus::Active, Error::<T>::ProposalNotActive);
            let now = <frame_system::Pallet<T>>::block_number();
            ensure!(now < prop.voting_period_end, Error::<T>::VotingPeriodEnded);

            let effective_voter = DelegatedVotes::<T>::get(&voter).unwrap_or(voter.clone());
            let balance = Balances::<T>::get(&effective_voter);
            ensure!(voting_power <= balance, Error::<T>::InsufficientBalance);
            ensure!(Votes::<T>::get(proposal_id, &voter).is_none(), Error::<T>::AlreadyVoted);

            let period = prop.voting_period_end.saturating_sub(prop.created_at);
            let weight = Self::conviction_multiplier(conviction_blocks, period);
            let weighted_power = voting_power.saturating_mul(weight.saturated_into())
                .checked_div(&1000u32.saturated_into())
                .unwrap_or_else(Zero::zero);

            let record = VoteRecord::<T> {
                direction: direction.clone(),
                voting_power,
                conviction_blocks,
            };
            Votes::<T>::insert(proposal_id, &voter, &record);

            if direction == VoteDirection::Yes {
                prop.yes_votes = prop.yes_votes.saturating_add(weighted_power);
            } else {
                prop.no_votes = prop.no_votes.saturating_add(weighted_power);
            }
            Proposals::<T>::insert(proposal_id, prop);

            Self::deposit_event(Event::VotedOnProposal {
                proposal_id,
                voter,
                direction,
                voting_power,
            });
            Ok(())
        }

        /// Delegate voting power to another account.
        #[pallet::call_index(24)]
        #[pallet::weight(T::WeightInfo::delegate_votes())]
        pub fn delegate_votes(
            origin: OriginFor<T>,
            delegate: T::AccountId,
        ) -> DispatchResult {
            let delegator = ensure_signed(origin)?;
            ensure!(delegator != delegate, Error::<T>::CannotDelegateToSelf);
            DelegatedVotes::<T>::insert(&delegator, &delegate);
            Self::deposit_event(Event::VotesDelegated {
                delegator,
                delegate,
            });
            Ok(())
        }

        /// Execute a passed proposal (anyone can call after voting period; refunds deposit on success).
        #[pallet::call_index(25)]
        #[pallet::weight(T::WeightInfo::execute_proposal())]
        pub fn execute_proposal(
            origin: OriginFor<T>,
            proposal_id: u32,
        ) -> DispatchResult {
            let executor = ensure_signed(origin)?;

            let mut prop = Proposals::<T>::get(proposal_id).ok_or(Error::<T>::ProposalNotFound)?;
            ensure!(prop.status == ProposalStatus::Active, Error::<T>::ProposalNotActive);
            let now = <frame_system::Pallet<T>>::block_number();
            ensure!(now >= prop.voting_period_end, Error::<T>::VotingPeriodEnded);

            let params = VotingParameters::<T>::get().unwrap_or(VotingParams::<T> {
                min_quorum_permille: T::MinQuorumPermille::get(),
                approval_threshold_permille: T::ApprovalThresholdPermille::get(),
                voting_period_blocks: T::VotingPeriodBlocks::get(),
            });
            let total = prop.yes_votes.saturating_add(prop.no_votes);
            let supply = TotalSupply::<T>::get();
            let quorum_votes = supply.saturating_mul(params.min_quorum_permille.saturated_into())
                .checked_div(&1000u32.saturated_into())
                .unwrap_or_else(Zero::zero);
            ensure!(total >= quorum_votes, Error::<T>::ProposalDidNotPass);
            ensure!(!total.is_zero(), Error::<T>::ProposalDidNotPass);

            let threshold = prop.yes_votes.saturating_mul(1000u32.saturated_into())
                .checked_div(&total)
                .unwrap_or_else(Zero::zero);
            let required = params.approval_threshold_permille;
            // Strictly greater than the threshold permille (e.g. >500 = clear majority).
            ensure!(threshold > required.saturated_into(), Error::<T>::ProposalDidNotPass);

            prop.status = ProposalStatus::Executed;
            if let (Some(amount), Some(beneficiary)) = (prop.requested_amount.clone(), prop.beneficiary.clone()) {
                let treasury = TreasuryBalance::<T>::get();
                ensure!(treasury >= amount, Error::<T>::InsufficientTreasuryBalance);
                TreasuryBalance::<T>::mutate(|t| *t -= amount);
                ApprovedGrants::<T>::insert(&beneficiary, proposal_id, amount);
            }

            if let Some((proposer, deposit)) = ProposalDeposits::<T>::take(proposal_id) {
                Balances::<T>::mutate(&proposer, |b| *b += deposit);
            }

            Proposals::<T>::insert(proposal_id, prop);
            Self::deposit_event(Event::ProposalExecuted {
                proposal_id,
                executor,
            });
            Ok(())
        }

        /// Allocate treasury funds to a category (e.g. reward pool, dev fund). Root or via passed proposal.
        #[pallet::call_index(26)]
        #[pallet::weight(T::WeightInfo::treasury_allocate())]
        pub fn treasury_allocate(
            origin: OriginFor<T>,
            category: TreasuryAllocationCategory,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;
            ensure!(amount > Zero::zero(), Error::<T>::ZeroAmount);

            let treasury = TreasuryBalance::<T>::get();
            ensure!(treasury >= amount, Error::<T>::InsufficientTreasuryBalance);

            match category {
                TreasuryAllocationCategory::PatientRewardPool => {
                    TreasuryBalance::<T>::mutate(|t| *t -= amount);
                    RewardPool::<T>::mutate(|p| *p += amount);
                }
                TreasuryAllocationCategory::Development
                | TreasuryAllocationCategory::Marketing
                | TreasuryAllocationCategory::EmergencyReserve
                | TreasuryAllocationCategory::CommunityGrant => {
                    // Allocated conceptually; actual spend via proposals. No balance move here.
                }
            }
            Self::deposit_event(Event::TreasuryAllocated { category, amount });
            Ok(())
        }

        /// Claim an approved treasury grant (beneficiary).
        #[pallet::call_index(27)]
        #[pallet::weight(T::WeightInfo::claim_treasury_grant())]
        pub fn claim_treasury_grant(
            origin: OriginFor<T>,
            proposal_id: u32,
        ) -> DispatchResult {
            let beneficiary = ensure_signed(origin)?;
            let amount = ApprovedGrants::<T>::take(&beneficiary, proposal_id)
                .ok_or(Error::<T>::NoGrantToClaim)?;

            let now = <frame_system::Pallet<T>>::block_number();
            let record = SpendingRecord::<T> {
                proposal_id,
                beneficiary: beneficiary.clone(),
                amount,
                category: TreasuryAllocationCategory::CommunityGrant,
                block: now,
            };
            SpendingHistory::<T>::mutate(|h| {
                while h.len() >= 200 {
                    h.remove(0);
                }
                let _ = h.try_push(record);
            });

            Self::mint_internal(&beneficiary, amount)?;
            Self::deposit_event(Event::TreasuryGrantClaimed {
                beneficiary,
                proposal_id,
                amount,
            });
            Ok(())
        }

        /// Collect protocol revenue into treasury (from marketplace, fees, etc.).
        #[pallet::call_index(28)]
        #[pallet::weight(T::WeightInfo::collect_to_treasury())]
        pub fn collect_to_treasury(
            origin: OriginFor<T>,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let from = ensure_signed(origin)?;
            ensure!(amount > Zero::zero(), Error::<T>::ZeroAmount);
            let balance = Balances::<T>::get(&from);
            ensure!(balance >= amount, Error::<T>::InsufficientBalance);

            Balances::<T>::mutate(&from, |b| *b -= amount);
            TreasuryBalance::<T>::mutate(|t| *t += amount);

            Self::deposit_event(Event::TreasuryCollected {
                from,
                amount,
            });
            Ok(())
        }

        /// Update voting parameters (governance or root).
        #[pallet::call_index(29)]
        #[pallet::weight(T::WeightInfo::update_voting_parameters())]
        pub fn update_voting_parameters(
            origin: OriginFor<T>,
            min_quorum_permille: u32,
            approval_threshold_permille: u32,
            voting_period_blocks: BlockNumberFor<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;
            ensure!(min_quorum_permille <= 1000 && approval_threshold_permille <= 1000, Error::<T>::InvalidVotingParameters);

            VotingParameters::<T>::put(VotingParams::<T> {
                min_quorum_permille,
                approval_threshold_permille,
                voting_period_blocks,
            });
            Self::deposit_event(Event::VotingParametersUpdated {
                min_quorum_permille,
                approval_threshold_permille,
            });
            Ok(())
        }
    }

    /// Internal functions
    impl<T: Config> Pallet<T> {
        /// Total supply cap: 1 billion ABENA (10^18 decimals)
        fn total_supply_cap() -> BalanceOf<T> {
            let one_billion = 1_000_000_000u128;
            let ten_18 = 1_000_000_000_000_000_000u128;
            one_billion.saturating_mul(ten_18).saturated_into()
        }

        /// Internal mint function (checks supply cap)
        fn mint_internal(
            account: &T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let supply = TotalSupply::<T>::get();
            let new_supply = supply.checked_add(&amount).ok_or(Error::<T>::InsufficientBalance)?;
            ensure!(new_supply <= Self::total_supply_cap(), Error::<T>::SupplyCapExceeded);

            let current_balance = Balances::<T>::get(account);
            let new_balance = current_balance
                .checked_add(&amount)
                .ok_or(Error::<T>::InsufficientBalance)?;

            Balances::<T>::insert(account, new_balance);
            TotalSupply::<T>::put(new_supply);

            Ok(())
        }

        /// Minimum stake per tier (in raw units, 18 decimals)
        fn min_stake_for_tier(tier: StakingTier) -> BalanceOf<T> {
            let (v, _) = match tier {
                StakingTier::Bronze => (100_000u128, 0u128),
                StakingTier::Silver => (500_000u128, 0u128),
                StakingTier::Gold => (1_000_000u128, 0u128),
                StakingTier::Platinum => (5_000_000u128, 0u128),
            };
            let ten_18 = 1_000_000_000_000_000_000u128;
            v.saturating_mul(ten_18).saturated_into()
        }

        /// Compute tier from total staked amount
        fn tier_from_stake(staked: BalanceOf<T>) -> StakingTier {
            let platinum = Self::min_stake_for_tier(StakingTier::Platinum);
            let gold = Self::min_stake_for_tier(StakingTier::Gold);
            let silver = Self::min_stake_for_tier(StakingTier::Silver);
            if staked >= platinum {
                StakingTier::Platinum
            } else if staked >= gold {
                StakingTier::Gold
            } else if staked >= silver {
                StakingTier::Silver
            } else {
                StakingTier::Bronze
            }
        }

        /// Reward multiplier per mille (1000 = 1x). Streak: 7d=1.5x, 30d=2x, 90d=3x; seasonal on top.
        fn calculate_multiplier(account: &T::AccountId, _category: AchievementCategory) -> u32 {
            let mut mille = 1000u32;
            for streak_type in [StreakType::DailyLogin, StreakType::WellnessActivity] {
                if let Some(info) = StreakTracking::<T>::get(account, streak_type) {
                    let s = info.current_streak.max(info.longest_streak);
                    if s >= 90 {
                        mille = mille.saturating_add(2000);
                        break;
                    } else if s >= 30 {
                        mille = mille.saturating_add(1000);
                    } else if s >= 7 {
                        mille = mille.saturating_add(500);
                    }
                }
            }
            let now = <frame_system::Pallet<T>>::block_number();
            if let Some((start, end, seasonal_mille)) = SeasonalMultiplier::<T>::get() {
                if now >= start && now <= end {
                    mille = mille.saturating_mul(seasonal_mille).saturating_div(1000);
                }
            }
            mille
        }

        /// Distribute referral bonus to referrer (mint). Returns Err if mint fails.
        fn distribute_referral_bonus_internal(
            referrer: &T::AccountId,
            referred: &T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            Self::mint_internal(referrer, amount)?;
            Self::deposit_event(Event::ReferralBonusDistributed {
                referrer: referrer.clone(),
                referred: referred.clone(),
                amount,
            });
            Ok(())
        }

        /// Conviction multiplier in permille (1000 = 1x). Longer lock = more weight.
        fn conviction_multiplier(conviction_blocks: BlockNumberFor<T>, period_blocks: BlockNumberFor<T>) -> u32 {
            if period_blocks.is_zero() {
                return 1000;
            }
            let periods = conviction_blocks.checked_div(&period_blocks).unwrap_or_else(Zero::zero).saturated_into::<u32>();
            match periods {
                0 => 1000,
                1 => 1500,
                2 => 2000,
                3 => 2500,
                _ => 3000,
            }
        }

        /// Check and unlock achievements based on user activity
        fn check_achievements(account: &T::AccountId) -> DispatchResult {
            let achievements = Achievements::<T>::get(account);
            let reward_history = RewardHistory::<T>::get(account, &RewardType::HealthRecordCreated);

            // Example: Unlock achievement for creating 10 health records
            if reward_history.as_ref().map(|h| h.len()).unwrap_or(0) >= 10 && !achievements.unlocked_achievements.contains(&AchievementType::HealthRecordCreator) {
                Self::claim_achievement_internal(account, AchievementType::HealthRecordCreator)?;
            }

            Ok(())
        }

           /// Internal achievement claiming
        fn claim_achievement_internal(
            account: &T::AccountId,
            achievement: AchievementType,
        ) -> DispatchResult {
            let mut achievements = Achievements::<T>::get(account);
            
            if !achievements.unlocked_achievements.contains(&achievement) {
                achievements.unlocked_achievements.try_push(achievement.clone())
                    .map_err(|_| Error::<T>::AchievementLimitReached)?;
                achievements.total_achievements += 1;

                let reward_amount = Self::get_achievement_reward(&achievement);
                Self::mint_internal(account, reward_amount)?;

                Achievements::<T>::insert(account, achievements);

                Self::deposit_event(Event::AchievementUnlocked {
                    account: account.clone(),
                    achievement,
                });
            }

            Ok(())
        }

        /// Get reward amount for an achievement
        fn get_achievement_reward(achievement: &AchievementType) -> BalanceOf<T> {
            match achievement {
                AchievementType::HealthRecordCreator => BalanceOf::<T>::saturated_from(1000u128),
                AchievementType::ActiveUser => BalanceOf::<T>::saturated_from(500u128),
                AchievementType::DataContributor => BalanceOf::<T>::saturated_from(2000u128),
                AchievementType::QuantumResearcher => BalanceOf::<T>::saturated_from(5000u128),
                AchievementType::WellnessStreak => BalanceOf::<T>::saturated_from(750u128),
                AchievementType::IntegrativeCareComplete => BalanceOf::<T>::saturated_from(3000u128),
            }
        }
    }
}

/// Weight information for extrinsics
pub trait WeightInfo {
    fn mint() -> Weight;
    fn burn() -> Weight;
    fn transfer() -> Weight;
    fn grant_reward() -> Weight;
    fn claim_achievement() -> Weight;
    fn approve() -> Weight;
    fn transfer_from() -> Weight;
    fn stake() -> Weight;
    fn unstake() -> Weight;
    fn claim_vested_tokens() -> Weight;
    fn distribute_patient_reward() -> Weight;
    fn vote() -> Weight;
    fn pay_on_behalf() -> Weight;
    fn add_vesting_schedule() -> Weight;
    fn fund_reward_pool() -> Weight;
    fn create_achievement() -> Weight;
    fn claim_gamification_achievement() -> Weight;
    fn verify_achievement() -> Weight;
    fn award_streak_bonus() -> Weight;
    fn update_streak() -> Weight;
    fn register_referral() -> Weight;
    fn set_seasonal_multiplier() -> Weight;
    fn submit_proposal() -> Weight;
    fn vote_on_proposal() -> Weight;
    fn delegate_votes() -> Weight;
    fn execute_proposal() -> Weight;
    fn treasury_allocate() -> Weight;
    fn claim_treasury_grant() -> Weight;
    fn collect_to_treasury() -> Weight;
    fn update_voting_parameters() -> Weight;
}

pub use pallet::*;
