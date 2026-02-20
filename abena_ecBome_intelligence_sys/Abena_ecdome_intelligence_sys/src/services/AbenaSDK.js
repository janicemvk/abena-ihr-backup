// Mock Abena SDK for development
class AbenaSDK {
  constructor(config = {}) {
    this.authServiceUrl = config.authServiceUrl || 'http://localhost:3001';
    this.dataServiceUrl = config.dataServiceUrl || 'http://localhost:8001';
    this.privacyServiceUrl = config.privacyServiceUrl || 'http://localhost:8002';
    this.blockchainServiceUrl = config.blockchainServiceUrl || 'http://localhost:8003';
    this.ecbomeServiceUrl = config.ecbomeServiceUrl || 'http://localhost:8004';
    this.correlationEngineUrl = config.correlationEngineUrl || 'http://localhost:8005';
    this.patternRecognitionUrl = config.patternRecognitionUrl || 'http://localhost:8006';
    this.predictiveModelingUrl = config.predictiveModelingUrl || 'http://localhost:8007';
  }

  async getPatientData(patientId, dataType) {
    // Mock patient data
    return {
      patientId: patientId || 'TEST123',
      name: 'Test Patient',
      status: 'demo',
      dataType: dataType
    };
  }

  async getHistoricalData(module, patientId, options) {
    // Mock historical data
    return [];
  }

  async saveModuleData(module, data) {
    // Mock save operation
    return { success: true, message: 'Data saved successfully' };
  }

  async authenticate(credentials) {
    // Mock authentication
    return { success: true, token: 'mock-token' };
  }
}

export default AbenaSDK;
