//! Service implementation for ABENA node

use abena_runtime::{self, opaque::Block, RuntimeApi};
use sc_client_api::{Backend, BlockImportOperation, StorageProvider};
use sc_consensus_aura::{ImportQueueParams, SlotDuration, StartSlot};
use sc_executor::WasmExecutor;
use sc_service::{error::Error as ServiceError, Configuration, TaskManager};
use sp_consensus_aura::sr25519::AuthorityId as AuraId;
use sp_runtime::traits::BlakeTwo256;
use std::sync::Arc;

pub fn new_partial(
    config: &Configuration,
) -> Result<
    sc_service::PartialComponents<
        sc_consensus_aura::AuraBlockImport<
            Block,
            sc_client_api::Client<sc_client_api::LocalCallExecutor<Block, WasmExecutor<sp_io::SubstrateHostFunctions>>, Block, RuntimeApi, ()>,
            Block,
        >,
        sc_consensus_aura::AuraLink<Block>,
        sc_transaction_pool::FullPool<Block, sc_client_api::Client<sc_client_api::LocalCallExecutor<Block, WasmExecutor<sp_io::SubstrateHostFunctions>>, Block, RuntimeApi, ()>>,
        sc_consensus_aura::AuraBlockImport<
            Block,
            sc_client_api::Client<sc_client_api::LocalCallExecutor<Block, WasmExecutor<sp_io::SubstrateHostFunctions>>, Block, RuntimeApi, ()>,
            Block,
        >,
        (),
        sc_consensus_aura::AuraLink<Block>,
    >,
    ServiceError,
> {
    let wasm_executor = WasmExecutor::default();
    let (client, backend, keystore_container, task_manager) =
        sc_service::new_full_parts::<Block, RuntimeApi, _>(
            config,
            wasm_executor,
        )?;

    let client = Arc::new(client);
    let slot_duration = sc_consensus_aura::slot_duration(&*client)?;

    let import_queue = sc_consensus_aura::import_queue::<AuraId, _, _, _, _, _>(
        ImportQueueParams {
            block_import: client.clone(),
            client: client.clone(),
            create_inherent_data_providers: move |_, ()| async move {
                Ok(())
            },
            spawner: &task_manager.spawn_essential_handle(),
            registry: config.prometheus_config.as_ref().map(|cfg| &cfg.registry),
            can_author_with: sp_consensus::CanAuthorWithNativeVersion::new(client.executor().clone()),
            slot_duration,
            check_for_equivocation: Default::default(),
            telemetry: config.telemetry_endpoints.clone(),
        },
    )?;

    Ok(sc_service::PartialComponents {
        client,
        backend,
        task_manager,
        import_queue,
        keystore_container,
        select_chain: (),
        other: (),
    })
}

pub fn new_full(config: Configuration) -> Result<TaskManager, ServiceError> {
    let sc_service::PartialComponents {
        client,
        backend,
        mut task_manager,
        import_queue,
        keystore_container,
        select_chain,
        other,
    } = new_partial(&config)?;

    Ok(task_manager)
}

