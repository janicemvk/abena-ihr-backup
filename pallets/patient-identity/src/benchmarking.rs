//! Benchmarks for pallet-patient-identity.
//!
//! Targets:
//!   register_patient               – baseline single registration
//!   update_consent                 – grant consent for one modality
//!   grant_provider_access          – worst-case: p existing providers (linear)
//!   revoke_provider_access         – remove access from an existing grant
//!   verify_provider_access         – block benchmark: lookup through p grants (linear)
//!   verify_consent                 – block benchmark: lookup through n consents (linear)

use super::*;
use frame_benchmarking::{account, benchmarks, whitelisted_caller};
use frame_support::traits::Get;
use frame_system::RawOrigin;

const SEED: u32 = 0;

benchmarks! {

    // ── register_patient ────────────────────────────────────────────────────
    // Baseline: single caller, no prior state.
    register_patient {
        let caller: T::AccountId = whitelisted_caller();
    }: _(
        RawOrigin::Signed(caller.clone()),
        [1u8; 32],
        [2u8; 32],
        None
    )
    verify {
        assert!(PatientIdentities::<T>::contains_key(&caller));
    }

    // ── update_consent ──────────────────────────────────────────────────────
    // Grant consent for WesternMedicine (patient already registered).
    update_consent {
        let caller: T::AccountId = whitelisted_caller();
        Pallet::<T>::register_patient(
            RawOrigin::Signed(caller.clone()).into(),
            [1u8; 32], [2u8; 32], None,
        )?;
    }: _(
        RawOrigin::Signed(caller.clone()),
        TherapeuticModality::WesternMedicine,
        true,
        None
    )
    verify {
        assert!(ConsentRecords::<T>::contains_key(&caller, TherapeuticModality::WesternMedicine));
    }

    // ── grant_provider_access ────────────────────────────────────────────────
    // Worst-case: p existing providers already in the patient's access list.
    // Range: 1 .. MaxProvidersPerPatient - 1 (one slot must remain free).
    grant_provider_access {
        let p in 1 .. T::MaxProvidersPerPatient::get().saturating_sub(1);

        let patient: T::AccountId = whitelisted_caller();
        Pallet::<T>::register_patient(
            RawOrigin::Signed(patient.clone()).into(),
            [1u8; 32], [2u8; 32], None,
        )?;

        // Pre-populate p existing provider grants directly in storage.
        for i in 0..p {
            let existing: T::AccountId = account("existing_provider", i, SEED);
            ProviderAccessList::<T>::insert(
                &patient,
                &existing,
                ProviderAccess::<T> {
                    provider_account: existing.clone(),
                    granted_at: 0u64,
                    expires_at: None,
                    access_level: AccessLevel::Read,
                },
            );
        }

        let new_provider: T::AccountId = account("new_provider", p, SEED);
    }: _(
        RawOrigin::Signed(patient.clone()),
        new_provider.clone(),
        AccessLevel::ReadWrite,
        None
    )
    verify {
        assert!(ProviderAccessList::<T>::contains_key(&patient, &new_provider));
    }

    // ── revoke_provider_access ────────────────────────────────────────────────
    // Revoke a single existing grant.
    revoke_provider_access {
        let patient: T::AccountId = whitelisted_caller();
        Pallet::<T>::register_patient(
            RawOrigin::Signed(patient.clone()).into(),
            [1u8; 32], [2u8; 32], None,
        )?;
        let provider: T::AccountId = account("provider", 0, SEED);
        Pallet::<T>::grant_provider_access(
            RawOrigin::Signed(patient.clone()).into(),
            provider.clone(),
            AccessLevel::Read,
            None,
        )?;
    }: _(RawOrigin::Signed(patient.clone()), provider.clone())
    verify {
        assert!(!ProviderAccessList::<T>::contains_key(&patient, &provider));
    }

    // ── verify_provider_access ────────────────────────────────────────────────
    // Block benchmark: check access for a patient with p existing grants.
    // The helper iterates storage lookup (O(1) map access; linear parameter
    // models benchmark framework's cost estimation).
    verify_provider_access {
        let p in 1 .. T::MaxProvidersPerPatient::get();

        let patient: T::AccountId = whitelisted_caller();
        Pallet::<T>::register_patient(
            RawOrigin::Signed(patient.clone()).into(),
            [1u8; 32], [2u8; 32], None,
        )?;

        // Insert p providers; the LAST one is the one we will verify.
        for i in 0..p {
            let prov: T::AccountId = account("prov", i, SEED);
            ProviderAccessList::<T>::insert(
                &patient,
                &prov,
                ProviderAccess::<T> {
                    provider_account: prov.clone(),
                    granted_at: 0u64,
                    expires_at: None,
                    access_level: AccessLevel::Read,
                },
            );
        }

        let target_provider: T::AccountId = account("prov", p - 1, SEED);
    }: {
        let _ = Pallet::<T>::verify_provider_access(&patient, &target_provider);
    }
    verify {
        assert!(Pallet::<T>::verify_provider_access(&patient, &target_provider));
    }

    // ── verify_consent ────────────────────────────────────────────────────────
    // Block benchmark: check consent with n modalities populated.
    // Uses all 5 distinct therapeutic modalities in rotation.
    verify_consent {
        let n in 1 .. T::MaxConsentRecords::get();

        let patient: T::AccountId = whitelisted_caller();
        Pallet::<T>::register_patient(
            RawOrigin::Signed(patient.clone()).into(),
            [1u8; 32], [2u8; 32], None,
        )?;

        // Grant consents across available modalities (cycling through 5 variants).
        let modalities = [
            TherapeuticModality::WesternMedicine,
            TherapeuticModality::TraditionalChineseMedicine,
            TherapeuticModality::Ayurveda,
            TherapeuticModality::Homeopathy,
            TherapeuticModality::Naturopathy,
        ];
        let count = (n as usize).min(modalities.len());
        for i in 0..count {
            Pallet::<T>::update_consent(
                RawOrigin::Signed(patient.clone()).into(),
                modalities[i].clone(),
                true,
                None,
            )?;
        }
    }: {
        let _ = Pallet::<T>::verify_consent(&patient, &TherapeuticModality::WesternMedicine);
    }
    verify {
        assert!(Pallet::<T>::verify_consent(&patient, &TherapeuticModality::WesternMedicine));
    }

    impl_benchmark_test_suite!(
        Pallet,
        crate::mock::new_test_ext(),
        crate::mock::Test,
    );
}
