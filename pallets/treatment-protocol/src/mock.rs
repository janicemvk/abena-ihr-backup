//! Mock runtime for pallet-treatment-protocol tests.
//!
//! The pallet Config only requires RuntimeEvent + WeightInfo, so this mock is
//! self-contained — no patient-identity, health-records, quantum-results, or
//! abena-coin pallet is needed at the Config level. Tests that simulate
//! cross-pallet workflows manipulate the pallet's own storage directly.

use crate as pallet_treatment_protocol;
use frame_support::traits::{ConstU16, ConstU32, ConstU64};
use frame_system as system;
use sp_core::H256;
use sp_runtime::{
    traits::{BlakeTwo256, IdentityLookup},
    BuildStorage,
};

type Block = frame_system::mocking::MockBlock<Test>;

frame_support::construct_runtime!(
    pub enum Test {
        System: frame_system,
        TreatmentProtocol: pallet_treatment_protocol,
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

impl pallet_treatment_protocol::WeightInfo for () {
    fn create_protocol() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn validate_protocol() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn update_protocol() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn register_guideline() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn register_protocol() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn validate_protocol_spec() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn initiate_treatment() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn record_step_completion() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn check_contraindications() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn evaluate_milestone() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn modify_protocol() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn complete_treatment() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn report_adverse_event() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn add_interaction_rule() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn query_interaction() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
}

impl pallet_treatment_protocol::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
}

// ──────────────────────────────────────────────────────────────────────────────
// Test accounts
// ──────────────────────────────────────────────────────────────────────────────

/// Protocol creator / first provider.
pub const ALICE: u64 = 1;
/// Patient under treatment.
pub const BOB: u64 = 2;
/// Second provider / medical board validator.
pub const CHARLIE: u64 = 3;
/// Second validator / safety officer.
pub const DAVE: u64 = 4;
/// Unauthorised caller used in failure tests.
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
