# ABENA Blockchain – Repository Structure

Target layout and mapping to current paths.

## Target structure (records / canonical layout)

```
abena-blockchain/
├── pallets/
│   ├── patient-identity/
│   ├── health-records/
│   ├── quantum-results/
│   ├── treatment-protocol/
│   ├── abena-coin/
│   ├── interoperability/
│   └── governance/
├── runtime/
│   └── abena-runtime.rs
├── node/
│   └── abena-node.rs
├── api/
│   ├── rest/
│   └── websocket/
├── cryptography/
│   ├── kyber/
│   ├── dilithium/
│   └── key-management/
└── clinical-modules/
    ├── module-001-symptom-checker/
    ├── module-002-drug-interactions/
    ├── ...
    └── module-150-integrative-protocols/
```

## Current mapping

| Target | Current location | Notes |
|--------|------------------|--------|
| **pallets/patient-identity/** | `pallets/patient-identity/` | ✅ Same |
| **pallets/health-records/** | `pallets/health-record-hash/` + `pallets/patient-health-records/` | Two pallets: hashes + IPFS pointers, and encrypted metadata + access |
| **pallets/quantum-results/** | `pallets/quantum-computing/` | Same role; pallet name is `quantum-computing` |
| **pallets/treatment-protocol/** | `pallets/treatment-protocol/` | ✅ Same |
| **pallets/abena-coin/** | `pallets/abena-coin/` | ✅ Same |
| **pallets/interoperability/** | `pallets/interoperability/` | ✅ Same |
| **pallets/governance/** | `pallets/governance/` | ✅ Same |
| **runtime/abena-runtime.rs** | `runtime/src/lib.rs` | Runtime entry is `runtime/src/lib.rs` |
| **node/abena-node.rs** | `node/src/main.rs` | Node entry is `node/src/main.rs` |
| **api/rest/** | `api/rest/` | ✅ Added (placeholder) |
| **api/websocket/** | `api/websocket/` | ✅ Added (placeholder) |
| **cryptography/kyber/** | `cryptography/kyber/` | ✅ Added (placeholder) |
| **cryptography/dilithium/** | `cryptography/dilithium/` | ✅ Added (placeholder) |
| **cryptography/key-management/** | `cryptography/key-management/` | ✅ Added (placeholder) |
| **clinical-modules/** | `clinical-modules/` | ✅ Added; example modules 001, 002, 150 |

## Additional pallets (beyond target list)

Present in repo and used by runtime:

- `pallets/access-control/` – patient/institutional permissions, emergency access, audit log
- `pallets/account-management/` – account lifecycle
- `pallets/fee-management/` – fee and economic parameters

These support the same Tier 3 / records model; the target diagram focuses on the core records-related pallets.

