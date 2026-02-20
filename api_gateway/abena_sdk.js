// Mock Abena SDK for Module Registry
// This provides the interface that the module registry expects

class AbenaSDK {
    constructor(config = {}) {
        this.config = config;
        this.authServiceUrl = config.authServiceUrl || 'http://localhost:3001';
        this.dataServiceUrl = config.dataServiceUrl || 'http://localhost:8001';
        this.privacyServiceUrl = config.privacyServiceUrl || 'http://localhost:8002';
        this.blockchainServiceUrl = config.blockchainServiceUrl || 'http://localhost:8003';
    }

    async logBlockchainAccess(resource, action, context, metadata) {
        // Mock blockchain logging
        console.log(`Module Registry: Blockchain log: ${action} on ${resource}`, metadata);
        return { txId: 'mock-tx-' + Date.now() };
    }

    async storeData(collection, id, data, context) {
        // Mock data storage
        console.log(`Module Registry: Storing data in ${collection}:`, { id, data, context });
        return { success: true, id };
    }

    async updateData(collection, id, data, context) {
        // Mock data update
        console.log(`Module Registry: Updating data in ${collection}:`, { id, data, context });
        return { success: true };
    }

    async getData(collection, id, context) {
        // Mock data retrieval
        console.log(`Module Registry: Getting data from ${collection}:`, { id, context });
        return { success: true, data: { mock: 'data' } };
    }

    getLogger() {
        // Mock logger
        return {
            info: (message, data) => console.log('Module Registry INFO:', message, data),
            error: (message, data) => console.error('Module Registry ERROR:', message, data),
            warn: (message, data) => console.warn('Module Registry WARN:', message, data),
            debug: (message, data) => console.log('Module Registry DEBUG:', message, data)
        };
    }

    async recordMetric(name, value, tags) {
        // Mock metrics recording
        console.log(`Module Registry Metric: ${name} = ${value}`, tags);
        return { success: true };
    }
}

module.exports = AbenaSDK; 