import AbenaSDK from '@abena/sdk';

/**
 * Clinical Outcomes Module - Demonstrates proper Abena SDK usage
 * 
 * This module shows the correct pattern for integrating with the Abena IHR system:
 * - Uses Abena SDK for authentication, data access, privacy, and audit logging
 * - Focuses on business logic rather than infrastructure concerns
 * - Automatically handles security, encryption, and compliance
 */
class ClinicalOutcomesModule {

  constructor() {
    // ✅ Correct - Uses Abena SDK instead of custom implementations
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001', 
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003'
    });
  }

  /**
   * Get patient's latest clinical outcomes data
   * @param {string} patientId - Patient identifier
   * @param {string} userId - User requesting the data
   * @returns {Promise<Object>} Patient outcomes data
   */
  async getPatientOutcomes(patientId, userId) {
    try {
      // 1. Auto-handled auth & permissions
      const patientData = await this.abena.getPatientData(patientId, 'clinical_outcomes_analysis');
      
      // 2. Auto-handled privacy & encryption
      // 3. Auto-handled audit logging
      
      // 4. Focus on business logic
      return this.processOutcomesData(patientData);
    } catch (error) {
      console.error('Error retrieving patient outcomes:', error);
      throw new Error(`Failed to retrieve outcomes for patient ${patientId}`);
    }
  }

  /**
   * Record new pain assessment for a patient
   * @param {string} patientId - Patient identifier
   * @param {string} userId - User recording the assessment
   * @param {Object} assessmentData - Pain assessment data
   * @returns {Promise<Object>} Recorded assessment
   */
  async recordPainAssessment(patientId, userId, assessmentData) {
    try {
      // Validate assessment data
      this.validatePainAssessment(assessmentData);
      
      // Auto-handled auth, privacy, and audit logging
      const result = await this.abena.storePatientData(
        patientId, 
        'pain_assessment',
        {
          ...assessmentData,
          recorded_by: userId,
          recorded_at: new Date().toISOString()
        }
      );
      
      // Process and return the result
      return this.formatAssessmentResult(result);
    } catch (error) {
      console.error('Error recording pain assessment:', error);
      throw new Error(`Failed to record pain assessment for patient ${patientId}`);
    }
  }

  /**
   * Get patient progress over time
   * @param {string} patientId - Patient identifier
   * @param {string} userId - User requesting the data
   * @param {string} outcomeType - Type of outcome to analyze
   * @returns {Promise<Object>} Progress analysis
   */
  async getPatientProgress(patientId, userId, outcomeType = 'pain') {
    try {
      // Auto-handled auth & permissions
      const historicalData = await this.abena.getPatientData(patientId, 'outcome_progress_analysis');
      
      // Focus on business logic
      return this.analyzeProgress(historicalData, outcomeType);
    } catch (error) {
      console.error('Error analyzing patient progress:', error);
      throw new Error(`Failed to analyze progress for patient ${patientId}`);
    }
  }

  /**
   * Generate clinical outcomes report
   * @param {string} patientId - Patient identifier
   * @param {string} userId - User requesting the report
   * @param {Object} reportOptions - Report configuration
   * @returns {Promise<Object>} Clinical report
   */
  async generateClinicalReport(patientId, userId, reportOptions = {}) {
    try {
      // Auto-handled auth & permissions
      const patientData = await this.abena.getPatientData(patientId, 'clinical_report_generation');
      
      // Focus on business logic
      return this.generateReport(patientData, reportOptions);
    } catch (error) {
      console.error('Error generating clinical report:', error);
      throw new Error(`Failed to generate report for patient ${patientId}`);
    }
  }

  /**
   * Update patient treatment plan based on outcomes
   * @param {string} patientId - Patient identifier
   * @param {string} userId - User updating the plan
   * @param {Object} treatmentPlan - New treatment plan
   * @returns {Promise<Object>} Updated treatment plan
   */
  async updateTreatmentPlan(patientId, userId, treatmentPlan) {
    try {
      // Validate treatment plan
      this.validateTreatmentPlan(treatmentPlan);
      
      // Auto-handled auth, privacy, and audit logging
      const result = await this.abena.storePatientData(
        patientId,
        'treatment_plan_update',
        {
          ...treatmentPlan,
          updated_by: userId,
          updated_at: new Date().toISOString()
        }
      );
      
      return this.formatTreatmentPlanResult(result);
    } catch (error) {
      console.error('Error updating treatment plan:', error);
      throw new Error(`Failed to update treatment plan for patient ${patientId}`);
    }
  }

  // ============================================================================
  // Private Business Logic Methods
  // ============================================================================

  /**
   * Process and format outcomes data
   * @private
   */
  processOutcomesData(patientData) {
    // Business logic for processing outcomes
    const processed = {
      patientId: patientData.patientId,
      latestAssessments: this.extractLatestAssessments(patientData),
      trends: this.calculateTrends(patientData),
      recommendations: this.generateRecommendations(patientData)
    };
    
    return processed;
  }

  /**
   * Validate pain assessment data
   * @private
   */
  validatePainAssessment(assessmentData) {
    const required = ['current_pain', 'average_pain_24h', 'worst_pain_24h', 'least_pain_24h'];
    const missing = required.filter(field => !assessmentData[field]);
    
    if (missing.length > 0) {
      throw new Error(`Missing required fields: ${missing.join(', ')}`);
    }
    
    // Validate pain scores (0-10 scale)
    const painFields = ['current_pain', 'average_pain_24h', 'worst_pain_24h', 'least_pain_24h'];
    painFields.forEach(field => {
      const value = assessmentData[field];
      if (value < 0 || value > 10) {
        throw new Error(`${field} must be between 0 and 10`);
      }
    });
  }

  /**
   * Analyze patient progress over time
   * @private
   */
  analyzeProgress(historicalData, outcomeType) {
    // Business logic for progress analysis
    const baseline = this.findBaselineAssessment(historicalData, outcomeType);
    const current = this.findCurrentAssessment(historicalData, outcomeType);
    
    if (!baseline || !current) {
      return { error: 'Insufficient data for progress analysis' };
    }
    
    return {
      outcomeType,
      baseline: baseline.score,
      current: current.score,
      improvement: baseline.score - current.score,
      percentChange: ((baseline.score - current.score) / baseline.score) * 100,
      trend: this.determineTrend(baseline.score, current.score)
    };
  }

  /**
   * Generate clinical report
   * @private
   */
  generateReport(patientData, options) {
    // Business logic for report generation
    return {
      patientId: patientData.patientId,
      reportDate: new Date().toISOString(),
      summary: this.generateSummary(patientData),
      details: this.generateDetails(patientData, options),
      recommendations: this.generateRecommendations(patientData)
    };
  }

  /**
   * Validate treatment plan
   * @private
   */
  validateTreatmentPlan(treatmentPlan) {
    if (!treatmentPlan.interventions || treatmentPlan.interventions.length === 0) {
      throw new Error('Treatment plan must include at least one intervention');
    }
    
    if (!treatmentPlan.goals || treatmentPlan.goals.length === 0) {
      throw new Error('Treatment plan must include at least one goal');
    }
  }

  // ============================================================================
  // Helper Methods
  // ============================================================================

  extractLatestAssessments(patientData) {
    // Implementation for extracting latest assessments
    return patientData.assessments?.slice(-1)[0] || null;
  }

  calculateTrends(patientData) {
    // Implementation for calculating trends
    return {
      pain: 'improving',
      function: 'stable',
      quality: 'improving'
    };
  }

  generateRecommendations(patientData) {
    // Implementation for generating recommendations
    return [
      'Continue current treatment plan',
      'Schedule follow-up in 4 weeks',
      'Consider physical therapy referral'
    ];
  }

  findBaselineAssessment(data, outcomeType) {
    // Implementation for finding baseline assessment
    return data.assessments?.find(a => a.timing === 'baseline' && a.type === outcomeType);
  }

  findCurrentAssessment(data, outcomeType) {
    // Implementation for finding current assessment
    return data.assessments?.slice(-1).find(a => a.type === outcomeType);
  }

  determineTrend(baseline, current) {
    const change = baseline - current;
    if (change > 0.5) return 'improving';
    if (change < -0.5) return 'worsening';
    return 'stable';
  }

  generateSummary(patientData) {
    // Implementation for generating summary
    return {
      totalAssessments: patientData.assessments?.length || 0,
      lastAssessment: patientData.assessments?.slice(-1)[0]?.date,
      overallStatus: 'stable'
    };
  }

  generateDetails(patientData, options) {
    // Implementation for generating detailed report
    return {
      painAssessments: patientData.assessments?.filter(a => a.type === 'pain') || [],
      functionalAssessments: patientData.assessments?.filter(a => a.type === 'function') || [],
      qualityOfLife: patientData.assessments?.filter(a => a.type === 'qol') || []
    };
  }

  formatAssessmentResult(result) {
    return {
      success: true,
      assessmentId: result.id,
      recordedAt: result.recorded_at,
      message: 'Pain assessment recorded successfully'
    };
  }

  formatTreatmentPlanResult(result) {
    return {
      success: true,
      planId: result.id,
      updatedAt: result.updated_at,
      message: 'Treatment plan updated successfully'
    };
  }
}

export default ClinicalOutcomesModule; 