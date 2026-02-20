//! # Fee Management Pallet
//!
//! A pallet for institution subscription registry, rate limiting by account type,
//! usage metering and tracking, and validator reward distribution.

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
    use scale_info::TypeInfo;
    use sp_std::vec::Vec;
    use sp_runtime::traits::{Zero, Saturating};
    use codec::MaxEncodedLen;
    use sp_runtime::BoundedVec;
    use super::{SubscriptionId, InstitutionSubscription, AccountType, RateLimit, UsageRecord, ValidatorReward, SubscriptionStatus};
    use crate::WeightInfo;

    /// Balance type alias
    pub type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    /// Configuration trait for the pallet.
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// Weight information for extrinsics
        type WeightInfo: crate::WeightInfo;
        /// Currency type for fees and rewards
        type Currency: Currency<Self::AccountId> + ReservableCurrency<Self::AccountId>;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Institution subscription registry
    /// Maps institution account to subscription details
    #[pallet::storage]
    pub type InstitutionSubscriptions<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        InstitutionSubscription<T>,
        OptionQuery,
    >;

    /// Rate limits by account type
    /// Maps account type to rate limit configuration
    #[pallet::storage]
    pub type RateLimits<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        AccountType,
        RateLimit<T>,
        ValueQuery,
    >;

    /// Usage records for tracking API calls and operations
    /// Maps (account, period_start_block) to usage record
    #[pallet::storage]
    pub type UsageRecords<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        Blake2_128Concat,
        BlockNumberFor<T>,
        UsageRecord<T>,
        OptionQuery,
    >;

    /// Validator rewards pool
    /// Maps validator account to accumulated rewards
    #[pallet::storage]
    pub type ValidatorRewards<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BalanceOf<T>,
        ValueQuery,
    >;

    /// Total rewards distributed
    #[pallet::storage]
    pub type TotalRewardsDistributed<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    /// Events emitted by this pallet
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Institution subscription created
        SubscriptionCreated {
            institution: T::AccountId,
            subscription_id: SubscriptionId,
            plan: SubscriptionPlan,
        },
        /// Subscription renewed
        SubscriptionRenewed {
            institution: T::AccountId,
            subscription_id: SubscriptionId,
        },
        /// Subscription cancelled
        SubscriptionCancelled {
            institution: T::AccountId,
            subscription_id: SubscriptionId,
        },
        /// Rate limit updated for account type
        RateLimitUpdated {
            account_type: AccountType,
            rate_limit: RateLimit<T>,
        },
        /// Usage recorded
        UsageRecorded {
            account: T::AccountId,
            operation_type: OperationType,
            count: u32,
        },
        /// Rate limit exceeded
        RateLimitExceeded {
            account: T::AccountId,
            account_type: AccountType,
        },
        /// Validator reward distributed
        ValidatorRewardDistributed {
            validator: T::AccountId,
            amount: BalanceOf<T>,
        },
    }

    /// Errors that can occur in this pallet
    #[pallet::error]
    pub enum Error<T> {
        /// Subscription not found
        SubscriptionNotFound,
        /// Subscription already exists
        SubscriptionAlreadyExists,
        /// Subscription expired
        SubscriptionExpired,
        /// Insufficient balance for subscription
        InsufficientBalance,
        /// Rate limit exceeded
        RateLimitExceeded,
        /// Invalid account type
        InvalidAccountType,
        /// Invalid subscription plan
        InvalidPlan,
    }

    /// Hooks for the pallet
    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {}

    /// Extrinsics for the pallet
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create or update institution subscription
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::create_subscription())]
        pub fn create_subscription(
            origin: OriginFor<T>,
            subscription_id: SubscriptionId,
            plan: SubscriptionPlan,
            duration_blocks: BlockNumberFor<T>,
        ) -> DispatchResult {
            let institution = ensure_signed(origin)?;

            // Check if subscription already exists
            ensure!(
                !InstitutionSubscriptions::<T>::contains_key(&institution),
                Error::<T>::SubscriptionAlreadyExists
            );

            // Calculate subscription fee based on plan
            let fee = Self::calculate_subscription_fee(&plan, duration_blocks);
            
            // Reserve funds for subscription
            T::Currency::reserve(&institution, fee)
                .map_err(|_| Error::<T>::InsufficientBalance)?;

            let subscription = InstitutionSubscription {
                subscription_id,
                institution: institution.clone(),
                plan,
                start_block: <frame_system::Pallet<T>>::block_number(),
                end_block: <frame_system::Pallet<T>>::block_number() + duration_blocks,
                status: SubscriptionStatus::Active,
                created_at: <frame_system::Pallet<T>>::block_number(),
            };

            InstitutionSubscriptions::<T>::insert(&institution, subscription);

            Self::deposit_event(Event::SubscriptionCreated {
                institution,
                subscription_id,
                plan,
            });

            Ok(())
        }

        /// Renew subscription
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::renew_subscription())]
        pub fn renew_subscription(
            origin: OriginFor<T>,
            duration_blocks: BlockNumberFor<T>,
        ) -> DispatchResult {
            let institution = ensure_signed(origin)?;

            let mut subscription = InstitutionSubscriptions::<T>::get(&institution)
                .ok_or(Error::<T>::SubscriptionNotFound)?;

            // Check if subscription is active or expired
            let current_block = <frame_system::Pallet<T>>::block_number();
            if current_block > subscription.end_block {
                subscription.status = SubscriptionStatus::Expired;
            }

            ensure!(
                subscription.status == SubscriptionStatus::Active || subscription.status == SubscriptionStatus::Expired,
                Error::<T>::SubscriptionNotFound
            );

            // Calculate renewal fee
            let fee = Self::calculate_subscription_fee(&subscription.plan, duration_blocks);
            
            // Reserve funds
            T::Currency::reserve(&institution, fee)
                .map_err(|_| Error::<T>::InsufficientBalance)?;

            // Extend subscription
            subscription.end_block = current_block + duration_blocks;
            subscription.status = SubscriptionStatus::Active;

            InstitutionSubscriptions::<T>::insert(&institution, subscription.clone());

            Self::deposit_event(Event::SubscriptionRenewed {
                institution,
                subscription_id: subscription.subscription_id,
            });

            Ok(())
        }

        /// Cancel subscription
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::cancel_subscription())]
        pub fn cancel_subscription(origin: OriginFor<T>) -> DispatchResult {
            let institution = ensure_signed(origin)?;

            let subscription = InstitutionSubscriptions::<T>::get(&institution)
                .ok_or(Error::<T>::SubscriptionNotFound)?;

            // Calculate refund (proportional to remaining time)
            let current_block = <frame_system::Pallet<T>>::block_number();
            let remaining_blocks = subscription.end_block.saturating_sub(current_block);
            let total_blocks = subscription.end_block.saturating_sub(subscription.start_block);
            
            if total_blocks > Zero::zero() && remaining_blocks > Zero::zero() {
                let fee = Self::calculate_subscription_fee(&subscription.plan, total_blocks);
                let refund = fee.saturating_mul(remaining_blocks.into()) / total_blocks.into();
                
                // Unreserve and transfer refund
                T::Currency::unreserve(&institution, fee);
                // Note: In production, you'd calculate actual refund based on used time
            }

            InstitutionSubscriptions::<T>::remove(&institution);

            Self::deposit_event(Event::SubscriptionCancelled {
                institution,
                subscription_id: subscription.subscription_id,
            });

            Ok(())
        }

        /// Set rate limit for account type
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::set_rate_limit())]
        pub fn set_rate_limit(
            origin: OriginFor<T>,
            account_type: AccountType,
            max_requests: u32,
            time_window_blocks: BlockNumberFor<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;

            let rate_limit = RateLimit {
                max_requests,
                time_window_blocks,
            };

            RateLimits::<T>::insert(&account_type, rate_limit.clone());

            Self::deposit_event(Event::RateLimitUpdated {
                account_type,
                rate_limit,
            });

            Ok(())
        }

        /// Record usage for an account
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::record_usage())]
        pub fn record_usage(
            origin: OriginFor<T>,
            account: T::AccountId,
            operation_type: OperationType,
            count: u32,
        ) -> DispatchResult {
            ensure_root(origin)?;

            let current_block = <frame_system::Pallet<T>>::block_number();
            
            // Get or create usage record for current period
            let mut usage_record = UsageRecords::<T>::get(&account, &current_block)
                .unwrap_or_else(|| UsageRecord {
                    period_start: current_block,
                    total_operations: 0,
                    operations_by_type: Default::default(),
                });

            usage_record.total_operations = usage_record.total_operations.saturating_add(count);
            
            // Update operation count by type
            match operation_type {
                OperationType::Read => {
                    usage_record.operations_by_type.reads = 
                        usage_record.operations_by_type.reads.saturating_add(count);
                },
                OperationType::Write => {
                    usage_record.operations_by_type.writes = 
                        usage_record.operations_by_type.writes.saturating_add(count);
                },
                OperationType::Query => {
                    usage_record.operations_by_type.queries = 
                        usage_record.operations_by_type.queries.saturating_add(count);
                },
            }

            UsageRecords::<T>::insert(&account, &current_block, usage_record);

            Self::deposit_event(Event::UsageRecorded {
                account,
                operation_type,
                count,
            });

            Ok(())
        }

        /// Check rate limit for account
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::check_rate_limit())]
        pub fn check_rate_limit(
            account: &T::AccountId,
            account_type: AccountType,
        ) -> Result<(), Error<T>> {
            let rate_limit = RateLimits::<T>::get(&account_type);
            let current_block = <frame_system::Pallet<T>>::block_number();
            
            // Get usage in the time window
            let window_start = current_block.saturating_sub(rate_limit.time_window_blocks);
            let mut total_requests = 0u32;

            // Sum up usage in the time window
            for block in window_start..=current_block {
                if let Some(record) = UsageRecords::<T>::get(account, &block) {
                    total_requests = total_requests.saturating_add(record.total_operations);
                }
            }

            if total_requests >= rate_limit.max_requests {
                Self::deposit_event(Event::RateLimitExceeded {
                    account: account.clone(),
                    account_type,
                });
                return Err(Error::<T>::RateLimitExceeded);
            }

            Ok(())
        }

        /// Distribute validator reward
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::distribute_validator_reward())]
        pub fn distribute_validator_reward(
            origin: OriginFor<T>,
            validator: T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;

            // Add to validator's reward pool
            ValidatorRewards::<T>::mutate(&validator, |rewards| {
                *rewards = rewards.saturating_add(amount);
            });

            TotalRewardsDistributed::<T>::mutate(|total| {
                *total = total.saturating_add(amount);
            });

            Self::deposit_event(Event::ValidatorRewardDistributed {
                validator: validator.clone(),
                amount,
            });

            Ok(())
        }

        /// Claim validator rewards
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::claim_validator_rewards())]
        pub fn claim_validator_rewards(origin: OriginFor<T>) -> DispatchResult {
            let validator = ensure_signed(origin)?;

            let rewards = ValidatorRewards::<T>::take(&validator);

            if rewards > Zero::zero() {
                T::Currency::deposit_creating(&validator, rewards);

                Self::deposit_event(Event::ValidatorRewardDistributed {
                    validator,
                    amount: rewards,
                });
            }

            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        /// Calculate subscription fee based on plan and duration
        fn calculate_subscription_fee(
            plan: &SubscriptionPlan,
            duration_blocks: BlockNumberFor<T>,
        ) -> BalanceOf<T> {
            let base_fee = match plan {
                SubscriptionPlan::Basic => BalanceOf::<T>::from(1000u128),
                SubscriptionPlan::Professional => BalanceOf::<T>::from(5000u128),
                SubscriptionPlan::Enterprise => BalanceOf::<T>::from(20000u128),
            };

            // Fee per block (simplified calculation)
            let fee_per_block = base_fee / BalanceOf::<T>::from(10000u128);
            fee_per_block.saturating_mul(duration_blocks.into())
        }
    }
}

/// Weight information for extrinsics
pub trait WeightInfo {
    fn create_subscription() -> Weight;
    fn renew_subscription() -> Weight;
    fn cancel_subscription() -> Weight;
    fn set_rate_limit() -> Weight;
    fn record_usage() -> Weight;
    fn check_rate_limit() -> Weight;
    fn distribute_validator_reward() -> Weight;
    fn claim_validator_rewards() -> Weight;
}

/// Subscription ID type
pub type SubscriptionId = u64;

/// Subscription plan types
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum SubscriptionPlan {
    /// Basic plan - limited features
    Basic,
    /// Professional plan - standard features
    Professional,
    /// Enterprise plan - full features
    Enterprise,
}

/// Institution subscription
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct InstitutionSubscription<T: frame_system::Config> {
    /// Subscription identifier
    pub subscription_id: SubscriptionId,
    /// Institution account
    pub institution: T::AccountId,
    /// Subscription plan
    pub plan: SubscriptionPlan,
    /// Block when subscription starts
    pub start_block: BlockNumberFor<T>,
    /// Block when subscription ends
    pub end_block: BlockNumberFor<T>,
    /// Subscription status
    pub status: SubscriptionStatus,
    /// Block when subscription was created
    pub created_at: BlockNumberFor<T>,
}

/// Subscription status
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum SubscriptionStatus {
    /// Subscription is active
    Active,
    /// Subscription has expired
    Expired,
    /// Subscription was cancelled
    Cancelled,
}

/// Account type for rate limiting
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen, Copy)]
pub enum AccountType {
    /// Patient account
    Patient,
    /// Provider account
    Provider,
    /// Institution account
    Institution,
}

/// Rate limit configuration
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct RateLimit<T: frame_system::Config> {
    /// Maximum number of requests allowed
    pub max_requests: u32,
    /// Time window in blocks
    pub time_window_blocks: BlockNumberFor<T>,
}

/// Operation type for usage tracking
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
pub enum OperationType {
    /// Read operation
    Read,
    /// Write operation
    Write,
    /// Query operation
    Query,
}

/// Usage record
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct UsageRecord<T: frame_system::Config> {
    /// Block when period started
    pub period_start: BlockNumberFor<T>,
    /// Total operations in period
    pub total_operations: u32,
    /// Operations broken down by type
    pub operations_by_type: OperationCounts,
}

/// Operation counts by type
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen, Default)]
pub struct OperationCounts {
    /// Number of read operations
    pub reads: u32,
    /// Number of write operations
    pub writes: u32,
    /// Number of query operations
    pub queries: u32,
}

/// Validator reward information
#[derive(Clone, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
#[scale_info(skip_type_params(T))]
pub struct ValidatorReward<T: frame_system::Config> {
    /// Validator account
    pub validator: T::AccountId,
    /// Reward amount
    pub amount: u128,
    /// Block when reward was distributed
    pub distributed_at: BlockNumberFor<T>,
}

