import { BaseFeatureExtractor } from './BaseFeatureExtractor.js';

/**
 * STRESS RESPONSE FEATURE EXTRACTOR
 * Extracts stress response system and adaptation features
 */
class StressResponseFeatureExtractor extends BaseFeatureExtractor {
  constructor() {
    super('stressResponse');
  }

  async extract(moduleData, ecdomeData, patientId) {
    return [
      this.normalizeFeature(this.validateData(moduleData.cortisol_levels), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.hpa_axis_function), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.sympathetic_nervous_activity), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.parasympathetic_tone), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.stress_adaptation_capacity), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.resilience_markers), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.psychological_stress_indicators), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.physical_stress_tolerance), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.recovery_time_metrics), 0, 100),
      this.normalizeFeature(this.validateData(ecdomeData.stress_ecs_modulation), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.allostatic_load), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.stress_related_inflammation), 0, 100)
    ];
  }
}

export { StressResponseFeatureExtractor };
export default StressResponseFeatureExtractor; 