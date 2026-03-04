use super::*;
use crate::pallet::*;
use frame_benchmarking::v2::*;
use frame_system::RawOrigin;

#[benchmarks]
mod benches {
    use super::*;

    #[benchmark]
    fn set_network_mode() {
        // Start in Public, switch to Permissioned
        CurrentNetworkMode::<T>::put(NetworkMode::Public);
        #[extrinsic_call]
        _(RawOrigin::Root, NetworkMode::Permissioned);
        assert_eq!(CurrentNetworkMode::<T>::get(), NetworkMode::Permissioned);
    }

    #[benchmark]
    fn add_validator() {
        let caller: T::AccountId = whitelisted_caller();
        let name = b"Benchmark Hospital".to_vec();
        #[extrinsic_call]
        _(RawOrigin::Root, caller.clone(), name, ValidatorRole::BlockProducer, 0u32);
        assert!(ApprovedValidators::<T>::contains_key(&caller));
    }

    #[benchmark]
    fn remove_validator() {
        let caller: T::AccountId = whitelisted_caller();
        let name: BoundedVec<u8, ConstU32<64>> =
            BoundedVec::try_from(b"Benchmark Hospital".to_vec()).unwrap();
        let info = ValidatorInfo {
            account: caller.clone(),
            institution_name: name,
            role: ValidatorRole::BlockProducer,
            status: ApprovalStatus::Approved,
            added_at: frame_system::Pallet::<T>::block_number(),
            consortium_id: 0,
        };
        ApprovedValidators::<T>::insert(&caller, info);
        ValidatorList::<T>::mutate(|list| {
            let _ = list.try_push(caller.clone());
        });
        #[extrinsic_call]
        _(RawOrigin::Root, caller.clone());
        assert!(!ApprovedValidators::<T>::contains_key(&caller));
    }

    #[benchmark]
    fn update_validator() {
        let caller: T::AccountId = whitelisted_caller();
        let name: BoundedVec<u8, ConstU32<64>> =
            BoundedVec::try_from(b"Benchmark Hospital".to_vec()).unwrap();
        let info = ValidatorInfo {
            account: caller.clone(),
            institution_name: name,
            role: ValidatorRole::BlockProducer,
            status: ApprovalStatus::Approved,
            added_at: frame_system::Pallet::<T>::block_number(),
            consortium_id: 0,
        };
        ApprovedValidators::<T>::insert(&caller, info);
        #[extrinsic_call]
        _(RawOrigin::Root, caller.clone(), ValidatorRole::ConsortiumMember, 5u32);
        let updated = ApprovedValidators::<T>::get(&caller).unwrap();
        assert_eq!(updated.role, ValidatorRole::ConsortiumMember);
    }

    #[benchmark]
    fn register_institution() {
        let caller: T::AccountId = whitelisted_caller();
        let name = b"Benchmark Clinic".to_vec();
        #[extrinsic_call]
        _(
            RawOrigin::Signed(caller.clone()),
            name,
            InstitutionType::Hospital,
            [0u8; 32],
        );
        assert!(RegisteredInstitutions::<T>::contains_key(&caller));
    }

    #[benchmark]
    fn approve_institution() {
        let caller: T::AccountId = whitelisted_caller();
        let name: BoundedVec<u8, ConstU32<64>> =
            BoundedVec::try_from(b"Benchmark Clinic".to_vec()).unwrap();
        let info = InstitutionInfo {
            account: caller.clone(),
            name,
            institution_type: InstitutionType::Hospital,
            contact_hash: [0u8; 32],
            status: ApprovalStatus::Pending,
            registered_at: frame_system::Pallet::<T>::block_number(),
        };
        RegisteredInstitutions::<T>::insert(&caller, info);
        #[extrinsic_call]
        _(RawOrigin::Root, caller.clone());
        let updated = RegisteredInstitutions::<T>::get(&caller).unwrap();
        assert_eq!(updated.status, ApprovalStatus::Approved);
    }

    #[benchmark]
    fn revoke_institution() {
        let caller: T::AccountId = whitelisted_caller();
        let name: BoundedVec<u8, ConstU32<64>> =
            BoundedVec::try_from(b"Benchmark Clinic".to_vec()).unwrap();
        let info = InstitutionInfo {
            account: caller.clone(),
            name,
            institution_type: InstitutionType::Hospital,
            contact_hash: [0u8; 32],
            status: ApprovalStatus::Approved,
            registered_at: frame_system::Pallet::<T>::block_number(),
        };
        RegisteredInstitutions::<T>::insert(&caller, info);
        #[extrinsic_call]
        _(RawOrigin::Root, caller.clone());
        let updated = RegisteredInstitutions::<T>::get(&caller).unwrap();
        assert_eq!(updated.status, ApprovalStatus::Revoked);
    }

    impl_benchmark_test_suite!(
        Pallet,
        crate::mock::new_test_ext(),
        crate::mock::Test,
    );
}
