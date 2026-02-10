import axios from 'axios';
import API_CONFIG from '../config/api.config';

// Create axios instances for each service
const createApiInstance = (baseURL) => {
  return axios.create({
    baseURL,
    ...API_CONFIG.DEFAULT_CONFIG
  });
};

// Initialize API instances
const ihrIntelligenceApi = createApiInstance(API_CONFIG.BASE_URLS.IHR_INTELLIGENCE);
const medicalDbApi = createApiInstance(API_CONFIG.BASE_URLS.MEDICAL_DB);
const drugInteractionsApi = createApiInstance(API_CONFIG.BASE_URLS.DRUG_INTERACTIONS);
const scientificLitApi = createApiInstance(API_CONFIG.BASE_URLS.SCIENTIFIC_LIT);
const labResultsApi = createApiInstance(API_CONFIG.BASE_URLS.LAB_RESULTS);

// Error handling middleware
export const handleApiError = (error) => {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    switch (error.response.status) {
      case 401:
        return new Error(API_CONFIG.ERROR_MESSAGES.UNAUTHORIZED);
      case 404:
        return new Error(API_CONFIG.ERROR_MESSAGES.NOT_FOUND);
      case 422:
        return new Error(API_CONFIG.ERROR_MESSAGES.VALIDATION_ERROR);
      default:
        return new Error(API_CONFIG.ERROR_MESSAGES.SERVER_ERROR);
    }
  } else if (error.request) {
    // The request was made but no response was received
    return new Error(API_CONFIG.ERROR_MESSAGES.NETWORK_ERROR);
  } else {
    // Something happened in setting up the request that triggered an Error
    return error;
  }
};

// IHR Intelligence Service
export const ihrIntelligenceService = {
  processPatientData: async (patientId) => {
    try {
      const response = await ihrIntelligenceApi.post(
        API_CONFIG.ENDPOINTS.IHR_INTELLIGENCE.PROCESS_PATIENT_DATA,
        { patientId }
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getRealTimeMetrics: async (patientId) => {
    try {
      const response = await ihrIntelligenceApi.get(
        `${API_CONFIG.ENDPOINTS.IHR_INTELLIGENCE.GET_REAL_TIME_METRICS}/${patientId}`
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getAnalysisHistory: async (patientId) => {
    try {
      const response = await ihrIntelligenceApi.get(
        `${API_CONFIG.ENDPOINTS.IHR_INTELLIGENCE.GET_ANALYSIS_HISTORY}/${patientId}`
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  analyzeEndocannabinoidLevels: async (levels) => {
    try {
      const response = await ihrIntelligenceApi.post(
        API_CONFIG.ENDPOINTS.IHR_INTELLIGENCE.ANALYZE_ENDOCANNABINOID_LEVELS,
        { levels }
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  analyzeReceptorActivity: async (activity) => {
    try {
      const response = await ihrIntelligenceApi.post(
        API_CONFIG.ENDPOINTS.IHR_INTELLIGENCE.ANALYZE_RECEPTOR_ACTIVITY,
        { activity }
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getTreatmentRecommendations: async (metrics, medications) => {
    try {
      const response = await ihrIntelligenceApi.post(
        API_CONFIG.ENDPOINTS.IHR_INTELLIGENCE.GET_TREATMENT_RECOMMENDATIONS,
        { metrics, medications }
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
};

// Medical Database Service
export const medicalDatabaseService = {
  getPatientHistory: async (patientId) => {
    try {
      const response = await medicalDbApi.get(
        `${API_CONFIG.ENDPOINTS.MEDICAL_DB.GET_PATIENT_HISTORY}/${patientId}`
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getMedicalConditions: async (patientId) => {
    try {
      const response = await medicalDbApi.get(
        `${API_CONFIG.ENDPOINTS.MEDICAL_DB.GET_MEDICAL_CONDITIONS}/${patientId}`
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getTreatmentHistory: async (patientId) => {
    try {
      const response = await medicalDbApi.get(
        `${API_CONFIG.ENDPOINTS.MEDICAL_DB.GET_TREATMENT_HISTORY}/${patientId}`
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
};

// Drug Interactions Service
export const drugInteractionsService = {
  checkInteractions: async (medications, cannabinoids) => {
    try {
      const response = await drugInteractionsApi.post(
        API_CONFIG.ENDPOINTS.DRUG_INTERACTIONS.CHECK_INTERACTIONS,
        { medications, cannabinoids }
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getDrugInfo: async (drugId) => {
    try {
      const response = await drugInteractionsApi.get(
        `${API_CONFIG.ENDPOINTS.DRUG_INTERACTIONS.GET_DRUG_INFO}/${drugId}`
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
};

// Scientific Literature Service
export const scientificLiteratureService = {
  searchLiterature: async (query) => {
    try {
      const response = await scientificLitApi.get(
        API_CONFIG.ENDPOINTS.SCIENTIFIC_LIT.SEARCH_LITERATURE,
        { params: { query } }
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getArticleDetails: async (articleId) => {
    try {
      const response = await scientificLitApi.get(
        `${API_CONFIG.ENDPOINTS.SCIENTIFIC_LIT.GET_ARTICLE_DETAILS}/${articleId}`
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
};

// Lab Results Service
export const labResultsService = {
  getLabResults: async (patientId) => {
    try {
      const response = await labResultsApi.get(
        `${API_CONFIG.ENDPOINTS.LAB_RESULTS.GET_LAB_RESULTS}/${patientId}`
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getEndocannabinoidLevels: async (patientId) => {
    try {
      const response = await labResultsApi.get(
        `${API_CONFIG.ENDPOINTS.LAB_RESULTS.GET_ENDOCANNABINOID_LEVELS}/${patientId}`
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getReceptorActivity: async (patientId) => {
    try {
      const response = await labResultsApi.get(
        `${API_CONFIG.ENDPOINTS.LAB_RESULTS.GET_RECEPTOR_ACTIVITY}/${patientId}`
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
}; 