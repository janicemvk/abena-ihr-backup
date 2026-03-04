//! Mock runtime for testing

use crate as pallet_enterprise_identity;
use frame_support::traits::{ConstU16, ConstU32, ConstU64};
use frame_support::weights::Weight;
use frame_system::EnsureRoot;
use frame_system as system;
use sp_core::H256;
use sp_runtime::traits::{BlakeTwo256, IdentityLookup};
use sp_runtime::BuildStorage;

type Block = frame_system::mocking::MockBlock<Test>;

frame_support::construct_runtime!(
    pub enum Test {
        System: frame_system,
        EnterpriseIdentityPallet: pallet_enterprise_identity,
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
    fn register_enterprise_user() -> Weight {
        Weight::zero()
    }
    fn revoke_enterprise_user() -> Weight {
        Weight::zero()
    }
}

impl pallet_enterprise_identity::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
    type RegisterOrigin = EnsureRoot<u64>;
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let t = RuntimeGenesisConfig::default()
        .build_storage()
        .unwrap();
    let mut ext: sp_io::TestExternalities = t.into();
    ext.execute_with(|| System::set_block_number(1));
    ext
}
