import { BaseFeatureExtractor } from './BaseFeatureExtractor.js';

/**
 * INFLAMMATOME FEATURE EXTRACTOR
 * Extracts inflammatory response and immune signaling features
 */
class InflammatomeFeatureExtractor extends BaseFeatureExtractor {
  constructor() {
    super('inflammatome');
  }

  async extract(moduleData, ecbomeData, patientId) {
    return [
      this.normalizeFeature(this.validateData(moduleData.c_reactive_protein), 0, 10),
      this.normalizeFeature(this.validateData(moduleData.interleukin_6), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.tnf_alpha), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.il1_beta), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.nf_kappa_b_activity), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.prostaglandin_levels), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.nitric_oxide), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.oxidative_stress), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.antioxidant_capacity), 0, 100),
      this.normalizeFeature(this.validateData(ecbomeData.cb2_anti_inflammatory), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.tissue_healing_rate), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.inflammation_resolution), 0, 100)
    ];
  }
}

export { InflammatomeFeatureExtractor };
export default InflammatomeFeatureExtractor; 