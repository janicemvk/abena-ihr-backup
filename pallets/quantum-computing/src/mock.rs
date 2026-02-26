//! Mock runtime for testing

use crate as pallet_quantum_computing;
use frame_support::{
    traits::{ConstU16, ConstU32, ConstU64},
    weights::Weight,
    PalletId,
};
use frame_system as system;
use sp_core::H256;
use sp_runtime::{
    traits::{BlakeTwo256, IdentityLookup},
    BuildStorage,
};

type Block = frame_system::mocking::MockBlock<Test>;

frame_support::construct_runtime!(
    pub enum Test
    {
        System: frame_system,
        QuantumComputing: pallet_quantum_computing,
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

pub struct TestPalletId;
impl frame_support::traits::Get<PalletId> for TestPalletId {
    fn get() -> PalletId {
        PalletId(*b"test/qcp")
    }
}

impl crate::WeightInfo for () {
    fn submit_job() -> Weight { Weight::zero() }
    fn store_result() -> Weight { Weight::zero() }
    fn register_integration_point() -> Weight { Weight::zero() }
    fn update_integration_point() -> Weight { Weight::zero() }
    fn query_result() -> Weight { Weight::zero() }
}

impl pallet_quantum_computing::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type PalletId = TestPalletId;
    type WeightInfo = ();
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let mut ext: sp_io::TestExternalities = system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap()
        .into();
    ext.execute_with(|| System::set_block_number(1));
    ext
}
