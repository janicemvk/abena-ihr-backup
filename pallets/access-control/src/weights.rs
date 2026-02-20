//! Weights for access control pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn grant_patient_authorization() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn revoke_patient_authorization() -> Weight {
        Weight::from_parts(25_000_000, 0)
    }
    fn grant_institutional_permission() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
    fn revoke_institutional_permission() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn grant_emergency_access() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn revoke_emergency_access() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn check_read_access() -> Weight {
        Weight::from_parts(20_000_000, 0)
    }
}

