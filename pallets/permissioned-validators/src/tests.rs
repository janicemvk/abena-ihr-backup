use super::*;
use crate::mock::*;
use frame_support::{assert_err, assert_ok};
use pallet::Event;

// ── helpers ──────────────────────────────────────────────────────────────────

fn add_validator_ok(validator: u64, name: &[u8], role: ValidatorRole, cid: u32) {
    assert_ok!(PermissionedValidators::add_validator(
        RuntimeOrigin::root(),
        validator,
        name.to_vec(),
        role,
        cid,
    ));
}

fn register_institution_ok(who: u64, name: &[u8], itype: InstitutionType) {
    assert_ok!(PermissionedValidators::register_institution(
        RuntimeOrigin::signed(who),
        name.to_vec(),
        itype,
        [0u8; 32],
    ));
}

// ── set_network_mode ─────────────────────────────────────────────────────────

#[test]
fn set_network_mode_to_permissioned() {
    new_test_ext().execute_with(|| {
        assert_ok!(PermissionedValidators::set_network_mode(
            RuntimeOrigin::root(),
            NetworkMode::Permissioned
        ));
        assert_eq!(PermissionedValidators::network_mode(), NetworkMode::Permissioned);
    });
}

#[test]
fn set_network_mode_to_consortium() {
    new_test_ext().execute_with(|| {
        assert_ok!(PermissionedValidators::set_network_mode(
            RuntimeOrigin::root(),
            NetworkMode::Consortium
        ));
        assert_eq!(PermissionedValidators::network_mode(), NetworkMode::Consortium);
    });
}

#[test]
fn set_network_mode_to_hybrid() {
    new_test_ext().execute_with(|| {
        assert_ok!(PermissionedValidators::set_network_mode(
            RuntimeOrigin::root(),
            NetworkMode::Hybrid
        ));
        assert!(PermissionedValidators::is_permissioned());
    });
}

#[test]
fn set_network_mode_public_is_not_permissioned() {
    new_test_ext().execute_with(|| {
        // Default is already Public, switch to Permissioned then back
        assert_ok!(PermissionedValidators::set_network_mode(
            RuntimeOrigin::root(),
            NetworkMode::Permissioned
        ));
        assert_ok!(PermissionedValidators::set_network_mode(
            RuntimeOrigin::root(),
            NetworkMode::Public
        ));
        assert!(!PermissionedValidators::is_permissioned());
    });
}

#[test]
fn set_network_mode_unchanged_fails() {
    new_test_ext().execute_with(|| {
        // Default is Public; setting it to Public again should fail
        assert_err!(
            PermissionedValidators::set_network_mode(RuntimeOrigin::root(), NetworkMode::Public),
            Error::<Test>::ModeUnchanged
        );
    });
}

#[test]
fn set_network_mode_requires_admin() {
    new_test_ext().execute_with(|| {
        assert_err!(
            PermissionedValidators::set_network_mode(
                RuntimeOrigin::signed(ALICE),
                NetworkMode::Permissioned
            ),
            sp_runtime::DispatchError::BadOrigin
        );
    });
}

#[test]
fn set_network_mode_emits_event() {
    new_test_ext().execute_with(|| {
        assert_ok!(PermissionedValidators::set_network_mode(
            RuntimeOrigin::root(),
            NetworkMode::Permissioned
        ));
        System::assert_has_event(RuntimeEvent::PermissionedValidators(
            Event::NetworkModeChanged {
                old_mode: NetworkMode::Public,
                new_mode: NetworkMode::Permissioned,
            },
        ));
    });
}

// ── add_validator ─────────────────────────────────────────────────────────────

#[test]
fn add_validator_success() {
    new_test_ext().execute_with(|| {
        add_validator_ok(ALICE, b"City Hospital", ValidatorRole::BlockProducer, 0);
        assert!(PermissionedValidators::is_approved_validator(&ALICE));
    });
}

#[test]
fn add_validator_stores_correct_info() {
    new_test_ext().execute_with(|| {
        add_validator_ok(ALICE, b"City Hospital", ValidatorRole::ConsortiumMember, 7);
        let info = PermissionedValidators::validator_info(&ALICE).unwrap();
        assert_eq!(info.role, ValidatorRole::ConsortiumMember);
        assert_eq!(info.consortium_id, 7);
        assert_eq!(info.status, ApprovalStatus::Approved);
        assert_eq!(info.institution_name.as_slice(), b"City Hospital");
    });
}

#[test]
fn add_validator_appears_in_list() {
    new_test_ext().execute_with(|| {
        add_validator_ok(ALICE, b"Alpha Clinic", ValidatorRole::BlockProducer, 0);
        add_validator_ok(BOB, b"Beta Clinic", ValidatorRole::Finalizer, 0);
        let list = PermissionedValidators::validator_list();
        assert!(list.contains(&ALICE));
        assert!(list.contains(&BOB));
    });
}

#[test]
fn add_duplicate_validator_fails() {
    new_test_ext().execute_with(|| {
        add_validator_ok(ALICE, b"City Hospital", ValidatorRole::BlockProducer, 0);
        assert_err!(
            PermissionedValidators::add_validator(
                RuntimeOrigin::root(),
                ALICE,
                b"City Hospital".to_vec(),
                ValidatorRole::BlockProducer,
                0,
            ),
            Error::<Test>::ValidatorAlreadyExists
        );
    });
}

#[test]
fn add_validator_name_too_long_fails() {
    new_test_ext().execute_with(|| {
        let long_name = vec![b'X'; 65];
        assert_err!(
            PermissionedValidators::add_validator(
                RuntimeOrigin::root(),
                ALICE,
                long_name,
                ValidatorRole::BlockProducer,
                0,
            ),
            Error::<Test>::NameTooLong
        );
    });
}

#[test]
fn add_validator_requires_admin() {
    new_test_ext().execute_with(|| {
        assert_err!(
            PermissionedValidators::add_validator(
                RuntimeOrigin::signed(ALICE),
                BOB,
                b"Rogue Clinic".to_vec(),
                ValidatorRole::BlockProducer,
                0,
            ),
            sp_runtime::DispatchError::BadOrigin
        );
    });
}

#[test]
fn add_validator_emits_event() {
    new_test_ext().execute_with(|| {
        add_validator_ok(ALICE, b"City Hospital", ValidatorRole::BridgeOperator, 3);
        let expected_name: sp_runtime::BoundedVec<u8, frame_support::traits::ConstU32<64>> =
            sp_runtime::BoundedVec::try_from(b"City Hospital".to_vec()).unwrap();
        System::assert_has_event(RuntimeEvent::PermissionedValidators(
            Event::ValidatorAdded {
                validator: ALICE,
                institution_name: expected_name,
                role: ValidatorRole::BridgeOperator,
                consortium_id: 3,
            },
        ));
    });
}

// ── remove_validator ──────────────────────────────────────────────────────────

#[test]
fn remove_validator_success() {
    new_test_ext().execute_with(|| {
        add_validator_ok(ALICE, b"City Hospital", ValidatorRole::BlockProducer, 0);
        assert_ok!(PermissionedValidators::remove_validator(
            RuntimeOrigin::root(),
            ALICE
        ));
        assert!(!PermissionedValidators::is_approved_validator(&ALICE));
        assert!(!PermissionedValidators::validator_list().contains(&ALICE));
    });
}

#[test]
fn remove_nonexistent_validator_fails() {
    new_test_ext().execute_with(|| {
        assert_err!(
            PermissionedValidators::remove_validator(RuntimeOrigin::root(), ALICE),
            Error::<Test>::ValidatorNotFound
        );
    });
}

#[test]
fn remove_validator_emits_event() {
    new_test_ext().execute_with(|| {
        add_validator_ok(ALICE, b"City Hospital", ValidatorRole::BlockProducer, 0);
        assert_ok!(PermissionedValidators::remove_validator(
            RuntimeOrigin::root(),
            ALICE
        ));
        System::assert_has_event(RuntimeEvent::PermissionedValidators(
            Event::ValidatorRemoved { validator: ALICE },
        ));
    });
}

#[test]
fn remove_validator_requires_admin() {
    new_test_ext().execute_with(|| {
        add_validator_ok(ALICE, b"City Hospital", ValidatorRole::BlockProducer, 0);
        assert_err!(
            PermissionedValidators::remove_validator(RuntimeOrigin::signed(BOB), ALICE),
            sp_runtime::DispatchError::BadOrigin
        );
    });
}

// ── update_validator ──────────────────────────────────────────────────────────

#[test]
fn update_validator_role_and_consortium() {
    new_test_ext().execute_with(|| {
        add_validator_ok(ALICE, b"City Hospital", ValidatorRole::BlockProducer, 1);
        assert_ok!(PermissionedValidators::update_validator(
            RuntimeOrigin::root(),
            ALICE,
            ValidatorRole::ConsortiumMember,
            5
        ));
        let info = PermissionedValidators::validator_info(&ALICE).unwrap();
        assert_eq!(info.role, ValidatorRole::ConsortiumMember);
        assert_eq!(info.consortium_id, 5);
    });
}

#[test]
fn update_nonexistent_validator_fails() {
    new_test_ext().execute_with(|| {
        assert_err!(
            PermissionedValidators::update_validator(
                RuntimeOrigin::root(),
                ALICE,
                ValidatorRole::Finalizer,
                0,
            ),
            Error::<Test>::ValidatorNotFound
        );
    });
}

#[test]
fn update_validator_emits_event() {
    new_test_ext().execute_with(|| {
        add_validator_ok(ALICE, b"City Hospital", ValidatorRole::BlockProducer, 0);
        assert_ok!(PermissionedValidators::update_validator(
            RuntimeOrigin::root(),
            ALICE,
            ValidatorRole::Finalizer,
            2
        ));
        System::assert_has_event(RuntimeEvent::PermissionedValidators(
            Event::ValidatorUpdated {
                validator: ALICE,
                new_role: ValidatorRole::Finalizer,
                new_consortium_id: 2,
            },
        ));
    });
}

// ── register_institution ──────────────────────────────────────────────────────

#[test]
fn register_institution_success() {
    new_test_ext().execute_with(|| {
        register_institution_ok(HOSPITAL_A, b"Accra General Hospital", InstitutionType::Hospital);
        let info = PermissionedValidators::institution_info(HOSPITAL_A).unwrap();
        assert_eq!(info.status, ApprovalStatus::Pending);
        assert_eq!(info.institution_type, InstitutionType::Hospital);
    });
}

#[test]
fn register_institution_appears_in_list() {
    new_test_ext().execute_with(|| {
        register_institution_ok(HOSPITAL_A, b"Accra General", InstitutionType::Hospital);
        assert!(PermissionedValidators::institution_list().contains(&HOSPITAL_A));
    });
}

#[test]
fn register_institution_duplicate_fails() {
    new_test_ext().execute_with(|| {
        register_institution_ok(HOSPITAL_A, b"Accra General", InstitutionType::Hospital);
        assert_err!(
            PermissionedValidators::register_institution(
                RuntimeOrigin::signed(HOSPITAL_A),
                b"Accra General".to_vec(),
                InstitutionType::Hospital,
                [0u8; 32],
            ),
            Error::<Test>::InstitutionAlreadyRegistered
        );
    });
}

#[test]
fn register_institution_name_too_long_fails() {
    new_test_ext().execute_with(|| {
        let long_name = vec![b'X'; 65];
        assert_err!(
            PermissionedValidators::register_institution(
                RuntimeOrigin::signed(HOSPITAL_A),
                long_name,
                InstitutionType::Hospital,
                [0u8; 32],
            ),
            Error::<Test>::NameTooLong
        );
    });
}

#[test]
fn register_institution_emits_event() {
    new_test_ext().execute_with(|| {
        register_institution_ok(HOSPITAL_A, b"Accra General", InstitutionType::Hospital);
        let expected_name: sp_runtime::BoundedVec<u8, frame_support::traits::ConstU32<64>> =
            sp_runtime::BoundedVec::try_from(b"Accra General".to_vec()).unwrap();
        System::assert_has_event(RuntimeEvent::PermissionedValidators(
            Event::InstitutionRegistered {
                institution: HOSPITAL_A,
                name: expected_name,
                institution_type: InstitutionType::Hospital,
            },
        ));
    });
}

#[test]
fn register_various_institution_types() {
    new_test_ext().execute_with(|| {
        register_institution_ok(10, b"Lab A", InstitutionType::Laboratory);
        register_institution_ok(11, b"Pharmacy B", InstitutionType::Pharmacy);
        register_institution_ok(12, b"Insurer C", InstitutionType::InsuranceProvider);
        register_institution_ok(13, b"Research D", InstitutionType::ResearchInstitution);
        assert_eq!(PermissionedValidators::institution_list().len(), 4);
    });
}

// ── approve_institution ───────────────────────────────────────────────────────

#[test]
fn approve_institution_success() {
    new_test_ext().execute_with(|| {
        register_institution_ok(HOSPITAL_A, b"Accra General", InstitutionType::Hospital);
        assert_ok!(PermissionedValidators::approve_institution(
            RuntimeOrigin::root(),
            HOSPITAL_A
        ));
        let info = PermissionedValidators::institution_info(HOSPITAL_A).unwrap();
        assert_eq!(info.status, ApprovalStatus::Approved);
    });
}

#[test]
fn approve_institution_not_pending_fails() {
    new_test_ext().execute_with(|| {
        register_institution_ok(HOSPITAL_A, b"Accra General", InstitutionType::Hospital);
        assert_ok!(PermissionedValidators::approve_institution(
            RuntimeOrigin::root(),
            HOSPITAL_A
        ));
        assert_err!(
            PermissionedValidators::approve_institution(RuntimeOrigin::root(), HOSPITAL_A),
            Error::<Test>::InstitutionNotPending
        );
    });
}

#[test]
fn approve_nonexistent_institution_fails() {
    new_test_ext().execute_with(|| {
        assert_err!(
            PermissionedValidators::approve_institution(RuntimeOrigin::root(), HOSPITAL_A),
            Error::<Test>::InstitutionNotFound
        );
    });
}

#[test]
fn approve_institution_requires_admin() {
    new_test_ext().execute_with(|| {
        register_institution_ok(HOSPITAL_A, b"Accra General", InstitutionType::Hospital);
        assert_err!(
            PermissionedValidators::approve_institution(
                RuntimeOrigin::signed(ALICE),
                HOSPITAL_A
            ),
            sp_runtime::DispatchError::BadOrigin
        );
    });
}

#[test]
fn approve_institution_emits_event() {
    new_test_ext().execute_with(|| {
        register_institution_ok(HOSPITAL_A, b"Accra General", InstitutionType::Hospital);
        assert_ok!(PermissionedValidators::approve_institution(
            RuntimeOrigin::root(),
            HOSPITAL_A
        ));
        System::assert_has_event(RuntimeEvent::PermissionedValidators(
            Event::InstitutionApproved { institution: HOSPITAL_A },
        ));
    });
}

// ── revoke_institution ────────────────────────────────────────────────────────

#[test]
fn revoke_pending_institution_success() {
    new_test_ext().execute_with(|| {
        register_institution_ok(HOSPITAL_A, b"Accra General", InstitutionType::Hospital);
        assert_ok!(PermissionedValidators::revoke_institution(
            RuntimeOrigin::root(),
            HOSPITAL_A
        ));
        let info = PermissionedValidators::institution_info(HOSPITAL_A).unwrap();
        assert_eq!(info.status, ApprovalStatus::Revoked);
    });
}

#[test]
fn revoke_approved_institution_success() {
    new_test_ext().execute_with(|| {
        register_institution_ok(HOSPITAL_A, b"Accra General", InstitutionType::Hospital);
        assert_ok!(PermissionedValidators::approve_institution(
            RuntimeOrigin::root(),
            HOSPITAL_A
        ));
        assert_ok!(PermissionedValidators::revoke_institution(
            RuntimeOrigin::root(),
            HOSPITAL_A
        ));
        let info = PermissionedValidators::institution_info(HOSPITAL_A).unwrap();
        assert_eq!(info.status, ApprovalStatus::Revoked);
    });
}

#[test]
fn revoke_nonexistent_institution_fails() {
    new_test_ext().execute_with(|| {
        assert_err!(
            PermissionedValidators::revoke_institution(RuntimeOrigin::root(), HOSPITAL_A),
            Error::<Test>::InstitutionNotFound
        );
    });
}

#[test]
fn revoke_institution_emits_event() {
    new_test_ext().execute_with(|| {
        register_institution_ok(HOSPITAL_A, b"Accra General", InstitutionType::Hospital);
        assert_ok!(PermissionedValidators::revoke_institution(
            RuntimeOrigin::root(),
            HOSPITAL_A
        ));
        System::assert_has_event(RuntimeEvent::PermissionedValidators(
            Event::InstitutionRevoked { institution: HOSPITAL_A },
        ));
    });
}

// ── query helpers ─────────────────────────────────────────────────────────────

#[test]
fn approved_validator_accounts_returns_only_approved() {
    new_test_ext().execute_with(|| {
        add_validator_ok(ALICE, b"Alpha", ValidatorRole::BlockProducer, 0);
        add_validator_ok(BOB, b"Beta", ValidatorRole::BlockProducer, 0);
        // Remove BOB so it is no longer in the map
        assert_ok!(PermissionedValidators::remove_validator(RuntimeOrigin::root(), BOB));
        let list = PermissionedValidators::approved_validator_accounts();
        assert!(list.contains(&ALICE));
        assert!(!list.contains(&BOB));
    });
}

#[test]
fn consortium_validators_filter_by_group() {
    new_test_ext().execute_with(|| {
        add_validator_ok(ALICE, b"Alpha", ValidatorRole::ConsortiumMember, 1);
        add_validator_ok(BOB, b"Beta", ValidatorRole::ConsortiumMember, 2);
        add_validator_ok(CHARLIE, b"Gamma", ValidatorRole::ConsortiumMember, 1);

        let group1 = PermissionedValidators::consortium_validators(1);
        assert!(group1.contains(&ALICE));
        assert!(group1.contains(&CHARLIE));
        assert!(!group1.contains(&BOB));

        let group2 = PermissionedValidators::consortium_validators(2);
        assert!(group2.contains(&BOB));
        assert!(!group2.contains(&ALICE));
    });
}

#[test]
fn is_permissioned_reflects_mode() {
    new_test_ext().execute_with(|| {
        assert!(!PermissionedValidators::is_permissioned());

        assert_ok!(PermissionedValidators::set_network_mode(
            RuntimeOrigin::root(),
            NetworkMode::Permissioned
        ));
        assert!(PermissionedValidators::is_permissioned());

        assert_ok!(PermissionedValidators::set_network_mode(
            RuntimeOrigin::root(),
            NetworkMode::Public
        ));
        assert!(!PermissionedValidators::is_permissioned());
    });
}

// ── full lifecycle integration ────────────────────────────────────────────────

#[test]
fn full_validator_lifecycle() {
    new_test_ext().execute_with(|| {
        // 1. Switch to Permissioned mode
        assert_ok!(PermissionedValidators::set_network_mode(
            RuntimeOrigin::root(),
            NetworkMode::Permissioned
        ));

        // 2. Add two validators
        add_validator_ok(HOSPITAL_A, b"Accra General Validator", ValidatorRole::BlockProducer, 0);
        add_validator_ok(HOSPITAL_B, b"Kumasi Teaching Validator", ValidatorRole::BlockProducer, 0);
        assert_eq!(PermissionedValidators::approved_validator_accounts().len(), 2);

        // 3. Update one to a consortium role
        assert_ok!(PermissionedValidators::update_validator(
            RuntimeOrigin::root(),
            HOSPITAL_B,
            ValidatorRole::ConsortiumMember,
            1
        ));

        // 4. Remove one
        assert_ok!(PermissionedValidators::remove_validator(
            RuntimeOrigin::root(),
            HOSPITAL_A
        ));
        assert_eq!(PermissionedValidators::approved_validator_accounts().len(), 1);

        // 5. Switch to Consortium mode
        assert_ok!(PermissionedValidators::set_network_mode(
            RuntimeOrigin::root(),
            NetworkMode::Consortium
        ));
        assert_eq!(PermissionedValidators::consortium_validators(1).len(), 1);
    });
}

#[test]
fn full_institution_lifecycle() {
    new_test_ext().execute_with(|| {
        // Register
        register_institution_ok(HOSPITAL_A, b"Accra General", InstitutionType::Hospital);
        assert_eq!(
            PermissionedValidators::institution_info(HOSPITAL_A).unwrap().status,
            ApprovalStatus::Pending
        );

        // Approve
        assert_ok!(PermissionedValidators::approve_institution(
            RuntimeOrigin::root(),
            HOSPITAL_A
        ));
        assert_eq!(
            PermissionedValidators::institution_info(HOSPITAL_A).unwrap().status,
            ApprovalStatus::Approved
        );

        // Revoke
        assert_ok!(PermissionedValidators::revoke_institution(
            RuntimeOrigin::root(),
            HOSPITAL_A
        ));
        assert_eq!(
            PermissionedValidators::institution_info(HOSPITAL_A).unwrap().status,
            ApprovalStatus::Revoked
        );

        // Record is retained after revocation
        assert!(PermissionedValidators::institution_info(HOSPITAL_A).is_some());
    });
}
