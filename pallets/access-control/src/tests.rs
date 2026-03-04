//! Comprehensive tests for the ABENA Access Control pallet.

use crate::{mock::*, *};
use frame_support::{assert_err, assert_ok};
use sp_core::H256;

fn res(n: u64) -> H256 { H256::from_low_u64_be(n) }

// ── grant_patient_authorization ─────────────────────────────────────────────

#[test]
fn grant_patient_authorization_stores_entry() {
    new_test_ext().execute_with(|| {
        let rid = res(1);
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(1), rid, PermissionType::Read
        ));
        assert!(PatientAuthorizations::<Test>::contains_key(1u64, rid));
    });
}

#[test]
fn grant_patient_authorization_emits_event() {
    new_test_ext().execute_with(|| {
        let rid = res(42);
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(1), rid, PermissionType::Full
        ));
        System::assert_has_event(RuntimeEvent::AccessControl(
            Event::PatientAuthorizationGranted {
                patient: 1,
                resource_id: rid,
                permission_type: PermissionType::Full,
            }
        ));
    });
}

#[test]
fn grant_patient_authorization_creates_audit_log() {
    new_test_ext().execute_with(|| {
        let rid = res(1);
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(1), rid, PermissionType::Write
        ));
        assert_eq!(NextAuditLogId::<Test>::get(), 1);
        assert!(AuditLogs::<Test>::contains_key(0u64));
    });
}

#[test]
fn grant_patient_authorization_all_permission_types() {
    new_test_ext().execute_with(|| {
        for (i, perm) in [PermissionType::Read, PermissionType::Write, PermissionType::Full]
            .into_iter()
            .enumerate()
        {
            let rid = res(i as u64 + 1);
            assert_ok!(AccessControl::grant_patient_authorization(
                RuntimeOrigin::signed(1), rid, perm
            ));
        }
        assert_eq!(NextAuditLogId::<Test>::get(), 3);
    });
}

// ── revoke_patient_authorization ────────────────────────────────────────────

#[test]
fn revoke_patient_authorization_removes_entry() {
    new_test_ext().execute_with(|| {
        let rid = res(1);
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(1), rid, PermissionType::Read
        ));
        assert_ok!(AccessControl::revoke_patient_authorization(
            RuntimeOrigin::signed(1), rid
        ));
        assert!(!PatientAuthorizations::<Test>::contains_key(1u64, rid));
    });
}

#[test]
fn revoke_patient_authorization_fails_if_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AccessControl::revoke_patient_authorization(RuntimeOrigin::signed(1), res(99)),
            Error::<Test>::AuthorizationNotFound
        );
    });
}

#[test]
fn revoke_patient_authorization_emits_event() {
    new_test_ext().execute_with(|| {
        let rid = res(5);
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(1), rid, PermissionType::Read
        ));
        assert_ok!(AccessControl::revoke_patient_authorization(
            RuntimeOrigin::signed(1), rid
        ));
        System::assert_has_event(RuntimeEvent::AccessControl(
            Event::PatientAuthorizationRevoked { patient: 1, resource_id: rid }
        ));
    });
}

// ── grant_institutional_permission ──────────────────────────────────────────

#[test]
fn grant_institutional_permission_stores_entry() {
    new_test_ext().execute_with(|| {
        let rid = res(10);
        assert_ok!(AccessControl::grant_institutional_permission(
            RuntimeOrigin::signed(1), 2, rid, AccessLevel::Read, None
        ));
        assert!(InstitutionalPermissions::<Test>::contains_key(2u64, rid));
    });
}

#[test]
fn grant_institutional_permission_with_expiry() {
    new_test_ext().execute_with(|| {
        let rid = res(11);
        assert_ok!(AccessControl::grant_institutional_permission(
            RuntimeOrigin::signed(1), 2, rid, AccessLevel::Full, Some(1000)
        ));
        let perm = InstitutionalPermissions::<Test>::get(2u64, rid).unwrap();
        assert_eq!(perm.expires_at, Some(1000));
    });
}

#[test]
fn grant_institutional_permission_emits_event() {
    new_test_ext().execute_with(|| {
        let rid = res(12);
        assert_ok!(AccessControl::grant_institutional_permission(
            RuntimeOrigin::signed(1), 2, rid, AccessLevel::Write, None
        ));
        System::assert_has_event(RuntimeEvent::AccessControl(
            Event::InstitutionalPermissionGranted {
                institution: 2,
                resource_id: rid,
                access_level: AccessLevel::Write,
            }
        ));
    });
}

#[test]
fn grant_institutional_permission_stores_granter() {
    new_test_ext().execute_with(|| {
        let rid = res(13);
        assert_ok!(AccessControl::grant_institutional_permission(
            RuntimeOrigin::signed(1), 2, rid, AccessLevel::Read, None
        ));
        let perm = InstitutionalPermissions::<Test>::get(2u64, rid).unwrap();
        assert_eq!(perm.granted_by, 1u64);
    });
}

// ── revoke_institutional_permission ─────────────────────────────────────────

#[test]
fn revoke_institutional_permission_removes_entry() {
    new_test_ext().execute_with(|| {
        let rid = res(20);
        assert_ok!(AccessControl::grant_institutional_permission(
            RuntimeOrigin::signed(1), 2, rid, AccessLevel::Read, None
        ));
        assert_ok!(AccessControl::revoke_institutional_permission(
            RuntimeOrigin::signed(1), 2, rid
        ));
        assert!(!InstitutionalPermissions::<Test>::contains_key(2u64, rid));
    });
}

#[test]
fn revoke_institutional_permission_fails_if_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AccessControl::revoke_institutional_permission(
                RuntimeOrigin::signed(1), 2, res(99)
            ),
            Error::<Test>::PermissionNotFound
        );
    });
}

#[test]
fn revoke_institutional_permission_emits_event() {
    new_test_ext().execute_with(|| {
        let rid = res(21);
        assert_ok!(AccessControl::grant_institutional_permission(
            RuntimeOrigin::signed(1), 2, rid, AccessLevel::Read, None
        ));
        assert_ok!(AccessControl::revoke_institutional_permission(
            RuntimeOrigin::signed(1), 2, rid
        ));
        System::assert_has_event(RuntimeEvent::AccessControl(
            Event::InstitutionalPermissionRevoked { institution: 2, resource_id: rid }
        ));
    });
}

// ── grant_emergency_access ──────────────────────────────────────────────────

#[test]
fn grant_emergency_access_stores_entry() {
    new_test_ext().execute_with(|| {
        let rid = res(30);
        assert_ok!(AccessControl::grant_emergency_access(
            RuntimeOrigin::signed(1), 2, rid, EmergencyAccessReason::MedicalEmergency, 100
        ));
        assert!(EmergencyAccessRecords::<Test>::contains_key(2u64, rid));
    });
}

#[test]
fn grant_emergency_access_sets_expiry_correctly() {
    new_test_ext().execute_with(|| {
        System::set_block_number(50);
        let rid = res(31);
        assert_ok!(AccessControl::grant_emergency_access(
            RuntimeOrigin::signed(1), 2, rid, EmergencyAccessReason::LifeThreatening, 200
        ));
        let rec = EmergencyAccessRecords::<Test>::get(2u64, rid).unwrap();
        assert_eq!(rec.expires_at, 50 + 200);
        assert_eq!(rec.granted_at, 50);
    });
}

#[test]
fn grant_emergency_access_life_threatening() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccessControl::grant_emergency_access(
            RuntimeOrigin::signed(1), 2, res(32),
            EmergencyAccessReason::LifeThreatening, 50
        ));
    });
}

#[test]
fn grant_emergency_access_legal_requirement() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccessControl::grant_emergency_access(
            RuntimeOrigin::signed(1), 2, res(33),
            EmergencyAccessReason::LegalRequirement, 50
        ));
    });
}

#[test]
fn grant_emergency_access_emits_event() {
    new_test_ext().execute_with(|| {
        let rid = res(34);
        assert_ok!(AccessControl::grant_emergency_access(
            RuntimeOrigin::signed(1), 2, rid, EmergencyAccessReason::MedicalEmergency, 100
        ));
        System::assert_has_event(RuntimeEvent::AccessControl(
            Event::EmergencyAccessGranted {
                requester: 2,
                resource_id: rid,
                reason: EmergencyAccessReason::MedicalEmergency,
                authorized_by: 1,
            }
        ));
    });
}

// ── revoke_emergency_access ─────────────────────────────────────────────────

#[test]
fn revoke_emergency_access_removes_entry() {
    new_test_ext().execute_with(|| {
        let rid = res(40);
        assert_ok!(AccessControl::grant_emergency_access(
            RuntimeOrigin::signed(1), 2, rid, EmergencyAccessReason::MedicalEmergency, 100
        ));
        assert_ok!(AccessControl::revoke_emergency_access(
            RuntimeOrigin::signed(1), 2, rid
        ));
        assert!(!EmergencyAccessRecords::<Test>::contains_key(2u64, rid));
    });
}

#[test]
fn revoke_emergency_access_fails_if_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AccessControl::revoke_emergency_access(RuntimeOrigin::signed(1), 2, res(99)),
            Error::<Test>::AuthorizationNotFound
        );
    });
}

#[test]
fn revoke_emergency_access_emits_event() {
    new_test_ext().execute_with(|| {
        let rid = res(41);
        assert_ok!(AccessControl::grant_emergency_access(
            RuntimeOrigin::signed(1), 2, rid, EmergencyAccessReason::MedicalEmergency, 100
        ));
        assert_ok!(AccessControl::revoke_emergency_access(RuntimeOrigin::signed(1), 2, rid));
        System::assert_has_event(RuntimeEvent::AccessControl(
            Event::EmergencyAccessRevoked { requester: 2, resource_id: rid }
        ));
    });
}

// ── check_read_access ────────────────────────────────────────────────────────

#[test]
fn check_read_access_passes_for_patient_authorization() {
    new_test_ext().execute_with(|| {
        let rid = res(50);
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(1), rid, PermissionType::Read
        ));
        assert_ok!(AccessControl::check_read_access(RuntimeOrigin::signed(1), rid));
    });
}

#[test]
fn check_read_access_passes_for_institutional_read() {
    new_test_ext().execute_with(|| {
        let rid = res(51);
        assert_ok!(AccessControl::grant_institutional_permission(
            RuntimeOrigin::signed(1), 2, rid, AccessLevel::Read, None
        ));
        assert_ok!(AccessControl::check_read_access(RuntimeOrigin::signed(2), rid));
    });
}

#[test]
fn check_read_access_passes_for_institutional_write() {
    new_test_ext().execute_with(|| {
        let rid = res(52);
        assert_ok!(AccessControl::grant_institutional_permission(
            RuntimeOrigin::signed(1), 2, rid, AccessLevel::Write, None
        ));
        assert_ok!(AccessControl::check_read_access(RuntimeOrigin::signed(2), rid));
    });
}

#[test]
fn check_read_access_fails_without_any_permission() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AccessControl::check_read_access(RuntimeOrigin::signed(99), res(60)),
            Error::<Test>::Unauthorized
        );
    });
}

#[test]
fn check_read_access_fails_for_expired_institutional_permission() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        let rid = res(53);
        assert_ok!(AccessControl::grant_institutional_permission(
            RuntimeOrigin::signed(1), 2, rid, AccessLevel::Read, Some(5)
        ));
        System::set_block_number(10);
        assert_err!(
            AccessControl::check_read_access(RuntimeOrigin::signed(2), rid),
            Error::<Test>::Unauthorized
        );
    });
}

#[test]
fn check_read_access_passes_for_valid_emergency_access() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        let rid = res(54);
        assert_ok!(AccessControl::grant_emergency_access(
            RuntimeOrigin::signed(1), 2, rid, EmergencyAccessReason::LifeThreatening, 100
        ));
        assert_ok!(AccessControl::check_read_access(RuntimeOrigin::signed(2), rid));
    });
}

#[test]
fn check_read_access_fails_for_expired_emergency_access() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        let rid = res(55);
        assert_ok!(AccessControl::grant_emergency_access(
            RuntimeOrigin::signed(1), 2, rid, EmergencyAccessReason::MedicalEmergency, 5
        ));
        System::set_block_number(100);
        assert_err!(
            AccessControl::check_read_access(RuntimeOrigin::signed(2), rid),
            Error::<Test>::Unauthorized
        );
    });
}

// ── audit log ───────────────────────────────────────────────────────────────

#[test]
fn audit_log_id_increments_per_action() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(1), res(1), PermissionType::Read
        ));
        assert_ok!(AccessControl::grant_institutional_permission(
            RuntimeOrigin::signed(1), 2, res(2), AccessLevel::Read, None
        ));
        assert_ok!(AccessControl::grant_emergency_access(
            RuntimeOrigin::signed(1), 2, res(3), EmergencyAccessReason::MedicalEmergency, 100
        ));
        assert_eq!(NextAuditLogId::<Test>::get(), 3);
    });
}

#[test]
fn audit_log_records_correct_account() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(42), res(1), PermissionType::Read
        ));
        let log = AuditLogs::<Test>::get(0u64).unwrap();
        assert_eq!(log.account, 42u64);
    });
}

// ── integration ─────────────────────────────────────────────────────────────

#[test]
fn integration_grant_revoke_all_types() {
    new_test_ext().execute_with(|| {
        let rid = res(100);
        // Patient auth lifecycle
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(1), rid, PermissionType::Full
        ));
        assert_ok!(AccessControl::check_read_access(RuntimeOrigin::signed(1), rid));
        assert_ok!(AccessControl::revoke_patient_authorization(RuntimeOrigin::signed(1), rid));
        assert_err!(
            AccessControl::check_read_access(RuntimeOrigin::signed(1), rid),
            Error::<Test>::Unauthorized
        );

        // Institutional permission lifecycle
        assert_ok!(AccessControl::grant_institutional_permission(
            RuntimeOrigin::signed(1), 2, rid, AccessLevel::Full, None
        ));
        assert_ok!(AccessControl::check_read_access(RuntimeOrigin::signed(2), rid));
        assert_ok!(AccessControl::revoke_institutional_permission(RuntimeOrigin::signed(1), 2, rid));

        // Emergency access lifecycle
        System::set_block_number(1);
        assert_ok!(AccessControl::grant_emergency_access(
            RuntimeOrigin::signed(1), 3, rid, EmergencyAccessReason::LifeThreatening, 50
        ));
        assert_ok!(AccessControl::check_read_access(RuntimeOrigin::signed(3), rid));
        assert_ok!(AccessControl::revoke_emergency_access(RuntimeOrigin::signed(1), 3, rid));
        assert_err!(
            AccessControl::check_read_access(RuntimeOrigin::signed(3), rid),
            Error::<Test>::Unauthorized
        );
    });
}

#[test]
fn multiple_resources_per_patient_are_independent() {
    new_test_ext().execute_with(|| {
        let rid1 = res(200);
        let rid2 = res(201);
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(1), rid1, PermissionType::Read
        ));
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(1), rid2, PermissionType::Write
        ));
        assert_ok!(AccessControl::revoke_patient_authorization(RuntimeOrigin::signed(1), rid1));
        // rid2 still accessible
        assert_ok!(AccessControl::check_read_access(RuntimeOrigin::signed(1), rid2));
    });
}

#[test]
fn different_patients_have_independent_authorizations() {
    new_test_ext().execute_with(|| {
        let rid = res(300);
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(1), rid, PermissionType::Read
        ));
        // Patient 2 has no auth for the same resource
        assert_err!(
            AccessControl::check_read_access(RuntimeOrigin::signed(2), rid),
            Error::<Test>::Unauthorized
        );
    });
}
