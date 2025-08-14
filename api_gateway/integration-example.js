/**
 * Abena IHR Module Integration Example
 * Demonstrates how modules communicate through the API gateway
 */

const { AbenaSDK } = require('@abena/sdk');

class AbenaIntegrationExample {
    constructor() {
        this.sdk = new AbenaSDK({
            authServiceUrl: process.env.AUTH_SERVICE_URL || 'http://localhost:3001',
            dataServiceUrl: process.env.DATA_SERVICE_URL || 'http://localhost:8001',
            privacyServiceUrl: process.env.PRIVACY_SERVICE_URL || 'http://localhost:8002',
            blockchainServiceUrl: process.env.BLOCKCHAIN_SERVICE_URL || 'http://localhost:8003'
        });
        
        this.apiGatewayUrl = process.env.API_GATEWAY_URL || 'http://localhost:80';
    }

    /**
     * Example: Complete patient health analysis workflow
     * This demonstrates how multiple modules work together
     */
    async performCompleteHealthAnalysis(patientId, userId) {
        console.log('🚀 Starting complete health analysis for patient:', patientId);

        try {
            // Step 1: Start background monitoring modules
            console.log('📊 Starting background monitoring modules...');
            const backgroundResult = await this.callModuleAPI('background-modules', '/api/v1/modules/start', {
                patientId,
                userId
            });

            if (!backgroundResult.success) {
                throw new Error('Failed to start background modules');
            }

            // Step 2: Get patient data from IHR system
            console.log('📋 Retrieving patient data from IHR...');
            const patientData = await this.callModuleAPI('abena-ihr', `/api/v1/patients/${patientId}`, {});

            // Step 3: Get biomarker data
            console.log('🔬 Retrieving biomarker data...');
            const biomarkerData = await this.callModuleAPI('biomarker-integration', `/api/v1/biomarkers/${patientId}`, {});

            // Step 4: Perform eCdome intelligence analysis
            console.log('🧠 Performing eCdome intelligence analysis...');
            const ecdomeAnalysis = await this.callModuleAPI('ecdome-intelligence', '/api/v1/analysis/ecbome', {
                patientId,
                biomarkerData: biomarkerData.data,
                patientData: patientData.data
            });

            // Step 5: Get comprehensive background analysis
            console.log('📈 Getting comprehensive background analysis...');
            const backgroundAnalysis = await this.callModuleAPI('background-modules', '/api/v1/analysis', {
                patientId,
                includeEcbome: true
            });

            // Step 6: Process through business rules
            console.log('⚖️ Processing through business rules...');
            const ruleResults = await this.callModuleAPI('business-rules', '/api/v1/conflicts/process', {
                patientId,
                analysisData: {
                    background: backgroundAnalysis.data,
                    ecdome: ecdomeAnalysis.data,
                    biomarkers: biomarkerData.data
                }
            });

            // Step 7: Generate unified report
            console.log('📋 Generating unified report...');
            const unifiedReport = await this.callModuleAPI('unified-integration', '/api/v1/orchestration/coordinate', {
                patientId,
                modules: {
                    background: backgroundAnalysis.data,
                    ecdome: ecdomeAnalysis.data,
                    biomarkers: biomarkerData.data,
                    rules: ruleResults.data
                }
            });

            // Step 8: Store results in IHR
            console.log('💾 Storing results in IHR...');
            await this.callModuleAPI('abena-ihr', '/api/v1/analytics/reports', {
                patientId,
                report: unifiedReport.data,
                timestamp: new Date().toISOString()
            });

            console.log('✅ Complete health analysis finished successfully!');
            return unifiedReport.data;

        } catch (error) {
            console.error('❌ Error in complete health analysis:', error);
            throw error;
        }
    }

    /**
     * Example: Telemedicine consultation workflow
     */
    async performTelemedicineConsultation(patientId, providerId, appointmentId) {
        console.log('🏥 Starting telemedicine consultation...');

        try {
            // Step 1: Get patient context from IHR
            const patientContext = await this.callModuleAPI('abena-ihr', `/api/v1/patients/${patientId}`, {});

            // Step 2: Get recent health analysis
            const healthAnalysis = await this.callModuleAPI('background-modules', '/api/v1/analysis', {
                patientId,
                includeEcbome: true
            });

            // Step 3: Start consultation
            const consultation = await this.callModuleAPI('telemedicine', '/api/v1/consultations/start', {
                appointmentId,
                patientId,
                providerId,
                patientContext: patientContext.data,
                healthAnalysis: healthAnalysis.data
            });

            // Step 4: Get provider workflow tasks
            const workflowTasks = await this.callModuleAPI('provider-workflow', `/api/v1/tasks/${providerId}`, {});

            console.log('✅ Telemedicine consultation started successfully!');
            return {
                consultation: consultation.data,
                workflowTasks: workflowTasks.data
            };

        } catch (error) {
            console.error('❌ Error in telemedicine consultation:', error);
            throw error;
        }
    }

    /**
     * Example: Real-time monitoring and alerting
     */
    async setupRealTimeMonitoring(patientId) {
        console.log('👁️ Setting up real-time monitoring...');

        try {
            // Step 1: Start background monitoring
            await this.callModuleAPI('background-modules', '/api/v1/modules/start', {
                patientId,
                userId: 'system'
            });

            // Step 2: Subscribe to background module events
            await this.sdk.subscribeToModuleEvents('background-modules', 'alert_generated', async (alertData) => {
                console.log('🚨 Alert received:', alertData);

                // Step 3: Process alert through business rules
                const ruleResponse = await this.callModuleAPI('business-rules', '/api/v1/conflicts/process', {
                    patientId,
                    alertData
                });

                // Step 4: If critical, trigger provider workflow
                if (ruleResponse.data.severity === 'critical') {
                    await this.callModuleAPI('provider-workflow', '/api/v1/automation/trigger', {
                        patientId,
                        alertType: 'critical_health_alert',
                        ruleResponse: ruleResponse.data
                    });
                }

                // Step 5: Log to IHR
                await this.callModuleAPI('abena-ihr', '/api/v1/analytics/alerts', {
                    patientId,
                    alert: alertData,
                    ruleResponse: ruleResponse.data,
                    timestamp: new Date().toISOString()
                });
            });

            console.log('✅ Real-time monitoring setup complete!');

        } catch (error) {
            console.error('❌ Error setting up real-time monitoring:', error);
            throw error;
        }
    }

    /**
     * Example: Biomarker integration workflow
     */
    async processLabResults(patientId, labResults) {
        console.log('🔬 Processing lab results...');

        try {
            // Step 1: Ingest lab results
            const ingestionResult = await this.callModuleAPI('biomarker-integration', '/api/v1/lab-results/ingest', {
                patientId,
                labResults
            });

            // Step 2: Process biomarkers
            const biomarkerAnalysis = await this.callModuleAPI('biomarker-integration', '/api/v1/biomarkers/process', {
                patientId,
                labResults: ingestionResult.data
            });

            // Step 3: Update background modules with new data
            await this.callModuleAPI('background-modules', '/api/v1/modules/update', {
                patientId,
                biomarkerData: biomarkerAnalysis.data
            });

            // Step 4: Trigger eCdome analysis
            const ecdomeAnalysis = await this.callModuleAPI('ecdome-intelligence', '/api/v1/analysis/ecbome', {
                patientId,
                biomarkerData: biomarkerAnalysis.data
            });

            // Step 5: Store in IHR
            await this.callModuleAPI('abena-ihr', '/api/v1/analytics/lab-results', {
                patientId,
                labResults: ingestionResult.data,
                biomarkerAnalysis: biomarkerAnalysis.data,
                ecdomeAnalysis: ecdomeAnalysis.data
            });

            console.log('✅ Lab results processed successfully!');
            return {
                ingestion: ingestionResult.data,
                biomarkers: biomarkerAnalysis.data,
                ecdome: ecdomeAnalysis.data
            };

        } catch (error) {
            console.error('❌ Error processing lab results:', error);
            throw error;
        }
    }

    /**
     * Helper method to call module APIs through the gateway
     */
    async callModuleAPI(moduleName, endpoint, data = {}) {
        try {
            const url = `${this.apiGatewayUrl}/api/v1/${moduleName}${endpoint}`;
            
            const response = await fetch(url, {
                method: data.method || 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${await this.sdk.getAccessToken()}`,
                    'X-Module-ID': moduleName,
                    'X-Request-ID': this.generateRequestId()
                },
                body: data.method !== 'GET' ? JSON.stringify(data) : undefined
            });

            if (!response.ok) {
                throw new Error(`API call failed: ${response.status} ${response.statusText}`);
            }

            return await response.json();

        } catch (error) {
            console.error(`Error calling ${moduleName} API:`, error);
            throw error;
        }
    }

    /**
     * Generate unique request ID
     */
    generateRequestId() {
        return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Example: Get system status
     */
    async getSystemStatus() {
        console.log('📊 Getting system status...');

        try {
            const modules = [
                'auth-service',
                'sdk-service', 
                'module-registry',
                'background-modules',
                'abena-ihr',
                'business-rules',
                'telemedicine',
                'ecdome-intelligence',
                'biomarker-integration',
                'provider-workflow',
                'unified-integration'
            ];

            const status = {};

            for (const module of modules) {
                try {
                    const healthResponse = await this.callModuleAPI(module, '/health', {});
                    status[module] = {
                        status: 'healthy',
                        data: healthResponse
                    };
                } catch (error) {
                    status[module] = {
                        status: 'unhealthy',
                        error: error.message
                    };
                }
            }

            return status;

        } catch (error) {
            console.error('❌ Error getting system status:', error);
            throw error;
        }
    }
}

// Example usage
async function main() {
    const integration = new AbenaIntegrationExample();

    try {
        // Get system status
        console.log('=== System Status ===');
        const status = await integration.getSystemStatus();
        console.log(JSON.stringify(status, null, 2));

        // Perform complete health analysis
        console.log('\n=== Complete Health Analysis ===');
        const analysis = await integration.performCompleteHealthAnalysis('patient-123', 'user-456');
        console.log('Analysis completed:', analysis.summary);

        // Setup real-time monitoring
        console.log('\n=== Real-time Monitoring ===');
        await integration.setupRealTimeMonitoring('patient-123');

        // Process lab results
        console.log('\n=== Lab Results Processing ===');
        const labResults = {
            glucose: 95,
            cholesterol: 180,
            bloodPressure: '120/80'
        };
        const labAnalysis = await integration.processLabResults('patient-123', labResults);
        console.log('Lab analysis completed:', labAnalysis);

    } catch (error) {
        console.error('Integration example failed:', error);
    }
}

// Run example if this file is executed directly
if (require.main === module) {
    main();
}

module.exports = AbenaIntegrationExample; 