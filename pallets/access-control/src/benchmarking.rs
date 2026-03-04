//! Benchmarks for the ABENA Access Control pallet.
//!
//! Covers all 7 extrinsics: grant/revoke patient authorization,
//! grant/revoke institutional permission, grant/revoke emergency access,
//! and check_read_access.

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_system::RawOrigin;
use sp_core::H256;

const SEED: u32 = 0;

fn resource(n: u32) -> H256 { H256::from_low_u64_be(n as u64) }

benchmarks! {

    // ── grant_patient_authorization ──────────────────────────────────────────
    grant_patient_authorization {
        let caller: T::AccountId = whitelisted_caller();
        let rid = resource(1);
    }: _(RawOrigin::Signed(caller.clone()), rid, PermissionType::Full)
    verify {
        assert!(PatientAuthorizations::<T>::contains_key(&caller, rid));
    }

    // ── revoke_patient_authorization ─────────────────────────────────────────
    revoke_patient_authorization {
        let caller: T::AccountId = whitelisted_caller();
        let rid = resource(1);
        Pallet::<T>::grant_patient_authorization(
            RawOrigin::Signed(caller.clone()).into(),
            rid,
            PermissionType::Read,
        )?;
    }: _(RawOrigin::Signed(caller.clone()), rid)
    verify {
        assert!(!PatientAuthorizations::<T>::contains_key(&caller, rid));
    }

    // ── grant_institutional_permission ───────────────────────────────────────
    grant_institutional_permission {
        let granter: T::AccountId   = whitelisted_caller();
        let institution: T::AccountId = account("inst", 0, SEED);
        let inst_key = institution.clone();
        let rid = resource(2);
    }: _(
        RawOrigin::Signed(granter.clone()),
        institution,
        rid,
        AccessLevel::Full,
        None
    )
    verify {
        assert!(InstitutionalPermissions::<T>::contains_key(&inst_key, rid));
    }

    // ── revoke_institutional_permission ──────────────────────────────────────
    revoke_institutional_permission {
        let granter: T::AccountId    = whitelisted_caller();
        let institution: T::AccountId = account("inst", 0, SEED);
        let inst_key = institution.clone();
        let rid = resource(2);
        Pallet::<T>::grant_institutional_permission(
            RawOrigin::Signed(granter.clone()).into(),
            institution.clone(),
            rid,
            AccessLevel::Read,
            None,
        )?;
    }: _(RawOrigin::Signed(granter.clone()), institution, rid)
    verify {
        assert!(!InstitutionalPermissions::<T>::contains_key(&inst_key, rid));
    }

    // ── grant_emergency_access ───────────────────────────────────────────────
    grant_emergency_access {
        let authorizer: T::AccountId = whitelisted_caller();
        let requester: T::AccountId  = account("requester", 0, SEED);
        let req_key = requester.clone();
        let rid = resource(3);
    }: _(
        RawOrigin::Signed(authorizer.clone()),
        requester,
        rid,
        EmergencyAccessReason::LifeThreatening,
        100u32.into()
    )
    verify {
        assert!(EmergencyAccessRecords::<T>::contains_key(&req_key, rid));
    }

    // ── revoke_emergency_access ──────────────────────────────────────────────
    revoke_emergency_access {
        let authorizer: T::AccountId = whitelisted_caller();
        let requester: T::AccountId  = account("requester", 0, SEED);
        let req_key = requester.clone();
        let rid = resource(3);
        Pallet::<T>::grant_emergency_access(
            RawOrigin::Signed(authorizer.clone()).into(),
            requester.clone(),
            rid,
            EmergencyAccessReason::MedicalEmergency,
            100u32.into(),
        )?;
    }: _(RawOrigin::Signed(authorizer.clone()), requester, rid)
    verify {
        assert!(!EmergencyAccessRecords::<T>::contains_key(&req_key, rid));
    }

    // ── check_read_access (patient authorization path) ───────────────────────
    check_read_access {
        let caller: T::AccountId = whitelisted_caller();
        let rid = resource(4);
        Pallet::<T>::grant_patient_authorization(
            RawOrigin::Signed(caller.clone()).into(),
            rid,
            PermissionType::Full,
        )?;
    }: _(RawOrigin::Signed(caller.clone()), rid)
    verify {}

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}
