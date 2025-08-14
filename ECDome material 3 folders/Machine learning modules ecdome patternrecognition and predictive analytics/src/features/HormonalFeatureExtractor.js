import { BaseFeatureExtractor } from './BaseFeatureExtractor.js';

/**
 * HORMONAL FEATURE EXTRACTOR
 * Extracts hormonal system and endocrine function features
 */
class HormonalFeatureExtractor extends BaseFeatureExtractor {
  constructor() {
    super('hormonal');
  }

  async extract(moduleData, ecdomeData, patientId) {
    return [
      this.normalizeFeature(this.validateData(moduleData.thyroid_function), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.adrenal_function), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.sex_hormone_balance), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.insulin_sensitivity), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.growth_hormone_levels), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.parathyroid_function), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.pineal_gland_function), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.hormonal_rhythm_synchronization), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.reproductive_health_markers), 0, 100),
      this.normalizeFeature(this.validateData(ecdomeData.hormonal_ecs_regulation), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.metabolic_hormone_integration), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.stress_hormone_balance), 0, 100)
    ];
  }
}

export { HormonalFeatureExtractor };
export default HormonalFeatureExtractor; 