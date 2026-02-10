// Demo script for Conflict Alert/Review Module
// Demonstrates various healthcare conflict scenarios and module functionality
// Uses Abena SDK for authentication, authorization, and data handling

import ConflictAlertModule from './ConflictAlertModule.js';
import MockAbenaSDK from './mocks/AbenaSDK.js';

/**
 * Demo script for the Abena IHR Conflict Alert Module
 * 
 * This demo showcases the module's capabilities with Abena SDK integration
 * Uses Abena SDK for authentication, authorization, and data handling
 */

console.log('🏥 Abena IHR Conflict Alert Module Demo\n');

// Demo user IDs
const DEMO_USERS = {
    DR001: 'DR001',
    DR_SMITH: 'DR_SMITH',
    LAB001: 'LAB001',
    LAB_SUPERVISOR: 'LAB_SUPERVISOR',
    ADMIN001: 'ADMIN001',
    DATA001: 'DATA001'
};

async function runDemo() {
    try {
        // Initialize the conflict alert module with Abena SDK
        const conflictAlerts = new ConflictAlertModule({
            alertExpiryDays: 30,
            escalationThreshold: 24,
            abenaSDK: {
                authServiceUrl: 'http://localhost:3001',
                dataServiceUrl: 'http://localhost:8001',
                privacyServiceUrl: 'http://localhost:8002',
                blockchainServiceUrl: 'http://localhost:8003'
            }
        });

        console.log('📋 Creating sample alerts...\n');

        // Critical priority alert - Medication dosage conflict
        const criticalAlert = await conflictAlerts.createAlert({
            patientId: 'P12345',
            conflictType: 'medication_dosage',
            description: 'Inconsistent medication dosage between pharmacy and physician orders',
            severity: 'critical',
            notes: ['Dosage discrepancy detected: Pharmacy shows 20mg, Physician ordered 10mg']
        }, DEMO_USERS.DR001);

        // High priority alert - Lab results conflict
        const highPriorityAlert = await conflictAlerts.createAlert({
            patientId: 'P12346',
            conflictType: 'lab_results',
            description: 'Conflicting lab results between different testing facilities',
            severity: 'warning',
            notes: ['Results from Lab A: 150 mg/dL, Results from Lab B: 180 mg/dL']
        }, DEMO_USERS.LAB001);

        // Medium priority alert - Patient demographic conflict
        const mediumAlert = await conflictAlerts.createAlert({
            patientId: 'P12347',
            conflictType: 'demographics',
            description: 'Inconsistent patient demographic information across systems',
            severity: 'warning',
            notes: ['Date of birth differs between registration and insurance systems']
        }, DEMO_USERS.ADMIN001);

        // Low priority alert - Duplicate record
        const lowAlert = await conflictAlerts.createAlert({
            patientId: 'P12348',
            conflictType: 'duplicate_record',
            description: 'Potential duplicate patient record detected',
            severity: 'info',
            notes: ['Similar patient information found in multiple records']
        }, DEMO_USERS.DATA001);

        console.log('✅ Sample alerts created successfully!\n');

        // Demo 2: Subscribe to alerts
        console.log('🔔 Setting up alert subscriptions...\n');

        // Subscribe to critical alerts
        const criticalSubscription = await conflictAlerts.subscribeToAlerts({ type: 'critical' }, DEMO_USERS.DR001);

        // Subscribe to medication-related alerts
        const medicationSubscription = await conflictAlerts.subscribeToAlerts({ priority: 'high' }, DEMO_USERS.DR_SMITH);

        console.log('✅ Alert subscriptions active!\n');

        // Demo 3: Assign and manage alerts
        console.log('👥 Managing alerts...\n');

        // Assign critical alert to physician
        await conflictAlerts.assignAlert(criticalAlert.id, DEMO_USERS.DR_SMITH, DEMO_USERS.DR001);

        // Assign high priority alert to lab supervisor
        await conflictAlerts.assignAlert(highPriorityAlert.id, DEMO_USERS.LAB_SUPERVISOR, DEMO_USERS.LAB001);

        // Get alerts for specific user (using filters)
        const drSmithAlerts = await conflictAlerts.getAlerts({ assignedTo: DEMO_USERS.DR_SMITH }, DEMO_USERS.DR_SMITH);
        console.log(`👨‍⚕️ Dr. Smith has ${drSmithAlerts.length} assigned alerts\n`);

        // Demo 4: Review and resolve alerts
        console.log('✅ Reviewing and resolving alerts...\n');

        // Mark critical alert as in review
        await conflictAlerts.updateAlertStatus(
            criticalAlert.id, 
            'in_review', 
            DEMO_USERS.DR_SMITH, 
            'Dosage corrected in pharmacy system - Verified with pharmacist and updated dosage to 10mg daily'
        );

        // Resolve the alert
        await conflictAlerts.resolveAlert(
            criticalAlert.id,
            'Medication dosage conflict resolved by updating pharmacy system with correct dosage',
            DEMO_USERS.DR_SMITH
        );

        // Escalate medium priority alert
        await conflictAlerts.escalateAlert(
            mediumAlert.id,
            'Patient unavailable for verification, requires supervisor review',
            DEMO_USERS.ADMIN001
        );

        console.log('✅ Alert management completed!\n');

        // Demo 5: Get statistics and reports
        console.log('📊 Generating statistics...\n');

        const stats = await conflictAlerts.getStatistics({}, DEMO_USERS.ADMIN001);
        console.log('📈 Alert Statistics:');
        console.log(`   Total Alerts: ${stats.total}`);
        console.log(`   Open: ${stats.byStatus.open || 0}`);
        console.log(`   Assigned: ${stats.byStatus.assigned || 0}`);
        console.log(`   In Review: ${stats.byStatus.in_review || 0}`);
        console.log(`   Resolved: ${stats.byStatus.resolved || 0}`);
        console.log(`   Escalated: ${stats.byStatus.escalated || 0}`);
        console.log(`   Recent Activity: ${stats.recentActivity}`);
        console.log(`   Average Resolution Time: ${Math.round(stats.averageResolutionTime)} hours`);

        console.log('\n📊 By Type:');
        Object.entries(stats.byType).forEach(([type, count]) => {
            console.log(`   ${type}: ${count}`);
        });

        console.log('\n📊 By Severity:');
        Object.entries(stats.bySeverity).forEach(([severity, count]) => {
            console.log(`   ${severity}: ${count}`);
        });

        console.log('\n');

        // Demo 6: Patient-specific alerts
        console.log('👤 Patient-specific alert retrieval...\n');

        const patientAlerts = await conflictAlerts.getPatientAlerts('P12345', DEMO_USERS.DR001);
        console.log(`📋 Patient P12345 has ${patientAlerts.length} alerts:`);
        patientAlerts.forEach(alert => {
            console.log(`   - ${alert.conflictType}: ${alert.status} (${alert.severity} severity)`);
        });

        console.log('\n');

        // Demo 7: Filtered alerts
        console.log('🔍 Filtered alert retrieval...\n');

        const warningAlerts = await conflictAlerts.getAlerts({ severity: 'warning' }, DEMO_USERS.DR001);
        console.log(`⚠️ Warning severity alerts: ${warningAlerts.length}`);

        const openAlerts = await conflictAlerts.getAlerts({ status: 'open' }, DEMO_USERS.DR_SMITH);
        console.log(`⏳ Open alerts: ${openAlerts.length}`);

        console.log('\n');

        // Demo 8: Cleanup expired alerts
        console.log('🧹 Cleaning up expired alerts...\n');

        const cleanupResult = await conflictAlerts.cleanupExpiredAlerts(DEMO_USERS.ADMIN001);
        console.log(`🗑️ Cleanup result: ${cleanupResult.cleanedCount} alerts cleaned`);

        console.log('\n');

        // Demo 9: Unsubscribe from alerts
        console.log('🔕 Unsubscribing from alerts...\n');

        await conflictAlerts.unsubscribeFromAlerts(criticalSubscription, DEMO_USERS.DR001);
        await conflictAlerts.unsubscribeFromAlerts(medicationSubscription, DEMO_USERS.DR_SMITH);

        console.log('✅ Unsubscribed from alert notifications\n');

        // Demo 10: Error handling demonstration
        console.log('⚠️ Error handling demonstration...\n');

        try {
            // Try to create alert without required fields
            await conflictAlerts.createAlert({
                description: 'This should fail'
            }, DEMO_USERS.DR001);
        } catch (error) {
            console.log(`❌ Expected error caught: ${error.message}`);
        }

        try {
            // Try to assign non-existent alert
            await conflictAlerts.assignAlert('NON_EXISTENT_ID', DEMO_USERS.DR001, DEMO_USERS.DR001);
        } catch (error) {
            console.log(`❌ Expected error caught: ${error.message}`);
        }

        console.log('\n');

        // Final statistics
        console.log('🎯 Final Module Statistics:');
        const finalStats = await conflictAlerts.getStatistics({}, DEMO_USERS.ADMIN001);
        console.log(`   Total Alerts in System: ${finalStats.total}`);

        console.log('\n✨ Demo completed successfully!');
        console.log('🚀 The Conflict Alert Module is ready for production use.');
        console.log('📚 Check the API documentation for integration details.');
        console.log('🔐 Abena SDK: Integrated for authentication & authorization');

    } catch (error) {
        console.error('❌ Demo failed:', error.message);
        console.error('Stack trace:', error.stack);
    }
}

// Run the demo
runDemo(); 