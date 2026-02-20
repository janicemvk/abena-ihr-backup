//! Weights for patient-identity pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn register_patient() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn update_consent() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn grant_provider_access() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn revoke_provider_access() -> Weight {
        Weight::from_parts(25_000_000, 0)
    }
    fn emergency_access() -> Weight {
        Weight::from_parts(45_000_000, 0)
    }
    fn deactivate_patient() -> Weight {
        Weight::from_parts(20_000_000, 0)
    }
}

