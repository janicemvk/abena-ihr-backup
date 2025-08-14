import ClinicalOutcomesModule from './ClinicalOutcomesModule.js';

/**
 * Usage Example - Demonstrating the Correct Abena SDK Pattern
 * 
 * This example shows how to use the ClinicalOutcomesModule that follows
 * the proper Abena SDK integration pattern instead of custom auth/database handling.
 */

// ============================================================================
// Module Initialization
// ============================================================================

// ✅ Correct - Initialize with Abena SDK configuration
const clinicalModule = new ClinicalOutcomesModule({
  authServiceUrl: 'http://localhost:3001',
  dataServiceUrl: 'http://localhost:8001',
  privacyServiceUrl: 'http://localhost:8002',
  blockchainServiceUrl: 'http://localhost:8003'
});

// ============================================================================
// Example Usage Scenarios
// ============================================================================

/**
 * Example 1: Get Patient Outcomes
 * Demonstrates automatic auth, privacy, and audit handling
 */
async function exampleGetPatientOutcomes() {
  try {
    console.log('=== Example 1: Get Patient Outcomes ===');
    
    const patientId = 'PATIENT_001';
    const userId = 'DR_SMITH';
    
    // ✅ Correct - Auto-handled auth & permissions
    const outcomes = await clinicalModule.getPatientOutcomes(patientId, userId);
    
    console.log('Patient Outcomes:', outcomes);
    console.log('✅ Auth, privacy, and audit logging handled automatically');
    
  } catch (error) {
    console.error('❌ Error getting patient outcomes:', error.message);
  }
}

/**
 * Example 2: Record Pain Assessment
 * Demonstrates data validation and automatic audit logging
 */
async function exampleRecordPainAssessment() {
  try {
    console.log('\n=== Example 2: Record Pain Assessment ===');
    
    const patientId = 'PATIENT_001';
    const userId = 'DR_SMITH';
    
    const assessmentData = {
      current_pain: 6.5,
      average_pain_24h: 6.0,
      worst_pain_24h: 8.0,
      least_pain_24h: 4.0,
      pain_interference: 6.5,
      pain_at_rest: 4.5,
      pain_with_movement: 7.5,
      pain_locations: ['right_knee', 'left_knee'],
      pain_quality: ['aching'],
      notes: 'Patient reports improvement with current treatment'
    };
    
    // ✅ Correct - Auto-handled validation, auth, privacy, and audit
    const result = await clinicalModule.recordPainAssessment(patientId, userId, assessmentData);
    
    console.log('Assessment Result:', result);
    console.log('✅ Data validation, auth, privacy, and audit handled automatically');
    
  } catch (error) {
    console.error('❌ Error recording pain assessment:', error.message);
  }
}

/**
 * Example 3: Get Patient Progress
 * Demonstrates progress analysis with automatic data access
 */
async function exampleGetPatientProgress() {
  try {
    console.log('\n=== Example 3: Get Patient Progress ===');
    
    const patientId = 'PATIENT_001';
    const userId = 'DR_SMITH';
    const outcomeType = 'pain';
    
    // ✅ Correct - Auto-handled auth & permissions for historical data
    const progress = await clinicalModule.getPatientProgress(patientId, userId, outcomeType);
    
    console.log('Progress Analysis:', progress);
    console.log('✅ Historical data access, auth, and permissions handled automatically');
    
  } catch (error) {
    console.error('❌ Error getting patient progress:', error.message);
  }
}

/**
 * Example 4: Generate Clinical Report
 * Demonstrates comprehensive report generation
 */
async function exampleGenerateClinicalReport() {
  try {
    console.log('\n=== Example 4: Generate Clinical Report ===');
    
    const patientId = 'PATIENT_001';
    const userId = 'DR_SMITH';
    const reportOptions = {
      includeTrends: true,
      includeRecommendations: true,
      format: 'detailed'
    };
    
    // ✅ Correct - Auto-handled auth & permissions for report generation
    const report = await clinicalModule.generateClinicalReport(patientId, userId, reportOptions);
    
    console.log('Clinical Report:', JSON.stringify(report, null, 2));
    console.log('✅ Report generation with auth and permissions handled automatically');
    
  } catch (error) {
    console.error('❌ Error generating clinical report:', error.message);
  }
}

/**
 * Example 5: Update Treatment Plan
 * Demonstrates treatment plan updates with validation
 */
async function exampleUpdateTreatmentPlan() {
  try {
    console.log('\n=== Example 5: Update Treatment Plan ===');
    
    const patientId = 'PATIENT_001';
    const userId = 'DR_SMITH';
    
    const treatmentPlan = {
      interventions: [
        {
          type: 'medication',
          name: 'Ibuprofen',
          description: 'Anti-inflammatory medication',
          frequency: 'TID',
          duration: '4 weeks'
        },
        {
          type: 'physical_therapy',
          name: 'Knee strengthening exercises',
          description: 'Progressive resistance training',
          frequency: '3x/week',
          duration: '8 weeks'
        }
      ],
      goals: [
        {
          description: 'Reduce pain score to 4 or below',
          target_value: 4.0,
          timeframe_weeks: 8,
          measurable: true
        },
        {
          description: 'Improve knee function for daily activities',
          timeframe_weeks: 12,
          measurable: false
        }
      ],
      duration_weeks: 12,
      notes: 'Updated based on recent pain assessment showing improvement'
    };
    
    // ✅ Correct - Auto-handled validation, auth, privacy, and audit
    const result = await clinicalModule.updateTreatmentPlan(patientId, userId, treatmentPlan);
    
    console.log('Treatment Plan Update Result:', result);
    console.log('✅ Validation, auth, privacy, and audit handled automatically');
    
  } catch (error) {
    console.error('❌ Error updating treatment plan:', error.message);
  }
}

// ============================================================================
// Run Examples
// ============================================================================

async function runAllExamples() {
  console.log('🚀 Abena SDK Integration Examples');
  console.log('=====================================\n');
  
  await exampleGetPatientOutcomes();
  await exampleRecordPainAssessment();
  await exampleGetPatientProgress();
  await exampleGenerateClinicalReport();
  await exampleUpdateTreatmentPlan();
  
  console.log('\n✅ All examples completed successfully!');
  console.log('\n📋 Key Benefits of Abena SDK Pattern:');
  console.log('   • Automatic authentication and authorization');
  console.log('   • Built-in privacy protection and encryption');
  console.log('   • Comprehensive audit logging');
  console.log('   • Focus on business logic, not infrastructure');
  console.log('   • Consistent security and compliance');
}

// Run the examples
runAllExamples().catch(console.error); 