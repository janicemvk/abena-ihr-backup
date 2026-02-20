//! Weights for interoperability pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn map_fhir_resource() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
    fn initiate_cross_chain_exchange() -> Weight {
        Weight::from_parts(60_000_000, 0)
    }
    fn verify_insurance_claim() -> Weight {
        Weight::from_parts(55_000_000, 0)
    }
    fn register_pharmacy() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn register_lab() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
}

