import { BaseFeatureExtractor } from './BaseFeatureExtractor.js';

/**
 * CHRONOBIOME FEATURE EXTRACTOR
 * Extracts circadian rhythm and temporal biological features
 */
class ChronobiomeFeatureExtractor extends BaseFeatureExtractor {
  constructor() {
    super('chronobiome');
  }

  async extract(moduleData, ecdomeData, patientId) {
    return [
      this.normalizeFeature(this.validateData(moduleData.circadian_rhythm_strength), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.sleep_quality_score), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.melatonin_levels), 0, 20),
      this.normalizeFeature(this.validateData(moduleData.cortisol_awakening_response), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.body_temperature_rhythm), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.heart_rate_variability), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.activity_rest_cycles), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.feeding_timing_regularity), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.light_exposure_patterns), 0, 100),
      this.normalizeFeature(this.validateData(ecdomeData.circadian_ecs_modulation), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.chronotype_alignment), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.seasonal_adaptation), 0, 100)
    ];
  }
}

export { ChronobiomeFeatureExtractor };
export default ChronobiomeFeatureExtractor; 