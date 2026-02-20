//! Weights for treatment-protocol pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn create_protocol() -> Weight {
        Weight::from_parts(60_000_000, 0)
    }
    fn validate_protocol() -> Weight {
        Weight::from_parts(70_000_000, 0)
    }
    fn update_protocol() -> Weight {
        Weight::from_parts(55_000_000, 0)
    }
    fn register_guideline() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
}

