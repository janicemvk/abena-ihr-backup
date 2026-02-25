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
    fn register_protocol() -> Weight {
        Weight::from_parts(100_000_000, 0)
    }
    fn validate_protocol_spec() -> Weight {
        Weight::from_parts(45_000_000, 0)
    }
    fn initiate_treatment() -> Weight {
        Weight::from_parts(60_000_000, 0)
    }
    fn record_step_completion() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
    fn check_contraindications() -> Weight {
        Weight::from_parts(80_000_000, 0)
    }
    fn evaluate_milestone() -> Weight {
        Weight::from_parts(45_000_000, 0)
    }
    fn modify_protocol() -> Weight {
        Weight::from_parts(55_000_000, 0)
    }
    fn complete_treatment() -> Weight {
        Weight::from_parts(55_000_000, 0)
    }
    fn report_adverse_event() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
    fn add_interaction_rule() -> Weight {
        Weight::from_parts(60_000_000, 0)
    }
    fn query_interaction() -> Weight {
        Weight::from_parts(80_000_000, 0)
    }
}

