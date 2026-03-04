//! Comprehensive tests for the ABENA Interoperability pallet.

use crate::{mock::*, *};
use frame_support::assert_ok;
use sp_core::H256;

fn hash(n: u64) -> H256 { H256::from_low_u64_be(n) }

// ── map_fhir_resource ────────────────────────────────────────────────────────

#[test]
fn map_fhir_resource_patient_type_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::map_fhir_resource(
            RuntimeOrigin::signed(1),
            1,
            FHIRResourceType::Patient,
            hash(100),
            b"record-001".to_vec(),
            DataStandard::HL7_FHIR_R4,
        ));
        assert!(FHIRResources::<Test>::contains_key(1u64, FHIRResourceType::Patient));
    });
}

#[test]
fn map_fhir_resource_observation_type_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::map_fhir_resource(
            RuntimeOrigin::signed(1), 1, FHIRResourceType::Observation,
            hash(101), b"obs-001".to_vec(),
            DataStandard::HL7_FHIR_R4,
        ));
        assert!(FHIRResources::<Test>::contains_key(1u64, FHIRResourceType::Observation));
    });
}

#[test]
fn map_fhir_resource_all_types() {
    new_test_ext().execute_with(|| {
        for (i, rtype) in [
            FHIRResourceType::Patient,
            FHIRResourceType::Observation,
            FHIRResourceType::Medication,
            FHIRResourceType::Condition,
            FHIRResourceType::Procedure,
            FHIRResourceType::DiagnosticReport,
        ].into_iter().enumerate() {
            assert_ok!(Interoperability::map_fhir_resource(
                RuntimeOrigin::signed(1), 1, rtype.clone(),
                hash(i as u64), format!("record-{}", i).into_bytes(),
                DataStandard::HL7_FHIR_R4,
            ));
            assert!(FHIRResources::<Test>::contains_key(1u64, rtype));
        }
    });
}

#[test]
fn map_fhir_resource_stores_correct_hash() {
    new_test_ext().execute_with(|| {
        let expected_hash = hash(999);
        assert_ok!(Interoperability::map_fhir_resource(
            RuntimeOrigin::signed(1), 1, FHIRResourceType::Medication,
            expected_hash, b"med-001".to_vec(),
            DataStandard::HL7_FHIR_R4,
        ));
        let mapping = FHIRResources::<Test>::get(1u64, FHIRResourceType::Medication).unwrap();
        assert_eq!(mapping.fhir_resource_hash, expected_hash);
    });
}

#[test]
fn map_fhir_resource_emits_event() {
    new_test_ext().execute_with(|| {
        let h = hash(50);
        assert_ok!(Interoperability::map_fhir_resource(
            RuntimeOrigin::signed(1), 2, FHIRResourceType::Condition,
            h, b"cond-001".to_vec(),
            DataStandard::HL7_FHIR_R4,
        ));
        System::assert_has_event(RuntimeEvent::Interoperability(
            Event::FHIRResourceMapped {
                patient: 2,
                resource_type: FHIRResourceType::Condition,
                resource_hash: h,
            }
        ));
    });
}

#[test]
fn map_fhir_resource_different_patients_independent() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::map_fhir_resource(
            RuntimeOrigin::signed(1), 1, FHIRResourceType::Patient,
            hash(1), b"r1".to_vec(),
            DataStandard::HL7_FHIR_R4,
        ));
        assert_ok!(Interoperability::map_fhir_resource(
            RuntimeOrigin::signed(1), 2, FHIRResourceType::Patient,
            hash(2), b"r2".to_vec(),
            DataStandard::HL7_FHIR_R4,
        ));
        assert!(FHIRResources::<Test>::contains_key(1u64, FHIRResourceType::Patient));
        assert!(FHIRResources::<Test>::contains_key(2u64, FHIRResourceType::Patient));
    });
}

// ── initiate_cross_chain_exchange ─────────────────────────────────────────────

#[test]
fn initiate_cross_chain_exchange_stores_entry() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::initiate_cross_chain_exchange(
            RuntimeOrigin::signed(1),
            1u64,
            b"abena-chain".to_vec(),
            b"polkadot-parachain".to_vec(),
            hash(200),
        ));
        assert!(CrossChainExchanges::<Test>::contains_key(1u64));
    });
}

#[test]
fn initiate_cross_chain_exchange_sets_pending_status() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::initiate_cross_chain_exchange(
            RuntimeOrigin::signed(1), 1u64,
            b"src".to_vec(), b"tgt".to_vec(), hash(1),
        ));
        let ex = CrossChainExchanges::<Test>::get(1u64).unwrap();
        assert_eq!(ex.status, ExchangeStatus::Pending);
    });
}

#[test]
fn initiate_cross_chain_exchange_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::initiate_cross_chain_exchange(
            RuntimeOrigin::signed(1), 5u64,
            b"chain-a".to_vec(), b"chain-b".to_vec(), hash(5),
        ));
        System::assert_has_event(RuntimeEvent::Interoperability(
            Event::CrossChainExchangeInitiated {
                exchange_id: 5,
                source_chain: b"chain-a".to_vec(),
                target_chain: b"chain-b".to_vec(),
            }
        ));
    });
}

#[test]
fn multiple_exchanges_stored_independently() {
    new_test_ext().execute_with(|| {
        for i in 1u64..=5 {
            assert_ok!(Interoperability::initiate_cross_chain_exchange(
                RuntimeOrigin::signed(1), i,
                b"src".to_vec(), b"tgt".to_vec(), hash(i),
            ));
        }
        for i in 1u64..=5 {
            assert!(CrossChainExchanges::<Test>::contains_key(i));
        }
    });
}

// ── verify_insurance_claim ───────────────────────────────────────────────────

#[test]
fn verify_insurance_claim_stores_entry() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::verify_insurance_claim(
            RuntimeOrigin::signed(1), 1u64, 2, hash(300),
        ));
        assert!(InsuranceClaims::<Test>::contains_key(1u64));
    });
}

#[test]
fn verify_insurance_claim_sets_verified_true() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::verify_insurance_claim(
            RuntimeOrigin::signed(1), 1u64, 2, hash(300),
        ));
        assert!(InsuranceClaims::<Test>::get(1u64).unwrap().verified);
    });
}

#[test]
fn verify_insurance_claim_stores_patient() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::verify_insurance_claim(
            RuntimeOrigin::signed(1), 10u64, 99, hash(1),
        ));
        assert_eq!(InsuranceClaims::<Test>::get(10u64).unwrap().patient, 99u64);
    });
}

#[test]
fn verify_insurance_claim_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::verify_insurance_claim(
            RuntimeOrigin::signed(1), 3u64, 5, hash(1),
        ));
        System::assert_has_event(RuntimeEvent::Interoperability(
            Event::InsuranceClaimVerified { claim_id: 3, patient: 5, verified: true }
        ));
    });
}

#[test]
fn multiple_claims_stored_independently() {
    new_test_ext().execute_with(|| {
        for i in 1u64..=5 {
            assert_ok!(Interoperability::verify_insurance_claim(
                RuntimeOrigin::signed(1), i, i, hash(i),
            ));
        }
        for i in 1u64..=5 {
            assert!(InsuranceClaims::<Test>::contains_key(i));
        }
    });
}

// ── register_pharmacy ────────────────────────────────────────────────────────

#[test]
fn register_pharmacy_stores_entry() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::register_pharmacy(
            RuntimeOrigin::signed(1),
            1u32,
            b"Accra Central Pharmacy".to_vec(),
            b"https://pharmacy.example.com".to_vec(),
        ));
        assert!(PharmacyIntegrations::<Test>::contains_key(1u32));
    });
}

#[test]
fn register_pharmacy_sets_active_true() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::register_pharmacy(
            RuntimeOrigin::signed(1), 1u32,
            b"Pharmacy".to_vec(), b"endpoint".to_vec(),
        ));
        assert!(PharmacyIntegrations::<Test>::get(1u32).unwrap().active);
    });
}

#[test]
fn register_pharmacy_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::register_pharmacy(
            RuntimeOrigin::signed(1), 5u32,
            b"Test Pharmacy".to_vec(), b"endpoint".to_vec(),
        ));
        System::assert_has_event(RuntimeEvent::Interoperability(
            Event::PharmacyIntegrationRegistered {
                pharmacy_id: 5,
                pharmacy_name: b"Test Pharmacy".to_vec(),
            }
        ));
    });
}

#[test]
fn multiple_pharmacies_stored_independently() {
    new_test_ext().execute_with(|| {
        for i in 1u32..=3 {
            assert_ok!(Interoperability::register_pharmacy(
                RuntimeOrigin::signed(1), i,
                format!("Pharmacy {}", i).into_bytes(), b"ep".to_vec(),
            ));
        }
        for i in 1u32..=3 {
            assert!(PharmacyIntegrations::<Test>::contains_key(i));
        }
    });
}

// ── register_lab ─────────────────────────────────────────────────────────────

#[test]
fn register_lab_stores_entry() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::register_lab(
            RuntimeOrigin::signed(1), 1u32,
            b"Korle Bu Lab".to_vec(), b"https://lab.example.com".to_vec(),
        ));
        assert!(LabIntegrations::<Test>::contains_key(1u32));
    });
}

#[test]
fn register_lab_sets_active_true() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::register_lab(
            RuntimeOrigin::signed(1), 1u32, b"Lab".to_vec(), b"ep".to_vec(),
        ));
        assert!(LabIntegrations::<Test>::get(1u32).unwrap().active);
    });
}

#[test]
fn register_lab_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(Interoperability::register_lab(
            RuntimeOrigin::signed(1), 7u32, b"Genomics Lab".to_vec(), b"ep".to_vec(),
        ));
        System::assert_has_event(RuntimeEvent::Interoperability(
            Event::LabIntegrationRegistered { lab_id: 7, lab_name: b"Genomics Lab".to_vec() }
        ));
    });
}

// ── integration ──────────────────────────────────────────────────────────────

#[test]
fn integration_full_patient_data_flow() {
    new_test_ext().execute_with(|| {
        // Register pharmacy and lab
        assert_ok!(Interoperability::register_pharmacy(
            RuntimeOrigin::signed(1), 1u32, b"Pharmacy A".to_vec(), b"ep".to_vec()
        ));
        assert_ok!(Interoperability::register_lab(
            RuntimeOrigin::signed(1), 1u32, b"Lab A".to_vec(), b"ep".to_vec()
        ));

        // Map FHIR resources for patient
        for rtype in [FHIRResourceType::Patient, FHIRResourceType::Observation, FHIRResourceType::Medication] {
            assert_ok!(Interoperability::map_fhir_resource(
                RuntimeOrigin::signed(1), 100, rtype.clone(),
                H256::random(), b"record".to_vec(),
                DataStandard::HL7_FHIR_R4,
            ));
        }

        // Verify insurance claim
        assert_ok!(Interoperability::verify_insurance_claim(
            RuntimeOrigin::signed(1), 1u64, 100, hash(500),
        ));

        // Initiate cross-chain exchange
        assert_ok!(Interoperability::initiate_cross_chain_exchange(
            RuntimeOrigin::signed(1), 1u64,
            b"abena".to_vec(), b"polkadot".to_vec(), hash(600),
        ));

        assert!(InsuranceClaims::<Test>::contains_key(1u64));
        assert!(CrossChainExchanges::<Test>::contains_key(1u64));
    });
}
