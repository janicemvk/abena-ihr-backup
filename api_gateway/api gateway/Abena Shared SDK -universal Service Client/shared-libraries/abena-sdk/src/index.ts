// Universal SDK for all Abena IHR modules

import axios, { AxiosInstance } from 'axios';

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

export class AbenaSDK {
  private authClient: AxiosInstance;
  private dataClient: AxiosInstance;
  private privacyClient: AxiosInstance;
  private blockchainClient: AxiosInstance;
  private currentToken: string | null = null;

  constructor(private config: AbenaConfig) {
    // Create axios instances for each service
    this.authClient = axios.create({
      baseURL: config.authServiceUrl,
      timeout: config.timeout || 10000,
    });

    this.dataClient = axios.create({
      baseURL: config.dataServiceUrl,
      timeout: config.timeout || 30000,
    });

    this.privacyClient = axios.create({
      baseURL: config.privacyServiceUrl,
      timeout: config.timeout || 10000,
    });

    this.blockchainClient = axios.create({
      baseURL: config.blockchainServiceUrl,
      timeout: config.timeout || 15000,
    });

    // Add auth interceptors to all clients
    this.setupAuthInterceptors();
  }

  private setupAuthInterceptors() {
    const addAuthHeader = (config: any) => {
      if (this.currentToken) {
        config.headers.Authorization = `Bearer ${this.currentToken}`;
      }
      return config;
    };

    this.dataClient.interceptors.request.use(addAuthHeader);
    this.privacyClient.interceptors.request.use(addAuthHeader);
    this.blockchainClient.interceptors.request.use(addAuthHeader);
  }

  // ================================
  // AUTHENTICATION METHODS
  // ================================
  
  async login(email: string, password: string, mfaToken?: string): Promise<{ user: User; token: string }> {
    const response = await this.authClient.post('/auth/login', {
      email,
      password,
      mfaToken
    });
    
    this.currentToken = response.data.token;
    return response.data;
  }

  async verifyToken(token: string): Promise<User> {
    this.currentToken = token;
    const response = await this.authClient.get('/auth/profile');
    return response.data;
  }

  async validateServiceAccess(patientId: string, action: string, service: string): Promise<AccessResult> {
    const response = await this.authClient.post('/auth/validate-access', {
      patientId,
      action,
      service
    });
    return response.data;
  }

  // ================================
  // UNIFIED DATA ACCESS METHODS
  // ================================

  async getPatientData(
    patientId: string, 
    purpose: string,
    options: {
      includeRecords?: boolean;
      includeConsents?: boolean;
      includeAuditLog?: boolean;
      emergency?: boolean;
    } = {}
  ): Promise<PatientData> {
    
    // 1. Validate access first
    const access = await this.validateServiceAccess(patientId, 'read', 'data_access');
    
    if (!access.granted) {
      throw new Error(`Access denied: ${access.reason}`);
    }

    // 2. Get unified patient data
    const response = await this.dataClient.get(`/patients/${patientId}`, {
      params: {
        purpose,
        include_records: options.includeRecords !== false,
        include_consents: options.includeConsents !== false,
        include_audit: options.includeAuditLog !== false,
        emergency: options.emergency || false
      }
    });

    // 3. Log access to blockchain
    await this.logBlockchainAccess(patientId, 'READ', purpose, {
      riskScore: access.riskScore,
      conditions: access.conditions
    });

    return response.data;
  }

  async getPatientHealthRecords(
    patientId: string,
    filters: {
      recordType?: string;
      dateFrom?: string;
      dateTo?: string;
      providerId?: string;
    } = {}
  ): Promise<any[]> {
    
    const access = await this.validateServiceAccess(patientId, 'read', 'health_records');
    if (!access.granted) {
      throw new Error(`Access denied: ${access.reason}`);
    }

    const response = await this.dataClient.get(`/patients/${patientId}/records`, {
      params: filters
    });

    await this.logBlockchainAccess(patientId, 'READ_RECORDS', 'clinical_analysis', filters);

    return response.data.records;
  }

  // ================================
  // PRIVACY & SECURITY METHODS
  // ================================

  async encryptSensitiveData(data: any, dataType: string, patientId?: string): Promise<string> {
    const response = await this.privacyClient.post('/encrypt', {
      data,
      data_type: dataType,
      patient_id: patientId,
      purpose: 'data_protection'
    });
    return response.data.encrypted_data;
  }

  async decryptSensitiveData(encryptedData: string, keyId: string, purpose: string): Promise<any> {
    const response = await this.privacyClient.post('/decrypt', {
      encrypted_data: encryptedData,
      encryption_key_id: keyId,
      purpose
    });
    return response.data.decrypted_data;
  }

  async anonymizeDataset(dataset: any[], config: {
    anonymizationType: 'k-anonymity' | 'differential-privacy';
    quasiIdentifiers: string[];
    kValue?: number;
    epsilon?: number;
  }): Promise<any[]> {
    const response = await this.privacyClient.post('/anonymize', {
      dataset,
      anonymization_type: config.anonymizationType,
      quasi_identifiers: config.quasiIdentifiers,
      k_value: config.kValue || 5,
      epsilon: config.epsilon || 1.0
    });
    return response.data.anonymized_data;
  }

  async checkPatientConsent(patientId: string, providerId: string, purpose: string): Promise<boolean> {
    const response = await this.privacyClient.get('/check-consent', {
      params: { patientId, providerId, purpose }
    });
    return response.data.hasConsent;
  }

  // ================================
  // BLOCKCHAIN METHODS
  // ================================

  async logBlockchainAccess(
    patientId: string, 
    action: string, 
    purpose: string, 
    metadata?: any
  ): Promise<string> {
    try {
      const response = await this.blockchainClient.post(`/records/${patientId}/access`, {
        purpose,
        action,
        metadata
      });
      return response.data.blockchain_tx_id;
    } catch (error) {
      console.warn('Blockchain logging failed:', error);
      return ''; // Don't fail the main operation if blockchain is down
    }
  }

  async verifyDataIntegrity(recordId: string): Promise<boolean> {
    try {
      const response = await this.blockchainClient.get(`/blockchain/verify/${recordId}`);
      return response.data.verified;
    } catch (error) {
      console.warn('Blockchain verification failed:', error);
      return false;
    }
  }

  async getAuditTrail(patientId: string, dateFrom?: string, dateTo?: string): Promise<any[]> {
    const response = await this.blockchainClient.get(`/patients/${patientId}/audit`, {
      params: { dateFrom, dateTo }
    });
    return response.data.audit_trail;
  }

  // ================================
  // DATA INGESTION METHODS
  // ================================

  async ingestVitalSigns(vitalSigns: any): Promise<string> {
    const response = await this.dataClient.post('/ingest/vitals', vitalSigns);
    return response.data.message_id;
  }

  async ingestLabResults(labResults: any): Promise<string> {
    const response = await this.dataClient.post('/ingest/lab-results', labResults);
    return response.data.message_id;
  }

  async ingestHL7Message(hl7Message: any): Promise<string> {
    const response = await this.dataClient.post('/ingest/hl7', hl7Message);
    return response.data.message_id;
  }

  async ingestFHIRResource(fhirResource: any): Promise<string> {
    const response = await this.dataClient.post('/ingest/fhir', fhirResource);
    return response.data.message_id;
  }

  // ================================
  // CONVENIENCE METHODS FOR MODULES
  // ================================

  /**
   * Complete patient context for clinical modules
   * Handles all security, privacy, and audit automatically
   */
  async getCompletePatientContext(
    patientId: string, 
    userId: string, 
    purpose: string,
    emergencyAccess: boolean = false
  ): Promise<{
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
  }> {

    // Validate access
    const access = await this.validateServiceAccess(patientId, 'read', purpose);
    
    if (!access.granted && !emergencyAccess) {
      throw new Error(`Access denied: ${access.reason}`);
    }

    // Get comprehensive patient data
    const patientData = await this.getPatientData(patientId, purpose, {
      includeRecords: true,
      includeConsents: true,
      includeAuditLog: true,
      emergency: emergencyAccess
    });

    // Get specific record types
    const healthRecords = await this.getPatientHealthRecords(patientId, {});
    
    // Categorize records by type
    const medications = healthRecords.filter(r => r.record_type === 'medication');
    const vitals = healthRecords.filter(r => r.record_type === 'vitals');
    const labResults = healthRecords.filter(r => r.record_type === 'lab_result');
    
    // Log comprehensive access
    const blockchainTxId = await this.logBlockchainAccess(
      patientId, 
      'COMPLETE_CONTEXT_ACCESS', 
      purpose,
      {
        emergency: emergencyAccess,
        recordCount: healthRecords.length,
        riskScore: access.riskScore
      }
    );

    return {
      patient: patientData,
      healthRecords,
      riskFactors: [], // Would be computed by clinical modules
      medications,
      allergies: [], // Would be extracted from records
      vitals,
      labResults,
      auditInfo: {
        accessGranted: access.granted || emergencyAccess,
        riskScore: access.riskScore,
        blockchainTxId
      }
    };
  }

  /**
   * Secure data processing for analytics modules
   */
  async getAnonymizedDataset(
    criteria: {
      patientCohort?: string[];
      dateRange?: { from: string; to: string };
      recordTypes?: string[];
      includeFields?: string[];
    },
    anonymizationConfig: {
      type: 'k-anonymity' | 'differential-privacy';
      kValue?: number;
      epsilon?: number;
    }
  ): Promise<any[]> {

    // Get raw dataset (requires research permissions)
    const response = await this.dataClient.post('/analytics/dataset', criteria);
    const rawDataset = response.data.dataset;

    // Anonymize the dataset
    const anonymizedDataset = await this.anonymizeDataset(rawDataset, {
      anonymizationType: anonymizationConfig.type,
      quasiIdentifiers: ['age', 'gender', 'zip_code'], // Standard quasi-identifiers
      kValue: anonymizationConfig.kValue,
      epsilon: anonymizationConfig.epsilon
    });

    // Log analytics access
    await this.logBlockchainAccess(
      'analytics_cohort',
      'ANONYMIZED_DATASET_ACCESS',
      'research_analytics',
      {
        recordCount: anonymizedDataset.length,
        anonymizationType: anonymizationConfig.type,
        criteria
      }
    );

    return anonymizedDataset;
  }

  // ================================
  // ERROR HANDLING & UTILITIES
  // ================================

  async healthCheck(): Promise<{ [service: string]: boolean }> {
    const services = {
      auth: this.authClient,
      data: this.dataClient,
      privacy: this.privacyClient,
      blockchain: this.blockchainClient
    };

    const healthStatus: { [service: string]: boolean } = {};

    for (const [name, client] of Object.entries(services)) {
      try {
        await client.get('/health');
        healthStatus[name] = true;
      } catch {
        healthStatus[name] = false;
      }
    }

    return healthStatus;
  }

  setAuthToken(token: string) {
    this.currentToken = token;
  }

  clearAuthToken() {
    this.currentToken = null;
  }
}

// Export types and SDK
export default AbenaSDK; 