//! Tests for account management pallet

use crate::{mock::*, *};
use frame_support::assert_ok;

#[test]
fn register_account_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1),
            AccountTier::Patient
        ));
    });
}

#[test]
fn submit_credential_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1),
            AccountTier::Provider
        ));
        assert_ok!(AccountManagement::submit_credential(
            RuntimeOrigin::signed(1),
            1,
            CredentialType::MedicalLicense,
            b"credential_data".to_vec()
        ));
    });
}

#[test]
fn make_deposit_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::make_deposit(
            RuntimeOrigin::signed(1),
            1000
        ));
    });
}

