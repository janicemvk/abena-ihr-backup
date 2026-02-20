import { BaseFeatureExtractor } from './BaseFeatureExtractor.js';

/**
 * NUTRIOME FEATURE EXTRACTOR
 * Extracts nutritional status and metabolic efficiency features
 */
class NutriomeFeatureExtractor extends BaseFeatureExtractor {
  constructor() {
    super('nutriome');
  }

  async extract(moduleData, ecdomeData, patientId) {
    return [
      this.normalizeFeature(this.validateData(moduleData.macronutrient_balance), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.micronutrient_sufficiency), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.vitamin_d_levels), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.omega3_fatty_acids), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.antioxidant_status), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.protein_synthesis_rate), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.nutrient_absorption_efficiency), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.food_sensitivity_markers), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.metabolic_nutrient_utilization), 0, 100),
      this.normalizeFeature(this.validateData(ecdomeData.nutritional_ecs_impact), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.hydration_status), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.mineral_balance), 0, 100)
    ];
  }
}

export { NutriomeFeatureExtractor };
export default NutriomeFeatureExtractor; 