//! Weights for consortium governance pallet

use frame_support::weights::Weight;

pub trait WeightInfo {
    fn register_consortium_member() -> Weight;
    fn propose() -> Weight;
    fn vote() -> Weight;
    fn close_and_execute() -> Weight;
}

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
    fn register_consortium_member() -> Weight {
        Weight::from_parts(60_000_000, 0)
    }
    fn propose() -> Weight {
        Weight::from_parts(80_000_000, 0)
    }
    fn vote() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn close_and_execute() -> Weight {
        Weight::from_parts(100_000_000, 0)
    }
}
