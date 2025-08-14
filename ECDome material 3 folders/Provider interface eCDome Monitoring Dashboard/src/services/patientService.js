import axios from 'axios';
import abena from './abenaSDK';

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

// Patient service methods using REAL API calls
export const patientService = {
  // Get all patients - USE REAL API
  getPatients: async () => {
    try {
      const response = await api.get('/patients');
      console.log('✅ Real patient data loaded:', response.data.length, 'patients');
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch patients from real API:', error);
      throw new Error('Failed to fetch patients from database');
    }
  },

  // Get patient by ID - USE REAL API
  getPatient: async (patientId) => {
    try {
      const response = await api.get(`/patients/${patientId}`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch patient:', error);
      throw new Error('Failed to fetch patient from database');
    }
  },

  // Get detailed patient data - USE REAL API
  getPatientData: async (patientId) => {
    try {
      const response = await api.get(`/patients/${patientId}/data`);
      console.log('✅ Real patient data loaded for:', patientId);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch patient data:', error);
      throw new Error('Failed to fetch patient data from database');
    }
  },

  // Get real-time patient data - USE REAL API
  getRealtimeData: async (patientId) => {
    try {
      const response = await api.get(`/patients/${patientId}/realtime`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch real-time data:', error);
      throw new Error('Failed to fetch real-time data from database');
    }
  },

  // Get module analysis - USE REAL API
  getModuleAnalysis: async (patientId, modules) => {
    try {
      const response = await api.get(`/patients/${patientId}/modules`, {
        params: { modules: modules.join(',') }
      });
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch module analysis:', error);
      throw new Error('Failed to fetch module analysis from database');
    }
  },

  // Get eCDome components - USE REAL API
  getEcdomeComponents: async (patientId, timeRange = '24h') => {
    try {
      const response = await api.get(`/patients/${patientId}/ecdome`, {
        params: { timeRange }
      });
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch eCDome components:', error);
      throw new Error('Failed to fetch eCDome components from database');
    }
  },

  // Get predictive alerts - USE REAL API
  getPredictiveAlerts: async (patientId) => {
    try {
      const response = await api.get(`/patients/${patientId}/alerts`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch predictive alerts:', error);
      throw new Error('Failed to fetch predictive alerts from database');
    }
  },

  // Get clinical recommendations - USE REAL API
  getClinicalRecommendations: async (patientId) => {
    try {
      const response = await api.get(`/patients/${patientId}/recommendations`);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch clinical recommendations:', error);
      throw new Error('Failed to fetch clinical recommendations from database');
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

  // Get patient history - USE REAL API
  getPatientHistory: async (patientId, timeRange = '30d') => {
    try {
      const response = await api.get(`/patients/${patientId}/history`, {
        params: { range: timeRange }
      });
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch patient history:', error);
      throw new Error('Failed to fetch patient history from database');
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