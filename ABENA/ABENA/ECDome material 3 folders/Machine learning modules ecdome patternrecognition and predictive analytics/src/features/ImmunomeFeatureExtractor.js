import { BaseFeatureExtractor } from './BaseFeatureExtractor.js';

/**
 * IMMUNOME FEATURE EXTRACTOR
 * Extracts immune system function and response features
 */
class ImmunomeFeatureExtractor extends BaseFeatureExtractor {
  constructor() {
    super('immunome');
  }

  async extract(moduleData, ecdomeData, patientId) {
    return [
      this.normalizeFeature(this.validateData(moduleData.white_blood_cell_count), 4000, 11000),
      this.normalizeFeature(this.validateData(moduleData.t_cell_count), 500, 2000),
      this.normalizeFeature(this.validateData(moduleData.b_cell_count), 100, 500),
      this.normalizeFeature(this.validateData(moduleData.natural_killer_cells), 50, 300),
      this.normalizeFeature(this.validateData(moduleData.antibody_levels), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.complement_activity), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.cytokine_balance), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.immune_memory), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.autoimmune_markers), 0, 100),
      this.normalizeFeature(this.validateData(ecdomeData.immune_cb2_modulation), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.immune_surveillance), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.allergic_response), 0, 100)
    ];
  }
}

export { ImmunomeFeatureExtractor };
export default ImmunomeFeatureExtractor; 