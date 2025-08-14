import AbenaSDK from '@abena/sdk';

/**
 * Database Integration Module - Demonstrates Abena SDK integration with existing PostgreSQL schema
 * 
 * This module shows how to use the Abena SDK to interact with the clinical outcomes database
 * without direct database connections, ensuring proper authentication, privacy, and audit logging.
 */
class DatabaseIntegrationModule {

  constructor() {
    // ✅ Correct - Uses Abena SDK for all database operations
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003'
    });
  }

  /**
   * Get pain assessments for a patient
   * @param {string} patientId - Patient identifier
   * @param {string} userId - User requesting the data
   * @param {Object} options - Query options
   * @returns {Promise<Array>} Pain assessments
   */
  async getPainAssessments(patientId, userId, options = {}) {
    try {
      // Auto-handled auth, privacy, and audit logging
      const assessments = await this.abena.queryDatabase(
        'clinical_outcomes',
        'pain_assessments',
        {
          patient_id: patientId,
          ...options.filters
        },
        {
          purpose: 'clinical_analysis',
          requested_by: userId,
          include_audit: true
        }
      );
      
      return this.formatPainAssessments(assessments);
    } catch (error) {
      console.error('Error retrieving pain assessments:', error);
      throw new Error(`Failed to retrieve pain assessments for patient ${patientId}`);
    }
  }

  /**
   * Insert new pain assessment
   * @param {string} patientId - Patient identifier
   * @param {string} userId - User recording the assessment
   * @param {Object} assessmentData - Pain assessment data
   * @returns {Promise<Object>} Inserted assessment
   */
  async insertPainAssessment(patientId, userId, assessmentData) {
    try {
      // Validate assessment data
      this.validatePainAssessmentData(assessmentData);
      
      // Auto-handled auth, privacy, and audit logging
      const result = await this.abena.insertDatabase(
        'clinical_outcomes',
        'pain_assessments',
        {
          ...assessmentData,
          patient_id: patientId,
          created_by: userId,
          created_at: new Date().toISOString()
        },
        {
          purpose: 'clinical_documentation',
          requested_by: userId,
          audit_level: 'full'
        }
      );
      
      return this.formatInsertResult(result);
    } catch (error) {
      console.error('Error inserting pain assessment:', error);
      throw new Error(`Failed to insert pain assessment for patient ${patientId}`);
    }
  }

  /**
   * Get WOMAC assessments for a patient
   * @param {string} patientId - Patient identifier
   * @param {string} userId - User requesting the data
   * @param {Object} options - Query options
   * @returns {Promise<Array>} WOMAC assessments
   */
  async getWomacAssessments(patientId, userId, options = {}) {
    try {
      // Auto-handled auth, privacy, and audit logging
      const assessments = await this.abena.queryDatabase(
        'clinical_outcomes',
        'womac_assessments',
        {
          patient_id: patientId,
          ...options.filters
        },
        {
          purpose: 'functional_assessment_analysis',
          requested_by: userId,
          include_audit: true
        }
      );
      
      return this.formatWomacAssessments(assessments);
    } catch (error) {
      console.error('Error retrieving WOMAC assessments:', error);
      throw new Error(`Failed to retrieve WOMAC assessments for patient ${patientId}`);
    }
  }

  /**
   * Get patient progress summary
   * @param {string} patientId - Patient identifier
   * @param {string} userId - User requesting the data
   * @returns {Promise<Object>} Progress summary
   */
  async getPatientProgressSummary(patientId, userId) {
    try {
      // Auto-handled auth, privacy, and audit logging
      const summary = await this.abena.executeStoredProcedure(
        'clinical_outcomes',
        'get_patient_progress_summary',
        [patientId],
        {
          purpose: 'progress_analysis',
          requested_by: userId,
          include_audit: true
        }
      );
      
      return this.formatProgressSummary(summary);
    } catch (error) {
      console.error('Error retrieving progress summary:', error);
      throw new Error(`Failed to retrieve progress summary for patient ${patientId}`);
    }
  }

  /**
   * Get data quality report
   * @param {string} userId - User requesting the report
   * @param {Object} options - Report options
   * @returns {Promise<Object>} Data quality report
   */
  async getDataQualityReport(userId, options = {}) {
    try {
      // Auto-handled auth, privacy, and audit logging
      const report = await this.abena.queryView(
        'clinical_outcomes',
        'data_quality_summary',
        options.filters || {},
        {
          purpose: 'data_quality_analysis',
          requested_by: userId,
          include_audit: true
        }
      );
      
      return this.formatDataQualityReport(report);
    } catch (error) {
      console.error('Error retrieving data quality report:', error);
      throw new Error('Failed to retrieve data quality report');
    }
  }

  /**
   * Update patient treatment plan
   * @param {string} patientId - Patient identifier
   * @param {string} userId - User updating the plan
   * @param {Object} treatmentPlan - Treatment plan data
   * @returns {Promise<Object>} Update result
   */
  async updateTreatmentPlan(patientId, userId, treatmentPlan) {
    try {
      // Validate treatment plan
      this.validateTreatmentPlan(treatmentPlan);
      
      // Auto-handled auth, privacy, and audit logging
      const result = await this.abena.updateDatabase(
        'clinical_outcomes',
        'treatment_plans',
        {
          patient_id: patientId,
          ...treatmentPlan
        },
        {
          patient_id: patientId
        },
        {
          purpose: 'treatment_plan_update',
          requested_by: userId,
          audit_level: 'full'
        }
      );
      
      return this.formatUpdateResult(result);
    } catch (error) {
      console.error('Error updating treatment plan:', error);
      throw new Error(`Failed to update treatment plan for patient ${patientId}`);
    }
  }

  /**
   * Get audit trail for a patient
   * @param {string} patientId - Patient identifier
   * @param {string} userId - User requesting the audit trail
   * @param {Object} options - Audit options
   * @returns {Promise<Array>} Audit trail
   */
  async getPatientAuditTrail(patientId, userId, options = {}) {
    try {
      // Auto-handled auth, privacy, and audit logging
      const auditTrail = await this.abena.getAuditTrail(
        'patient',
        patientId,
        {
          start_date: options.startDate,
          end_date: options.endDate,
          action_types: options.actionTypes,
          requested_by: userId
        }
      );
      
      return this.formatAuditTrail(auditTrail);
    } catch (error) {
      console.error('Error retrieving audit trail:', error);
      throw new Error(`Failed to retrieve audit trail for patient ${patientId}`);
    }
  }

  // ============================================================================
  // Private Helper Methods
  // ============================================================================

  /**
   * Validate pain assessment data
   * @private
   */
  validatePainAssessmentData(assessmentData) {
    const required = ['current_pain', 'average_pain_24h', 'worst_pain_24h', 'least_pain_24h', 'pain_interference'];
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

  /**
   * Format pain assessments
   * @private
   */
  formatPainAssessments(assessments) {
    return assessments.map(assessment => ({
      id: assessment.id,
      patientId: assessment.patient_id,
      assessmentDate: assessment.assessment_date,
      measurementTiming: assessment.measurement_timing,
      currentPain: assessment.current_pain,
      averagePain24h: assessment.average_pain_24h,
      worstPain24h: assessment.worst_pain_24h,
      leastPain24h: assessment.least_pain_24h,
      painInterference: assessment.pain_interference,
      painAtRest: assessment.pain_at_rest,
      painWithMovement: assessment.pain_with_movement,
      painWithExercise: assessment.pain_with_exercise,
      painLocations: assessment.pain_locations,
      painQuality: assessment.pain_quality,
      assessorId: assessment.assessor_id,
      dataQuality: assessment.data_quality,
      notes: assessment.notes,
      createdAt: assessment.created_at,
      updatedAt: assessment.updated_at
    }));
  }

  /**
   * Format WOMAC assessments
   * @private
   */
  formatWomacAssessments(assessments) {
    return assessments.map(assessment => ({
      id: assessment.id,
      patientId: assessment.patient_id,
      assessmentDate: assessment.assessment_date,
      measurementTiming: assessment.measurement_timing,
      painScore: assessment.pain_score,
      stiffnessScore: assessment.stiffness_score,
      functionScore: assessment.function_score,
      totalScore: assessment.total_score,
      normalizedScore: assessment.normalized_score,
      assessorId: assessment.assessor_id,
      dataQuality: assessment.data_quality,
      notes: assessment.notes,
      createdAt: assessment.created_at,
      updatedAt: assessment.updated_at
    }));
  }

  /**
   * Format progress summary
   * @private
   */
  formatProgressSummary(summary) {
    return {
      patientId: summary.patient_id,
      baselineDate: summary.baseline_date,
      currentDate: summary.current_date,
      painImprovement: summary.pain_improvement,
      womacImprovement: summary.womac_improvement,
      odiImprovement: summary.odi_improvement,
      qolImprovement: summary.qol_improvement,
      overallStatus: summary.overall_status,
      recommendations: summary.recommendations
    };
  }

  /**
   * Format data quality report
   * @private
   */
  formatDataQualityReport(report) {
    return report.map(item => ({
      tableName: item.table_name,
      totalRecords: item.total_records,
      completeRecords: item.complete_records,
      adequateRecords: item.adequate_records,
      minimalRecords: item.minimal_records,
      insufficientRecords: item.insufficient_records,
      acceptableQualityRate: item.acceptable_quality_rate
    }));
  }

  /**
   * Format insert result
   * @private
   */
  formatInsertResult(result) {
    return {
      success: true,
      id: result.id,
      message: 'Record inserted successfully',
      auditId: result.audit_id
    };
  }

  /**
   * Format update result
   * @private
   */
  formatUpdateResult(result) {
    return {
      success: true,
      rowsAffected: result.rows_affected,
      message: 'Record updated successfully',
      auditId: result.audit_id
    };
  }

  /**
   * Format audit trail
   * @private
   */
  formatAuditTrail(auditTrail) {
    return auditTrail.map(entry => ({
      timestamp: entry.timestamp,
      userId: entry.user_id,
      action: entry.action,
      resource: entry.resource,
      resourceId: entry.resource_id,
      details: entry.details,
      ipAddress: entry.ip_address,
      userAgent: entry.user_agent
    }));
  }
}

export default DatabaseIntegrationModule; 