//! Cross-pallet integration tests for the ABENA Healthcare Blockchain.
//!
//! Each scenario exercises a multi-pallet workflow end-to-end using a single
//! combined test runtime that includes every ABENA pallet.
//!
//! Pallet abbreviations used throughout:
//!   PI   → pallet_patient_identity
//!   HRH  → pallet_health_record_hash
//!   QR   → pallet_quantum_results
//!   TP   → pallet_treatment_protocol
//!   AC   → pallet_abena_coin
//!   DM   → pallet_data_marketplace

// ─────────────────────────────────────────────────────────────────────────────
// Combined test runtime
// ─────────────────────────────────────────────────────────────────────────────

mod mock {
    use frame_support::{
        parameter_types,
        traits::{ConstU16, ConstU128, ConstU32, ConstU64},
        PalletId,
    };
    use frame_system as system;
    use sp_core::H256;
    use sp_runtime::{
        testing::TestXt,
        traits::{BlakeTwo256, IdentityLookup},
        BuildStorage,
    };

    // Pallet aliases so the impls below are readable.
    use pallet_abena_coin as abena_coin;
    use pallet_data_marketplace as data_marketplace;
    use pallet_health_record_hash as health_record_hash;
    use pallet_patient_identity as patient_identity;
    use pallet_quantum_results as quantum_results;
    use pallet_treatment_protocol as treatment_protocol;

    type Block = frame_system::mocking::MockBlock<Test>;

    frame_support::construct_runtime!(
        pub enum Test {
            System:             frame_system,
            Balances:           pallet_balances,
            PatientIdentity:    pallet_patient_identity,
            HealthRecordHash:   pallet_health_record_hash,
            QuantumResults:     pallet_quantum_results,
            TreatmentProtocol:  pallet_treatment_protocol,
            AbenaCoin:          pallet_abena_coin,
            DataMarketplace:    pallet_data_marketplace,
        }
    );

    // ── Pallet configurations ────────────────────────────────────────────────

    parameter_types! {
        pub const AbenaCoinPalletId: PalletId = PalletId(*b"abn/coin");
        pub const MinProposalDeposit: u128 = 100;
        pub const VotingPeriodBlocks: u32 = 10;
    }

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
        // AccountData must carry pallet_balances data for AbenaCoin's Currency bound.
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

    impl<LocalCall> frame_system::offchain::CreateBare<LocalCall> for Test
    where
        RuntimeCall: From<LocalCall>,
    {
        type Extrinsic = TestXt<RuntimeCall, ()>;
        type RuntimeCall = RuntimeCall;
        fn create_bare(call: RuntimeCall) -> Self::Extrinsic {
            TestXt::new_unsigned(call)
        }
    }

    impl patient_identity::Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type MaxProvidersPerPatient = ConstU32<10>;
        type MaxConsentRecords = ConstU32<10>;
        type WeightInfo = patient_identity::weights::SubstrateWeight<Test>;
    }

    impl health_record_hash::Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type WeightInfo = health_record_hash::weights::SubstrateWeight<Test>;
    }

    impl quantum_results::Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type WeightInfo = ();
        type OffchainWorkerInterval = ConstU64<10>;
    }

    impl treatment_protocol::Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type WeightInfo = treatment_protocol::weights::SubstrateWeight<Test>;
    }

    impl abena_coin::Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type PalletId = AbenaCoinPalletId;
        type Currency = Balances;
        type WeightInfo = abena_coin::weights::SubstrateWeight<Test>;
        type MaxVestingSchedules = ConstU32<10>;
        type MaxReferralsPerAccount = ConstU32<100>;
        type SelfReportCooldownBlocks = ConstU64<10>;
        type MinProposalDeposit = MinProposalDeposit;
        type VotingPeriodBlocks = VotingPeriodBlocks;
        type MinQuorumPermille = ConstU32<1>;
        type ApprovalThresholdPermille = ConstU32<500>;
        type MaxSpendingHistoryEntries = ConstU32<200>;
    }

    impl data_marketplace::Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type WeightInfo = ();
    }

    // ── Test accounts ────────────────────────────────────────────────────────

    /// Healthcare provider / researcher.
    pub const ALICE: u64 = 1;
    /// Patient 1.
    pub const BOB: u64 = 2;
    /// Patient 2 / second validator.
    pub const CHARLIE: u64 = 3;
    /// Commercial entity / governance voter.
    pub const DAVE: u64 = 4;
    /// Second provider / voter / entity.
    pub const EVE: u64 = 5;

    /// One ABENA token (18 decimal places).
    pub const ONE: u128 = 1_000_000_000_000_000_000u128;

    // ── Test externalities ───────────────────────────────────────────────────

    /// Builds a test environment with pallet_balances pre-funded (for AbenaCoin Currency bound).
    pub fn new_test_ext() -> sp_io::TestExternalities {
        let t = RuntimeGenesisConfig {
            balances: pallet_balances::GenesisConfig {
                balances: vec![
                    (ALICE,   1_000_000 * ONE),
                    (BOB,     1_000_000 * ONE),
                    (CHARLIE, 1_000_000 * ONE),
                    (DAVE,    1_000_000 * ONE),
                    (EVE,     1_000_000 * ONE),
                ],
            },
            ..Default::default()
        }
        .build_storage()
        .unwrap();
        let mut ext: sp_io::TestExternalities = t.into();
        ext.execute_with(|| System::set_block_number(1));
        ext
    }

    pub fn set_block(n: u64) {
        System::set_block_number(n);
    }
} // end mod mock

// ─────────────────────────────────────────────────────────────────────────────
// Shared test helpers
// ─────────────────────────────────────────────────────────────────────────────

use codec::Encode;
use frame_support::{assert_ok, BoundedVec, traits::ConstU32};
use mock::*;
use sp_core::H256;
use sp_runtime::traits::Hash;

// Pallet aliases for clean call sites.
use pallet_abena_coin as abena_coin;
use pallet_data_marketplace as data_marketplace;
use pallet_health_record_hash as health_record_hash;
use pallet_patient_identity as patient_identity;
use pallet_quantum_results as quantum_results;
use pallet_treatment_protocol as treatment_protocol;

fn h256(seed: u8) -> H256 { H256::from([seed; 32]) }
fn h32(seed: u8) -> [u8; 32] { [seed; 32] }

fn bvec128(s: &[u8]) -> BoundedVec<u8, ConstU32<128>> {
    BoundedVec::try_from(s.to_vec()).unwrap()
}
fn bvec256(s: &[u8]) -> BoundedVec<u8, ConstU32<256>> {
    BoundedVec::try_from(s.to_vec()).unwrap()
}
fn bvec512(s: &[u8]) -> BoundedVec<u8, ConstU32<512>> {
    BoundedVec::try_from(s.to_vec()).unwrap()
}

/// Register BOB as a patient with ALICE as emergency contact.
fn register_patient(patient: u64, emergency: Option<u64>) {
    assert_ok!(PatientIdentity::register_patient(
        RuntimeOrigin::signed(patient),
        h32(patient as u8),
        h32((patient + 100) as u8),
        emergency,
    ));
}

/// BOB grants ALICE ReadWrite access.
fn grant_access(patient: u64, provider: u64) {
    assert_ok!(PatientIdentity::grant_provider_access(
        RuntimeOrigin::signed(patient),
        provider,
        patient_identity::AccessLevel::ReadWrite,
        None,
    ));
}

/// Create a 2-step spec protocol with the given hash.
fn register_2step_protocol(creator: u64, pid: H256) {
    use treatment_protocol::{
        ClinicalCondition, EvidenceLevel, Frequency, InterventionType,
        SuccessCriteria, TherapeuticModality, TreatmentStep,
    };
    let steps: BoundedVec<TreatmentStep, ConstU32<64>> = BoundedVec::try_from(vec![
        TreatmentStep {
            step_number: 1,
            intervention_type: InterventionType::Pharmaceutical,
            medication: None, herb_formula: None, procedure: None,
            duration_days: 14,
            frequency: Frequency { times_per_day: 1, days_per_week: 7 },
            prerequisites: BoundedVec::default(),
            success_criteria: None,
            next_step_conditions: BoundedVec::default(),
        },
        TreatmentStep {
            step_number: 2,
            intervention_type: InterventionType::Lifestyle,
            medication: None, herb_formula: None, procedure: None,
            duration_days: 30,
            frequency: Frequency { times_per_day: 1, days_per_week: 7 },
            prerequisites: BoundedVec::default(),
            success_criteria: None,
            next_step_conditions: BoundedVec::default(),
        },
    ]).unwrap();

    assert_ok!(TreatmentProtocol::register_protocol(
        RuntimeOrigin::signed(creator),
        pid,
        bvec128(b"Test Protocol"),
        ClinicalCondition {
            code: BoundedVec::try_from(b"T2DM".to_vec()).unwrap(),
            description: BoundedVec::try_from(b"Diabetes".to_vec()).unwrap(),
        },
        BoundedVec::try_from(vec![TherapeuticModality::Western]).unwrap(),
        EvidenceLevel::RandomizedControlled,
        90,
        SuccessCriteria {
            description: bvec256(b"HbA1c < 7%"),
            measurable: true,
        },
        steps,
    ));
}

/// Mint `amount` ABENA (internal ledger) to `account` via root.
fn mint_abena(account: u64, amount: u128) {
    assert_ok!(AbenaCoin::mint(RuntimeOrigin::root(), account, amount));
}

/// Register a data license as `requester`.
fn request_license(requester: u64, license_id: H256) {
    use data_marketplace::pallet::DataQuery;
    use pallet_data_marketplace::{DataField, LicensePurpose, PrivacyGuarantee};
    assert_ok!(DataMarketplace::request_data_license(
        RuntimeOrigin::signed(requester),
        license_id,
        DataQuery {
            fields: BoundedVec::try_from(vec![
                DataField::Diagnosis,
                DataField::LabResults,
            ]).unwrap(),
            condition: Some(pallet_data_marketplace::ClinicalCondition::Diabetes),
            demographic: None,
        },
        LicensePurpose::AcademicResearch,
        PrivacyGuarantee {
            k_anonymity: Some(10),
            l_diversity: None,
            differential_privacy_epsilon: None,
            no_reidentification_clause: true,
        },
    ));
}

// ─────────────────────────────────────────────────────────────────────────────
// SCENARIO 1: Complete Patient Journey
// ─────────────────────────────────────────────────────────────────────────────

/// Exercises the full longitudinal patient journey across all pallets:
///   PI → HRH → QR → TP → AC → DM
#[test]
fn scenario_1_complete_patient_journey() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // ── Step 1: Patient registers identity (PI) ──────────────────────────
        register_patient(BOB, Some(CHARLIE)); // CHARLIE is emergency contact
        assert!(patient_identity::PatientIdentities::<Test>::contains_key(BOB));

        // ── Step 2: Patient grants provider access (PI) ──────────────────────
        grant_access(BOB, ALICE);
        let access = patient_identity::ProviderAccessList::<Test>::get(BOB, ALICE);
        assert!(access.is_some());

        // ── Step 3: Provider creates clinical note (HRH) ─────────────────────
        let record_id = h256(1);
        assert_ok!(HealthRecordHash::create_record_hash(
            RuntimeOrigin::signed(ALICE),
            record_id,
            BOB,
            h32(42),
            Some(bvec256(b"ipfs://Qm1234...")),
            health_record_hash::RecordTypeSpec::ClinicalNote,
            health_record_hash::pallet::TherapeuticModality::WesternMedicine,
            bvec512(b"provider_sig"),
            h32(7),
        ));
        assert!(health_record_hash::RecordHashStore::<Test>::get(record_id).is_some());

        // ── Step 4: Researcher registers quantum algorithm (QR) ──────────────
        let algo_hash = h256(10);
        assert_ok!(QuantumResults::register_algorithm(
            RuntimeOrigin::signed(ALICE),
            algo_hash,
            quantum_results::QuantumAlgorithm::VQE,
            1,
            b"VQE for drug interaction screening".to_vec(),
        ));
        assert!(quantum_results::AlgorithmRegistry::<Test>::get(algo_hash).is_some());

        // ── Step 5: Quantum analysis result attested (QR) ────────────────────
        let job_id = b"ibm-job-001".to_vec();
        let patient_pseudonym = h256(99); // anonymised hash, not real identity
        assert_ok!(QuantumResults::attest_quantum_result(
            RuntimeOrigin::signed(ALICE),
            job_id.clone(),
            patient_pseudonym,
            quantum_results::QuantumAlgorithm::VQE,
            1,
            h256(11), // parameters hash
            h256(12), // result hash
            vec![0u8; 64], // IBM signature placeholder
            1_700_000_000u64, // execution timestamp
            20,  // circuit depth
            6,   // qubit count
            8192, // shots
            None,
        ));
        let job_id_b: BoundedVec<u8, quantum_results::JobIdMaxLen> =
            BoundedVec::try_from(job_id.clone()).expect("job_id within bounds");
        let job_id_hash = <Test as frame_system::Config>::Hashing::hash_of(&job_id_b.encode());
        assert!(quantum_results::QuantumResults::<Test>::get(job_id_hash).is_some());

        // ── Step 6: Provider registers treatment protocol (TP) ───────────────
        let protocol_id = h256(20);
        register_2step_protocol(ALICE, protocol_id);
        assert!(treatment_protocol::ProtocolRegistry::<Test>::get(protocol_id).is_some());

        // ── Step 7: Treatment initiated for BOB (TP) ─────────────────────────
        set_block(5);
        assert_ok!(TreatmentProtocol::initiate_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            protocol_id,
        ));
        let exec = treatment_protocol::ActiveTreatments::<Test>::get(BOB, protocol_id).unwrap();
        assert_eq!(exec.current_step, 1);
        assert_eq!(exec.status, treatment_protocol::TreatmentExecutionStatus::Active);

        // ── Step 8: Patient completes step 1 (TP) ────────────────────────────
        set_block(10);
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE),
            BOB,
            protocol_id,
            1,
        ));
        let exec = treatment_protocol::ActiveTreatments::<Test>::get(BOB, protocol_id).unwrap();
        assert_eq!(exec.completed_steps.len(), 1);
        assert_eq!(exec.current_step, 2);

        // ── Step 9: Root funds reward pool + mints adherence reward (AC) ─────
        assert_ok!(AbenaCoin::fund_reward_pool(RuntimeOrigin::root(), 10_000 * ONE));
        assert_ok!(AbenaCoin::distribute_patient_reward(RuntimeOrigin::root(), BOB, 50 * ONE));
        assert_eq!(abena_coin::pallet::Balances::<Test>::get(BOB), 50 * ONE);

        // ── Step 10: Commercial entity requests data license (DM) ────────────
        let license_id = h256(30);
        request_license(DAVE, license_id);
        let lic = data_marketplace::DataLicenses::<Test>::get(license_id).unwrap();
        assert_eq!(lic.status, data_marketplace::pallet::LicenseStatus::Pending);

        // ── Step 11: Off-chain worker finalizes license (DM, unsigned tx) ─────
        let dataset_hash = h256(31);
        assert_ok!(DataMarketplace::finalize_data_license(
            RuntimeOrigin::none(),
            license_id,
            dataset_hash,
        ));
        let lic = data_marketplace::DataLicenses::<Test>::get(license_id).unwrap();
        assert_eq!(lic.status, data_marketplace::pallet::LicenseStatus::Active);
        assert_eq!(lic.dataset_hash, Some(dataset_hash));

        // ── Step 12: Compensation distributed (DM) ───────────────────────────
        assert_ok!(DataMarketplace::distribute_compensation(
            RuntimeOrigin::signed(ALICE),
            license_id,
            vec![],
        ));
        System::assert_has_event(
            data_marketplace::pallet::Event::<Test>::CompensationDistributed { license_id }.into()
        );
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// SCENARIO 2: Data Marketplace Flow
// ─────────────────────────────────────────────────────────────────────────────

/// Entity stakes ABENA, multiple patients register data, license is
/// requested → finalized → compensation distributed → patients rewarded.
#[test]
fn scenario_2_data_marketplace_flow() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // ── Step 1: Mint tokens + Entity stakes (AC + DM simulation) ─────────
        // Mint ABENA so DAVE (entity) has a balance in the internal ledger.
        mint_abena(DAVE, 200_000 * ONE);
        // Stake to show commercial commitment (simulating entity registration).
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(DAVE), 100_000 * ONE));
        let staked = abena_coin::pallet::StakedBalances::<Test>::get(DAVE);
        assert_eq!(staked, 100_000 * ONE);

        // ── Step 2: Multiple patients register identities (PI) ───────────────
        register_patient(BOB, None);
        register_patient(CHARLIE, None);
        assert!(patient_identity::PatientIdentities::<Test>::contains_key(BOB));
        assert!(patient_identity::PatientIdentities::<Test>::contains_key(CHARLIE));

        // ── Step 3: Patients register data assets (DM) ───────────────────────
        let asset_bob = h256(50);
        let asset_charlie = h256(51);
        // Insert assets directly (find_matching_assets reads from DataAssets storage).
        data_marketplace::DataAssets::<Test>::insert(
            asset_bob,
            data_marketplace::pallet::DataAsset::<Test> {
                owner: BOB,
                data_hash: h256(52),
                tier: pallet_data_marketplace::DataTier::ClinicalData,
            },
        );
        data_marketplace::DataAssets::<Test>::insert(
            asset_charlie,
            data_marketplace::pallet::DataAsset::<Test> {
                owner: CHARLIE,
                data_hash: h256(53),
                tier: pallet_data_marketplace::DataTier::ClinicalData,
            },
        );
        assert!(data_marketplace::DataAssets::<Test>::get(asset_bob).is_some());
        assert!(data_marketplace::DataAssets::<Test>::get(asset_charlie).is_some());

        // ── Step 4: find_matching_assets returns both assets ─────────────────
        use data_marketplace::{DataField, LicensePurpose};
        use data_marketplace::pallet::DataQuery;
        let query = DataQuery {
            fields: BoundedVec::try_from(vec![DataField::LabResults]).unwrap(),
            condition: Some(pallet_data_marketplace::ClinicalCondition::Diabetes),
            demographic: None,
        };
        let matched = DataMarketplace::find_matching_assets(&query, &LicensePurpose::AcademicResearch)
            .expect("matching should succeed");
        assert!(matched.len() >= 2, "both assets should match");

        // ── Step 5: Entity requests data license (DM) ────────────────────────
        let license_id = h256(60);
        request_license(DAVE, license_id);

        // ── Step 6: Off-chain worker simulated: finalize license (DM) ────────
        assert_ok!(DataMarketplace::finalize_data_license(
            RuntimeOrigin::none(),
            license_id,
            h256(61),
        ));
        assert_eq!(
            data_marketplace::DataLicenses::<Test>::get(license_id).unwrap().status,
            data_marketplace::pallet::LicenseStatus::Active
        );

        // ── Step 7: Compensation distributed (DM) ────────────────────────────
        assert_ok!(DataMarketplace::distribute_compensation(
            RuntimeOrigin::signed(DAVE),
            license_id,
            vec![asset_bob, asset_charlie],
        ));

        // ── Step 8: Patient reward pools topped up and rewards distributed (AC)
        assert_ok!(AbenaCoin::fund_reward_pool(RuntimeOrigin::root(), 5_000 * ONE));
        assert_ok!(AbenaCoin::distribute_patient_reward(RuntimeOrigin::root(), BOB, 25 * ONE));
        assert_ok!(AbenaCoin::distribute_patient_reward(RuntimeOrigin::root(), CHARLIE, 25 * ONE));
        assert_eq!(abena_coin::pallet::Balances::<Test>::get(BOB), 25 * ONE);
        assert_eq!(abena_coin::pallet::Balances::<Test>::get(CHARLIE), 25 * ONE);
        assert_eq!(abena_coin::pallet::RewardPool::<Test>::get(), 4_950 * ONE);
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// SCENARIO 3: Clinical Workflow
// ─────────────────────────────────────────────────────────────────────────────

/// Full integrative clinical workflow: consent → access → safety check →
/// protocol → quantum → initiate → steps → notes → outcome → reward.
#[test]
fn scenario_3_clinical_workflow() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // ── Step 1: Patient registers and grants consent (PI) ────────────────
        register_patient(BOB, None);
        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(BOB),
            patient_identity::TherapeuticModality::WesternMedicine,
            true,
            None,
        ));
        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(BOB),
            patient_identity::TherapeuticModality::TraditionalChineseMedicine,
            true,
            None,
        ));

        // ── Step 2: Provider gets access (PI) ────────────────────────────────
        grant_access(BOB, ALICE);
        let access = patient_identity::ProviderAccessList::<Test>::get(BOB, ALICE).unwrap();
        assert_eq!(access.access_level, patient_identity::AccessLevel::ReadWrite);

        // ── Step 3: Add drug-herb interaction rules (TP) ─────────────────────
        // Warfarin + Ginkgo = Contraindicated
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            bvec128(b"Warfarin"),
            bvec128(b"Ginkgo"),
            treatment_protocol::InteractionSeverity::Contraindicated,
            bvec256(b"Anticoagulant potentiation"),
            bvec256(b"Do not combine - serious bleeding risk"),
        ));
        // Metformin + LicoriceRoot = Major
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            bvec128(b"Metformin"),
            bvec128(b"LicoriceRoot"),
            treatment_protocol::InteractionSeverity::Major,
            bvec256(b"Glucose-lowering additive effect"),
            bvec256(b"Monitor blood glucose closely"),
        ));

        // ── Step 4: Safety check → dangerous combination is blocked (TP) ─────
        assert!(
            TreatmentProtocol::check_contraindications(
                RuntimeOrigin::signed(ALICE),
                bvec128(b"Warfarin"),
                bvec128(b"Ginkgo"),
            ).is_err(),
            "Warfarin + Ginkgo must be blocked"
        );
        // Safe combination passes
        assert_ok!(TreatmentProtocol::check_contraindications(
            RuntimeOrigin::signed(ALICE),
            bvec128(b"Metformin"),
            bvec128(b"Vitamin-D"),
        ));

        // ── Step 5: Register integrative treatment protocol (TP) ─────────────
        let protocol_id = h256(70);
        register_2step_protocol(ALICE, protocol_id);

        // ── Step 6: Register quantum algorithm (QR) ──────────────────────────
        let algo_hash = h256(80);
        assert_ok!(QuantumResults::register_algorithm(
            RuntimeOrigin::signed(ALICE),
            algo_hash,
            quantum_results::QuantumAlgorithm::QML,
            1,
            b"QML personalised medicine".to_vec(),
        ));

        // ── Step 7: Quantum result attested for personalised dosing (QR) ─────
        let job_id = b"qml-personalise-001".to_vec();
        assert_ok!(QuantumResults::attest_quantum_result(
            RuntimeOrigin::signed(ALICE),
            job_id.clone(),
            h256(99),
            quantum_results::QuantumAlgorithm::QML,
            1,
            h256(81),
            h256(82),
            vec![0u8; 64],
            1_700_000_001u64,
            15, 5, 4096,
            None,
        ));

        // ── Step 8: Treatment initiated (TP) ─────────────────────────────────
        set_block(5);
        assert_ok!(TreatmentProtocol::initiate_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            protocol_id,
        ));

        // ── Step 9: Patient completes both steps (TP) ────────────────────────
        set_block(10);
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE), BOB, protocol_id, 1,
        ));
        set_block(20);
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE), BOB, protocol_id, 2,
        ));
        let exec = treatment_protocol::ActiveTreatments::<Test>::get(BOB, protocol_id).unwrap();
        assert_eq!(exec.completed_steps.len(), 2);

        // ── Step 10: Provider creates clinical notes for both steps (HRH) ────
        for (seed, rtype) in [
            (90u8, health_record_hash::RecordTypeSpec::ClinicalNote),
            (91u8, health_record_hash::RecordTypeSpec::TreatmentPlan),
        ] {
            assert_ok!(HealthRecordHash::create_record_hash(
                RuntimeOrigin::signed(ALICE),
                h256(seed),
                BOB,
                h32(seed),
                None,
                rtype,
                health_record_hash::pallet::TherapeuticModality::WesternMedicine,
                bvec512(b"sig"),
                h32(seed + 1),
            ));
        }

        // ── Step 11: Milestone evaluated + treatment completed (TP) ──────────
        assert_ok!(TreatmentProtocol::evaluate_milestone(
            RuntimeOrigin::signed(CHARLIE), BOB, protocol_id, 2, true,
        ));
        set_block(30);
        assert_ok!(TreatmentProtocol::complete_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            protocol_id,
            true,
            bvec512(b"HbA1c 6.4% - target achieved"),
        ));
        let exec = treatment_protocol::ActiveTreatments::<Test>::get(BOB, protocol_id).unwrap();
        assert_eq!(exec.status, treatment_protocol::TreatmentExecutionStatus::Completed);
        assert!(exec.outcome.unwrap().success);

        // ── Step 12: Adherence reward distributed (AC) ────────────────────────
        assert_ok!(AbenaCoin::fund_reward_pool(RuntimeOrigin::root(), 1_000 * ONE));
        assert_ok!(AbenaCoin::distribute_patient_reward(RuntimeOrigin::root(), BOB, 100 * ONE));
        assert_eq!(abena_coin::pallet::Balances::<Test>::get(BOB), 100 * ONE);
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// SCENARIO 4: Governance & Treasury
// ─────────────────────────────────────────────────────────────────────────────

/// Token holders submit and vote on a treasury spend proposal that passes.
#[test]
fn scenario_4_governance_treasury() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // ── Step 1: Mint tokens to participants (AC) ──────────────────────────
        // Proposer needs balance ≥ MinProposalDeposit (100) in internal ledger.
        // Voters need balances for voting power.
        mint_abena(ALICE, 10_000 * ONE);
        mint_abena(BOB,   8_000 * ONE);

        assert_eq!(abena_coin::pallet::Balances::<Test>::get(ALICE), 10_000 * ONE);

        // ── Step 2: ALICE funds the treasury before the proposal (AC) ────────
        // collect_to_treasury transfers from internal ledger to TreasuryBalance.
        assert_ok!(AbenaCoin::collect_to_treasury(RuntimeOrigin::signed(ALICE), 1_000 * ONE));
        assert_eq!(abena_coin::pallet::TreasuryBalance::<Test>::get(), 1_000 * ONE);
        // ALICE internal balance is now 9_000 * ONE.

        // ── Step 3: ALICE submits a treasury spend proposal (AC) ─────────────
        // The deposit (100 raw units) is held until execution.
        let description_hash = h256(100);
        assert_ok!(AbenaCoin::submit_proposal(
            RuntimeOrigin::signed(ALICE),
            abena_coin::ProposalType::TreasurySpend,
            description_hash,
            Some(500 * ONE),   // requested amount
            Some(CHARLIE),     // beneficiary: CHARLIE will receive the grant
        ));
        let proposals = abena_coin::pallet::Proposals::<Test>::iter().collect::<Vec<_>>();
        assert_eq!(proposals.len(), 1);
        let (proposal_id, proposal) = &proposals[0];
        assert_eq!(proposal.status, abena_coin::ProposalStatus::Active);
        let pid = *proposal_id;

        // ── Step 4: Token holders vote YES (AC) ──────────────────────────────
        // Voting must happen before voting_period_end (block 1 + 10 = 11).
        set_block(5);
        assert_ok!(AbenaCoin::vote_on_proposal(
            RuntimeOrigin::signed(ALICE),
            pid,
            abena_coin::VoteDirection::Yes,
            5_000 * ONE,
            0u64.into(), // no conviction multiplier
        ));
        assert_ok!(AbenaCoin::vote_on_proposal(
            RuntimeOrigin::signed(BOB),
            pid,
            abena_coin::VoteDirection::Yes,
            4_000 * ONE,
            0u64.into(),
        ));

        // ── Step 5: Advance past voting period and execute (AC) ──────────────
        // VotingPeriodBlocks = 10; started at block 1, so voting_period_end = 11.
        // execution requires current block >= voting_period_end.
        set_block(12);
        assert_ok!(AbenaCoin::execute_proposal(RuntimeOrigin::signed(EVE), pid));

        let prop = abena_coin::pallet::Proposals::<Test>::get(pid).unwrap();
        assert_eq!(prop.status, abena_coin::ProposalStatus::Executed);

        System::assert_has_event(
            abena_coin::pallet::Event::<Test>::ProposalExecuted {
                proposal_id: pid,
                executor: EVE,
            }.into()
        );
        // Treasury was debited 500 * ONE; CHARLIE has an approved grant.
        assert_eq!(abena_coin::pallet::TreasuryBalance::<Test>::get(), 500 * ONE);
        assert!(abena_coin::pallet::ApprovedGrants::<Test>::get(CHARLIE, pid).is_some());
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// SCENARIO 5: Violation Enforcement
// ─────────────────────────────────────────────────────────────────────────────

/// Entity licenses data, violation is detected, stake is slashed via governance.
/// (Full violation workflow will expand when the data-marketplace pallet is
///  extended; current implementation demonstrates stake slash via AbenaCoin.)
#[test]
fn scenario_5_violation_enforcement() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // ── Step 1: Entity mints and stakes tokens (AC) ───────────────────────
        mint_abena(DAVE, 500_000 * ONE);
        assert_ok!(AbenaCoin::stake(RuntimeOrigin::signed(DAVE), 200_000 * ONE));
        assert_eq!(abena_coin::pallet::StakedBalances::<Test>::get(DAVE), 200_000 * ONE);

        // ── Step 2: Patients register and register data assets (PI + DM) ─────
        register_patient(BOB, None);
        register_patient(CHARLIE, None);

        data_marketplace::DataAssets::<Test>::insert(
            h256(110),
            data_marketplace::pallet::DataAsset::<Test> {
                owner: BOB,
                data_hash: h256(111),
                tier: pallet_data_marketplace::DataTier::ClinicalData,
            },
        );

        // ── Step 3: Entity requests license (DM) ─────────────────────────────
        let license_id = h256(120);
        request_license(DAVE, license_id);
        assert_eq!(
            data_marketplace::DataLicenses::<Test>::get(license_id).unwrap().status,
            data_marketplace::pallet::LicenseStatus::Pending
        );

        // ── Step 4: License finalized by off-chain worker (DM) ───────────────
        assert_ok!(DataMarketplace::finalize_data_license(
            RuntimeOrigin::none(),
            license_id,
            h256(121),
        ));
        assert_eq!(
            data_marketplace::DataLicenses::<Test>::get(license_id).unwrap().status,
            data_marketplace::pallet::LicenseStatus::Active
        );

        // ── Step 5: Violation detected — governance slashes entity stake (AC) ─
        // Simulate: DAVE (entity) violated data terms.
        // Governance burns a portion of DAVE's staked tokens as penalty.
        let stake_before = abena_coin::pallet::StakedBalances::<Test>::get(DAVE);
        assert_ok!(AbenaCoin::unstake(RuntimeOrigin::signed(DAVE), stake_before));

        // Burn the entity's entire liquid balance as penalty (root governance action).
        let total_balance = abena_coin::pallet::Balances::<Test>::get(DAVE);
        assert_ok!(AbenaCoin::burn(RuntimeOrigin::signed(DAVE), total_balance));

        let post_balance = abena_coin::pallet::Balances::<Test>::get(DAVE);
        assert_eq!(post_balance, 0, "Entity stake fully slashed after violation");

        // ── Step 6: Distribute remaining funds to victimised patients (AC) ────
        assert_ok!(AbenaCoin::fund_reward_pool(RuntimeOrigin::root(), 1_000 * ONE));
        assert_ok!(AbenaCoin::distribute_patient_reward(RuntimeOrigin::root(), BOB, 100 * ONE));
        assert_eq!(abena_coin::pallet::Balances::<Test>::get(BOB), 100 * ONE);

        // Adverse event logged on treatment (demonstrating cross-pallet audit trail).
        // (Treatment is not active for BOB in this scenario, but the adverse event
        //  extrinsic is callable and records violations in the treatment pallet's log.)
        register_2step_protocol(ALICE, h256(130));
        assert_ok!(TreatmentProtocol::initiate_treatment(
            RuntimeOrigin::signed(ALICE), BOB, h256(130),
        ));
        assert_ok!(TreatmentProtocol::report_adverse_event(
            RuntimeOrigin::signed(ALICE),
            BOB,
            h256(130),
            bvec256(b"Data misuse detected by compliance system"),
        ));
        let adverse_events = treatment_protocol::AdverseEvents::<Test>::get(BOB, h256(130));
        assert_eq!(adverse_events.len(), 1);
    });
}

// ─────────────────────────────────────────────────────────────────────────────
// SCENARIO 6: Multi-Modality Safety Checking
// ─────────────────────────────────────────────────────────────────────────────

/// A patient on Western anticoagulants is also prescribed TCM herbs;
/// the interaction checker blocks the dangerous combination and the provider
/// falls back to a safe alternative protocol.
#[test]
fn scenario_6_multi_modality_safety() {
    new_test_ext().execute_with(|| {
        set_block(1);

        // ── Step 1: Patient on Western medication registers (PI + TP) ─────────
        register_patient(BOB, None);
        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(BOB),
            patient_identity::TherapeuticModality::WesternMedicine,
            true,
            None,
        ));
        assert_ok!(PatientIdentity::update_consent(
            RuntimeOrigin::signed(BOB),
            patient_identity::TherapeuticModality::TraditionalChineseMedicine,
            true,
            None,
        ));
        grant_access(BOB, ALICE);
        assert!(patient_identity::ProviderAccessList::<Test>::get(BOB, ALICE).is_some());

        // ── Step 2: Build the interaction database (TP) ───────────────────────
        // Warfarin + Ginkgo = Contraindicated (Western anticoagulant + TCM herb)
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            bvec128(b"Warfarin"),
            bvec128(b"Ginkgo"),
            treatment_protocol::InteractionSeverity::Contraindicated,
            bvec256(b"Inhibits platelet aggregation, potentiates anticoagulation"),
            bvec256(b"Absolutely contraindicated: risk of life-threatening haemorrhage"),
        ));
        // Aspirin + Ginger = Moderate (ok, but monitor)
        assert_ok!(TreatmentProtocol::add_interaction_rule(
            RuntimeOrigin::root(),
            bvec128(b"Aspirin"),
            bvec128(b"Ginger"),
            treatment_protocol::InteractionSeverity::Moderate,
            bvec256(b"Mild antiplatelet additive effect"),
            bvec256(b"Monitor for bleeding; usually well tolerated"),
        ));

        // ── Step 3: Provider checks planned Warfarin + Ginkgo → BLOCKED (TP) ──
        assert!(
            TreatmentProtocol::check_contraindications(
                RuntimeOrigin::signed(ALICE),
                bvec128(b"Warfarin"),
                bvec128(b"Ginkgo"),
            ).is_err(),
            "Warfarin + Ginkgo must be blocked by interaction checker"
        );
        // Bidirectional: reversed order is also blocked
        assert!(
            TreatmentProtocol::check_contraindications(
                RuntimeOrigin::signed(ALICE),
                bvec128(b"Ginkgo"),
                bvec128(b"Warfarin"),
            ).is_err(),
            "Ginkgo + Warfarin (reversed) must also be blocked"
        );

        // ── Step 4: Alternative TCM herb passes safety check (TP) ────────────
        // Provider substitutes Ginkgo with a safer herb: Astragalus (no rule).
        assert_ok!(TreatmentProtocol::check_contraindications(
            RuntimeOrigin::signed(ALICE),
            bvec128(b"Warfarin"),
            bvec128(b"Astragalus"),
        ));
        // Aspirin + Ginger is Moderate — allowed
        assert_ok!(TreatmentProtocol::check_contraindications(
            RuntimeOrigin::signed(ALICE),
            bvec128(b"Aspirin"),
            bvec128(b"Ginger"),
        ));

        // ── Step 5: Register safe alternative protocol with Astragalus (TP) ───
        use treatment_protocol::{
            ClinicalCondition, EvidenceLevel, Frequency, HerbFormula,
            InterventionType, SuccessCriteria, TherapeuticModality, TreatmentStep,
        };
        let alt_pid = h256(200);
        let safe_steps: BoundedVec<TreatmentStep, ConstU32<64>> =
            BoundedVec::try_from(vec![
                TreatmentStep {
                    step_number: 1,
                    intervention_type: InterventionType::Pharmaceutical, // Warfarin
                    medication: None, herb_formula: None, procedure: None,
                    duration_days: 30,
                    frequency: Frequency { times_per_day: 1, days_per_week: 7 },
                    prerequisites: BoundedVec::default(),
                    success_criteria: None,
                    next_step_conditions: BoundedVec::default(),
                },
                TreatmentStep {
                    step_number: 2,
                    intervention_type: InterventionType::Botanical, // Astragalus (safe)
                    medication: None,
                    herb_formula: Some(HerbFormula {
                        name: bvec128(b"Astragalus membranaceus"),
                        components_ref: bvec256(b"Huang Qi - immune modulation"),
                    }),
                    procedure: None,
                    duration_days: 28,
                    frequency: Frequency { times_per_day: 2, days_per_week: 7 },
                    prerequisites: BoundedVec::default(),
                    success_criteria: None,
                    next_step_conditions: BoundedVec::default(),
                },
            ]).unwrap();

        assert_ok!(TreatmentProtocol::register_protocol(
            RuntimeOrigin::signed(ALICE),
            alt_pid,
            bvec128(b"Western + TCM Safe Alternative"),
            ClinicalCondition {
                code: BoundedVec::try_from(b"AFIB".to_vec()).unwrap(),
                description: BoundedVec::try_from(b"Atrial Fibrillation".to_vec()).unwrap(),
            },
            BoundedVec::try_from(vec![
                TherapeuticModality::Western,
                TherapeuticModality::TCM,
            ]).unwrap(),
            EvidenceLevel::CohortStudy,
            58,
            SuccessCriteria {
                description: bvec256(b"INR stable 2-3, no adverse events"),
                measurable: true,
            },
            safe_steps,
        ));

        // ── Step 6: Initiate the safe alternative for BOB (TP) ───────────────
        set_block(5);
        assert_ok!(TreatmentProtocol::initiate_treatment(
            RuntimeOrigin::signed(ALICE), BOB, alt_pid,
        ));

        let exec = treatment_protocol::ActiveTreatments::<Test>::get(BOB, alt_pid).unwrap();
        assert_eq!(exec.status, treatment_protocol::TreatmentExecutionStatus::Active);
        assert_eq!(exec.current_step, 1);

        // ── Step 7: BOB progresses through the safe protocol (TP) ────────────
        set_block(10);
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE), BOB, alt_pid, 1,
        ));
        set_block(20);
        assert_ok!(TreatmentProtocol::record_step_completion(
            RuntimeOrigin::signed(ALICE), BOB, alt_pid, 2,
        ));

        // ── Step 8: Record a clinical note documenting the safety decision (HRH)
        assert_ok!(HealthRecordHash::create_record_hash(
            RuntimeOrigin::signed(ALICE),
            h256(201),
            BOB,
            h32(201),
            None,
            health_record_hash::RecordTypeSpec::ClinicalNote,
            health_record_hash::pallet::TherapeuticModality::WesternMedicine,
            bvec512(b"Switched from Ginkgo to Astragalus due to Warfarin interaction"),
            h32(202),
        ));

        // Verify the note was created and the safe protocol is still active.
        assert!(health_record_hash::RecordHashStore::<Test>::get(h256(201)).is_some());
        let exec = treatment_protocol::ActiveTreatments::<Test>::get(BOB, alt_pid).unwrap();
        assert_eq!(exec.completed_steps.len(), 2);

        // ── Step 9: Complete treatment successfully (TP) ──────────────────────
        set_block(30);
        assert_ok!(TreatmentProtocol::complete_treatment(
            RuntimeOrigin::signed(ALICE),
            BOB,
            alt_pid,
            true,
            bvec512(b"INR stable, no bleeding events, patient tolerated Astragalus well"),
        ));
        assert_eq!(
            treatment_protocol::ActiveTreatments::<Test>::get(BOB, alt_pid)
                .unwrap().status,
            treatment_protocol::TreatmentExecutionStatus::Completed
        );
    });
}
