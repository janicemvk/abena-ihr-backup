// Mock Abena SDK for development
// This provides the interface that the background modules expect

class AbenaSDK {
    constructor(config = {}) {
        this.config = config;
        this.authServiceUrl = config.authServiceUrl || 'http://localhost:3001';
        this.dataServiceUrl = config.dataServiceUrl || 'http://localhost:8001';
        this.privacyServiceUrl = config.privacyServiceUrl || 'http://localhost:8002';
        this.blockchainServiceUrl = config.blockchainServiceUrl || 'http://localhost:8003';
    }

    async verifyRequest(request) {
        // Mock authentication verification
        return { success: true, user: { id: 'mock-user', role: 'admin' } };
  }

    async getPatientData(patientId, context, options = {}) {
        // Mock patient data retrieval
    return {
            patient: {
                id: patientId,
                name: 'Mock Patient',
                status: 'active'
            },
            healthRecords: [],
            consents: [],
            auditLog: []
    };
  }

    async storeData(collection, id, data, context) {
        // Mock data storage
        console.log(`Storing data in ${collection}:`, { id, data, context });
        return { success: true, id };
    }

    async updateData(collection, id, data, context) {
        // Mock data update
        console.log(`Updating data in ${collection}:`, { id, data, context });
        return { success: true };
  }

    async logBlockchainAccess(resource, action, context, metadata) {
        // Mock blockchain logging
        console.log(`Blockchain log: ${action} on ${resource}`, metadata);
        return { txId: 'mock-tx-' + Date.now() };
    }

    async callModuleAPI(moduleName, endpoint, data) {
        // Mock inter-module communication
        console.log(`Calling ${moduleName}${endpoint}:`, data);
        return { success: true, data: { mock: 'response' } };
  }

    async subscribeToModuleEvents(moduleName, event, callback) {
        // Mock event subscription
        console.log(`Subscribing to ${moduleName} events: ${event}`);
        return { success: true };
    }

    getLogger() {
        // Mock logger
    return {
            info: (message, data) => console.log('INFO:', message, data),
            error: (message, data) => console.error('ERROR:', message, data),
            warn: (message, data) => console.warn('WARN:', message, data),
            debug: (message, data) => console.log('DEBUG:', message, data)
        };
    }

    async recordMetric(name, value, tags) {
        // Mock metrics recording
        console.log(`Metric: ${name} = ${value}`, tags);
        return { success: true };
  }

    async getAccessToken() {
        // Mock access token
        return 'mock-jwt-token-' + Date.now();
  }
}

// Export the SDK
export default AbenaSDK; 