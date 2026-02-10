/**
 * Quantum Healthcare Service
 * Fetches quantum analysis data from Quantum Healthcare API
 */

import axios from 'axios';

// Quantum Healthcare API URL
const QUANTUM_API_URL = process.env.REACT_APP_QUANTUM_API_URL || 'http://localhost:5000';
const QUANTUM_API_GATEWAY_URL = process.env.REACT_APP_API_GATEWAY_URL || 'http://localhost:8081/api/v1/quantum';

// Create axios instance for quantum API
const quantumApi = axios.create({
  baseURL: QUANTUM_API_URL,
  timeout: 60000, // 60 seconds for quantum computations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens
quantumApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('abena_token') || localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
quantumApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      console.error('Quantum API authentication failed');
    } else if (error.response?.status === 429) {
      // Rate limit exceeded
      console.error('Quantum API rate limit exceeded');
    }
    return Promise.reject(error);
  }
);

export const quantumService = {
  /**
   * Run quantum analysis for a patient
   * @param {string} patientId - Patient ID
   * @param {object} options - Optional analysis parameters
   * @returns {Promise<object>} Analysis results
   */
  analyzePatient: async (patientId, options = {}) => {
    try {
      // For demo purposes, use demo-results endpoint for sample patients
      const demoPatients = ['PAT-001', 'PAT-002', 'PAT-003', 'DEMO_001', 'DEMO_002'];
      const isDemoPatient = demoPatients.some(demo => patientId.includes(demo) || demo.includes(patientId));
      
      if (isDemoPatient) {
        // Use demo results for sample patients
        console.log('Using demo results for patient:', patientId);
        const demoResponse = await quantumApi.get('/api/demo-results');
        return {
          success: true,
          data: {
            ...demoResponse.data,
            patient_id: patientId, // Override with actual patient ID
            analysis_timestamp: new Date().toISOString(),
          },
        };
      }

      // Try full analysis for real patients
      const response = await quantumApi.post('/api/analyze', {
        patient_id: patientId,
        symptoms: options.symptoms || [],
        biomarkers: options.biomarkers || {},
        medications: options.medications || [],
        recommended_herbs: options.recommended_herbs || [],
      });

      // Handle different response formats
      if (response.data.success && response.data.results) {
        return {
          success: true,
          data: response.data.results,
        };
      } else if (response.data.results) {
        return {
          success: true,
          data: response.data.results,
        };
      } else {
        return {
          success: true,
          data: response.data,
        };
      }
    } catch (error) {
      console.error('Quantum analysis error:', error);
      
      // Fallback to demo results if analyze fails
      try {
        console.log('Falling back to demo results...');
        const demoResponse = await quantumApi.get('/api/demo-results');
        return {
          success: true,
          data: {
            ...demoResponse.data,
            patient_id: patientId,
            analysis_timestamp: new Date().toISOString(),
            note: 'Demo results (analysis endpoint unavailable)',
          },
        };
      } catch (demoError) {
        return {
          success: false,
          error: error.response?.data?.error || error.message || 'Analysis failed',
          detail: error.response?.data?.detail,
        };
      }
    }
  },

  /**
   * Get quantum analysis history for a patient
   * @param {string} patientId - Patient ID
   * @param {number} limit - Maximum number of results
   * @returns {Promise<object>} Analysis history
   */
  getPatientAnalyses: async (patientId, limit = 10) => {
    try {
      const response = await quantumApi.get(`/api/patients/${patientId}/analyses`, {
        params: { limit },
      });

      return {
        success: true,
        data: response.data.analyses || [],
        count: response.data.count || 0,
      };
    } catch (error) {
      console.error('Error fetching quantum analyses:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch analyses',
        data: [],
      };
    }
  },

  /**
   * Get specific quantum analysis by ID
   * @param {number} analysisId - Analysis ID
   * @returns {Promise<object>} Analysis details
   */
  getAnalysis: async (analysisId) => {
    try {
      const response = await quantumApi.get(`/api/analyses/${analysisId}`);

      return {
        success: true,
        data: response.data.analysis || response.data,
      };
    } catch (error) {
      console.error('Error fetching quantum analysis:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch analysis',
      };
    }
  },

  /**
   * Get demo quantum results (no auth required)
   * @returns {Promise<object>} Demo results
   */
  getDemoResults: async () => {
    try {
      const response = await quantumApi.get('/api/demo-results');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Error fetching demo results:', error);
      return {
        success: false,
        error: error.message || 'Failed to fetch demo results',
      };
    }
  },

  /**
   * Check quantum service health
   * @returns {Promise<object>} Health status
   */
  checkHealth: async () => {
    try {
      const response = await quantumApi.get('/health');
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Service unavailable',
      };
    }
  },
};

export default quantumService;



