/**
 * Cerner EHR connector (FHIR R4 REST)
 * Stub - same pattern as Epic
 */

import { EpicConnector } from './epic';
import type { ABENAFhirApiConfig } from './types';

export interface CernerConfig {
  fhirBaseUrl: string;
  clientId?: string;
  clientSecret?: string;
}

/** Cerner uses FHIR R4 REST - same interface as Epic */
export class CernerConnector extends EpicConnector {
  constructor(config: ABENAFhirApiConfig, cernerConfig?: CernerConfig) {
    super(config, cernerConfig);
  }
}
