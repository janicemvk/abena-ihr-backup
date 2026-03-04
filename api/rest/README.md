# REST API

REST API layer for the ABENA blockchain: chain state, extrinsics submission, and health-record queries.

## FHIR API Service

Off-chain HL7 FHIR bridge at `services/fhir-api/`:

- `GET  /fhir/Patient/{id}` — Query blockchain, return FHIR Patient JSON
- `POST /fhir/Observation` — Store on blockchain, emit event
- `GET  /fhir/DiagnosticReport/{id}` — Fetch from IPFS, verify hash

Run: `cargo run -p fhir-api` (see `services/fhir-api/README.md`).

## Planned (general REST)

- Chain state (balances, identity, record hashes)
- Submit extrinsics (patient registration, record hash, access control)
- Query by patient ID, record ID, block range

Integrates with `runtime` and `node` (RPC).

