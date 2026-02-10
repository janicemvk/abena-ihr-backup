/**
 * Migration Example: From Custom Auth/Database to Abena SDK
 * 
 * This file demonstrates the migration from custom authentication and database
 * management to using the unified Abena SDK.
 */

// ============================================================================
// BEFORE (❌ Wrong - has its own auth/data):
// ============================================================================

// AFTER (✅ Correct - uses Abena SDK):
const AbenaSDK = require('../lib/abena-sdk');

class SomeModuleAbena {
  constructor() {
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003'
    });
  }

  async someMethod(patientId, userId) {
    // 1. Auto-handled auth & permissions
    const patientData = await this.abena.getPatientData(patientId, 'module_purpose');
    // 2. Auto-handled privacy & encryption
    // 3. Auto-handled audit logging
    // 4. Focus on your business logic
    return this.processData(patientData);
  }
}

// ============================================================================
// REAL-WORLD MIGRATION EXAMPLES:
// ============================================================================

// Example 1: Patient Data Access
class PatientDataModule {
  constructor() {
    this.abena = new AbenaSDK({
      authServiceUrl: process.env.AUTH_SERVICE_URL || 'http://localhost:3001',
      dataServiceUrl: process.env.DATA_SERVICE_URL || 'http://localhost:8001',
      privacyServiceUrl: process.env.PRIVACY_SERVICE_URL || 'http://localhost:8002',
      blockchainServiceUrl: process.env.BLOCKCHAIN_SERVICE_URL || 'http://localhost:8003'
    });
  }

  async getPatientProfile(patientId) {
    // All auth, privacy, and audit handled automatically
    const patientData = await this.abena.getPatientData(patientId, 'patient_profile_view');
    return this.formatPatientProfile(patientData);
  }

  async updatePatientData(patientId, updates) {
    // All auth, privacy, audit, and blockchain handled automatically
    const result = await this.abena.savePatientData(patientId, updates, 'patient_data_update');
    return result;
  }

  formatPatientProfile(data) {
    return {
      id: data.patientId,
      name: `${data.firstName} ${data.lastName}`,
      dateOfBirth: data.dateOfBirth,
      conditions: data.medicalHistory.map(h => h.condition),
      medications: data.medications.map(m => m.name)
    };
  }
}

// Example 2: Clinical Data Access
class ClinicalDataModule {
  constructor() {
    this.abena = new AbenaSDK({
      authServiceUrl: process.env.AUTH_SERVICE_URL || 'http://localhost:3001',
      dataServiceUrl: process.env.DATA_SERVICE_URL || 'http://localhost:8001',
      privacyServiceUrl: process.env.PRIVACY_SERVICE_URL || 'http://localhost:8002',
      blockchainServiceUrl: process.env.BLOCKCHAIN_SERVICE_URL || 'http://localhost:8003'
    });
  }

  async getLabResults(patientId) {
    // All auth, privacy, and audit handled automatically
    const labData = await this.abena.getClinicalData(patientId, 'lab_results', 'clinical_review');
    return this.formatLabResults(labData);
  }

  async getVitalSigns(patientId) {
    // All auth, privacy, and audit handled automatically
    const vitalData = await this.abena.getClinicalData(patientId, 'vital_signs', 'clinical_review');
    return this.formatVitalSigns(vitalData);
  }

  formatLabResults(data) {
    return {
      patientId: data.patientId,
      results: data.results.map(r => ({
        test: r.test,
        value: r.value,
        unit: r.unit,
        date: r.date
      }))
    };
  }

  formatVitalSigns(data) {
    return {
      patientId: data.patientId,
      vitals: data.results
    };
  }
}

// Example 3: User Management
class UserManagementModule {
  constructor() {
    this.abena = new AbenaSDK({
      authServiceUrl: process.env.AUTH_SERVICE_URL || 'http://localhost:3001',
      dataServiceUrl: process.env.DATA_SERVICE_URL || 'http://localhost:8001',
      privacyServiceUrl: process.env.PRIVACY_SERVICE_URL || 'http://localhost:8002',
      blockchainServiceUrl: process.env.BLOCKCHAIN_SERVICE_URL || 'http://localhost:8003'
    });
  }

  async getUserProfile(userId) {
    // All auth, privacy, and audit handled automatically
    const userData = await this.abena.getUserData(userId, 'user_profile_view');
    return this.formatUserProfile(userData);
  }

  formatUserProfile(data) {
    return {
      id: data.userId,
      name: `${data.firstName} ${data.lastName}`,
      email: data.email,
      role: data.role,
      specialty: data.specialty
    };
  }
}

// Export examples for use
module.exports = {
  SomeModuleAbena,
  PatientDataModule,
  ClinicalDataModule,
  UserManagementModule
}; 