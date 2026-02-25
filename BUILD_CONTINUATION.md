# Build continuation – steps completed and next steps

## Completed in this session

1. **pallet-account-management**
   - Removed duplicate `#[derive(Clone, ...)]` on `AccountTier` (kept `Clone, Copy, Encode, Decode, PartialEq, Eq, RuntimeDebug, TypeInfo, MaxEncodedLen`).
   - `DepositInfo` and events already use the same balance type (`BalanceOf<T>` / `Currency::Balance`).

2. **pallet-interoperability**
   - Fixed syntax: added missing newline between `use sp_runtime::BoundedVec;` and the `/// Configuration trait` comment.

3. **pallet-governance**
   - Removed duplicate `#[scale_info(skip_type_params(T))]` on `GuidelineProposal`, `ProtocolProposal`, and `EmergencyIntervention`.

4. **pallet-patient-health-records**
   - Added `MaxEncodedLen` to `EncryptionMetadataRecord` (used in storage; all fields are bounded).

5. **pallet-patient-identity**
   - Normalized whitespace between the `#[pallet::call]` impl and the helper `impl<T: Config> Pallet<T>` (no structural change; brace count was already correct in this version).

6. **pallet-treatment-protocol**
   - Fixed unclosed delimiter: added the missing `}` to close the helper `impl<T: Config> Pallet<T>` block (so the `impl` that contains `check_compliance` and `check_contraindications` is properly closed before `WeightInfo` and the type definitions).

## What you need to do next

### 1. Patch the SDK (sc-network enum indices)

The Polkadot SDK `Message` enum in `sc-network` can have duplicate `#[codec(index)]` values, which breaks the build. Apply the fix by running the project fix script from the repo root (PowerShell):

```powershell
.\fix-all-errors-v2.ps1
```

That script:

- Finds `message.rs` under `%USERPROFILE%\.cargo\git\checkouts\polkadot-sdk-*`
- Sets unique indices for `RemoteCallRequest` (7), `RemoteCallResponse` (8), `RemoteReadRequest` (9), `RemoteReadResponse` (10).

If the build still reports duplicate codec indices, open that `message.rs` and assign **unique** `#[codec(index = N)]` to every variant of the `Message` enum (no two variants may share the same N).

### 2. Build

From the workspace root:

```bash
cargo build --release
```

First run can take a long time (10+ minutes). If new errors appear, fix them in this order:

- **sc-network** – duplicate `#[codec(index)]` in `message.rs` (see above).
- **pallet-account-management** – any remaining type/event issues (balance type should already be consistent).
- **Other pallets** – follow the compiler messages (e.g. missing traits, wrong types).

### 3. After a successful build

- Start the node: `./target/release/abena-node --dev --tmp` (or `.\target\release\abena-node.exe --dev --tmp` on Windows).
- Generate CLI metadata (with node running):  
  `subxt codegen --url ws://127.0.0.1:9944 > cli/src/runtime_types.rs`  
  Then wire the CLI to use the generated types.

## Optional: run fix script from project root

If you haven’t run it yet:

```powershell
cd "C:\Users\Jan Marie\Abena Blockchain"
.\fix-all-errors-v2.ps1
cargo build --release
```

## Reference

- **Patient-identity**: Implemented to spec; tests pass.
- **Pallets**: patient-health-records, health-record-hash, quantum-computing, abena-coin, treatment-protocol, interoperability, governance, fee-management, access-control, account-management.
- **Runtime**: `runtime/src/lib.rs`; **node**: `node/`; **CLI**: `cli/`.
