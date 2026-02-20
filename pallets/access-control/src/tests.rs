//! Tests for access control pallet

use crate::{mock::*, *};
use frame_support::assert_ok;
use sp_core::H256;

#[test]
fn grant_patient_authorization_works() {
    new_test_ext().execute_with(|| {
        let resource_id = H256::from_low_u64_be(1);
        assert_ok!(AccessControl::grant_patient_authorization(
            RuntimeOrigin::signed(1),
            resource_id,
            PermissionType::Read
        ));
    });
}

#[test]
fn grant_institutional_permission_works() {
    new_test_ext().execute_with(|| {
        let resource_id = H256::from_low_u64_be(1);
        assert_ok!(AccessControl::grant_institutional_permission(
            RuntimeOrigin::signed(1),
            2,
            resource_id,
            AccessLevel::Read,
            None
        ));
    });
}

#[test]
fn grant_emergency_access_works() {
    new_test_ext().execute_with(|| {
        let resource_id = H256::from_low_u64_be(1);
        assert_ok!(AccessControl::grant_emergency_access(
            RuntimeOrigin::signed(1),
            2,
            resource_id,
            EmergencyAccessReason::MedicalEmergency,
            100
        ));
    });
}

