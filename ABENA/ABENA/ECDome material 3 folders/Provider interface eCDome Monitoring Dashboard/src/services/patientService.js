import axios from 'axios';
import abena from './abenaSDK';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

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

// Patient service methods using ABENA SDK
export const patientService = {
  // Get all patients
  getPatients: async () => {
    try {
      // In production, this would use ABENA SDK: await abena.getPatientList();
      const response = await api.get('/patients');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch patients:', error);
      // Return mock data for development
      return Array.from({ length: 50 }, (_, i) => ({
        id: `PAT-${(i + 1).toString().padStart(3, '0')}`,
        name: `Patient ${i + 1}`,
        age: Math.floor(Math.random() * 60) + 20,
        gender: Math.random() > 0.5 ? 'Male' : 'Female',
        lastVisit: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        provider: `Dr. ${['Martinez', 'Smith', 'Johnson', 'Williams', 'Brown'][Math.floor(Math.random() * 5)]}`,
        status: ['active', 'inactive', 'critical'][Math.floor(Math.random() * 3)],
        riskLevel: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
        ecdomeScore: Math.random() * 0.4 + 0.6
      }));
    }
  },

  // Get patient by ID
  getPatient: async (patientId) => {
    try {
      const response = await api.get(`/patients/${patientId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch patient:', error);
      throw new Error('Failed to fetch patient');
    }
  },

  // Get detailed patient data for dashboard using ABENA SDK
  getPatientData: async (patientId) => {
    try {
      // Use ABENA SDK for patient data with eCDome analysis
      const patientData = await abena.getPatientData(patientId, 'clinical-dashboard');
      
      // Simulate API delay for realistic experience
      await new Promise(resolve => setTimeout(resolve, 800));
      
      return patientData;
    } catch (error) {
      console.error('Failed to fetch patient data:', error);
      throw new Error('Failed to fetch patient data');
    }
  },

  // Get real-time patient data using ABENA SDK
  getRealtimeData: async (patientId) => {
    try {
      return await abena.getRealtimeData(patientId);
    } catch (error) {
      console.error('Failed to fetch real-time data:', error);
      throw new Error('Failed to fetch real-time data');
    }
  },

  // Get module analysis using ABENA SDK
  getModuleAnalysis: async (patientId, modules) => {
    try {
      return await abena.getModuleAnalysis(patientId, modules);
    } catch (error) {
      console.error('Failed to fetch module analysis:', error);
      throw new Error('Failed to fetch module analysis');
    }
  },

  // Get eCDome components using ABENA SDK
  getEcdomeComponents: async (patientId, timeRange = '24h') => {
    try {
      return await abena.getEcdomeComponents(patientId, timeRange);
    } catch (error) {
      console.error('Failed to fetch eCDome components:', error);
      throw new Error('Failed to fetch eCDome components');
    }
  },

  // Get predictive alerts using ABENA SDK
  getPredictiveAlerts: async (patientId) => {
    try {
      return await abena.getPredictiveAlerts(patientId);
    } catch (error) {
      console.error('Failed to fetch predictive alerts:', error);
      throw new Error('Failed to fetch predictive alerts');
    }
  },

  // Get clinical recommendations using ABENA SDK
  getClinicalRecommendations: async (patientId) => {
    try {
      return await abena.getClinicalRecommendations(patientId);
    } catch (error) {
      console.error('Failed to fetch clinical recommendations:', error);
      throw new Error('Failed to fetch clinical recommendations');
    }
  },

  // Send intervention using ABENA SDK
  sendIntervention: async (patientId, intervention) => {
    try {
      return await abena.sendIntervention(patientId, intervention);
    } catch (error) {
      console.error('Failed to send intervention:', error);
      throw new Error('Failed to send intervention');
    }
  },

  // Subscribe to real-time patient updates using ABENA SDK
  subscribeToPatient: (patientId, callback) => {
    try {
      return abena.subscribeToPatient(patientId, callback);
    } catch (error) {
      console.error('Failed to subscribe to patient:', error);
      throw new Error('Failed to subscribe to patient');
    }
  },

  // Unsubscribe from real-time updates
  unsubscribeFromPatient: (subscriptionId) => {
    try {
      return abena.unsubscribe(subscriptionId);
    } catch (error) {
      console.error('Failed to unsubscribe from patient:', error);
    }
  },

  // Create new patient
  createPatient: async (patientData) => {
    try {
      const response = await api.post('/patients', patientData);
      return response.data;
    } catch (error) {
      console.error('Failed to create patient:', error);
      throw new Error('Failed to create patient');
    }
  },

  // Update patient
  updatePatient: async (patientId, patientData) => {
    try {
      const response = await api.put(`/patients/${patientId}`, patientData);
      return response.data;
    } catch (error) {
      console.error('Failed to update patient:', error);
      throw new Error('Failed to update patient');
    }
  },

  // Delete patient
  deletePatient: async (patientId) => {
    try {
      await api.delete(`/patients/${patientId}`);
      return { success: true };
    } catch (error) {
      console.error('Failed to delete patient:', error);
      throw new Error('Failed to delete patient');
    }
  },

  // Search patients
  searchPatients: async (query) => {
    try {
      const response = await api.get(`/patients/search?q=${query}`);
      return response.data;
    } catch (error) {
      console.error('Failed to search patients:', error);
      // Return mock search results for development
      const allPatients = Array.from({ length: 50 }, (_, i) => ({
        id: `PAT-${(i + 1).toString().padStart(3, '0')}`,
        name: `Patient ${i + 1}`,
        age: Math.floor(Math.random() * 60) + 20,
        gender: Math.random() > 0.5 ? 'Male' : 'Female',
        lastVisit: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        provider: `Dr. ${['Martinez', 'Smith', 'Johnson', 'Williams', 'Brown'][Math.floor(Math.random() * 5)]}`,
        status: ['active', 'inactive', 'critical'][Math.floor(Math.random() * 3)],
        riskLevel: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)]
      }));
      
      return allPatients.filter(patient => 
        patient.name.toLowerCase().includes(query.toLowerCase()) ||
        patient.id.toLowerCase().includes(query.toLowerCase())
      );
    }
  },

  // Get patient history
  getPatientHistory: async (patientId, timeRange = '30d') => {
    try {
      const response = await api.get(`/patients/${patientId}/history?range=${timeRange}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch patient history:', error);
      // Return mock history for development
      return Array.from({ length: 30 }, (_, i) => ({
        date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        ecdomeScore: Math.random() * 0.3 + 0.7,
        alertsCount: Math.floor(Math.random() * 5),
        interventions: Math.floor(Math.random() * 3)
      }));
    }
  },

  // Initialize ABENA SDK
  initializeABENA: async () => {
    try {
      await abena.initialize();
      console.log('ABENA SDK initialized successfully');
    } catch (error) {
      console.error('Failed to initialize ABENA SDK:', error);
      // Continue with mock data in development
    }
  }
}; 