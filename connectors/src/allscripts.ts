/**
 * Allscripts EHR connector (FHIR R4 REST)
 * Stub - same pattern as Epic
 */

import { EpicConnector } from './epic';
import type { ABENAFhirApiConfig } from './types';

export interface AllscriptsConfig {
  fhirBaseUrl: string;
  clientId?: string;
  clientSecret?: string;
}

/** Allscripts uses FHIR R4 REST - same interface as Epic */
export class AllscriptsConnector extends EpicConnector {
  constructor(config: ABENAFhirApiConfig, allscriptsConfig?: AllscriptsConfig) {
    super(config, allscriptsConfig);
  }
}
