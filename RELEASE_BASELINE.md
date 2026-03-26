# ABENA baseline (testnet / build-stable)

This document freezes what the repository is **intended** to build and ship on the current SDK line.

## SDK

- **polkadot-sdk** tag: `polkadot-stable2409` (see workspace `Cargo.toml` and `runtime/Cargo.toml` git dependencies).

## Runtime

- **Crate**: `abena-ihr-runtime` (library name `abena_runtime`).
- **`spec_version`**: `100` (increment when runtime logic changes).
- **Pallets in `construct_runtime!`**: `frame_system`, `pallet_timestamp`, `pallet_aura`, `pallet_grandpa`, `pallet_balances`, `pallet_transaction_payment`, `pallet_sudo`, `pallet_abena_rewards`, `pallet_abena_fee_abstraction`.

## Workspace members (Rust)

- `node`, `runtime`, `pallets/abena-rewards`, `pallets/abena-fee-abstraction`, `patches/sc-network` (+ `light`, `sync`).

## Deferred / not in this baseline

- Pallets under `pallets/` that are **not** workspace members (e.g. health-record, access-control) are **not** compiled with the main runtime until explicitly ported to the same SDK tag and wired into `runtime` + workspace.

## CI (GitHub Actions)

- Workflow: `.github/workflows/ci.yml` — **Ubuntu**, Rust **1.88** + `wasm32-unknown-unknown`, runs `scripts/fix-sp-io-no-mangle.sh`, then `cargo test -p abena-ihr-runtime` and `cargo build -p abena-node --release`.
- This is the most **versatile** check: same environment as many servers, no local Windows WASM toolchain required. For local runs on Windows, use **WSL2** (Linux) or rely on CI after pushing.

## Tag suggestion

After a green CI run (or `cargo build -p abena-node --release` on Linux), tag the commit (example): `abena-node-build-ok` or `v0.1-testnet`.
