//! Weights for the quantum-results pallet

use frame_support::weights::Weight;

pub trait WeightInfo {
    fn register_algorithm() -> Weight;
    fn attest_quantum_result() -> Weight;
    fn verify_ibm_signature() -> Weight;
    fn link_to_patient() -> Weight;
    fn generate_compliance_certificate() -> Weight;
    fn update_algorithm_version() -> Weight;
    fn register_ibm_key() -> Weight;
    fn register_ibm_backend() -> Weight;
    fn submit_batch_job() -> Weight;
    fn verify_job_completion() -> Weight;
    fn calculate_result_confidence() -> Weight;
    fn link_batch_results() -> Weight;
}

impl WeightInfo for () {
    fn register_algorithm() -> Weight {
        Weight::zero()
    }
    fn attest_quantum_result() -> Weight {
        Weight::zero()
    }
    fn verify_ibm_signature() -> Weight {
        Weight::zero()
    }
    fn link_to_patient() -> Weight {
        Weight::zero()
    }
    fn generate_compliance_certificate() -> Weight {
        Weight::zero()
    }
    fn update_algorithm_version() -> Weight {
        Weight::zero()
    }
    fn register_ibm_key() -> Weight {
        Weight::zero()
    }
    fn register_ibm_backend() -> Weight {
        Weight::zero()
    }
    fn submit_batch_job() -> Weight {
        Weight::zero()
    }
    fn verify_job_completion() -> Weight {
        Weight::zero()
    }
    fn calculate_result_confidence() -> Weight {
        Weight::zero()
    }
    fn link_batch_results() -> Weight {
        Weight::zero()
    }
}

pub struct SubstrateWeight<T>(sp_std::marker::PhantomData<T>);

impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
    fn register_algorithm() -> Weight {
        Weight::from_parts(50_000_000, 0)
    }
    fn attest_quantum_result() -> Weight {
        Weight::from_parts(80_000_000, 0)
    }
    fn verify_ibm_signature() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn link_to_patient() -> Weight {
        Weight::from_parts(30_000_000, 0)
    }
    fn generate_compliance_certificate() -> Weight {
        Weight::from_parts(25_000_000, 0)
    }
    fn update_algorithm_version() -> Weight {
        Weight::from_parts(45_000_000, 0)
    }
    fn register_ibm_key() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
    fn register_ibm_backend() -> Weight {
        Weight::from_parts(45_000_000, 0)
    }
    fn submit_batch_job() -> Weight {
        Weight::from_parts(60_000_000, 0)
    }
    fn verify_job_completion() -> Weight {
        Weight::from_parts(35_000_000, 0)
    }
    fn calculate_result_confidence() -> Weight {
        Weight::from_parts(40_000_000, 0)
    }
    fn link_batch_results() -> Weight {
        Weight::from_parts(55_000_000, 0)
    }
}
