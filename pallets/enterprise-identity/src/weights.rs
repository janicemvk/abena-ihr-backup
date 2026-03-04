//! Weights for enterprise identity pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn register_enterprise_user() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
    fn revoke_enterprise_user() -> Weight {
        Weight::from_parts(25_000_000, 0)
    }
}
