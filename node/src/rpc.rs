//! ABENA IHR Node RPC Extensions
//!
//! Extends the standard Substrate JSON-RPC with:
//!   - `system_*`   — Node health, peer count, chain name, version
//!   - `payment_*`  — Query transaction fees in ABENA Coin
//!   - Future: abena_protocolStats, abena_patientProfile

use std::sync::Arc;

use abena_runtime::{opaque::Block, AccountId, Balance, Nonce};
use jsonrpsee::RpcModule;
use pallet_transaction_payment_rpc::{TransactionPayment, TransactionPaymentApiServer};
use sc_client_api::AuxStore;
use sc_rpc_api::DenyUnsafe;
use sc_transaction_pool_api::TransactionPool;
use sp_api::ProvideRuntimeApi;
use sp_blockchain::{Error as BlockChainError, HeaderBackend, HeaderMetadata};
use substrate_frame_rpc_system::{System, SystemApiServer};

// ─── RPC Dependencies ────────────────────────────────────────────────────────

/// Full RPC dependencies for the ABENA node.
pub struct FullDeps<C, P> {
    /// The client instance to use.
    pub client: Arc<C>,
    /// Transaction pool instance.
    pub pool: Arc<P>,
    /// Whether to deny unsafe RPC calls (set true in production).
    /// Unsafe calls: author_insertKey, system_addReservedPeer, etc.
    pub deny_unsafe: DenyUnsafe,
}

// ─── create_full — Mount all RPC modules ─────────────────────────────────────

/// Instantiate all Full RPC extensions for the ABENA node.
///
/// Mounts:
///   - `system_*`   — Node health, peer count, chain name, version
///   - `payment_*`  — Query transaction fees in ABENA Coin (payment_queryInfo, payment_queryFeeDetails)
pub fn create_full<C, P>(
    deps: FullDeps<C, P>,
) -> Result<RpcModule<()>, Box<dyn std::error::Error + Send + Sync>>
where
    C: ProvideRuntimeApi<Block>
        + HeaderBackend<Block>
        + AuxStore
        + HeaderMetadata<Block, Error = BlockChainError>
        + Send
        + Sync
        + 'static,
    C::Api: sp_api::Metadata<Block>
        + sp_block_builder::BlockBuilder<Block>
        + sp_transaction_pool::runtime_api::TaggedTransactionQueue<Block>
        + substrate_frame_rpc_system::AccountNonceApi<Block, AccountId, Nonce>
        + pallet_transaction_payment_rpc::TransactionPaymentRuntimeApi<Block, Balance>,
    P: TransactionPool + 'static,
{
    let FullDeps { client, pool, deny_unsafe: _ } = deps;

    let mut module = RpcModule::new(());

    // ── System RPC ────────────────────────────────────────────────────────
    // Provides: system_health, system_name, system_version, system_chain, system_peers, etc.
    module.merge(System::new(client.clone(), pool.clone()).into_rpc())?;

    // ── Transaction Payment RPC ───────────────────────────────────────────
    // Provides: payment_queryInfo, payment_queryFeeDetails
    // Investors can call payment_queryInfo to see ABENA Coin fees
    module.merge(TransactionPayment::new(client).into_rpc())?;

    // ── ABENA Custom RPC module ────────────────────────────────────────────
    // Future: mount abena_protocolStats and abena_patientProfile here
    // Example:
    // use abena_rpc::{AbenaRpc, AbenaRpcApiServer};
    // module.merge(AbenaRpc::new(client.clone()).into_rpc())?;

    Ok(module)
}
