import ClinicalWorkflowEngine from './src/ClinicalWorkflowEngine.js';

// Example usage of the updated ClinicalWorkflowEngine with Abena SDK

async function exampleUsage() {
  // Mock module registry for example purposes
  const moduleRegistry = {
    getModulesByCapability: (capability) => {
      // Mock implementation
      return [];
    },
    routeClinicalData: async (patientId, dataType, data, context) => {
      // Mock implementation
      return [];
    }
  };

  // Initialize the ClinicalWorkflowEngine with Abena SDK configuration
  const workflowEngine = new ClinicalWorkflowEngine(
    moduleRegistry,
    {
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003'
    }
  );

  // Start a patient intake workflow
  const workflowInstanceId = await workflowEngine.startWorkflow(
    'patient-intake',
    'patient-123',
    {
      userId: 'clinician-456',
      priority: 'normal',
      source: 'patient-portal'
    }
  );

  console.log(`Started workflow: ${workflowInstanceId}`);

  // Route patient data through the workflow engine
  const results = await workflowEngine.routePatientData(
    'patient-123',
    'lab-results',
    {
      resourceType: 'Observation',
      code: {
        coding: [{
          system: 'http://loinc.org',
          code: '789-8',
          display: 'Red Blood Cells'
        }]
      },
      valueQuantity: {
        value: 4.2,
        unit: '10^12/L'
      }
    },
    {
      priority: 'normal',
      source: 'lab-system'
    }
  );

  console.log('Lab results processed:', results);
}

// Example of how a module would use the Abena SDK
class ExampleModule {
  constructor() {
    // Note: In a real implementation, you would import AbenaSDK
    // import AbenaSDK from '@abena/sdk';
    // this.abena = new AbenaSDK({...});
    
    // For this example, we'll mock the Abena SDK
    this.abena = {
      getPatientData: async (patientId, purpose) => {
        console.log(`Getting patient data for ${patientId} with purpose: ${purpose}`);
        return { id: patientId, name: 'John Doe' };
      },
      storeClinicalData: async (patientId, data, purpose) => {
        console.log(`Storing clinical data for ${patientId} with purpose: ${purpose}`);
        return { success: true };
      }
    };
  }

  async processLabResults(patientId, labData) {
    // 1. Auto-handled auth & permissions
    const patientData = await this.abena.getPatientData(patientId, 'lab_processing');
    
    // 2. Auto-handled privacy & encryption
    // 3. Auto-handled audit logging
    
    // 4. Focus on your business logic
    const processedResults = this.analyzeLabResults(labData, patientData);
    
    // Store results with auto-handled privacy & audit logging
    await this.abena.storeClinicalData(patientId, processedResults, 'lab_processing');
    
    return processedResults;
  }

  analyzeLabResults(labData, patientData) {
    // Your business logic here
    return {
      ...labData,
      analyzed: true,
      timestamp: new Date()
    };
  }
}

export { exampleUsage, ExampleModule }; 