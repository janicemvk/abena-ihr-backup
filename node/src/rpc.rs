//! RPC for ABENA node

use abena_runtime::opaque::Block;
use jsonrpc_core;
use sc_rpc_api::DenyUnsafe;
use sp_api::ProvideRuntimeApi;
use sp_blockchain::{Error as BlockChainError, HeaderMetadata, HeaderBackend};
use sp_block_builder::BlockBuilder;
use std::sync::Arc;

pub struct FullDeps<C, P> {
    pub client: Arc<C>,
    pub pool: Arc<P>,
    pub deny_unsafe: DenyUnsafe,
}

pub fn create_full<C, P>(
    deps: FullDeps<C, P>,
) -> jsonrpc_core::IoHandler<sc_rpc_api::Metadata>
where
    C: ProvideRuntimeApi<Block>,
    C: HeaderBackend<Block> + HeaderMetadata<Block, Error = BlockChainError> + 'static,
    C: Send + Sync + 'static,
    C::Api: BlockBuilder<Block>,
    P: sc_transaction_pool::ChainApi<Block = Block> + 'static,
{
    use sc_rpc::Chain;
    use sc_rpc::ChainSpec;
    use sc_rpc::System;
    use sc_rpc::state::StateApi;

    let mut io = jsonrpc_core::IoHandler::default();
    let FullDeps {
        client,
        pool,
        deny_unsafe,
    } = deps;

    io.extend_with(System::to_delegate(System::new(
        client.clone(),
        pool.clone(),
        deny_unsafe,
    )));
    io.extend_with(Chain::to_delegate(Chain::new(client.clone())));
    io.extend_with(StateApi::to_delegate(StateApi::new(client.clone(), deny_unsafe)));

    io
}

