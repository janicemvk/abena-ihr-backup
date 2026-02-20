//! Weights for patient-health-records pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn create_health_record() -> Weight {
        Weight::from_parts(50_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn update_health_record() -> Weight {
        Weight::from_parts(40_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn grant_access() -> Weight {
        Weight::from_parts(30_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn revoke_access() -> Weight {
        Weight::from_parts(25_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }

    fn update_encryption_metadata() -> Weight {
        Weight::from_parts(35_000_000, 0)
            .saturating_add(Weight::from_parts(0, 0))
    }
}

