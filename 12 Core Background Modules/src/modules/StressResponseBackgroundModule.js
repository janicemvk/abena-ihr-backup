import BaseBackgroundModule from '../core/BaseBackgroundModule.js';

/**
 * 9. STRESS RESPONSE MODULE
 * Stress-induced endocannabinoid depletion
 */
export default class StressResponseBackgroundModule extends BaseBackgroundModule {
  constructor(logger) {
    super('stress-response', {
      ecbomeCorrelationTypes: [
        'stress-induced-depletion',
        'hpa-axis-interaction',
        'cortisol-cannabinoid-relationship',
        'stress-recovery-patterns'
      ],
      alertThresholds: {
        chronicStress: 0.7,
        ecsDepletion: 0.6,
        hpaDisruption: 0.8
      }
    },
    logger);
  }

  setupMonitoringIntervals() {
    // Every 15 minutes: Stress biomarker sampling
    this.intervalIds.push(setInterval(async () => {
      await this.performStressBiomarkerSampling();
    }, this.config.samplingInterval));

    // Every hour: HPA axis analysis
    this.intervalIds.push(setInterval(async () => {
      await this.performHPAAxisAnalysis();
    }, 3600000));

    // Every 4 hours: Stress recovery assessment
    this.intervalIds.push(setInterval(async () => {
      await this.performStressRecoveryAssessment();
    }, this.config.deepAnalysisInterval));
  }

  async performAnalysis() {
    try {
      const stressData = await this.abena.getModuleData(
        this.patientId, 
        'stress-response'
      );

      const ecbomeCorrelations = await this.correlateWithECBome(stressData);

      const stressInducedECSDepletion = await this.analyzeStressInducedECSDepletion(
        stressData,
        ecbomeCorrelations
      );

      const stressResponse = this.assessStressResponse(stressData);

      const result = {
        timestamp: new Date().toISOString(),
        stressData,
        ecbomeCorrelations,
        stressInducedECSDepletion,
        stressResponse,
        chronicStress: this.detectChronicStress(stressData),
        recommendations: await this.generateStressManagementRecommendations(stressInducedECSDepletion),
        healthScore: this.calculateStressResponseScore(stressResponse)
      };

      this.lastAnalysis = result;
      return result;

    } catch (error) {
      await this.abena.logError('stress-response-analysis', error);
      throw error;
    }
  }

  async analyzeStressInducedECSDepletion(stressData, ecbomeCorrelations) {
    return {
      hpaAxisActivity: {
        cortisolLevels: stressData.cortisol_levels || 0,
        acthLevels: stressData.acth_levels || 0,
        crhActivity: stressData.crh_activity || 0,
        hpaDisruption: ecbomeCorrelations['hpa-axis-interaction']?.disruption_level || 0
      },
      endocannabinoidDepletion: {
        anandamideDepletion: ecbomeCorrelations['stress-induced-depletion']?.anandamide || 0,
        twoAGDepletion: ecbomeCorrelations['stress-induced-depletion']?.two_ag || 0,
        receptorDownregulation: ecbomeCorrelations['stress-induced-depletion']?.receptors || 0
      },
      stressBiomarkers: {
        heartRateVariability: stressData.hrv_metrics || {},
        bloodPressure: stressData.blood_pressure_variability || {},
        inflammatoryMarkers: stressData.stress_inflammatory_markers || {},
        neurotransmitters: stressData.stress_neurotransmitters || {}
      },
      recoveryCapacity: {
        resilience: stressData.stress_resilience_score || 0,
        recoveryTime: stressData.stress_recovery_time || 0,
        adaptability: stressData.stress_adaptation_capacity || 0
      }
    };
  }

  assessStressResponse(stressData) {
    return {
      acuteStressResponse: stressData.acute_stress_response || 0,
      chronicStressMarkers: stressData.chronic_stress_markers || 0,
      stressResilience: stressData.stress_resilience_score || 0,
      recoveryEfficiency: stressData.stress_recovery_efficiency || 0
    };
  }

  detectChronicStress(stressData) {
    const chronicStressMarkers = {
      elevatedCortisol: (stressData.cortisol_levels || 0) > 0.7,
      reducedHRV: (stressData.hrv_metrics?.rmssd || 0) < 0.3,
      persistentInflammation: (stressData.stress_inflammatory_markers?.crp || 0) > 0.6,
      poorRecovery: (stressData.stress_recovery_time || 0) > 0.8
    };

    const chronicStressScore = Object.values(chronicStressMarkers).filter(Boolean).length / 4;
    
    return {
      present: chronicStressScore > 0.5,
      severity: chronicStressScore > 0.75 ? 'HIGH' : chronicStressScore > 0.5 ? 'MEDIUM' : 'LOW',
      markers: chronicStressMarkers,
      score: chronicStressScore
    };
  }

  calculateStressResponseScore(stressResponse) {
    return (
      (1 - stressResponse.acuteStressResponse) * 0.2 +
      (1 - stressResponse.chronicStressMarkers) * 0.3 +
      stressResponse.stressResilience * 0.3 +
      stressResponse.recoveryEfficiency * 0.2
    );
  }

  async generateStressManagementRecommendations(stressInducedECSDepletion) {
    const recommendations = [];

    // HPA axis recommendations
    if (stressInducedECSDepletion.hpaAxisActivity.hpaDisruption > 0.6) {
      recommendations.push({
        category: 'hpa-axis-support',
        action: 'Implement HPA axis restoration protocol',
        rationale: 'Restore stress response system and ECS balance',
        priority: 'HIGH'
      });
    }

    // ECS depletion recommendations
    if (stressInducedECSDepletion.endocannabinoidDepletion.anandamideDepletion > 0.5) {
      recommendations.push({
        category: 'ecs-restoration',
        action: 'Support endocannabinoid synthesis and function',
        rationale: 'Replenish stress-depleted endocannabinoids',
        priority: 'HIGH'
      });
    }

    // Recovery capacity recommendations
    if (stressInducedECSDepletion.recoveryCapacity.resilience < 0.4) {
      recommendations.push({
        category: 'stress-resilience',
        action: 'Implement stress resilience training',
        rationale: 'Improve stress adaptation and recovery capacity',
        priority: 'MEDIUM'
      });
    }

    return recommendations;
  }

  async performStressBiomarkerSampling() {
    const stressBiomarkers = await this.abena.collectBiomarkers(
      this.patientId,
      ['cortisol', 'adrenaline', 'noradrenaline', 'hrv']
    );
    
    await this.abena.storeModuleData(this.patientId, 'stress-biomarkers', stressBiomarkers);
    await this.logActivity('stress-biomarker-sampling-completed', { biomarkers: stressBiomarkers });
  }

  async performHPAAxisAnalysis() {
    const hpaData = await this.abena.analyzeHPAAxis(this.patientId);
    await this.abena.storeModuleData(this.patientId, 'hpa-axis', hpaData);
    await this.logActivity('hpa-axis-analysis-completed', { analysis: hpaData });
  }

  async performStressRecoveryAssessment() {
    const recoveryData = await this.abena.assessStressRecovery(this.patientId);
    await this.abena.storeModuleData(this.patientId, 'stress-recovery', recoveryData);
    await this.logActivity('stress-recovery-assessment-completed', { assessment: recoveryData });
  }
} 