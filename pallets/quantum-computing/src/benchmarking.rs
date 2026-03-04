//! Benchmarks for quantum-computing pallet.
//!
//! Covers all 5 extrinsics: submit_job, store_result,
//! register_integration_point, update_integration_point, query_result.

use super::*;
use frame_benchmarking::{benchmarks, whitelisted_caller};
use frame_system::RawOrigin;
use sp_core::H256;

benchmarks! {

    // ── submit_job ───────────────────────────────────────────────────────────
    submit_job {
        let caller: T::AccountId = whitelisted_caller();
        let parameters = vec![0u8; 1024];
    }: _(
        RawOrigin::Signed(caller.clone()),
        QuantumJobType::Simulation,
        parameters,
        None,   // integration_point_id
        None,   // patient
        None    // health_record_hash
    )
    verify {
        assert!(QuantumJobs::<T>::contains_key(&1u64));
    }

    // ── store_result ─────────────────────────────────────────────────────────
    store_result {
        let caller: T::AccountId = whitelisted_caller();
        Pallet::<T>::submit_job(
            RawOrigin::Signed(caller.clone()).into(),
            QuantumJobType::Simulation,
            vec![0u8; 512],
            None, None, None,
        )?;
        let result_hash = H256::from_slice(&[1u8; 32]);
    }: _(RawOrigin::Signed(caller.clone()), 1u64, vec![0u8; 2048], result_hash)
    verify {
        assert!(QuantumResults::<T>::contains_key(&1u64));
    }

    // ── register_integration_point ───────────────────────────────────────────
    register_integration_point {
        let caller: T::AccountId = whitelisted_caller();
        let point_id = 1u32;
    }: _(
        RawOrigin::Signed(caller.clone()),
        point_id,
        b"IBM Quantum".to_vec(),
        b"https://quantum.ibm.com".to_vec(),
        vec![QuantumCapability::Simulation, QuantumCapability::Optimization]
    )
    verify {
        assert!(IntegrationPoints::<T>::contains_key(&point_id));
    }

    // ── update_integration_point ─────────────────────────────────────────────
    update_integration_point {
        let caller: T::AccountId = whitelisted_caller();
        let point_id = 1u32;
        Pallet::<T>::register_integration_point(
            RawOrigin::Signed(caller.clone()).into(),
            point_id,
            b"IBM Quantum".to_vec(),
            b"https://quantum.ibm.com".to_vec(),
            vec![QuantumCapability::Simulation],
        )?;
    }: _(
        RawOrigin::Signed(caller.clone()),
        point_id,
        Some(b"https://quantum.ibm.com/v2".to_vec()),
        Some(vec![QuantumCapability::Simulation, QuantumCapability::MachineLearning]),
        Some(true)
    )
    verify {
        let pt = IntegrationPoints::<T>::get(&point_id).unwrap();
        assert!(pt.active);
    }

    // ── query_result ─────────────────────────────────────────────────────────
    query_result {
        let caller: T::AccountId = whitelisted_caller();
        Pallet::<T>::submit_job(
            RawOrigin::Signed(caller.clone()).into(),
            QuantumJobType::QML,
            vec![0u8; 256],
            None, None, None,
        )?;
        Pallet::<T>::store_result(
            RawOrigin::Signed(caller.clone()).into(),
            1u64,
            vec![42u8; 512],
            H256::from_slice(&[2u8; 32]),
        )?;
    }: _(RawOrigin::Signed(caller.clone()), 1u64)
    verify {
        assert!(QuantumResults::<T>::contains_key(&1u64));
    }

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}
