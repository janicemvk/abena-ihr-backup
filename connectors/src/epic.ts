/**
 * Epic EHR connector (FHIR R4 REST)
 * Stub - implements base interface, forwards to ABENA FHIR API
 */

import axios from 'axios';
import * as crypto from 'crypto';
import { BaseEHRConnector, IngestResult } from './base';
import type { FHIRResourceType } from './types';

export interface EpicConfig {
  fhirBaseUrl: string;
  clientId?: string;
  clientSecret?: string;
}

export class EpicConnector extends BaseEHRConnector {
  private epicConfig?: EpicConfig;

  constructor(config: import('./types').ABENAFhirApiConfig, epicConfig?: EpicConfig) {
    super(config);
    this.epicConfig = epicConfig;
  }

  /** Ingest FHIR resource from Epic and submit to ABENA */
  async ingest(data: unknown): Promise<IngestResult> {
    const resource = typeof data === 'object' && data !== null ? (data as Record<string, unknown>) : {};
    const resourceType = (resource.resourceType as FHIRResourceType) || 'Observation';
    const fhir = this.toFhir(data);
    return this.submitToAbena(fhir, resourceType);
  }

  toFhir(data: unknown): Record<string, unknown> {
    if (typeof data === 'object' && data !== null && 'resourceType' in (data as object)) {
      return data as Record<string, unknown>;
    }
    return { resourceType: 'Unknown' };
  }

  /** Fetch resource from Epic FHIR API (stub - requires OAuth) */
  async fetchFromEpic(resourceType: string, id: string): Promise<Record<string, unknown> | null> {
    if (!this.epicConfig?.fhirBaseUrl) return null;
    try {
      const res = await axios.get(`${this.epicConfig.fhirBaseUrl}/${resourceType}/${id}`);
      return res.data as Record<string, unknown>;
    } catch {
      return null;
    }
  }

  private async submitToAbena(fhir: Record<string, unknown>, resourceType: FHIRResourceType): Promise<IngestResult> {
    try {
      const baseUrl = this.getFhirBaseUrl();
      const hash = '0x' + crypto.createHash('sha256').update(JSON.stringify(fhir)).digest('hex');

      const endpoint = resourceType === 'Patient' ? 'Patient' : resourceType === 'Observation' ? 'Observation' : 'Observation';
      await axios.post(`${baseUrl}/fhir/${endpoint}`, fhir);

      return { success: true, resourceType, hash };
    } catch (err: unknown) {
      return {
        success: false,
        resourceType,
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }
}
