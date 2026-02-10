// Mock Abena SDK for Business Rules Engine
// This provides the interface that the business rules expect

class AbenaSDK {
    constructor(config = {}) {
        this.config = config;
        this.authServiceUrl = config.authServiceUrl || 'http://localhost:3001';
        this.dataServiceUrl = config.dataServiceUrl || 'http://localhost:8001';
        this.privacyServiceUrl = config.privacyServiceUrl || 'http://localhost:8002';
        this.blockchainServiceUrl = config.blockchainServiceUrl || 'http://localhost:8003';
    }

    async storeData(collection, id, data, context) {
        // Mock data storage
        console.log(`Business Rules: Storing data in ${collection}:`, { id, data, context });
        return { success: true, id };
    }

    async updateData(collection, id, data, context) {
        // Mock data update
        console.log(`Business Rules: Updating data in ${collection}:`, { id, data, context });
        return { success: true };
    }

    async getData(collection, id, context) {
        // Mock data retrieval
        console.log(`Business Rules: Getting data from ${collection}:`, { id, context });
        return { success: true, data: { mock: 'data' } };
    }

    async logBlockchainAccess(resource, action, context, metadata) {
        // Mock blockchain logging
        console.log(`Business Rules: Blockchain log: ${action} on ${resource}`, metadata);
        return { txId: 'mock-tx-' + Date.now() };
    }

    async verifyRequest(request) {
        // Mock authentication verification
        return { success: true, user: { id: 'mock-user', role: 'admin' } };
    }

    getLogger() {
        // Mock logger
        return {
            info: (message, data) => console.log('Business Rules INFO:', message, data),
            error: (message, data) => console.error('Business Rules ERROR:', message, data),
            warn: (message, data) => console.warn('Business Rules WARN:', message, data),
            debug: (message, data) => console.log('Business Rules DEBUG:', message, data)
        };
    }

    async recordMetric(name, value, tags) {
        // Mock metrics recording
        console.log(`Business Rules Metric: ${name} = ${value}`, tags);
        return { success: true };
    }

    async getAccessToken() {
        // Mock access token
        return 'mock-jwt-token-' + Date.now();
    }
}

export default AbenaSDK; 