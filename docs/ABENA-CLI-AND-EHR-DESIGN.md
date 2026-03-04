# ABENA CLI & EHR Connectors – Design

## 1. abena-cli

Deployment and operations CLI for ABENA blockchain nodes (hospital, validator, backup/restore).

### 1.1 Commands

| Command | Purpose |
|---------|---------|
| `abena-cli deploy --type=hospital \| validator \| rpc --org="Mayo Clinic"` | Deploy node with chain spec, keys, config |
| `abena-cli join-network --consortium=us-healthcare [--validator]` | Configure bootnodes, sync, optionally validator keys |
| `abena-cli backup --destination=s3://bucket \| /path` | Snapshot chain DB, compress, upload |
| `abena-cli restore --from=snapshot-20260301 \| s3://bucket/key` | Download, decompress, replace DB |
| `abena-cli status` | Node health, sync status, peers |

### 1.2 Deploy Flow

1. **Generate keys** (optional): `abena-node key generate` for Aura/GRANDPA
2. **Create chain spec** (or use preset): `local`, `dev`, or custom JSON
3. **Write config**: `~/.local/share/abena/` or `./abena-data/`
4. **Start process**: `cargo run -p abena-node -- [args]` or Docker/systemd

### 1.3 Backup Flow

- Use Substrate `ExportState` / raw DB copy
- Compress (gzip)
- Upload to S3 or local path
- Optional: incremental with block height in filename

### 1.4 Tech Stack

- **Language**: Node.js (TypeScript) – orchestrates node binary, AWS CLI, Docker
- **Why Node**: Fast iteration, good AWS/FS APIs, can call `abena-node` via `child_process`

---

## 2. EHR Integration Connectors

Pre-built connectors from EHR systems (Epic, Cerner, Allscripts) to ABENA via FHIR/HL7.

### 2.1 Architecture

```
┌─────────────────┐     HL7v2 / FHIR      ┌──────────────────┐     FHIR R4      ┌─────────────────┐
│  Epic / Cerner  │ ───────────────────►  │  EHR Connector   │ ───────────────► │  ABENA FHIR API │
│  Allscripts     │                        │  (adapter)       │                   │  + Interop      │
└─────────────────┘                        └──────────────────┘                   └─────────────────┘
```

### 2.2 Connector Interface

All connectors implement:

- **Ingest**: Receive data from EHR (FHIR REST, HL7v2, MLLP)
- **Transform**: Normalize to FHIR R4
- **Submit**: POST to ABENA FHIR API or `map_fhir_resource` extrinsic

### 2.3 Connector Types

| Connector | EHR | Protocol | Status |
|-----------|-----|----------|--------|
| **HL7 Base** | Generic | HL7v2 → FHIR R4 | ✅ Implemented |
| **Epic** | Epic | FHIR R4 REST | Stub |
| **Cerner** | Cerner | FHIR R4 REST | Stub |
| **Allscripts** | Allscripts | FHIR R4 REST | Stub |

### 2.4 ABENA Integration Points

- **FHIR API** (`services/fhir-api`): `POST /fhir/Observation`, `GET /fhir/Patient/{id}`
- **Interoperability pallet**: `map_fhir_resource(patient, resource_type, hash, record_id, data_standard)`
- **Data standard**: `HL7_FHIR_R4`, `HL7_V2`, `CDA`, `DICOM`, `IHE_XDS`

### 2.5 HL7v2 → FHIR Mapping

| HL7v2 | FHIR R4 |
|-------|---------|
| ADT^A01 (Admit) | Patient + Encounter |
| ORU^R01 (Result) | Observation |
| ORM^O01 (Order) | ServiceRequest |
| MDM^T02 (Doc) | DiagnosticReport |

### 2.6 Tech Stack

- **Language**: Node.js (TypeScript)
- **HL7v2 parsing**: `hl7-standard` or custom
- **FHIR**: `fhir/r4` types
- **HTTP**: axios / fetch to ABENA FHIR API
