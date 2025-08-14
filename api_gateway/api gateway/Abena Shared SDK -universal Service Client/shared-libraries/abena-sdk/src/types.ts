// Core SDK Types and Interfaces

export interface AbenaConfig {
  authServiceUrl: string;
  dataServiceUrl: string;
  privacyServiceUrl: string;
  blockchainServiceUrl: string;
  apiKey?: string;
  timeout?: number;
}

export interface PatientData {
  patientId: string;
  demographics: any;
  healthRecords: any[];
  consents: any[];
  accessLog: any[];
}

export interface User {
  id: string;
  email: string;
  role: string;
  firstName: string;
  lastName: string;
}

export interface AccessResult {
  granted: boolean;
  riskScore: number;
  conditions: string[];
  reason: string;
}

export interface VitalSigns {
  patientId: string;
  timestamp: string;
  bloodPressure?: {
    systolic: number;
    diastolic: number;
  };
  heartRate?: number;
  temperature?: number;
  respiratoryRate?: number;
  oxygenSaturation?: number;
  weight?: number;
  height?: number;
}

export interface LabResult {
  patientId: string;
  testId: string;
  testName: string;
  result: string;
  unit?: string;
  referenceRange?: {
    low: number;
    high: number;
  };
  timestamp: string;
  status: 'normal' | 'abnormal' | 'critical';
}

export interface Medication {
  patientId: string;
  medicationId: string;
  name: string;
  dosage: string;
  frequency: string;
  startDate: string;
  endDate?: string;
  prescribedBy: string;
  status: 'active' | 'discontinued' | 'completed';
}

export interface HealthRecord {
  recordId: string;
  patientId: string;
  recordType: 'medication' | 'lab_result' | 'vitals' | 'diagnosis' | 'procedure' | 'allergy';
  timestamp: string;
  providerId: string;
  data: any;
  metadata?: any;
}

export interface Consent {
  consentId: string;
  patientId: string;
  providerId: string;
  purpose: string;
  granted: boolean;
  grantedAt: string;
  expiresAt?: string;
  scope: string[];
}

export interface AuditLog {
  logId: string;
  patientId: string;
  userId: string;
  action: string;
  timestamp: string;
  purpose: string;
  riskScore: number;
  blockchainTxId?: string;
  metadata?: any;
}

export interface AnonymizationConfig {
  anonymizationType: 'k-anonymity' | 'differential-privacy';
  quasiIdentifiers: string[];
  kValue?: number;
  epsilon?: number;
}

export interface DatasetCriteria {
  patientCohort?: string[];
  dateRange?: {
    from: string;
    to: string;
  };
  recordTypes?: string[];
  includeFields?: string[];
}

export interface PatientContext {
  patient: any;
  healthRecords: any[];
  riskFactors: any[];
  medications: any[];
  allergies: any[];
  vitals: any[];
  labResults: any[];
  auditInfo: {
    accessGranted: boolean;
    riskScore: number;
    blockchainTxId: string;
  };
}

export interface ServiceHealth {
  [service: string]: boolean;
}

// Error types
export class AbenaSDKError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'AbenaSDKError';
  }
}

export class AccessDeniedError extends AbenaSDKError {
  constructor(message: string, details?: any) {
    super(message, 'ACCESS_DENIED', 403, details);
    this.name = 'AccessDeniedError';
  }
}

export class ServiceUnavailableError extends AbenaSDKError {
  constructor(service: string, details?: any) {
    super(`Service ${service} is unavailable`, 'SERVICE_UNAVAILABLE', 503, details);
    this.name = 'ServiceUnavailableError';
  }
}

export class ValidationError extends AbenaSDKError {
  constructor(message: string, details?: any) {
    super(message, 'VALIDATION_ERROR', 400, details);
    this.name = 'ValidationError';
  }
} 