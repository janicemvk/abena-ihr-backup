/**
 * ABENA SDK - Advanced Biological & Environmental Network Analysis
 * Provider Interface for eCDome Data - Clinical Monitoring Dashboard
 * 
 * This SDK provides standardized access to the endocannabinoid system (eCDome)
 * monitoring data and the 12 core biological modules.
 */

import axios from 'axios';

// ABENA SDK Configuration - Point to our local services
const ABENA_CONFIG = {
  apiUrl: process.env.REACT_APP_ABENA_API_URL || 'http://localhost:8080/api/v1/background-modules',
  wsUrl: process.env.REACT_APP_ABENA_WS_URL || 'ws://localhost:8080',
  clientId: process.env.REACT_APP_ABENA_CLIENT_ID || 'clinical-dashboard',
  version: '1.0.0',
  timeout: 30000,
  retryAttempts: 3,
  retryDelay: 1000
};

// ABENA Module Definitions
const ABENA_MODULES = {
  METABOLOME: 'metabolome',
  MICROBIOME: 'microbiome', 
  INFLAMMATOME: 'inflammatome',
  IMMUNOME: 'immunome',
  CHRONOBIOME: 'chronobiome',
  NUTRIOME: 'nutriome',
  TOXICOME: 'toxicome',
  PHARMACOME: 'pharmacome',
  STRESS_RESPONSE: 'stressResponse',
  CARDIOVASCULAR: 'cardiovascular',
  NEUROLOGICAL: 'neurological',
  HORMONAL: 'hormonal'
};

// ABENA eCDome Components
const ECDOME_COMPONENTS = {
  ANANDAMIDE: 'anandamide',
  TWO_AG: 'twoAG',
  CB1_RECEPTOR: 'cb1',
  CB2_RECEPTOR: 'cb2',
  FAAH_ENZYME: 'faah',
  MAGL_ENZYME: 'magl',
  SYSTEM_BALANCE: 'systemBalance'
};

// ABENA Alert Types
const ALERT_TYPES = {
  CRITICAL: 'critical',
  WARNING: 'warning',
  INFO: 'info',
  PREDICTIVE: 'predictive'
};

class ABENAClient {
  constructor(config = {}) {
    this.config = { ...ABENA_CONFIG, ...config };
    this.wsConnection = null;
    this.subscriptions = new Map();
    this.cache = new Map();
    this.isConnected = false;
    
    // Initialize HTTP client
    this.httpClient = axios.create({
      baseURL: this.config.apiUrl,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
        'X-ABENA-Client': this.config.clientId,
        'X-ABENA-Version': this.config.version
      }
    });

    // Setup request/response interceptors
    this.setupInterceptors();
  }

  setupInterceptors() {
    // Request interceptor
    this.httpClient.interceptors.request.use(
      (config) => {
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        config.headers['X-ABENA-Timestamp'] = new Date().toISOString();
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.httpClient.interceptors.response.use(
      (response) => {
        // Cache successful responses
        if (response.config.method === 'get') {
          this.cache.set(response.config.url, {
            data: response.data,
            timestamp: Date.now()
          });
        }
        return response;
      },
      (error) => {
        if (error.response?.status === 401) {
          this.handleAuthError();
        }
        return Promise.reject(error);
      }
    );
  }

  getAuthToken() {
    return localStorage.getItem('abena_token');
  }

  handleAuthError() {
    localStorage.removeItem('abena_token');
    window.dispatchEvent(new CustomEvent('abena:auth:expired'));
  }

  // Core SDK Methods

  /**
   * Initialize ABENA SDK connection
   */
  async initialize() {
    try {
      const response = await this.httpClient.post('/auth/initialize', {
        clientId: this.config.clientId,
        version: this.config.version
      });
      
      this.isConnected = true;
      return response.data;
    } catch (error) {
      console.error('ABENA SDK initialization failed:', error);
      throw error;
    }
  }

  /**
   * Get patient data with eCDome analysis
   */
  async getPatientData(patientId, moduleScope = 'clinical-dashboard') {
    try {
      const response = await this.httpClient.get(`/patients/${patientId}/ecdome`, {
        params: { scope: moduleScope }
      });
      
      return this.formatPatientData(response.data);
    } catch (error) {
      console.error('Failed to fetch patient data:', error);
      return this.getMockPatientData(patientId);
    }
  }

  /**
   * Get real-time eCDome monitoring data
   */
  async getRealtimeData(patientId) {
    try {
      const response = await this.httpClient.get(`/patients/${patientId}/realtime`);
      return this.formatRealtimeData(response.data);
    } catch (error) {
      console.error('Failed to fetch real-time data:', error);
      return this.getMockRealtimeData();
    }
  }

  /**
   * Get module-specific analysis
   */
  async getModuleAnalysis(patientId, modules = Object.values(ABENA_MODULES)) {
    try {
      const response = await this.httpClient.post(`/patients/${patientId}/modules/analyze`, {
        modules,
        includeComparisons: true,
        includePredictions: true
      });
      
      return response.data;
    } catch (error) {
      console.error('Failed to fetch module analysis:', error);
      return this.getMockModuleAnalysis(modules);
    }
  }

  /**
   * Get eCDome component levels
   */
  async getEcdomeComponents(patientId, timeRange = '24h') {
    try {
      const response = await this.httpClient.get(`/patients/${patientId}/ecdome/components`, {
        params: { timeRange }
      });
      
      return response.data;
    } catch (error) {
      console.error('Failed to fetch eCDome components:', error);
      return this.getMockEcdomeComponents();
    }
  }

  /**
   * Get predictive alerts
   */
  async getPredictiveAlerts(patientId) {
    try {
      const response = await this.httpClient.get(`/patients/${patientId}/alerts/predictive`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch predictive alerts:', error);
      return this.getMockPredictiveAlerts();
    }
  }

  /**
   * Get clinical recommendations
   */
  async getClinicalRecommendations(patientId) {
    try {
      const response = await this.httpClient.get(`/patients/${patientId}/recommendations`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch clinical recommendations:', error);
      return this.getMockClinicalRecommendations();
    }
  }

  /**
   * Send intervention
   */
  async sendIntervention(patientId, intervention) {
    try {
      const response = await this.httpClient.post(`/patients/${patientId}/interventions`, {
        ...intervention,
        timestamp: new Date().toISOString(),
        provider: this.getCurrentProvider()
      });
      
      return response.data;
    } catch (error) {
      console.error('Failed to send intervention:', error);
      throw error;
    }
  }

  // WebSocket Methods for Real-time Updates

  /**
   * Subscribe to real-time patient data
   */
  subscribeToPatient(patientId, callback) {
    if (!this.wsConnection) {
      this.initializeWebSocket();
    }

    const subscriptionId = `patient:${patientId}`;
    this.subscriptions.set(subscriptionId, callback);

    if (this.wsConnection && this.wsConnection.readyState === WebSocket.OPEN) {
      this.wsConnection.send(JSON.stringify({
        type: 'subscribe',
        channel: 'patient-data',
        patientId: patientId
      }));
    }

    return subscriptionId;
  }

  /**
   * Unsubscribe from real-time updates
   */
  unsubscribe(subscriptionId) {
    this.subscriptions.delete(subscriptionId);
  }

  /**
   * Initialize WebSocket connection
   */
  initializeWebSocket() {
    try {
      this.wsConnection = new WebSocket(this.config.wsUrl);
      
      this.wsConnection.onopen = () => {
        console.log('ABENA WebSocket connected');
      };
      
      this.wsConnection.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this.handleWebSocketMessage(message);
      };
      
      this.wsConnection.onclose = () => {
        console.log('ABENA WebSocket disconnected');
        setTimeout(() => this.initializeWebSocket(), 5000);
      };
      
      this.wsConnection.onerror = (error) => {
        console.error('ABENA WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
    }
  }

  handleWebSocketMessage(message) {
    const { type, patientId, data } = message;
    const subscriptionId = `patient:${patientId}`;
    
    if (this.subscriptions.has(subscriptionId)) {
      const callback = this.subscriptions.get(subscriptionId);
      callback(data);
    }
  }

  // Data Formatting Methods

  formatPatientData(rawData) {
    return {
      patientInfo: rawData.patient,
      ecdomeProfile: rawData.ecdome_profile,
      moduleData: rawData.modules,
      timelineData: rawData.timeline,
      predictiveAlerts: rawData.alerts || [],
      recommendations: rawData.recommendations || []
    };
  }

  formatRealtimeData(rawData) {
    return {
      timestamp: rawData.timestamp,
      heartRate: rawData.vitals?.heart_rate,
      bloodPressure: rawData.vitals?.blood_pressure,
      ecdomeActivity: rawData.ecdome?.activity_level,
      ...rawData
    };
  }

  // Mock Data Methods (for development)

  getMockPatientData(patientId) {
    return {
      patientInfo: {
        id: patientId,
        name: `Patient ${patientId}`,
        age: Math.floor(Math.random() * 60) + 20,
        gender: Math.random() > 0.5 ? 'Male' : 'Female',
        lastVisit: new Date().toISOString().split('T')[0],
        provider: 'Dr. Martinez'
      },
      ecdomeProfile: {
        overallScore: 0.78 + Math.random() * 0.15,
        anandamideLevels: 0.65 + Math.random() * 0.2,
        twoAGLevels: 0.58 + Math.random() * 0.25,
        cb1Activity: 0.72 + Math.random() * 0.18,
        cb2Activity: 0.68 + Math.random() * 0.15,
        systemBalance: 0.75 + Math.random() * 0.2
      },
      moduleData: this.generateMockModuleData(),
      timelineData: this.generateMockTimelineData(),
      predictiveAlerts: this.getMockPredictiveAlerts(),
      recommendations: this.getMockClinicalRecommendations()
    };
  }

  getMockRealtimeData() {
    return {
      timestamp: new Date().toISOString(),
      heartRate: 68 + Math.random() * 12,
      bloodPressure: {
        systolic: 115 + Math.random() * 10,
        diastolic: 72 + Math.random() * 8
      },
      ecdomeActivity: 0.78 + Math.random() * 0.15,
      temperature: 98.2 + Math.random() * 1.2,
      oxygenSaturation: 97 + Math.random() * 2,
      stressLevel: Math.random() * 100,
      sleepQuality: 0.6 + Math.random() * 0.3
    };
  }

  generateMockModuleData() {
    const modules = {};
    Object.values(ABENA_MODULES).forEach(module => {
      modules[module] = {
        score: Math.random() * 0.4 + 0.6,
        status: ['excellent', 'optimal', 'good', 'moderate', 'suboptimal'][Math.floor(Math.random() * 5)],
        trend: ['improving', 'stable', 'declining'][Math.floor(Math.random() * 3)]
      };
    });
    return modules;
  }

  generateMockTimelineData() {
    return Array.from({ length: 24 }, (_, i) => ({
      time: `${i.toString().padStart(2, '0')}:00`,
      anandamide: 0.65 + Math.sin(i * Math.PI / 12) * 0.15 + Math.random() * 0.05,
      twoAG: 0.58 + Math.sin(i * Math.PI / 12) * 0.12 + Math.random() * 0.05,
      cb1: 0.72 + Math.sin(i * Math.PI / 12) * 0.18 + Math.random() * 0.05,
      cb2: 0.68 + Math.sin(i * Math.PI / 12) * 0.15 + Math.random() * 0.05
    }));
  }

  getMockPredictiveAlerts() {
    return [
      {
        type: 'stress-overload',
        severity: 'high',
        timeframe: '3-weeks',
        confidence: 0.94,
        message: 'Elevated stress markers detected in eCDome analysis'
      },
      {
        type: 'metabolic-disruption',
        severity: 'medium',
        timeframe: '6-weeks',
        confidence: 0.87,
        message: 'Metabolic imbalance trending negatively'
      }
    ];
  }

  getMockClinicalRecommendations() {
    return [
      {
        priority: 'high',
        category: 'eCDome',
        action: 'Optimize endocannabinoid synthesis with targeted nutrition',
        estimatedImprovement: '15-20%'
      },
      {
        priority: 'medium',
        category: 'Sleep',
        action: 'Implement circadian rhythm optimization protocol',
        estimatedImprovement: '10-15%'
      }
    ];
  }

  getCurrentProvider() {
    return 'Dr. Martinez'; // In production, get from auth context
  }
}

// Export singleton instance
export const abena = new ABENAClient();

// Export constants for use in components
export { ABENA_MODULES, ECDOME_COMPONENTS, ALERT_TYPES };

// Export types for TypeScript users
export default abena; 