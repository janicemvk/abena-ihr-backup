#!/bin/bash
# Fix path dependencies in patched sc-network (block-builder, primitives, etc.)
# Run from project root after setup-sc-network-patch.sh copies substrate/client/network.

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MAIN_CARGO="patches/sc-network/Cargo.toml"
SYNC_CARGO="patches/sc-network/sync/Cargo.toml"

if [ ! -f "$MAIN_CARGO" ]; then
  echo "Error: $MAIN_CARGO not found. Run setup-sc-network-patch.sh first."
  exit 1
fi

echo "Patching $MAIN_CARGO dev-dependencies (no ../block-builder — use workspace/git)..."
# Main crate: replace monorepo paths with workspace / git (matches root Cargo.toml [workspace.dependencies])
sed -i 's|sc-block-builder = { default-features = true, path = "../block-builder" }|sc-block-builder = { workspace = true }|' "$MAIN_CARGO"
sed -i 's|sp-crypto-hashing = { default-features = true, path = "../../primitives/crypto/hashing" }|sp-crypto-hashing = { workspace = true, default-features = true }|' "$MAIN_CARGO"
sed -i 's|sp-consensus = { default-features = true, path = "../../primitives/consensus/common" }|sp-consensus = { workspace = true, default-features = true }|' "$MAIN_CARGO"
sed -i 's|sp-test-primitives = { path = "../../primitives/test-primitives" }|sp-test-primitives = { workspace = true }|' "$MAIN_CARGO"
sed -i 's|sp-tracing = { default-features = true, path = "../../primitives/tracing" }|sp-tracing = { workspace = true, default-features = true }|' "$MAIN_CARGO"
sed -i 's|substrate-test-runtime = { path = "../../test-utils/runtime" }|substrate-test-runtime = { workspace = true }|' "$MAIN_CARGO"
sed -i 's|substrate-test-runtime-client = { path = "../../test-utils/runtime/client" }|substrate-test-runtime-client = { workspace = true }|' "$MAIN_CARGO"

if [ -f "$SYNC_CARGO" ]; then
  echo "Patching $SYNC_CARGO..."
  sed -i 's|sc-block-builder = { default-features = true, path = "../../block-builder" }|sc-block-builder = { workspace = true }|' "$SYNC_CARGO"
  sed -i 's|sp-tracing = { default-features = true, path = "../../../primitives/tracing" }|sp-tracing = { workspace = true }|' "$SYNC_CARGO"
  sed -i 's|sp-test-primitives = { path = "../../../primitives/test-primitives" }|sp-test-primitives = { git = "https://github.com/paritytech/polkadot-sdk.git", tag = "polkadot-stable2409" }|' "$SYNC_CARGO"
  sed -i 's|substrate-test-runtime-client = { path = "../../../test-utils/runtime/client" }|substrate-test-runtime-client = { git = "https://github.com/paritytech/polkadot-sdk.git", tag = "polkadot-stable2409" }|' "$SYNC_CARGO"
fi

echo "Done. Ensure root Cargo.toml lists all [workspace.dependencies] for sc-network. Then: cargo build --release -p abena-node"
