//! Benchmarks for enterprise identity pallet

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_system::RawOrigin;
use sp_runtime::BoundedVec;

const SEED: u32 = 0;

benchmarks! {
    register_enterprise_user {
        let caller: T::AccountId = whitelisted_caller();
        let account: T::AccountId = account("user", 0, SEED);
        let employee_id = BoundedVec::try_from(b"emp-bench".to_vec()).unwrap();
        let user = EnterpriseUser {
            enterprise_id: 1,
            employee_id,
            metadata_hash: [0u8; 32],
        };
        let idp = IdentityProvider::ActiveDirectory {
            domain: BoundedVec::try_from(b"bench.local".to_vec()).unwrap(),
        };
        let cert_fp = [1u8; 32];
    }: _(RawOrigin::Root, account, user, idp, cert_fp)
    verify {
        assert!(EnterpriseIdentities::<T>::contains_key(&account));
    }

    revoke_enterprise_user {
        let caller: T::AccountId = whitelisted_caller();
        let account: T::AccountId = account("user", 0, SEED);
        let user = EnterpriseUser {
            enterprise_id: 1,
            employee_id: BoundedVec::try_from(b"emp-rev".to_vec()).unwrap(),
            metadata_hash: [0u8; 32],
        };
        let idp = IdentityProvider::SAML {
            idp_url: BoundedVec::try_from(b"https://idp.example.com".to_vec()).unwrap(),
        };
        let cert_fp = [2u8; 32];
        crate::Pallet::<T>::register_enterprise_user(
            RawOrigin::Root.into(),
            account.clone(),
            user,
            idp,
            cert_fp,
        ).unwrap();
    }: _(RawOrigin::Root, account)
    verify {
        assert!(!EnterpriseIdentities::<T>::contains_key(&account));
    }

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}
