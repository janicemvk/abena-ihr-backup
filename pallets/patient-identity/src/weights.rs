//! Weights for patient-identity pallet

use frame_support::weights::Weight;

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> crate::WeightInfo for SubstrateWeight<T> {
    fn register_patient() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn register_did() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn update_did() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
    fn issue_zk_credential() -> Weight {
        Weight::from_parts(50_000_000, 0)
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
    fn grant_consent() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn revoke_consent() -> Weight {
        Weight::from_parts(25_000_000, 0)
    }
    fn issue_auth_token() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
    fn verify_auth_token() -> Weight {
        Weight::from_parts(20_000_000, 0)
    }
}

