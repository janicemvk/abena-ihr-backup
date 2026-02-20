import { BaseFeatureExtractor } from './BaseFeatureExtractor.js';

/**
 * TOXICOME FEATURE EXTRACTOR
 * Extracts toxin exposure and detoxification system features
 */
class ToxicomeFeatureExtractor extends BaseFeatureExtractor {
  constructor() {
    super('toxicome');
  }

  async extract(moduleData, ecdomeData, patientId) {
    return [
      this.normalizeFeature(this.validateData(moduleData.heavy_metal_burden), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.environmental_toxin_exposure), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.liver_detox_capacity), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.phase1_detox_efficiency), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.phase2_detox_efficiency), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.glutathione_levels), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.oxidative_stress_markers), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.cellular_repair_capacity), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.xenobiotic_metabolism), 0, 100),
      this.normalizeFeature(this.validateData(ecdomeData.detox_ecs_support), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.elimination_pathway_efficiency), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.toxin_binding_capacity), 0, 100)
    ];
  }
}

export { ToxicomeFeatureExtractor };
export default ToxicomeFeatureExtractor; 