//! Weights for data-separation pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

/// Zero weight for tests.
impl crate::WeightInfo for () {
    fn register_data_asset() -> Weight {
        Weight::zero()
    }
    fn set_anonymization_preferences() -> Weight {
        Weight::zero()
    }
    fn license_data() -> Weight {
        Weight::zero()
    }
    fn calculate_compensation() -> Weight {
        Weight::zero()
    }
    fn verify_privacy_guarantees() -> Weight {
        Weight::zero()
    }
    fn register_commercial_entity() -> Weight {
        Weight::zero()
    }
    fn request_data_license() -> Weight {
        Weight::zero()
    }
    fn finalize_data_license() -> Weight {
        Weight::zero()
    }
    fn report_data_violation() -> Weight {
        Weight::zero()
    }
    fn confirm_violation_and_penalize() -> Weight {
        Weight::zero()
    }
}

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn register_data_asset() -> Weight {
        Weight::from_parts(60_000_000, 0)
    }
    fn set_anonymization_preferences() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn license_data() -> Weight {
        Weight::from_parts(80_000_000, 0)
    }
    fn calculate_compensation() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
    fn verify_privacy_guarantees() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn register_commercial_entity() -> Weight {
        Weight::from_parts(20_000_000, 0)
    }
    fn request_data_license() -> Weight {
        Weight::from_parts(150_000_000, 0)
    }
    fn finalize_data_license() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn report_data_violation() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
    fn confirm_violation_and_penalize() -> Weight {
        Weight::from_parts(120_000_000, 0)
    }
}
