const API_CONFIG = {
  // Base URLs for different services
  BASE_URLS: {
    IHR_INTELLIGENCE: process.env.REACT_APP_IHR_INTELLIGENCE_URL || 'http://138.68.24.154:4002/api/v1',
    MEDICAL_DB: process.env.REACT_APP_MEDICAL_DB_URL || 'http://138.68.24.154:4002/api/v1',
    DRUG_INTERACTIONS: process.env.REACT_APP_DRUG_INTERACTIONS_URL || 'http://138.68.24.154:4002/api/v1',
    SCIENTIFIC_LIT: process.env.REACT_APP_SCIENTIFIC_LIT_URL || 'http://138.68.24.154:4002/api/v1',
    LAB_RESULTS: process.env.REACT_APP_LAB_RESULTS_URL || 'http://138.68.24.154:4002/api/v1'
  },

  // API endpoints for each service - using existing ABENA IHR endpoints
  ENDPOINTS: {
    IHR_INTELLIGENCE: {
      PROCESS_PATIENT_DATA: '/patients',
      GET_REAL_TIME_METRICS: '/patients',
      GET_ANALYSIS_HISTORY: '/outcomes',
      ANALYZE_ENDOCANNABINOID_LEVELS: '/outcomes',
      ANALYZE_RECEPTOR_ACTIVITY: '/outcomes',
      GET_TREATMENT_RECOMMENDATIONS: '/predictions'
    },
    MEDICAL_DB: {
      GET_PATIENT_HISTORY: '/patients',
      GET_MEDICAL_CONDITIONS: '/outcomes',
      GET_TREATMENT_HISTORY: '/outcomes'
    },
    DRUG_INTERACTIONS: {
      CHECK_INTERACTIONS: '/outcomes',
      GET_DRUG_INFO: '/outcomes'
    },
    SCIENTIFIC_LIT: {
      SEARCH_LITERATURE: '/outcomes',
      GET_ARTICLE_DETAILS: '/outcomes'
    },
    LAB_RESULTS: {
      GET_LAB_RESULTS: '/measurements',
      GET_ENDOCANNABINOID_LEVELS: '/measurements',
      GET_RECEPTOR_ACTIVITY: '/measurements'
    }
  },

  // Default request configuration
  DEFAULT_CONFIG: {
    timeout: 30000, // 30 seconds
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  },

  // Error messages
  ERROR_MESSAGES: {
    NETWORK_ERROR: 'Unable to connect to the server. Please check your internet connection.',
    TIMEOUT_ERROR: 'Request timed out. Please try again.',
    SERVER_ERROR: 'An error occurred on the server. Please try again later.',
    UNAUTHORIZED: 'You are not authorized to access this resource.',
    NOT_FOUND: 'The requested resource was not found.',
    VALIDATION_ERROR: 'Invalid input data. Please check your request.'
  },

  CLAUDE_AI: {
    BASE_URL: 'https://api.anthropic.com/v1/messages',
    API_KEY: 'YOUR_CLAUDE_API_KEY' // Replace with your actual Claude API key
  },
  CONSENSUS_AI: {
    BASE_URL: 'https://api.consensus.app/v1/search',
    API_KEY: 'YOUR_CONSENSUS_API_KEY' // Replace with your actual Consensus API key
  }
};

export default API_CONFIG; 