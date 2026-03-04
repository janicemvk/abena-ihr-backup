# ABENA FHIR API Service

Off-chain REST API bridging HL7 FHIR clients to the ABENA blockchain. Queries chain state, fetches from IPFS, and returns FHIR R4–compliant JSON.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/fhir/Patient/{id}` | Query blockchain, return FHIR Patient JSON |
| POST | `/fhir/Observation` | Store on blockchain, emit event |
| GET | `/fhir/DiagnosticReport/{id}` | Fetch from IPFS, verify hash |
| GET | `/health` | Health check |

## Configuration

| Env | Default | Description |
|-----|---------|-------------|
| `ABENA_WS_URL` | `ws://127.0.0.1:9944` | Substrate node WebSocket URL |
| `IPFS_GATEWAY` | `https://ipfs.io/ipfs/` | IPFS gateway for content fetch |
| `FHIR_API_PORT` | `3000` | HTTP listen port |
| `RUST_LOG` | `info` | Log level |

## Run

```bash
# Start ABENA node first
cargo run -p abena-node -- --dev

# In another terminal, start FHIR API
cargo run -p fhir-api
```

## Integration status

- [x] Endpoint scaffold (GET Patient, POST Observation, GET DiagnosticReport)
- [x] `to_fhir_patient` stub
- [ ] RPC: PatientIdentity + FHIRResources queries
- [ ] IPFS fetch + decrypt for metadata
- [ ] Extrinsic submission (map_fhir_resource)
- [ ] OAuth2/OIDC provider authorization
