/**
 * ABENACernerBridge - Real-time lab result sync from Cerner to ABENA
 */

import axios from 'axios';
import * as crypto from 'crypto';
import { EventEmitter } from 'events';

export interface CernerCredentials {
  baseUrl: string;
  clientId?: string;
  clientSecret?: string;
  accessToken?: string;
}

export interface LabResultPayload {
  patientId: string;
  data: Record<string, unknown> | string;
  resourceType?: string;
}

export interface ABENACernerBridgeConfig {
  cernerAuth: CernerCredentials;
  abenaNode: string;
  abenaFhirApi?: string;
  /** MRN/Cerner patientId -> ABENA DID mapping */
  identifierMap?: Map<string, string>;
}

export class ABENACernerBridge extends EventEmitter {
  private config: ABENACernerBridgeConfig;
  private identifierMap: Map<string, string> = new Map();

  constructor(config: ABENACernerBridgeConfig) {
    super();
    this.config = config;
    if (config.identifierMap) {
      this.identifierMap = config.identifierMap;
    }
  }

  /** Register MRN/patientId -> ABENA DID mapping */
  registerIdentifier(cernerPatientId: string, abenaDid: string): void {
    this.identifierMap.set(cernerPatientId, abenaDid);
  }

  /** Lookup ABENA DID from Cerner patient ID / MRN */
  async lookupDID(patientId: string): Promise<string | null> {
    return this.identifierMap.get(patientId) ?? null;
  }

  /** Handle new lab result from Cerner (call from your Cerner webhook/poll) */
  async onNewLabResult(result: LabResultPayload): Promise<{ success: boolean; hash?: string; error?: string }> {
    this.emit('newLabResult', result);

    const did = await this.lookupDID(result.patientId);
    if (!did) {
      this.emit('error', new Error(`No ABENA DID for patient ${result.patientId}`));
      return { success: false, error: 'Patient not linked to ABENA' };
    }

    return this.storeLabResult({
      patientDID: did,
      labData: result.data,
      hash: this.sha3(result.data),
    });
  }

  /** Store lab result on ABENA (health record hash + optional IPFS) */
  private async storeLabResult(params: {
    patientDID: string;
    labData: Record<string, unknown> | string;
    hash: string;
    ipfsCID?: string;
  }): Promise<{ success: boolean; hash?: string; error?: string }> {
    try {
      const dataStr = typeof params.labData === 'string' ? params.labData : JSON.stringify(params.labData);
      const hashHex = params.hash.startsWith('0x') ? params.hash : '0x' + params.hash;

      const fhirApi = this.config.abenaFhirApi ?? `http://${this.config.abenaNode.replace('wss://', '').replace('ws://', '').replace(':9944', ':3000')}`;
      const extensions: Array<{ url: string; valueString: string }> = [
        { url: 'urn:abena:hash', valueString: hashHex },
      ];
      if (params.ipfsCID) {
        extensions.push({ url: 'urn:abena:ipfs', valueString: params.ipfsCID });
      }
      const observation = {
        resourceType: 'Observation',
        status: 'final',
        subject: { reference: `Patient/${params.patientDID}` },
        code: { coding: [{ system: 'http://loinc.org', code: '58410-2', display: 'Lab results' }] },
        valueString: dataStr,
        meta: { extension: extensions },
      };

      const res = await axios.post(`${fhirApi}/fhir/Observation`, observation);
      return { success: res.status < 300, hash: hashHex };
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      this.emit('error', err);
      return { success: false, error: msg };
    }
  }

  private sha3(data: Record<string, unknown> | string): string {
    const str = typeof data === 'string' ? data : JSON.stringify(data);
    return '0x' + crypto.createHash('sha256').update(str).digest('hex');
  }

  /** Start polling Cerner for new results (stub - implement per Cerner API) */
  startPolling(intervalMs: number = 60000): void {
    this.emit('pollingStarted');
    // In production: poll Cerner FHIR Observation API, filter by lastUpdated,
    // emit newLabResult for each new result
  }

  /** Stop polling */
  stopPolling(): void {
    this.emit('pollingStopped');
  }
}
