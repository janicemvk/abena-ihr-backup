//! Smoke tests for the **shipped** ABENA runtime (`runtime/src/lib.rs`).
//!
//! Older cross-pallet scenarios (HealthRecordHash, PatientIdentity, etc.) lived here
//! with a separate mock runtime; those pallets are not workspace members on
//! `polkadot-stable2409`. When you port them, add targeted tests under `pallets/` or
//! reintroduce a mock runtime that matches the workspace.

use abena_runtime::VERSION;

#[test]
fn runtime_spec_matches_baseline() {
    assert_eq!(VERSION.spec_name, "abena-ihr");
    assert_eq!(VERSION.impl_name, "abena-ihr");
    assert_eq!(VERSION.spec_version, 100);
}

#[test]
fn native_version_matches_runtime_version() {
    let nv = abena_runtime::native_version();
    assert_eq!(nv.runtime_version.spec_version, VERSION.spec_version);
    assert_eq!(nv.runtime_version.transaction_version, VERSION.transaction_version);
}
