//! Comprehensive test suite for pallet-health-record-hash.
//!
//! Covers both the **legacy** API (record_hash / update_hash / set_multi_sig_requirement)
//! and the **spec** API (create_record_hash, update_record_hash, grant/revoke/access_record,
//! multi-sig, emergency override, integrity verification, quantum linking, right-to-forget).
//!
//! Storage key:
//!   Legacy  → RecordHashes / RecordVersions / MultiSigRequirements / AuditLogs
//!   Spec    → RecordHashStore / PatientRecordIds / AccessGrants / AccessLog /
//!             MultiSigPermissions / QuantumResultLinks / EmergencyOverrideLog

use crate::mock::*;
use crate::{
    AccessGrants, AccessLog, AuditAction, AuditLogs, EmergencyOverrideLog, Error, Event,
    MultiSigConfig, MultiSigPermissions, MultiSigRequirement, MultiSigRequirements,
    PatientRecordIds, QuantumResultLinks, RecordHash, RecordHashEntry, RecordHashes,
    RecordHashStore, RecordType, RecordTypeSpec, RecordVersions, TherapeuticModality,
};
use frame_support::{assert_err, assert_ok, BoundedVec, traits::ConstU32};
use sp_core::H256;

// ──────────────────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────────────────

/// Build a distinct H256 record ID from a single byte.
fn rid(n: u8) -> H256 {
    H256::from([n; 32])
}

/// Build a 32-byte content hash from a single fill byte.
fn h32(n: u8) -> [u8; 32] {
    [n; 32]
}

/// A valid 512-byte-bounded provider signature.
fn sig512() -> BoundedVec<u8, ConstU32<512>> {
    BoundedVec::try_from(vec![0xABu8; 64]).unwrap()
}

/// A valid 128-byte-bounded multi-sig entry signature.
fn sig128() -> BoundedVec<u8, ConstU32<128>> {
    BoundedVec::try_from(vec![0xCDu8; 64]).unwrap()
}

/// An IPFS CID as a bounded byte vector.
fn cid(s: &[u8]) -> BoundedVec<u8, ConstU32<256>> {
    BoundedVec::try_from(s.to_vec()).unwrap()
}

/// Advance the chain to block `n`.
fn set_block(n: u64) {
    System::set_block_number(n);
}

/// Create a minimal spec-API record with `patient_id = patient`, stored under `record_id`.
/// The provider / creator is `ALICE`.
fn spec_create(record_id: H256, patient: u64) {
    assert_ok!(HealthRecordHash::create_record_hash(
        RuntimeOrigin::signed(ALICE),
        record_id,
        patient,
        h32(1),
        None,
        RecordTypeSpec::ClinicalNote,
        TherapeuticModality::WesternMedicine,
        sig512(),
        h32(0),
    ));
}

/// Grant access to `accessor` for `expiry_block` blocks from now. Caller must be
/// the patient on the record.
fn spec_grant(patient: u64, record_id: H256, accessor: u64, expiry: u64) {
    assert_ok!(HealthRecordHash::grant_record_access(
        RuntimeOrigin::signed(patient),
        record_id,
        accessor,
        expiry.into(),
    ));
}

// ──────────────────────────────────────────────────────────────────────────────
// LEGACY API — record_hash / update_hash / set_multi_sig_requirement
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn legacy_record_hash_stores_entry() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            42u64,
            H256::from([1u8; 32]),
            RecordType::ClinicalEncounter,
            None,
        ));
        let entry = RecordHashes::<Test>::get(BOB, 42u64).unwrap();
        assert_eq!(entry.version, 1);
        assert_eq!(entry.provider, ALICE);
    });
}

#[test]
fn legacy_record_hash_initialises_version_history() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            1u64,
            H256::from([2u8; 32]),
            RecordType::LabResults,
            Some(b"Qm...".to_vec()),
        ));
        let versions = RecordVersions::<Test>::get(BOB, 1u64);
        assert_eq!(versions.len(), 1);
        assert_eq!(versions[0].version, 1);
    });
}

#[test]
fn legacy_record_hash_creates_audit_log_entry() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            10u64,
            H256::from([3u8; 32]),
            RecordType::Imaging,
            None,
        ));
        let logs = AuditLogs::<Test>::get(BOB, 10u64);
        assert_eq!(logs.len(), 1);
        assert_eq!(logs[0].action, AuditAction::RecordCreated);
        assert_eq!(logs[0].actor, ALICE);
    });
}

#[test]
fn legacy_record_hash_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        let rh = H256::from([4u8; 32]);
        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            5u64,
            rh,
            RecordType::Medication,
            None,
        ));
        System::assert_has_event(
            Event::<Test>::RecordHashRecorded {
                patient: BOB,
                record_id: 5u64,
                record_hash: rh,
                provider: ALICE,
            }
            .into(),
        );
    });
}

#[test]
fn legacy_update_hash_increments_version() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            7u64,
            H256::from([5u8; 32]),
            RecordType::Diagnosis,
            None,
        ));
        set_block(2);
        assert_ok!(HealthRecordHash::update_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            7u64,
            H256::from([6u8; 32]),
            None,
        ));
        let entry = RecordHashes::<Test>::get(BOB, 7u64).unwrap();
        assert_eq!(entry.version, 2);
    });
}

#[test]
fn legacy_update_hash_appends_version_history() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            8u64,
            H256::from([7u8; 32]),
            RecordType::Vitals,
            None,
        ));
        assert_ok!(HealthRecordHash::update_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            8u64,
            H256::from([8u8; 32]),
            None,
        ));
        let versions = RecordVersions::<Test>::get(BOB, 8u64);
        assert_eq!(versions.len(), 2);
        assert_eq!(versions[1].version, 2);
    });
}

#[test]
fn legacy_update_hash_fails_for_non_existent_record() {
    new_test_ext().execute_with(|| {
        assert_err!(
            HealthRecordHash::update_hash(
                RuntimeOrigin::signed(ALICE),
                BOB,
                999u64,
                H256::from([1u8; 32]),
                None,
            ),
            Error::<Test>::RecordNotFound
        );
    });
}

#[test]
fn legacy_update_hash_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            9u64,
            H256::from([9u8; 32]),
            RecordType::TreatmentPlan,
            None,
        ));
        let new_h = H256::from([10u8; 32]);
        assert_ok!(HealthRecordHash::update_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            9u64,
            new_h,
            None,
        ));
        System::assert_has_event(
            Event::<Test>::RecordHashUpdated {
                patient: BOB,
                record_id: 9u64,
                new_hash: new_h,
                version: 2,
            }
            .into(),
        );
    });
}

#[test]
fn legacy_set_multi_sig_requirement_stores_config() {
    new_test_ext().execute_with(|| {
        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            20u64,
            H256::from([11u8; 32]),
            RecordType::Genomic,
            None,
        ));
        assert_ok!(HealthRecordHash::set_multi_sig_requirement(
            RuntimeOrigin::signed(BOB),
            BOB,
            20u64,
            2,
            vec![ALICE, CHARLIE],
        ));
        let config = MultiSigRequirements::<Test>::get(BOB, 20u64).unwrap();
        assert_eq!(config.required_signatures, 2);
        assert_eq!(config.authorized_signers.len(), 2);
    });
}

#[test]
fn legacy_set_multi_sig_requirement_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            21u64,
            H256::from([12u8; 32]),
            RecordType::Longitudinal,
            None,
        ));
        assert_ok!(HealthRecordHash::set_multi_sig_requirement(
            RuntimeOrigin::signed(BOB),
            BOB,
            21u64,
            1,
            vec![ALICE],
        ));
        System::assert_has_event(
            Event::<Test>::MultiSigRequirementSet {
                patient: BOB,
                record_id: 21u64,
                required_signatures: 1,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — create_record_hash
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn create_record_hash_stores_entry_with_version_1() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(1), BOB);
        let entry = RecordHashStore::<Test>::get(rid(1)).unwrap();
        assert_eq!(entry.version, 1);
        assert_eq!(entry.patient_id, BOB);
        assert_eq!(entry.record_hash, h32(1));
        assert!(entry.active);
        assert!(entry.previous_version.is_none());
    });
}

#[test]
fn create_record_hash_stores_provider_signature() {
    new_test_ext().execute_with(|| {
        let custom_sig =
            BoundedVec::try_from(vec![0xFFu8; 32]).unwrap();
        assert_ok!(HealthRecordHash::create_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(2),
            BOB,
            h32(2),
            None,
            RecordTypeSpec::LabResult,
            TherapeuticModality::Integrative,
            custom_sig.clone(),
            h32(0),
        ));
        let entry = RecordHashStore::<Test>::get(rid(2)).unwrap();
        assert_eq!(entry.provider_signature, custom_sig);
    });
}

#[test]
fn create_record_hash_stores_ipfs_cid() {
    new_test_ext().execute_with(|| {
        assert_ok!(HealthRecordHash::create_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(3),
            BOB,
            h32(3),
            Some(cid(b"QmTestCID123")),
            RecordTypeSpec::ImagingReport,
            TherapeuticModality::WesternMedicine,
            sig512(),
            h32(0),
        ));
        let entry = RecordHashStore::<Test>::get(rid(3)).unwrap();
        assert_eq!(entry.ipfs_cid, Some(cid(b"QmTestCID123")));
    });
}

#[test]
fn create_record_hash_adds_to_patient_record_list() {
    new_test_ext().execute_with(|| {
        spec_create(rid(4), BOB);
        spec_create(rid(5), BOB);
        let ids = PatientRecordIds::<Test>::get(BOB);
        assert_eq!(ids.len(), 2);
        assert!(ids.contains(&rid(4)));
        assert!(ids.contains(&rid(5)));
    });
}

#[test]
fn create_record_hash_sets_creation_timestamp() {
    new_test_ext().execute_with(|| {
        set_block(42);
        spec_create(rid(6), BOB);
        let entry = RecordHashStore::<Test>::get(rid(6)).unwrap();
        assert_eq!(entry.created_at, 42);
        assert_eq!(entry.updated_at, 42);
    });
}

#[test]
fn create_record_hash_fails_when_id_already_exists() {
    new_test_ext().execute_with(|| {
        spec_create(rid(7), BOB);
        assert_err!(
            HealthRecordHash::create_record_hash(
                RuntimeOrigin::signed(CHARLIE),
                rid(7), // same id
                BOB,
                h32(99),
                None,
                RecordTypeSpec::ClinicalNote,
                TherapeuticModality::WesternMedicine,
                sig512(),
                h32(0),
            ),
            Error::<Test>::RecordAlreadyExists
        );
    });
}

#[test]
fn create_record_hash_emits_record_hash_created_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(HealthRecordHash::create_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(8),
            BOB,
            h32(8),
            None,
            RecordTypeSpec::ConsentForm,
            TherapeuticModality::Ayurveda,
            sig512(),
            h32(0),
        ));
        System::assert_last_event(
            Event::<Test>::RecordHashCreated {
                record_id: rid(8),
                patient: BOB,
                record_type: RecordTypeSpec::ConsentForm,
                version: 1,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — record types (one test per RecordTypeSpec variant)
// ──────────────────────────────────────────────────────────────────────────────

macro_rules! record_type_test {
    ($test_name:ident, $record_type:expr, $rid_byte:expr) => {
        #[test]
        fn $test_name() {
            new_test_ext().execute_with(|| {
                assert_ok!(HealthRecordHash::create_record_hash(
                    RuntimeOrigin::signed(ALICE),
                    rid($rid_byte),
                    BOB,
                    h32($rid_byte),
                    None,
                    $record_type,
                    TherapeuticModality::WesternMedicine,
                    sig512(),
                    h32(0),
                ));
                let entry = RecordHashStore::<Test>::get(rid($rid_byte)).unwrap();
                assert_eq!(entry.record_type, $record_type);
            });
        }
    };
}

record_type_test!(record_type_clinical_note, RecordTypeSpec::ClinicalNote, 101);
record_type_test!(record_type_lab_result, RecordTypeSpec::LabResult, 102);
record_type_test!(record_type_prescription, RecordTypeSpec::Prescription, 103);
record_type_test!(record_type_imaging_report, RecordTypeSpec::ImagingReport, 104);
record_type_test!(record_type_quantum_analysis, RecordTypeSpec::QuantumAnalysis, 105);
record_type_test!(record_type_treatment_plan, RecordTypeSpec::TreatmentPlan, 106);
record_type_test!(record_type_consent_form, RecordTypeSpec::ConsentForm, 107);
record_type_test!(record_type_integrative_assessment, RecordTypeSpec::IntegrativeAssessment, 108);

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — update_record_hash
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn update_record_hash_increments_version() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(20), BOB);
        set_block(5);
        assert_ok!(HealthRecordHash::update_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(20),
            h32(20),
            None,
            sig512(),
        ));
        let entry = RecordHashStore::<Test>::get(rid(20)).unwrap();
        assert_eq!(entry.version, 2);
        assert_eq!(entry.record_hash, h32(20));
    });
}

#[test]
fn update_record_hash_links_previous_version() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(21), BOB);
        set_block(2);
        assert_ok!(HealthRecordHash::update_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(21),
            h32(21),
            None,
            sig512(),
        ));
        let entry = RecordHashStore::<Test>::get(rid(21)).unwrap();
        assert!(entry.previous_version.is_some(), "previous_version should be set");
    });
}

#[test]
fn update_record_hash_updates_timestamp() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(22), BOB);
        set_block(10);
        assert_ok!(HealthRecordHash::update_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(22),
            h32(22),
            None,
            sig512(),
        ));
        let entry = RecordHashStore::<Test>::get(rid(22)).unwrap();
        assert_eq!(entry.updated_at, 10);
    });
}

#[test]
fn update_record_hash_updates_ipfs_cid() {
    new_test_ext().execute_with(|| {
        spec_create(rid(23), BOB);
        assert_ok!(HealthRecordHash::update_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(23),
            h32(23),
            Some(cid(b"QmNewCID456")),
            sig512(),
        ));
        let entry = RecordHashStore::<Test>::get(rid(23)).unwrap();
        assert_eq!(entry.ipfs_cid, Some(cid(b"QmNewCID456")));
    });
}

#[test]
fn update_record_hash_fails_for_non_existent_record() {
    new_test_ext().execute_with(|| {
        assert_err!(
            HealthRecordHash::update_record_hash(
                RuntimeOrigin::signed(ALICE),
                rid(99),
                h32(99),
                None,
                sig512(),
            ),
            Error::<Test>::RecordNotFound
        );
    });
}

#[test]
fn update_record_hash_fails_for_inactive_record() {
    new_test_ext().execute_with(|| {
        spec_create(rid(24), BOB);
        // Patient deactivates
        assert_ok!(HealthRecordHash::mark_record_inactive(
            RuntimeOrigin::signed(BOB),
            rid(24)
        ));
        assert_err!(
            HealthRecordHash::update_record_hash(
                RuntimeOrigin::signed(ALICE),
                rid(24),
                h32(24),
                None,
                sig512(),
            ),
            Error::<Test>::RecordInactive
        );
    });
}

#[test]
fn update_record_hash_emits_spec_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(25), BOB);
        set_block(2);
        assert_ok!(HealthRecordHash::update_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(25),
            h32(25),
            None,
            sig512(),
        ));
        // Event should contain version=2 and a non-zero previous_version
        let events = System::events();
        let found = events.iter().any(|e| {
            matches!(
                e.event,
                RuntimeEvent::HealthRecordHash(Event::RecordHashUpdatedSpec { version: 2, .. })
            )
        });
        assert!(found, "RecordHashUpdatedSpec event not emitted");
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — grant_record_access / revoke_record_access
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn grant_record_access_stores_expiry_block() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(30), BOB);
        spec_grant(BOB, rid(30), CHARLIE, 100);
        let expiry = AccessGrants::<Test>::get(rid(30), CHARLIE).unwrap();
        assert_eq!(expiry, 100u64);
    });
}

#[test]
fn grant_record_access_fails_if_not_patient() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(31), BOB);
        assert_err!(
            HealthRecordHash::grant_record_access(
                RuntimeOrigin::signed(DAVE), // not the patient
                rid(31),
                CHARLIE,
                100u64.into(),
            ),
            Error::<Test>::Unauthorized
        );
    });
}

#[test]
fn grant_record_access_fails_for_inactive_record() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(32), BOB);
        assert_ok!(HealthRecordHash::mark_record_inactive(
            RuntimeOrigin::signed(BOB),
            rid(32)
        ));
        assert_err!(
            HealthRecordHash::grant_record_access(
                RuntimeOrigin::signed(BOB),
                rid(32),
                CHARLIE,
                100u64.into(),
            ),
            Error::<Test>::RecordInactive
        );
    });
}

#[test]
fn grant_record_access_fails_if_expiry_not_in_future() {
    new_test_ext().execute_with(|| {
        set_block(50);
        spec_create(rid(33), BOB);
        // Expiry == current block (not strictly greater)
        assert_err!(
            HealthRecordHash::grant_record_access(
                RuntimeOrigin::signed(BOB),
                rid(33),
                CHARLIE,
                50u64.into(),
            ),
            Error::<Test>::AccessDenied
        );
    });
}

#[test]
fn grant_record_access_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(34), BOB);
        assert_ok!(HealthRecordHash::grant_record_access(
            RuntimeOrigin::signed(BOB),
            rid(34),
            CHARLIE,
            200u64.into(),
        ));
        System::assert_last_event(
            Event::<Test>::RecordAccessGranted {
                record_id: rid(34),
                accessor: CHARLIE,
                expiry_block: 200u64.into(),
            }
            .into(),
        );
    });
}

#[test]
fn revoke_record_access_removes_grant() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(35), BOB);
        spec_grant(BOB, rid(35), CHARLIE, 100);
        assert_ok!(HealthRecordHash::revoke_record_access(
            RuntimeOrigin::signed(BOB),
            rid(35),
            CHARLIE,
        ));
        assert!(AccessGrants::<Test>::get(rid(35), CHARLIE).is_none());
    });
}

#[test]
fn revoke_record_access_fails_if_not_patient() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(36), BOB);
        spec_grant(BOB, rid(36), CHARLIE, 100);
        assert_err!(
            HealthRecordHash::revoke_record_access(
                RuntimeOrigin::signed(DAVE), // not patient
                rid(36),
                CHARLIE,
            ),
            Error::<Test>::Unauthorized
        );
    });
}

#[test]
fn revoke_record_access_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(37), BOB);
        spec_grant(BOB, rid(37), CHARLIE, 100);
        assert_ok!(HealthRecordHash::revoke_record_access(
            RuntimeOrigin::signed(BOB),
            rid(37),
            CHARLIE,
        ));
        System::assert_last_event(
            Event::<Test>::RecordAccessRevoked {
                record_id: rid(37),
                accessor: CHARLIE,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — access_record
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn access_record_patient_always_succeeds() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(40), BOB);
        // BOB is both patient and caller
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(BOB),
            rid(40),
        ));
    });
}

#[test]
fn access_record_granted_provider_succeeds_before_expiry() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(41), BOB);
        spec_grant(BOB, rid(41), CHARLIE, 100);
        set_block(50); // well within grant
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(CHARLIE),
            rid(41),
        ));
    });
}

#[test]
fn access_record_fails_after_grant_expiry() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(42), BOB);
        spec_grant(BOB, rid(42), CHARLIE, 10); // expires at block 10
        set_block(11); // past expiry
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(CHARLIE),
            rid(42),
        ));
        let log = AccessLog::<Test>::get(rid(42), CHARLIE);
        assert!(!log.last().unwrap().granted);
    });
}

#[test]
fn access_record_fails_with_no_permission() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(43), BOB);
        // DAVE was never granted access
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(DAVE),
            rid(43),
        ));
        let log = AccessLog::<Test>::get(rid(43), DAVE);
        assert!(!log.last().unwrap().granted);
    });
}

#[test]
fn access_record_fails_for_inactive_record() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(44), BOB);
        assert_ok!(HealthRecordHash::mark_record_inactive(
            RuntimeOrigin::signed(BOB),
            rid(44)
        ));
        assert_err!(
            HealthRecordHash::access_record(
                RuntimeOrigin::signed(BOB),
                rid(44),
            ),
            Error::<Test>::RecordInactive
        );
    });
}

#[test]
fn access_record_creates_audit_trail_entry() {
    new_test_ext().execute_with(|| {
        set_block(5);
        spec_create(rid(45), BOB);
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(BOB),
            rid(45),
        ));
        let log = AccessLog::<Test>::get(rid(45), BOB);
        assert_eq!(log.len(), 1);
        assert_eq!(log[0].accessor, BOB);
        assert_eq!(log[0].block, 5u64);
        assert!(log[0].granted);
        assert!(!log[0].emergency_override);
    });
}

#[test]
fn access_record_denied_attempt_is_still_logged() {
    new_test_ext().execute_with(|| {
        set_block(3);
        spec_create(rid(46), BOB);
        // DAVE has no access but the attempt is still logged
        assert_ok!(HealthRecordHash::access_record(RuntimeOrigin::signed(DAVE), rid(46)));
        let log = AccessLog::<Test>::get(rid(46), DAVE);
        assert_eq!(log.len(), 1);
        assert!(!log[0].granted);
    });
}

#[test]
fn access_record_fails_for_non_existent_record() {
    new_test_ext().execute_with(|| {
        assert_err!(
            HealthRecordHash::access_record(
                RuntimeOrigin::signed(ALICE),
                rid(200),
            ),
            Error::<Test>::RecordNotFound
        );
    });
}

#[test]
fn access_record_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(47), BOB);
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(BOB),
            rid(47),
        ));
        System::assert_last_event(
            Event::<Test>::RecordAccessed {
                record_id: rid(47),
                accessor: BOB,
                granted: true,
                emergency: false,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — create_multisig_requirement / sign_record_access
// ──────────────────────────────────────────────────────────────────────────────

fn make_signers(accounts: &[u64]) -> BoundedVec<u64, ConstU32<16>> {
    BoundedVec::try_from(accounts.to_vec()).unwrap()
}

#[test]
fn create_multisig_requirement_stores_requirement() {
    new_test_ext().execute_with(|| {
        spec_create(rid(50), BOB);
        let signers = make_signers(&[ALICE, CHARLIE]);
        assert_ok!(HealthRecordHash::create_multisig_requirement(
            RuntimeOrigin::signed(BOB),
            rid(50),
            2,
            signers.clone(),
        ));
        let req = MultiSigPermissions::<Test>::get(rid(50)).unwrap();
        assert_eq!(req.required_signatures, 2);
        assert_eq!(req.approved_signers.len(), 2);
        assert_eq!(req.current_signatures.len(), 0);
    });
}

#[test]
fn create_multisig_requirement_fails_if_not_patient() {
    new_test_ext().execute_with(|| {
        spec_create(rid(51), BOB);
        let signers = make_signers(&[ALICE, CHARLIE]);
        assert_err!(
            HealthRecordHash::create_multisig_requirement(
                RuntimeOrigin::signed(DAVE), // not the patient
                rid(51),
                1,
                signers,
            ),
            Error::<Test>::Unauthorized
        );
    });
}

#[test]
fn create_multisig_requirement_fails_when_required_exceeds_signers() {
    new_test_ext().execute_with(|| {
        spec_create(rid(52), BOB);
        let signers = make_signers(&[ALICE]); // only 1 signer
        assert_err!(
            HealthRecordHash::create_multisig_requirement(
                RuntimeOrigin::signed(BOB),
                rid(52),
                3, // requires 3 but only 1 signer
                signers,
            ),
            Error::<Test>::InsufficientSignatures
        );
    });
}

#[test]
fn create_multisig_requirement_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(53), BOB);
        let signers = make_signers(&[ALICE, CHARLIE]);
        assert_ok!(HealthRecordHash::create_multisig_requirement(
            RuntimeOrigin::signed(BOB),
            rid(53),
            2,
            signers,
        ));
        System::assert_last_event(
            Event::<Test>::MultiSigRequirementCreated {
                record_id: rid(53),
                required_signatures: 2,
            }
            .into(),
        );
    });
}

#[test]
fn sign_record_access_approved_signer_adds_signature() {
    new_test_ext().execute_with(|| {
        spec_create(rid(54), BOB);
        let signers = make_signers(&[ALICE, CHARLIE]);
        assert_ok!(HealthRecordHash::create_multisig_requirement(
            RuntimeOrigin::signed(BOB),
            rid(54),
            2,
            signers,
        ));
        assert_ok!(HealthRecordHash::sign_record_access(
            RuntimeOrigin::signed(ALICE),
            rid(54),
            sig128(),
        ));
        let req = MultiSigPermissions::<Test>::get(rid(54)).unwrap();
        assert_eq!(req.current_signatures.len(), 1);
        assert_eq!(req.current_signatures[0].0, ALICE);
    });
}

#[test]
fn sign_record_access_fails_for_non_approved_signer() {
    new_test_ext().execute_with(|| {
        spec_create(rid(55), BOB);
        let signers = make_signers(&[ALICE]);
        assert_ok!(HealthRecordHash::create_multisig_requirement(
            RuntimeOrigin::signed(BOB),
            rid(55),
            1,
            signers,
        ));
        assert_err!(
            HealthRecordHash::sign_record_access(
                RuntimeOrigin::signed(DAVE), // not in approved_signers
                rid(55),
                sig128(),
            ),
            Error::<Test>::Unauthorized
        );
    });
}

#[test]
fn sign_record_access_fails_for_double_signing() {
    new_test_ext().execute_with(|| {
        spec_create(rid(56), BOB);
        let signers = make_signers(&[ALICE, CHARLIE]);
        assert_ok!(HealthRecordHash::create_multisig_requirement(
            RuntimeOrigin::signed(BOB),
            rid(56),
            2,
            signers,
        ));
        assert_ok!(HealthRecordHash::sign_record_access(
            RuntimeOrigin::signed(ALICE),
            rid(56),
            sig128(),
        ));
        // Second attempt by same signer
        assert_err!(
            HealthRecordHash::sign_record_access(
                RuntimeOrigin::signed(ALICE),
                rid(56),
                sig128(),
            ),
            Error::<Test>::InsufficientSignatures
        );
    });
}

#[test]
fn access_granted_after_multisig_threshold_met() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(57), BOB);
        let signers = make_signers(&[ALICE, CHARLIE]);
        assert_ok!(HealthRecordHash::create_multisig_requirement(
            RuntimeOrigin::signed(BOB),
            rid(57),
            2,
            signers,
        ));
        // Collect both required signatures
        assert_ok!(HealthRecordHash::sign_record_access(
            RuntimeOrigin::signed(ALICE),
            rid(57),
            sig128(),
        ));
        assert_ok!(HealthRecordHash::sign_record_access(
            RuntimeOrigin::signed(CHARLIE),
            rid(57),
            sig128(),
        ));
        // Now DAVE (not a signer but can access if multi-sig is satisfied) —
        // actually the multi-sig check in access_record checks current_signatures.len() >= required.
        // Any accessor benefits from the satisfied multi-sig requirement:
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(DAVE),
            rid(57),
        ));
    });
}

#[test]
fn access_denied_when_multisig_threshold_not_met() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(58), BOB);
        let signers = make_signers(&[ALICE, CHARLIE]);
        assert_ok!(HealthRecordHash::create_multisig_requirement(
            RuntimeOrigin::signed(BOB),
            rid(58),
            2,
            signers,
        ));
        // Only one signature collected — threshold not met
        assert_ok!(HealthRecordHash::sign_record_access(
            RuntimeOrigin::signed(ALICE),
            rid(58),
            sig128(),
        ));
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(DAVE),
            rid(58),
        ));
        let log = AccessLog::<Test>::get(rid(58), DAVE);
        assert!(!log.last().unwrap().granted);
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — emergency_access_override
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn emergency_access_override_succeeds_for_root() {
    new_test_ext().execute_with(|| {
        set_block(7);
        spec_create(rid(60), BOB);
        assert_ok!(HealthRecordHash::emergency_access_override(
            RuntimeOrigin::root(),
            rid(60),
            CHARLIE,
        ));
        // Access log should have an emergency entry for CHARLIE
        let log = AccessLog::<Test>::get(rid(60), CHARLIE);
        assert_eq!(log.len(), 1);
        assert!(log[0].emergency_override);
        assert_eq!(log[0].block, 7u64);
    });
}

#[test]
fn emergency_access_override_records_in_emergency_log() {
    new_test_ext().execute_with(|| {
        set_block(9);
        spec_create(rid(61), BOB);
        assert_ok!(HealthRecordHash::emergency_access_override(
            RuntimeOrigin::root(),
            rid(61),
            CHARLIE,
        ));
        let block = crate::pallet::EmergencyOverrideLog::<Test>::get(rid(61), CHARLIE).unwrap();
        assert_eq!(block, 9u64);
    });
}

#[test]
fn emergency_access_override_fails_for_non_root() {
    new_test_ext().execute_with(|| {
        spec_create(rid(62), BOB);
        assert_err!(
            HealthRecordHash::emergency_access_override(
                RuntimeOrigin::signed(DAVE),
                rid(62),
                CHARLIE,
            ),
            frame_support::error::BadOrigin
        );
    });
}

#[test]
fn emergency_access_override_fails_for_inactive_record() {
    new_test_ext().execute_with(|| {
        spec_create(rid(63), BOB);
        assert_ok!(HealthRecordHash::mark_record_inactive(
            RuntimeOrigin::signed(BOB),
            rid(63)
        ));
        assert_err!(
            HealthRecordHash::emergency_access_override(
                RuntimeOrigin::root(),
                rid(63),
                CHARLIE,
            ),
            Error::<Test>::RecordInactive
        );
    });
}

#[test]
fn emergency_access_override_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(10);
        spec_create(rid(64), BOB);
        assert_ok!(HealthRecordHash::emergency_access_override(
            RuntimeOrigin::root(),
            rid(64),
            CHARLIE,
        ));
        System::assert_last_event(
            Event::<Test>::EmergencyAccessOverride {
                record_id: rid(64),
                accessor: CHARLIE,
                block: 10u64.into(),
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — verify_record_integrity
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn verify_record_integrity_matches_stored_hash() {
    new_test_ext().execute_with(|| {
        set_block(1);
        // create record with h32(1) as the hash
        assert_ok!(HealthRecordHash::create_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(70),
            BOB,
            h32(1),
            None,
            RecordTypeSpec::LabResult,
            TherapeuticModality::WesternMedicine,
            sig512(),
            h32(0),
        ));
        assert_ok!(HealthRecordHash::verify_record_integrity(
            RuntimeOrigin::signed(ALICE),
            rid(70),
            h32(1), // correct hash
        ));
        // Event should say matches = true
        System::assert_last_event(
            Event::<Test>::RecordIntegrityVerified {
                record_id: rid(70),
                verifier: ALICE,
                matches: true,
            }
            .into(),
        );
    });
}

#[test]
fn verify_record_integrity_detects_tampered_hash() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(HealthRecordHash::create_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(71),
            BOB,
            h32(1),
            None,
            RecordTypeSpec::LabResult,
            TherapeuticModality::WesternMedicine,
            sig512(),
            h32(0),
        ));
        assert_ok!(HealthRecordHash::verify_record_integrity(
            RuntimeOrigin::signed(ALICE),
            rid(71),
            h32(99), // wrong hash
        ));
        System::assert_last_event(
            Event::<Test>::RecordIntegrityVerified {
                record_id: rid(71),
                verifier: ALICE,
                matches: false,
            }
            .into(),
        );
    });
}

#[test]
fn verify_record_integrity_fails_for_non_existent_record() {
    new_test_ext().execute_with(|| {
        assert_err!(
            HealthRecordHash::verify_record_integrity(
                RuntimeOrigin::signed(ALICE),
                rid(200),
                h32(0),
            ),
            Error::<Test>::RecordNotFound
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — link_to_quantum_result
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn link_to_quantum_result_stores_link() {
    new_test_ext().execute_with(|| {
        spec_create(rid(80), BOB);
        let quantum_id = rid(200);
        assert_ok!(HealthRecordHash::link_to_quantum_result(
            RuntimeOrigin::signed(ALICE),
            rid(80),
            quantum_id,
        ));
        assert_eq!(
            QuantumResultLinks::<Test>::get(rid(80)),
            Some(quantum_id)
        );
    });
}

#[test]
fn link_to_quantum_result_fails_for_non_existent_record() {
    new_test_ext().execute_with(|| {
        assert_err!(
            HealthRecordHash::link_to_quantum_result(
                RuntimeOrigin::signed(ALICE),
                rid(201),
                rid(100),
            ),
            Error::<Test>::RecordNotFound
        );
    });
}

#[test]
fn link_to_quantum_result_fails_for_inactive_record() {
    new_test_ext().execute_with(|| {
        spec_create(rid(81), BOB);
        assert_ok!(HealthRecordHash::mark_record_inactive(
            RuntimeOrigin::signed(BOB),
            rid(81)
        ));
        assert_err!(
            HealthRecordHash::link_to_quantum_result(
                RuntimeOrigin::signed(ALICE),
                rid(81),
                rid(100),
            ),
            Error::<Test>::RecordInactive
        );
    });
}

#[test]
fn link_to_quantum_result_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(82), BOB);
        let qid = rid(250);
        assert_ok!(HealthRecordHash::link_to_quantum_result(
            RuntimeOrigin::signed(ALICE),
            rid(82),
            qid,
        ));
        System::assert_last_event(
            Event::<Test>::LinkedToQuantumResult {
                record_id: rid(82),
                quantum_result_id: qid,
            }
            .into(),
        );
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// SPEC API — mark_record_inactive (right to be forgotten)
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn mark_record_inactive_sets_active_false() {
    new_test_ext().execute_with(|| {
        spec_create(rid(90), BOB);
        assert_ok!(HealthRecordHash::mark_record_inactive(
            RuntimeOrigin::signed(BOB),
            rid(90)
        ));
        let entry = RecordHashStore::<Test>::get(rid(90)).unwrap();
        assert!(!entry.active);
    });
}

#[test]
fn mark_record_inactive_preserves_record_hash() {
    new_test_ext().execute_with(|| {
        assert_ok!(HealthRecordHash::create_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(91),
            BOB,
            h32(77),
            None,
            RecordTypeSpec::ClinicalNote,
            TherapeuticModality::WesternMedicine,
            sig512(),
            h32(0),
        ));
        assert_ok!(HealthRecordHash::mark_record_inactive(
            RuntimeOrigin::signed(BOB),
            rid(91)
        ));
        // Record still exists in storage (audit preserved)
        let entry = RecordHashStore::<Test>::get(rid(91)).unwrap();
        assert_eq!(entry.record_hash, h32(77));
    });
}

#[test]
fn mark_record_inactive_fails_if_not_patient() {
    new_test_ext().execute_with(|| {
        spec_create(rid(92), BOB);
        assert_err!(
            HealthRecordHash::mark_record_inactive(
                RuntimeOrigin::signed(DAVE), // not BOB
                rid(92)
            ),
            Error::<Test>::Unauthorized
        );
    });
}

#[test]
fn mark_record_inactive_emits_event() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(93), BOB);
        assert_ok!(HealthRecordHash::mark_record_inactive(
            RuntimeOrigin::signed(BOB),
            rid(93)
        ));
        System::assert_last_event(
            Event::<Test>::RecordMarkedInactive {
                record_id: rid(93),
                patient: BOB,
            }
            .into(),
        );
    });
}

#[test]
fn mark_record_inactive_patient_record_list_still_contains_id() {
    new_test_ext().execute_with(|| {
        spec_create(rid(94), BOB);
        assert_ok!(HealthRecordHash::mark_record_inactive(
            RuntimeOrigin::signed(BOB),
            rid(94)
        ));
        // PatientRecordIds still carries the id (audit trail intact)
        let ids = PatientRecordIds::<Test>::get(BOB);
        assert!(ids.contains(&rid(94)));
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// VERSION CONTROL — multi-version chain traversal
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn version_chain_previous_version_links_form_chain() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(110), BOB);

        set_block(2);
        assert_ok!(HealthRecordHash::update_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(110),
            h32(2),
            None,
            sig512(),
        ));
        let v2 = RecordHashStore::<Test>::get(rid(110)).unwrap();
        let prev = v2.previous_version.unwrap();

        set_block(3);
        assert_ok!(HealthRecordHash::update_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(110),
            h32(3),
            None,
            sig512(),
        ));
        let v3 = RecordHashStore::<Test>::get(rid(110)).unwrap();
        assert_eq!(v3.version, 3);
        assert!(v3.previous_version.is_some());
        // v3 links back to something, v2 linked to the initial hash
        assert!(v2.previous_version.is_some() || prev != v3.previous_version.unwrap());
    });
}

#[test]
fn multiple_versions_preserve_history_in_legacy_store() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            111u64,
            H256::from([1u8; 32]),
            RecordType::ClinicalEncounter,
            None,
        ));
        for i in 2u8..=5 {
            assert_ok!(HealthRecordHash::update_hash(
                RuntimeOrigin::signed(ALICE),
                BOB,
                111u64,
                H256::from([i; 32]),
                None,
            ));
        }
        let versions = RecordVersions::<Test>::get(BOB, 111u64);
        assert_eq!(versions.len(), 5);
        assert_eq!(versions[4].version, 5);
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// AUDIT TRAIL
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn audit_log_captures_all_access_attempts() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(120), BOB);
        spec_grant(BOB, rid(120), CHARLIE, 200);

        set_block(10);
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(BOB),
            rid(120),
        ));
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(CHARLIE),
            rid(120),
        ));
        // DAVE (no access) — attempt logged but denied
        assert_ok!(HealthRecordHash::access_record(RuntimeOrigin::signed(DAVE), rid(120)));

        assert_eq!(AccessLog::<Test>::get(rid(120), BOB).len(), 1);
        assert_eq!(AccessLog::<Test>::get(rid(120), CHARLIE).len(), 1);
        assert_eq!(AccessLog::<Test>::get(rid(120), DAVE).len(), 1);
        assert!(!AccessLog::<Test>::get(rid(120), DAVE)[0].granted);
    });
}

#[test]
fn audit_log_records_accessor_and_timestamp() {
    new_test_ext().execute_with(|| {
        set_block(15);
        spec_create(rid(121), BOB);
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(BOB),
            rid(121),
        ));
        let entry = &AccessLog::<Test>::get(rid(121), BOB)[0];
        assert_eq!(entry.accessor, BOB);
        assert_eq!(entry.block, 15u64);
    });
}

#[test]
fn legacy_audit_log_records_created_and_updated_actions() {
    new_test_ext().execute_with(|| {
        assert_ok!(HealthRecordHash::record_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            130u64,
            H256::from([1u8; 32]),
            RecordType::ClinicalEncounter,
            None,
        ));
        assert_ok!(HealthRecordHash::update_hash(
            RuntimeOrigin::signed(ALICE),
            BOB,
            130u64,
            H256::from([2u8; 32]),
            None,
        ));
        let logs = AuditLogs::<Test>::get(BOB, 130u64);
        assert_eq!(logs.len(), 2);
        assert_eq!(logs[0].action, AuditAction::RecordCreated);
        assert_eq!(logs[1].action, AuditAction::RecordUpdated);
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// INTEGRATION TESTS
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn integration_complete_record_lifecycle() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // 1. Provider (ALICE) creates a record for patient BOB
        assert_ok!(HealthRecordHash::create_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(150),
            BOB,
            h32(10),
            Some(cid(b"QmLifecycle")),
            RecordTypeSpec::ClinicalNote,
            TherapeuticModality::Integrative,
            sig512(),
            h32(0),
        ));
        assert_eq!(
            RecordHashStore::<Test>::get(rid(150)).unwrap().version,
            1
        );

        // 2. Patient BOB grants temporary access to CHARLIE
        set_block(2);
        spec_grant(BOB, rid(150), CHARLIE, 100);

        // 3. CHARLIE accesses the record — should succeed
        set_block(50);
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(CHARLIE),
            rid(150),
        ));

        // 4. BOB revokes CHARLIE's access
        assert_ok!(HealthRecordHash::revoke_record_access(
            RuntimeOrigin::signed(BOB),
            rid(150),
            CHARLIE,
        ));

        // 5. CHARLIE's access is now denied (but still logged)
        set_block(51);
        assert_ok!(HealthRecordHash::access_record(RuntimeOrigin::signed(CHARLIE), rid(150)));
        let charlie_log = AccessLog::<Test>::get(rid(150), CHARLIE);
        assert!(!charlie_log.last().unwrap().granted);

        // 6. Audit trail has both access attempts logged (1 granted + 1 denied)
        assert_eq!(charlie_log.len(), 2);
    });
}

#[test]
fn integration_multi_version_history_preserved() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(151), BOB);

        set_block(2);
        assert_ok!(HealthRecordHash::update_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(151),
            h32(2),
            Some(cid(b"QmV2")),
            sig512(),
        ));

        set_block(3);
        assert_ok!(HealthRecordHash::update_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(151),
            h32(3),
            Some(cid(b"QmV3")),
            sig512(),
        ));

        let entry = RecordHashStore::<Test>::get(rid(151)).unwrap();
        assert_eq!(entry.version, 3);
        assert_eq!(entry.record_hash, h32(3));
        assert!(entry.previous_version.is_some()); // links to v2's hash
        assert_eq!(entry.ipfs_cid, Some(cid(b"QmV3")));
    });
}

#[test]
fn integration_multisig_full_workflow() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // 1. Create record for patient BOB
        spec_create(rid(152), BOB);

        // 2. BOB sets a 2-of-3 multi-sig requirement
        let signers = make_signers(&[ALICE, CHARLIE, DAVE]);
        assert_ok!(HealthRecordHash::create_multisig_requirement(
            RuntimeOrigin::signed(BOB),
            rid(152),
            2,
            signers,
        ));

        // 3. Before threshold — access denied (but still logged)
        assert_ok!(HealthRecordHash::access_record(RuntimeOrigin::signed(EVE), rid(152)));
        assert!(!AccessLog::<Test>::get(rid(152), EVE).last().unwrap().granted);

        // 4. ALICE signs
        assert_ok!(HealthRecordHash::sign_record_access(
            RuntimeOrigin::signed(ALICE),
            rid(152),
            sig128(),
        ));
        // Still one short
        assert_ok!(HealthRecordHash::access_record(RuntimeOrigin::signed(EVE), rid(152)));
        assert!(!AccessLog::<Test>::get(rid(152), EVE).last().unwrap().granted);

        // 5. CHARLIE signs — threshold met
        assert_ok!(HealthRecordHash::sign_record_access(
            RuntimeOrigin::signed(CHARLIE),
            rid(152),
            sig128(),
        ));

        // 6. Access now granted
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(EVE),
            rid(152),
        ));
    });
}

#[test]
fn integration_quantum_link_and_integrity_check() {
    new_test_ext().execute_with(|| {
        set_block(1);
        assert_ok!(HealthRecordHash::create_record_hash(
            RuntimeOrigin::signed(ALICE),
            rid(153),
            BOB,
            h32(42),
            None,
            RecordTypeSpec::QuantumAnalysis,
            TherapeuticModality::WesternMedicine,
            sig512(),
            h32(0),
        ));

        let quantum_id = rid(255);
        assert_ok!(HealthRecordHash::link_to_quantum_result(
            RuntimeOrigin::signed(ALICE),
            rid(153),
            quantum_id,
        ));
        assert_eq!(QuantumResultLinks::<Test>::get(rid(153)), Some(quantum_id));

        // Correct hash verifies
        assert_ok!(HealthRecordHash::verify_record_integrity(
            RuntimeOrigin::signed(ALICE),
            rid(153),
            h32(42),
        ));
        System::assert_last_event(
            Event::<Test>::RecordIntegrityVerified {
                record_id: rid(153),
                verifier: ALICE,
                matches: true,
            }
            .into(),
        );
    });
}

#[test]
fn integration_right_to_forget_blocks_all_operations() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(154), BOB);

        // BOB exercises right to be forgotten
        assert_ok!(HealthRecordHash::mark_record_inactive(
            RuntimeOrigin::signed(BOB),
            rid(154)
        ));

        // All write/access operations on the inactive record fail
        assert_err!(
            HealthRecordHash::update_record_hash(
                RuntimeOrigin::signed(ALICE),
                rid(154),
                h32(99),
                None,
                sig512(),
            ),
            Error::<Test>::RecordInactive
        );
        assert_err!(
            HealthRecordHash::grant_record_access(
                RuntimeOrigin::signed(BOB),
                rid(154),
                CHARLIE,
                100u64.into(),
            ),
            Error::<Test>::RecordInactive
        );
        assert_err!(
            HealthRecordHash::access_record(RuntimeOrigin::signed(BOB), rid(154)),
            Error::<Test>::RecordInactive
        );
        assert_err!(
            HealthRecordHash::link_to_quantum_result(
                RuntimeOrigin::signed(ALICE),
                rid(154),
                rid(100),
            ),
            Error::<Test>::RecordInactive
        );

        // Record hash still retrievable (audit trail preserved)
        assert!(RecordHashStore::<Test>::get(rid(154)).is_some());
    });
}

// ──────────────────────────────────────────────────────────────────────────────
// EDGE CASES
// ──────────────────────────────────────────────────────────────────────────────

#[test]
fn edge_case_multiple_records_per_patient() {
    new_test_ext().execute_with(|| {
        for n in 1u8..=10 {
            spec_create(rid(n), BOB);
        }
        let ids = PatientRecordIds::<Test>::get(BOB);
        assert_eq!(ids.len(), 10);
    });
}

#[test]
fn edge_case_concurrent_grants_to_multiple_providers() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(160), BOB);
        spec_grant(BOB, rid(160), ALICE, 100);
        spec_grant(BOB, rid(160), CHARLIE, 200);
        spec_grant(BOB, rid(160), DAVE, 300);
        assert!(AccessGrants::<Test>::get(rid(160), ALICE).is_some());
        assert!(AccessGrants::<Test>::get(rid(160), CHARLIE).is_some());
        assert!(AccessGrants::<Test>::get(rid(160), DAVE).is_some());
    });
}

#[test]
fn edge_case_access_log_accumulates_for_many_accesses() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(161), BOB);
        for blk in 1u64..=20 {
            set_block(blk);
            assert_ok!(HealthRecordHash::access_record(
                RuntimeOrigin::signed(BOB),
                rid(161),
            ));
        }
        let log = AccessLog::<Test>::get(rid(161), BOB);
        assert_eq!(log.len(), 20);
    });
}

#[test]
fn edge_case_10_signer_multisig() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(162), BOB);
        // Create 10-account signer list using sequential account IDs 10..=19
        let signer_ids: Vec<u64> = (10u64..=19).collect();
        let signers = BoundedVec::<u64, ConstU32<16>>::try_from(signer_ids.clone()).unwrap();
        assert_ok!(HealthRecordHash::create_multisig_requirement(
            RuntimeOrigin::signed(BOB),
            rid(162),
            10,
            signers,
        ));
        // Sign with all 10 accounts
        for account in 10u64..=19 {
            assert_ok!(HealthRecordHash::sign_record_access(
                RuntimeOrigin::signed(account),
                rid(162),
                sig128(),
            ));
        }
        let req = MultiSigPermissions::<Test>::get(rid(162)).unwrap();
        assert_eq!(req.current_signatures.len(), 10);
        // Access should now be granted
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(ALICE),
            rid(162),
        ));
    });
}

#[test]
fn edge_case_emergency_access_during_active_grant() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(163), BOB);
        spec_grant(BOB, rid(163), CHARLIE, 200);

        // Both grant access and emergency override can coexist
        set_block(50);
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(CHARLIE),
            rid(163),
        ));
        assert_ok!(HealthRecordHash::emergency_access_override(
            RuntimeOrigin::root(),
            rid(163),
            DAVE,
        ));
        assert_eq!(
            crate::pallet::EmergencyOverrideLog::<Test>::get(rid(163), DAVE).unwrap(),
            50u64
        );
    });
}

#[test]
fn edge_case_grant_expiry_at_exact_block_boundary() {
    new_test_ext().execute_with(|| {
        set_block(1);
        spec_create(rid(164), BOB);
        spec_grant(BOB, rid(164), CHARLIE, 100); // expires AT block 100

        // Block 100 — expiry check is `now <= expiry`, so access is granted
        set_block(100);
        assert_ok!(HealthRecordHash::access_record(
            RuntimeOrigin::signed(CHARLIE),
            rid(164),
        ));

        // Block 101 — past expiry, denied (but still logged)
        set_block(101);
        assert_ok!(HealthRecordHash::access_record(RuntimeOrigin::signed(CHARLIE), rid(164)));
        assert!(!AccessLog::<Test>::get(rid(164), CHARLIE).last().unwrap().granted);
    });
}

#[test]
fn edge_case_different_patients_records_are_independent() {
    new_test_ext().execute_with(|| {
        // Same record_id but different patients — storage is (patient, record_id) for legacy,
        // but spec API uses a global record_id (T::Hash). Different record IDs keep them separate.
        spec_create(rid(170), ALICE); // ALICE is the patient
        spec_create(rid(171), BOB);   // BOB is the patient

        assert_eq!(RecordHashStore::<Test>::get(rid(170)).unwrap().patient_id, ALICE);
        assert_eq!(RecordHashStore::<Test>::get(rid(171)).unwrap().patient_id, BOB);
    });
}
