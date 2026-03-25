# Server build checklist (abena-testnet)

When building on the server (`~/abena-ihr-backup`), ensure:

## 1. patches/sc-network exists

The node and `[patch]` both use `patches/sc-network` (relative to workspace root). You need a patched copy of sc-network there.

**Quick setup (run from project root):**
```bash
chmod +x scripts/setup-sc-network-patch.sh
./scripts/setup-sc-network-patch.sh
```
This copies from `/root/patches/sc-network` if it exists, otherwise clones from the SDK.

**Option A – Copy from existing patch:**
```bash
mkdir -p ~/abena-ihr-backup/patches
cp -r /root/patches/sc-network ~/abena-ihr-backup/patches/
```

**Option B – Clone and patch from SDK:**
```bash
mkdir -p ~/abena-ihr-backup/patches
git clone --depth 1 --branch polkadot-stable2409 \
  https://github.com/paritytech/polkadot-sdk.git /tmp/sdk
cp -r /tmp/sdk/substrate/client/network ~/abena-ihr-backup/patches/sc-network
# Apply the message.rs enum index fix (indices 7–15 for RemoteCallRequest etc.)
```

## 2. Root Cargo.toml is up to date

Pull the latest changes so the workspace `[workspace.dependencies]` includes all sc-network-related crates:

```bash
cd ~/abena-ihr-backup
git pull   # or sync your Cargo.toml manually
```

## 3. Build

```bash
cd ~/abena-ihr-backup
cargo build --release -p abena-node
```

## If "fork-tree was not found in workspace.dependencies"

The root `Cargo.toml` must have `fork-tree` and the other SDK crates in `[workspace.dependencies]`. If the error persists after `git pull`, copy the updated root `Cargo.toml` from your local project.

## sc-network duplicate / wrong `#[codec(index = …)]`

The repo includes a fixed `patches/sc-network/src/protocol/message.rs` (indices 7–15 after `Consensus`). After `git pull`, overwrite the server copy:

```bash
# from your laptop (example)
scp "path/to/abena-ihr-backup/patches/sc-network/src/protocol/message.rs" \
  root@abena-testnet:~/abena-ihr-backup/patches/sc-network/src/protocol/message.rs
```

Or run locally / on CI: `python3 scripts/apply-sc-network-enum-fix.py` (requires the unpatched SDK `message.rs` in that path).
