//! Tests for enterprise identity pallet

use crate::mock::*;
use crate::{
    EnterpriseIdentities, EnterpriseUser, EnterpriseUserAccounts, IdentityProvider, OAuthProvider,
};
use frame_support::{assert_ok, traits::ConstU32};
use sp_runtime::BoundedVec;

fn bounded(b: &[u8]) -> BoundedVec<u8, ConstU32<64>> {
    BoundedVec::try_from(b.to_vec()).unwrap()
}

fn bounded256(b: &[u8]) -> BoundedVec<u8, ConstU32<256>> {
    BoundedVec::try_from(b.to_vec()).unwrap()
}

#[test]
fn register_enterprise_user_works() {
    new_test_ext().execute_with(|| {
        let user = EnterpriseUser {
            enterprise_id: 100,
            employee_id: bounded(b"emp-001"),
            metadata_hash: [0u8; 32],
        };
        let idp = IdentityProvider::ActiveDirectory {
            domain: bounded256(b"hospital.local"),
        };
        let cert_fp = [1u8; 32];

        assert_ok!(EnterpriseIdentityPallet::register_enterprise_user(
            RuntimeOrigin::root(),
            1,
            user.clone(),
            idp.clone(),
            cert_fp,
        ));

        let identity = EnterpriseIdentities::<Test>::get(1).unwrap();
        assert_eq!(identity.enterprise_id, 100);
        assert_eq!(identity.cert_fingerprint, cert_fp);

        let acct = EnterpriseUserAccounts::<Test>::get(100, bounded(b"emp-001")).unwrap();
        assert_eq!(acct, 1);
    });
}

#[test]
fn register_twice_fails() {
    new_test_ext().execute_with(|| {
        let user = EnterpriseUser {
            enterprise_id: 100,
            employee_id: bounded(b"emp-001"),
            metadata_hash: [0u8; 32],
        };
        let idp = IdentityProvider::LDAP {
            server: bounded256(b"ldap://dc.example.com"),
        };

        assert_ok!(EnterpriseIdentityPallet::register_enterprise_user(
            RuntimeOrigin::root(),
            1,
            user.clone(),
            idp.clone(),
            [2u8; 32],
        ));

        assert!(EnterpriseIdentityPallet::register_enterprise_user(
            RuntimeOrigin::root(),
            1,
            user,
            idp,
            [3u8; 32],
        )
        .is_err());
    });
}

#[test]
fn revoke_enterprise_user_works() {
    new_test_ext().execute_with(|| {
        let user = EnterpriseUser {
            enterprise_id: 200,
            employee_id: bounded(b"emp-002"),
            metadata_hash: [5u8; 32],
        };
        let idp = IdentityProvider::OAuth {
            provider: OAuthProvider::AzureAD,
        };

        assert_ok!(EnterpriseIdentityPallet::register_enterprise_user(
            RuntimeOrigin::root(),
            2,
            user,
            idp,
            [10u8; 32],
        ));

        assert_ok!(EnterpriseIdentityPallet::revoke_enterprise_user(
            RuntimeOrigin::root(),
            2,
        ));

        assert!(EnterpriseIdentities::<Test>::get(2).is_none());
        assert!(EnterpriseUserAccounts::<Test>::get(200, bounded(b"emp-002")).is_none());
    });
}
