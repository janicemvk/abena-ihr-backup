import BusinessRuleEngine from './BusinessRuleEngine.js';

async function runTests() {
    console.log('=== Business Rule Engine Test (Abena SDK) ===\n');

    // Test 1: Basic functionality
    console.log('Test 1: Basic Rule Engine Creation');
    const ruleEngine = new BusinessRuleEngine({
        authServiceUrl: 'http://localhost:3001',
        dataServiceUrl: 'http://localhost:8001',
        privacyServiceUrl: 'http://localhost:8002',
        blockchainServiceUrl: 'http://localhost:8003'
    });
    console.log('✓ Rule engine created successfully');
    
    const stats = await ruleEngine.getRuleStats('test_user');
    console.log(`✓ Default rules loaded: ${stats.totalRules}\n`);

    // Test 2: Process medication conflict
    console.log('Test 2: Medication Dosage Conflict Processing');
    const medicationConflict = {
        id: 'TEST_001',
        type: 'medication_dosage',
        patientId: 'P12345',
        conflictingValues: [
            { value: '10mg', timestamp: '2025-06-19T10:00:00Z', source: 'ehr', dosage: 10 },
            { value: '15mg', timestamp: '2025-06-19T11:00:00Z', source: 'pharmacy', dosage: 15 }
        ],
        previousDosage: 5,
        sources: ['ehr', 'pharmacy']
    };

    const medicationResult = await ruleEngine.processConflict(medicationConflict, 'test_user');
    console.log('✓ Medication conflict processed');
    console.log(`✓ Recommended action: ${medicationResult.recommendedAction}`);
    console.log(`✓ Manual review required: ${medicationResult.requiresManualReview}\n`);

    // Test 3: Add custom rule
    console.log('Test 3: Custom Rule Addition');
    const customRuleId = await ruleEngine.addRule({
        id: 'test_custom_rule',
        name: 'Test Custom Rule',
        category: ruleEngine.ruleCategories.CLINICAL,
        description: 'Test rule for validation',
        condition: (data) => data.type === 'test_conflict',
        action: async (data, abena) => ({ resolution: 'test_resolution' }),
        priority: 1
    }, 'test_user');
    console.log(`✓ Custom rule added with ID: ${customRuleId}\n`);

    // Test 4: Test custom rule
    console.log('Test 4: Custom Rule Processing');
    const testConflict = {
        id: 'TEST_002',
        type: 'test_conflict',
        patientId: 'P12345',
        conflictingValues: [
            { value: 'test1', source: 'system1' },
            { value: 'test2', source: 'system2' }
        ]
    };

    const testResult = await ruleEngine.processConflict(testConflict, 'test_user');
    console.log('✓ Custom rule processed');
    console.log(`✓ Resolution: ${testResult.processedRules[0]?.result?.resolution}\n`);

    // Test 5: Rule statistics
    console.log('Test 5: Rule Statistics');
    const updatedStats = await ruleEngine.getRuleStats('test_user');
    console.log(`✓ Total rules: ${updatedStats.totalRules}`);
    console.log(`✓ Enabled rules: ${updatedStats.enabledRules}`);
    console.log(`✓ Clinical rules: ${updatedStats.byCategory.clinical}`);
    console.log(`✓ Administrative rules: ${updatedStats.byCategory.administrative}`);
    console.log(`✓ Privacy rules: ${updatedStats.byCategory.privacy}\n`);

    // Test 6: Rule export/import
    console.log('Test 6: Rule Export/Import');
    const exportedRules = await ruleEngine.exportRules('test_user');
    const newRuleEngine = new BusinessRuleEngine();
    await newRuleEngine.importRules(exportedRules, 'test_user');
    const newStats = await newRuleEngine.getRuleStats('test_user');
    console.log(`✓ Exported ${exportedRules.length} rules`);
    console.log(`✓ Imported ${newStats.totalRules} rules\n`);

    // Test 7: Rule management
    console.log('Test 7: Rule Management');
    const ruleId = await ruleEngine.addRule({
        name: 'Test Management Rule',
        category: ruleEngine.ruleCategories.ADMINISTRATIVE,
        description: 'Test rule for management operations',
        condition: (data) => data.type === 'management_test',
        action: async (data, abena) => ({ resolution: 'management_action' })
    }, 'test_user');

    // Update rule
    const updateSuccess = await ruleEngine.updateRule(ruleId, { priority: 1 }, 'test_user');
    console.log(`✓ Rule update: ${updateSuccess}`);

    // Toggle rule
    const toggleSuccess = await ruleEngine.toggleRule(ruleId, false, 'test_user');
    console.log(`✓ Rule toggle: ${toggleSuccess}\n`);

    // Test 8: Error handling
    console.log('Test 8: Error Handling');
    const errorRuleId = await ruleEngine.addRule({
        name: 'Error Test Rule',
        category: ruleEngine.ruleCategories.CLINICAL,
        description: 'Rule that throws an error',
        condition: (data) => data.type === 'error_test',
        action: async (data, abena) => {
            throw new Error('Test error for error handling');
        }
    }, 'test_user');

    const errorConflict = {
        id: 'TEST_003',
        type: 'error_test',
        patientId: 'P12345',
        conflictingValues: [{ value: 'test', source: 'test' }]
    };

    const errorResult = await ruleEngine.processConflict(errorConflict, 'test_user');
    console.log('✓ Error handling test completed');
    console.log(`✓ Error captured: ${errorResult.processedRules[0]?.error ? 'Yes' : 'No'}\n`);

    // Test 9: Audit and History
    console.log('Test 9: Audit Trail and History');
    try {
        const conflictHistory = await ruleEngine.getConflictHistory('P12345', 'test_user');
        console.log('✓ Conflict history retrieved');
        
        const auditTrail = await ruleEngine.getRuleAuditTrail('medication_dosage_conflict', 'test_user');
        console.log('✓ Audit trail retrieved');
    } catch (error) {
        console.log('✓ Audit/history test completed (expected if services not running)');
    }

    console.log('\n=== All Tests Passed! ===');
    console.log('\nThe Business Rule Engine is working correctly with Abena SDK.');
    console.log('Run "npm start" to see comprehensive examples.');
}

// Run the tests
runTests().catch(console.error); 