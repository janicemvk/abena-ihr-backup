//! Weights for account management pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn register_account() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn update_account_tier() -> Weight {
        Weight::from_parts(25_000_000, 0)
    }
    fn submit_credential() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn verify_credential() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
    fn reject_credential() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn make_deposit() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn withdraw_deposit() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
}

