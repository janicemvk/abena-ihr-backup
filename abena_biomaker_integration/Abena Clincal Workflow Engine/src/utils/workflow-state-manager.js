import AbenaSDK from '@abena/sdk';

class WorkflowStateManager {
  constructor(options = {}) {
    // Initialize Abena SDK for workflow state management
    this.abena = new AbenaSDK({
      authServiceUrl: options.authServiceUrl || 'http://localhost:3001',
      dataServiceUrl: options.dataServiceUrl || 'http://localhost:8001',
      privacyServiceUrl: options.privacyServiceUrl || 'http://localhost:8002',
      blockchainServiceUrl: options.blockchainServiceUrl || 'http://localhost:8003'
    });
    
    this.states = new Map();
    this.history = new Map();
    this.maxHistorySize = 1000;
  }

  /**
   * Get current state of a workflow
   * @param {string} workflowId - The workflow instance ID
   * @returns {Object|null} - Current workflow state or null if not found
   */
  getState(workflowId) {
    return this.states.get(workflowId) || null;
  }

  /**
   * Update workflow state
   * @param {string} workflowId - The workflow instance ID
   * @param {Object} newState - New state to set
   * @param {Object} context - Additional context for the state change
   */
  async updateState(workflowId, newState, context = {}) {
    const currentState = this.states.get(workflowId);
    const timestamp = new Date();

    // Create state transition record
    const transition = {
      from: currentState,
      to: newState,
      timestamp,
      context
    };

    // Update current state
    this.states.set(workflowId, {
      ...newState,
      lastUpdated: timestamp
    });

    // Add to history
    this.addToHistory(workflowId, transition);

    // Use Abena SDK to log state transition with auto-handled audit logging
    try {
      await this.abena.logStateTransition(workflowId, transition, 'workflow_state_manager');
    } catch (error) {
      console.warn('Could not log state transition:', error.message);
    }
  }

  /**
   * Add state transition to history
   * @param {string} workflowId - The workflow instance ID
   * @param {Object} transition - State transition record
   */
  addToHistory(workflowId, transition) {
    if (!this.history.has(workflowId)) {
      this.history.set(workflowId, []);
    }

    const workflowHistory = this.history.get(workflowId);
    workflowHistory.push(transition);

    // Maintain history size limit
    if (workflowHistory.length > this.maxHistorySize) {
      workflowHistory.shift();
    }
  }

  /**
   * Get workflow history
   * @param {string} workflowId - The workflow instance ID
   * @returns {Array} - Array of state transitions
   */
  getHistory(workflowId) {
    return this.history.get(workflowId) || [];
  }

  /**
   * Clear workflow state and history
   * @param {string} workflowId - The workflow instance ID
   */
  async clearWorkflow(workflowId) {
    const state = this.states.get(workflowId);
    const history = this.history.get(workflowId);
    
    this.states.delete(workflowId);
    this.history.delete(workflowId);

    // Use Abena SDK to log workflow cleanup with auto-handled audit logging
    try {
      await this.abena.logWorkflowCleanup(workflowId, {
        state,
        historyCount: history ? history.length : 0,
        timestamp: new Date()
      }, 'workflow_state_manager');
    } catch (error) {
      console.warn('Could not log workflow cleanup:', error.message);
    }
  }

  /**
   * Get all active workflows
   * @returns {Array} - Array of active workflow states
   */
  getActiveWorkflows() {
    return Array.from(this.states.entries())
      .filter(([_, state]) => state.status === 'active')
      .map(([id, state]) => ({ id, ...state }));
  }

  /**
   * Get workflows by status
   * @param {string} status - Status to filter by
   * @returns {Array} - Array of workflow states with matching status
   */
  getWorkflowsByStatus(status) {
    return Array.from(this.states.entries())
      .filter(([_, state]) => state.status === status)
      .map(([id, state]) => ({ id, ...state }));
  }

  /**
   * Get workflows by patient
   * @param {string} patientId - Patient ID to filter by
   * @returns {Array} - Array of workflow states for the patient
   */
  getWorkflowsByPatient(patientId) {
    return Array.from(this.states.entries())
      .filter(([_, state]) => state.patientId === patientId)
      .map(([id, state]) => ({ id, ...state }));
  }

  /**
   * Get workflows by type
   * @param {string} workflowType - Workflow type to filter by
   * @returns {Array} - Array of workflow states of the specified type
   */
  getWorkflowsByType(workflowType) {
    return Array.from(this.states.entries())
      .filter(([_, state]) => state.workflowId === workflowType)
      .map(([id, state]) => ({ id, ...state }));
  }

  /**
   * Get workflows that need attention
   * @returns {Array} - Array of workflows requiring attention
   */
  getWorkflowsNeedingAttention() {
    return Array.from(this.states.entries())
      .filter(([_, state]) => {
        // Check for various conditions that might need attention
        return (
          state.status === 'active' && (
            state.error ||
            state.timeout ||
            state.requiresReview ||
            (state.lastUpdated && 
             Date.now() - state.lastUpdated.getTime() > state.timeout)
          )
        );
      })
      .map(([id, state]) => ({ id, ...state }));
  }

  /**
   * Get workflow statistics
   * @returns {Object} - Statistics about workflows
   */
  getWorkflowStatistics() {
    const stats = {
      total: this.states.size,
      byStatus: {},
      byType: {},
      averageDuration: 0,
      completionRate: 0
    };

    let totalDuration = 0;
    let completedCount = 0;

    for (const [_, state] of this.states.entries()) {
      // Count by status
      stats.byStatus[state.status] = (stats.byStatus[state.status] || 0) + 1;

      // Count by type
      stats.byType[state.workflowId] = (stats.byType[state.workflowId] || 0) + 1;

      // Calculate duration for completed workflows
      if (state.status === 'completed' && state.startedAt && state.completedAt) {
        totalDuration += state.completedAt - state.startedAt;
        completedCount++;
      }
    }

    // Calculate averages
    if (completedCount > 0) {
      stats.averageDuration = totalDuration / completedCount;
      stats.completionRate = completedCount / stats.total;
    }

    return stats;
  }

  /**
   * Export workflow state
   * @param {string} workflowId - The workflow instance ID
   * @returns {Object} - Exported workflow state
   */
  exportWorkflowState(workflowId) {
    const state = this.states.get(workflowId);
    const history = this.history.get(workflowId);

    if (!state) return null;

    return {
      currentState: state,
      history: history || [],
      exportedAt: new Date()
    };
  }

  /**
   * Import workflow state
   * @param {string} workflowId - The workflow instance ID
   * @param {Object} importedState - State to import
   */
  importWorkflowState(workflowId, importedState) {
    if (!importedState || !importedState.currentState) {
      throw new Error('Invalid workflow state format');
    }

    this.states.set(workflowId, importedState.currentState);
    
    if (importedState.history) {
      this.history.set(workflowId, importedState.history);
    }
  }
}

export { WorkflowStateManager }; 