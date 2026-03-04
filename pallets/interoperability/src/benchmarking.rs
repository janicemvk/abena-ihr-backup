//! Benchmarks for the ABENA Interoperability pallet.

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_system::RawOrigin;
use sp_core::H256;

const SEED: u32 = 0;

benchmarks! {

    // ── map_fhir_resource ────────────────────────────────────────────────────
    map_fhir_resource {
        let mapper: T::AccountId   = whitelisted_caller();
        let patient: T::AccountId  = account("patient", 0, SEED);
        let patient_key            = patient.clone();
        let resource_hash          = H256::from_low_u64_be(1);
    }: _(
        RawOrigin::Signed(mapper),
        patient,
        FHIRResourceType::Observation,
        resource_hash,
        b"blockchain-record-001".to_vec(),
        DataStandard::HL7_FHIR_R4
    )
    verify {
        assert!(FHIRResources::<T>::contains_key(&patient_key, FHIRResourceType::Observation));
    }

    // ── initiate_cross_chain_exchange ────────────────────────────────────────
    initiate_cross_chain_exchange {
        let initiator: T::AccountId = whitelisted_caller();
        let data_hash               = H256::from_low_u64_be(2);
    }: _(
        RawOrigin::Signed(initiator),
        1u64,
        b"abena-health-chain".to_vec(),
        b"polkadot-relay-chain".to_vec(),
        data_hash
    )
    verify {
        assert!(CrossChainExchanges::<T>::contains_key(1u64));
    }

    // ── verify_insurance_claim ───────────────────────────────────────────────
    verify_insurance_claim {
        let verifier: T::AccountId = whitelisted_caller();
        let patient: T::AccountId  = account("patient", 0, SEED);
        let patient_key            = patient.clone();
        let claim_hash             = H256::from_low_u64_be(3);
    }: _(RawOrigin::Signed(verifier), 1u64, patient, claim_hash)
    verify {
        assert!(InsuranceClaims::<T>::contains_key(1u64));
    }

    // ── register_pharmacy ────────────────────────────────────────────────────
    register_pharmacy {
        let registrar: T::AccountId = whitelisted_caller();
    }: _(
        RawOrigin::Signed(registrar),
        1u32,
        b"ABENA Pharmacy Network".to_vec(),
        b"https://pharmacy.abena.health".to_vec()
    )
    verify {
        assert!(PharmacyIntegrations::<T>::contains_key(1u32));
    }

    // ── register_lab ─────────────────────────────────────────────────────────
    register_lab {
        let registrar: T::AccountId = whitelisted_caller();
    }: _(
        RawOrigin::Signed(registrar),
        1u32,
        b"ABENA Genomics Lab".to_vec(),
        b"https://lab.abena.health".to_vec()
    )
    verify {
        assert!(LabIntegrations::<T>::contains_key(1u32));
    }

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}
