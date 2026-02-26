//! Mock runtime for pallet-quantum-results tests.

use crate as pallet_quantum_results;
use frame_support::traits::{ConstU16, ConstU32, ConstU64};
use frame_system as system;
use sp_core::H256;
use sp_runtime::{
    testing::TestXt,
    traits::{BlakeTwo256, IdentityLookup},
    BuildStorage,
};

type Block = frame_system::mocking::MockBlock<Test>;

frame_support::construct_runtime!(
    pub enum Test {
        System: frame_system,
        QuantumResults: pallet_quantum_results,
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

/// Implement SendTransactionTypes so the OCW-capable pallet compiles in the mock.
/// Uses `TestXt` from sp_runtime::testing as the extrinsic type.
impl<LocalCall> frame_system::offchain::SendTransactionTypes<LocalCall> for Test
where
    RuntimeCall: From<LocalCall>,
{
    type OverarchingCall = RuntimeCall;
    type Extrinsic = TestXt<RuntimeCall, ()>;
}

impl pallet_quantum_results::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
    /// Run off-chain worker every 10 blocks (irrelevant for unit tests, needed for Config).
    type OffchainWorkerInterval = ConstU64<10>;
}

// ---- Test accounts ----------------------------------------------------------

/// Researcher / attestation submitter.
pub const ALICE: u64 = 1;
/// A second researcher.
pub const BOB: u64 = 2;
/// Governance / root.
pub const ROOT: u64 = 99;

// ---- Helpers ----------------------------------------------------------------

/// A deterministic H256 from a small integer seed.
pub fn h256(seed: u8) -> H256 {
    H256::from([seed; 32])
}

/// A valid-looking job ID (≤ 64 bytes).
pub fn job_id(tag: &str) -> Vec<u8> {
    format!("ibm-job-{}", tag).into_bytes()
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let mut ext: sp_io::TestExternalities = system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap()
        .into();
    // FRAME only stores events when block_number > 0.
    ext.execute_with(|| System::set_block_number(1));
    ext
}
