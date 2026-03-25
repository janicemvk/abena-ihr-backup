//! ABENA IHR Runtime
//! DK Technologies, Inc. — Integrative Health Record
//! Quantum-powered healthcare blockchain on Substrate/Polkadot SDK
//!
//! ABENA Coin: Native currency of the ABENA blockchain
//!   Symbol:   ABENA
//!   Decimals: 12
//!   Supply:   1,000,000,000 ABENA

#![cfg_attr(not(feature = "std"), no_std)]
// Required for Substrate runtimes
#![recursion_limit = "256"]

// Make the WASM binary available.
#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

// ============================================================
// External crate imports
// ============================================================
use frame_support::genesis_builder_helper::{build_state, get_preset};
use frame_support::{
    construct_runtime, parameter_types,
    traits::{ConstBool, ConstU32, ConstU64, ConstU8, Everything},
    weights::{constants::WEIGHT_REF_TIME_PER_SECOND, Weight},
    PalletId,
};
use frame_system as system;
use sp_api::impl_runtime_apis;
use sp_consensus_aura::sr25519::AuthorityId as AuraId;
use sp_consensus_grandpa::ed25519::AuthorityId as GrandpaId;
use sp_core::{crypto::KeyTypeId, OpaqueMetadata};
use sp_runtime::{
    create_runtime_str, generic, impl_opaque_keys,
    traits::{BlakeTwo256, Block as BlockT, IdentifyAccount, Verify},
    transaction_validity::{TransactionSource, TransactionValidity},
    ApplyExtrinsicResult, MultiSignature,
};
#[cfg(not(feature = "std"))]
use sp_std::prelude::*;
#[cfg(feature = "std")]
use sp_version::NativeVersion;
use sp_version::RuntimeVersion;

pub use pallet_balances;
pub use pallet_timestamp;
pub use pallet_aura;
pub use pallet_sudo;
pub use pallet_abena_rewards;
pub use pallet_abena_fee_abstraction;

pub use sp_runtime::{MultiAddress, Perbill, Permill};

// ============================================================
// ABENA COIN — Currency Constants
// ============================================================
/// All currency amounts are in planck units (1 ABENA = 1_000_000_000_000 planck)
pub mod currency {
    use super::Balance;

    /// 1 ABENA Coin = 10^12 planck (12 decimal places, Substrate standard)
    pub const ABENA: Balance = 1_000_000_000_000;

    /// 0.001 ABENA
    pub const MILLI_ABENA: Balance = ABENA / 1_000;

    /// 0.000001 ABENA
    pub const MICRO_ABENA: Balance = ABENA / 1_000_000;

    /// Existential deposit — minimum balance to keep an account alive
    /// Set to 0.001 ABENA (patients don't accidentally lose tiny balances)
    pub const EXISTENTIAL_DEPOSIT: Balance = MILLI_ABENA;

    /// Transaction base fee
    pub const TRANSACTION_BASE_FEE: Balance = MILLI_ABENA;

    /// Total supply: 1,000,000,000 ABENA
    pub const TOTAL_SUPPLY: Balance = 1_000_000_000u128 * ABENA;
}

// ============================================================
// Core Type Aliases
// ============================================================

/// An index to a block.
pub type BlockNumber = u32;

/// Alias for the ABENA Coin balance type.
/// u128 supports values up to ~3.4 × 10^38 planck — far beyond total supply.
pub type Balance = u128;

/// Alias to 512-bit hash when used in the context of a transaction signature on the chain.
pub type Signature = MultiSignature;

/// Some way of identifying an account on the chain.
pub type AccountId = <<Signature as Verify>::Signer as IdentifyAccount>::AccountId;

/// Index of a transaction in the chain.
pub type Nonce = u32;

/// A hash of some data used by the chain.
pub type Hash = sp_core::H256;

/// The type for storing how many extrinsics an account has signed.
pub type Index = u32;

// ============================================================
// Opaque types — used for the node side
// ============================================================
pub mod opaque {
    use super::*;

    pub use sp_runtime::OpaqueExtrinsic as UncheckedExtrinsic;

    pub type Header = generic::Header<BlockNumber, BlakeTwo256>;
    pub type Block = generic::Block<Header, UncheckedExtrinsic>;
    pub type BlockId = generic::BlockId<Block>;

    impl_opaque_keys! {
        pub struct SessionKeys {
            pub aura: AuraId,
            pub grandpa: GrandpaId,
        }
    }
}

// ============================================================
// Runtime Version
// ============================================================
#[sp_version::runtime_version]
pub const VERSION: RuntimeVersion = RuntimeVersion {
    spec_name: create_runtime_str!("abena-ihr"),
    impl_name: create_runtime_str!("abena-ihr"),
    authoring_version: 1,
    // Increment spec_version after any runtime logic change
    spec_version: 100,
    impl_version: 1,
    apis: sp_version::create_apis_vec!([]),
    transaction_version: 1,
    system_version: 1,
};

/// The version information used to identify this runtime when compiled natively.
#[cfg(feature = "std")]
pub fn native_version() -> NativeVersion {
    NativeVersion {
        runtime_version: VERSION,
        can_author_with: Default::default(),
    }
}

// ============================================================
// Block & Weight Configuration
// ============================================================
pub const MILLISECS_PER_BLOCK: u64 = 6000;
pub const SLOT_DURATION: u64 = MILLISECS_PER_BLOCK;

pub const MINUTES: BlockNumber = 60_000 / (MILLISECS_PER_BLOCK as BlockNumber);
pub const HOURS: BlockNumber = MINUTES * 60;
pub const DAYS: BlockNumber = HOURS * 24;

const NORMAL_DISPATCH_RATIO: Perbill = Perbill::from_percent(75);

parameter_types! {
    pub const BlockHashCount: BlockNumber = 2400;
    pub const Version: RuntimeVersion = VERSION;
    pub BlockWeights: system::limits::BlockWeights = system::limits::BlockWeights::with_sensible_defaults(
        Weight::from_parts(2u64 * WEIGHT_REF_TIME_PER_SECOND, u64::MAX),
        NORMAL_DISPATCH_RATIO,
    );
    pub BlockLength: system::limits::BlockLength = system::limits::BlockLength::max_with_normal_ratio(5 * 1024 * 1024, NORMAL_DISPATCH_RATIO);
    pub const SS58Prefix: u8 = 42; // Generic Substrate prefix (change to custom for mainnet)
}

// ============================================================
// ABENA COIN — pallet_balances existential deposit
// ============================================================
parameter_types! {
    /// Minimum balance to keep an account alive on the ABENA chain.
    /// Set to 0.001 ABENA. Patients with small balances won't lose their accounts.
    pub const ExistentialDeposit: Balance = currency::EXISTENTIAL_DEPOSIT;
    pub const MaxLocks: u32 = 50;
}

parameter_types! {
    pub const TransactionByteFee: Balance = 1;
}

// ============================================================
// construct_runtime! — Assemble the ABENA runtime
// ============================================================
construct_runtime!(
    pub enum Runtime where
        Block = Block,
        NodeBlock = opaque::Block,
        UncheckedExtrinsic = UncheckedExtrinsic,
    {
        // ── Core system ──────────────────────────────────────────
        System: system,
        Timestamp: pallet_timestamp,
        Aura: pallet_aura,
        Grandpa: pallet_grandpa,

        // ── ABENA COIN ───────────────────────────────────────────
        Balances: pallet_balances,              // ← Native ABENA Coin
        TransactionPayment: pallet_transaction_payment,

        // ── ABENA Health Rewards ─────────────────────────────────
        AbenaRewards: pallet_abena_rewards,     // ← Health incentive minting

        // ── Gasless model for patients ───────────────────────────
        AbenaFeeAbstraction: pallet_abena_fee_abstraction,

        // ── Admin (testnet only) ─────────────────────────────────
        Sudo: pallet_sudo,
    }
);

pub type Call = RuntimeCall;
pub type Event = RuntimeEvent;
pub type Origin = RuntimeOrigin;

// ============================================================
// frame_system — System pallet
// ============================================================
impl system::Config for Runtime {
    type BaseCallFilter = Everything;
    type Block = Block;
    type BlockWeights = BlockWeights;
    type BlockLength = BlockLength;
    type DbWeight = frame_support::weights::constants::RocksDbWeight;
    type RuntimeOrigin = Origin;
    type RuntimeCall = Call;
    type Nonce = Nonce;
    type Hash = Hash;
    type Hashing = BlakeTwo256;
    type AccountId = AccountId;
    type Lookup = sp_runtime::traits::AccountIdLookup<AccountId, ()>;
    type Block = Block;
    type RuntimeEvent = Event;
    type BlockHashCount = BlockHashCount;
    type Version = Version;
    type PalletInfo = PalletInfo;
    // AccountData holds ABENA Coin balances (free, reserved, frozen)
    type AccountData = pallet_balances::AccountData<Balance>;
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type SS58Prefix = SS58Prefix;
    type OnSetCode = ();
    type MaxConsumers = ConstU32<16>;
    type RuntimeTask = RuntimeTask;
    type SingleBlockMigrations = ();
    type MultiBlockMigrator = ();
    type PreInherents = ();
    type PostInherents = ();
    type PostTransactions = ();
    type ExtensionsWeightInfo = ();
}

// ============================================================
// pallet_grandpa — BFT finality gadget
// ============================================================
impl pallet_grandpa::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = ();
}

// ============================================================
// pallet_aura — Block authorship
// ============================================================
impl pallet_aura::Config for Runtime {
    type AuthorityId = AuraId;
    type DisabledValidators = ();
    type MaxAuthorities = ConstU32<32>;
    type AllowMultipleBlocksPerSlot = ConstBool<false>;
    type SlotDuration = pallet_aura::MinimumPeriodTimesTwo<Runtime>;
}

// ============================================================
// pallet_timestamp
// ============================================================
impl pallet_timestamp::Config for Runtime {
    type Moment = u64;
    type OnTimestampSet = Aura;
    type MinimumPeriod = ConstU64<{ SLOT_DURATION / 2 }>; // 3 seconds (6s block time / 2)
    type WeightInfo = ();
}

// ============================================================
// pallet_balances — ABENA COIN CONFIGURATION
// ============================================================
impl pallet_balances::Config for Runtime {
    type MaxLocks = MaxLocks;
    type MaxReserves = ();
    type ReserveIdentifier = [u8; 8];

    /// Balance type: u128 supports 1 billion ABENA × 10^12 planck per ABENA
    type Balance = Balance;

    type RuntimeEvent = Event;

    /// Dust removal: burn tiny balances below existential deposit
    type DustRemoval = ();

    type ExistentialDeposit = ExistentialDeposit;

    /// Store account data in the System pallet (standard approach)
    type AccountStore = system::Pallet<Runtime>;

    type WeightInfo = pallet_balances::weights::SubstrateWeight<Runtime>;

    type RuntimeHoldReason = ();
    type RuntimeFreezeReason = ();
    type FreezeIdentifier = ();
    type MaxFreezes = ConstU32<0>;
    type DoneSlashHandler = ();
}

// ============================================================
// pallet_transaction_payment — Fee handling
// ============================================================
impl pallet_transaction_payment::Config for Runtime {
    type RuntimeEvent = Event;
    type OnChargeTransaction = pallet_transaction_payment::FungibleAdapter<Balances, ()>;
    type OperationalFeeMultiplier = ConstU8<5>;
    type WeightToFee = frame_support::weights::IdentityFee<Balance>;
    type LengthToFee = frame_support::weights::ConstantMultiplier<Balance, TransactionByteFee>;
    type FeeMultiplierUpdate = ();
    type WeightInfo = pallet_transaction_payment::weights::SubstrateWeight<Runtime>;
}

// ============================================================
// pallet_sudo — Admin control (testnet only — remove for mainnet)
// ============================================================
impl pallet_sudo::Config for Runtime {
    type RuntimeEvent = Event;
    type RuntimeCall = Call;
    type WeightInfo = ();
}

parameter_types! {
    pub const AbenaMaxActionsPerBlock: u32 = 100;
}

// ============================================================
// pallet_abena_rewards — Health reward coin minting
// ============================================================
impl pallet_abena_rewards::Config for Runtime {
    type RuntimeEvent = Event;
    type Currency = Balances;
    type AuthorizedOracle = frame_system::EnsureRoot<AccountId>;
    type MaxActionsPerBlock = AbenaMaxActionsPerBlock;
    type WeightInfo = pallet_abena_rewards::weights::SubstrateWeight<Runtime>;
}

// ============================================================
// pallet_abena_fee_abstraction — Gasless model for patients
// ============================================================
impl pallet_abena_fee_abstraction::Config for Runtime {
    type RuntimeEvent = Event;
    type AdminOrigin = frame_system::EnsureRoot<AccountId>;
    type WeightInfo = pallet_abena_fee_abstraction::weights::SubstrateWeight<Runtime>;
}

// ============================================================
// Block & Extrinsic types
// ============================================================
pub type Address = MultiAddress<AccountId, ()>;
pub type Header = generic::Header<BlockNumber, BlakeTwo256>;
pub type Block = generic::Block<Header, UncheckedExtrinsic>;
pub type SignedBlock = generic::SignedBlock<Block>;
pub type BlockId = generic::BlockId<Block>;
pub type SignedExtra = (
    system::CheckNonce<Runtime>,
    system::CheckWeight<Runtime>,
    pallet_transaction_payment::ChargeTransactionPayment<Runtime>,
);
pub type UncheckedExtrinsic = generic::UncheckedExtrinsic<Address, Call, Signature, SignedExtra>;
pub type SignedPayload = generic::SignedPayload<Call, SignedExtra>;
pub type Executive = frame_executive::Executive<
    Runtime,
    Block,
    frame_system::ChainContext<Runtime>,
    Runtime,
    AllPalletsWithSystem,
>;

// ============================================================
// Runtime API Implementations
// ============================================================
impl_runtime_apis! {
    impl sp_api::Core<Block> for Runtime {
        fn version() -> RuntimeVersion {
            VERSION
        }
        fn execute_block(block: <Block as BlockT>::LazyBlock) {
            Executive::execute_block(block);
        }
        fn initialize_block(header: &<Block as BlockT>::Header) -> sp_runtime::ExtrinsicInclusionMode {
            Executive::initialize_block(header)
        }
    }

    impl sp_api::Metadata<Block> for Runtime {
        fn metadata() -> OpaqueMetadata {
            OpaqueMetadata::new(Runtime::metadata().into())
        }
        fn metadata_at_version(version: u32) -> Option<OpaqueMetadata> {
            Runtime::metadata_at_version(version)
        }
        fn metadata_versions() -> sp_std::vec::Vec<u32> {
            Runtime::metadata_versions()
        }
    }

    impl sp_block_builder::BlockBuilder<Block> for Runtime {
        fn apply_extrinsic(extrinsic: <Block as BlockT>::Extrinsic) -> ApplyExtrinsicResult {
            Executive::apply_extrinsic(extrinsic)
        }
        fn finalize_block() -> <Block as BlockT>::Header {
            Executive::finalize_block()
        }
        fn inherent_extrinsics(data: sp_inherents::InherentData) -> Vec<<Block as BlockT>::Extrinsic> {
            data.create_extrinsics()
        }
        fn check_inherents(
            block: <Block as BlockT>::LazyBlock,
            data: sp_inherents::InherentData,
        ) -> sp_inherents::CheckInherentsResult {
            data.check_extrinsics(&block)
        }
    }

    impl sp_transaction_pool::runtime_api::TaggedTransactionQueue<Block> for Runtime {
        fn validate_transaction(
            source: TransactionSource,
            tx: <Block as BlockT>::Extrinsic,
            block_hash: <Block as BlockT>::Hash,
        ) -> TransactionValidity {
            Executive::validate_transaction(source, tx, block_hash)
        }
    }

    impl sp_offchain::OffchainWorkerApi<Block> for Runtime {
        fn offchain_worker(header: &<Block as BlockT>::Header) {
            Executive::offchain_worker(header)
        }
    }

    impl sp_session::SessionKeys<Block> for Runtime {
        fn generate_session_keys(seed: Option<Vec<u8>>) -> Vec<u8> {
            opaque::SessionKeys::generate(seed)
        }
        fn decode_session_keys(
            encoded: Vec<u8>,
        ) -> Option<Vec<(Vec<u8>, KeyTypeId)>> {
            opaque::SessionKeys::decode_into_raw_public_keys(&encoded)
        }
    }

    impl sp_consensus_aura::AuraApi<Block, AuraId> for Runtime {
        fn slot_duration() -> sp_consensus_aura::SlotDuration {
            sp_consensus_aura::SlotDuration::from_millis(Aura::slot_duration())
        }
        fn authorities() -> Vec<AuraId> {
            pallet_aura::Authorities::<Runtime>::get().into_inner()
        }
    }

    impl sp_consensus_grandpa::GrandpaApi<Block> for Runtime {
        fn grandpa_authorities() -> sp_consensus_grandpa::AuthorityList {
            Grandpa::grandpa_authorities()
        }
        fn current_set_id() -> sp_consensus_grandpa::SetId {
            Grandpa::current_set_id()
        }
    }

    impl frame_system_rpc_runtime_api::AccountNonceApi<Block, AccountId, Nonce> for Runtime {
        fn account_nonce(account: AccountId) -> Nonce {
            System::account_nonce(account)
        }
    }

    impl pallet_transaction_payment_rpc_runtime_api::TransactionPaymentApi<Block, Balance> for Runtime {
        fn query_info(
            uxt: <Block as BlockT>::Extrinsic,
            len: u32,
        ) -> pallet_transaction_payment_rpc_runtime_api::RuntimeDispatchInfo<Balance> {
            TransactionPayment::query_info(uxt, len)
        }
        fn query_fee_details(
            uxt: <Block as BlockT>::Extrinsic,
            len: u32,
        ) -> pallet_transaction_payment::FeeDetails<Balance> {
            TransactionPayment::query_fee_details(uxt, len)
        }
        fn query_weight_to_fee(weight: Weight) -> Balance {
            TransactionPayment::weight_to_fee(weight)
        }
        fn query_length_to_fee(length: u32) -> Balance {
            TransactionPayment::length_to_fee(length)
        }
    }

    impl sp_genesis_builder::GenesisBuilder<Block> for Runtime {
        fn build_state(json: sp_std::vec::Vec<u8>) -> sp_genesis_builder::Result {
            build_state::<RuntimeGenesisConfig>(json)
        }

        fn get_preset(id: &Option<sp_genesis_builder::PresetId>) -> Option<sp_std::vec::Vec<u8>> {
            get_preset::<RuntimeGenesisConfig>(id, |_| None)
        }

        fn preset_names() -> sp_std::vec::Vec<sp_genesis_builder::PresetId> {
            Default::default()
        }
    }
}
