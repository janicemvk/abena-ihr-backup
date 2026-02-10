import AbenaSDK from '@abena/sdk';

// Initialize Abena SDK for all operations
const abenaSDK = new AbenaSDK({
  authServiceUrl: 'http://localhost:3001',
  dataServiceUrl: 'http://localhost:8001',
  privacyServiceUrl: 'http://localhost:8002',
  blockchainServiceUrl: 'http://localhost:8003'
});

// Abena SDK middleware - handles all auth, privacy, and audit automatically
const abenaMiddleware = async (req, res, next) => {
  try {
    // 1. Auto-handled auth & permissions via Abena SDK
    const authContext = await abenaSDK.validateRequest(req, 'api_gateway');
    
    // 2. Auto-handled privacy & encryption
    // 3. Auto-handled audit logging
    
    // 4. Focus on your business logic
    req.abenaContext = authContext;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Authentication failed' });
  }
};

// eCBome Correlation Engine using Abena SDK
class ECbomeCorrelationEngine {
  constructor() {
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003'
    });
    this.patterns = new Map();
    this.confidenceThreshold = 80;
  }
  
  async analyzeCorrelations(data, patientId, userId) {
    // 1. Auto-handled auth & permissions
    const patientData = await this.abena.getPatientData(patientId, 'ecbome_analysis');
    
    // 2. Auto-handled privacy & encryption
    const encryptedData = await this.abena.encryptHealthData(data, patientId);
    
    // 3. Auto-handled audit logging
    await this.abena.logDataAccess(patientId, userId, 'analyze', 'ecbome_correlations');
    
    // 4. Focus on your business logic
    const correlations = {
      biomarkers: [],
      patterns: [],
      confidence: 0,
      timestamp: new Date().toISOString()
    };
    
    // Mock correlation analysis - replace with actual eCBome analysis
    if (data.heartRate && data.mood) {
      correlations.biomarkers.push({
        name: 'AEA',
        correlation: 0.87,
        confidence: 94,
        pattern: 'Stress Response'
      });
    }
    
    if (data.sleepQuality && data.activity) {
      correlations.biomarkers.push({
        name: '2-AG',
        correlation: 0.92,
        confidence: 89,
        pattern: 'Circadian Rhythm'
      });
    }
    
    // Calculate overall confidence
    if (correlations.biomarkers.length > 0) {
      correlations.confidence = correlations.biomarkers.reduce((sum, bio) => sum + bio.confidence, 0) / correlations.biomarkers.length;
    }
    
    return correlations;
  }
  
  async updatePatterns(correlations, patientId, userId) {
    // 1. Auto-handled auth & permissions
    await this.abena.getPatientData(patientId, 'pattern_update');
    
    // 2. Auto-handled privacy & encryption
    // 3. Auto-handled audit logging
    await this.abena.logDataAccess(patientId, userId, 'update', 'ecbome_patterns');
    
    // 4. Focus on your business logic
    correlations.biomarkers.forEach(biomarker => {
      const key = `${biomarker.name}_${biomarker.pattern}`;
      if (!this.patterns.has(key)) {
        this.patterns.set(key, {
          count: 0,
          avgConfidence: 0,
          lastSeen: null
        });
      }
      
      const pattern = this.patterns.get(key);
      pattern.count++;
      pattern.avgConfidence = (pattern.avgConfidence * (pattern.count - 1) + biomarker.confidence) / pattern.count;
      pattern.lastSeen = new Date().toISOString();
    });
  }
}

// eCBome Analysis Module using Abena SDK
class ECbomeAnalysisModule {
  constructor() {
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003'
    });
    this.analysisHistory = [];
  }
  
  async updatePatterns(correlations, patientId, userId) {
    // 1. Auto-handled auth & permissions
    await this.abena.getPatientData(patientId, 'analysis_update');
    
    // 2. Auto-handled privacy & encryption
    const encryptedAnalysis = await this.abena.encryptHealthData(correlations, patientId);
    
    // 3. Auto-handled audit logging
    await this.abena.logDataAccess(patientId, userId, 'update', 'analysis_patterns');
    
    // 4. Focus on your business logic
    this.analysisHistory.push({
      ...correlations,
      analyzedAt: new Date().toISOString()
    });
    
    // Keep only last 1000 analyses
    if (this.analysisHistory.length > 1000) {
      this.analysisHistory = this.analysisHistory.slice(-1000);
    }
    
    console.log('eCBome patterns updated:', correlations);
  }
  
  async getAnalysisHistory(patientId, userId) {
    // 1. Auto-handled auth & permissions
    await this.abena.getPatientData(patientId, 'analysis_history');
    
    // 2. Auto-handled privacy & encryption
    // 3. Auto-handled audit logging
    await this.abena.logDataAccess(patientId, userId, 'read', 'analysis_history');
    
    // 4. Focus on your business logic
    return this.analysisHistory;
  }
}

// Initialize eCBome components
const eCBomeCorrelationEngine = new ECbomeCorrelationEngine();
const eCBomeAnalysisModule = new ECbomeAnalysisModule();

// Add eCBome correlation hook using Abena SDK
const onDataIngested = async (data, patientId, userId) => {
  // 1. Auto-handled auth & permissions
  // 2. Auto-handled privacy & encryption
  // 3. Auto-handled audit logging
  
  // 4. Focus on your business logic
  const correlations = await eCBomeCorrelationEngine.analyzeCorrelations(data, patientId, userId);
  
  if (correlations.confidence > 80) {
    await eCBomeAnalysisModule.updatePatterns(correlations, patientId, userId);
  }
};

// Export only Abena SDK components
module.exports = {
  abenaMiddleware,
  onDataIngested,
  eCBomeCorrelationEngine,
  eCBomeAnalysisModule
}; 