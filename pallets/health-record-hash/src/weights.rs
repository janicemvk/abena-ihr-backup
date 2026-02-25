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
    fn create_record_hash() -> Weight {
        Weight::from_parts(80_000_000, 0)
    }
    fn update_record_hash() -> Weight {
        Weight::from_parts(60_000_000, 0)
    }
    fn grant_record_access() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn revoke_record_access() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
    fn access_record() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
    fn verify_record_integrity() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn link_to_quantum_result() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
    fn create_multisig_requirement() -> Weight {
        Weight::from_parts(55_000_000, 0)
    }
    fn sign_record_access() -> Weight {
        Weight::from_parts(45_000_000, 0)
    }
    fn emergency_access_override() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn mark_record_inactive() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
}

