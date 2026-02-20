import AbenaSDK from '@abena/sdk';

class FHIRValidator {
  constructor(options = {}) {
    // Initialize Abena SDK for FHIR validation
    this.abena = new AbenaSDK({
      authServiceUrl: options.authServiceUrl || 'http://localhost:3001',
      dataServiceUrl: options.dataServiceUrl || 'http://localhost:8001',
      privacyServiceUrl: options.privacyServiceUrl || 'http://localhost:8002',
      blockchainServiceUrl: options.blockchainServiceUrl || 'http://localhost:8003'
    });
  }

  /**
   * Validate a FHIR resource against the FHIR specification
   * @param {Object} resource - The FHIR resource to validate
   * @returns {Promise<boolean>} - Whether the resource is valid
   */
  async validate(resource) {
    try {
      // Use Abena SDK for FHIR validation with auto-handled audit logging
      const validationResult = await this.abena.validateFHIRResource(resource, 'clinical_workflow_engine');
      
      if (!validationResult.valid) {
        console.error('FHIR validation errors:', validationResult.errors);
        throw new Error('FHIR resource validation failed');
      }

      // Additional clinical validation rules
      await this.validateClinicalRules(resource);

      return true;
    } catch (error) {
      console.error('FHIR validation error:', error);
      throw error;
    }
  }

  /**
   * Apply additional clinical validation rules
   * @param {Object} resource - The FHIR resource to validate
   * @returns {Promise<void>}
   */
  async validateClinicalRules(resource) {
    switch (resource.resourceType) {
      case 'Observation':
        await this.validateObservation(resource);
        break;
      case 'MedicationRequest':
        await this.validateMedicationRequest(resource);
        break;
      case 'CarePlan':
        await this.validateCarePlan(resource);
        break;
      // Add more resource type validations as needed
    }
  }

  /**
   * Validate Observation resource
   * @param {Object} observation - The Observation resource
   * @returns {Promise<void>}
   */
  async validateObservation(observation) {
    if (!observation.code || !observation.code.coding) {
      throw new Error('Observation must have a code with coding');
    }

    if (!observation.effectiveDateTime && !observation.effectivePeriod) {
      throw new Error('Observation must have an effective date/time or period');
    }

    if (!observation.valueQuantity && !observation.valueCodeableConcept) {
      throw new Error('Observation must have a value');
    }
  }

  /**
   * Validate MedicationRequest resource
   * @param {Object} medicationRequest - The MedicationRequest resource
   * @returns {Promise<void>}
   */
  async validateMedicationRequest(medicationRequest) {
    if (!medicationRequest.medicationCodeableConcept && !medicationRequest.medicationReference) {
      throw new Error('MedicationRequest must specify a medication');
    }

    if (!medicationRequest.dosageInstruction || medicationRequest.dosageInstruction.length === 0) {
      throw new Error('MedicationRequest must have at least one dosage instruction');
    }

    if (!medicationRequest.authoredOn) {
      throw new Error('MedicationRequest must have an authored date');
    }
  }

  /**
   * Validate CarePlan resource
   * @param {Object} carePlan - The CarePlan resource
   * @returns {Promise<void>}
   */
  async validateCarePlan(carePlan) {
    if (!carePlan.category || carePlan.category.length === 0) {
      throw new Error('CarePlan must have at least one category');
    }

    if (!carePlan.activity || carePlan.activity.length === 0) {
      throw new Error('CarePlan must have at least one activity');
    }

    if (!carePlan.period || !carePlan.period.start) {
      throw new Error('CarePlan must have a period with start date');
    }
  }
}

export { FHIRValidator }; 