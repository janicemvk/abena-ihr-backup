//! Mock runtime for pallet-health-record-hash tests.
//!
//! The pallet is self-contained (no Currency, no patient-identity dependency at
//! the Config level), so this mock only needs frame_system + the pallet itself.

use crate as pallet_health_record_hash;
use frame_support::traits::{ConstU16, ConstU32, ConstU64};
use frame_system as system;
use sp_core::H256;
use frame_support::weights::Weight;
use sp_runtime::{
    traits::{BlakeTwo256, IdentityLookup},
    BuildStorage,
};

type Block = frame_system::mocking::MockBlock<Test>;

frame_support::construct_runtime!(
    pub enum Test {
        System: frame_system,
        HealthRecordHash: pallet_health_record_hash,
    }
);

impl system::Config for Test {
    type BaseCallFilter = frame_support::traits::Everything;
    type BlockWeights = ();
    type BlockLength = ();
    type DbWeight = ();
    type RuntimeOrigin = RuntimeOrigin;
    type RuntimeCall = RuntimeCall;
    type Nonce = u64;
    type Hash = H256;
    type Hashing = BlakeTwo256;
    type AccountId = u64;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
    type RuntimeEvent = RuntimeEvent;
    type BlockHashCount = ConstU64<250>;
    type Version = ();
    type PalletInfo = PalletInfo;
    type AccountData = ();
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type SS58Prefix = ConstU16<42>;
    type OnSetCode = ();
    type MaxConsumers = ConstU32<16>;
    type RuntimeTask = ();
    type SingleBlockMigrations = ();
    type MultiBlockMigrator = ();
    type PreInherents = ();
    type PostInherents = ();
    type PostTransactions = ();
}

impl crate::WeightInfo for () {
    fn record_hash() -> Weight { Weight::zero() }
    fn update_hash() -> Weight { Weight::zero() }
    fn set_multi_sig() -> Weight { Weight::zero() }
    fn create_record_hash() -> Weight { Weight::zero() }
    fn update_record_hash() -> Weight { Weight::zero() }
    fn grant_record_access() -> Weight { Weight::zero() }
    fn revoke_record_access() -> Weight { Weight::zero() }
    fn access_record() -> Weight { Weight::zero() }
    fn verify_record_integrity() -> Weight { Weight::zero() }
    fn link_to_quantum_result() -> Weight { Weight::zero() }
    fn create_multisig_requirement() -> Weight { Weight::zero() }
    fn sign_record_access() -> Weight { Weight::zero() }
    fn emergency_access_override() -> Weight { Weight::zero() }
    fn mark_record_inactive() -> Weight { Weight::zero() }
}

impl pallet_health_record_hash::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
}

// ──────────────────────────────────────────────────────────────────────────────
// Test accounts
// ──────────────────────────────────────────────────────────────────────────────

/// A healthcare provider / record creator.
pub const ALICE: u64 = 1;
/// The patient whose records are being managed.
pub const BOB: u64 = 2;
/// A second provider or collaborator.
pub const CHARLIE: u64 = 3;
/// An unauthorised third party used in failure tests.
pub const DAVE: u64 = 4;
/// Additional signer for multi-sig tests.
pub const EVE: u64 = 5;

// ──────────────────────────────────────────────────────────────────────────────
// Test externalities
// ──────────────────────────────────────────────────────────────────────────────

pub fn new_test_ext() -> sp_io::TestExternalities {
    let mut ext: sp_io::TestExternalities = system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap()
        .into();
    ext.execute_with(|| System::set_block_number(1));
    ext
}
