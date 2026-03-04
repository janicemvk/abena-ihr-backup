use crate as pallet_permissioned_validators;
use frame_support::{
    derive_impl,
    traits::ConstU32,
};
use frame_system::EnsureRoot;
use sp_runtime::{traits::IdentityLookup, BuildStorage};

type Block = frame_system::mocking::MockBlock<Test>;

frame_support::construct_runtime!(
    pub enum Test {
        System: frame_system,
        PermissionedValidators: pallet_permissioned_validators,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type Block = Block;
    type AccountId = u64;
    type Lookup = IdentityLookup<u64>;
    type AccountData = ();
}

impl pallet_permissioned_validators::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type AdminOrigin = EnsureRoot<u64>;
    type MaxValidators = ConstU32<50>;
    type MaxInstitutions = ConstU32<100>;
    type WeightInfo = ();
    type ValidatorProposalSubmitter = ();
}

impl crate::WeightInfo for () {
    fn set_network_mode() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn propose_new_validator() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn add_validator() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn remove_validator() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn update_validator() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn register_institution() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn approve_institution() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn revoke_institution() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let mut ext: sp_io::TestExternalities = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap()
        .into();
    // Events are only emitted from block 1 onward.
    ext.execute_with(|| System::set_block_number(1));
    ext
}

// Unprivileged users
pub const ALICE: u64 = 1;
pub const BOB: u64 = 2;
pub const CHARLIE: u64 = 3;
pub const HOSPITAL_A: u64 = 10;
pub const HOSPITAL_B: u64 = 11;
#[allow(dead_code)]
pub const INSURER: u64 = 20;
