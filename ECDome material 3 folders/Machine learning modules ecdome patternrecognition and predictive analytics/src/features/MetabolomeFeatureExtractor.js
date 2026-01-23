import { BaseFeatureExtractor } from './BaseFeatureExtractor.js';

/**
 * METABOLOME FEATURE EXTRACTOR
 * Extracts metabolic and energy production features
 */
class MetabolomeFeatureExtractor extends BaseFeatureExtractor {
  constructor() {
    super('metabolome');
  }

  async extract(moduleData, ecbomeData, patientId) {
    return [
      this.normalizeFeature(this.validateData(moduleData.glucose_levels), 70, 140),
      this.normalizeFeature(this.validateData(moduleData.insulin_sensitivity), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.lipid_metabolism_rate), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.mitochondrial_efficiency), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.metabolic_flexibility), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.ketone_production), 0, 5),
      this.normalizeFeature(this.validateData(moduleData.lactate_levels), 0, 4),
      this.normalizeFeature(this.validateData(moduleData.fatty_acid_oxidation), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.glycogen_stores), 0, 100),
      this.normalizeFeature(this.validateData(ecbomeData.cb1_metabolic_impact), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.atp_production_rate), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.basal_metabolic_rate), 1000, 3000)
    ];
  }
}

export { MetabolomeFeatureExtractor };
export default MetabolomeFeatureExtractor; 