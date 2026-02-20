//! Tests for treatment protocol pallet

use crate::mock::*;
use crate::*;
use frame_support::{assert_err, assert_ok};

#[test]
fn create_protocol_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        let protocol_id = 1u64;
        let treatments = vec![Treatment {
            treatment_type: TreatmentType::Medication,
            details: b"aspirin 100mg".to_vec(),
            modality: Modality::Western,
            dosage: b"daily".to_vec(),
        }];

        assert_ok!(TreatmentProtocol::create_protocol(
            RuntimeOrigin::signed(provider),
            patient,
            protocol_id,
            treatments.clone(),
            None
        ));

        let protocol = TreatmentProtocol::treatment_protocols(patient, protocol_id);
        assert!(protocol.is_some());
        assert_eq!(protocol.unwrap().treatments, treatments);
        assert_eq!(protocol.unwrap().status, ProtocolStatus::Active);
    });
}

#[test]
fn validate_protocol_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        let protocol_id = 1u64;
        let treatments = vec![Treatment {
            treatment_type: TreatmentType::Medication,
            details: b"aspirin 100mg".to_vec(),
            modality: Modality::Western,
            dosage: b"daily".to_vec(),
        }];

        assert_ok!(TreatmentProtocol::create_protocol(
            RuntimeOrigin::signed(provider),
            patient,
            protocol_id,
            treatments,
            None
        ));

        assert_ok!(TreatmentProtocol::validate_protocol(
            RuntimeOrigin::signed(provider),
            patient,
            protocol_id
        ));
    });
}

#[test]
fn update_protocol_works() {
    new_test_ext().execute_with(|| {
        let patient = 1u64;
        let provider = 2u64;
        let protocol_id = 1u64;
        let initial_treatments = vec![Treatment {
            treatment_type: TreatmentType::Medication,
            details: b"aspirin 100mg".to_vec(),
            modality: Modality::Western,
            dosage: b"daily".to_vec(),
        }];

        assert_ok!(TreatmentProtocol::create_protocol(
            RuntimeOrigin::signed(provider),
            patient,
            protocol_id,
            initial_treatments,
            None
        ));

        let updated_treatments = vec![Treatment {
            treatment_type: TreatmentType::Medication,
            details: b"aspirin 200mg".to_vec(),
            modality: Modality::Western,
            dosage: b"twice daily".to_vec(),
        }];

        assert_ok!(TreatmentProtocol::update_protocol(
            RuntimeOrigin::signed(provider),
            patient,
            protocol_id,
            updated_treatments.clone()
        ));

        let protocol = TreatmentProtocol::treatment_protocols(patient, protocol_id);
        assert_eq!(protocol.unwrap().treatments, updated_treatments);
        assert_eq!(protocol.unwrap().status, ProtocolStatus::Updated);
    });
}

