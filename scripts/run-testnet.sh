#!/usr/bin/env bash
# Launch ABENA testnet node
set -e
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec ./target/release/abena-node --chain abena-testnet --tmp "$@"
