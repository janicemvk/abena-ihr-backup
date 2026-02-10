import AbenaSDK from '@abena/sdk';

// Import all 12 background modules
import MetabolomeBackgroundModule from '../modules/MetabolomeBackgroundModule.js';
import MicrobiomeBackgroundModule from '../modules/MicrobiomeBackgroundModule.js';
import InflammatomeBackgroundModule from '../modules/InflammatomeBackgroundModule.js';
import ImmunomeBackgroundModule from '../modules/ImmunomeBackgroundModule.js';
import ChronobiomeBackgroundModule from '../modules/ChronobiomeBackgroundModule.js';
import NutriomeBackgroundModule from '../modules/NutriomeBackgroundModule.js';
import ToxicomeBackgroundModule from '../modules/ToxicomeBackgroundModule.js';
import PharmacomedBackgroundModule from '../modules/PharmacomedBackgroundModule.js';
import StressResponseBackgroundModule from '../modules/StressResponseBackgroundModule.js';
import CardiovascularBackgroundModule from '../modules/CardiovascularBackgroundModule.js';
import NeurologicalBackgroundModule from '../modules/NeurologicalBackgroundModule.js';
import HormonalBackgroundModule from '../modules/HormonalBackgroundModule.js';

/**
 * MASTER MODULE ORCHESTRATOR
 * Manages all 12 background modules and coordinates their activities
 */
export default class BackgroundModuleOrchestrator {
  constructor() {
    this.modules = {
      metabolome: new MetabolomeBackgroundModule(),
      microbiome: new MicrobiomeBackgroundModule(),
      inflammatome: new InflammatomeBackgroundModule(),
      immunome: new ImmunomeBackgroundModule(),
      chronobiome: new ChronobiomeBackgroundModule(),
      nutriome: new NutriomeBackgroundModule(),
      toxicome: new ToxicomeBackgroundModule(),
      pharmacome: new PharmacomedBackgroundModule(),
      stressResponse: new StressResponseBackgroundModule(),
      cardiovascular: new CardiovascularBackgroundModule(),
      neurological: new NeurologicalBackgroundModule(),
      hormonal: new HormonalBackgroundModule()
    };

    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003',
      ecbomeServiceUrl: 'http://localhost:8004',
      correlationEngineUrl: 'http://localhost:8005'
    });

    this.isOrchestrating = false;
    this.orchestrationInterval = null;
  }

  /**
   * Start all 12 background modules for a patient
   */
  async startAllBackgroundModules(patientId, userId) {
    try {
      if (this.isOrchestrating) {
        console.log('Orchestrator already running for patient:', patientId);
        return;
      }
      
      this.isOrchestrating = true;
      this.patientId = patientId;
      this.userId = userId;

      console.log(`Starting all 12 background modules for patient ${patientId}...`);

      // Start all modules in parallel
      const startPromises = Object.entries(this.modules).map(async ([moduleName, module]) => {
        try {
          await module.startBackgroundMonitoring(patientId, userId);
          console.log(`✅ ${moduleName} module started successfully`);
          return { moduleName, success: true };
        } catch (error) {
          console.error(`❌ Failed to start ${moduleName} module:`, error);
          return { moduleName, success: false, error: error.message };
        }
      });

      const results = await Promise.allSettled(startPromises);

      // Set up orchestrator-level coordination
      this.setupOrchestration();

      await this.abena.logActivity('all-background-modules-started', {
        patientId, userId, 
        modulesCount: Object.keys(this.modules).length,
        results: results.map(r => r.value || r.reason),
        timestamp: new Date().toISOString()
      });

      console.log('🎉 All background modules started successfully!');

      return {
        success: true,
        message: `All 12 background modules started for patient ${patientId}`,
        modules: Object.keys(this.modules),
        results: results.map(r => r.value || r.reason),
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      console.error('Error starting background modules:', error);
      await this.abena.logError('orchestrator-start-all', error);
      throw error;
    }
  }

  /**
   * Stop all background modules
   */
  async stopAllBackgroundModules() {
    console.log('Stopping all background modules...');
    
    this.isOrchestrating = false;
    
    // Stop all modules
    Object.entries(this.modules).forEach(([moduleName, module]) => {
      try {
        module.stopBackgroundMonitoring();
        console.log(`✅ ${moduleName} module stopped successfully`);
      } catch (error) {
        console.error(`❌ Error stopping ${moduleName} module:`, error);
      }
    });
    
    // Clear orchestrator interval
    if (this.orchestrationInterval) {
      clearInterval(this.orchestrationInterval);
      this.orchestrationInterval = null;
    }

    await this.abena.logActivity('all-background-modules-stopped', {
      patientId: this.patientId,
      timestamp: new Date().toISOString()
    });

    console.log('🛑 All background modules stopped');
  }

  /**
   * Get comprehensive analysis from all modules
   */
  async getComprehensiveAnalysis() {
    try {
      console.log('Generating comprehensive analysis from all modules...');
      
      const moduleAnalyses = {};
      
      // Get analysis from each module in parallel
      const analysisPromises = Object.entries(this.modules).map(async ([moduleName, module]) => {
        try {
          const analysis = await module.performAnalysis();
          return { moduleName, analysis, success: true };
        } catch (error) {
          console.error(`Error in ${moduleName} analysis:`, error);
          return { 
            moduleName, 
            analysis: { 
              error: error.message, 
              timestamp: new Date().toISOString() 
            }, 
            success: false 
          };
        }
      });

      const results = await Promise.allSettled(analysisPromises);
      
      // Process results
      results.forEach(result => {
        if (result.status === 'fulfilled') {
          const { moduleName, analysis, success } = result.value;
          moduleAnalyses[moduleName] = analysis;
          if (success) {
            console.log(`✅ ${moduleName} analysis completed`);
          } else {
            console.warn(`⚠️ ${moduleName} analysis failed`);
          }
        } else {
          console.error('Analysis promise rejected:', result.reason);
        }
      });

      // Generate cross-module insights
      const crossModuleInsights = await this.generateCrossModuleInsights(moduleAnalyses);

      // Calculate overall health score
      const overallHealthScore = this.calculateOverallHealthScore(moduleAnalyses);

      const comprehensiveAnalysis = {
        moduleAnalyses,
        crossModuleInsights,
        overallHealthScore,
        timestamp: new Date().toISOString(),
        patientId: this.patientId,
        userId: this.userId
      };

      console.log(`🔍 Comprehensive analysis completed. Overall health score: ${overallHealthScore.toFixed(2)}`);

      return comprehensiveAnalysis;

    } catch (error) {
      console.error('Error generating comprehensive analysis:', error);
      await this.abena.logError('comprehensive-analysis', error);
      throw error;
    }
  }

  /**
   * Setup orchestration coordination between modules
   */
  setupOrchestration() {
    console.log('Setting up cross-module orchestration...');
    
    // Every hour: Cross-module coordination
    this.orchestrationInterval = setInterval(async () => {
      await this.performCrossModuleCoordination();
    }, 3600000); // 1 hour

    console.log('✅ Cross-module orchestration setup complete');
  }

  /**
   * Cross-module coordination and pattern recognition
   */
  async performCrossModuleCoordination() {
    try {
      console.log('Performing cross-module coordination...');
      
      const comprehensiveAnalysis = await this.getComprehensiveAnalysis();
      
      // Store cross-module patterns
      await this.abena.storeModuleData(
        this.patientId, 
        'cross-module-coordination', 
        comprehensiveAnalysis.crossModuleInsights
      );

      // Generate alerts if critical patterns detected
      const criticalPatterns = this.identifyCriticalPatterns(comprehensiveAnalysis);
      if (criticalPatterns.length > 0) {
        await this.generateCriticalAlerts(criticalPatterns);
        console.log(`⚠️ ${criticalPatterns.length} critical patterns detected`);
      }

      console.log('✅ Cross-module coordination completed');

    } catch (error) {
      console.error('Error in cross-module coordination:', error);
      await this.abena.logError('cross-module-coordination', error);
    }
  }

  /**
   * Generate insights across all modules
   */
  async generateCrossModuleInsights(moduleAnalyses) {
    console.log('Generating cross-module insights...');
    
    return {
      systemicPatterns: await this.identifySystemicPatterns(moduleAnalyses),
      ecbomeIntegration: await this.analyzeECBomeIntegration(moduleAnalyses),
      predictiveIndicators: await this.identifyPredictiveIndicators(moduleAnalyses),
      interventionOpportunities: await this.identifyInterventionOpportunities(moduleAnalyses),
      moduleInteractions: this.analyzeModuleInteractions(moduleAnalyses),
      emergentPatterns: this.identifyEmergentPatterns(moduleAnalyses)
    };
  }

  /**
   * Calculate overall health score from all modules
   */
  calculateOverallHealthScore(moduleAnalyses) {
    let totalScore = 0;
    let validModules = 0;

    Object.entries(moduleAnalyses).forEach(([moduleName, analysis]) => {
      if (!analysis.error && analysis.healthScore !== undefined) {
        totalScore += analysis.healthScore;
        validModules++;
      }
    });

    return validModules > 0 ? totalScore / validModules : 0;
  }

  /**
   * Identify systemic patterns across modules
   */
  async identifySystemicPatterns(moduleAnalyses) {
    const patterns = [];
    
    // Pattern 1: Inflammatory cascade across modules
    const inflammatoryModules = ['inflammatome', 'immunome', 'cardiovascular', 'neurological'];
    let inflammatoryScore = 0;
    let inflammatoryCount = 0;

    inflammatoryModules.forEach(moduleName => {
      const analysis = moduleAnalyses[moduleName];
      if (analysis && !analysis.error && analysis.healthScore !== undefined) {
        inflammatoryScore += analysis.healthScore;
        inflammatoryCount++;
      }
    });

    if (inflammatoryCount > 0) {
      const avgInflammatoryScore = inflammatoryScore / inflammatoryCount;
      if (avgInflammatoryScore < 0.5) {
        patterns.push({
          type: 'systemic-inflammation',
          severity: 'HIGH',
          description: 'Systemic inflammatory pattern detected across multiple modules',
          affectedModules: inflammatoryModules,
          score: avgInflammatoryScore
        });
      }
    }

    // Pattern 2: Metabolic dysfunction cascade
    const metabolicModules = ['metabolome', 'hormonal', 'cardiovascular', 'nutriome'];
    let metabolicScore = 0;
    let metabolicCount = 0;

    metabolicModules.forEach(moduleName => {
      const analysis = moduleAnalyses[moduleName];
      if (analysis && !analysis.error && analysis.healthScore !== undefined) {
        metabolicScore += analysis.healthScore;
        metabolicCount++;
      }
    });

    if (metabolicCount > 0) {
      const avgMetabolicScore = metabolicScore / metabolicCount;
      if (avgMetabolicScore < 0.6) {
        patterns.push({
          type: 'metabolic-dysfunction',
          severity: avgMetabolicScore < 0.4 ? 'HIGH' : 'MEDIUM',
          description: 'Metabolic dysfunction pattern detected across multiple modules',
          affectedModules: metabolicModules,
          score: avgMetabolicScore
        });
      }
    }

    return patterns;
  }

  /**
   * Analyze eCBome integration across modules
   */
  async analyzeECBomeIntegration(moduleAnalyses) {
    const ecbomeAnalysis = {
      overallIntegration: 0,
      moduleECBomeScores: {},
      correlationStrength: 0,
      systemicECSHealth: 0
    };

    let totalECBomeScore = 0;
    let validECBomeModules = 0;

    Object.entries(moduleAnalyses).forEach(([moduleName, analysis]) => {
      if (analysis && !analysis.error && analysis.ecbomeCorrelations) {
        const ecbomeTypes = Object.keys(analysis.ecbomeCorrelations);
        if (ecbomeTypes.length > 0) {
          // Calculate module-specific eCBome score
          let moduleECBomeScore = 0;
          ecbomeTypes.forEach(type => {
            const correlation = analysis.ecbomeCorrelations[type];
            if (typeof correlation === 'object' && correlation !== null) {
              const correlationValues = Object.values(correlation).filter(v => typeof v === 'number');
              if (correlationValues.length > 0) {
                moduleECBomeScore += correlationValues.reduce((sum, val) => sum + val, 0) / correlationValues.length;
              }
            }
          });
          
          moduleECBomeScore = moduleECBomeScore / ecbomeTypes.length;
          ecbomeAnalysis.moduleECBomeScores[moduleName] = moduleECBomeScore;
          totalECBomeScore += moduleECBomeScore;
          validECBomeModules++;
        }
      }
    });

    if (validECBomeModules > 0) {
      ecbomeAnalysis.overallIntegration = totalECBomeScore / validECBomeModules;
      ecbomeAnalysis.correlationStrength = validECBomeModules / Object.keys(this.modules).length;
      ecbomeAnalysis.systemicECSHealth = ecbomeAnalysis.overallIntegration * ecbomeAnalysis.correlationStrength;
    }

    return ecbomeAnalysis;
  }

  /**
   * Identify predictive indicators
   */
  async identifyPredictiveIndicators(moduleAnalyses) {
    const indicators = [];

    // Stress-inflammation-metabolic cascade prediction
    const stressScore = moduleAnalyses.stressResponse?.healthScore || 0;
    const inflammationScore = moduleAnalyses.inflammatome?.healthScore || 0;
    const metabolicScore = moduleAnalyses.metabolome?.healthScore || 0;

    if (stressScore < 0.5 && inflammationScore < 0.6) {
      indicators.push({
        type: 'metabolic-dysfunction-risk',
        probability: 0.7,
        timeframe: '2-4 weeks',
        description: 'High stress and inflammation predict metabolic dysfunction',
        preventiveActions: ['stress management', 'anti-inflammatory interventions']
      });
    }

    // Microbiome-immune-neurological prediction
    const microbiomeScore = moduleAnalyses.microbiome?.healthScore || 0;
    const immuneScore = moduleAnalyses.immunome?.healthScore || 0;
    const neurologicalScore = moduleAnalyses.neurological?.healthScore || 0;

    if (microbiomeScore < 0.4 && immuneScore < 0.5) {
      indicators.push({
        type: 'cognitive-decline-risk',
        probability: 0.6,
        timeframe: '1-3 months',
        description: 'Microbiome dysbiosis and immune dysfunction predict cognitive decline',
        preventiveActions: ['microbiome restoration', 'immune system support']
      });
    }

    return indicators;
  }

  /**
   * Identify intervention opportunities
   */
  async identifyInterventionOpportunities(moduleAnalyses) {
    const opportunities = [];

    // High-impact intervention opportunities
    Object.entries(moduleAnalyses).forEach(([moduleName, analysis]) => {
      if (analysis && !analysis.error && analysis.recommendations) {
        const highPriorityRecommendations = analysis.recommendations.filter(
          rec => rec.priority === 'HIGH'
        );

        if (highPriorityRecommendations.length > 0) {
          opportunities.push({
            moduleName,
            interventionType: 'high-priority',
            recommendations: highPriorityRecommendations,
            expectedImpact: 'HIGH',
            urgency: 'IMMEDIATE'
          });
        }
      }
    });

    // Synergistic intervention opportunities
    const metabolicModules = ['metabolome', 'nutriome', 'hormonal'];
    const metabolicRecommendations = [];
    
    metabolicModules.forEach(moduleName => {
      const analysis = moduleAnalyses[moduleName];
      if (analysis && !analysis.error && analysis.recommendations) {
        metabolicRecommendations.push(...analysis.recommendations);
      }
    });

    if (metabolicRecommendations.length >= 2) {
      opportunities.push({
        moduleName: 'metabolic-synergy',
        interventionType: 'synergistic',
        recommendations: metabolicRecommendations,
        expectedImpact: 'VERY HIGH',
        urgency: 'HIGH'
      });
    }

    return opportunities;
  }

  /**
   * Analyze interactions between modules
   */
  analyzeModuleInteractions(moduleAnalyses) {
    const interactions = [];

    // Strong interaction pairs
    const interactionPairs = [
      ['stressResponse', 'hormonal'],
      ['microbiome', 'immunome'],
      ['metabolome', 'cardiovascular'],
      ['neurological', 'chronobiome'],
      ['inflammatome', 'immunome']
    ];

    interactionPairs.forEach(([module1, module2]) => {
      const analysis1 = moduleAnalyses[module1];
      const analysis2 = moduleAnalyses[module2];

      if (analysis1 && analysis2 && !analysis1.error && !analysis2.error) {
        const scoreDifference = Math.abs(analysis1.healthScore - analysis2.healthScore);
        
        if (scoreDifference > 0.3) {
          interactions.push({
            modules: [module1, module2],
            type: 'imbalanced-interaction',
            description: `Significant health score difference between ${module1} and ${module2}`,
            impact: scoreDifference > 0.5 ? 'HIGH' : 'MEDIUM',
            recommendation: `Address imbalance between ${module1} and ${module2} systems`
          });
        }
      }
    });

    return interactions;
  }

  /**
   * Identify emergent patterns
   */
  identifyEmergentPatterns(moduleAnalyses) {
    const patterns = [];

    // Calculate overall system coherence
    const healthScores = Object.values(moduleAnalyses)
      .filter(analysis => analysis && !analysis.error && analysis.healthScore !== undefined)
      .map(analysis => analysis.healthScore);

    if (healthScores.length > 0) {
      const avgScore = healthScores.reduce((sum, score) => sum + score, 0) / healthScores.length;
      const variance = healthScores.reduce((sum, score) => sum + Math.pow(score - avgScore, 2), 0) / healthScores.length;
      const coherence = 1 - variance;

      patterns.push({
        type: 'system-coherence',
        score: coherence,
        description: coherence > 0.7 ? 'High system coherence' : coherence > 0.5 ? 'Moderate system coherence' : 'Low system coherence',
        implications: coherence < 0.5 ? 'System dysregulation detected' : 'System functioning within normal parameters'
      });
    }

    return patterns;
  }

  /**
   * Identify critical patterns requiring immediate attention
   */
  identifyCriticalPatterns(comprehensiveAnalysis) {
    const criticalPatterns = [];

    // Overall health score critically low
    if (comprehensiveAnalysis.overallHealthScore < 0.3) {
      criticalPatterns.push({
        type: 'critical-health-decline',
        severity: 'CRITICAL',
        description: 'Overall health score critically low across multiple systems',
        score: comprehensiveAnalysis.overallHealthScore
      });
    }

    // Multiple high-priority alerts
    const highPriorityAlerts = Object.values(comprehensiveAnalysis.moduleAnalyses)
      .filter(analysis => analysis && !analysis.error && analysis.alerts)
      .reduce((total, analysis) => total + analysis.alerts.filter(alert => alert.severity === 'HIGH').length, 0);

    if (highPriorityAlerts >= 3) {
      criticalPatterns.push({
        type: 'multiple-high-priority-alerts',
        severity: 'CRITICAL',
        description: `${highPriorityAlerts} high-priority alerts detected across modules`,
        count: highPriorityAlerts
      });
    }

    // Systemic patterns with high severity
    const systemicPatterns = comprehensiveAnalysis.crossModuleInsights.systemicPatterns || [];
    systemicPatterns.forEach(pattern => {
      if (pattern.severity === 'HIGH') {
        criticalPatterns.push({
          type: 'systemic-pattern',
          severity: 'CRITICAL',
          description: pattern.description,
          pattern: pattern.type,
          affectedModules: pattern.affectedModules
        });
      }
    });

    return criticalPatterns;
  }

  /**
   * Generate critical alerts
   */
  async generateCriticalAlerts(criticalPatterns) {
    const alerts = criticalPatterns.map(pattern => ({
      type: 'CRITICAL_SYSTEM_ALERT',
      severity: 'CRITICAL',
      timestamp: new Date().toISOString(),
      patientId: this.patientId,
      pattern: pattern.type,
      description: pattern.description,
      requiresImmediateAttention: true
    }));

    // Send alerts through Abena SDK
    await this.abena.sendAlerts(this.patientId, alerts);
    
    console.log(`🚨 ${alerts.length} critical alerts generated and sent`);
  }

  /**
   * Get orchestrator status
   */
  getOrchestratorStatus() {
    return {
      isOrchestrating: this.isOrchestrating,
      patientId: this.patientId,
      userId: this.userId,
      moduleCount: Object.keys(this.modules).length,
      modules: Object.keys(this.modules),
      moduleStatuses: Object.fromEntries(
        Object.entries(this.modules).map(([name, module]) => [
          name, 
          {
            isRunning: module.isRunning,
            lastAnalysis: module.lastAnalysis?.timestamp || null
          }
        ])
      ),
      timestamp: new Date().toISOString()
    };
  }
} 