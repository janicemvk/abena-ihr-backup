//! ABENA IHR Node Service
//!
//! DK Technologies, Inc. — Integrative Health Record
//!
//! This file wires together:
//!   - The ABENA runtime (WASM + native)
//!   - Aura block authorship
//!   - GRANDPA finality with warp sync (NetworkProvider + WarpSyncConfig::WithProvider)
//!   - RPC server (Polkadot.js Apps connects here)
//!   - Transaction pool
//!   - Peer-to-peer networking (libp2p)
//!   - State database (RocksDB)
//!
//! Two service modes:
//!   `new_full`  — Full validator node (used for testnet at testnet.abenihr.com)
//!   `new_light` — Light client (future: ABENA mobile app backend)

use abena_runtime::{self, opaque::Block, RuntimeApi};
use sc_consensus_aura::{ImportQueueParams, SlotProportion, StartAuraParams};
use sc_consensus_grandpa::AuthorityPair as GrandpaPair;
use sc_consensus_grandpa::warp_proof::NetworkProvider;
use sc_service::{RpcMethods, WarpSyncConfig};
use sc_service::{error::Error as ServiceError, Configuration, TaskManager};
use sc_telemetry::{Telemetry, TelemetryWorker};
use sp_consensus_aura::sr25519::AuthorityPair as AuraPair;
use std::sync::Arc;

pub type FullClient =
    sc_service::TFullClient<Block, RuntimeApi, WasmExecutor>;
pub type FullBackend = sc_service::TFullBackend<Block>;
pub type FullSelectChain = sc_consensus::LongestChain<FullBackend, Block>;
pub type WasmExecutor = sc_executor::WasmExecutor<sp_io::SubstrateHostFunctions>;

/// Grandpa block import and link (blocks must go through this for finality).
pub type GrandpaBlockImport = sc_consensus_grandpa::GrandpaBlockImport<
    FullBackend,
    Block,
    FullClient,
    FullSelectChain,
>;
pub type GrandpaLink = sc_consensus_grandpa::LinkHalf<Block, FullClient, FullSelectChain>;

/// Components created by [`new_partial`].
pub struct NewPartial {
    pub client: Arc<FullClient>,
    pub backend: Arc<FullBackend>,
    pub task_manager: TaskManager,
    pub keystore_container: sc_service::KeystoreContainer,
    pub select_chain: FullSelectChain,
    pub import_queue: sc_consensus::DefaultImportQueue<Block>,
    pub transaction_pool: Arc<
        sc_transaction_pool::BasicPool<
            sc_transaction_pool::FullChainApi<FullClient, Block>,
            Block,
        >,
    >,
    pub telemetry: Option<Telemetry>,
    pub grandpa_block_import: GrandpaBlockImport,
    pub grandpa_link: GrandpaLink,
}

pub fn new_partial(config: &Configuration) -> Result<NewPartial, ServiceError> {
    let telemetry = config
        .telemetry_endpoints
        .clone()
        .filter(|x| !x.is_empty())
        .map(|endpoints| -> Result<_, sc_telemetry::Error> {
            let worker = TelemetryWorker::new(16)?;
            let telemetry = worker.handle().new_telemetry(endpoints);
            Ok((worker, telemetry))
        })
        .transpose()?;

    let executor = WasmExecutor::builder()
        .with_onchain_heap_alloc_strategy(
            sc_executor::HeapAllocStrategy::Dynamic { maximum_pages: Some(64) },
        )
        .with_offchain_heap_alloc_strategy(
            sc_executor::HeapAllocStrategy::Dynamic { maximum_pages: Some(64) },
        )
        .build();

    let (client, backend, keystore_container, task_manager) =
        sc_service::new_full_parts::<Block, RuntimeApi, _>(
            config,
            telemetry.as_ref().map(|(_, telemetry)| telemetry.handle()),
            executor,
        )?;
    let client = Arc::new(client);

    let telemetry = telemetry.map(|(worker, telemetry)| {
        task_manager
            .spawn_handle()
            .spawn("telemetry", None, worker.run());
        telemetry
    });

    let select_chain = sc_consensus::LongestChain::new(backend.clone());

    let transaction_pool = Arc::new(sc_transaction_pool::BasicPool::new_full(
        sc_transaction_pool::Options::default(),
        config.role.is_authority().into(),
        config.prometheus_registry(),
        task_manager.spawn_essential_handle(),
        client.clone(),
    ));

    let slot_duration = sc_consensus_aura::slot_duration(&*client)?;

    let (grandpa_block_import, grandpa_link) = sc_consensus_grandpa::block_import(
        client.clone(),
        512, // justification import period (every ~51 min at 6s/block)
        &*client,
        select_chain.clone(),
        telemetry.as_ref().map(|x| x.handle()),
    )?;

    let import_queue =
        sc_consensus_aura::import_queue::<AuraPair, _, _, _, _, _>(ImportQueueParams {
            block_import: grandpa_block_import.clone(),
            justification_import: Some(Box::new(grandpa_block_import.clone())),
            client: client.clone(),
            create_inherent_data_providers: move |_, ()| async move {
                let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
                let slot =
                    sp_consensus_aura::inherents::InherentDataProvider::from_timestamp_and_slot_duration(
                        *timestamp,
                        slot_duration,
                    );
                Ok((slot, timestamp))
            },
            spawner: &task_manager.spawn_essential_handle(),
            registry: config.prometheus_config.as_ref().map(|cfg| &cfg.registry),
            check_for_equivocation: Default::default(),
            telemetry: telemetry.as_ref().map(|x| x.handle()),
            compatibility_mode: Default::default(),
        })?;

    Ok(NewPartial {
        client,
        backend,
        task_manager,
        keystore_container,
        select_chain,
        import_queue,
        transaction_pool,
        telemetry,
        grandpa_block_import,
        grandpa_link,
    })
}

pub fn new_full(config: Configuration) -> Result<TaskManager, ServiceError> {
    let NewPartial {
        client,
        backend,
        mut task_manager,
        keystore_container,
        select_chain,
        import_queue,
        transaction_pool,
        mut telemetry,
        grandpa_block_import,
        grandpa_link,
    } = new_partial(&config)?;

    let grandpa_protocol_name = sc_consensus_grandpa::protocol_standard_name(
        &client.block_hash(0).ok().flatten().unwrap_or_default(),
        &config.chain_spec.fork_id(),
    );
    let mut net_config = sc_network::config::FullNetworkConfiguration::<
        Block,
        <Block as sp_runtime::traits::Block>::Hash,
        sc_network::NetworkWorker<
            Block,
            <Block as sp_runtime::traits::Block>::Hash,
        >,
    >::new(&config.network, config.prometheus_registry().cloned());
    net_config.add_notification_protocol(sc_consensus_grandpa::grandpa_peers_set_config(
        grandpa_protocol_name.clone(),
    ));

    let warp_sync_provider = NetworkProvider::new(
        backend.clone(),
        grandpa_link.shared_authority_set().clone(),
        vec![],
    );
    let warp_sync_config =
        Some(WarpSyncConfig::WithProvider(Arc::new(warp_sync_provider)));

    let (network, system_rpc_tx, tx_handler_controller, sync_service) =
        sc_service::build_network(sc_service::BuildNetworkParams {
            config: &config,
            net_config,
            client: client.clone(),
            transaction_pool: transaction_pool.clone(),
            spawn_handle: task_manager.spawn_handle(),
            import_queue,
            block_announce_validator_builder: None,
            warp_sync_config,
            block_relay: None,
            metrics: sc_network::NotificationMetrics::new(
                config.prometheus_config.as_ref().map(|cfg| &cfg.registry),
            ),
        })?;

    let role = config.role.clone();
    let force_authoring = config.force_authoring;
    let backoff_authoring_blocks: Option<()> = None;
    let prometheus_registry = config.prometheus_registry().cloned();

    let rpc_extensions_builder = {
        let client = client.clone();
        let pool = transaction_pool.clone();
        let deny_unsafe = match config.rpc.methods {
            RpcMethods::Safe => sc_rpc_api::DenyUnsafe::Yes,
            RpcMethods::Unsafe | RpcMethods::Auto => sc_rpc_api::DenyUnsafe::No,
        };
        Box::new(move |_executor| {
            let deps = crate::rpc::FullDeps {
                client: client.clone(),
                pool: pool.clone(),
                deny_unsafe,
            };
            crate::rpc::create_full(deps).map_err(Into::into)
        })
    };

    let _rpc_handlers = sc_service::spawn_tasks(sc_service::SpawnTasksParams {
        network: Arc::new(network.clone()),
        client: client.clone(),
        keystore: keystore_container.keystore(),
        task_manager: &mut task_manager,
        transaction_pool: transaction_pool.clone(),
        rpc_builder: rpc_extensions_builder,
        backend,
        system_rpc_tx,
        tx_handler_controller,
        sync_service: sync_service.clone(),
        config,
        telemetry: telemetry.as_mut(),
        tracing_execute_block: None,
    })?;

    let grandpa_config = sc_consensus_grandpa::Config {
        gossip_duration: std::time::Duration::from_millis(333),
        justification_period: 512,
        name: Some("abena-grandpa".to_string()),
        observer_enabled: true,
        keystore: None,
        local_role: role.clone(),
        telemetry: telemetry.as_ref().map(|x| x.handle()),
        protocol_name: grandpa_protocol_name,
    };

    let grandpa_network = network.clone();
    let grandpa_client = client.clone();
    let grandpa_keystore = keystore_container.keystore();
    let grandpa_select_chain = select_chain.clone();

    let (grandpa_task, _grandpa_handler) = sc_consensus_grandpa::run_grandpa_voter(
        grandpa_config,
        grandpa_link,
        grandpa_network,
        grandpa_client,
        grandpa_select_chain,
        grandpa_keystore,
        telemetry.as_ref().map(|x| x.handle()),
    )?;
    task_manager
        .spawn_essential_handle()
        .spawn_blocking("grandpa-voter", Some("finality"), grandpa_task);

    if role.is_authority() {
        let proposer_factory = sc_basic_authorship::ProposerFactory::new(
            task_manager.spawn_handle(),
            client.clone(),
            transaction_pool.clone(),
            prometheus_registry.as_ref(),
            telemetry.as_ref().map(|x| x.handle()),
        );

        let slot_duration = sc_consensus_aura::slot_duration(&*client)?;

        let aura = sc_consensus_aura::start_aura::<AuraPair, _, _, _, _, _, _, _, _, _, _>(
            StartAuraParams {
                slot_duration,
                client: client.clone(),
                select_chain,
                block_import: grandpa_block_import,
                proposer_factory,
                create_inherent_data_providers: move |_, ()| async move {
                    let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
                    let slot =
                        sp_consensus_aura::inherents::InherentDataProvider::from_timestamp_and_slot_duration(
                            *timestamp,
                            slot_duration,
                        );
                    Ok((slot, timestamp))
                },
                force_authoring,
                backoff_authoring_blocks,
                keystore: keystore_container.keystore(),
                sync_oracle: sync_service.clone(),
                justification_sync_link: (),
                block_proposal_slot_portion: SlotProportion::new(2f32 / 3f32),
                max_block_proposal_slot_portion: None,
                telemetry: telemetry.as_ref().map(|x| x.handle()),
                compatibility_mode: Default::default(),
            },
        )?;
        task_manager
            .spawn_essential_handle()
            .spawn_blocking("aura", Some("block-authoring"), aura);
    }

    Ok(task_manager)
}
