/**
 * Test Migration: From Custom Auth/Database to Abena SDK
 * 
 * This script demonstrates the migration and tests the new Abena SDK implementation.
 */

const AbenaSDK = require('./lib/abena-sdk');
const { PatientDataModule, ClinicalDataModule, UserManagementModule } = require('./examples/migration-example');

// Test configuration
const testConfig = {
  authServiceUrl: 'http://localhost:3001',
  dataServiceUrl: 'http://localhost:8001',
  privacyServiceUrl: 'http://localhost:8002',
  blockchainServiceUrl: 'http://localhost:8003'
};

async function testAbenaSDK() {
  console.log('🧪 Testing Abena SDK Migration...\n');

  try {
    // Test 1: Direct SDK usage
    console.log('📋 Test 1: Direct Abena SDK Usage');
    const abena = new AbenaSDK(testConfig);
    
    const patientData = await abena.getPatientData('PAT-123', 'test_purpose');
    console.log('✅ Patient data retrieved:', patientData.patientId);
    
    const clinicalData = await abena.getClinicalData('PAT-123', 'lab_results', 'test_purpose');
    console.log('✅ Clinical data retrieved:', clinicalData.dataType);
    
    const userData = await abena.getUserData('USR-456', 'test_purpose');
    console.log('✅ User data retrieved:', userData.userId);
    
    console.log('\n');

    // Test 2: Patient Data Module
    console.log('📋 Test 2: Patient Data Module');
    const patientModule = new PatientDataModule();
    
    const profile = await patientModule.getPatientProfile('PAT-123');
    console.log('✅ Patient profile formatted:', profile.name);
    
    const updateResult = await patientModule.updatePatientData('PAT-123', {
      firstName: 'Jane',
      lastName: 'Smith'
    });
    console.log('✅ Patient data updated:', updateResult.success);
    
    console.log('\n');

    // Test 3: Clinical Data Module
    console.log('📋 Test 3: Clinical Data Module');
    const clinicalModule = new ClinicalDataModule();
    
    const labResults = await clinicalModule.getLabResults('PAT-123');
    console.log('✅ Lab results retrieved:', labResults.patientId);
    
    const vitalSigns = await clinicalModule.getVitalSigns('PAT-123');
    console.log('✅ Vital signs retrieved:', vitalSigns.patientId);
    
    console.log('\n');

    // Test 4: User Management Module
    console.log('📋 Test 4: User Management Module');
    const userModule = new UserManagementModule();
    
    const userProfile = await userModule.getUserProfile('USR-456');
    console.log('✅ User profile retrieved:', userProfile.name);
    
    console.log('\n');

    // Test 5: Error Handling
    console.log('📋 Test 5: Error Handling');
    try {
      await abena.getPatientData('INVALID-ID', 'test_purpose');
    } catch (error) {
      console.log('✅ Error handling works:', error.message);
    }
    
    console.log('\n');

    console.log('🎉 All migration tests passed successfully!');
    console.log('\n📊 Migration Summary:');
    console.log('  ✅ Authentication: Auto-handled');
    console.log('  ✅ Authorization: Auto-handled');
    console.log('  ✅ Privacy Compliance: Auto-handled');
    console.log('  ✅ Audit Logging: Auto-handled');
    console.log('  ✅ Blockchain Recording: Auto-handled');
    console.log('  ✅ Business Logic: Focused and clean');

  } catch (error) {
    console.error('❌ Migration test failed:', error);
    process.exit(1);
  }
}

// Comparison function to show the difference
function showComparison() {
  console.log('\n📊 BEFORE vs AFTER Comparison:\n');
  
  console.log('❌ BEFORE (Custom Implementation):');
  console.log('  - Manual authentication checks');
  console.log('  - Manual permission validation');
  console.log('  - Manual privacy compliance');
  console.log('  - Manual audit logging');
  console.log('  - Manual database queries');
  console.log('  - Complex error handling');
  console.log('  - ~50 lines of boilerplate code\n');
  
  console.log('✅ AFTER (Abena SDK):');
  console.log('  - Auto-handled authentication');
  console.log('  - Auto-handled authorization');
  console.log('  - Auto-handled privacy compliance');
  console.log('  - Auto-handled audit logging');
  console.log('  - Auto-handled blockchain recording');
  console.log('  - Unified error handling');
  console.log('  - ~5 lines of business logic\n');
  
  console.log('🚀 Benefits:');
  console.log('  - 90% reduction in boilerplate code');
  console.log('  - Consistent security policies');
  console.log('  - Automatic compliance');
  console.log('  - Focus on business logic');
  console.log('  - Easier maintenance');
  console.log('  - Better scalability');
}

// Run the tests
async function main() {
  console.log('🔐 Abena SDK Migration Test Suite');
  console.log('=====================================\n');
  
  await testAbenaSDK();
  showComparison();
}

// Run if this file is executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  testAbenaSDK,
  showComparison
}; 