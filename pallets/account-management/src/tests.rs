//! Comprehensive tests for the ABENA Account Management pallet.

use crate::{mock::*, *};
use frame_support::{assert_err, assert_ok};

// ── register_account ─────────────────────────────────────────────────────────

#[test]
fn register_account_patient_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Patient
        ));
        let info = AccountInfos::<Test>::get(1u64).unwrap();
        assert_eq!(info.tier, AccountTier::Patient);
        assert!(!info.verified);
    });
}

#[test]
fn register_account_provider_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Provider
        ));
        assert_eq!(AccountInfos::<Test>::get(1u64).unwrap().tier, AccountTier::Provider);
    });
}

#[test]
fn register_account_institution_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Institution
        ));
        assert_eq!(AccountInfos::<Test>::get(1u64).unwrap().tier, AccountTier::Institution);
    });
}

#[test]
fn register_account_fails_when_already_registered() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Patient
        ));
        assert_err!(
            AccountManagement::register_account(RuntimeOrigin::signed(1), AccountTier::Provider),
            Error::<Test>::AccountAlreadyRegistered
        );
    });
}

#[test]
fn register_account_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Patient
        ));
        System::assert_has_event(RuntimeEvent::AccountManagement(
            Event::AccountRegistered { account: 1, tier: AccountTier::Patient }
        ));
    });
}

#[test]
fn register_account_stores_block_number() {
    new_test_ext().execute_with(|| {
        System::set_block_number(42);
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Patient
        ));
        assert_eq!(AccountInfos::<Test>::get(1u64).unwrap().registered_at, 42);
    });
}

// ── update_account_tier ──────────────────────────────────────────────────────

#[test]
fn update_account_tier_requires_root() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Patient
        ));
        assert_ok!(AccountManagement::update_account_tier(
            RuntimeOrigin::root(), 1, AccountTier::Provider
        ));
        assert_eq!(AccountInfos::<Test>::get(1u64).unwrap().tier, AccountTier::Provider);
    });
}

#[test]
fn update_account_tier_fails_for_non_root() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Patient
        ));
        assert!(AccountManagement::update_account_tier(
            RuntimeOrigin::signed(2), 1, AccountTier::Provider
        ).is_err());
    });
}

#[test]
fn update_account_tier_fails_if_account_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AccountManagement::update_account_tier(RuntimeOrigin::root(), 99, AccountTier::Provider),
            Error::<Test>::AccountNotFound
        );
    });
}

#[test]
fn update_account_tier_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Patient
        ));
        assert_ok!(AccountManagement::update_account_tier(
            RuntimeOrigin::root(), 1, AccountTier::Institution
        ));
        System::assert_has_event(RuntimeEvent::AccountManagement(
            Event::AccountTierUpdated {
                account: 1,
                old_tier: AccountTier::Patient,
                new_tier: AccountTier::Institution,
            }
        ));
    });
}

// ── submit_credential ────────────────────────────────────────────────────────

#[test]
fn submit_credential_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Provider
        ));
        assert_ok!(AccountManagement::submit_credential(
            RuntimeOrigin::signed(1),
            1u64,
            CredentialType::MedicalLicense,
            b"license_data_here".to_vec(),
        ));
        assert!(CredentialVerifications::<Test>::contains_key(1u64, 1u64));
    });
}

#[test]
fn submit_credential_fails_if_account_not_registered() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AccountManagement::submit_credential(
                RuntimeOrigin::signed(99),
                1u64,
                CredentialType::MedicalLicense,
                b"data".to_vec(),
            ),
            Error::<Test>::AccountNotFound
        );
    });
}

#[test]
fn submit_credential_sets_pending_status() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Provider
        ));
        assert_ok!(AccountManagement::submit_credential(
            RuntimeOrigin::signed(1), 1u64, CredentialType::ProfessionalCertification, b"data".to_vec()
        ));
        let cred = CredentialVerifications::<Test>::get(1u64, 1u64).unwrap();
        assert_eq!(cred.status, VerificationStatus::Pending);
    });
}

#[test]
fn submit_credential_all_types() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Institution
        ));
        for (i, ctype) in [
            CredentialType::MedicalLicense,
            CredentialType::ProfessionalCertification,
            CredentialType::InstitutionAccreditation,
            CredentialType::IdentityDocument,
        ].into_iter().enumerate() {
            assert_ok!(AccountManagement::submit_credential(
                RuntimeOrigin::signed(1), i as u64, ctype, b"data".to_vec()
            ));
        }
    });
}

#[test]
fn submit_credential_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Provider
        ));
        assert_ok!(AccountManagement::submit_credential(
            RuntimeOrigin::signed(1), 1u64, CredentialType::MedicalLicense, b"data".to_vec()
        ));
        System::assert_has_event(RuntimeEvent::AccountManagement(
            Event::CredentialSubmitted {
                account: 1,
                credential_id: 1,
                credential_type: CredentialType::MedicalLicense,
            }
        ));
    });
}

// ── verify_credential ────────────────────────────────────────────────────────

#[test]
fn verify_credential_updates_status() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Provider
        ));
        assert_ok!(AccountManagement::submit_credential(
            RuntimeOrigin::signed(1), 1u64, CredentialType::MedicalLicense, b"data".to_vec()
        ));
        assert_ok!(AccountManagement::verify_credential(RuntimeOrigin::signed(2), 1, 1));
        let cred = CredentialVerifications::<Test>::get(1u64, 1u64).unwrap();
        assert_eq!(cred.status, VerificationStatus::Verified);
    });
}

#[test]
fn verify_credential_marks_account_as_verified() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Provider
        ));
        assert_ok!(AccountManagement::submit_credential(
            RuntimeOrigin::signed(1), 1u64, CredentialType::MedicalLicense, b"data".to_vec()
        ));
        assert_ok!(AccountManagement::verify_credential(RuntimeOrigin::signed(2), 1, 1));
        assert!(AccountInfos::<Test>::get(1u64).unwrap().verified);
    });
}

#[test]
fn verify_credential_fails_if_not_found() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AccountManagement::verify_credential(RuntimeOrigin::signed(2), 1, 99),
            Error::<Test>::CredentialNotFound
        );
    });
}

#[test]
fn verify_credential_fails_if_already_verified() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Provider
        ));
        assert_ok!(AccountManagement::submit_credential(
            RuntimeOrigin::signed(1), 1u64, CredentialType::MedicalLicense, b"data".to_vec()
        ));
        assert_ok!(AccountManagement::verify_credential(RuntimeOrigin::signed(2), 1, 1));
        assert_err!(
            AccountManagement::verify_credential(RuntimeOrigin::signed(2), 1, 1),
            Error::<Test>::CredentialAlreadyVerified
        );
    });
}

#[test]
fn verify_credential_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Provider
        ));
        assert_ok!(AccountManagement::submit_credential(
            RuntimeOrigin::signed(1), 1u64, CredentialType::MedicalLicense, b"data".to_vec()
        ));
        assert_ok!(AccountManagement::verify_credential(RuntimeOrigin::signed(2), 1, 1));
        System::assert_has_event(RuntimeEvent::AccountManagement(
            Event::CredentialVerified { account: 1, credential_id: 1, verified_by: 2 }
        ));
    });
}

// ── reject_credential ────────────────────────────────────────────────────────

#[test]
fn reject_credential_updates_status() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Provider
        ));
        assert_ok!(AccountManagement::submit_credential(
            RuntimeOrigin::signed(1), 1u64, CredentialType::MedicalLicense, b"data".to_vec()
        ));
        assert_ok!(AccountManagement::reject_credential(
            RuntimeOrigin::signed(2), 1, 1, b"Expired license".to_vec()
        ));
        let cred = CredentialVerifications::<Test>::get(1u64, 1u64).unwrap();
        assert_eq!(cred.status, VerificationStatus::Rejected);
    });
}

#[test]
fn reject_credential_fails_if_already_verified() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Provider
        ));
        assert_ok!(AccountManagement::submit_credential(
            RuntimeOrigin::signed(1), 1u64, CredentialType::MedicalLicense, b"data".to_vec()
        ));
        assert_ok!(AccountManagement::verify_credential(RuntimeOrigin::signed(2), 1, 1));
        assert_err!(
            AccountManagement::reject_credential(
                RuntimeOrigin::signed(2), 1, 1, b"too late".to_vec()
            ),
            Error::<Test>::CredentialAlreadyVerified
        );
    });
}

#[test]
fn reject_credential_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Provider
        ));
        assert_ok!(AccountManagement::submit_credential(
            RuntimeOrigin::signed(1), 1u64, CredentialType::MedicalLicense, b"data".to_vec()
        ));
        assert_ok!(AccountManagement::reject_credential(
            RuntimeOrigin::signed(2), 1, 1, b"Reason".to_vec()
        ));
        System::assert_has_event(RuntimeEvent::AccountManagement(
            Event::CredentialRejected {
                account: 1,
                credential_id: 1,
                reason: b"Reason".to_vec(),
            }
        ));
    });
}

// ── make_deposit ─────────────────────────────────────────────────────────────

#[test]
fn make_deposit_reserves_funds() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::make_deposit(RuntimeOrigin::signed(1), 1_000));
        let info = DepositInfos::<Test>::get(1u64).unwrap();
        assert_eq!(info.total_deposit, 1_000);
    });
}

#[test]
fn make_deposit_fails_for_insufficient_balance() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AccountManagement::make_deposit(RuntimeOrigin::signed(1), 999_999_999),
            Error::<Test>::InsufficientDeposit
        );
    });
}

#[test]
fn make_deposit_accumulates_over_multiple_calls() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::make_deposit(RuntimeOrigin::signed(1), 1_000));
        assert_ok!(AccountManagement::make_deposit(RuntimeOrigin::signed(1), 2_000));
        assert_eq!(DepositInfos::<Test>::get(1u64).unwrap().total_deposit, 3_000);
    });
}

#[test]
fn make_deposit_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::make_deposit(RuntimeOrigin::signed(1), 5_000));
        System::assert_has_event(RuntimeEvent::AccountManagement(
            Event::DepositMade { account: 1, amount: 5_000, total_deposit: 5_000 }
        ));
    });
}

// ── withdraw_deposit ─────────────────────────────────────────────────────────

#[test]
fn withdraw_deposit_reduces_total() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::make_deposit(RuntimeOrigin::signed(1), 10_000));
        assert_ok!(AccountManagement::withdraw_deposit(RuntimeOrigin::signed(1), 4_000));
        assert_eq!(DepositInfos::<Test>::get(1u64).unwrap().total_deposit, 6_000);
    });
}

#[test]
fn withdraw_deposit_clears_record_when_zero() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::make_deposit(RuntimeOrigin::signed(1), 5_000));
        assert_ok!(AccountManagement::withdraw_deposit(RuntimeOrigin::signed(1), 5_000));
        assert!(DepositInfos::<Test>::get(1u64).is_none());
    });
}

#[test]
fn withdraw_deposit_fails_if_no_deposit() {
    new_test_ext().execute_with(|| {
        assert_err!(
            AccountManagement::withdraw_deposit(RuntimeOrigin::signed(1), 1_000),
            Error::<Test>::AccountNotFound
        );
    });
}

#[test]
fn withdraw_deposit_fails_if_insufficient_deposit() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::make_deposit(RuntimeOrigin::signed(1), 1_000));
        assert_err!(
            AccountManagement::withdraw_deposit(RuntimeOrigin::signed(1), 5_000),
            Error::<Test>::InsufficientDeposit
        );
    });
}

#[test]
fn withdraw_deposit_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::make_deposit(RuntimeOrigin::signed(1), 10_000));
        assert_ok!(AccountManagement::withdraw_deposit(RuntimeOrigin::signed(1), 3_000));
        System::assert_has_event(RuntimeEvent::AccountManagement(
            Event::DepositWithdrawn { account: 1, amount: 3_000, remaining_deposit: 7_000 }
        ));
    });
}

// ── integration ──────────────────────────────────────────────────────────────

#[test]
fn integration_provider_full_lifecycle() {
    new_test_ext().execute_with(|| {
        // Register
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Provider
        ));
        // Submit and verify credential
        assert_ok!(AccountManagement::submit_credential(
            RuntimeOrigin::signed(1), 100, CredentialType::MedicalLicense, b"lic".to_vec()
        ));
        assert_ok!(AccountManagement::verify_credential(RuntimeOrigin::signed(99), 1, 100));
        assert!(AccountInfos::<Test>::get(1u64).unwrap().verified);
        // Make deposit
        assert_ok!(AccountManagement::make_deposit(RuntimeOrigin::signed(1), 50_000));
        // Upgrade tier
        assert_ok!(AccountManagement::update_account_tier(
            RuntimeOrigin::root(), 1, AccountTier::Institution
        ));
        assert_eq!(AccountInfos::<Test>::get(1u64).unwrap().tier, AccountTier::Institution);
    });
}

#[test]
fn multiple_accounts_are_independent() {
    new_test_ext().execute_with(|| {
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(1), AccountTier::Patient
        ));
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(2), AccountTier::Provider
        ));
        assert_ok!(AccountManagement::register_account(
            RuntimeOrigin::signed(3), AccountTier::Institution
        ));
        assert_eq!(AccountInfos::<Test>::get(1u64).unwrap().tier, AccountTier::Patient);
        assert_eq!(AccountInfos::<Test>::get(2u64).unwrap().tier, AccountTier::Provider);
        assert_eq!(AccountInfos::<Test>::get(3u64).unwrap().tier, AccountTier::Institution);
    });
}
