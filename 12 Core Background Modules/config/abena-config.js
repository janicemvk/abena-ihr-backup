/**
 * ABENA SDK CONFIGURATION
 * Configuration for the 12 Core Background Modules System
 */

export const abenaConfig = {
  // Abena SDK Service URLs
  services: {
    authServiceUrl: process.env.ABENA_AUTH_SERVICE_URL || 'http://localhost:3001',
    dataServiceUrl: process.env.ABENA_DATA_SERVICE_URL || 'http://localhost:8001',
    privacyServiceUrl: process.env.ABENA_PRIVACY_SERVICE_URL || 'http://localhost:8002',
    blockchainServiceUrl: process.env.ABENA_BLOCKCHAIN_SERVICE_URL || 'http://localhost:8003',
    ecbomeServiceUrl: process.env.ABENA_ECBOME_SERVICE_URL || 'http://localhost:8004',
    correlationEngineUrl: process.env.ABENA_CORRELATION_ENGINE_URL || 'http://localhost:8005'
  },

  // Module Monitoring Intervals (in milliseconds)
  intervals: {
    samplingInterval: 900000,      // 15 minutes
    analysisInterval: 1800000,     // 30 minutes
    deepAnalysisInterval: 14400000, // 4 hours
    orchestrationInterval: 3600000  // 1 hour
  },

  // Module-specific configurations
  modules: {
    metabolome: {
      alertThresholds: {
        metabolicDisruption: 0.7,
        cannabinoidDeficiency: 0.6,
        pathwayBlockage: 0.8
      },
      samplingBiomarkers: ['glucose', 'insulin', 'ketones', 'lactate']
    },

    microbiome: {
      alertThresholds: {
        dysbiosis: 0.6,
        ecsProduction: 0.5,
        intestinalPermeability: 0.7
      },
      samplingData: ['bacterial-composition', 'metabolites', 'ph-levels']
    },

    inflammatome: {
      alertThresholds: {
        chronicInflammation: 0.7,
        cytokinestorm: 0.9,
        resolutionFailure: 0.6
      },
      samplingBiomarkers: ['crp', 'tnf-alpha', 'il6', 'il1-beta']
    },

    immunome: {
      alertThresholds: {
        immuneSuppression: 0.3,
        autoimmunity: 0.7,
        hyperactivation: 0.8
      },
      samplingBiomarkers: ['white-blood-cells', 'immunoglobulins', 'cytokines']
    },

    chronobiome: {
      alertThresholds: {
        circadianDisruption: 0.6,
        sleepDisorder: 0.7,
        jetlag: 0.5
      },
      samplingBiomarkers: ['melatonin', 'cortisol', 'body-temperature', 'activity-level']
    },

    nutriome: {
      alertThresholds: {
        nutritionalDeficiency: 0.6,
        synthesisImpairment: 0.7,
        malabsorption: 0.5
      },
      samplingBiomarkers: ['vitamins', 'minerals', 'fatty-acids', 'amino-acids']
    },

    toxicome: {
      alertThresholds: {
        toxicOverload: 0.8,
        heavyMetalToxicity: 0.7,
        detoxificationImpairment: 0.6
      },
      samplingMarkers: ['heavy-metals', 'pesticides', 'vocs', 'plasticizers']
    },

    pharmacome: {
      alertThresholds: {
        drugInteraction: 0.8,
        metabolismImpairment: 0.7,
        therapeuticInterference: 0.6
      },
      monitoringData: ['therapeutic-drugs', 'metabolites', 'cannabinoids']
    },

    stressResponse: {
      alertThresholds: {
        chronicStress: 0.7,
        ecsDepletion: 0.6,
        hpaDisruption: 0.8
      },
      samplingBiomarkers: ['cortisol', 'adrenaline', 'noradrenaline', 'hrv']
    },

    cardiovascular: {
      alertThresholds: {
        cardiacRisk: 0.7,
        arrhythmia: 0.8,
        hypertension: 0.6
      },
      monitoringInterval: 600000 // 10 minutes for cardiovascular monitoring
    },

    neurological: {
      alertThresholds: {
        cognitiveDecline: 0.6,
        neurotransmitterImbalance: 0.7,
        neuropathology: 0.8
      }
    },

    hormonal: {
      alertThresholds: {
        hormonalImbalance: 0.6,
        endocrineDisruption: 0.7,
        reproductiveIssues: 0.5
      }
    }
  },

  // Orchestrator Configuration
  orchestrator: {
    // Cross-module pattern recognition settings
    patternRecognition: {
      systemicInflammationThreshold: 0.5,
      metabolicDysfunctionThreshold: 0.6,
      chronicStressThreshold: 0.7
    },

    // Critical alert settings
    criticalAlerts: {
      healthScoreThreshold: 0.3,
      multipleHighPriorityThreshold: 3,
      systemCoherenceThreshold: 0.5
    },

    // Predictive indicator settings
    predictiveIndicators: {
      enabled: true,
      confidenceThreshold: 0.6,
      timeframeWeighting: {
        'immediate': 1.0,
        '1-2 weeks': 0.8,
        '1-3 months': 0.6,
        '3-6 months': 0.4
      }
    }
  },

  // Logging Configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    enableConsoleLogging: process.env.NODE_ENV !== 'production',
    enableFileLogging: true,
    logDirectory: './logs',
    maxLogFiles: 10,
    maxLogSize: '10MB'
  },

  // Performance Configuration
  performance: {
    maxConcurrentAnalyses: 5,
    analysisTimeout: 30000, // 30 seconds
    retryAttempts: 3,
    retryDelay: 1000 // 1 second
  },

  // Privacy and Security
  privacy: {
    enableDataEncryption: true,
    enableBlockchainLogging: true,
    dataRetentionPeriod: 2592000000, // 30 days in milliseconds
    anonymizePatientData: true
  }
};

// Environment-specific overrides
if (process.env.NODE_ENV === 'development') {
  abenaConfig.logging.level = 'debug';
  abenaConfig.performance.analysisTimeout = 60000; // 1 minute for development
}

if (process.env.NODE_ENV === 'production') {
  abenaConfig.logging.enableConsoleLogging = false;
  abenaConfig.performance.maxConcurrentAnalyses = 10;
}

export default abenaConfig; 