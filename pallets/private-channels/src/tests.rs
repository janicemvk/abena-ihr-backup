use super::*;
use crate::mock::*;
use frame_support::{assert_err, assert_ok};
use pallet::Event;

// ── helpers ──────────────────────────────────────────────────────────────────

fn create_channel_ok(creator: u64, name: &[u8], ctype: ChannelType) -> ChannelId {
    assert_ok!(PrivateChannels::create_channel(
        RuntimeOrigin::signed(creator),
        name.to_vec(),
        ctype,
        vec![],
    ));
    // The channel ID is always NextChannelId - 1 after creation
    PrivateChannels::next_channel_id() - 1
}

fn post_data_ok(who: u64, channel_id: ChannelId) -> DataEntryId {
    assert_ok!(PrivateChannels::post_data(
        RuntimeOrigin::signed(who),
        channel_id,
        [1u8; 32],
        [2u8; 32],
        DataType::HealthRecord,
    ));
    // Entry ID is NextEntryId - 1 for this channel
    pallet::NextEntryId::<Test>::get(channel_id) - 1
}

// ── create_channel ────────────────────────────────────────────────────────────

#[test]
fn create_channel_success() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Hospital A - NHIA Channel", ChannelType::HospitalInsurer);
        let ch = PrivateChannels::channel(id).unwrap();
        assert_eq!(ch.channel_type, ChannelType::HospitalInsurer);
        assert_eq!(ch.status, ChannelStatus::Active);
        assert_eq!(ch.creator, ALICE);
        assert_eq!(ch.member_count, 1);
    });
}

#[test]
fn create_channel_creator_becomes_admin() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test Channel", ChannelType::Custom);
        let member = PrivateChannels::member_info(id, ALICE).unwrap();
        assert_eq!(member.role, MemberRole::Admin);
    });
}

#[test]
fn create_channel_with_initial_members() {
    new_test_ext().execute_with(|| {
        assert_ok!(PrivateChannels::create_channel(
            RuntimeOrigin::signed(ALICE),
            b"Research Channel".to_vec(),
            ChannelType::Research,
            vec![BOB, CHARLIE],
        ));
        let id = PrivateChannels::next_channel_id() - 1;
        let ch = PrivateChannels::channel(id).unwrap();
        assert_eq!(ch.member_count, 3); // ALICE + BOB + CHARLIE
        assert!(PrivateChannels::is_member(id, &BOB));
        assert!(PrivateChannels::is_member(id, &CHARLIE));
        let bob_info = PrivateChannels::member_info(id, BOB).unwrap();
        assert_eq!(bob_info.role, MemberRole::ReadWrite);
    });
}

#[test]
fn create_channel_name_too_long_fails() {
    new_test_ext().execute_with(|| {
        let long_name = vec![b'X'; 65];
        assert_err!(
            PrivateChannels::create_channel(
                RuntimeOrigin::signed(ALICE),
                long_name,
                ChannelType::Custom,
                vec![],
            ),
            Error::<Test>::NameTooLong
        );
    });
}

#[test]
fn create_channel_increments_id() {
    new_test_ext().execute_with(|| {
        let id1 = create_channel_ok(ALICE, b"Channel One", ChannelType::Custom);
        let id2 = create_channel_ok(ALICE, b"Channel Two", ChannelType::Research);
        assert_eq!(id2, id1 + 1);
    });
}

#[test]
fn create_channel_emits_event() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"My Channel", ChannelType::PatientCentric);
        let expected_name: sp_runtime::BoundedVec<u8, frame_support::traits::ConstU32<64>> =
            sp_runtime::BoundedVec::try_from(b"My Channel".to_vec()).unwrap();
        System::assert_has_event(RuntimeEvent::PrivateChannels(Event::ChannelCreated {
            channel_id: id,
            name: expected_name,
            channel_type: ChannelType::PatientCentric,
            creator: ALICE,
        }));
    });
}

#[test]
fn create_channel_member_channels_reverse_index() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        let channels = PrivateChannels::channels_of(&ALICE);
        assert!(channels.contains(&id));
    });
}

// ── add_member ────────────────────────────────────────────────────────────────

#[test]
fn add_member_success() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Hosp-Insurer", ChannelType::HospitalInsurer);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE),
            id,
            CHARLIE,
            MemberRole::ReadWrite,
        ));
        assert!(PrivateChannels::is_member(id, &CHARLIE));
        assert_eq!(PrivateChannels::channel(id).unwrap().member_count, 2);
    });
}

#[test]
fn add_member_requires_admin() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE),
            id,
            BOB,
            MemberRole::ReadWrite,
        ));
        // BOB (ReadWrite) cannot add members
        assert_err!(
            PrivateChannels::add_member(
                RuntimeOrigin::signed(BOB),
                id,
                CHARLIE,
                MemberRole::ReadOnly,
            ),
            Error::<Test>::InsufficientRole
        );
    });
}

#[test]
fn add_duplicate_member_fails() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE),
            id,
            BOB,
            MemberRole::ReadWrite,
        ));
        assert_err!(
            PrivateChannels::add_member(
                RuntimeOrigin::signed(ALICE),
                id,
                BOB,
                MemberRole::ReadOnly,
            ),
            Error::<Test>::AlreadyMember
        );
    });
}

#[test]
fn add_member_to_nonexistent_channel_fails() {
    new_test_ext().execute_with(|| {
        assert_err!(
            PrivateChannels::add_member(RuntimeOrigin::signed(ALICE), 99, BOB, MemberRole::ReadWrite),
            Error::<Test>::ChannelNotFound
        );
    });
}

#[test]
fn add_member_emits_event() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE),
            id,
            BOB,
            MemberRole::ReadOnly,
        ));
        System::assert_has_event(RuntimeEvent::PrivateChannels(Event::MemberAdded {
            channel_id: id,
            member: BOB,
            role: MemberRole::ReadOnly,
        }));
    });
}

// ── remove_member ─────────────────────────────────────────────────────────────

#[test]
fn remove_member_success() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadWrite,
        ));
        assert_ok!(PrivateChannels::remove_member(RuntimeOrigin::signed(ALICE), id, BOB));
        assert!(!PrivateChannels::is_member(id, &BOB));
        assert_eq!(PrivateChannels::channel(id).unwrap().member_count, 1);
    });
}

#[test]
fn remove_member_removes_from_reverse_index() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadWrite,
        ));
        assert_ok!(PrivateChannels::remove_member(RuntimeOrigin::signed(ALICE), id, BOB));
        assert!(!PrivateChannels::channels_of(&BOB).contains(&id));
    });
}

#[test]
fn admin_cannot_remove_self() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_err!(
            PrivateChannels::remove_member(RuntimeOrigin::signed(ALICE), id, ALICE),
            Error::<Test>::CannotRemoveSelf
        );
    });
}

#[test]
fn remove_non_member_fails() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_err!(
            PrivateChannels::remove_member(RuntimeOrigin::signed(ALICE), id, BOB),
            Error::<Test>::NotAMember
        );
    });
}

#[test]
fn remove_member_emits_event() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadWrite,
        ));
        assert_ok!(PrivateChannels::remove_member(RuntimeOrigin::signed(ALICE), id, BOB));
        System::assert_has_event(RuntimeEvent::PrivateChannels(Event::MemberRemoved {
            channel_id: id,
            member: BOB,
        }));
    });
}

// ── update_member_role ────────────────────────────────────────────────────────

#[test]
fn promote_member_to_admin() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::InterHospital);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadWrite,
        ));
        assert_ok!(PrivateChannels::update_member_role(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::Admin,
        ));
        let info = PrivateChannels::member_info(id, BOB).unwrap();
        assert_eq!(info.role, MemberRole::Admin);
    });
}

#[test]
fn demote_member_to_readonly() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadWrite,
        ));
        assert_ok!(PrivateChannels::update_member_role(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadOnly,
        ));
        assert!(!PrivateChannels::can_write(id, &BOB));
        assert!(PrivateChannels::can_read(id, &BOB));
    });
}

#[test]
fn update_role_for_nonmember_fails() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_err!(
            PrivateChannels::update_member_role(
                RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadWrite,
            ),
            Error::<Test>::NotAMember
        );
    });
}

#[test]
fn update_role_emits_event() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadOnly,
        ));
        assert_ok!(PrivateChannels::update_member_role(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadWrite,
        ));
        System::assert_has_event(RuntimeEvent::PrivateChannels(Event::MemberRoleUpdated {
            channel_id: id,
            member: BOB,
            new_role: MemberRole::ReadWrite,
        }));
    });
}

// ── post_data ─────────────────────────────────────────────────────────────────

#[test]
fn post_data_success() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Clinical Channel", ChannelType::HospitalInsurer);
        let entry_id = post_data_ok(ALICE, id);
        let entry = PrivateChannels::data_entry(id, entry_id).unwrap();
        assert_eq!(entry.data_hash, [1u8; 32]);
        assert_eq!(entry.data_type, DataType::HealthRecord);
        assert!(!entry.is_shared);
    });
}

#[test]
fn post_data_increments_channel_count() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        post_data_ok(ALICE, id);
        post_data_ok(ALICE, id);
        assert_eq!(PrivateChannels::channel(id).unwrap().data_count, 2);
    });
}

#[test]
fn readonly_member_cannot_post() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadOnly,
        ));
        assert_err!(
            PrivateChannels::post_data(
                RuntimeOrigin::signed(BOB),
                id,
                [0u8; 32],
                [0u8; 32],
                DataType::LabResult,
            ),
            Error::<Test>::InsufficientRole
        );
    });
}

#[test]
fn non_member_cannot_post() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_err!(
            PrivateChannels::post_data(
                RuntimeOrigin::signed(BOB),
                id,
                [0u8; 32],
                [0u8; 32],
                DataType::Prescription,
            ),
            Error::<Test>::NotAMember
        );
    });
}

#[test]
fn post_data_to_closed_channel_fails() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::close_channel(RuntimeOrigin::signed(ALICE), id));
        assert_err!(
            PrivateChannels::post_data(
                RuntimeOrigin::signed(ALICE),
                id,
                [0u8; 32],
                [0u8; 32],
                DataType::HealthRecord,
            ),
            Error::<Test>::ChannelClosed
        );
    });
}

#[test]
fn readwrite_member_can_post() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadWrite,
        ));
        let entry_id = post_data_ok(BOB, id);
        let entry = PrivateChannels::data_entry(id, entry_id).unwrap();
        assert_eq!(entry.posted_by, BOB);
    });
}

#[test]
fn post_data_emits_event() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        post_data_ok(ALICE, id);
        System::assert_has_event(RuntimeEvent::PrivateChannels(Event::DataPosted {
            channel_id: id,
            entry_id: 0,
            posted_by: ALICE,
            data_type: DataType::HealthRecord,
            data_hash: [1u8; 32],
        }));
    });
}

#[test]
fn post_various_data_types() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Multi", ChannelType::Research);
        for dtype in [
            DataType::LabResult,
            DataType::Prescription,
            DataType::ImagingStudy,
            DataType::ClinicalTrialData,
            DataType::ConsentDocument,
        ] {
            assert_ok!(PrivateChannels::post_data(
                RuntimeOrigin::signed(ALICE),
                id,
                [3u8; 32],
                [4u8; 32],
                dtype,
            ));
        }
        assert_eq!(PrivateChannels::channel(id).unwrap().data_count, 5);
    });
}

// ── share_data_cross_channel ─────────────────────────────────────────────────

#[test]
fn share_data_cross_channel_success() {
    new_test_ext().execute_with(|| {
        // Hospital A channel
        let ch_a = create_channel_ok(ALICE, b"Hospital A", ChannelType::InterHospital);
        // Hospital B channel, ALICE is also a member
        let ch_b = create_channel_ok(EVE, b"Hospital B", ChannelType::InterHospital);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(EVE), ch_b, ALICE, MemberRole::ReadWrite,
        ));

        let entry_id = post_data_ok(ALICE, ch_a);
        assert_ok!(PrivateChannels::share_data_cross_channel(
            RuntimeOrigin::signed(ALICE),
            ch_a,
            entry_id,
            ch_b,
        ));

        // A grant record exists
        let grant = PrivateChannels::cross_channel_grant(ch_a, entry_id).unwrap();
        assert_eq!(grant.target_channel, ch_b);

        // A mirrored entry was created in channel B
        let mirror_id = pallet::NextEntryId::<Test>::get(ch_b) - 1;
        let mirror = PrivateChannels::data_entry(ch_b, mirror_id).unwrap();
        assert!(mirror.is_shared);
        assert_eq!(mirror.data_hash, [1u8; 32]);
    });
}

#[test]
fn share_requires_source_membership() {
    new_test_ext().execute_with(|| {
        let ch_a = create_channel_ok(ALICE, b"Channel A", ChannelType::Custom);
        let ch_b = create_channel_ok(EVE, b"Channel B", ChannelType::Custom);
        let entry_id = post_data_ok(ALICE, ch_a);

        // BOB is not a member of ch_a
        assert_err!(
            PrivateChannels::share_data_cross_channel(
                RuntimeOrigin::signed(BOB),
                ch_a,
                entry_id,
                ch_b,
            ),
            Error::<Test>::NotAMember
        );
    });
}

#[test]
fn share_requires_target_membership() {
    new_test_ext().execute_with(|| {
        let ch_a = create_channel_ok(ALICE, b"Channel A", ChannelType::Custom);
        let ch_b = create_channel_ok(EVE, b"Channel B", ChannelType::Custom);
        let entry_id = post_data_ok(ALICE, ch_a);

        // ALICE is not in ch_b
        assert_err!(
            PrivateChannels::share_data_cross_channel(
                RuntimeOrigin::signed(ALICE),
                ch_a,
                entry_id,
                ch_b,
            ),
            Error::<Test>::NotAMember
        );
    });
}

#[test]
fn share_nonexistent_entry_fails() {
    new_test_ext().execute_with(|| {
        let ch_a = create_channel_ok(ALICE, b"Channel A", ChannelType::Custom);
        let ch_b = create_channel_ok(EVE, b"Channel B", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(EVE), ch_b, ALICE, MemberRole::ReadWrite,
        ));
        assert_err!(
            PrivateChannels::share_data_cross_channel(
                RuntimeOrigin::signed(ALICE),
                ch_a,
                99, // doesn't exist
                ch_b,
            ),
            Error::<Test>::DataEntryNotFound
        );
    });
}

#[test]
fn duplicate_share_fails() {
    new_test_ext().execute_with(|| {
        let ch_a = create_channel_ok(ALICE, b"Channel A", ChannelType::Custom);
        let ch_b = create_channel_ok(EVE, b"Channel B", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(EVE), ch_b, ALICE, MemberRole::ReadWrite,
        ));
        let entry_id = post_data_ok(ALICE, ch_a);
        assert_ok!(PrivateChannels::share_data_cross_channel(
            RuntimeOrigin::signed(ALICE), ch_a, entry_id, ch_b,
        ));
        assert_err!(
            PrivateChannels::share_data_cross_channel(
                RuntimeOrigin::signed(ALICE), ch_a, entry_id, ch_b,
            ),
            Error::<Test>::AlreadyShared
        );
    });
}

#[test]
fn share_data_emits_event() {
    new_test_ext().execute_with(|| {
        let ch_a = create_channel_ok(ALICE, b"A", ChannelType::Custom);
        let ch_b = create_channel_ok(EVE, b"B", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(EVE), ch_b, ALICE, MemberRole::ReadWrite,
        ));
        let entry_id = post_data_ok(ALICE, ch_a);
        assert_ok!(PrivateChannels::share_data_cross_channel(
            RuntimeOrigin::signed(ALICE), ch_a, entry_id, ch_b,
        ));
        System::assert_has_event(RuntimeEvent::PrivateChannels(Event::DataSharedCrossChannel {
            source_channel: ch_a,
            target_channel: ch_b,
            entry_id,
            shared_by: ALICE,
        }));
    });
}

// ── close_channel ─────────────────────────────────────────────────────────────

#[test]
fn close_channel_success() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::close_channel(RuntimeOrigin::signed(ALICE), id));
        assert_eq!(PrivateChannels::channel(id).unwrap().status, ChannelStatus::Closed);
    });
}

#[test]
fn close_already_closed_channel_fails() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::close_channel(RuntimeOrigin::signed(ALICE), id));
        assert_err!(
            PrivateChannels::close_channel(RuntimeOrigin::signed(ALICE), id),
            Error::<Test>::ChannelClosed
        );
    });
}

#[test]
fn close_channel_non_admin_fails() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadWrite,
        ));
        assert_err!(
            PrivateChannels::close_channel(RuntimeOrigin::signed(BOB), id),
            Error::<Test>::InsufficientRole
        );
    });
}

#[test]
fn close_channel_emits_event() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::close_channel(RuntimeOrigin::signed(ALICE), id));
        System::assert_has_event(RuntimeEvent::PrivateChannels(Event::ChannelClosed {
            channel_id: id,
        }));
    });
}

#[test]
fn add_member_to_closed_channel_fails() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::close_channel(RuntimeOrigin::signed(ALICE), id));
        assert_err!(
            PrivateChannels::add_member(
                RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadWrite,
            ),
            Error::<Test>::ChannelClosed
        );
    });
}

// ── query helpers ─────────────────────────────────────────────────────────────

#[test]
fn can_read_returns_false_for_non_member() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert!(!PrivateChannels::can_read(id, &BOB));
    });
}

#[test]
fn can_write_returns_false_for_readonly() {
    new_test_ext().execute_with(|| {
        let id = create_channel_ok(ALICE, b"Test", ChannelType::Custom);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE), id, BOB, MemberRole::ReadOnly,
        ));
        assert!(!PrivateChannels::can_write(id, &BOB));
        assert!(PrivateChannels::can_read(id, &BOB));
    });
}

#[test]
fn channels_of_returns_all_enrolled() {
    new_test_ext().execute_with(|| {
        let id1 = create_channel_ok(ALICE, b"C1", ChannelType::Custom);
        let id2 = create_channel_ok(ALICE, b"C2", ChannelType::Research);
        let channels = PrivateChannels::channels_of(&ALICE);
        assert!(channels.contains(&id1));
        assert!(channels.contains(&id2));
    });
}

// ── full lifecycle integration ────────────────────────────────────────────────

#[test]
fn hospital_insurer_channel_lifecycle() {
    new_test_ext().execute_with(|| {
        // 1. Hospital A admin creates a hospital-insurer channel
        let ch = create_channel_ok(ALICE, b"Accra General - NHIA", ChannelType::HospitalInsurer);

        // 2. Add hospital staff and insurer
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE), ch, BOB, MemberRole::ReadWrite,
        ));
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(ALICE), ch, CHARLIE, MemberRole::ReadOnly,
        ));

        // 3. Hospital staff posts a claim
        let entry_id = post_data_ok(BOB, ch);

        // 4. Insurer (ReadOnly) cannot post back
        assert_err!(
            PrivateChannels::post_data(
                RuntimeOrigin::signed(CHARLIE), ch, [9u8; 32], [9u8; 32], DataType::InsuranceClaim,
            ),
            Error::<Test>::InsufficientRole
        );

        // 5. The claim exists and is accessible
        let entry = PrivateChannels::data_entry(ch, entry_id).unwrap();
        assert_eq!(entry.posted_by, BOB);

        // 6. Admin closes the channel
        assert_ok!(PrivateChannels::close_channel(RuntimeOrigin::signed(ALICE), ch));
    });
}

#[test]
fn research_cross_channel_sharing_lifecycle() {
    new_test_ext().execute_with(|| {
        // Hospital A research channel
        let ch_a = create_channel_ok(ALICE, b"Hospital A Research", ChannelType::Research);
        // Hospital B research channel, ALICE is a bridge member
        let ch_b = create_channel_ok(EVE, b"Hospital B Research", ChannelType::Research);
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(EVE), ch_b, ALICE, MemberRole::ReadWrite,
        ));

        // Hospital A posts anonymised dataset
        let entry_id = post_data_ok(ALICE, ch_a);

        // Verify Hospital B members cannot see ch_a data directly
        assert!(!PrivateChannels::is_member(ch_a, &EVE));

        // Share dataset to ch_b
        assert_ok!(PrivateChannels::share_data_cross_channel(
            RuntimeOrigin::signed(ALICE),
            ch_a,
            entry_id,
            ch_b,
        ));

        // ch_b now has a mirrored entry with the same data hash
        let mirror_id = pallet::NextEntryId::<Test>::get(ch_b) - 1;
        let mirror = PrivateChannels::data_entry(ch_b, mirror_id).unwrap();
        assert!(mirror.is_shared);
        assert_eq!(mirror.data_hash, [1u8; 32]);

        // Channel B data count reflects the shared entry
        assert_eq!(PrivateChannels::channel(ch_b).unwrap().data_count, 1);
    });
}

#[test]
fn patient_centric_channel_lifecycle() {
    new_test_ext().execute_with(|| {
        // Patient creates their own channel
        let ch = create_channel_ok(FRANK, b"Frank - My Care Team", ChannelType::PatientCentric);

        // Patient invites their GP and specialist
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(FRANK), ch, ALICE, MemberRole::ReadWrite,
        ));
        assert_ok!(PrivateChannels::add_member(
            RuntimeOrigin::signed(FRANK), ch, BOB, MemberRole::ReadOnly,
        ));

        // GP posts a health record
        post_data_ok(ALICE, ch);

        // Specialist (ReadOnly) reads but can't post
        assert!(PrivateChannels::can_read(ch, &BOB));
        assert!(!PrivateChannels::can_write(ch, &BOB));

        // Patient promotes specialist to ReadWrite
        assert_ok!(PrivateChannels::update_member_role(
            RuntimeOrigin::signed(FRANK), ch, BOB, MemberRole::ReadWrite,
        ));
        assert!(PrivateChannels::can_write(ch, &BOB));

        // Patient removes GP after treatment ends
        assert_ok!(PrivateChannels::remove_member(RuntimeOrigin::signed(FRANK), ch, ALICE));
        assert!(!PrivateChannels::is_member(ch, &ALICE));
    });
}
