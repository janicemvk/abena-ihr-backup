# abena-epic-connector

Epic FHIR to ABENA blockchain bridge.

## Install

```bash
cd connectors/python/abena_epic_connector
pip install -e .
pip install websockets  # for async RPC
```

## Usage

```python
from abena_epic_connector import ABENAEpicBridge

bridge = ABENAEpicBridge(
    epic_fhir_endpoint="https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4",
    abena_endpoint="wss://hospital.abena-ihr.com",
    epic_token="your-oauth-token",
)

# Sync patient by MRN to blockchain
did = bridge.sync_patient_to_blockchain(
    patient_mrn="MRN-12345",
    signer_ss58="5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
    emergency_contact_ss58=None,
)
print(f"ABENA DID: {did}")

# Lookup DID from MRN
did = bridge.lookup_did("MRN-12345")
```

## MRN ↔ DID mapping

Stored in `./abena-epic-links.json` (or `ABENA_LINKS_PATH`).
