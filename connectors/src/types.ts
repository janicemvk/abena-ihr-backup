/**
 * EHR Connector types - FHIR R4 and ABENA interoperability
 */

export type FHIRResourceType =
  | 'Patient'
  | 'Observation'
  | 'Condition'
  | 'Medication'
  | 'Procedure'
  | 'DiagnosticReport'
  | 'Encounter';

export type DataStandard = 'HL7_FHIR_R4' | 'HL7_V2' | 'CDA' | 'DICOM' | 'IHE_XDS';

export interface ABENAFhirApiConfig {
  baseUrl: string;
  fhirApiPort?: number;
  wsUrl?: string;
}

export interface MapFhirResourcePayload {
  patient: string;
  resourceType: FHIRResourceType;
  resourceHash: string;
  blockchainRecordId: string;
  dataStandard: DataStandard;
}
