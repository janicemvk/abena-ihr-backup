import AbenaSDK from '@abena/sdk';
import { FHIRValidator } from './utils/fhir-validator.js';
import { ClinicalDecisionSupport } from './utils/clinical-decision-support.js';
import { WorkflowStateManager } from './utils/workflow-state-manager.js';

class ClinicalWorkflowEngine {
  constructor(moduleRegistry, options = {}) {
    this.moduleRegistry = moduleRegistry;
    
    // Initialize Abena SDK with service URLs
    this.abena = new AbenaSDK({
      authServiceUrl: options.authServiceUrl || 'http://localhost:3001',
      dataServiceUrl: options.dataServiceUrl || 'http://localhost:8001',
      privacyServiceUrl: options.privacyServiceUrl || 'http://localhost:8002',
      blockchainServiceUrl: options.blockchainServiceUrl || 'http://localhost:8003'
    });
    
    // Initialize utility classes with Abena SDK configuration
    this.validator = new FHIRValidator(options);
    this.decisionSupport = new ClinicalDecisionSupport(options);
    this.stateManager = new WorkflowStateManager(options);
    this.workflowDefinitions = new Map();
    this.activeWorkflows = new Map();
    
    this.initializeStandardWorkflows();
  }

  /**
   * Initialize standard healthcare workflows
   */
  initializeStandardWorkflows() {
    // Patient Intake Workflow
    this.defineWorkflow('patient-intake', {
      steps: [
        { id: 'demographics', module: 'patient-portal', required: true },
        { id: 'insurance-verification', module: 'insurance-module', required: true },
        { id: 'medical-history', module: 'patient-portal', required: true },
        { id: 'initial-assessment', module: 'clinical-assessment', required: false },
        { id: 'care-plan-generation', module: 'care-planning', required: false }
      ],
      triggers: ['patient-registration'],
      timeout: 1800000 // 30 minutes
    });

    // Lab Results Processing Workflow
    this.defineWorkflow('lab-results-processing', {
      steps: [
        { id: 'result-ingestion', module: 'lab-integration', required: true },
        { id: 'result-validation', module: 'lab-results', required: true },
        { id: 'clinical-interpretation', module: 'clinical-context-engine', required: true },
        { id: 'provider-notification', module: 'notification-service', required: true },
        { id: 'patient-notification', module: 'patient-portal', required: false }
      ],
      triggers: ['lab-result-received'],
      timeout: 300000 // 5 minutes
    });

    // Medication Management Workflow
    this.defineWorkflow('medication-management', {
      steps: [
        { id: 'prescription-validation', module: 'pharmacy-integration', required: true },
        { id: 'drug-interaction-check', module: 'clinical-decision-support', required: true },
        { id: 'allergy-check', module: 'clinical-context-engine', required: true },
        { id: 'dosage-calculation', module: 'medication-module', required: true },
        { id: 'prescription-routing', module: 'pharmacy-integration', required: true }
      ],
      triggers: ['prescription-created', 'medication-review'],
      timeout: 600000 // 10 minutes
    });

    // Comprehensive Care Workflow (Multi-modal)
    this.defineWorkflow('comprehensive-care', {
      steps: [
        { id: 'traditional-assessment', module: 'clinical-assessment', required: true },
        { id: 'tcm-evaluation', module: 'tcm', required: false },
        { id: 'ayurveda-evaluation', module: 'ayurveda', required: false },
        { id: 'functional-medicine-analysis', module: 'functional-medicine', required: false },
        { id: 'nutrition-assessment', module: 'nutrition', required: false },
        { id: 'integrated-care-plan', module: 'care-planning', required: true }
      ],
      triggers: ['comprehensive-evaluation-requested'],
      timeout: 3600000 // 60 minutes
    });
  }

  /**
   * Define a new workflow
   */
  defineWorkflow(workflowId, definition) {
    this.workflowDefinitions.set(workflowId, {
      ...definition,
      id: workflowId,
      createdAt: new Date()
    });
  }

  /**
   * Start a workflow for a patient
   */
  async startWorkflow(workflowId, patientId, context = {}) {
    const definition = this.workflowDefinitions.get(workflowId);
    if (!definition) {
      throw new Error(`Workflow not found: ${workflowId}`);
    }

    const workflowInstanceId = `${workflowId}-${patientId}-${Date.now()}`;
    
    const workflowInstance = {
      id: workflowInstanceId,
      workflowId,
      patientId,
      status: 'active',
      currentStep: 0,
      steps: definition.steps.map(step => ({
        ...step,
        status: 'pending',
        attempts: 0,
        results: null
      })),
      context: {
        ...context,
        startedAt: new Date(),
        timeout: definition.timeout
      },
      results: new Map()
    };

    this.activeWorkflows.set(workflowInstanceId, workflowInstance);
    
    // Set timeout
    setTimeout(() => {
      this.handleWorkflowTimeout(workflowInstanceId);
    }, definition.timeout);

    // Start first step
    await this.executeNextStep(workflowInstanceId);
    
    return workflowInstanceId;
  }

  /**
   * Execute the next step in a workflow
   */
  async executeNextStep(workflowInstanceId) {
    const workflow = this.activeWorkflows.get(workflowInstanceId);
    if (!workflow || workflow.status !== 'active') {
      return;
    }

    const currentStep = workflow.steps[workflow.currentStep];
    if (!currentStep) {
      // Workflow complete
      await this.completeWorkflow(workflowInstanceId);
      return;
    }

    try {
      currentStep.status = 'running';
      currentStep.startedAt = new Date();
      currentStep.attempts++;

      // Get target modules for this step
      const targetModules = this.moduleRegistry.getModulesByCapability(currentStep.module);
      
      if (targetModules.length === 0 && currentStep.required) {
        throw new Error(`No modules available for required step: ${currentStep.id}`);
      }

      let stepResult = null;
      let stepSuccess = false;

      // Try each module until one succeeds
      for (const module of targetModules) {
        try {
          stepResult = await this.executeStepWithModule(
            workflow,
            currentStep,
            module
          );
          stepSuccess = true;
          break;
        } catch (error) {
          console.warn(`Module ${module.id} failed for step ${currentStep.id}:`, error.message);
          continue;
        }
      }

      if (!stepSuccess && currentStep.required) {
        throw new Error(`All modules failed for required step: ${currentStep.id}`);
      }

      // Update step status
      currentStep.status = stepSuccess ? 'completed' : 'skipped';
      currentStep.completedAt = new Date();
      currentStep.results = stepResult;

      // Store results in workflow context
      workflow.results.set(currentStep.id, stepResult);
      workflow.context[`${currentStep.id}_result`] = stepResult;

      // Move to next step
      workflow.currentStep++;
      
      // Execute next step
      setTimeout(() => this.executeNextStep(workflowInstanceId), 100);

    } catch (error) {
      await this.handleStepError(workflowInstanceId, currentStep, error);
    }
  }

  /**
   * Execute a workflow step with a specific module
   */
  async executeStepWithModule(workflow, step, module) {
    const stepContext = {
      workflowId: workflow.workflowId,
      workflowInstanceId: workflow.id,
      patientId: workflow.patientId,
      stepId: step.id,
      previousResults: Object.fromEntries(workflow.results),
      ...workflow.context
    };

    // Prepare step data based on step type
    const stepData = await this.prepareStepData(step, stepContext);

    // Execute step through module
    const result = await module.instance.executeWorkflowStep({
      stepId: step.id,
      stepType: step.module,
      data: stepData,
      context: stepContext,
      patientId: workflow.patientId
    });

    // Validate result if it's clinical data
    if (this.isClinicalData(result)) {
      await this.validateClinicalResult(result, step);
    }

    return result;
  }

  /**
   * Prepare data for workflow step execution
   */
  async prepareStepData(step, context) {
    const stepData = {
      timestamp: new Date(),
      context
    };

    // Add patient data if needed
    if (this.stepRequiresPatientData(step)) {
      stepData.patient = await this.getPatientData(context.patientId);
    }

    // Add previous step results
    if (step.dependsOn) {
      stepData.dependencies = {};
      for (const dep of step.dependsOn) {
        stepData.dependencies[dep] = context[`${dep}_result`];
      }
    }

    return stepData;
  }

  /**
   * Handle workflow step errors
   */
  async handleStepError(workflowInstanceId, step, error) {
    const workflow = this.activeWorkflows.get(workflowInstanceId);
    
    step.status = 'failed';
    step.error = error.message;
    step.failedAt = new Date();

    // Retry logic for non-critical steps
    if (step.attempts < 3 && !step.required) {
      setTimeout(() => {
        step.status = 'pending';
        this.executeNextStep(workflowInstanceId);
      }, 5000 * step.attempts); // Exponential backoff
      return;
    }

    // Handle critical step failure
    if (step.required) {
      workflow.status = 'failed';
      workflow.error = `Required step failed: ${step.id} - ${error.message}`;
      workflow.failedAt = new Date();
      
      // Notify clinical staff
      await this.notifyClinicalStaff(workflow, 'workflow_failed');
    } else {
      // Skip optional step and continue
      step.status = 'skipped';
      workflow.currentStep++;
      await this.executeNextStep(workflowInstanceId);
    }
  }

  /**
   * Complete a workflow
   */
  async completeWorkflow(workflowInstanceId) {
    const workflow = this.activeWorkflows.get(workflowInstanceId);
    if (!workflow) return;

    workflow.status = 'completed';
    workflow.completedAt = new Date();

    // Generate workflow summary
    const summary = this.generateWorkflowSummary(workflow);
    
    // Store workflow results in patient record
    await this.storeWorkflowResults(workflow, summary);
    
    // Trigger downstream processes
    await this.triggerDownstreamProcesses(workflow, summary);
    
    // Clean up
    this.activeWorkflows.delete(workflowInstanceId);
    
    // Notify completion
    await this.notifyWorkflowCompletion(workflow, summary);
  }

  /**
   * Handle workflow timeout
   */
  async handleWorkflowTimeout(workflowInstanceId) {
    const workflow = this.activeWorkflows.get(workflowInstanceId);
    if (!workflow || workflow.status !== 'active') return;

    workflow.status = 'timeout';
    workflow.timedOutAt = new Date();

    // Notify clinical staff
    await this.notifyClinicalStaff(workflow, 'workflow_timeout');
    
    this.activeWorkflows.delete(workflowInstanceId);
  }

  /**
   * Route patient data to appropriate clinical modules
   */
  async routePatientData(patientId, dataType, data, options = {}) {
    const context = {
      patientId,
      dataType,
      timestamp: new Date(),
      source: options.source || 'clinical-workflow-engine',
      priority: options.priority || 'normal',
      ...options.context
    };

    // Determine routing strategy based on data type
    const routingStrategy = this.determineRoutingStrategy(dataType, data);
    
    let results = [];

    switch (routingStrategy) {
      case 'parallel':
        results = await this.routeParallel(patientId, dataType, data, context);
        break;
      case 'sequential':
        results = await this.routeSequential(patientId, dataType, data, context);
        break;
      case 'conditional':
        results = await this.routeConditional(patientId, dataType, data, context);
        break;
      default:
        results = await this.moduleRegistry.routeClinicalData(patientId, dataType, data, context);
    }

    // Apply clinical decision support
    const enhancedResults = await this.applyClinicalDecisionSupport(
      patientId, dataType, results, context
    );

    return enhancedResults;
  }

  /**
   * Determine routing strategy based on data type
   */
  determineRoutingStrategy(dataType, data) {
    const parallelTypes = ['lab-results', 'vital-signs', 'diagnostic-images'];
    const sequentialTypes = ['medication-orders', 'care-plans'];
    const conditionalTypes = ['symptoms', 'assessments'];

    if (parallelTypes.includes(dataType)) return 'parallel';
    if (sequentialTypes.includes(dataType)) return 'sequential';
    if (conditionalTypes.includes(dataType)) return 'conditional';
    
    return 'parallel'; // default
  }

  /**
   * Route data in parallel to multiple modules
   */
  async routeParallel(patientId, dataType, data, context) {
    const targetModules = this.moduleRegistry.getModulesByCapability(dataType);
    
    const promises = targetModules.map(async (module) => {
      try {
        return await module.instance.processData({
          patientId,
          dataType,
          data,
          context
        });
      } catch (error) {
        return { moduleId: module.id, error: error.message };
      }
    });

    return await Promise.allSettled(promises);
  }

  /**
   * Route data sequentially through modules
   */
  async routeSequential(patientId, dataType, data, context) {
    const targetModules = this.moduleRegistry.getModulesByCapability(dataType);
    const results = [];
    let currentData = data;

    for (const module of targetModules) {
      try {
        const result = await module.instance.processData({
          patientId,
          dataType,
          data: currentData,
          context: { ...context, previousResults: results }
        });
        
        results.push({ moduleId: module.id, result });
        
        // Use result as input for next module if it transforms data
        if (result && result.transformedData) {
          currentData = result.transformedData;
        }
      } catch (error) {
        results.push({ moduleId: module.id, error: error.message });
        break; // Stop sequential processing on error
      }
    }

    return results;
  }

  /**
   * Route data conditionally based on clinical rules
   */
  async routeConditional(patientId, dataType, data, context) {
    // Get patient context for conditional routing
    const patientContext = await this.getPatientData(patientId);
    
    // Determine which modules to route to based on conditions
    const applicableModules = await this.determineApplicableModules(
      dataType, data, patientContext
    );

    return await this.routeParallel(patientId, dataType, data, {
      ...context,
      targetModules: applicableModules
    });
  }

  /**
   * Apply clinical decision support to results
   */
  async applyClinicalDecisionSupport(patientId, dataType, results, context) {
    return await this.decisionSupport.analyzeResults({
      patientId,
      dataType,
      results,
      context
    });
  }

  /**
   * Generate workflow summary
   */
  generateWorkflowSummary(workflow) {
    const completedSteps = workflow.steps.filter(s => s.status === 'completed');
    const failedSteps = workflow.steps.filter(s => s.status === 'failed');
    const skippedSteps = workflow.steps.filter(s => s.status === 'skipped');

    return {
      workflowId: workflow.workflowId,
      patientId: workflow.patientId,
      status: workflow.status,
      duration: workflow.completedAt - workflow.context.startedAt,
      stepsSummary: {
        total: workflow.steps.length,
        completed: completedSteps.length,
        failed: failedSteps.length,
        skipped: skippedSteps.length
      },
      results: Object.fromEntries(workflow.results),
      clinicalFindings: this.extractClinicalFindings(workflow.results)
    };
  }

  /**
   * Utility methods
   */
  stepRequiresPatientData(step) {
    return ['clinical-assessment', 'care-planning', 'medication-management'].includes(step.module);
  }

  isClinicalData(data) {
    return data && (data.resourceType || data.clinicalData || data.fhirResource);
  }

  async validateClinicalResult(result, step) {
    if (result.fhirResource) {
      return await this.validator.validate(result.fhirResource);
    }
    return true;
  }

  async getPatientData(patientId) {
    // Use Abena SDK to get patient data with auto-handled auth & privacy
    return await this.abena.getPatientData(patientId, 'clinical_workflow_engine');
  }

  async determineApplicableModules(dataType, data, patientContext) {
    // Clinical logic to determine which modules should process the data
    // Based on patient conditions, preferences, treatment plans, etc.
    return this.moduleRegistry.getModulesByCapability(dataType);
  }

  extractClinicalFindings(results) {
    // Extract key clinical findings from workflow results
    const findings = [];
    
    for (const [stepId, result] of results) {
      if (result && result.clinicalFindings) {
        findings.push(...result.clinicalFindings);
      }
    }
    
    return findings;
  }

  async storeWorkflowResults(workflow, summary) {
    // Store workflow results using Abena SDK with auto-handled privacy & audit logging
    const workflowResource = {
      resourceType: 'CarePlan',
      id: `workflow-${workflow.id}`,
      status: 'completed',
      intent: 'plan',
      title: `Clinical Workflow: ${workflow.workflowId}`,
      description: `Workflow execution results for patient ${workflow.patientId}`,
      subject: {
        reference: `Patient/${workflow.patientId}`
      },
      period: {
        start: workflow.context.startedAt,
        end: workflow.completedAt
      },
      activity: workflow.steps.map(step => ({
        detail: {
          code: {
            coding: [{
              system: 'http://abena.com/workflow-steps',
              code: step.id,
              display: step.module
            }]
          },
          status: step.status,
          description: step.results ? JSON.stringify(step.results) : undefined
        }
      })),
      note: [{
        text: `Workflow Summary: ${JSON.stringify(summary)}`
      }]
    };

    await this.abena.storeClinicalData(workflow.patientId, workflowResource, 'workflow_results');
  }

  async triggerDownstreamProcesses(workflow, summary) {
    // Use Abena SDK to trigger downstream processes with auto-handled audit logging
    
    // Trigger care plan updates if workflow generated care plan data
    if (summary.results.care_plan_generation) {
      await this.abena.triggerProcess('care_plan_update', {
        patientId: workflow.patientId,
        workflowId: workflow.workflowId,
        carePlanData: summary.results.care_plan_generation,
        timestamp: new Date()
      }, 'clinical_workflow_engine');
    }

    // Trigger follow-up scheduling if needed
    if (summary.clinicalFindings.some(finding => finding.requiresFollowUp)) {
      await this.abena.triggerProcess('follow_up_scheduling', {
        patientId: workflow.patientId,
        workflowId: workflow.workflowId,
        findings: summary.clinicalFindings.filter(f => f.requiresFollowUp),
        timestamp: new Date()
      }, 'clinical_workflow_engine');
    }

    // Trigger medication reviews if medication data was processed
    if (summary.results.medication_management) {
      await this.abena.triggerProcess('medication_review', {
        patientId: workflow.patientId,
        workflowId: workflow.workflowId,
        medicationData: summary.results.medication_management,
        timestamp: new Date()
      }, 'clinical_workflow_engine');
    }
  }

  async notifyWorkflowCompletion(workflow, summary) {
    // Use Abena SDK to send workflow completion notification
    const notification = {
      type: 'workflow_completion',
      priority: 'normal',
      title: 'Workflow Completed',
      message: `Workflow ${workflow.workflowId} for patient ${workflow.patientId} has completed successfully`,
      details: {
        workflowId: workflow.workflowId,
        workflowInstanceId: workflow.id,
        patientId: workflow.patientId,
        summary,
        timestamp: new Date()
      },
      recipients: ['care_team']
    };

    await this.abena.sendNotification(notification, 'clinical_workflow_engine');
  }

  async notifyClinicalStaff(workflow, eventType) {
    // Use Abena SDK to send notifications with auto-handled audit logging
    const notification = {
      type: 'clinical_alert',
      priority: 'high',
      title: `Workflow ${eventType.replace('_', ' ')}`,
      message: `Workflow ${workflow.workflowId} for patient ${workflow.patientId} has ${eventType.replace('_', ' ')}`,
      details: {
        workflowId: workflow.workflowId,
        workflowInstanceId: workflow.id,
        patientId: workflow.patientId,
        eventType,
        timestamp: new Date(),
        error: workflow.error || null
      },
      recipients: ['clinical_staff']
    };

    await this.abena.sendNotification(notification, 'clinical_workflow_engine');
  }
}

export default ClinicalWorkflowEngine; 