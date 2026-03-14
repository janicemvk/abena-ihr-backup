//! ABENA IHR Chain Specification
//! Genesis configuration for ABENA Coin distribution

use abena_runtime::{
    currency::ABENA,
    AccountId, Signature, WASM_BINARY,
};
use sc_service::ChainType;
use sp_consensus_aura::sr25519::AuthorityId as AuraId;
use sp_consensus_grandpa::ed25519::AuthorityId as GrandpaId;
use sp_core::{ed25519, sr25519, Pair, Public};
use sp_runtime::traits::{IdentifyAccount, Verify};

pub type ChainSpec = sc_service::GenericChainSpec<()>;

type AccountPublic = <Signature as Verify>::Signer;

fn get_from_seed<TPublic: Public>(seed: &str) -> <TPublic::Pair as Pair>::Public {
    TPublic::Pair::from_string(&format!("//{}", seed), None)
        .expect("static values are valid; qed")
        .public()
}

fn get_account_id_from_seed<TPublic: Public>(seed: &str) -> AccountId
where
    AccountPublic: From<<TPublic::Pair as Pair>::Public>,
{
    AccountPublic::from(get_from_seed::<TPublic>(seed)).into_account()
}

fn get_aura_from_seed(seed: &str) -> AuraId {
    get_from_seed::<AuraId>(seed)
}

fn get_grandpa_from_seed(seed: &str) -> GrandpaId {
    get_from_seed::<GrandpaId>(seed)
}

fn authority_keys_from_seed(seed: &str) -> (AuraId, GrandpaId) {
    (get_aura_from_seed(seed), get_grandpa_from_seed(seed))
}

// ─── Development chain (local --dev) ──────────────────────────────────────────
pub fn development_config() -> Result<ChainSpec, String> {
    let wasm_binary = WASM_BINARY.ok_or_else(|| "Dev wasm binary not available".to_string())?;
    let (aura, grandpa) = authority_keys_from_seed("Alice");
    Ok(ChainSpec::builder(wasm_binary, Default::default())
        .with_name("ABENA IHR Development")
        .with_id("abena_dev")
        .with_chain_type(ChainType::Development)
        .with_genesis_config_patch(testnet_genesis(
            vec![aura],
            vec![grandpa],
            get_account_id_from_seed::<sr25519::Public>("Alice"),
            true,
        ))
        .build())
}

// ─── Local testnet (two validators) ───────────────────────────────────────────
pub fn local_testnet_config() -> Result<ChainSpec, String> {
    let wasm_binary = WASM_BINARY.ok_or_else(|| "Local wasm binary not available".to_string())?;
    let (aura_a, grandpa_a) = authority_keys_from_seed("Alice");
    let (aura_b, grandpa_b) = authority_keys_from_seed("Bob");
    Ok(ChainSpec::builder(wasm_binary, Default::default())
        .with_name("ABENA IHR Local Testnet")
        .with_id("abena_local_testnet")
        .with_chain_type(ChainType::Local)
        .with_genesis_config_patch(testnet_genesis(
            vec![aura_a, aura_b],
            vec![grandpa_a, grandpa_b],
            get_account_id_from_seed::<sr25519::Public>("Alice"),
            true,
        ))
        .build())
}

// ─── Public testnet (wss://testnet.abenihr.com) ────────────────────────────────
pub fn abena_testnet_config() -> Result<ChainSpec, String> {
    let wasm_binary = WASM_BINARY.ok_or_else(|| "ABENA wasm binary not available".to_string())?;
    let (aura_a, grandpa_a) = authority_keys_from_seed("Alice");
    let (aura_b, grandpa_b) = authority_keys_from_seed("Bob");
    Ok(ChainSpec::builder(wasm_binary, Default::default())
        .with_name("ABENA IHR Public Testnet")
        .with_id("abena_testnet")
        .with_chain_type(ChainType::Live)
        .with_properties(serde_json::json!({
            "tokenSymbol": "ABENA",
            "tokenDecimals": 12,
            "ss58Format": 42
        }))
        .with_genesis_config_patch(testnet_genesis(
            vec![aura_a, aura_b],
            vec![grandpa_a, grandpa_b],
            get_account_id_from_seed::<sr25519::Public>("Alice"),
            false, // set false for public testnet (no dev endowments)
        ))
        .build())
}

// ─── Genesis: ABENA Coin distribution ─────────────────────────────────────────
fn testnet_genesis(
    initial_aura: Vec<AuraId>,
    initial_grandpa: Vec<GrandpaId>,
    root_key: AccountId,
    is_dev_or_local: bool,
) -> serde_json::Value {
    // ── Account seeds (replace with real keys for production) ──────────────
    let treasury = get_account_id_from_seed::<sr25519::Public>("Treasury");
    let team = get_account_id_from_seed::<sr25519::Public>("Team");
    let institutional = get_account_id_from_seed::<sr25519::Public>("Institutional");
    let ecosystem = get_account_id_from_seed::<sr25519::Public>("Ecosystem");

    // ── ABENA Coin allocations ──────────────────────────────────────────────
    //   Treasury      40%  →  400,000,000 ABENA (includes health rewards minting allocation)
    //   Team (4yr)    20%  →  200,000,000 ABENA
    //   Institutional 20%  →  200,000,000 ABENA
    //   Ecosystem     20%  →  200,000,000 ABENA
    //   Total:       100%  → 1,000,000,000 ABENA
    //   Health rewards: minted via deposit_creating (inflation), no pool
    let mut balances: Vec<(AccountId, u128)> = vec![
        (treasury, 400_000_000u128 * ABENA),
        (team, 200_000_000u128 * ABENA),
        (institutional, 200_000_000u128 * ABENA),
        (ecosystem, 200_000_000u128 * ABENA),
    ];

    // Add validator accounts with operational balances
    for aura in &initial_aura {
        let validator_account: AccountId = AccountPublic::from(aura.clone()).into_account();
        balances.push((validator_account, 10_000u128 * ABENA));
    }

    // Dev endowments: Alice, Bob, Charlie etc. get test ABENA on dev/local chains
    if is_dev_or_local {
        let dev_accounts = vec![
            get_account_id_from_seed::<sr25519::Public>("Alice"),
            get_account_id_from_seed::<sr25519::Public>("Bob"),
            get_account_id_from_seed::<sr25519::Public>("Charlie"),
            get_account_id_from_seed::<sr25519::Public>("Dave"),
            get_account_id_from_seed::<sr25519::Public>("Eve"),
            get_account_id_from_seed::<sr25519::Public>("Ferdie"),
        ];
        for acct in dev_accounts {
            balances.push((acct, 1_000_000u128 * ABENA));
        }
    }

    serde_json::json!({
        "balances": {
            "balances": balances
        },
        "aura": {
            "authorities": initial_aura
        },
        "grandpa": {
            "authorities": initial_grandpa.iter().map(|g| (g.clone(), 1u64)).collect::<Vec<_>>()
        },
        "sudo": {
            "key": Some(root_key)
        },
        "abenaRewards": {
            "initialRewards": [],
            "initialDailyCap": Some(50u128 * ABENA)
        }
    })
}
