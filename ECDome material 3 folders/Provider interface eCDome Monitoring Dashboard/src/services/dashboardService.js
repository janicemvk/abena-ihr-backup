import axios from 'axios';
import abena from './abenaSDK';

// Base API configuration - Point to our local API Gateway
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api/v1/background-modules';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
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

// Dashboard service methods using ABENA SDK
export const dashboardService = {
  // Get real-time data using ABENA SDK
  getRealtimeData: async (patientId) => {
    try {
      return await abena.getRealtimeData(patientId);
    } catch (error) {
      console.error('Failed to fetch real-time data:', error);
      throw new Error('Failed to fetch real-time data');
    }
  },

  // Get dashboard metrics using ABENA SDK
  getDashboardMetrics: async (patientId, timeRange = '24h') => {
    try {
      // In production: const response = await api.get(`/dashboard/metrics/${patientId}?range=${timeRange}`);
      const mockMetrics = {
        avgEcdomeScore: 0.78 + Math.random() * 0.15,
        avgHeartRate: 70 + Math.random() * 10,
        avgBloodPressure: {
          systolic: 118 + Math.random() * 8,
          diastolic: 75 + Math.random() * 5
        },
        sleepEfficiency: 0.75 + Math.random() * 0.2,
        stressLevel: Math.random() * 100,
        alertsGenerated: Math.floor(Math.random() * 15),
        interventionsCompleted: Math.floor(Math.random() * 8),
        complianceScore: 0.8 + Math.random() * 0.15
      };
      
      await new Promise(resolve => setTimeout(resolve, 300));
      return mockMetrics;
    } catch (error) {
      console.error('Failed to fetch dashboard metrics:', error);
      throw new Error('Failed to fetch dashboard metrics');
    }
  },

  // Get system alerts using ABENA SDK
  getSystemAlerts: async (patientId) => {
    try {
      return await abena.getPredictiveAlerts(patientId);
    } catch (error) {
      console.error('Failed to fetch system alerts:', error);
      throw new Error('Failed to fetch system alerts');
    }
  },

  // Get chart data using ABENA SDK
  getChartData: async (patientId, chartType, timeRange = '24h') => {
    try {
      // Use ABENA SDK for specific chart types
      if (chartType === 'ecdome-timeline') {
        return await abena.getEcdomeComponents(patientId, timeRange);
      }
      
      // For other chart types, use mock data for now
      let mockData = [];
      const dataPoints = timeRange === '24h' ? 24 : timeRange === '7d' ? 7 : 30;
      
      for (let i = 0; i < dataPoints; i++) {
        const baseTime = new Date();
        if (timeRange === '24h') {
          baseTime.setHours(i);
        } else if (timeRange === '7d') {
          baseTime.setDate(baseTime.getDate() - (6 - i));
        } else {
          baseTime.setDate(baseTime.getDate() - (29 - i));
        }
        
        mockData.push({
          time: timeRange === '24h' ? 
            `${i.toString().padStart(2, '0')}:00` : 
            baseTime.toISOString().split('T')[0],
          anandamide: 0.65 + Math.sin(i * Math.PI / 12) * 0.15 + Math.random() * 0.05,
          twoAG: 0.58 + Math.sin(i * Math.PI / 12) * 0.12 + Math.random() * 0.05,
          cb1: 0.72 + Math.sin(i * Math.PI / 12) * 0.18 + Math.random() * 0.05,
          cb2: 0.68 + Math.sin(i * Math.PI / 12) * 0.15 + Math.random() * 0.05,
          heartRate: 70 + Math.sin(i * Math.PI / 12) * 8 + Math.random() * 5,
          bloodPressure: 120 + Math.sin(i * Math.PI / 12) * 10 + Math.random() * 5,
          stressLevel: 30 + Math.sin(i * Math.PI / 12) * 20 + Math.random() * 10,
          sleepQuality: 0.7 + Math.sin(i * Math.PI / 12) * 0.2 + Math.random() * 0.1
        });
      }
      
      await new Promise(resolve => setTimeout(resolve, 200));
      return mockData;
    } catch (error) {
      console.error('Failed to fetch chart data:', error);
      throw new Error('Failed to fetch chart data');
    }
  },

  // Send intervention using ABENA SDK
  sendIntervention: async (patientId, interventionData) => {
    try {
      return await abena.sendIntervention(patientId, interventionData);
    } catch (error) {
      console.error('Failed to send intervention:', error);
      throw new Error('Failed to send intervention');
    }
  },

  // Generate report using ABENA SDK
  generateReport: async (patientId, reportType, timeRange = '7d') => {
    try {
      // In production: const response = await api.post(`/dashboard/reports/${patientId}`, { type: reportType, range: timeRange });
      const mockReport = {
        id: Date.now(),
        patientId,
        type: reportType,
        timeRange,
        generatedAt: new Date().toISOString(),
        downloadUrl: `/api/reports/${Date.now()}.pdf`,
        status: 'completed',
        summary: {
          overallScore: 0.78 + Math.random() * 0.15,
          improvements: Math.floor(Math.random() * 5) + 1,
          concerns: Math.floor(Math.random() * 3),
          recommendations: Math.floor(Math.random() * 8) + 2
        }
      };
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      return mockReport;
    } catch (error) {
      console.error('Failed to generate report:', error);
      throw new Error('Failed to generate report');
    }
  },

  // Get system status using ABENA SDK
  getSystemStatus: async () => {
    try {
      // In production: const response = await api.get('/dashboard/system-status');
      const mockStatus = {
        overall: 'online',
        components: {
          abenaSDK: abena.isConnected ? 'online' : 'offline',
          dataProcessing: 'online',
          alertSystem: 'online',
          backupSystem: 'online',
          monitoring: 'online'
        },
        uptime: 99.98,
        lastMaintenance: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        activePatients: 247,
        dataPoints: 1.2e6,
        alertsProcessed: 1543
      };
      
      await new Promise(resolve => setTimeout(resolve, 100));
      return mockStatus;
    } catch (error) {
      console.error('Failed to fetch system status:', error);
      throw new Error('Failed to fetch system status');
    }
  },

  // Update dashboard settings using ABENA SDK
  updateDashboardSettings: async (settings) => {
    try {
      // In production: const response = await api.put('/dashboard/settings', settings);
      const updatedSettings = {
        ...settings,
        updatedAt: new Date().toISOString()
      };
      
      await new Promise(resolve => setTimeout(resolve, 300));
      return updatedSettings;
    } catch (error) {
      console.error('Failed to update dashboard settings:', error);
      throw new Error('Failed to update dashboard settings');
    }
  },

  // Subscribe to real-time updates using ABENA SDK
  subscribeToRealtimeUpdates: (patientId, callback) => {
    try {
      return abena.subscribeToPatient(patientId, callback);
    } catch (error) {
      console.error('Failed to subscribe to real-time updates:', error);
      throw new Error('Failed to subscribe to real-time updates');
    }
  },

  // Unsubscribe from real-time updates
  unsubscribeFromRealtimeUpdates: (subscriptionId) => {
    try {
      return abena.unsubscribe(subscriptionId);
    } catch (error) {
      console.error('Failed to unsubscribe from real-time updates:', error);
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

  // Get clinical recommendations using ABENA SDK
  getClinicalRecommendations: async (patientId) => {
    try {
      return await abena.getClinicalRecommendations(patientId);
    } catch (error) {
      console.error('Failed to fetch clinical recommendations:', error);
      throw new Error('Failed to fetch clinical recommendations');
    }
  },

  // Initialize ABENA SDK for dashboard
  initializeABENA: async () => {
    try {
      await abena.initialize();
      console.log('ABENA SDK initialized for dashboard');
    } catch (error) {
      console.error('Failed to initialize ABENA SDK:', error);
      // Continue with mock data in development
    }
  }
}; 