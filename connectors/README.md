# @abena/ehr-connectors

EHR integration connectors for ABENA blockchain.

## Connectors

| Connector | EHR | Status |
|-----------|-----|--------|
| HL7Connector | Generic HL7v2 | Implemented |
| ABENACernerBridge | Cerner Millennium | Event-driven lab sync |
| EpicConnector | Epic | Stub |
| CernerConnector | Cerner | Stub |
| AllscriptsConnector | Allscripts | Stub |

## ABENACernerBridge – Real-time lab sync

```typescript
import { ABENACernerBridge } from '@abena/ehr-connectors';

const cernerToABENA = new ABENACernerBridge({
  cernerAuth: {
    baseUrl: 'https://fhir.cerner.com/r4/ecard',
    accessToken: '...',
  },
  abenaNode: 'wss://hospital.abena-ihr.com',
  abenaFhirApi: 'http://localhost:3000',
});

// Link Cerner patient ID to ABENA DID
cernerToABENA.registerIdentifier('cerner-patient-123', '5GrwvaEF...');

// Handle new lab results (from Cerner webhook or polling)
cernerToABENA.on('newLabResult', async (result) => {
  const did = await cernerToABENA.lookupDID(result.patientId);
  if (did) {
    await cernerToABENA.onNewLabResult(result);
  }
});

const result = await cernerToABENA.onNewLabResult({
  patientId: 'cerner-patient-123',
  data: { loinc: '58410-2', value: '120', unit: 'mg/dL' },
});
```

## HL7Connector

```typescript
import { HL7Connector } from '@abena/ehr-connectors';

const hl7 = new HL7Connector({ baseUrl: 'http://localhost:3000' });
const result = await hl7.ingest(hl7v2Message);
```

## HL7 Message Types

- ADT^A01 (Admit) → FHIR Patient
- ORU^R01 (Result) → FHIR Observation
