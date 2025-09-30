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

// Patient service methods using MOCK DATA for immediate display
export const patientService = {
  // Get all patients - USE MOCK DATA
  getPatients: async () => {
    try {
      // Mock patient list
      const mockPatients = [
        {
          id: 'PAT-001',
          name: 'John Doe',
          age: 40,
          gender: 'Male',
          status: 'active',
          riskLevel: 'medium',
          lastVisit: new Date().toISOString(),
          provider: 'Dr. Martinez'
        },
        {
          id: 'PAT-002',
          name: 'Jane Smith',
          age: 35,
          gender: 'Female',
          status: 'active',
          riskLevel: 'low',
          lastVisit: new Date().toISOString(),
          provider: 'Dr. Johnson'
        },
        {
          id: 'PAT-003',
          name: 'Mike Wilson',
          age: 55,
          gender: 'Male',
          status: 'active',
          riskLevel: 'high',
          lastVisit: new Date().toISOString(),
          provider: 'Dr. Martinez'
        }
      ];
      
      console.log('✅ Mock patient data loaded:', mockPatients.length, 'patients');
      return mockPatients;
    } catch (error) {
      console.error('❌ Failed to load mock patients:', error);
      throw new Error('Failed to load patient data');
    }
  },

  // Get patient by ID - USE MOCK DATA
  getPatient: async (patientId) => {
    try {
      // Mock patient data
      const mockPatient = {
        id: patientId,
        name: 'John Doe',
        age: 40,
        gender: 'Male',
        status: 'active',
        riskLevel: 'medium',
        lastVisit: new Date().toISOString(),
        provider: 'Dr. Martinez'
      };
      
      console.log('✅ Mock patient data loaded for:', patientId);
      return mockPatient;
    } catch (error) {
      console.error('❌ Failed to load mock patient:', error);
      throw new Error('Failed to load patient data');
    }
  },

  // Get detailed patient data - USE MOCK DATA
  getPatientData: async (patientId) => {
    try {
      // Mock detailed patient data
      const mockPatientData = {
        success: true,
        data: {
          patientInfo: {
            id: patientId,
            name: 'John Doe',
            age: 40,
            gender: 'Male',
            lastVisit: new Date().toISOString(),
            provider: 'Dr. Martinez',
            status: 'active',
            riskLevel: 'medium',
            ecdomeScore: 0.75,
            vitalSigns: {
              heartRate: 72,
              bloodPressure: '120/80',
              temperature: 98.6,
              oxygenSaturation: 98
            },
            medications: [
              { name: 'Metformin', dosage: '500mg', frequency: 'Twice daily' },
              { name: 'Lisinopril', dosage: '10mg', frequency: 'Once daily' }
            ],
            allergies: ['Penicillin', 'Shellfish'],
            conditions: ['Type 2 Diabetes', 'Hypertension'],
            lastLabResults: {
              glucose: 95,
              hba1c: 6.2,
              cholesterol: 180
            }
          },
          ecdomeProfile: {
            score: 0.75,
            status: 'Good',
            components: {
              endocannabinoid: { status: 'active', reading: 0.80 },
              metabolic: { status: 'active', reading: 0.75 },
              immune: { status: 'active', reading: 0.70 },
              hormonal: { status: 'active', reading: 0.80 }
            }
          },
          timestamp: new Date().toISOString()
        }
      };
      
      console.log('✅ Mock patient data loaded for:', patientId);
      return mockPatientData;
    } catch (error) {
      console.error('❌ Failed to load mock patient data:', error);
      throw new Error('Failed to load patient data');
    }
  },

  // Get real-time patient data - USE MOCK DATA
  getRealtimeData: async (patientId) => {
    try {
      // Mock real-time data
      const mockRealtimeData = {
        success: true,
        data: {
          patientId: patientId,
          timestamp: new Date().toISOString(),
          vitalSigns: {
            heartRate: Math.floor(Math.random() * 20) + 60, // 60-80
            bloodPressure: `${Math.floor(Math.random() * 20) + 110}/${Math.floor(Math.random() * 10) + 70}`,
            temperature: (Math.random() * 2 + 97).toFixed(1), // 97-99
            oxygenSaturation: Math.floor(Math.random() * 5) + 95 // 95-99
          },
          ecdomeReadings: {
            endocannabinoid: (Math.random() * 0.4 + 0.6).toFixed(2), // 0.6-1.0
            metabolic: (Math.random() * 0.4 + 0.6).toFixed(2),
            immune: (Math.random() * 0.4 + 0.6).toFixed(2),
            hormonal: (Math.random() * 0.4 + 0.6).toFixed(2)
          },
          alerts: [],
          status: 'stable'
        }
      };
      
      console.log('✅ Mock real-time data loaded for:', patientId);
      return mockRealtimeData;
    } catch (error) {
      console.error('❌ Failed to load mock real-time data:', error);
      throw new Error('Failed to load real-time data');
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