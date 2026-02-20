import { BaseFeatureExtractor } from './BaseFeatureExtractor.js';

/**
 * PHARMACOME FEATURE EXTRACTOR
 * Extracts pharmacological response and drug metabolism features
 */
class PharmacomedFeatureExtractor extends BaseFeatureExtractor {
  constructor() {
    super('pharmacome');
  }

  async extract(moduleData, ecdomeData, patientId) {
    return [
      this.normalizeFeature(this.validateData(moduleData.drug_metabolism_rate), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.cytochrome_p450_activity), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.drug_transporter_efficiency), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.pharmacokinetic_profile), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.adverse_drug_reaction_risk), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.therapeutic_response_prediction), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.drug_interaction_potential), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.medication_adherence_factors), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.personalized_dosing_requirements), 0, 100),
      this.normalizeFeature(this.validateData(ecdomeData.drug_ecs_interactions), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.bioavailability_factors), 0, 100),
      this.normalizeFeature(this.validateData(moduleData.therapeutic_drug_monitoring), 0, 100)
    ];
  }
}

export { PharmacomedFeatureExtractor };
export default PharmacomedFeatureExtractor; 