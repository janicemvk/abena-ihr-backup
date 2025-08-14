import BusinessRuleEngine from './BusinessRuleEngine.js';

// Create a new instance of the Business Rule Engine with Abena SDK
const ruleEngine = new BusinessRuleEngine({
    authServiceUrl: 'http://localhost:3001',
    dataServiceUrl: 'http://localhost:8001',
    privacyServiceUrl: 'http://localhost:8002',
    blockchainServiceUrl: 'http://localhost:8003'
});

// Example user ID for demonstration
const userId = 'USER_12345';

async function runExamples() {
    console.log('=== Business Rule Engine Demo (Abena SDK) ===\n');

    // Example 1: Medication Dosage Conflict
    console.log('1. Processing Medication Dosage Conflict:');
    const medicationConflict = {
        id: 'CONFLICT_001',
        type: 'medication_dosage',
        patientId: 'P12345',
        field: 'dosage',
        conflictingValues: [
            { value: '10mg', timestamp: '2025-06-19T10:00:00Z', source: 'ehr', dosage: 10 },
            { value: '15mg', timestamp: '2025-06-19T11:00:00Z', source: 'pharmacy', dosage: 15 }
        ],
        previousDosage: 5,
        sources: ['ehr', 'pharmacy']
    };

    const medicationResult = await ruleEngine.processConflict(medicationConflict, userId);
    console.log('Result:', JSON.stringify(medicationResult, null, 2));
    console.log('\n' + '='.repeat(50) + '\n');

    // Example 2: Lab Result Conflict
    console.log('2. Processing Lab Result Conflict:');
    const labConflict = {
        id: 'CONFLICT_002',
        type: 'lab_result',
        patientId: 'P12345',
        field: 'glucose_level',
        conflictingValues: [
            { value: '120', timestamp: '2025-06-19T09:00:00Z', source: 'lab_system' },
            { value: '125', timestamp: '2025-06-19T09:30:00Z', source: 'ehr' },
            { value: '118', timestamp: '2025-06-19T10:00:00Z', source: 'manual_entry' }
        ],
        sources: ['lab_system', 'ehr', 'manual_entry']
    };

    const labResult = await ruleEngine.processConflict(labConflict, userId);
    console.log('Result:', JSON.stringify(labResult, null, 2));
    console.log('\n' + '='.repeat(50) + '\n');

    // Example 3: Patient Demographics Conflict (Critical Field)
    console.log('3. Processing Patient Demographics Conflict (Critical Field):');
    const demoConflictCritical = {
        id: 'CONFLICT_003',
        type: 'patient_demographics',
        patientId: 'P12345',
        field: 'dateOfBirth',
        conflictingValues: [
            { value: '1985-03-15', lastUpdated: '2025-06-19T08:00:00Z', source: 'registration' },
            { value: '1985-03-20', lastUpdated: '2025-06-19T09:00:00Z', source: 'insurance' }
        ],
        sources: ['registration', 'insurance']
    };

    const demoResultCritical = await ruleEngine.processConflict(demoConflictCritical, userId);
    console.log('Result:', JSON.stringify(demoResultCritical, null, 2));
    console.log('\n' + '='.repeat(50) + '\n');

    // Example 4: Patient Demographics Conflict (Non-Critical Field)
    console.log('4. Processing Patient Demographics Conflict (Non-Critical Field):');
    const demoConflictNonCritical = {
        id: 'CONFLICT_004',
        type: 'patient_demographics',
        patientId: 'P12345',
        field: 'phoneNumber',
        conflictingValues: [
            { value: '555-123-4567', lastUpdated: '2025-06-19T08:00:00Z', source: 'registration' },
            { value: '555-123-4568', lastUpdated: '2025-06-19T10:00:00Z', source: 'ehr' }
        ],
        sources: ['registration', 'ehr']
    };

    const demoResultNonCritical = await ruleEngine.processConflict(demoConflictNonCritical, userId);
    console.log('Result:', JSON.stringify(demoResultNonCritical, null, 2));
    console.log('\n' + '='.repeat(50) + '\n');

    // Example 5: Privacy Consent Conflict
    console.log('5. Processing Privacy Consent Conflict:');
    const privacyConflict = {
        id: 'CONFLICT_005',
        type: 'privacy_consent',
        patientId: 'P12345',
        field: 'dataSharingConsent',
        conflictingValues: [
            { value: 'full', restrictionLevel: 1, source: 'patient_portal' },
            { value: 'limited', restrictionLevel: 3, source: 'registration' },
            { value: 'none', restrictionLevel: 5, source: 'legal' }
        ],
        sources: ['patient_portal', 'registration', 'legal']
    };

    const privacyResult = await ruleEngine.processConflict(privacyConflict, userId);
    console.log('Result:', JSON.stringify(privacyResult, null, 2));
    console.log('\n' + '='.repeat(50) + '\n');

    // Example 6: Adding a Custom Rule
    console.log('6. Adding and Testing a Custom Rule:');
    const customRuleId = await ruleEngine.addRule({
        id: 'custom_allergy_conflict',
        name: 'Allergy Conflict Resolution',
        category: ruleEngine.ruleCategories.CLINICAL,
        description: 'Handle conflicts in patient allergy information',
        condition: (data) => data.type === 'allergy',
        action: async (data, abena) => {
            // Get patient allergy history with privacy controls
            const patientAllergyHistory = await abena.getPatientData(data.patientId, 'allergy_conflict_resolution');
            
            // Always prefer the most comprehensive allergy list
            const mostComprehensive = data.conflictingValues.reduce((comprehensive, current) => 
                current.allergens.length > comprehensive.allergens.length ? current : comprehensive
            );
            return {
                resolution: 'use_most_comprehensive',
                selectedValue: mostComprehensive,
                requiresManualReview: false,
                reason: 'Using most comprehensive allergy list for patient safety'
            };
        },
        priority: 1,
        metadata: {
            conflictTypes: ['allergy'],
            dataSources: ['ehr', 'pharmacy', 'patient_input']
        }
    }, userId);

    console.log(`Custom rule added with ID: ${customRuleId}`);

    // Test the custom rule
    const allergyConflict = {
        id: 'CONFLICT_006',
        type: 'allergy',
        patientId: 'P12345',
        field: 'allergies',
        conflictingValues: [
            { value: 'Penicillin', allergens: ['penicillin'], source: 'ehr' },
            { value: 'Penicillin, Sulfa', allergens: ['penicillin', 'sulfa'], source: 'pharmacy' }
        ],
        sources: ['ehr', 'pharmacy']
    };

    const allergyResult = await ruleEngine.processConflict(allergyConflict, userId);
    console.log('Custom Rule Result:', JSON.stringify(allergyResult, null, 2));
    console.log('\n' + '='.repeat(50) + '\n');

    // Example 7: Rule Statistics
    console.log('7. Rule Engine Statistics:');
    const stats = await ruleEngine.getRuleStats(userId);
    console.log('Statistics:', JSON.stringify(stats, null, 2));

    // Get rules by category
    console.log('\nClinical Rules:');
    const clinicalRules = await ruleEngine.getRulesByCategory(ruleEngine.ruleCategories.CLINICAL, userId);
    clinicalRules.forEach(rule => {
        console.log(`- ${rule.name} (${rule.id})`);
    });

    console.log('\n' + '='.repeat(50) + '\n');

    // Example 8: Export/Import Rules
    console.log('8. Exporting and Importing Rules:');
    const exportedRules = await ruleEngine.exportRules(userId);
    console.log(`Exported ${exportedRules.length} rules`);

    // Create a new engine instance and import rules
    const newRuleEngine = new BusinessRuleEngine();
    await newRuleEngine.importRules(exportedRules, userId);
    const newStats = await newRuleEngine.getRuleStats(userId);
    console.log(`Imported ${newStats.totalRules} rules into new engine`);

    console.log('\n' + '='.repeat(50) + '\n');

    // Example 9: Rule Management
    console.log('9. Rule Management Operations:');
    const managementRuleId = await ruleEngine.addRule({
        name: 'Test Management Rule',
        category: ruleEngine.ruleCategories.ADMINISTRATIVE,
        description: 'Test rule for management operations',
        condition: (data) => data.type === 'management_test',
        action: async (data, abena) => ({ resolution: 'management_action' })
    }, userId);

    // Update rule
    const updateSuccess = await ruleEngine.updateRule(managementRuleId, { priority: 1 }, userId);
    console.log(`✓ Rule update: ${updateSuccess}`);

    // Toggle rule
    const toggleSuccess = await ruleEngine.toggleRule(managementRuleId, false, userId);
    console.log(`✓ Rule toggle: ${toggleSuccess}`);

    console.log('\n' + '='.repeat(50) + '\n');

    // Example 10: Audit and History
    console.log('10. Audit Trail and History:');
    
    // Get conflict history for a patient
    const conflictHistory = await ruleEngine.getConflictHistory('P12345', userId);
    console.log(`✓ Retrieved conflict history for patient P12345`);

    // Get audit trail for a rule
    const auditTrail = await ruleEngine.getRuleAuditTrail('medication_dosage_conflict', userId);
    console.log(`✓ Retrieved audit trail for medication dosage rule`);

    console.log('\n=== Demo Complete ===');
}

// Run the examples
runExamples().catch(console.error); 