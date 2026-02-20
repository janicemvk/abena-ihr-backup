//! Weights for governance pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn create_guideline_proposal() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
    fn create_protocol_proposal() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
    fn cast_vote() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn execute_emergency_intervention() -> Weight {
        Weight::from_parts(60_000_000, 0)
    }
}

