import axios from 'axios';
import API_CONFIG from '../config/api.config';

// Create axios instances for each service
const createApiInstance = (baseURL) => {
  return axios.create({
    baseURL,
    ...API_CONFIG.DEFAULT_CONFIG
  });
};

// Initialize API instances - pointing to our actual running services
const backgroundModulesApi = createApiInstance('http://localhost:8080/api/v1/background-modules');

// Mock API service that works with our actual services
export const ihrIntelligenceService = {
  processPatientData: async (patientId) => {
    try {
      // Use our actual background modules service
      const response = await backgroundModulesApi.get('/health');
      return {
        success: true,
        data: {
          patientId,
          status: 'processed',
          timestamp: new Date().toISOString(),
          backgroundModules: response.data
        }
      };
    } catch (error) {
      return {
        success: false,
        error: 'Service temporarily unavailable'
      };
    }
  },

  getRealTimeMetrics: async (patientId) => {
    try {
      // Get real-time data from our background modules
      const response = await backgroundModulesApi.get('/api/v1/modules/status');
      return {
        success: true,
        data: {
          patientId,
          metrics: response.data,
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      return {
        success: false,
        error: 'Unable to fetch real-time metrics'
      };
    }
  },

  getAnalysisHistory: async (patientId) => {
    try {
      // Mock analysis history
      return {
        success: true,
        data: {
          patientId,
          history: [
            {
              id: 'analysis-1',
              type: 'eCBome Analysis',
              status: 'completed',
              timestamp: new Date().toISOString(),
              results: {
                overallHealthScore: 85,
                recommendations: ['Increase physical activity', 'Monitor stress levels']
              }
            }
          ]
        }
      };
    } catch (error) {
      return {
        success: false,
        error: 'Unable to fetch analysis history'
      };
    }
  },

  analyzeEndocannabinoidLevels: async (levels) => {
    try {
      // Mock endocannabinoid analysis
      return {
        success: true,
        data: {
          analysis: {
            anandamide: levels.anandamide || 0.5,
            pparAlpha: levels.pparAlpha || 0.3,
            pparGamma: levels.pparGamma || 0.4,
            recommendations: ['Maintain current levels', 'Consider dietary adjustments']
          },
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      return {
        success: false,
        error: 'Analysis failed'
      };
    }
  },

  analyzeReceptorActivity: async (activity) => {
    try {
      // Mock receptor activity analysis
      return {
        success: true,
        data: {
          analysis: {
            receptors: activity,
            status: 'analyzed',
            insights: ['Normal receptor activity detected', 'No significant abnormalities']
          },
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      return {
        success: false,
        error: 'Receptor analysis failed'
      };
    }
  }
};

// Mock other services to prevent errors
export const medicalDbService = {
  getPatientHistory: async () => ({ success: true, data: [] }),
  getMedicalConditions: async () => ({ success: true, data: [] }),
  getTreatmentHistory: async () => ({ success: true, data: [] })
};

export const drugInteractionsService = {
  checkInteractions: async () => ({ success: true, data: [] }),
  getDrugInfo: async () => ({ success: true, data: {} })
};

export const scientificLitService = {
  searchLiterature: async () => ({ success: true, data: [] }),
  getArticleDetails: async () => ({ success: true, data: {} })
};

// Alias for compatibility
export const scientificLiteratureService = scientificLitService;
export const medicalDatabaseService = medicalDbService;

export const labResultsService = {
  getLabResults: async () => ({ success: true, data: [] }),
  getEndocannabinoidLevels: async () => ({ success: true, data: {} }),
  getReceptorActivity: async () => ({ success: true, data: {} })
};

// Error handling middleware
export const handleApiError = (error) => {
  if (error.response) {
    switch (error.response.status) {
      case 401:
        return new Error('Unauthorized access');
      case 404:
        return new Error('Service not found');
      case 422:
        return new Error('Invalid data');
      default:
        return new Error('Server error');
    }
  } else if (error.request) {
    return new Error('Network error - please check your connection');
  } else {
    return error;
  }
}; 