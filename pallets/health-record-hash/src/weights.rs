//! Weights for health-record-hash pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn record_hash() -> Weight {
        Weight::from_parts(45_000_000, 0)
    }
    fn update_hash() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
    fn set_multi_sig() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
}

