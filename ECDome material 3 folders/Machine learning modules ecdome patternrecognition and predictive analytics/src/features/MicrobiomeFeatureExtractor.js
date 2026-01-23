import { BaseFeatureExtractor } from './BaseFeatureExtractor.js';

/**
 * MICROBIOME FEATURE EXTRACTOR
 * Extracts gut microbiome and digestive health features
 */
class MicrobiomeFeatureExtractor extends BaseFeatureExtractor {
  constructor() {
    super('microbiome');
  }

  async extract(moduleData, ecbomeData, patientId) {
    return [
      this.normalizeFeature(this.validateData(moduleData.shannon_diversity), 0, 4),
      this.normalizeFeature(this.validateData(moduleData.firmicutes_bacteroidetes_ratio), 0, 10),
      this.normalizeFeature(this.validateData(moduleData.beneficial_bacteria_count), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.pathogenic_bacteria_count), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.gut_barrier_integrity), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.short_chain_fatty_acids), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.intestinal_ph), 5, 8),
      this.normalizeFeature(this.validateData(moduleData.probiotic_species_count), 0, 50),
      this.normalizeFeature(this.validateData(moduleData.gut_inflammation), 0, 100),
      this.normalizeFeature(this.validateData(ecbomeData.gut_ecs_production), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.neurotransmitter_production), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.immune_modulation), 0, 100)
    ];
  }
}

export { MicrobiomeFeatureExtractor };
export default MicrobiomeFeatureExtractor; 