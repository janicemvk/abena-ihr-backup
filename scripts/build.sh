#!/usr/bin/env bash
# =============================================================================
# ABENA IHR — Build & Debug Scripts
# DK Technologies, Inc.
# =============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# ─────────────────────────────────────────────────────────────────────────────
# KNOWN BUILD ISSUES & FIXES (from your Substrate debugging history)
# =============================================================================

# ─── Issue 1: Enum index bug ──────────────────────────────────────────────────
# Error: "encoded enum index 4 is invalid" or codec mismatch errors
# Cause: Multiple versions of parity-scale-codec in your dependency tree
# Fix:
#   1. Add to workspace Cargo.toml:
#      [workspace.dependencies]
#      codec = { package = "parity-scale-codec", version = "3.6.1", features = ["derive"] }
#   2. Run: cargo update -p parity-scale-codec
#   3. Check: cargo tree -d -p parity-scale-codec  (should show ZERO duplicates)

# ─── Issue 2: Missing fflonk package ─────────────────────────────────────────
# Error: "package `fflonk` not found" or similar crate registry error
# Cause: Some Substrate versions pull in zero-knowledge proof crates
#        that aren't yet on crates.io
# Fix A (preferred): Use stable2409 branch which doesn't require fflonk:
#   All Cargo.toml entries: branch = "stable2409"
# Fix B: Add to Cargo.toml [patch.crates-io]:
#   fflonk = { git = "https://github.com/paritytech/fflonk", branch = "master" }

# ─── Issue 3: OpenSSL not found (DigitalOcean server) ────────────────────────
# Error: "Could not find directory of OpenSSL installation"
# Fix on Ubuntu (DigitalOcean) — run these commands manually:
#
#   sudo apt-get update
#   sudo apt-get install -y \
#       build-essential \
#       pkg-config \
#       libssl-dev \
#       clang \
#       libclang-dev \
#       protobuf-compiler \
#       git \
#       curl
#
# Verify OpenSSL is findable:
#   pkg-config --libs openssl
#
# If still failing, set explicitly before building:
#   export OPENSSL_DIR=/usr
#   export OPENSSL_INCLUDE_DIR=/usr/include/openssl
#   export OPENSSL_LIB_DIR=/usr/lib/x86_64-linux-gnu
#   export PKG_CONFIG_PATH=/usr/lib/x86_64-linux-gnu/pkgconfig

# ─── Issue 4: WASM build fails / rocksdb compile errors ──────────────────────
# Error: wasm32-unknown-unknown target not installed, or rocksdb C++ errors
# Fix:
#   rustup target add wasm32-unknown-unknown
#   rustup component add rust-src

# ─── Issue 5: Rust version mismatch ──────────────────────────────────────────
# Error: "this compiler is 1.XX but minimum required is 1.YY"
# Fix: rust-toolchain.toml pins to 1.88 — install it:
#   rustup install 1.88
#   rustup override set 1.88

# ─── Issue 6: OpenSSL on Windows (Perl/Locale errors) ─────────────────────────
# Error: "perl reported failure" or "Locale/Maketext/Simple.pm not found"
# Fix: Use system OpenSSL via vcpkg:
#   vcpkg install openssl:x64-windows
#   set VCPKG_ROOT=C:\path\to\vcpkg
#   set OPENSSL_NO_VENDOR=1
# Or build on Linux (recommended for DigitalOcean deploy).

# =============================================================================
# CLEAN BUILD (run this when switching branches or after dependency changes)
# =============================================================================
echo "=== ABENA IHR Clean Build ==="
echo "Project root: $PROJECT_ROOT"
echo ""

# Verify Rust toolchain (1.85+ for edition2024 in transitive deps)
if ! rustc --version 2>/dev/null | grep -qE "1\.(8[5-9]|9[0-9])"; then
    echo "ERROR: Rust 1.85+ required (see rust-toolchain.toml)."
    echo "FIX:  rustup install 1.88 && rustup override set 1.88"
    exit 1
fi

# Nuclear clean (removes all build artifacts)
cargo clean

# Re-fetch dependencies
cargo fetch

# Build in release mode
RUST_LOG=warn cargo build --release 2>&1 | tee /tmp/abena-build.log

echo ""
echo "Build complete. Binary at: ./target/release/abena-node"
echo ""

# =============================================================================
# LAUNCH TESTNET (after successful build)
# =============================================================================
echo "=== To start ABENA Public Testnet, run: ==="
echo ""
echo "./target/release/abena-node \\"
echo "    --base-path /var/lib/abena \\"
echo "    --chain abena-testnet \\"
echo "    --validator \\"
echo "    --name \"ABENA-Testnet-Node-1\" \\"
echo "    --port 30333 \\"
echo "    --rpc-port 9944 \\"
echo "    --rpc-cors all \\"
echo "    --rpc-methods Unsafe \\"
echo "    --log info \\"
echo "    --telemetry-url \"wss://telemetry.polkadot.io/submit/ 0\""
echo ""
echo "For dev/local testing:"
echo "  ./target/release/abena-node --chain abena-testnet --tmp"
echo ""

# =============================================================================
# INSERT SESSION KEYS (run ONCE per validator after starting the node)
# =============================================================================
echo "=== Insert keys (run in another terminal while node is running): ==="
echo ""
echo "# Insert Aura key"
echo "curl -sS -H \"Content-Type: application/json\" \\"
echo "    --data '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"author_insertKey\",\"params\":[\"aura\",\"YOUR_SECRET_SEED//aura\",\"YOUR_AURA_PUBLIC_KEY\"]}' \\"
echo "    http://localhost:9944"
echo ""
echo "# Or use CLI (Aura + Grandpa for validators):"
echo "  ./target/release/abena-node key insert --chain abena-testnet --suri '//Alice' --key-type aura"
echo "  ./target/release/abena-node key insert --chain abena-testnet --suri '//Alice' --key-type gran"
echo "  ./target/release/abena-node key insert --chain abena-testnet --suri '//Bob' --key-type aura"
echo "  ./target/release/abena-node key insert --chain abena-testnet --suri '//Bob' --key-type gran"
echo ""
echo "Keys inserted. Restart the node to activate validator."
echo ""

# =============================================================================
# VERIFY ABENA COIN IS LIVE
# =============================================================================
echo "=== Verify ABENA Coin: ==="
echo "  1. Polkadot.js Apps: https://polkadot.js.org/apps?rpc=ws://127.0.0.1:9944"
echo "  2. Chain properties: tokenSymbol=ABENA, tokenDecimals=12"
echo "  3. Accounts tab: balances in ABENA"
echo ""
echo "# Or wscat:"
echo "  wscat -c wss://testnet.abenihr.com"
echo "  {\"id\":1,\"jsonrpc\":\"2.0\",\"method\":\"chain_getHeader\",\"params\":[]}"
echo ""

echo "=== Done ==="
