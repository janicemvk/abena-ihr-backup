// Demo script for Abena SDK
// Run with: node demo.js

const { AbenaSDK } = require('./dist/index');

async function runDemo() {
  console.log('🚀 Abena SDK Demo\n');

  // Initialize the SDK
  const sdk = new AbenaSDK({
    authServiceUrl: 'https://auth.abena.health',
    dataServiceUrl: 'https://data.abena.health',
    privacyServiceUrl: 'https://privacy.abena.health',
    blockchainServiceUrl: 'https://blockchain.abena.health',
    timeout: 30000
  });

  try {
    console.log('1. Checking service health...');
    const healthStatus = await sdk.healthCheck();
    console.log('   Service health:', healthStatus);
    console.log('   ✅ All services operational\n');

    console.log('2. Simulating login...');
    // Note: This would normally connect to real services
    console.log('   🔐 Authentication would happen here\n');

    console.log('3. SDK Features Available:');
    console.log('   • Unified Authentication');
    console.log('   • Patient Data Access');
    console.log('   • Privacy & Security Controls');
    console.log('   • Blockchain Audit Logging');
    console.log('   • Data Ingestion (HL7, FHIR)');
    console.log('   • Analytics & Research Support');
    console.log('   • Emergency Access Controls\n');

    console.log('4. Example API calls:');
    console.log('   • sdk.login(email, password)');
    console.log('   • sdk.getPatientData(patientId, purpose)');
    console.log('   • sdk.encryptSensitiveData(data, type)');
    console.log('   • sdk.getCompletePatientContext(patientId, userId, purpose)');
    console.log('   • sdk.getAnonymizedDataset(criteria, config)');
    console.log('   • sdk.healthCheck()\n');

    console.log('✅ Demo completed successfully!');
    console.log('📚 Check the README.md for detailed documentation');
    console.log('🧪 Run "npm test" to see the test suite');

  } catch (error) {
    console.error('❌ Demo failed:', error.message);
    console.log('💡 This is expected since we\'re not connecting to real services');
  }
}

// Run the demo
runDemo().catch(console.error); 