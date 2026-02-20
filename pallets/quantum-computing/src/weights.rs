//! Weights for quantum-computing pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn submit_job() -> Weight {
        Weight::from_parts(60_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn store_result() -> Weight {
        Weight::from_parts(70_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn register_integration_point() -> Weight {
        Weight::from_parts(50_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn update_integration_point() -> Weight {
        Weight::from_parts(40_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn query_result() -> Weight {
        Weight::from_parts(20_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }
}

