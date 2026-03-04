/**
 * Base EHR Connector interface
 */

import type { ABENAFhirApiConfig, FHIRResourceType } from './types';

export interface IngestResult {
  success: boolean;
  resourceType: FHIRResourceType;
  resourceId?: string;
  hash?: string;
  error?: string;
}

export abstract class BaseEHRConnector {
  constructor(protected config: ABENAFhirApiConfig) {}

  /** Ingest data from EHR (FHIR or HL7v2) and submit to ABENA */
  abstract ingest(data: unknown): Promise<IngestResult | IngestResult[]>;

  /** Transform raw EHR data to FHIR R4 JSON */
  abstract toFhir(data: unknown): Record<string, unknown>;

  protected getFhirBaseUrl(): string {
    const port = this.config.fhirApiPort ?? 3000;
    const base = this.config.baseUrl.replace(/\/$/, '');
    return base.includes(':') ? base : `${base}:${port}`;
  }
}
