//! Mock runtime for testing data-separation pallet (includes patient-identity and balances for escrow)

use crate as pallet_data_separation;
use frame_support::traits::{ConstU16, ConstU32, ConstU64, ConstU128};
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
        Balances: pallet_balances,
        PatientIdentity: pallet_patient_identity,
        DataSeparation: pallet_data_separation,
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
    type AccountData = pallet_balances::AccountData<u128>;
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

impl pallet_balances::Config for Test {
    type MaxLocks = ConstU32<50>;
    type MaxReserves = ();
    type ReserveIdentifier = [u8; 8];
    type Balance = u128;
    type RuntimeEvent = RuntimeEvent;
    type DustRemoval = ();
    type ExistentialDeposit = ConstU128<1>;
    type AccountStore = System;
    type WeightInfo = ();
    type FreezeIdentifier = RuntimeFreezeReason;
    type MaxFreezes = ConstU32<0>;
    type RuntimeHoldReason = RuntimeHoldReason;
    type RuntimeFreezeReason = RuntimeFreezeReason;
}

impl pallet_patient_identity::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = pallet_patient_identity::weights::SubstrateWeight<Test>;
    type MaxProvidersPerPatient = ConstU32<50>;
    type MaxConsentRecords = ConstU32<10>;
}

pub struct DataPricingConfig;
impl frame_support::traits::Get<pallet_data_separation::DataPricing> for DataPricingConfig {
    fn get() -> pallet_data_separation::DataPricing {
        pallet_data_separation::DataPricing::default_prices()
    }
}

pub struct ViolationPenaltyConfig;
impl frame_support::traits::Get<u128> for ViolationPenaltyConfig {
    fn get() -> u128 {
        1_000_000
    }
}

impl pallet_data_separation::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
    type Currency = Balances;
    type MinKAnonymity = ConstU32<2>;
    type MaxDataAssetsPerPatient = ConstU32<64>;
    type MaxAssetsToScan = ConstU32<256>;
    type DataPricing = DataPricingConfig;
    type ViolationPenalty = ViolationPenaltyConfig;
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let mut t = RuntimeGenesisConfig {
        balances: pallet_balances::GenesisConfig {
            balances: vec![(1, 1_000_000), (2, 1_000_000), (3, 1_000_000)],
        },
        ..Default::default()
    }
    .build_storage()
    .unwrap();
    let mut ext: sp_io::TestExternalities = t.into();
    ext.execute_with(|| System::set_block_number(1));
    ext
}
