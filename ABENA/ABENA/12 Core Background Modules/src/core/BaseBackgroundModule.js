import AbenaSDK from '@abena/sdk';

/**
 * BASE MODULE CLASS
 * All 12 core modules extend this base class for consistent functionality
 */
export default class BaseBackgroundModule {
  constructor(moduleName, moduleConfig = {}) {
    this.moduleName = moduleName;
    this.moduleId = `${moduleName}-background-module`;
    this.version = '2.0.0';
    
    // ✅ Uses Abena SDK for all core services
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003',
      ecbomeServiceUrl: 'http://localhost:8004',
      correlationEngineUrl: 'http://localhost:8005',
      ...moduleConfig.serviceUrls
    });

    // Module configuration
    this.config = {
      samplingInterval: 900000, // 15 minutes
      analysisInterval: 1800000, // 30 minutes
      deepAnalysisInterval: 14400000, // 4 hours
      alertThresholds: moduleConfig.alertThresholds || {},
      ecbomeCorrelationTypes: moduleConfig.ecbomeCorrelationTypes || [],
      ...moduleConfig
    };

    // Initialize real-time monitoring
    this.isRunning = false;
    this.lastAnalysis = null;
    this.intervalIds = [];
  }

  // Start background monitoring
  async startBackgroundMonitoring(patientId, userId) {
    if (this.isRunning) return;
    
    this.isRunning = true;
    this.patientId = patientId;
    this.userId = userId;

    // Initial baseline analysis
    await this.performInitialAnalysis();

    // Set up continuous monitoring intervals
    this.setupMonitoringIntervals();
    
    await this.abena.logActivity(`${this.moduleName}-background-started`, {
      patientId, userId, timestamp: new Date().toISOString()
    });
  }

  // Stop background monitoring
  stopBackgroundMonitoring() {
    this.isRunning = false;
    this.intervalIds.forEach(id => clearInterval(id));
    this.intervalIds = [];
  }

  // Setup monitoring intervals (implemented by each module)
  setupMonitoringIntervals() {
    // Override in each specific module
  }

  // Base analysis method (implemented by each module)
  async performAnalysis() {
    throw new Error(`performAnalysis must be implemented by ${this.moduleName}`);
  }

  // Initial analysis method (implemented by each module)
  async performInitialAnalysis() {
    try {
      await this.performAnalysis();
      await this.abena.logActivity(`${this.moduleName}-initial-analysis-completed`, {
        patientId: this.patientId,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      await this.abena.logError(`${this.moduleName}-initial-analysis-failed`, error);
    }
  }

  // Base eCBome correlation method
  async correlateWithECBome(moduleData) {
    try {
      const correlations = {};
      
      for (const correlationType of this.config.ecbomeCorrelationTypes) {
        correlations[correlationType] = await this.abena.getECBomeCorrelations(
          this.patientId,
          correlationType
        );
      }

      return correlations;
    } catch (error) {
      await this.abena.logError(`${this.moduleName}-ecbome-correlation`, error);
      return {};
    }
  }

  // Generate alerts based on thresholds
  async generateAlerts(analysisData, alertType) {
    try {
      const alerts = [];
      const thresholds = this.config.alertThresholds;

      for (const [metric, threshold] of Object.entries(thresholds)) {
        if (analysisData[metric] && analysisData[metric] > threshold) {
          alerts.push({
            type: alertType,
            metric,
            value: analysisData[metric],
            threshold,
            severity: this.calculateSeverity(analysisData[metric], threshold),
            timestamp: new Date().toISOString()
          });
        }
      }

      if (alerts.length > 0) {
        await this.abena.sendAlerts(this.patientId, alerts);
      }

      return alerts;
    } catch (error) {
      await this.abena.logError(`${this.moduleName}-alert-generation`, error);
      return [];
    }
  }

  // Calculate alert severity
  calculateSeverity(value, threshold) {
    const ratio = value / threshold;
    if (ratio >= 1.5) return 'CRITICAL';
    if (ratio >= 1.2) return 'HIGH';
    if (ratio >= 1.0) return 'MEDIUM';
    return 'LOW';
  }

  // Get module status
  getModuleStatus() {
    return {
      moduleName: this.moduleName,
      moduleId: this.moduleId,
      version: this.version,
      isRunning: this.isRunning,
      patientId: this.patientId,
      userId: this.userId,
      lastAnalysis: this.lastAnalysis,
      config: this.config,
      timestamp: new Date().toISOString()
    };
  }

  // Log module activity
  async logActivity(activity, data = {}) {
    await this.abena.logActivity(`${this.moduleName}-${activity}`, {
      patientId: this.patientId,
      userId: this.userId,
      ...data,
      timestamp: new Date().toISOString()
    });
  }

  // Log module error
  async logError(errorType, error) {
    await this.abena.logError(`${this.moduleName}-${errorType}`, error);
  }
} 