//! # ABENA Coin Pallet
//!
//! A pallet for managing the native ABENA Coin token used for gamification
//! and rewards in the healthcare platform.

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Encode, Decode, MaxEncodedLen};
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
    };
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;
    use sp_runtime::traits::{Zero, CheckedAdd};
    use sp_runtime::SaturatedConversion;
    use codec::{Encode, Decode, MaxEncodedLen};
    use scale_info::TypeInfo;
    use sp_runtime::RuntimeDebug;

    use crate::WeightInfo;
    /// Balance type alias
    pub type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    /// Reward types for gamification
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
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
    }

    /// Achievement types
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum AchievementType {
        /// Created first health record
        HealthRecordCreator,
        /// Active user (logged in regularly)
        ActiveUser,
        /// Contributed data for research
        DataContributor,
        /// Contributed to quantum computing research
        QuantumResearcher,
    }

/// Achievement record for a user
#[derive(Clone, Encode, Decode, PartialEq, Eq, TypeInfo, MaxEncodedLen)]
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
    #[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct RewardEntry<T: Config> {
        /// Amount rewarded
        pub amount: BalanceOf<T>,
        /// Block number when reward was granted
        pub block_number: BlockNumberFor<T>,
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

            let current_balance = Balances::<T>::get(&to);
            let new_balance = current_balance
                .checked_add(&amount)
                .ok_or(Error::<T>::InsufficientBalance)?;

            Balances::<T>::insert(&to, new_balance);
            TotalSupply::<T>::mutate(|supply| *supply += amount);

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
    }


/// Internal functions
    impl<T: Config> Pallet<T> {
        /// Internal mint function
        fn mint_internal(
            account: &T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let current_balance = Balances::<T>::get(account);
            let new_balance = current_balance
                .checked_add(&amount)
                .ok_or(Error::<T>::InsufficientBalance)?;

            Balances::<T>::insert(account, new_balance);
            TotalSupply::<T>::mutate(|supply| *supply += amount);

            Ok(())
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
}

