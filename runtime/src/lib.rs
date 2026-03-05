#![recursion_limit = "256"]

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

pub mod constants;
pub mod weights;

use frame_support::{
    construct_runtime, parameter_types,
    traits::{ConstBool, ConstU128, ConstU32, ConstU64, ConstU8, Everything},
    weights::{constants::WEIGHT_REF_TIME_PER_SECOND, Weight},
    PalletId,
};
use frame_system as system;
use sp_api::impl_runtime_apis;
use sp_core::{crypto::KeyTypeId, OpaqueMetadata};
use sp_runtime::{
    create_runtime_str, generic, impl_opaque_keys,
    traits::{BlakeTwo256, Block as BlockT, IdentifyAccount, Verify},
    transaction_validity::{TransactionSource, TransactionValidity},
    ApplyExtrinsicResult, MultiSignature,
};
use sp_std::prelude::*;
use sp_version::RuntimeVersion;

use codec::Encode;

pub use sp_consensus_aura::sr25519::AuthorityId as AuraId;
pub use sp_runtime::{MultiAddress, Perbill, Permill};

/// Import the template pallet.
pub use pallet_balances;
pub use pallet_timestamp;
pub use pallet_aura;
pub use pallet_sudo;

// Custom pallets
pub use pallet_patient_health_records;
pub use pallet_abena_coin;
pub use pallet_quantum_computing;
pub use pallet_patient_identity;
pub use pallet_health_record_hash;
pub use pallet_treatment_protocol;
pub use pallet_interoperability;
pub use pallet_governance;
pub use pallet_fee_management;
pub use pallet_access_control;
pub use pallet_account_management;
pub use pallet_data_separation;
pub use pallet_quantum_results;
pub use pallet_data_marketplace;
pub use pallet_permissioned_validators;
pub use pallet_private_channels;
pub use pallet_enterprise_identity;
pub use pallet_consortium_governance;

/// An index to a block.
pub type BlockNumber = u32;

/// Alias to 512-bit hash when used in the context of a transaction signature on the chain.
pub type Signature = MultiSignature;

/// Some way of identifying an account on the chain. We intentionally make it equivalent
/// to the public key of our transaction signing scheme.
pub type AccountId = <<Signature as Verify>::Signer as IdentifyAccount>::AccountId;

/// Balance of an account.
pub type Balance = u128;

/// Index of a transaction in the chain.
pub type Nonce = u32;

/// A hash of some data used by the chain.
pub type Hash = sp_core::H256;

/// Opaque types. These are used by the CLI to instantiate machinery that don't need to know
/// the specifics of the runtime. They can then be made to be agnostic over specific formats
/// of data like extrinsics, allowing for them to continue syncing the network through upgrades
/// to even the core data structures.
pub mod opaque {
    use super::*;

    pub use sp_runtime::OpaqueExtrinsic as UncheckedExtrinsic;

    /// Opaque block header type.
    pub type Header = generic::Header<BlockNumber, BlakeTwo256>;
    /// Opaque block type.
    pub type Block = generic::Block<Header, UncheckedExtrinsic>;
    /// Opaque block identifier type.
    pub type BlockId = generic::BlockId<Block>;
}

/// Session keys: just Aura for block production.
impl_opaque_keys! {
    pub struct SessionKeys {
        pub aura: AuraId,
    }
}

// To learn more about runtime versioning, see:
// https://docs.substrate.io/main-docs/build/upgrade#runtime-versioning
#[sp_version::runtime_version]
pub const VERSION: RuntimeVersion = RuntimeVersion {
    spec_name: create_runtime_str!("abena"),
    impl_name: create_runtime_str!("abena"),
    authoring_version: 1,
    spec_version: 1,
    impl_version: 1,
    apis: sp_version::create_apis_vec!([]),
    transaction_version: 1,
    state_version: 1,
};

/// This determines the average expected block time that we are targeting.
/// Blocks will be produced at a minimum duration defined by `SLOT_DURATION`.
/// `SLOT_DURATION` is picked up by `pallet_timestamp` which is in turn picked
/// up by `pallet_aura` to implement `fn slot_duration()`.
///
/// Change this to adjust the block time.
pub const MILLISECS_PER_BLOCK: u64 = 6000;

// NOTE: Currently it is not possible to change the slot duration after the chain has started.
//       Attempting to do so will brick block production.
pub const SLOT_DURATION: u64 = MILLISECS_PER_BLOCK;

// Time is measured by number of blocks.
pub const MINUTES: BlockNumber = 60_000 / (MILLISECS_PER_BLOCK as BlockNumber);
pub const HOURS: BlockNumber = MINUTES * 60;
pub const DAYS: BlockNumber = HOURS * 24;

/// The version information used to identify this runtime when compiled natively.
#[cfg(feature = "std")]
pub fn native_version() -> sp_version::NativeVersion {
    sp_version::NativeVersion {
        runtime_version: VERSION,
        can_author_with: Default::default(),
    }
}

const NORMAL_DISPATCH_RATIO: Perbill = Perbill::from_percent(75);

parameter_types! {
    pub const BlockHashCount: BlockNumber = 2400;
    pub const Version: sp_version::RuntimeVersion = VERSION;
    /// We allow for 2 seconds of compute with a 6 second average block time.
    pub BlockWeights: system::limits::BlockWeights = system::limits::BlockWeights::with_sensible_defaults(
        Weight::from_parts(2u64 * WEIGHT_REF_TIME_PER_SECOND, u64::MAX),
        NORMAL_DISPATCH_RATIO,
    );
    pub BlockLength: system::limits::BlockLength = system::limits::BlockLength::max_with_normal_ratio(5 * 1024 * 1024, NORMAL_DISPATCH_RATIO);
    pub const SS58Prefix: u8 = 42;
}

// Create the runtime by composing the FRAME pallets that were previously configured.
construct_runtime!(
    pub enum Runtime where
        Block = Block,
        NodeBlock = opaque::Block,
        UncheckedExtrinsic = UncheckedExtrinsic,
    {
        System: system,
        Timestamp: pallet_timestamp,
        Aura: pallet_aura,
        Balances: pallet_balances,
        TransactionPayment: pallet_transaction_payment,
        Sudo: pallet_sudo,

        // Custom pallets
        PatientHealthRecords: pallet_patient_health_records,
        AbenaCoin: pallet_abena_coin,
        QuantumComputing: pallet_quantum_computing,
        PatientIdentity: pallet_patient_identity,
        HealthRecordHash: pallet_health_record_hash,
        TreatmentProtocol: pallet_treatment_protocol,
        Interoperability: pallet_interoperability,
        Governance: pallet_governance,
        FeeManagement: pallet_fee_management,
        AccessControl: pallet_access_control,
        AccountManagement: pallet_account_management,
        DataSeparation: pallet_data_separation,
        QuantumResults: pallet_quantum_results,
        DataMarketplace: pallet_data_marketplace,
        PermissionedValidators: pallet_permissioned_validators,
        PrivateChannels: pallet_private_channels,
        EnterpriseIdentity: pallet_enterprise_identity,
        ConsortiumGovernance: pallet_consortium_governance,
    }
);

// Type aliases for compatibility with code that expects Call, Event, Origin.
pub type Call = RuntimeCall;
pub type Event = RuntimeEvent;
pub type Origin = RuntimeOrigin;

impl system::Config for Runtime {
    /// The basic call filter to use in dispatchable.
    type BaseCallFilter = Everything;
    /// The block type for the runtime.
    type Block = Block;
    /// Block & extrinsics weights: base values and limits.
    type BlockWeights = BlockWeights;
    /// The maximum length of a block (in bytes).
    type BlockLength = BlockLength;
    /// The identifier used to distinguish between accounts.
    type AccountId = AccountId;
    /// The aggregated dispatch type that is available for extrinsics.
    type RuntimeCall = Call;
    /// The lookup mechanism to get account ID from whatever is passed in dispatchers.
    type Lookup = sp_runtime::traits::AccountIdLookup<AccountId, ()>;
    /// The type for storing how many extrinsics an account has signed.
    type Nonce = Nonce;
    /// The type for hashing blocks and tries.
    type Hash = Hash;
    /// The hashing algorithm used.
    type Hashing = BlakeTwo256;
    /// The ubiquitous event type.
    type RuntimeEvent = Event;
    /// The ubiquitous origin type.
    type RuntimeOrigin = Origin;
    /// Maximum number of block number to block hash mappings to keep (oldest pruned first).
    type BlockHashCount = BlockHashCount;
    /// The weight of database operations that the runtime can invoke.
    type DbWeight = weights::RuntimeDbWeightGet;
    /// Version of the runtime.
    type Version = Version;
    /// Converts a module to the index of the module in `construct_runtime!`.
    type PalletInfo = PalletInfo;
    /// What to do if a new account is created.
    type OnNewAccount = ();
    /// What to do if an account is fully reaped from the system.
    type OnKilledAccount = ();
    /// The data to be stored in an account.
    type AccountData = pallet_balances::AccountData<Balance>;
    /// Weight information for the extrinsics of this pallet.
    type SystemWeightInfo = ();
    /// This is used as an identifier of the chain. 42 is the generic substrate prefix.
    type SS58Prefix = SS58Prefix;
    /// The set code logic, just the default since we're not a parachain.
    type OnSetCode = ();
    type MaxConsumers = frame_support::traits::ConstU32<16>;
    type RuntimeTask = RuntimeTask;
    type SingleBlockMigrations = ();
    type MultiBlockMigrator = ();
    type PreInherents = ();
    type PostInherents = ();
    type PostTransactions = ();
}

impl pallet_aura::Config for Runtime {
    type AuthorityId = AuraId;
    type MaxAuthorities = ConstU32<32>;
    type DisabledValidators = ();
    type AllowMultipleBlocksPerSlot = ConstBool<false>;
    type SlotDuration = ConstU64<{ SLOT_DURATION }>;
}

impl pallet_timestamp::Config for Runtime {
    /// A timestamp: milliseconds since the unix epoch.
    type Moment = u64;
    type OnTimestampSet = Aura;
    type MinimumPeriod = ConstU64<{ SLOT_DURATION / 2 }>;
    type WeightInfo = ();
}

parameter_types! {
    pub const ExistentialDeposit: u128 = 500;
    pub const MaxLocks: u32 = 50;
}

impl pallet_balances::Config for Runtime {
    type MaxLocks = MaxLocks;
    type MaxReserves = ();
    type ReserveIdentifier = [u8; 8];
    /// The type for recording an account's balance.
    type Balance = Balance;
    /// The ubiquitous event type.
    type RuntimeEvent = Event;
    type DustRemoval = ();
    /// The existence deposit.
    type ExistentialDeposit = ExistentialDeposit;
    /// Weight information for the extrinsics of this pallet.
    type WeightInfo = pallet_balances::weights::SubstrateWeight<Runtime>;
    type AccountStore = system::Pallet<Runtime>;
    type RuntimeHoldReason = ();
    type RuntimeFreezeReason = ();
    type FreezeIdentifier = ();
    type MaxFreezes = ConstU32<0>;
}

parameter_types! {
    pub const TransactionByteFee: Balance = 1;
}

impl pallet_transaction_payment::Config for Runtime {
    type RuntimeEvent = Event;
    type OnChargeTransaction = pallet_transaction_payment::CurrencyAdapter<Balances, ()>;
    type OperationalFeeMultiplier = ConstU8<5>;
    type WeightToFee = frame_support::weights::IdentityFee<Balance>;
    type LengthToFee = frame_support::weights::ConstantMultiplier<Balance, TransactionByteFee>;
    type FeeMultiplierUpdate = ();
}

parameter_types! {
    pub const PatientHealthRecordsPalletId: PalletId = PalletId(*b"abena/hr");
    pub const AbenaCoinPalletId: PalletId = PalletId(*b"abena/co");
    pub const QuantumComputingPalletId: PalletId = PalletId(*b"abena/qc");
    pub const PatientIdentityPalletId: PalletId = PalletId(*b"abena/pi");
    pub const TreatmentProtocolPalletId: PalletId = PalletId(*b"abena/tp");
    pub const MaxProvidersPerPatient: u32 = 50;
    pub const MaxConsentRecords: u32 = 10;
    pub const AbenaMinProposalDeposit: Balance = 1_000_000_000_000_000_000; // 1 ABENA
    pub const AbenaVotingPeriodBlocks: BlockNumber = 7200; // ~1 day at 12s/block
    pub const AbenaMinQuorumPermille: u32 = 100;  // 10%
    pub const AbenaApprovalThresholdPermille: u32 = 500; // majority
    pub const AbenaMaxSpendingHistoryEntries: u32 = 200;
}

impl pallet_patient_health_records::Config for Runtime {
    type RuntimeEvent = Event;
    type PalletId = PatientHealthRecordsPalletId;
    type WeightInfo = pallet_patient_health_records::weights::SubstrateWeight<Runtime>;
}

impl pallet_abena_coin::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type PalletId = AbenaCoinPalletId;
    type Currency = Balances;
    type WeightInfo = pallet_abena_coin::weights::SubstrateWeight<Runtime>;
    type MaxVestingSchedules = ConstU32<10>;
    type MaxReferralsPerAccount = ConstU32<100>;
    type SelfReportCooldownBlocks = ConstU32<100>;
    type MinProposalDeposit = AbenaMinProposalDeposit;
    type VotingPeriodBlocks = AbenaVotingPeriodBlocks;
    type MinQuorumPermille = AbenaMinQuorumPermille;
    type ApprovalThresholdPermille = AbenaApprovalThresholdPermille;
    type MaxSpendingHistoryEntries = AbenaMaxSpendingHistoryEntries;
}

impl pallet_quantum_computing::Config for Runtime {
    type RuntimeEvent = Event;
    type PalletId = QuantumComputingPalletId;
    type WeightInfo = pallet_quantum_computing::weights::SubstrateWeight<Runtime>;
}


impl pallet_sudo::Config for Runtime {
    type RuntimeEvent = Event;
    type RuntimeCall = Call;
    type WeightInfo = ();
}

impl pallet_patient_identity::Config for Runtime {
    type RuntimeEvent = Event;
    type MaxProvidersPerPatient = MaxProvidersPerPatient;
    type MaxConsentRecords = MaxConsentRecords;
    type WeightInfo = pallet_patient_identity::weights::SubstrateWeight<Runtime>;
}

impl pallet_health_record_hash::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = pallet_health_record_hash::weights::SubstrateWeight<Runtime>;
}

impl pallet_treatment_protocol::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = pallet_treatment_protocol::weights::SubstrateWeight<Runtime>;
}

impl pallet_interoperability::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = pallet_interoperability::weights::SubstrateWeight<Runtime>;
}

impl pallet_governance::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = pallet_governance::weights::SubstrateWeight<Runtime>;
}

impl pallet_fee_management::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = pallet_fee_management::weights::SubstrateWeight<Runtime>;
    type Currency = Balances;
}

impl pallet_access_control::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = pallet_access_control::weights::SubstrateWeight<Runtime>;
}

impl pallet_account_management::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = pallet_account_management::weights::SubstrateWeight<Runtime>;
    type Currency = Balances;
}

parameter_types! {
    pub const MinKAnonymity: u32 = 2;
    pub const MaxDataAssetsPerPatient: u32 = 64;
    pub const MaxAssetsToScan: u32 = 256;
    pub const DataPricingConfig: pallet_data_separation::DataPricing =
        pallet_data_separation::DataPricing {
            basic_vitals: 10,
            lab_results: 50,
            genetic_data: 500,
            longitudinal_data: 200,
            quantum_analyzed_data: 1_000,
            rare_disease_data: 5_000,
        };
    pub const ViolationPenalty: u128 = 1_000_000;
}

impl pallet_data_separation::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = pallet_data_separation::weights::SubstrateWeight<Runtime>;
    type Currency = Balances;
    type MinKAnonymity = MinKAnonymity;
    type MaxDataAssetsPerPatient = MaxDataAssetsPerPatient;
    type MaxAssetsToScan = MaxAssetsToScan;
    type DataPricing = DataPricingConfig;
    type ViolationPenalty = ViolationPenalty;
}

// ----------------------------------------------------------------------------
// Off-chain worker configuration
// ----------------------------------------------------------------------------
// Pallets with off-chain workers: PatientIdentity, DataMarketplace, QuantumResults.
// - QuantumResults: polls IBM Quantum API for job completion, submits attestations via
//   submit_attestation_unsigned (requires OffchainWorkerInterval and SendTransactionTypes).
// - DataMarketplace: dataset preparation, anonymization, IPFS; submits finalize via unsigned tx.
// - Executive::offchain_worker(header) runs all pallets' Hooks::offchain_worker each block.
// - sp_offchain::OffchainWorkerApi below exposes that to the node so workers are executed.
// ----------------------------------------------------------------------------

impl pallet_quantum_results::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = pallet_quantum_results::weights::SubstrateWeight<Runtime>;
    /// Run quantum results off-chain worker every N blocks (poll IBM, submit attestations).
    type OffchainWorkerInterval = frame_support::traits::ConstU32<10>;
}

impl pallet_data_marketplace::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = ();
}

parameter_types! {
    pub const MaxPermissionedValidators: u32 = 100;
    pub const MaxRegisteredInstitutions: u32 = 500;
}

parameter_types! {
    pub const MaxMembersPerChannel: u32 = 50;
    pub const MaxChannelsPerMember: u32 = 20;
    pub const MaxEntriesPerChannel: u32 = 10_000;
}

impl pallet_private_channels::Config for Runtime {
    type RuntimeEvent = Event;
    type MaxMembersPerChannel = MaxMembersPerChannel;
    type MaxChannelsPerMember = MaxChannelsPerMember;
    type MaxEntriesPerChannel = MaxEntriesPerChannel;
    type WeightInfo = pallet_private_channels::weights::SubstrateWeight<Runtime>;
}

impl pallet_enterprise_identity::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = pallet_enterprise_identity::weights::SubstrateWeight<Runtime>;
    type RegisterOrigin = frame_system::EnsureRoot<AccountId>;
}

parameter_types! {
    pub const ConsortiumVotingPeriod: u32 = 100_800; // ~7 days at 6s/block
    pub const ConsortiumEmergencyVotingPeriod: u32 = 14_400; // ~24 hours at 6s/block
    pub const ConsortiumApprovalThreshold: Permill = Permill::from_percent(67); // 2/3 for normal
    pub const ConsortiumEmergencyApprovalThreshold: Permill = Permill::from_percent(75); // 75% for emergency
}

impl pallet_consortium_governance::Config for Runtime {
    type RuntimeEvent = Event;
    type WeightInfo = pallet_consortium_governance::weights::SubstrateWeight<Runtime>;
    type RegisterOrigin = frame_system::EnsureRoot<AccountId>;
    type VotingPeriod = ConsortiumVotingPeriod;
    type EmergencyVotingPeriod = ConsortiumEmergencyVotingPeriod;
    type ApprovalThreshold = ConsortiumApprovalThreshold;
    type EmergencyApprovalThreshold = ConsortiumEmergencyApprovalThreshold;
}

/// Bridges propose_new_validator to consortium-governance: builds the add_validator call
/// and submits it via ConsortiumGovernance::propose for weighted consortium vote.
struct AbenaValidatorProposalSubmitter;

impl pallet_permissioned_validators::ValidatorProposalSubmitter<Runtime> for AbenaValidatorProposalSubmitter {
    fn submit_validator_proposal(
        origin: <Runtime as frame_system::Config>::RuntimeOrigin,
        candidate: AccountId,
        institution_name: sp_std::vec::Vec<u8>,
        role: pallet_permissioned_validators::ValidatorRole,
        consortium_id: u32,
    ) -> sp_runtime::DispatchResult {
        use pallet_consortium_governance::MaxProposalCallLen;
        use sp_runtime::BoundedVec;

        let inner_call = pallet_permissioned_validators::Call::<Runtime>::add_validator {
            validator: candidate,
            institution_name,
            role,
            consortium_id,
        };
        let runtime_call = Call::PermissionedValidators(inner_call);
        let encoded = runtime_call.encode();

        let bounded = BoundedVec::<u8, MaxProposalCallLen>::try_from(encoded)
        .map_err(|_| sp_runtime::DispatchError::Other("Proposal call too large"))?;
        pallet_consortium_governance::Pallet::<Runtime>::propose(
            origin,
            bounded,
            pallet_consortium_governance::ProposalPriority::Normal,
        )
    }
}

impl pallet_permissioned_validators::Config for Runtime {
    type RuntimeEvent = Event;
    /// Only Root (Sudo) or a future governance collective may change validators/mode.
    type AdminOrigin = frame_system::EnsureRoot<AccountId>;
    type MaxValidators = MaxPermissionedValidators;
    type MaxInstitutions = MaxRegisteredInstitutions;
    type WeightInfo = pallet_permissioned_validators::weights::SubstrateWeight<Runtime>;
    type ValidatorProposalSubmitter = AbenaValidatorProposalSubmitter;
}

/// The address format for describing accounts.
pub type Address = MultiAddress<AccountId, ()>;
/// Block header type as expected by this runtime.
pub type Header = generic::Header<BlockNumber, BlakeTwo256>;
/// Block type as expected by this runtime.
pub type Block = generic::Block<Header, UncheckedExtrinsic>;
/// A signed block.
pub type SignedBlock = generic::SignedBlock<Block>;
/// Block ID type as expected by this runtime.
pub type BlockId = generic::BlockId<Block>;
/// The SignedExtension to the basic transaction logic.
pub type SignedExtra = (
    system::CheckNonce<Runtime>,
    system::CheckWeight<Runtime>,
    pallet_transaction_payment::ChargeTransactionPayment<Runtime>,
);
/// Unchecked extrinsic type as expected by this runtime.
pub type UncheckedExtrinsic = generic::UncheckedExtrinsic<Address, Call, Signature, SignedExtra>;
/// The payload being signed in transactions.
pub type SignedPayload = generic::SignedPayload<Call, SignedExtra>;
/// Executive: handles dispatch to the various modules.
pub type Executive = frame_executive::Executive<
    Runtime,
    Block,
    frame_system::ChainContext<Runtime>,
    Runtime,
    AllPalletsWithSystem,
>;

// Off-chain workers submit unsigned transactions; these impls allow the runtime to accept them.
impl frame_system::offchain::SendTransactionTypes<pallet_data_marketplace::Call<Runtime>> for Runtime {
    type OverarchingCall = Call;
    type Extrinsic = UncheckedExtrinsic;
}
impl frame_system::offchain::SendTransactionTypes<pallet_quantum_results::Call<Runtime>> for Runtime {
    type OverarchingCall = Call;
    type Extrinsic = UncheckedExtrinsic;
}

#[cfg(feature = "runtime-benchmarks")]
#[macro_use]
extern crate frame_benchmarking;

#[cfg(feature = "runtime-benchmarks")]
mod benches {
    define_benchmarks!(
        [frame_benchmarking, BaselineBench::<Runtime>]
        [frame_system, SystemBench::<Runtime>]
        [pallet_balances, Balances]
        [pallet_patient_health_records, PatientHealthRecords]
        [pallet_abena_coin, AbenaCoin]
        [pallet_quantum_computing, QuantumComputing]
        [pallet_patient_identity, PatientIdentity]
        [pallet_health_record_hash, HealthRecordHash]
        [pallet_treatment_protocol, TreatmentProtocol]
        [pallet_interoperability, Interoperability]
        [pallet_governance, Governance]
        [pallet_fee_management, FeeManagement]
        [pallet_access_control, AccessControl]
        [pallet_account_management, AccountManagement]
        [pallet_permissioned_validators, PermissionedValidators]
        [pallet_private_channels, PrivateChannels]
        [pallet_enterprise_identity, EnterpriseIdentity]
    );
}

impl_runtime_apis! {
    impl sp_api::Core<Block> for Runtime {
        fn version() -> sp_version::RuntimeVersion {
            VERSION
        }

        fn execute_block(block: Block) {
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
            block: Block,
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

    /// Enable off-chain workers: node calls this each block; Executive runs all pallets' workers.
    impl sp_offchain::OffchainWorkerApi<Block> for Runtime {
        fn offchain_worker(header: &<Block as BlockT>::Header) {
            Executive::offchain_worker(header)
        }
    }

    impl sp_session::SessionKeys<Block> for Runtime {
        fn generate_session_keys(seed: Option<Vec<u8>>) -> Vec<u8> {
            SessionKeys::generate(seed)
        }

        fn decode_session_keys(
            encoded: Vec<u8>,
        ) -> Option<Vec<(Vec<u8>, KeyTypeId)>> {
            SessionKeys::decode_into_raw_public_keys(&encoded)
        }
    }

    impl sp_consensus_aura::AuraApi<Block, AuraId> for Runtime {
        fn slot_duration() -> sp_consensus_aura::SlotDuration {
            sp_consensus_aura::SlotDuration::from_millis(MILLISECS_PER_BLOCK)
        }

        fn authorities() -> Vec<AuraId> {
            pallet_aura::Authorities::<Runtime>::get().to_vec()
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
            frame_support::genesis_builder_helper::build_state::<RuntimeGenesisConfig>(json)
        }

        fn get_preset(name: &Option<sp_genesis_builder::PresetId>) -> Option<sp_std::vec::Vec<u8>> {
            frame_support::genesis_builder_helper::get_preset::<RuntimeGenesisConfig>(name, |_| None)
        }

        fn preset_names() -> sp_std::vec::Vec<sp_genesis_builder::PresetId> {
            vec![]
        }
    }
}

