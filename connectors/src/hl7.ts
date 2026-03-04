/**
 * HL7v2 to FHIR R4 connector
 */

import axios from 'axios';
import * as crypto from 'crypto';
import { BaseEHRConnector, IngestResult } from './base';
import type { FHIRResourceType } from './types';

function parseHL7Message(raw: string): Record<string, string[]> {
  const segments: Record<string, string[]> = {};
  const lines = raw.split(/\r?\n/).filter(Boolean);
  for (const line of lines) {
    const type = line.slice(0, 3);
    const fields = line.split('|').slice(1);
    segments[type] = fields;
  }
  return segments;
}

function getMessageType(segments: Record<string, string[]>): string {
  const msh = segments['MSH'];
  return msh?.[8] ?? '';
}

function adtToPatient(segments: Record<string, string[]>): Record<string, unknown> {
  const pid = segments['PID'] ?? [];
  const name = pid[5] ? pid[5].split('^') : [];
  return {
    resourceType: 'Patient',
    identifier: pid[2] ? [{ value: pid[2] }] : [],
    name: [{ family: name[0] || '', given: [name[1]].filter(Boolean) }],
    birthDate: pid[7] || undefined,
    gender: pid[8] === 'M' ? 'male' : pid[8] === 'F' ? 'female' : 'unknown',
  };
}

function oruToObservation(
  _segments: Record<string, string[]>,
  obr: string[],
  obx: string[]
): Record<string, unknown> {
  return {
    resourceType: 'Observation',
    status: 'final',
    code: obr[3] ? { coding: [{ code: obr[3].split('^')[0], display: obr[3].split('^')[1] }] } : {},
    subject: obr[2] ? { reference: `Patient/${obr[2]}` } : {},
    valueQuantity: obx[4] ? { value: parseFloat(obx[4]) || obx[4], unit: obx[5] } : undefined,
  };
}

function hashFhir(resource: Record<string, unknown>): string {
  return crypto.createHash('sha256').update(JSON.stringify(resource)).digest('hex');
}

export class HL7Connector extends BaseEHRConnector {
  ingest(data: unknown): Promise<IngestResult> {
    const raw = typeof data === 'string' ? data : String(data);
    const segments = parseHL7Message(raw);
    const msgType = getMessageType(segments);

    let fhir: Record<string, unknown>;
    let resourceType: FHIRResourceType;

    if (msgType.startsWith('ADT^')) {
      fhir = adtToPatient(segments);
      resourceType = 'Patient';
    } else if (msgType.startsWith('ORU^')) {
      const obr = segments['OBR'] ?? [];
      const obx = segments['OBX'] ?? obr;
      fhir = oruToObservation(segments, obr, obx);
      resourceType = 'Observation';
    } else {
      return Promise.resolve({
        success: false,
        resourceType: 'Observation',
        error: `Unsupported HL7 message type: ${msgType}`,
      });
    }

    return this.submitToAbena(fhir, resourceType);
  }

  toFhir(data: unknown): Record<string, unknown> {
    const raw = typeof data === 'string' ? data : String(data);
    const segments = parseHL7Message(raw);
    const msgType = getMessageType(segments);

    if (msgType.startsWith('ADT^')) return adtToPatient(segments);
    if (msgType.startsWith('ORU^')) {
      const obr = segments['OBR'] ?? [];
      const obx = segments['OBX'] ?? obr;
      return oruToObservation(segments, obr, obx);
    }
    return { resourceType: 'Unknown' };
  }

  private async submitToAbena(fhir: Record<string, unknown>, resourceType: FHIRResourceType): Promise<IngestResult> {
    try {
      const baseUrl = this.getFhirBaseUrl();
      const hash = hashFhir(fhir);

      if (resourceType === 'Observation') {
        const res = await axios.post(`${baseUrl}/fhir/Observation`, fhir);
        return {
          success: res.status < 300,
          resourceType,
          hash: '0x' + hash,
        };
      }

      return { success: true, resourceType, hash: '0x' + hash };
    } catch (err: unknown) {
      return {
        success: false,
        resourceType,
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }
}
