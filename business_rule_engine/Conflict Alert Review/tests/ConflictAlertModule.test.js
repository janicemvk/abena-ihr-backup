// Basic tests for Conflict Alert Module with Abena SDK integration
// Run with: npm test

import ConflictAlertModule from '../src/modules/ConflictAlertModule.js';

// Mock Abena SDK for testing
jest.mock('@abena/sdk', () => {
    return jest.fn().mockImplementation(() => ({
        getPatientData: jest.fn().mockResolvedValue({ id: 'P12345', name: 'Test Patient' }),
        storeAlertData: jest.fn().mockResolvedValue(true),
        getAlertData: jest.fn().mockResolvedValue([]),
        updateAlertData: jest.fn().mockResolvedValue(true),
        deleteAlertData: jest.fn().mockResolvedValue(true),
        getUserPermissions: jest.fn().mockResolvedValue({
            canAccessAlertType: jest.fn().mockReturnValue(true),
            canAssignAlerts: true,
            canReviewAllAlerts: true,
            canResolveAlerts: true,
            canEscalateAlerts: true,
            canViewStatistics: true,
            canCleanupAlerts: true
        }),
        logActivity: jest.fn().mockResolvedValue(true),
        subscribeToNotifications: jest.fn().mockResolvedValue('sub_123'),
        unsubscribeFromNotifications: jest.fn().mockResolvedValue(true)
    }));
});

describe('ConflictAlertModule', () => {
    let conflictAlerts;
    const testUserId = 'TEST_USER_001';

    beforeEach(() => {
        conflictAlerts = new ConflictAlertModule({
            authServiceUrl: 'http://localhost:3001',
            dataServiceUrl: 'http://localhost:8001',
            privacyServiceUrl: 'http://localhost:8002',
            blockchainServiceUrl: 'http://localhost:8003'
        });
    });

    describe('Alert Creation', () => {
        test('should create a new alert with required fields', async () => {
            const alertData = {
                patientId: 'P12345',
                conflictType: 'medication_dosage',
                description: 'Test alert',
                priority: 'high'
            };

            const alert = await conflictAlerts.createAlert(alertData, testUserId);

            expect(alert).toBeDefined();
            expect(alert.patientId).toBe('P12345');
            expect(alert.conflictType).toBe('medication_dosage');
            expect(alert.priority).toBe('high');
            expect(alert.status).toBe('pending');
            expect(alert.id).toMatch(/^ALERT_\d+_/);
            expect(alert.createdBy).toBe(testUserId);
        });

        test('should throw error when required fields are missing', async () => {
            await expect(async () => {
                await conflictAlerts.createAlert({
                    description: 'Test alert without required fields'
                }, testUserId);
            }).rejects.toThrow('Patient ID and conflict type are required');
        });

        test('should determine alert type based on severity', async () => {
            const criticalAlert = await conflictAlerts.createAlert({
                patientId: 'P12345',
                conflictType: 'test',
                severity: 'critical',
                affectsPatientSafety: true
            }, testUserId);

            const warningAlert = await conflictAlerts.createAlert({
                patientId: 'P12346',
                conflictType: 'test',
                severity: 'warning'
            }, testUserId);

            expect(criticalAlert.type).toBe('critical');
            expect(warningAlert.type).toBe('warning');
        });
    });

    describe('Alert Management', () => {
        let testAlert;

        beforeEach(async () => {
            testAlert = await conflictAlerts.createAlert({
                patientId: 'P12345',
                conflictType: 'test',
                description: 'Test alert',
                priority: 'medium'
            }, testUserId);
        });

        test('should assign alert to user', async () => {
            const success = await conflictAlerts.assignAlert(testAlert.id, 'DR_SMITH', testUserId);
            
            expect(success).toBe(true);
        });

        test('should mark alert as reviewed', async () => {
            await conflictAlerts.assignAlert(testAlert.id, 'DR_SMITH', testUserId);
            
            const success = await conflictAlerts.markAsReviewed(
                testAlert.id, 
                'DR_SMITH', 
                'Test resolution',
                'Test notes'
            );
            
            expect(success).toBe(true);
        });

        test('should resolve alert', async () => {
            const success = await conflictAlerts.resolveAlert(
                testAlert.id,
                'DR_SMITH',
                'Test resolution details'
            );
            
            expect(success).toBe(true);
        });

        test('should escalate alert', async () => {
            const success = await conflictAlerts.escalateAlert(
                testAlert.id,
                'ADMIN001',
                'Test escalation reason'
            );
            
            expect(success).toBe(true);
        });
    });

    describe('Alert Retrieval', () => {
        beforeEach(async () => {
            // Create multiple alerts for testing
            await conflictAlerts.createAlert({
                patientId: 'P12345',
                conflictType: 'test1',
                description: 'Test alert 1',
                priority: 'high'
            }, 'DR001');

            await conflictAlerts.createAlert({
                patientId: 'P12346',
                conflictType: 'test2',
                description: 'Test alert 2',
                priority: 'medium'
            }, 'DR002');

            await conflictAlerts.createAlert({
                patientId: 'P12345',
                conflictType: 'test3',
                description: 'Test alert 3',
                priority: 'low'
            }, 'DR001');
        });

        test('should get alerts for specific user', async () => {
            const userAlerts = await conflictAlerts.getAlertsForUser('DR001');
            expect(userAlerts).toBeDefined();
        });

        test('should get alerts by priority', async () => {
            const highPriorityAlerts = await conflictAlerts.getAlertsByPriority('high', testUserId);
            expect(highPriorityAlerts).toBeDefined();
        });

        test('should get alerts for specific patient', async () => {
            const patientAlerts = await conflictAlerts.getAlertsForPatient('P12345', testUserId);
            expect(patientAlerts).toBeDefined();
        });

        test('should get alert by ID', async () => {
            const alert = await conflictAlerts.createAlert({
                patientId: 'P12347',
                conflictType: 'test',
                description: 'Test alert',
                priority: 'medium'
            }, testUserId);

            const retrievedAlert = await conflictAlerts.getAlertById(alert.id, testUserId);
            expect(retrievedAlert).toBeDefined();
        });
    });

    describe('Statistics', () => {
        beforeEach(async () => {
            // Create alerts with different statuses
            const alert1 = await conflictAlerts.createAlert({
                patientId: 'P12345',
                conflictType: 'test1',
                description: 'Test alert 1',
                priority: 'high'
            }, testUserId);

            const alert2 = await conflictAlerts.createAlert({
                patientId: 'P12346',
                conflictType: 'test2',
                description: 'Test alert 2',
                priority: 'medium'
            }, testUserId);

            // Assign and resolve first alert
            await conflictAlerts.assignAlert(alert1.id, 'DR_SMITH', testUserId);
            await conflictAlerts.resolveAlert(alert1.id, 'DR_SMITH', 'Resolved');

            // Escalate second alert
            await conflictAlerts.escalateAlert(alert2.id, 'ADMIN001', 'Escalation reason');
        });

        test('should generate correct statistics', async () => {
            const stats = await conflictAlerts.getAlertStats({}, testUserId);

            expect(stats).toBeDefined();
            expect(stats.total).toBeDefined();
            expect(stats.byType).toBeDefined();
            expect(stats.byPriority).toBeDefined();
        });
    });

    describe('Subscriptions', () => {
        test('should create and manage subscriptions', async () => {
            const subscriptionId = await conflictAlerts.subscribeToAlerts(testUserId, { type: 'critical' });

            expect(subscriptionId).toBeDefined();

            // Unsubscribe
            const success = await conflictAlerts.unsubscribeFromAlerts(subscriptionId, testUserId);
            expect(success).toBe(true);
        });
    });

    describe('Cleanup', () => {
        test('should clear old alerts', async () => {
            // Create an alert
            await conflictAlerts.createAlert({
                patientId: 'P12345',
                conflictType: 'test',
                description: 'Test alert',
                priority: 'low'
            }, testUserId);

            const removedCount = await conflictAlerts.clearOldAlerts(90, testUserId);
            expect(removedCount).toBeDefined();
        });
    });

    describe('Abena SDK Integration', () => {
        test('should initialize with Abena SDK configuration', () => {
            expect(conflictAlerts.abena).toBeDefined();
        });

        test('should use Abena SDK for patient data access', async () => {
            const alertData = {
                patientId: 'P12345',
                conflictType: 'test',
                description: 'Test alert'
            };

            await conflictAlerts.createAlert(alertData, testUserId);

            expect(conflictAlerts.abena.getPatientData).toHaveBeenCalledWith('P12345', 'conflict_alert_creation');
        });

        test('should use Abena SDK for alert storage', async () => {
            const alertData = {
                patientId: 'P12345',
                conflictType: 'test',
                description: 'Test alert'
            };

            await conflictAlerts.createAlert(alertData, testUserId);

            expect(conflictAlerts.abena.storeAlertData).toHaveBeenCalled();
        });

        test('should use Abena SDK for activity logging', async () => {
            const alertData = {
                patientId: 'P12345',
                conflictType: 'test',
                description: 'Test alert'
            };

            await conflictAlerts.createAlert(alertData, testUserId);

            expect(conflictAlerts.abena.logActivity).toHaveBeenCalledWith({
                action: 'alert_created',
                userId: testUserId,
                patientId: 'P12345',
                alertId: expect.any(String),
                details: expect.any(String)
            });
        });
    });
}); 