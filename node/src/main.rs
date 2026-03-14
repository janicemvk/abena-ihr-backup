//! ABENA IHR Node — Binary Entry Point
//!
//! DK Technologies, Inc.
//!
//! Usage:
//!   abena-node --dev                          # local dev chain
//!   abena-node --chain=local                  # local two-validator testnet
//!   abena-node --chain=abena-testnet          # public testnet
//!   abena-node --chain=abena-testnet --validator  # validator mode

#![warn(missing_docs)]

mod chain_spec;
mod cli;
mod command;
mod rpc;
mod service;

fn main() -> sc_cli::Result<()> {
    command::run()
}

