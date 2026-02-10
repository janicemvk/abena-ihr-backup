import BaseBackgroundModule from '../core/BaseBackgroundModule.js';
import { abenaLogger } from "../utils/logger.js"; // import logger

/**
 * 10. CARDIOVASCULAR MODULE
 * Cardiovascular cannabinoid receptor impact
 */
export default class CardiovascularBackgroundModule extends BaseBackgroundModule {
  constructor(logger) {
    super('cardiovascular', {
      ecbomeCorrelationTypes: [
        'cardiovascular-receptors',
        'cardiac-function-modulation',
        'vascular-tone-regulation',
        'blood-pressure-control'
      ],
      alertThresholds: {
        cardiacRisk: 0.7,
        arrhythmia: 0.8,
        hypertension: 0.6
      }
    },
    logger  // <-- pass the logger to BaseBackgroundModule
  );
  }

  setupMonitoringIntervals() {
    // Every 10 minutes: Cardiovascular monitoring
    this.intervalIds.push(setInterval(async () => {
      await this.performCardiovascularMonitoring();
    }, 600000));

    // Every 30 minutes: Heart rate variability analysis
    this.intervalIds.push(setInterval(async () => {
      await this.performHRVAnalysis();
    }, this.config.analysisInterval));

    // Every 2 hours: Complete cardiovascular assessment
    this.intervalIds.push(setInterval(async () => {
      await this.performCompleteCardiovascularAssessment();
    }, 7200000));
  }

  async performAnalysis() {
    try {
      const cardiovascularData = await this.abena.getModuleData(
        this.patientId, 
        'cardiovascular'
      );

      const ecbomeCorrelations = await this.correlateWithECBome(cardiovascularData);

      const cardiovascularCannabinoidImpact = await this.analyzeCardiovascularCannabinoidImpact(
        cardiovascularData,
        ecbomeCorrelations
      );

      const cardiovascularHealth = this.assessCardiovascularHealth(cardiovascularData);

      const result = {
        timestamp: new Date().toISOString(),
        cardiovascularData,
        ecbomeCorrelations,
        cardiovascularCannabinoidImpact,
        cardiovascularHealth,
        riskAssessment: this.assessCardiovascularRisk(cardiovascularData),
        recommendations: await this.generateCardiovascularRecommendations(cardiovascularCannabinoidImpact),
        healthScore: this.calculateCardiovascularHealthScore(cardiovascularHealth)
      };

      this.lastAnalysis = result;
      return result;

    } catch (error) {
      await this.abena.logError('cardiovascular-analysis', error);
      throw error;
    }
  }

  async analyzeCardiovascularCannabinoidImpact(cardiovascularData, ecbomeCorrelations) {
    return {
      cardiacFunction: {
        heartRate: cardiovascularData.heart_rate || 0,
        heartRateVariability: cardiovascularData.hrv_metrics || {},
        cardiacOutput: cardiovascularData.cardiac_output || 0,
        cb1ReceptorActivity: ecbomeCorrelations['cardiac-function-modulation']?.cb1_activity || 0
      },
      vascularFunction: {
        bloodPressure: cardiovascularData.blood_pressure || {},
        arterialStiffness: cardiovascularData.arterial_stiffness || 0,
        endothelialFunction: cardiovascularData.endothelial_function || 0,
        vascularTone: ecbomeCorrelations['vascular-tone-regulation']?.tone_modulation || 0
      },
      cardioprotection: {
        antiArrhythmic: ecbomeCorrelations['cardiovascular-receptors']?.anti_arrhythmic || 0,
        cardioprotectiveEffects: ecbomeCorrelations['cardiovascular-receptors']?.cardioprotection || 0,
        ischemiaProtection: ecbomeCorrelations['cardiovascular-receptors']?.ischemia_protection || 0
      }
    };
  }

  assessCardiovascularHealth(cardiovascularData) {
    return {
      overallCardiacHealth: cardiovascularData.overall_cardiac_health || 0,
      heartRateVariability: cardiovascularData.hrv_score || 0,
      bloodPressureControl: cardiovascularData.blood_pressure_control || 0,
      vascularHealth: cardiovascularData.vascular_health_score || 0
    };
  }

  assessCardiovascularRisk(cardiovascularData) {
    const riskFactors = {
      hypertension: (cardiovascularData.blood_pressure?.systolic || 0) > 140,
      tachycardia: (cardiovascularData.heart_rate || 0) > 100,
      reducedHRV: (cardiovascularData.hrv_metrics?.rmssd || 0) < 0.3,
      arterialStiffness: (cardiovascularData.arterial_stiffness || 0) > 0.7
    };

    const riskScore = Object.values(riskFactors).filter(Boolean).length / 4;
    
    return {
      overallRisk: riskScore > 0.5 ? 'HIGH' : riskScore > 0.3 ? 'MEDIUM' : 'LOW',
      riskFactors,
      score: riskScore
    };
  }

  calculateCardiovascularHealthScore(cardiovascularHealth) {
    return (
      cardiovascularHealth.overallCardiacHealth * 0.3 +
      cardiovascularHealth.heartRateVariability * 0.3 +
      cardiovascularHealth.bloodPressureControl * 0.2 +
      cardiovascularHealth.vascularHealth * 0.2
    );
  }

  async generateCardiovascularRecommendations(cardiovascularCannabinoidImpact) {
    const recommendations = [];

    // Cardiac function recommendations
    if (cardiovascularCannabinoidImpact.cardiacFunction.cb1ReceptorActivity < 0.5) {
      recommendations.push({
        category: 'cardiac-function',
        action: 'Support CB1 receptor function in cardiac tissue',
        rationale: 'Improve cardiac function and rhythm stability',
        priority: 'HIGH'
      });
    }

    // Vascular function recommendations
    if (cardiovascularCannabinoidImpact.vascularFunction.endothelialFunction < 0.4) {
      recommendations.push({
        category: 'vascular-function',
        action: 'Implement endothelial function support protocol',
        rationale: 'Improve vascular health and blood flow',
        priority: 'MEDIUM'
      });
    }

    // Cardioprotection recommendations
    if (cardiovascularCannabinoidImpact.cardioprotection.cardioprotectiveEffects < 0.6) {
      recommendations.push({
        category: 'cardioprotection',
        action: 'Enhance cardioprotective mechanisms',
        rationale: 'Increase cardiac resilience and protection',
        priority: 'MEDIUM'
      });
    }

    return recommendations;
  }

  async performCardiovascularMonitoring() {
    const cvMonitoring = await this.abena.monitorCardiovascular(this.patientId);
    await this.abena.storeModuleData(this.patientId, 'cv-monitoring', cvMonitoring);
    await this.logActivity('cardiovascular-monitoring-completed', { monitoring: cvMonitoring });
  }

  async performHRVAnalysis() {
    const hrvData = await this.abena.analyzeHRV(this.patientId);
    await this.abena.storeModuleData(this.patientId, 'hrv-analysis', hrvData);
    await this.logActivity('hrv-analysis-completed', { analysis: hrvData });
  }

  async performCompleteCardiovascularAssessment() {
    const cvAssessment = await this.abena.performCompleteCardiovascularAssessment(this.patientId);
    await this.abena.storeModuleData(this.patientId, 'cv-complete', cvAssessment);
    await this.logActivity('complete-cardiovascular-assessment-completed', { assessment: cvAssessment });
  }
} 