const API_CONFIG = {
  // Base URLs for different services
  BASE_URLS: {
    IHR_INTELLIGENCE: process.env.REACT_APP_IHR_INTELLIGENCE_URL || 'http://localhost:8000/api/ihr',
    MEDICAL_DB: process.env.REACT_APP_MEDICAL_DB_URL || 'http://localhost:8000/api/medical',
    DRUG_INTERACTIONS: process.env.REACT_APP_DRUG_INTERACTIONS_URL || 'http://localhost:8000/api/drugs',
    SCIENTIFIC_LIT: process.env.REACT_APP_SCIENTIFIC_LIT_URL || 'http://localhost:8000/api/literature',
    LAB_RESULTS: process.env.REACT_APP_LAB_RESULTS_URL || 'http://localhost:8000/api/labs'
  },

  // API endpoints for each service
  ENDPOINTS: {
    IHR_INTELLIGENCE: {
      PROCESS_PATIENT_DATA: '/process',
      GET_REAL_TIME_METRICS: '/metrics',
      GET_ANALYSIS_HISTORY: '/history',
      ANALYZE_ENDOCANNABINOID_LEVELS: '/analyze/levels',
      ANALYZE_RECEPTOR_ACTIVITY: '/analyze/receptors',
      GET_TREATMENT_RECOMMENDATIONS: '/recommendations'
    },
    MEDICAL_DB: {
      GET_PATIENT_HISTORY: '/patient',
      GET_MEDICAL_CONDITIONS: '/conditions',
      GET_TREATMENT_HISTORY: '/treatments'
    },
    DRUG_INTERACTIONS: {
      CHECK_INTERACTIONS: '/check',
      GET_DRUG_INFO: '/info'
    },
    SCIENTIFIC_LIT: {
      SEARCH_LITERATURE: '/search',
      GET_ARTICLE_DETAILS: '/article'
    },
    LAB_RESULTS: {
      GET_LAB_RESULTS: '/results',
      GET_ENDOCANNABINOID_LEVELS: '/endocannabinoids',
      GET_RECEPTOR_ACTIVITY: '/receptors'
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