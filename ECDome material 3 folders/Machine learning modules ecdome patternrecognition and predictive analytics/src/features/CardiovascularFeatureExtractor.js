import { BaseFeatureExtractor } from './BaseFeatureExtractor.js';

/**
 * CARDIOVASCULAR FEATURE EXTRACTOR
 * Extracts cardiovascular system health and function features
 */
class CardiovascularFeatureExtractor extends BaseFeatureExtractor {
  constructor() {
    super('cardiovascular');
  }

  async extract(moduleData, ecbomeData, patientId) {
    return [
      this.normalizeFeature(this.validateData(moduleData.heart_rate_variability), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.blood_pressure_control), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.arterial_stiffness), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.endothelial_function), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.cardiac_output_efficiency), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.vascular_health_markers), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.lipid_profile_optimization), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.clotting_factor_balance), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.exercise_capacity), 0, 100),
      this.normalizeFeature(this.validateData(ecbomeData.cardiovascular_ecs_influence), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.cardiac_rhythm_stability), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.peripheral_circulation), 0, 100)
    ];
  }
}

export { CardiovascularFeatureExtractor };
export default CardiovascularFeatureExtractor; 