use super::*;
use crate::pallet::*;
use frame_benchmarking::v2::*;
use frame_system::RawOrigin;

#[benchmarks]
mod benches {
    use super::*;

    // ── create_channel ────────────────────────────────────────────────────

    #[benchmark]
    fn create_channel() {
        let caller: T::AccountId = whitelisted_caller();
        #[extrinsic_call]
        _(
            RawOrigin::Signed(caller.clone()),
            b"Benchmark Hospital Channel".to_vec(),
            ChannelType::HospitalInsurer,
            vec![],
        );
        let id = NextChannelId::<T>::get() - 1;
        assert!(Channels::<T>::contains_key(id));
    }

    // ── add_member ────────────────────────────────────────────────────────

    #[benchmark]
    fn add_member() {
        let caller: T::AccountId = whitelisted_caller();
        let new_member: T::AccountId = account("member", 1, 1);

        // Create a channel first
        let channel_id = 0u64;
        NextChannelId::<T>::put(1u64);
        let now = frame_system::Pallet::<T>::block_number();
        let name: BoundedVec<u8, ConstU32<64>> =
            BoundedVec::try_from(b"Bench Channel".to_vec()).unwrap();
        let info = ChannelInfo {
            id: channel_id,
            name,
            channel_type: ChannelType::Custom,
            creator: caller.clone(),
            created_at: now,
            status: ChannelStatus::Active,
            member_count: 1,
            data_count: 0,
        };
        Channels::<T>::insert(channel_id, info);
        ChannelMembers::<T>::insert(
            channel_id,
            &caller,
            MemberInfo { role: MemberRole::Admin, enrolled_at: now },
        );
        MemberChannels::<T>::mutate(&caller, |list| {
            let _ = list.try_push(channel_id);
        });

        #[extrinsic_call]
        _(
            RawOrigin::Signed(caller.clone()),
            channel_id,
            new_member.clone(),
            MemberRole::ReadWrite,
        );
        assert!(ChannelMembers::<T>::contains_key(channel_id, &new_member));
    }

    // ── remove_member ─────────────────────────────────────────────────────

    #[benchmark]
    fn remove_member() {
        let caller: T::AccountId = whitelisted_caller();
        let member: T::AccountId = account("member", 1, 1);

        let channel_id = 0u64;
        NextChannelId::<T>::put(1u64);
        let now = frame_system::Pallet::<T>::block_number();
        let name: BoundedVec<u8, ConstU32<64>> =
            BoundedVec::try_from(b"Bench Channel".to_vec()).unwrap();
        let info = ChannelInfo {
            id: channel_id,
            name,
            channel_type: ChannelType::Custom,
            creator: caller.clone(),
            created_at: now,
            status: ChannelStatus::Active,
            member_count: 2,
            data_count: 0,
        };
        Channels::<T>::insert(channel_id, info);
        ChannelMembers::<T>::insert(
            channel_id,
            &caller,
            MemberInfo { role: MemberRole::Admin, enrolled_at: now },
        );
        ChannelMembers::<T>::insert(
            channel_id,
            &member,
            MemberInfo { role: MemberRole::ReadWrite, enrolled_at: now },
        );
        MemberChannels::<T>::mutate(&caller, |l| { let _ = l.try_push(channel_id); });
        MemberChannels::<T>::mutate(&member, |l| { let _ = l.try_push(channel_id); });

        #[extrinsic_call]
        _(RawOrigin::Signed(caller.clone()), channel_id, member.clone());
        assert!(!ChannelMembers::<T>::contains_key(channel_id, &member));
    }

    // ── update_member_role ────────────────────────────────────────────────

    #[benchmark]
    fn update_member_role() {
        let caller: T::AccountId = whitelisted_caller();
        let member: T::AccountId = account("member", 1, 1);

        let channel_id = 0u64;
        NextChannelId::<T>::put(1u64);
        let now = frame_system::Pallet::<T>::block_number();
        let name: BoundedVec<u8, ConstU32<64>> =
            BoundedVec::try_from(b"Bench Channel".to_vec()).unwrap();
        let info = ChannelInfo {
            id: channel_id,
            name,
            channel_type: ChannelType::Custom,
            creator: caller.clone(),
            created_at: now,
            status: ChannelStatus::Active,
            member_count: 2,
            data_count: 0,
        };
        Channels::<T>::insert(channel_id, info);
        ChannelMembers::<T>::insert(
            channel_id,
            &caller,
            MemberInfo { role: MemberRole::Admin, enrolled_at: now },
        );
        ChannelMembers::<T>::insert(
            channel_id,
            &member,
            MemberInfo { role: MemberRole::ReadOnly, enrolled_at: now },
        );

        #[extrinsic_call]
        _(RawOrigin::Signed(caller), channel_id, member.clone(), MemberRole::ReadWrite);
        let updated = ChannelMembers::<T>::get(channel_id, &member).unwrap();
        assert_eq!(updated.role, MemberRole::ReadWrite);
    }

    // ── post_data ─────────────────────────────────────────────────────────

    #[benchmark]
    fn post_data() {
        let caller: T::AccountId = whitelisted_caller();

        let channel_id = 0u64;
        NextChannelId::<T>::put(1u64);
        let now = frame_system::Pallet::<T>::block_number();
        let name: BoundedVec<u8, ConstU32<64>> =
            BoundedVec::try_from(b"Bench Channel".to_vec()).unwrap();
        let info = ChannelInfo {
            id: channel_id,
            name,
            channel_type: ChannelType::Custom,
            creator: caller.clone(),
            created_at: now,
            status: ChannelStatus::Active,
            member_count: 1,
            data_count: 0,
        };
        Channels::<T>::insert(channel_id, info);
        ChannelMembers::<T>::insert(
            channel_id,
            &caller,
            MemberInfo { role: MemberRole::Admin, enrolled_at: now },
        );

        #[extrinsic_call]
        _(
            RawOrigin::Signed(caller),
            channel_id,
            [1u8; 32],
            [2u8; 32],
            DataType::HealthRecord,
        );
        assert!(ChannelData::<T>::contains_key(channel_id, 0u64));
    }

    // ── share_data_cross_channel ──────────────────────────────────────────

    #[benchmark]
    fn share_data_cross_channel() {
        let caller: T::AccountId = whitelisted_caller();
        let other_admin: T::AccountId = account("other", 1, 1);

        let now = frame_system::Pallet::<T>::block_number();
        let name_a: BoundedVec<u8, ConstU32<64>> =
            BoundedVec::try_from(b"Channel A".to_vec()).unwrap();
        let name_b: BoundedVec<u8, ConstU32<64>> =
            BoundedVec::try_from(b"Channel B".to_vec()).unwrap();

        let ch_a = 0u64;
        let ch_b = 1u64;
        NextChannelId::<T>::put(2u64);

        for (ch_id, ch_name, admin) in [(ch_a, name_a, caller.clone()), (ch_b, name_b, other_admin.clone())] {
            let info = ChannelInfo {
                id: ch_id,
                name: ch_name,
                channel_type: ChannelType::InterHospital,
                creator: admin.clone(),
                created_at: now,
                status: ChannelStatus::Active,
                member_count: 1,
                data_count: 0,
            };
            Channels::<T>::insert(ch_id, info);
            ChannelMembers::<T>::insert(
                ch_id,
                &admin,
                MemberInfo { role: MemberRole::Admin, enrolled_at: now },
            );
            MemberChannels::<T>::mutate(&admin, |l| { let _ = l.try_push(ch_id); });
        }

        // Caller is also a ReadWrite member of ch_b
        ChannelMembers::<T>::insert(
            ch_b,
            &caller,
            MemberInfo { role: MemberRole::ReadWrite, enrolled_at: now },
        );
        MemberChannels::<T>::mutate(&caller, |l| { let _ = l.try_push(ch_b); });

        // Insert a data entry in ch_a
        let entry = DataEntry {
            entry_id: 0,
            channel_id: ch_a,
            posted_by: caller.clone(),
            data_hash: [7u8; 32],
            metadata_hash: [8u8; 32],
            data_type: DataType::ResearchDataset,
            posted_at: now,
            is_shared: false,
        };
        ChannelData::<T>::insert(ch_a, 0u64, entry);
        NextEntryId::<T>::insert(ch_a, 1u64);
        Channels::<T>::mutate(ch_a, |c| { if let Some(c) = c { c.data_count = 1; } });

        #[extrinsic_call]
        _(RawOrigin::Signed(caller), ch_a, 0u64, ch_b);
        assert!(CrossChannelGrants::<T>::contains_key(ch_a, 0u64));
    }

    // ── close_channel ─────────────────────────────────────────────────────

    #[benchmark]
    fn close_channel() {
        let caller: T::AccountId = whitelisted_caller();

        let channel_id = 0u64;
        NextChannelId::<T>::put(1u64);
        let now = frame_system::Pallet::<T>::block_number();
        let name: BoundedVec<u8, ConstU32<64>> =
            BoundedVec::try_from(b"Bench Channel".to_vec()).unwrap();
        let info = ChannelInfo {
            id: channel_id,
            name,
            channel_type: ChannelType::Custom,
            creator: caller.clone(),
            created_at: now,
            status: ChannelStatus::Active,
            member_count: 1,
            data_count: 0,
        };
        Channels::<T>::insert(channel_id, info);
        ChannelMembers::<T>::insert(
            channel_id,
            &caller,
            MemberInfo { role: MemberRole::Admin, enrolled_at: now },
        );

        #[extrinsic_call]
        _(RawOrigin::Signed(caller), channel_id);
        assert_eq!(
            Channels::<T>::get(channel_id).unwrap().status,
            ChannelStatus::Closed
        );
    }

    impl_benchmark_test_suite!(
        Pallet,
        crate::mock::new_test_ext(),
        crate::mock::Test,
    );
}
