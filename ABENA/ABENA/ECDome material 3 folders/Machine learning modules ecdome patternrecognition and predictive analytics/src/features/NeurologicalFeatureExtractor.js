import { BaseFeatureExtractor } from './BaseFeatureExtractor.js';

/**
 * NEUROLOGICAL FEATURE EXTRACTOR
 * Extracts neurological system and cognitive function features
 */
class NeurologicalFeatureExtractor extends BaseFeatureExtractor {
  constructor() {
    super('neurological');
  }

  async extract(moduleData, ecdomeData, patientId) {
    return [
      this.normalizeFeature(this.validateData(moduleData.cognitive_performance), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.memory_function), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.attention_focus), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.executive_function), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.neuroplasticity_markers), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.neurotransmitter_balance), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.brain_derived_neurotrophic_factor), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.neural_connectivity), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.mood_regulation), 0, 100),
      this.normalizeFeature(this.validateData(ecdomeData.neurological_ecs_signaling), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.sleep_brain_function), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.neuroprotective_factors), 0, 100)
    ];
  }
}

export { NeurologicalFeatureExtractor };
export default NeurologicalFeatureExtractor; 