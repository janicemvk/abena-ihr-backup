//! Mock runtime for pallet-data-marketplace tests
//!
//! Minimal test runtime with System, PatientIdentity, and DataMarketplace.
//! Balances can be added when the pallet Config is extended for payments.

use crate as pallet_data_marketplace;
use frame_support::traits::{ConstU16, ConstU32, ConstU64};
use frame_system as system;
use pallet_patient_identity;
use sp_core::H256;
use sp_runtime::{
    traits::{BlakeTwo256, IdentityLookup},
    BuildStorage,
};

pub type Block = frame_system::mocking::MockBlock<Test>;

frame_support::construct_runtime!(
    pub enum Test {
        System: frame_system,
        PatientIdentity: pallet_patient_identity,
        DataMarketplace: pallet_data_marketplace,
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

impl pallet_patient_identity::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type MaxProvidersPerPatient = ConstU32<50>;
    type MaxConsentRecords = ConstU32<10>;
    type WeightInfo = pallet_patient_identity::weights::SubstrateWeight<Test>;
}

impl pallet_data_marketplace::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
}

impl frame_system::offchain::SendTransactionTypes<pallet_data_marketplace::Call<Test>> for Test {
    type OverarchingCall = RuntimeCall;
    type Extrinsic = frame_system::mocking::MockUncheckedExtrinsic<Test>;
}

/// Build test externalities
pub fn new_test_ext() -> sp_io::TestExternalities {
    system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap()
        .into()
}

/// Advance to block n (for event tests)
pub fn run_to_block(n: u32) {
    frame_system::Pallet::<Test>::set_block_number(n.into());
}
