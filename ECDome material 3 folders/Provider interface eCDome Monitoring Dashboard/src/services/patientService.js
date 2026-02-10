import axios from 'axios';
import abena from './abenaSDK';
import { 
  mockPatients, 
  mockPatientDetails, 
  generateRealtimeVitals, 
  generateEcbomeTimeline,
  getPatientStats 
} from './mockPatientData';

// Base API configuration - Point to our local API Gateway
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:4001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('abena_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('abena_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Patient service methods using COMPREHENSIVE MOCK DATA
export const patientService = {
  // Get all patients - USE COMPREHENSIVE MOCK DATA
  getPatients: async () => {
    try {
      // Simulate network delay for realism
      await new Promise(resolve => setTimeout(resolve, 300));
      
      console.log('✅ Mock patient data loaded:', mockPatients.length, 'patients');
      return mockPatients;
    } catch (error) {
      console.error('❌ Failed to load mock patients:', error);
      throw new Error('Failed to load patient data');
    }
  },

  // Get patient by ID - USE COMPREHENSIVE MOCK DATA
  getPatient: async (patientId) => {
    try {
      // Simulate network delay for realism
      await new Promise(resolve => setTimeout(resolve, 200));
      
      const patient = mockPatients.find(p => p.id === patientId);
      if (!patient) {
        throw new Error(`Patient ${patientId} not found`);
      }
      
      console.log('✅ Mock patient data loaded for:', patientId);
      return patient;
    } catch (error) {
      console.error('❌ Failed to load mock patient:', error);
      throw new Error('Failed to load patient data');
    }
  },

  // Get detailed patient data - USE COMPREHENSIVE MOCK DATA
  getPatientData: async (patientId) => {
    try {
      // Simulate network delay for realism
      await new Promise(resolve => setTimeout(resolve, 400));
      
      const patientDetails = mockPatientDetails[patientId];
      if (!patientDetails) {
        // Fallback to basic patient info if detailed data not available
        const patient = mockPatients.find(p => p.id === patientId);
        if (!patient) {
          throw new Error(`Patient ${patientId} not found`);
        }
        return {
          success: true,
          data: {
            patientInfo: patient,
            ecbomeProfile: {
              score: patient.ecbomeScore,
              status: 'Unknown',
              components: {}
            },
            timestamp: new Date().toISOString()
          }
        };
      }
      
      console.log('✅ Comprehensive mock patient data loaded for:', patientId);
      return {
        success: true,
        data: patientDetails
      };
    } catch (error) {
      console.error('❌ Failed to load mock patient data:', error);
      throw new Error('Failed to load patient data');
    }
  },

  // Get real-time patient data - USE COMPREHENSIVE MOCK DATA
  getRealtimeData: async (patientId) => {
    try {
      // Simulate network delay for realism
      await new Promise(resolve => setTimeout(resolve, 150));
      
      const patientDetails = mockPatientDetails[patientId];
      if (!patientDetails) {
        throw new Error(`Patient ${patientId} not found`);
      }

      // Generate dynamic vital signs with some variation
      const vitals = generateRealtimeVitals(patientId);
      
      const mockRealtimeData = {
        success: true,
        data: {
          patientId: patientId,
          timestamp: new Date().toISOString(),
          vitalSigns: vitals,
          ecbomeReadings: Object.keys(patientDetails.ecbomeProfile.components).reduce((acc, key) => {
            const component = patientDetails.ecbomeProfile.components[key];
            // Add slight variation to readings
            const variation = (Math.random() * 0.06) - 0.03; // ±3% variation
            acc[key] = Math.max(0, Math.min(1, component.reading + variation)).toFixed(2);
            return acc;
          }, {}),
          alerts: patientDetails.alerts || [],
          status: patientDetails.patientInfo.status
        }
      };
      
      console.log('✅ Mock real-time data loaded for:', patientId);
      return mockRealtimeData;
    } catch (error) {
      console.error('❌ Failed to load mock real-time data:', error);
      throw new Error('Failed to load real-time data');
    }
  },

  // Get module analysis - USE COMPREHENSIVE MOCK DATA
  getModuleAnalysis: async (patientId, modules) => {
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const patientDetails = mockPatientDetails[patientId];
      if (!patientDetails) {
        throw new Error(`Patient ${patientId} not found`);
      }

      const moduleAnalysis = {
        success: true,
        data: {
          patientId,
          modules: {},
          timestamp: new Date().toISOString()
        }
      };

      // Return analysis for requested modules (or all if none specified)
      const requestedModules = modules && modules.length > 0 ? modules : Object.keys(patientDetails.ecbomeProfile.components);
      
      requestedModules.forEach(moduleName => {
        const component = patientDetails.ecbomeProfile.components[moduleName];
        if (component) {
          moduleAnalysis.data.modules[moduleName] = {
            name: moduleName,
            status: component.status,
            reading: component.reading,
            trend: component.trend,
            analysis: `${moduleName} system is ${component.status} with current reading at ${(component.reading * 100).toFixed(0)}%`
          };
        }
      });

      console.log('✅ Module analysis loaded for:', patientId);
      return moduleAnalysis;
    } catch (error) {
      console.error('❌ Failed to fetch module analysis:', error);
      throw new Error('Failed to fetch module analysis');
    }
  },

  // Get eCBome components - USE COMPREHENSIVE MOCK DATA
  getEcbomeComponents: async (patientId, timeRange = '24h') => {
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 250));
      
      const patientDetails = mockPatientDetails[patientId];
      if (!patientDetails) {
        throw new Error(`Patient ${patientId} not found`);
      }

      // Parse timeRange to get hours
      const hours = timeRange === '24h' ? 24 : timeRange === '7d' ? 168 : timeRange === '30d' ? 720 : 24;

      const ecbomeData = {
        success: true,
        data: {
          patientId,
          timeRange,
          components: patientDetails.ecbomeProfile.components,
          timeline: generateEcbomeTimeline(patientId, Math.min(hours, 24)), // Limit to 24 hours for performance
          overallScore: patientDetails.ecbomeProfile.score,
          status: patientDetails.ecbomeProfile.status,
          timestamp: new Date().toISOString()
        }
      };

      console.log('✅ eCBome components loaded for:', patientId);
      return ecbomeData;
    } catch (error) {
      console.error('❌ Failed to fetch eCBome components:', error);
      throw new Error('Failed to fetch eCBome components');
    }
  },

  // Get predictive alerts - USE COMPREHENSIVE MOCK DATA
  getPredictiveAlerts: async (patientId) => {
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 200));
      
      const patientDetails = mockPatientDetails[patientId];
      if (!patientDetails) {
        throw new Error(`Patient ${patientId} not found`);
      }

      const alertsData = {
        success: true,
        data: {
          patientId,
          alerts: patientDetails.alerts || [],
          alertCount: {
            critical: patientDetails.alerts?.filter(a => a.type === 'critical').length || 0,
            warning: patientDetails.alerts?.filter(a => a.type === 'warning').length || 0,
            info: patientDetails.alerts?.filter(a => a.type === 'info').length || 0
          },
          timestamp: new Date().toISOString()
        }
      };

      console.log('✅ Predictive alerts loaded for:', patientId);
      return alertsData;
    } catch (error) {
      console.error('❌ Failed to fetch predictive alerts:', error);
      throw new Error('Failed to fetch predictive alerts');
    }
  },

  // Get clinical recommendations - USE COMPREHENSIVE MOCK DATA
  getClinicalRecommendations: async (patientId) => {
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 250));
      
      const patientDetails = mockPatientDetails[patientId];
      if (!patientDetails) {
        throw new Error(`Patient ${patientId} not found`);
      }

      const recommendationsData = {
        success: true,
        data: {
          patientId,
          recommendations: patientDetails.recommendations || [],
          recommendationCount: {
            high: patientDetails.recommendations?.filter(r => r.priority === 'high').length || 0,
            medium: patientDetails.recommendations?.filter(r => r.priority === 'medium').length || 0,
            low: patientDetails.recommendations?.filter(r => r.priority === 'low').length || 0,
            critical: patientDetails.recommendations?.filter(r => r.priority === 'critical').length || 0
          },
          timestamp: new Date().toISOString()
        }
      };

      console.log('✅ Clinical recommendations loaded for:', patientId);
      return recommendationsData;
    } catch (error) {
      console.error('❌ Failed to fetch clinical recommendations:', error);
      throw new Error('Failed to fetch clinical recommendations');
    }
  },

  // Send intervention - USE REAL API
  sendIntervention: async (patientId, intervention) => {
    try {
      const response = await api.post(`/patients/${patientId}/interventions`, intervention);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to send intervention:', error);
      throw new Error('Failed to send intervention to database');
    }
  },

  // Subscribe to real-time patient updates
  subscribeToPatient: (patientId, callback) => {
    try {
      return abena.subscribeToPatient(patientId, callback);
    } catch (error) {
      console.error('❌ Failed to subscribe to patient:', error);
      throw new Error('Failed to subscribe to patient updates');
    }
  },

  // Unsubscribe from real-time updates
  unsubscribeFromPatient: (subscriptionId) => {
    try {
      return abena.unsubscribe(subscriptionId);
    } catch (error) {
      console.error('❌ Failed to unsubscribe from patient:', error);
    }
  },

  // Create new patient - USE REAL API
  createPatient: async (patientData) => {
    try {
      const response = await api.post('/patients', patientData);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to create patient:', error);
      throw new Error('Failed to create patient in database');
    }
  },

  // Update patient - USE REAL API
  updatePatient: async (patientId, patientData) => {
    try {
      const response = await api.put(`/patients/${patientId}`, patientData);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to update patient:', error);
      throw new Error('Failed to update patient in database');
    }
  },

  // Delete patient - USE REAL API
  deletePatient: async (patientId) => {
    try {
      await api.delete(`/patients/${patientId}`);
      return { success: true };
    } catch (error) {
      console.error('❌ Failed to delete patient:', error);
      throw new Error('Failed to delete patient from database');
    }
  },

  // Search patients - USE REAL API
  searchPatients: async (query) => {
    try {
      const response = await api.get(`/patients/search?q=${query}`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to search patients:', error);
      throw new Error('Failed to search patients in database');
    }
  },

  // Get patient history - USE COMPREHENSIVE MOCK DATA
  getPatientHistory: async (patientId, timeRange = '30d') => {
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 400));
      
      const patientDetails = mockPatientDetails[patientId];
      if (!patientDetails) {
        throw new Error(`Patient ${patientId} not found`);
      }

      // Generate historical data points
      const days = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : timeRange === '90d' ? 90 : 30;
      const historyPoints = [];

      for (let i = days; i >= 0; i--) {
        historyPoints.push({
          date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString(),
          ecbomeScore: Math.max(0.3, Math.min(1, patientDetails.ecbomeProfile.score + (Math.random() * 0.1 - 0.05))),
          vitalSigns: generateRealtimeVitals(patientId),
          status: patientDetails.patientInfo.status
        });
      }

      const historyData = {
        success: true,
        data: {
          patientId,
          timeRange,
          history: historyPoints,
          trends: {
            ecbomeScore: patientDetails.ecbomeProfile.components.endocannabinoid.trend,
            overallHealth: 'stable'
          },
          timestamp: new Date().toISOString()
        }
      };

      console.log('✅ Patient history loaded for:', patientId);
      return historyData;
    } catch (error) {
      console.error('❌ Failed to fetch patient history:', error);
      throw new Error('Failed to fetch patient history');
    }
  },

  // Get system statistics - USE COMPREHENSIVE MOCK DATA
  getSystemStats: async () => {
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 150));
      
      const stats = getPatientStats();
      
      console.log('✅ System statistics loaded');
      return {
        success: true,
        data: stats
      };
    } catch (error) {
      console.error('❌ Failed to fetch system stats:', error);
      throw new Error('Failed to fetch system statistics');
    }
  },

  // Initialize ABENA SDK
  initializeABENA: async () => {
    try {
      await abena.initialize();
      console.log('✅ ABENA SDK initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize ABENA SDK:', error);
      throw new Error('Failed to initialize ABENA SDK');
    }
  }
}; 