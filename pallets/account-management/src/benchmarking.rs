//! Benchmarks for the ABENA Account Management pallet.

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_system::RawOrigin;

const SEED: u32 = 0;

benchmarks! {

    register_account {
        let caller: T::AccountId = whitelisted_caller();
    }: _(RawOrigin::Signed(caller.clone()), AccountTier::Provider)
    verify {
        assert!(AccountInfos::<T>::contains_key(&caller));
    }

    update_account_tier {
        let caller: T::AccountId = whitelisted_caller();
        Pallet::<T>::register_account(
            RawOrigin::Signed(caller.clone()).into(),
            AccountTier::Patient,
        )?;
    }: _(RawOrigin::Root, caller.clone(), AccountTier::Institution)
    verify {
        assert_eq!(AccountInfos::<T>::get(&caller).unwrap().tier, AccountTier::Institution);
    }

    submit_credential {
        let caller: T::AccountId = whitelisted_caller();
        Pallet::<T>::register_account(
            RawOrigin::Signed(caller.clone()).into(),
            AccountTier::Provider,
        )?;
    }: _(
        RawOrigin::Signed(caller.clone()),
        1u64,
        CredentialType::MedicalLicense,
        b"license_data".to_vec()
    )
    verify {
        assert!(CredentialVerifications::<T>::contains_key(&caller, 1u64));
    }

    verify_credential {
        let owner: T::AccountId    = whitelisted_caller();
        let verifier: T::AccountId = account("verifier", 0, SEED);
        Pallet::<T>::register_account(
            RawOrigin::Signed(owner.clone()).into(),
            AccountTier::Provider,
        )?;
        Pallet::<T>::submit_credential(
            RawOrigin::Signed(owner.clone()).into(),
            1u64,
            CredentialType::MedicalLicense,
            b"data".to_vec(),
        )?;
    }: _(RawOrigin::Signed(verifier.clone()), owner.clone(), 1u64)
    verify {
        let cred = CredentialVerifications::<T>::get(&owner, 1u64).unwrap();
        assert_eq!(cred.status, VerificationStatus::Verified);
    }

    reject_credential {
        let owner: T::AccountId    = whitelisted_caller();
        let rejector: T::AccountId = account("rejector", 0, SEED);
        Pallet::<T>::register_account(
            RawOrigin::Signed(owner.clone()).into(),
            AccountTier::Provider,
        )?;
        Pallet::<T>::submit_credential(
            RawOrigin::Signed(owner.clone()).into(),
            2u64,
            CredentialType::ProfessionalCertification,
            b"data".to_vec(),
        )?;
    }: _(RawOrigin::Signed(rejector), owner.clone(), 2u64, b"Reason".to_vec())
    verify {
        let cred = CredentialVerifications::<T>::get(&owner, 2u64).unwrap();
        assert_eq!(cred.status, VerificationStatus::Rejected);
    }

    make_deposit {
        let caller: T::AccountId = whitelisted_caller();
        let amount: BalanceOf<T> = 1_000u32.into();
        // Fund the caller via the mock genesis (done in new_test_ext) — just use small amount.
    }: _(RawOrigin::Signed(caller.clone()), amount)
    verify {
        assert!(DepositInfos::<T>::contains_key(&caller));
    }

    withdraw_deposit {
        let caller: T::AccountId = whitelisted_caller();
        let amount: BalanceOf<T> = 1_000u32.into();
        Pallet::<T>::make_deposit(RawOrigin::Signed(caller.clone()).into(), amount)?;
    }: _(RawOrigin::Signed(caller.clone()), amount)
    verify {
        assert!(DepositInfos::<T>::get(&caller).is_none());
    }

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}
