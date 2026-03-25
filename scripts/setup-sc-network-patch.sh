#!/bin/bash
# Set up patches/sc-network for the sc-network enum-index fix.
# Run from project root: ./scripts/setup-sc-network-patch.sh

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PATCH_DIR="patches/sc-network"
SDK_TAG="polkadot-stable2409"

# If /root/patches/sc-network exists (typical on abena-testnet), copy it
if [ -d "/root/patches/sc-network" ]; then
  echo "Copying from /root/patches/sc-network..."
  mkdir -p patches
  rm -rf "$PATCH_DIR"
  cp -r /root/patches/sc-network "$PATCH_DIR"
else
  echo "Cloning polkadot-sdk ($SDK_TAG) to create patch..."
  TMP=$(mktemp -d)
  git clone --depth 1 --branch "$SDK_TAG" \
    https://github.com/paritytech/polkadot-sdk.git "$TMP/sdk"

  mkdir -p patches
  rm -rf "$PATCH_DIR"
  cp -r "$TMP/sdk/substrate/client/network" "$PATCH_DIR"
  rm -rf "$TMP"
fi

if [ -f "./scripts/fix-patch-paths.sh" ]; then
  bash ./scripts/fix-patch-paths.sh
fi
if command -v python3 >/dev/null 2>&1; then
  python3 ./scripts/apply-sc-network-enum-fix.py
fi

echo "Updating lockfile for sc-network-types (matches polkadot-stable2409)..."
cargo update -p sc-network-types 2>/dev/null || true

echo "Done. Next: cargo build --release -p abena-node"
