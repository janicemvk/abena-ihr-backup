import AbenaSDK from '@abena/sdk';

// ============================================================================
// Type Definitions
// ============================================================================

interface PainAssessmentData {
  current_pain: number;
  average_pain_24h: number;
  worst_pain_24h: number;
  least_pain_24h: number;
  pain_interference: number;
  pain_at_rest?: number;
  pain_with_movement?: number;
  pain_with_exercise?: number;
  pain_locations?: string[];
  pain_quality?: string[];
  notes?: string;
}

interface TreatmentPlan {
  interventions: TreatmentIntervention[];
  goals: TreatmentGoal[];
  duration_weeks: number;
  notes?: string;
}

interface TreatmentIntervention {
  type: 'medication' | 'physical_therapy' | 'lifestyle' | 'procedure';
  name: string;
  description: string;
  frequency?: string;
  duration?: string;
}

interface TreatmentGoal {
  description: string;
  target_value?: number;
  timeframe_weeks: number;
  measurable: boolean;
}

interface PatientData {
  patientId: string;
  assessments?: Assessment[];
  demographics?: any;
  medical_history?: any;
}

interface Assessment {
  id: string;
  type: 'pain' | 'function' | 'qol' | 'womac' | 'odi';
  timing: 'baseline' | 'week_2' | 'week_4' | 'week_8' | 'week_12' | 'week_24' | 'week_52';
  date: string;
  score: number;
  data: any;
}

interface ProgressAnalysis {
  outcomeType: string;
  baseline: number;
  current: number;
  improvement: number;
  percentChange: number;
  trend: 'improving' | 'worsening' | 'stable';
}

interface ClinicalReport {
  patientId: string;
  reportDate: string;
  summary: ReportSummary;
  details: ReportDetails;
  recommendations: string[];
}

interface ReportSummary {
  totalAssessments: number;
  lastAssessment?: string;
  overallStatus: string;
}

interface ReportDetails {
  painAssessments: Assessment[];
  functionalAssessments: Assessment[];
  qualityOfLife: Assessment[];
}

interface AbenaSDKConfig {
  authServiceUrl: string;
  dataServiceUrl: string;
  privacyServiceUrl: string;
  blockchainServiceUrl: string;
}

// ============================================================================
// Clinical Outcomes Module
// ============================================================================

/**
 * Clinical Outcomes Module - Demonstrates proper Abena SDK usage
 * 
 * This module shows the correct pattern for integrating with the Abena IHR system:
 * - Uses Abena SDK for authentication, data access, privacy, and audit logging
 * - Focuses on business logic rather than infrastructure concerns
 * - Automatically handles security, encryption, and compliance
 */
class ClinicalOutcomesModule {

  private abena: AbenaSDK;

  constructor(config?: Partial<AbenaSDKConfig>) {
    // ✅ Correct - Uses Abena SDK instead of custom implementations
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001', 
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003',
      ...config
    });
  }

  /**
   * Get patient's latest clinical outcomes data
   * @param patientId - Patient identifier
   * @param userId - User requesting the data
   * @returns Patient outcomes data
   */
  async getPatientOutcomes(patientId: string, userId: string): Promise<any> {
    try {
      // 1. Auto-handled auth & permissions
      const patientData: PatientData = await this.abena.getPatientData(patientId, 'clinical_outcomes_analysis');
      
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
   * @param patientId - Patient identifier
   * @param userId - User recording the assessment
   * @param assessmentData - Pain assessment data
   * @returns Recorded assessment
   */
  async recordPainAssessment(
    patientId: string, 
    userId: string, 
    assessmentData: PainAssessmentData
  ): Promise<{ success: boolean; assessmentId: string; recordedAt: string; message: string }> {
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
   * @param patientId - Patient identifier
   * @param userId - User requesting the data
   * @param outcomeType - Type of outcome to analyze
   * @returns Progress analysis
   */
  async getPatientProgress(
    patientId: string, 
    userId: string, 
    outcomeType: string = 'pain'
  ): Promise<ProgressAnalysis | { error: string }> {
    try {
      // Auto-handled auth & permissions
      const historicalData: PatientData = await this.abena.getPatientData(patientId, 'outcome_progress_analysis');
      
      // Focus on business logic
      return this.analyzeProgress(historicalData, outcomeType);
    } catch (error) {
      console.error('Error analyzing patient progress:', error);
      throw new Error(`Failed to analyze progress for patient ${patientId}`);
    }
  }

  /**
   * Generate clinical outcomes report
   * @param patientId - Patient identifier
   * @param userId - User requesting the report
   * @param reportOptions - Report configuration
   * @returns Clinical report
   */
  async generateClinicalReport(
    patientId: string, 
    userId: string, 
    reportOptions: any = {}
  ): Promise<ClinicalReport> {
    try {
      // Auto-handled auth & permissions
      const patientData: PatientData = await this.abena.getPatientData(patientId, 'clinical_report_generation');
      
      // Focus on business logic
      return this.generateReport(patientData, reportOptions);
    } catch (error) {
      console.error('Error generating clinical report:', error);
      throw new Error(`Failed to generate report for patient ${patientId}`);
    }
  }

  /**
   * Update patient treatment plan based on outcomes
   * @param patientId - Patient identifier
   * @param userId - User updating the plan
   * @param treatmentPlan - New treatment plan
   * @returns Updated treatment plan
   */
  async updateTreatmentPlan(
    patientId: string, 
    userId: string, 
    treatmentPlan: TreatmentPlan
  ): Promise<{ success: boolean; planId: string; updatedAt: string; message: string }> {
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
  private processOutcomesData(patientData: PatientData): any {
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
  private validatePainAssessment(assessmentData: PainAssessmentData): void {
    const required: (keyof PainAssessmentData)[] = ['current_pain', 'average_pain_24h', 'worst_pain_24h', 'least_pain_24h'];
    const missing = required.filter(field => !assessmentData[field]);
    
    if (missing.length > 0) {
      throw new Error(`Missing required fields: ${missing.join(', ')}`);
    }
    
    // Validate pain scores (0-10 scale)
    const painFields: (keyof PainAssessmentData)[] = ['current_pain', 'average_pain_24h', 'worst_pain_24h', 'least_pain_24h'];
    painFields.forEach(field => {
      const value = assessmentData[field];
      if (typeof value === 'number' && (value < 0 || value > 10)) {
        throw new Error(`${field} must be between 0 and 10`);
      }
    });
  }

  /**
   * Analyze patient progress over time
   * @private
   */
  private analyzeProgress(historicalData: PatientData, outcomeType: string): ProgressAnalysis | { error: string } {
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
  private generateReport(patientData: PatientData, options: any): ClinicalReport {
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
  private validateTreatmentPlan(treatmentPlan: TreatmentPlan): void {
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

  private extractLatestAssessments(patientData: PatientData): Assessment | null {
    // Implementation for extracting latest assessments
    return patientData.assessments?.slice(-1)[0] || null;
  }

  private calculateTrends(patientData: PatientData): { pain: string; function: string; quality: string } {
    // Implementation for calculating trends
    return {
      pain: 'improving',
      function: 'stable',
      quality: 'improving'
    };
  }

  private generateRecommendations(patientData: PatientData): string[] {
    // Implementation for generating recommendations
    return [
      'Continue current treatment plan',
      'Schedule follow-up in 4 weeks',
      'Consider physical therapy referral'
    ];
  }

  private findBaselineAssessment(data: PatientData, outcomeType: string): Assessment | undefined {
    // Implementation for finding baseline assessment
    return data.assessments?.find(a => a.timing === 'baseline' && a.type === outcomeType);
  }

  private findCurrentAssessment(data: PatientData, outcomeType: string): Assessment | undefined {
    // Implementation for finding current assessment
    return data.assessments?.slice(-1).find(a => a.type === outcomeType);
  }

  private determineTrend(baseline: number, current: number): 'improving' | 'worsening' | 'stable' {
    const change = baseline - current;
    if (change > 0.5) return 'improving';
    if (change < -0.5) return 'worsening';
    return 'stable';
  }

  private generateSummary(patientData: PatientData): ReportSummary {
    // Implementation for generating summary
    return {
      totalAssessments: patientData.assessments?.length || 0,
      lastAssessment: patientData.assessments?.slice(-1)[0]?.date,
      overallStatus: 'stable'
    };
  }

  private generateDetails(patientData: PatientData, options: any): ReportDetails {
    // Implementation for generating detailed report
    return {
      painAssessments: patientData.assessments?.filter(a => a.type === 'pain') || [],
      functionalAssessments: patientData.assessments?.filter(a => a.type === 'function') || [],
      qualityOfLife: patientData.assessments?.filter(a => a.type === 'qol') || []
    };
  }

  private formatAssessmentResult(result: any): { success: boolean; assessmentId: string; recordedAt: string; message: string } {
    return {
      success: true,
      assessmentId: result.id,
      recordedAt: result.recorded_at,
      message: 'Pain assessment recorded successfully'
    };
  }

  private formatTreatmentPlanResult(result: any): { success: boolean; planId: string; updatedAt: string; message: string } {
    return {
      success: true,
      planId: result.id,
      updatedAt: result.updated_at,
      message: 'Treatment plan updated successfully'
    };
  }
}

export default ClinicalOutcomesModule;
export type {
  PainAssessmentData,
  TreatmentPlan,
  TreatmentIntervention,
  TreatmentGoal,
  PatientData,
  Assessment,
  ProgressAnalysis,
  ClinicalReport,
  ReportSummary,
  ReportDetails,
  AbenaSDKConfig
}; 