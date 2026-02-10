const express = require('express');
const cors = require('cors');
const AbenaSDK = require('./abena_sdk.js');

class ModuleRegistry {
    constructor() {
        this.app = express();
        this.modules = new Map();
        this.sdk = new AbenaSDK({
            authServiceUrl: process.env.AUTH_SERVICE_URL || 'http://localhost:3001',
            dataServiceUrl: process.env.DATA_SERVICE_URL || 'http://localhost:8001',
            privacyServiceUrl: process.env.PRIVACY_SERVICE_URL || 'http://localhost:8002',
            blockchainServiceUrl: process.env.BLOCKCHAIN_SERVICE_URL || 'http://localhost:8003'
        });
        
        this.setupMiddleware();
        this.setupRoutes();
        this.initializeDefaultModules();
    }

    setupMiddleware() {
        this.app.use(cors({
            origin: [
                'http://localhost:3000',
                'http://localhost:4005',  // eCDome Intelligence
                'http://localhost:4006',  // Gamification
                'http://localhost:4007',  // Unified Integration
                'http://localhost:4008',  // Provider Dashboard
                'http://localhost:4009',  // Patient Dashboard
                'http://localhost:4011',  // Data Ingestion
                'http://localhost:4012',  // Biomarker GUI
                'http://localhost:8000',  // Telemedicine Platform
                'http://localhost:8080',  // API Gateway
            ],
            credentials: true,
            methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
        }));
        this.app.use(express.json());
        this.app.use(express.urlencoded({ extended: true }));
    }

    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({ status: 'healthy', modules: this.modules.size });
        });

        // Register a new module
        this.app.post('/register', async (req, res) => {
            try {
                const { moduleId, name, version, endpoints, healthCheck, metadata } = req.body;
                
                const moduleInfo = {
                    id: moduleId,
                    name,
                    version,
                    endpoints,
                    healthCheck,
                    metadata,
                    registeredAt: new Date().toISOString(),
                    lastHealthCheck: new Date().toISOString(),
                    status: 'active'
                };

                this.modules.set(moduleId, moduleInfo);
                
                // Log to blockchain
                await this.sdk.logBlockchainAccess(
                    'module-registry',
                    'REGISTER',
                    'system_admin',
                    { moduleId, name, version }
                );

                res.json({ success: true, moduleId });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Get all modules
        this.app.get('/modules', (req, res) => {
            const modulesList = Array.from(this.modules.values());
            res.json({ modules: modulesList });
        });

        // Get specific module
        this.app.get('/modules/:moduleId', (req, res) => {
            const module = this.modules.get(req.params.moduleId);
            if (module) {
                res.json(module);
            } else {
                res.status(404).json({ error: 'Module not found' });
            }
        });

        // Update module status
        this.app.put('/modules/:moduleId/status', async (req, res) => {
            try {
                const { status } = req.body;
                const module = this.modules.get(req.params.moduleId);
                
                if (module) {
                    module.status = status;
                    module.lastHealthCheck = new Date().toISOString();
                    
                    // Log status change
                    await this.sdk.logBlockchainAccess(
                        'module-registry',
                        'STATUS_UPDATE',
                        'system_admin',
                        { moduleId: req.params.moduleId, status }
                    );
                    
                    res.json({ success: true });
                } else {
                    res.status(404).json({ error: 'Module not found' });
                }
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Discover modules automatically
        this.app.post('/discover', async (req, res) => {
            try {
                const discoveredModules = await this.discoverModules();
                res.json({ discovered: discoveredModules.length, modules: discoveredModules });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Get module endpoints for routing
        this.app.get('/endpoints', (req, res) => {
            const endpoints = {};
            for (const [moduleId, module] of this.modules) {
                endpoints[moduleId] = {
                    baseUrl: module.endpoints.baseUrl,
                    healthCheck: module.endpoints.healthCheck,
                    status: module.status
                };
            }
            res.json(endpoints);
        });
    }

    initializeDefaultModules() {
        // Register default modules based on the system architecture
        const defaultModules = [
            {
                id: 'background-modules',
                name: '12 Core Background Modules',
                version: '2.0.0',
                endpoints: {
                    baseUrl: 'http://background-modules:4001',
                    healthCheck: 'http://background-modules:4001/health',
                    api: {
                        startAllModules: '/api/v1/modules/start',
                        getAnalysis: '/api/v1/analysis',
                        stopModules: '/api/v1/modules/stop'
                    }
                },
                metadata: {
                    description: 'Biological system monitoring with eCBome correlation',
                    category: 'monitoring',
                    dependencies: ['sdk-service']
                }
            },
            {
                id: 'abena-ihr',
                name: 'Abena IHR Main System',
                version: '1.0.0',
                endpoints: {
                    baseUrl: 'http://abena-ihr:4002',
                    healthCheck: 'http://abena-ihr:4002/health',
                    api: {
                        patients: '/api/v1/patients',
                        outcomes: '/api/v1/outcomes',
                        analytics: '/api/v1/analytics'
                    }
                },
                metadata: {
                    description: 'Clinical outcomes management system',
                    category: 'core',
                    dependencies: ['sdk-service', 'background-modules']
                }
            },
            {
                id: 'business-rules',
                name: 'Business Rule Engine',
                version: '1.0.0',
                endpoints: {
                    baseUrl: 'http://business-rules:4003',
                    healthCheck: 'http://business-rules:4003/health',
                    api: {
                        rules: '/api/v1/rules',
                        conflicts: '/api/v1/conflicts',
                        decisions: '/api/v1/decisions'
                    }
                },
                metadata: {
                    description: 'Conflict resolution and clinical decision support',
                    category: 'intelligence',
                    dependencies: ['sdk-service']
                }
            },
            {
                id: 'telemedicine',
                name: 'Telemedicine Platform',
                version: '1.0.0',
                endpoints: {
                    baseUrl: 'http://telemedicine:4004',
                    healthCheck: 'http://telemedicine:4004/health',
                    api: {
                        appointments: '/api/v1/appointments',
                        consultations: '/api/v1/consultations',
                        recordings: '/api/v1/recordings'
                    }
                },
                metadata: {
                    description: 'Video consultation and remote care platform',
                    category: 'communication',
                    dependencies: ['sdk-service', 'auth-service']
                }
            },
            {
                id: 'ecdome-intelligence',
                name: 'eCdome Intelligence System',
                version: '1.0.0',
                endpoints: {
                    baseUrl: 'http://ecdome-intelligence:4005',
                    healthCheck: 'http://ecdome-intelligence:4005/health',
                    api: {
                        analysis: '/api/v1/analysis',
                        patterns: '/api/v1/patterns',
                        predictions: '/api/v1/predictions'
                    }
                },
                metadata: {
                    description: 'Endocannabinoid system analysis and intelligence',
                    category: 'intelligence',
                    dependencies: ['sdk-service', 'background-modules']
                }
            },
            {
                id: 'biomarker-integration',
                name: 'Biomarker Integration',
                version: '1.0.0',
                endpoints: {
                    baseUrl: 'http://biomarker-integration:4006',
                    healthCheck: 'http://biomarker-integration:4006/health',
                    api: {
                        labResults: '/api/v1/lab-results',
                        biomarkers: '/api/v1/biomarkers',
                        integration: '/api/v1/integration'
                    }
                },
                metadata: {
                    description: 'Lab results and biomarker processing',
                    category: 'data',
                    dependencies: ['sdk-service']
                }
            },
            {
                id: 'provider-workflow',
                name: 'Provider Workflow Integration',
                version: '1.0.0',
                endpoints: {
                    baseUrl: 'http://provider-workflow:4007',
                    healthCheck: 'http://provider-workflow:4007/health',
                    api: {
                        workflows: '/api/v1/workflows',
                        tasks: '/api/v1/tasks',
                        automation: '/api/v1/automation'
                    }
                },
                metadata: {
                    description: 'Clinical workflow automation and integration',
                    category: 'workflow',
                    dependencies: ['sdk-service', 'business-rules']
                }
            },
            {
                id: 'unified-integration',
                name: 'Unified Integration Layer',
                version: '1.0.0',
                endpoints: {
                    baseUrl: 'http://unified-integration:4008',
                    healthCheck: 'http://unified-integration:4008/health',
                    api: {
                        orchestration: '/api/v1/orchestration',
                        coordination: '/api/v1/coordination',
                        integration: '/api/v1/integration'
                    }
                },
                metadata: {
                    description: 'Central coordination and integration layer',
                    category: 'core',
                    dependencies: ['sdk-service', 'module-registry']
                }
            }
        ];

        defaultModules.forEach(module => {
            this.modules.set(module.id, {
                ...module,
                registeredAt: new Date().toISOString(),
                lastHealthCheck: new Date().toISOString(),
                status: 'active'
            });
        });
    }

    async discoverModules() {
        // Auto-discover modules by checking common ports and endpoints
        const discoveredModules = [];
        const commonPorts = [4001, 4002, 4003, 4004, 4005, 4006, 4007, 4008];
        
        for (const port of commonPorts) {
            try {
                const response = await fetch(`http://localhost:${port}/health`);
                if (response.ok) {
                    const moduleInfo = await response.json();
                    discoveredModules.push({
                        port,
                        ...moduleInfo
                    });
                }
            } catch (error) {
                // Module not available on this port
            }
        }
        
        return discoveredModules;
    }

    start(port = 3003) {
        this.app.listen(port, () => {
            console.log(`Module Registry running on port ${port}`);
            console.log(`Registered modules: ${this.modules.size}`);
        });
    }
}

// Start the registry
const registry = new ModuleRegistry();
registry.start(process.env.REGISTRY_PORT || 3003);

module.exports = ModuleRegistry; 