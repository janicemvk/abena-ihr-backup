# ABENA Blockchain CLI Tool

A command-line interface for interacting with the ABENA healthcare blockchain.

## Installation

```bash
cd cli
cargo build --release
```

## Usage

### Prerequisites

1. Build and run the ABENA node:
```bash
# From project root
cargo build --release
./target/release/abena-node --dev --tmp
```

2. The node should be running on `ws://127.0.0.1:9944` (default)

### Commands

#### Register a Patient

```bash
./target/release/abena-cli register-patient \
    <ACCOUNT_ADDRESS> \
    --public-key <32_BYTE_HEX> \
    --metadata-hash <32_BYTE_HEX> \
    [--emergency-contact <CONTACT_ADDRESS>]
```

Example:
```bash
./target/release/abena-cli register-patient \
    5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY \
    --public-key 0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20 \
    --metadata-hash 202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f40
```

#### Update Consent

```bash
./target/release/abena-cli update-consent \
    <PATIENT_ACCOUNT> \
    --modality <MODALITY> \
    --granted <true|false> \
    [--expires-at <TIMESTAMP>]
```

Modalities: `WesternMedicine`, `TCM`, `Ayurveda`, `Homeopathy`, `Naturopathy`, `Other`

Example:
```bash
./target/release/abena-cli update-consent \
    5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY \
    --modality WesternMedicine \
    --granted true
```

#### Grant Provider Access

```bash
./target/release/abena-cli grant-provider-access \
    <PATIENT_ACCOUNT> \
    <PROVIDER_ACCOUNT> \
    --access-level <Read|ReadWrite|Emergency> \
    [--expires-at <TIMESTAMP>]
```

Example:
```bash
./target/release/abena-cli grant-provider-access \
    5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY \
    5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty \
    --access-level Read
```

#### Revoke Provider Access

```bash
./target/release/abena-cli revoke-provider-access \
    <PATIENT_ACCOUNT> \
    <PROVIDER_ACCOUNT>
```

#### Query Patient Identity

```bash
./target/release/abena-cli query-patient <PATIENT_ACCOUNT>
```

#### Verify Provider Access

```bash
./target/release/abena-cli verify-access \
    <PATIENT_ACCOUNT> \
    <PROVIDER_ACCOUNT>
```

## Development Notes

This is currently a template CLI. To make it fully functional:

1. **Generate Runtime Metadata**:
```bash
subxt codegen --url ws://127.0.0.1:9944 > src/runtime_types.rs
```

2. **Add Account Management**:
   - Use `subxt`'s account management features
   - Load private keys securely
   - Sign transactions before submission

3. **Implement Actual Calls**:
   - Use the generated types from step 1
   - Create proper transaction builders
   - Handle errors and display results

4. **Add Query Functionality**:
   - Use subxt's storage query API
   - Parse and display results nicely

## Example Workflow

```bash
# 1. Start the node
./target/release/abena-node --dev --tmp

# 2. Register a patient (in another terminal)
./target/release/abena-cli register-patient \
    5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY \
    --public-key $(echo -n "patient-public-key" | xxd -p -l 32) \
    --metadata-hash $(echo -n "patient-metadata" | sha256sum | cut -d' ' -f1)

# 3. Query the patient
./target/release/abena-cli query-patient \
    5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY

# 4. Grant consent
./target/release/abena-cli update-consent \
    5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY \
    --modality WesternMedicine \
    --granted true
```

## Security Notes

- Never commit private keys to version control
- Use environment variables or secure key management for production
- Validate all inputs before submitting transactions
- Always verify transaction results


