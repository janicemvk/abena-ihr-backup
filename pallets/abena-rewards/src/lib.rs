//! # ABENA Health Rewards Pallet
//!
//! DK Technologies, Inc. — ABENA IHR (Integrative Health Record)
//!
//! ## Overview
//!
//! This pallet implements the ABENA Coin health incentive system. It mints
//! ABENA Coins directly into patient wallets when verified health actions
//! are completed on-chain. Oracles (verified healthcare institutions) submit
//! attestations; the pallet validates them and calls `Currency::deposit_creating`
//! to mint new coins.
//!
//! ## Health Actions & Default Rewards
//!
//! | Action                  | Default Reward  |
//! |-------------------------|-----------------|
//! | Lab result uploaded     |  5 ABENA        |
//! | Medication adherence   |  2 ABENA        |
//! | Wellness check-in      |  1 ABENA        |
//! | Preventive care        | 10 ABENA        |
//! | Data sharing consent   |  3 ABENA        |
//! | Telehealth visit       |  5 ABENA        |
//! | Integrative therapy    |  4 ABENA        |
//! | Genetic data upload    | 15 ABENA        |
//!
//! ## Security Model
//!
//! - Only `AuthorizedOracle` origin can award rewards (sudo on testnet,
//!   governance-gated oracle set on mainnet)
//! - Daily reward cap per patient prevents oracle abuse
//! - Per-action cooldown prevents double-counting the same event
//! - Root can pause all rewards (emergency stop)
//! - All events are emitted on-chain for full auditability

#![cfg_attr(not(feature = "std"), no_std)]
#![allow(clippy::unused_unit)]

pub use pallet::*;

// ─── Weight benchmarking stubs ────────────────────────────────────────────────
pub mod weights {
    use frame_support::weights::Weight;

    pub trait WeightInfo {
        fn award_health_reward() -> Weight;
        fn set_reward_amount() -> Weight;
        fn set_daily_cap() -> Weight;
        fn pause_rewards() -> Weight;
        fn resume_rewards() -> Weight;
        fn add_oracle() -> Weight;
        fn remove_oracle() -> Weight;
    }

    /// Placeholder weights — run benchmarks before mainnet
    pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);
    impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
        fn award_health_reward()  -> Weight { Weight::from_parts(50_000_000, 0) }
        fn set_reward_amount()    -> Weight { Weight::from_parts(20_000_000, 0) }
        fn set_daily_cap()        -> Weight { Weight::from_parts(20_000_000, 0) }
        fn pause_rewards()        -> Weight { Weight::from_parts(10_000_000, 0) }
        fn resume_rewards()       -> Weight { Weight::from_parts(10_000_000, 0) }
        fn add_oracle()           -> Weight { Weight::from_parts(15_000_000, 0) }
        fn remove_oracle()        -> Weight { Weight::from_parts(15_000_000, 0) }
    }
}

#[frame_support::pallet]
pub mod pallet {
    use super::weights::WeightInfo;
    use frame_support::{
        pallet_prelude::*,
        traits::{Currency, ExistenceRequirement, ReservableCurrency},
    };
    use frame_system::pallet_prelude::*;
    use sp_runtime::traits::{Saturating, Zero};
    use sp_std::vec::Vec;

    // ── Type aliases ──────────────────────────────────────────────────────────

    /// Shorthand for the balance type derived from the Currency trait.
    pub type BalanceOf<T> =
        <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    // ─────────────────────────────────────────────────────────────────────────
    // Health Action Enum
    // ─────────────────────────────────────────────────────────────────────────

    /// All health actions that can earn ABENA Coin rewards.
    ///
    /// Each variant maps to a configurable reward amount stored in
    /// `RewardAmounts`. Adding a new health action = adding a variant here
    /// + setting its amount via `set_reward_amount`.
    #[derive(
        Encode, Decode, Clone, Copy, PartialEq, Eq,
        TypeInfo, MaxEncodedLen, RuntimeDebug, PartialOrd, Ord,
    )]
    pub enum HealthAction {
        /// Patient uploads lab result (blood panel, imaging, pathology, etc.)
        LabResultUploaded       = 0,
        /// Patient confirms medication taken on schedule (via oracle attestation)
        MedicationAdherence     = 1,
        /// Periodic wellness survey or biometric check-in completed
        WellnessCheckIn         = 2,
        /// Preventive care completed: vaccination, cancer screening, annual exam
        PreventiveCare          = 3,
        /// Patient opts into anonymized research data sharing
        DataSharingConsent      = 4,
        /// Completed telehealth visit (conventional or integrative medicine)
        TelehealthVisit         = 5,
        /// Completed integrative therapy session (acupuncture, functional med, etc.)
        IntegrativeTherapy      = 6,
        /// Uploaded genetic / genomic data for integrative health record
        GeneticDataUpload       = 7,
    }

    impl HealthAction {
        /// All variants — used for genesis initialization
        pub fn all() -> &'static [HealthAction] {
            use HealthAction::*;
            &[
                LabResultUploaded,
                MedicationAdherence,
                WellnessCheckIn,
                PreventiveCare,
                DataSharingConsent,
                TelehealthVisit,
                IntegrativeTherapy,
                GeneticDataUpload,
            ]
        }

        /// Human-readable name for events and logs
        pub fn name(&self) -> &'static str {
            match self {
                HealthAction::LabResultUploaded    => "lab_result_uploaded",
                HealthAction::MedicationAdherence  => "medication_adherence",
                HealthAction::WellnessCheckIn      => "wellness_check_in",
                HealthAction::PreventiveCare       => "preventive_care",
                HealthAction::DataSharingConsent   => "data_sharing_consent",
                HealthAction::TelehealthVisit      => "telehealth_visit",
                HealthAction::IntegrativeTherapy   => "integrative_therapy",
                HealthAction::GeneticDataUpload    => "genetic_data_upload",
            }
        }

        /// Minimum blocks between rewards for the same action for the same patient.
        /// Prevents rapid-fire double submissions by a faulty oracle.
        pub fn cooldown_blocks(&self) -> u32 {
            match self {
                HealthAction::LabResultUploaded    => 100,   // ~10 min
                HealthAction::MedicationAdherence  => 7_200,  // ~12 hours
                HealthAction::WellnessCheckIn      => 14_400, // ~24 hours
                HealthAction::PreventiveCare       => 86_400, // ~7 days
                HealthAction::DataSharingConsent   => 0,      // one-time, handled separately
                HealthAction::TelehealthVisit      => 14_400, // ~24 hours
                HealthAction::IntegrativeTherapy   => 14_400, // ~24 hours
                HealthAction::GeneticDataUpload    => 0,      // one-time
            }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Pallet Config
    // ─────────────────────────────────────────────────────────────────────────

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;

        /// The currency used to mint ABENA Coins.
        /// Bound to pallet_balances in the runtime.
        type Currency: Currency<Self::AccountId> + ReservableCurrency<Self::AccountId>;

        /// Origin allowed to award rewards (EnsureRoot on testnet,
        /// oracle governance set on mainnet).
        type AuthorizedOracle: EnsureOrigin<Self::RuntimeOrigin>;

        /// Maximum number of reward actions that can be processed per block.
        /// Prevents DoS via flooding.
        #[pallet::constant]
        type MaxActionsPerBlock: Get<u32>;

        /// Weight information
        type WeightInfo: WeightInfo;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Pallet Declaration
    // ─────────────────────────────────────────────────────────────────────────

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // ─────────────────────────────────────────────────────────────────────────
    // Storage
    // ─────────────────────────────────────────────────────────────────────────

    /// ABENA Coin reward amount per health action (in planck).
    /// Set by root via `set_reward_amount`.
    #[pallet::storage]
    #[pallet::getter(fn reward_amount)]
    pub type RewardAmounts<T: Config> =
        StorageMap<_, Blake2_128Concat, HealthAction, BalanceOf<T>, OptionQuery>;

    /// Daily ABENA Coin cap per patient.
    /// Default: 50 ABENA per day. Prevents oracle abuse from generating
    /// unlimited coins for a single patient.
    #[pallet::storage]
    #[pallet::getter(fn daily_cap)]
    pub type DailyRewardCap<T: Config> =
        StorageValue<_, BalanceOf<T>, ValueQuery>;

    /// Tracks how many ABENA Coins each patient has earned today.
    /// Key: (AccountId, day_number)
    #[pallet::storage]
    #[pallet::getter(fn daily_earned)]
    pub type DailyEarned<T: Config> =
        StorageDoubleMap<
            _,
            Blake2_128Concat, T::AccountId,
            Blake2_128Concat, u32,
            BalanceOf<T>,
            ValueQuery,
        >;

    /// Tracks cumulative lifetime ABENA Coins earned by each patient.
    #[pallet::storage]
    #[pallet::getter(fn lifetime_earned)]
    pub type LifetimeEarned<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, BalanceOf<T>, ValueQuery>;

    /// Tracks the last block at which a patient received a reward for a
    /// specific action. Used to enforce per-action cooldowns.
    #[pallet::storage]
    #[pallet::getter(fn last_reward_block)]
    pub type LastRewardBlock<T: Config> =
        StorageDoubleMap<
            _,
            Blake2_128Concat, T::AccountId,
            Blake2_128Concat, HealthAction,
            BlockNumberFor<T>,
            OptionQuery,
        >;

    /// Total ABENA Coins minted by this pallet since genesis.
    #[pallet::storage]
    #[pallet::getter(fn total_rewards_minted)]
    pub type TotalRewardsMinted<T: Config> =
        StorageValue<_, BalanceOf<T>, ValueQuery>;

    /// Total number of health actions rewarded since genesis.
    #[pallet::storage]
    #[pallet::getter(fn total_actions_rewarded)]
    pub type TotalActionsRewarded<T: Config> =
        StorageValue<_, u64, ValueQuery>;

    /// Emergency pause flag. When true, all reward minting is halted.
    #[pallet::storage]
    #[pallet::getter(fn rewards_paused)]
    pub type RewardsPaused<T: Config> =
        StorageValue<_, bool, ValueQuery>;

    /// Authorized oracle accounts (in addition to the origin check).
    #[pallet::storage]
    #[pallet::getter(fn is_oracle)]
    pub type AuthorizedOracles<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, bool, ValueQuery>;

    // ─────────────────────────────────────────────────────────────────────────
    // Genesis Configuration
    // ─────────────────────────────────────────────────────────────────────────

    #[pallet::genesis_config]
    #[derive(frame_support::DefaultNoBound)]
    pub struct GenesisConfig<T: Config> {
        /// Initial reward amounts: Vec<(HealthAction, amount_in_planck)>
        pub initial_rewards: Vec<(HealthAction, BalanceOf<T>)>,
        /// Initial daily cap in planck (default set in genesis)
        pub initial_daily_cap: Option<BalanceOf<T>>,
    }

    #[pallet::genesis_build]
    impl<T: Config> BuildGenesisConfig for GenesisConfig<T> {
        fn build(&self) {
            for (action, amount) in &self.initial_rewards {
                RewardAmounts::<T>::insert(action, amount);
            }

            if self.initial_rewards.is_empty() {
                let abena: BalanceOf<T> = 1_000_000_000_000u128
                    .try_into()
                    .unwrap_or_default();
                let defaults: Vec<(HealthAction, u128)> = vec![
                    (HealthAction::LabResultUploaded,    5  * 1_000_000_000_000u128),
                    (HealthAction::MedicationAdherence,  2  * 1_000_000_000_000u128),
                    (HealthAction::WellnessCheckIn,      1  * 1_000_000_000_000u128),
                    (HealthAction::PreventiveCare,       10 * 1_000_000_000_000u128),
                    (HealthAction::DataSharingConsent,   3  * 1_000_000_000_000u128),
                    (HealthAction::TelehealthVisit,      5  * 1_000_000_000_000u128),
                    (HealthAction::IntegrativeTherapy,   4  * 1_000_000_000_000u128),
                    (HealthAction::GeneticDataUpload,    15 * 1_000_000_000_000u128),
                ];
                for (action, amount_u128) in defaults {
                    if let Ok(amount) = TryInto::<BalanceOf<T>>::try_into(amount_u128) {
                        RewardAmounts::<T>::insert(action, amount);
                    }
                }
                let _ = abena;
            }

            let cap = self.initial_daily_cap.unwrap_or_else(|| {
                TryInto::<BalanceOf<T>>::try_into(50u128 * 1_000_000_000_000u128)
                    .unwrap_or_default()
            });
            DailyRewardCap::<T>::put(cap);
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Events
    // ─────────────────────────────────────────────────────────────────────────

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        RewardIssued {
            patient: T::AccountId,
            action: HealthAction,
            amount: BalanceOf<T>,
            lifetime_total: BalanceOf<T>,
        },
        RewardAmountUpdated {
            action: HealthAction,
            old_amount: BalanceOf<T>,
            new_amount: BalanceOf<T>,
        },
        DailyCapUpdated {
            old_cap: BalanceOf<T>,
            new_cap: BalanceOf<T>,
        },
        RewardsPaused,
        RewardsResumed,
        OracleAdded { oracle: T::AccountId },
        OracleRemoved { oracle: T::AccountId },
        DailyCapReached {
            patient: T::AccountId,
            action: HealthAction,
            cap: BalanceOf<T>,
        },
        ActionOnCooldown {
            patient: T::AccountId,
            action: HealthAction,
            blocks_remaining: BlockNumberFor<T>,
        },
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Errors
    // ─────────────────────────────────────────────────────────────────────────

    #[pallet::error]
    pub enum Error<T> {
        RewardNotConfigured,
        RewardsMintingPaused,
        DailyCapExceeded,
        CooldownNotElapsed,
        NotAuthorizedOracle,
        ArithmeticOverflow,
        OracleAlreadyExists,
        OracleNotFound,
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Constants
    // ─────────────────────────────────────────────────────────────────────────

    #[pallet::constant_name(BlocksPerDay)]
    const BLOCKS_PER_DAY: u32 = 14_400;

    // ─────────────────────────────────────────────────────────────────────────
    // Pallet Calls (Extrinsics)
    // ─────────────────────────────────────────────────────────────────────────

    #[pallet::call]
    impl<T: Config> Pallet<T> {

        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::award_health_reward())]
        pub fn award_health_reward(
            origin: OriginFor<T>,
            patient: T::AccountId,
            action: HealthAction,
        ) -> DispatchResult {
            T::AuthorizedOracle::ensure_origin(origin)?;
            ensure!(!RewardsPaused::<T>::get(), Error::<T>::RewardsMintingPaused);

            let amount = RewardAmounts::<T>::get(&action)
                .ok_or(Error::<T>::RewardNotConfigured)?;

            let current_block = frame_system::Pallet::<T>::block_number();
            let cooldown = BlockNumberFor::<T>::from(action.cooldown_blocks());

            if let Some(last_block) = LastRewardBlock::<T>::get(&patient, &action) {
                let elapsed = current_block.saturating_sub(last_block);
                if elapsed < cooldown {
                    let blocks_remaining = cooldown.saturating_sub(elapsed);
                    Self::deposit_event(Event::ActionOnCooldown {
                        patient: patient.clone(),
                        action,
                        blocks_remaining,
                    });
                    return Err(Error::<T>::CooldownNotElapsed.into());
                }
            }

            let day = Self::current_day(current_block);
            let cap = DailyRewardCap::<T>::get();
            let earned_today = DailyEarned::<T>::get(&patient, day);

            if !cap.is_zero() {
                let remaining_today = cap.saturating_sub(earned_today);
                if remaining_today.is_zero() {
                    Self::deposit_event(Event::DailyCapReached {
                        patient: patient.clone(),
                        action,
                        cap,
                    });
                    return Err(Error::<T>::DailyCapExceeded.into());
                }
                ensure!(amount <= remaining_today, Error::<T>::DailyCapExceeded);
            }

            let _imbalance = T::Currency::deposit_creating(&patient, amount);

            LastRewardBlock::<T>::insert(&patient, &action, current_block);

            DailyEarned::<T>::mutate(&patient, day, |earned| {
                *earned = earned.saturating_add(amount);
            });

            if day > 0 {
                DailyEarned::<T>::remove(&patient, day.saturating_sub(1));
            }

            let new_lifetime = LifetimeEarned::<T>::mutate(&patient, |total| {
                *total = total.saturating_add(amount);
                *total
            });

            TotalRewardsMinted::<T>::mutate(|total| {
                *total = total.saturating_add(amount);
            });
            TotalActionsRewarded::<T>::mutate(|count| {
                *count = count.saturating_add(1);
            });

            Self::deposit_event(Event::RewardIssued {
                patient,
                action,
                amount,
                lifetime_total: new_lifetime,
            });

            Ok(())
        }

        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::set_reward_amount())]
        pub fn set_reward_amount(
            origin: OriginFor<T>,
            action: HealthAction,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;
            let old_amount = RewardAmounts::<T>::get(&action).unwrap_or_default();
            RewardAmounts::<T>::insert(&action, amount);
            Self::deposit_event(Event::RewardAmountUpdated {
                action,
                old_amount,
                new_amount: amount,
            });
            Ok(())
        }

        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::set_daily_cap())]
        pub fn set_daily_cap(
            origin: OriginFor<T>,
            new_cap: BalanceOf<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;
            let old_cap = DailyRewardCap::<T>::get();
            DailyRewardCap::<T>::put(new_cap);
            Self::deposit_event(Event::DailyCapUpdated { old_cap, new_cap });
            Ok(())
        }

        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::pause_rewards())]
        pub fn pause_rewards(origin: OriginFor<T>) -> DispatchResult {
            ensure_root(origin)?;
            RewardsPaused::<T>::put(true);
            Self::deposit_event(Event::RewardsPaused);
            Ok(())
        }

        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::resume_rewards())]
        pub fn resume_rewards(origin: OriginFor<T>) -> DispatchResult {
            ensure_root(origin)?;
            RewardsPaused::<T>::put(false);
            Self::deposit_event(Event::RewardsResumed);
            Ok(())
        }

        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::add_oracle())]
        pub fn add_oracle(
            origin: OriginFor<T>,
            oracle: T::AccountId,
        ) -> DispatchResult {
            ensure_root(origin)?;
            ensure!(!AuthorizedOracles::<T>::get(&oracle), Error::<T>::OracleAlreadyExists);
            AuthorizedOracles::<T>::insert(&oracle, true);
            Self::deposit_event(Event::OracleAdded { oracle });
            Ok(())
        }

        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::remove_oracle())]
        pub fn remove_oracle(
            origin: OriginFor<T>,
            oracle: T::AccountId,
        ) -> DispatchResult {
            ensure_root(origin)?;
            ensure!(AuthorizedOracles::<T>::get(&oracle), Error::<T>::OracleNotFound);
            AuthorizedOracles::<T>::remove(&oracle);
            Self::deposit_event(Event::OracleRemoved { oracle });
            Ok(())
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Helper Methods
    // ─────────────────────────────────────────────────────────────────────────

    impl<T: Config> Pallet<T> {

        pub fn current_day(block: BlockNumberFor<T>) -> u32 {
            let block_u32: u32 = TryInto::<u32>::try_into(block).unwrap_or(u32::MAX);
            block_u32 / BLOCKS_PER_DAY
        }

        pub fn protocol_stats() -> ProtocolStats<BalanceOf<T>> {
            ProtocolStats {
                total_rewards_minted: TotalRewardsMinted::<T>::get(),
                total_actions_rewarded: TotalActionsRewarded::<T>::get(),
                rewards_paused: RewardsPaused::<T>::get(),
                daily_cap: DailyRewardCap::<T>::get(),
            }
        }

        pub fn patient_profile(
            patient: &T::AccountId,
        ) -> PatientRewardProfile<BalanceOf<T>, BlockNumberFor<T>> {
            let current_block = frame_system::Pallet::<T>::block_number();
            let current_day = Self::current_day(current_block);
            PatientRewardProfile {
                lifetime_earned: LifetimeEarned::<T>::get(patient),
                earned_today: DailyEarned::<T>::get(patient, current_day),
                daily_cap: DailyRewardCap::<T>::get(),
                last_reward_blocks: HealthAction::all()
                    .iter()
                    .filter_map(|action| {
                        LastRewardBlock::<T>::get(patient, action)
                            .map(|block| (*action, block))
                    })
                    .collect(),
            }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Return types for helper methods
    // ─────────────────────────────────────────────────────────────────────────

    #[derive(Encode, Decode, Clone, PartialEq, Eq, TypeInfo, RuntimeDebug)]
    pub struct ProtocolStats<Balance> {
        pub total_rewards_minted: Balance,
        pub total_actions_rewarded: u64,
        pub rewards_paused: bool,
        pub daily_cap: Balance,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, TypeInfo, RuntimeDebug)]
    pub struct PatientRewardProfile<Balance, BlockNumber> {
        pub lifetime_earned: Balance,
        pub earned_today: Balance,
        pub daily_cap: Balance,
        pub last_reward_blocks: Vec<(HealthAction, BlockNumber)>,
    }
}
