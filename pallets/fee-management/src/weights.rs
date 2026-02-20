//! Weights for fee management pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn create_subscription() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn renew_subscription() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
    fn cancel_subscription() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn set_rate_limit() -> Weight {
        Weight::from_parts(20_000_000, 0)
    }
    fn record_usage() -> Weight {
        Weight::from_parts(25_000_000, 0)
    }
    fn check_rate_limit() -> Weight {
        Weight::from_parts(15_000_000, 0)
    }
    fn distribute_validator_reward() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn claim_validator_rewards() -> Weight {
        Weight::from_parts(25_000_000, 0)
    }
}

