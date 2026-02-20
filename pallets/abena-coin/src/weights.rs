//! Weights for abena-coin pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn mint() -> Weight {
        Weight::from_parts(30_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn burn() -> Weight {
        Weight::from_parts(30_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn transfer() -> Weight {
        Weight::from_parts(40_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn grant_reward() -> Weight {
        Weight::from_parts(50_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn claim_achievement() -> Weight {
        Weight::from_parts(45_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }
}

