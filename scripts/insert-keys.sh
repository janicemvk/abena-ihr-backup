#!/usr/bin/env bash
# Insert Aura (and optionally Grandpa) keys for ABENA testnet validators
# Run with: ./scripts/insert-keys.sh [chain]
# chain: dev | local | abena-testnet (default: local)
CHAIN="${1:-local}"

cd "$(dirname "${BASH_SOURCE[0]}")/.."
NODE="./target/release/abena-node"

echo "Inserting Aura keys for chain=$CHAIN"
$NODE key insert --chain "$CHAIN" --suri '//Alice' --key-type aura
$NODE key insert --chain "$CHAIN" --suri '//Bob' --key-type aura
echo "Done. Restart the node to produce blocks."
