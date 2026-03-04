use crate as pallet_private_channels;
use frame_support::{
    derive_impl,
    traits::ConstU32,
};
use sp_runtime::{traits::IdentityLookup, BuildStorage};

type Block = frame_system::mocking::MockBlock<Test>;

frame_support::construct_runtime!(
    pub enum Test {
        System: frame_system,
        PrivateChannels: pallet_private_channels,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type Block = Block;
    type AccountId = u64;
    type Lookup = IdentityLookup<u64>;
    type AccountData = ();
}

impl pallet_private_channels::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type MaxMembersPerChannel = ConstU32<20>;
    type MaxChannelsPerMember = ConstU32<10>;
    type MaxEntriesPerChannel = ConstU32<100>;
    type WeightInfo = ();
}

impl crate::WeightInfo for () {
    fn create_channel() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn add_member() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn remove_member() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn update_member_role() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn post_data() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn share_data_cross_channel() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
    fn close_channel() -> frame_support::weights::Weight { frame_support::weights::Weight::zero() }
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let mut ext: sp_io::TestExternalities = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap()
        .into();
    ext.execute_with(|| System::set_block_number(1));
    ext
}

// Test accounts
pub const ALICE: u64 = 1;    // Hospital A admin
pub const BOB: u64 = 2;      // Hospital A staff
pub const CHARLIE: u64 = 3;  // Insurer
#[allow(dead_code)]
pub const DAVE: u64 = 4;     // Researcher
pub const EVE: u64 = 5;      // Hospital B admin
pub const FRANK: u64 = 6;    // Patient
