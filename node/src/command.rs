//! ABENA IHR Node — Command Dispatcher
//!
//! Routes CLI subcommands to the appropriate service or utility function.

use crate::chain_spec;
use crate::cli::{Cli, Subcommand};
use clap::Parser;
use sc_cli::SubstrateCli;

impl SubstrateCli for Cli {
    fn impl_name() -> String {
        "ABENA IHR Node".into()
    }

    fn impl_version() -> String {
        env!("SUBSTRATE_CLI_IMPL_VERSION").into()
    }

    fn description() -> String {
        env!("CARGO_PKG_DESCRIPTION").into()
    }

    fn author() -> String {
        env!("CARGO_PKG_AUTHORS").into()
    }

    fn support_url() -> String {
        "https://github.com/janicemvk/abena-ihr-backup/issues".into()
    }

    fn copyright_start_year() -> i32 {
        2025
    }

    fn load_spec(&self, id: &str) -> Result<Box<dyn sc_service::ChainSpec>, String> {
        Ok(match id {
            // Dev chain: single Alice validator, dev endowments
            "dev" | "" => Box::new(chain_spec::development_config()?),

            // Local two-validator testnet
            "local" => Box::new(chain_spec::local_testnet_config()?),

            // Public testnet at wss://testnet.abenihr.com
            "abena-testnet" | "testnet" => Box::new(chain_spec::abena_testnet_config()?),

            // Load a custom chain spec from file path
            path => Box::new(chain_spec::ChainSpec::from_json_file(
                std::path::PathBuf::from(path),
            )?),
        })
    }
}

/// Parse CLI args and dispatch to the appropriate command.
pub fn run() -> sc_cli::Result<()> {
    let cli = Cli::parse();

    match &cli.subcommand {
        // ── Utility subcommands ──────────────────────────────────────────
        Some(Subcommand::Key(cmd)) => cmd.run(&cli),

        Some(Subcommand::BuildSpec(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.sync_run(|config| cmd.run(config.chain_spec, config.network))
        }
        Some(Subcommand::CheckBlock(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let crate::service::NewPartial { client, task_manager, import_queue, .. } =
                    crate::service::new_partial(&config)?;
                Ok((cmd.run(client, import_queue), task_manager))
            })
        }
        Some(Subcommand::ExportBlocks(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let crate::service::NewPartial { client, task_manager, .. } =
                    crate::service::new_partial(&config)?;
                Ok((cmd.run(client, config.database), task_manager))
            })
        }
        Some(Subcommand::ExportState(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let crate::service::NewPartial { client, task_manager, .. } =
                    crate::service::new_partial(&config)?;
                Ok((cmd.run(client, config.chain_spec), task_manager))
            })
        }
        Some(Subcommand::ImportBlocks(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let crate::service::NewPartial { client, task_manager, import_queue, .. } =
                    crate::service::new_partial(&config)?;
                Ok((cmd.run(client, import_queue), task_manager))
            })
        }
        Some(Subcommand::PurgeChain(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.sync_run(|config| cmd.run(config.database))
        }
        Some(Subcommand::Revert(cmd)) => {
            let runner = cli.create_runner(cmd)?;
            runner.async_run(|config| {
                let crate::service::NewPartial { client, task_manager, backend, .. } =
                    crate::service::new_partial(&config)?;
                let aux_revert = Box::new(|client, _, blocks| {
                    sc_consensus_grandpa::revert(client, blocks)?;
                    Ok(())
                });
                Ok((cmd.run(client, backend, Some(aux_revert)), task_manager))
            })
        }
        // ── Main node run ────────────────────────────────────────────────
        None => {
            let runner = cli.create_runner(&cli.run)?;
            runner.run_node_until_exit(|config| async move {
                match config.network.network_backend {
                    sc_network::config::NetworkBackendType::Libp2p => crate::service::new_full::<
                        sc_network::NetworkWorker<
                            abena_runtime::opaque::Block,
                            <abena_runtime::opaque::Block as sp_runtime::traits::Block>::Hash,
                        >,
                    >(config)
                    .map_err(sc_cli::Error::Service),
                    sc_network::config::NetworkBackendType::Litep2p => {
                        crate::service::new_full::<sc_network::Litep2pNetworkBackend>(config)
                            .map_err(sc_cli::Error::Service)
                    }
                }
            })
        }

        // ── Benchmarking (feature-gated) ─────────────────────────────────
        #[cfg(feature = "runtime-benchmarks")]
        Some(Subcommand::Benchmark(cmd)) => {
            use crate::service::{FullBackend, FullClient};
            let runner = cli.create_runner(cmd)?;
            runner.sync_run(|config| {
                let crate::service::NewPartial { client, backend, .. } =
                    crate::service::new_partial(&config)?;
                cmd.run::<abena_runtime::Block, FullClient>(client, backend)
            })
        }

    }
}
