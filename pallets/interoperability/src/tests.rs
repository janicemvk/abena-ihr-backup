//! Tests for interoperability pallet

use crate::mock::*;
use crate::*;
use frame_support::assert_ok;
use sp_core::H256;

#[test]
fn map_fhir_resource_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let mapper = 2u64;
        let resource_type = FHIRResourceType::Patient;
        let fhir_hash = H256::from_slice(&[1u8; 32]);
        let record_id = b"record123".to_vec();

        assert_ok!(Interoperability::map_fhir_resource(
            RuntimeOrigin::signed(mapper),
            patient,
            resource_type.clone(),
            fhir_hash,
            record_id.clone()
        ));

        let mapping = Interoperability::fhir_resources(patient, resource_type);
        assert!(mapping.is_some());
        assert_eq!(mapping.unwrap().fhir_resource_hash, fhir_hash);
    });
}

#[test]
fn initiate_cross_chain_exchange_works() {
    new_test_ext().execute_with(|| {
        let initiator = 1u64;
        let exchange_id = 1u64;
        let source_chain = b"abena-chain".to_vec();
        let target_chain = b"ethereum".to_vec();
        let data_hash = H256::from_slice(&[1u8; 32]);

        assert_ok!(Interoperability::initiate_cross_chain_exchange(
            RuntimeOrigin::signed(initiator),
            exchange_id,
            source_chain.clone(),
            target_chain.clone(),
            data_hash
        ));

        let exchange = Interoperability::cross_chain_exchanges(exchange_id);
        assert!(exchange.is_some());
        assert_eq!(exchange.unwrap().source_chain, source_chain);
        assert_eq!(exchange.unwrap().target_chain, target_chain);
    });
}

#[test]
fn verify_insurance_claim_works() {
    new_test_ext().execute_with(|| {
        let verifier = 1u64;
        let patient = 2u64;
        let claim_id = 1u64;
        let claim_hash = H256::from_slice(&[1u8; 32]);

        assert_ok!(Interoperability::verify_insurance_claim(
            RuntimeOrigin::signed(verifier),
            claim_id,
            patient,
            claim_hash
        ));

        let claim = Interoperability::insurance_claims(claim_id);
        assert!(claim.is_some());
        assert_eq!(claim.unwrap().patient, patient);
        assert!(claim.unwrap().verified);
    });
}

#[test]
fn register_pharmacy_and_lab_works() {
    new_test_ext().execute_with(|| {
        let registrar = 1u64;
        let pharmacy_id = 1u32;
        let pharmacy_name = b"ABC Pharmacy".to_vec();
        let endpoint = b"https://pharmacy.example.com".to_vec();

        assert_ok!(Interoperability::register_pharmacy(
            RuntimeOrigin::signed(registrar),
            pharmacy_id,
            pharmacy_name.clone(),
            endpoint.clone()
        ));

        let pharmacy = Interoperability::pharmacy_integrations(pharmacy_id);
        assert!(pharmacy.is_some());
        assert_eq!(pharmacy.unwrap().pharmacy_name, pharmacy_name);

        let lab_id = 1u32;
        let lab_name = b"XYZ Lab".to_vec();
        let lab_endpoint = b"https://lab.example.com".to_vec();

        assert_ok!(Interoperability::register_lab(
            RuntimeOrigin::signed(registrar),
            lab_id,
            lab_name.clone(),
            lab_endpoint.clone()
        ));

        let lab = Interoperability::lab_integrations(lab_id);
        assert!(lab.is_some());
        assert_eq!(lab.unwrap().lab_name, lab_name);
    });
}

