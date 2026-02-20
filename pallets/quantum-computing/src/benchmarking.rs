//! Benchmarking for quantum computing pallet

use super::*;
use frame_benchmarking::{benchmarks, whitelisted_caller};
use frame_system::RawOrigin;
use sp_core::H256;

benchmarks! {
    submit_job {
        let caller: T::AccountId = whitelisted_caller();
        let job_type = QuantumJobType::Simulation;
        let parameters = vec![0u8; 1024];
    }: _(RawOrigin::Signed(caller.clone()), job_type, parameters, None)
    verify {
        assert!(QuantumJobs::<T>::contains_key(&1));
    }

    store_result {
        let caller: T::AccountId = whitelisted_caller();
        let job_type = QuantumJobType::Simulation;
        let parameters = vec![0u8; 1024];
        Pallet::<T>::submit_job(
            RawOrigin::Signed(caller.clone()).into(),
            job_type,
            parameters,
            None,
        )?;
        let result_data = vec![0u8; 2048];
        let result_hash = H256::from_slice(&[1u8; 32]);
    }: _(RawOrigin::Signed(caller.clone()), 1, result_data, result_hash)
    verify {
        assert!(QuantumResults::<T>::contains_key(&1));
    }

    register_integration_point {
        let caller: T::AccountId = whitelisted_caller();
        let point_id = 1u32;
        let provider_name = b"Test Provider".to_vec();
        let endpoint = b"https://test.example.com".to_vec();
        let capabilities = vec![QuantumCapability::Simulation];
    }: _(RawOrigin::Signed(caller.clone()), point_id, provider_name, endpoint, capabilities)
    verify {
        assert!(IntegrationPoints::<T>::contains_key(&point_id));
    }

    update_integration_point {
        let caller: T::AccountId = whitelisted_caller();
        let point_id = 1u32;
        let provider_name = b"Test Provider".to_vec();
        let endpoint = b"https://test.example.com".to_vec();
        let capabilities = vec![QuantumCapability::Simulation];
        Pallet::<T>::register_integration_point(
            RawOrigin::Signed(caller.clone()).into(),
            point_id,
            provider_name,
            endpoint,
            capabilities,
        )?;
        let new_endpoint = b"https://new.example.com".to_vec();
    }: _(RawOrigin::Signed(caller.clone()), point_id, Some(new_endpoint), None, None)
    verify {
        assert!(IntegrationPoints::<T>::contains_key(&point_id));
    }

    query_result {
        let caller: T::AccountId = whitelisted_caller();
        let job_type = QuantumJobType::Simulation;
        let parameters = vec![0u8; 1024];
        Pallet::<T>::submit_job(
            RawOrigin::Signed(caller.clone()).into(),
            job_type,
            parameters,
            None,
        )?;
        let result_data = vec![0u8; 2048];
        let result_hash = H256::from_slice(&[1u8; 32]);
        Pallet::<T>::store_result(
            RawOrigin::Signed(caller.clone()).into(),
            1,
            result_data,
            result_hash,
        )?;
    }: _(RawOrigin::Signed(caller.clone()), 1)
    verify {
        assert!(QuantumResults::<T>::contains_key(&1));
    }

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}

