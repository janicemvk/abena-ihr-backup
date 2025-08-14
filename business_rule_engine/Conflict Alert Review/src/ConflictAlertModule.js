import MockAbenaSDK from './mocks/AbenaSDK.js';

/**
 * Conflict Alert/Review Module for Abena IHR System
 * 
 * This module provides comprehensive conflict alert management functionality
 * integrated with the Abena SDK for authentication, authorization, data handling,
 * privacy compliance, audit logging, and notifications.
 */
class ConflictAlertModule {
    constructor(config = {}) {
        this.config = {
            alertExpiryDays: 30,
            escalationThreshold: 24, // hours
            maxRetries: 3,
            ...config
        };
        
        // Initialize Abena SDK
        this.abenaSDK = new MockAbenaSDK(config.abenaSDK || {});
        
        console.log('🚨 Conflict Alert Module initialized with Abena SDK integration');
    }

    /**
     * Create a new conflict alert
     * @param {Object} alertData - Alert data
     * @param {string} userId - User creating the alert
     * @returns {Promise<Object>} Created alert
     */
    async createAlert(alertData, userId) {
        try {
            // Validate required fields
            if (!alertData.patientId || !alertData.conflictType || !alertData.description) {
                throw new Error('Missing required fields: patientId, conflictType, description');
            }

            // Get patient data through Abena SDK
            const patientData = await this.abenaSDK.getPatientData(alertData.patientId, 'conflict_alert_creation');
            
            if (!patientData) {
                throw new Error('Patient not found');
            }

            // Get user permissions
            const permissions = await this.abenaSDK.getUserPermissions(userId, 'create_alerts');
            
            if (!permissions.canAccessAlertType(alertData.conflictType)) {
                throw new Error('Insufficient permissions to create this type of alert');
            }

            // Create alert object
            const alert = {
                id: `ALERT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                patientId: alertData.patientId,
                patientName: patientData.name,
                conflictType: alertData.conflictType,
                description: alertData.description,
                severity: alertData.severity || 'medium',
                status: 'open',
                assignedTo: null,
                createdBy: userId,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                expiresAt: new Date(Date.now() + (this.config.alertExpiryDays * 24 * 60 * 60 * 1000)).toISOString(),
                retryCount: 0,
                notes: alertData.notes || [],
                attachments: alertData.attachments || []
            };

            // Store alert data through Abena SDK
            await this.abenaSDK.storeAlertData(alert, 'conflict_alert_creation');

            // Log activity
            await this.abenaSDK.logActivity({
                userId,
                action: 'create_alert',
                resourceType: 'conflict_alert',
                resourceId: alert.id,
                details: {
                    patientId: alert.patientId,
                    conflictType: alert.conflictType,
                    severity: alert.severity
                }
            });

            console.log(`✅ Alert created: ${alert.id} for patient ${alert.patientId}`);
            return alert;

        } catch (error) {
            console.error('❌ Error creating alert:', error.message);
            throw error;
        }
    }

    /**
     * Get all alerts with optional filtering
     * @param {Object} filters - Filter criteria
     * @param {string} userId - User requesting alerts
     * @returns {Promise<Array>} Array of alerts
     */
    async getAlerts(filters = {}, userId) {
        try {
            // Get user permissions
            const permissions = await this.abenaSDK.getUserPermissions(userId, 'view_alerts');
            
            if (!permissions.canViewStatistics) {
                throw new Error('Insufficient permissions to view alerts');
            }

            // Get alerts from Abena SDK
            let alerts = await this.abenaSDK.getAlertData('conflict_alerts', 'view_alerts') || [];

            // Apply filters
            if (filters.status) {
                alerts = alerts.filter(alert => alert.status === filters.status);
            }
            if (filters.conflictType) {
                alerts = alerts.filter(alert => alert.conflictType === filters.conflictType);
            }
            if (filters.severity) {
                alerts = alerts.filter(alert => alert.severity === filters.severity);
            }
            if (filters.assignedTo) {
                alerts = alerts.filter(alert => alert.assignedTo === filters.assignedTo);
            }
            if (filters.patientId) {
                alerts = alerts.filter(alert => alert.patientId === filters.patientId);
            }

            // Sort by creation date (newest first)
            alerts.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

            // Log activity
            await this.abenaSDK.logActivity({
                userId,
                action: 'view_alerts',
                resourceType: 'conflict_alerts',
                details: { filters, count: alerts.length }
            });

            return alerts;

        } catch (error) {
            console.error('❌ Error getting alerts:', error.message);
            throw error;
        }
    }

    /**
     * Get a specific alert by ID
     * @param {string} alertId - Alert ID
     * @param {string} userId - User requesting the alert
     * @returns {Promise<Object>} Alert object
     */
    async getAlert(alertId, userId) {
        try {
            // Get user permissions
            const permissions = await this.abenaSDK.getUserPermissions(userId, 'view_alerts');
            
            if (!permissions.canViewStatistics) {
                throw new Error('Insufficient permissions to view alerts');
            }

            // Get alert from Abena SDK
            const alert = await this.abenaSDK.getAlertData(alertId, 'view_alert');
            
            if (!alert) {
                throw new Error('Alert not found');
            }

            // Log activity
            await this.abenaSDK.logActivity({
                userId,
                action: 'view_alert',
                resourceType: 'conflict_alert',
                resourceId: alertId
            });

            return alert;

        } catch (error) {
            console.error('❌ Error getting alert:', error.message);
            throw error;
        }
    }

    /**
     * Assign an alert to a user
     * @param {string} alertId - Alert ID
     * @param {string} assigneeId - User ID to assign to
     * @param {string} userId - User making the assignment
     * @returns {Promise<Object>} Updated alert
     */
    async assignAlert(alertId, assigneeId, userId) {
        try {
            // Get user permissions
            const permissions = await this.abenaSDK.getUserPermissions(userId, 'assign_alerts');
            
            if (!permissions.canAssignAlerts) {
                throw new Error('Insufficient permissions to assign alerts');
            }

            // Get current alert
            const alert = await this.abenaSDK.getAlertData(alertId, 'assign_alert');
            
            if (!alert) {
                throw new Error('Alert not found');
            }

            if (alert.status === 'resolved') {
                throw new Error('Cannot assign resolved alert');
            }

            // Update alert
            const updatedAlert = {
                ...alert,
                assignedTo: assigneeId,
                updatedAt: new Date().toISOString(),
                status: 'assigned'
            };

            // Store updated alert through Abena SDK
            await this.abenaSDK.updateAlertData(alertId, updatedAlert, 'assign_alert');

            // Log activity
            await this.abenaSDK.logActivity({
                userId,
                action: 'assign_alert',
                resourceType: 'conflict_alert',
                resourceId: alertId,
                details: { assigneeId }
            });

            console.log(`✅ Alert ${alertId} assigned to ${assigneeId}`);
            return updatedAlert;

        } catch (error) {
            console.error('❌ Error assigning alert:', error.message);
            throw error;
        }
    }

    /**
     * Update alert status
     * @param {string} alertId - Alert ID
     * @param {string} status - New status
     * @param {string} userId - User updating the alert
     * @param {string} notes - Optional notes
     * @returns {Promise<Object>} Updated alert
     */
    async updateAlertStatus(alertId, status, userId, notes = '') {
        try {
            // Get user permissions
            const permissions = await this.abenaSDK.getUserPermissions(userId, 'review_alerts');
            
            if (!permissions.canReviewAllAlerts) {
                throw new Error('Insufficient permissions to update alert status');
            }

            // Get current alert
            const alert = await this.abenaSDK.getAlertData(alertId, 'update_alert');
            
            if (!alert) {
                throw new Error('Alert not found');
            }

            // Validate status transition
            const validTransitions = {
                'open': ['assigned', 'resolved'],
                'assigned': ['in_review', 'resolved', 'escalated'],
                'in_review': ['resolved', 'escalated'],
                'escalated': ['assigned', 'resolved'],
                'resolved': []
            };

            if (!validTransitions[alert.status].includes(status)) {
                throw new Error(`Invalid status transition from ${alert.status} to ${status}`);
            }

            // Update alert
            const updatedAlert = {
                ...alert,
                status,
                updatedAt: new Date().toISOString()
            };

            // Add notes if provided
            if (notes) {
                updatedAlert.notes.push({
                    id: `NOTE_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                    text: notes,
                    createdBy: userId,
                    createdAt: new Date().toISOString()
                });
            }

            // Store updated alert through Abena SDK
            await this.abenaSDK.updateAlertData(alertId, updatedAlert, 'update_alert');

            // Log activity
            await this.abenaSDK.logActivity({
                userId,
                action: 'update_alert_status',
                resourceType: 'conflict_alert',
                resourceId: alertId,
                details: { status, notes }
            });

            console.log(`✅ Alert ${alertId} status updated to ${status}`);
            return updatedAlert;

        } catch (error) {
            console.error('❌ Error updating alert status:', error.message);
            throw error;
        }
    }

    /**
     * Resolve an alert
     * @param {string} alertId - Alert ID
     * @param {string} resolution - Resolution details
     * @param {string} userId - User resolving the alert
     * @returns {Promise<Object>} Resolved alert
     */
    async resolveAlert(alertId, resolution, userId) {
        try {
            // Get user permissions
            const permissions = await this.abenaSDK.getUserPermissions(userId, 'resolve_alerts');
            
            if (!permissions.canResolveAlerts) {
                throw new Error('Insufficient permissions to resolve alerts');
            }

            // Get current alert
            const alert = await this.abenaSDK.getAlertData(alertId, 'resolve_alert');
            
            if (!alert) {
                throw new Error('Alert not found');
            }

            if (alert.status === 'resolved') {
                throw new Error('Alert is already resolved');
            }

            // Update alert
            const updatedAlert = {
                ...alert,
                status: 'resolved',
                resolution,
                resolvedBy: userId,
                resolvedAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };

            // Store updated alert through Abena SDK
            await this.abenaSDK.updateAlertData(alertId, updatedAlert, 'resolve_alert');

            // Log activity
            await this.abenaSDK.logActivity({
                userId,
                action: 'resolve_alert',
                resourceType: 'conflict_alert',
                resourceId: alertId,
                details: { resolution }
            });

            console.log(`✅ Alert ${alertId} resolved`);
            return updatedAlert;

        } catch (error) {
            console.error('❌ Error resolving alert:', error.message);
            throw error;
        }
    }

    /**
     * Escalate an alert
     * @param {string} alertId - Alert ID
     * @param {string} escalationReason - Reason for escalation
     * @param {string} userId - User escalating the alert
     * @returns {Promise<Object>} Escalated alert
     */
    async escalateAlert(alertId, escalationReason, userId) {
        try {
            // Get user permissions
            const permissions = await this.abenaSDK.getUserPermissions(userId, 'escalate_alerts');
            
            if (!permissions.canEscalateAlerts) {
                throw new Error('Insufficient permissions to escalate alerts');
            }

            // Get current alert
            const alert = await this.abenaSDK.getAlertData(alertId, 'escalate_alert');
            
            if (!alert) {
                throw new Error('Alert not found');
            }

            if (alert.status === 'resolved') {
                throw new Error('Cannot escalate resolved alert');
            }

            // Update alert
            const updatedAlert = {
                ...alert,
                status: 'escalated',
                escalationReason,
                escalatedBy: userId,
                escalatedAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };

            // Store updated alert through Abena SDK
            await this.abenaSDK.updateAlertData(alertId, updatedAlert, 'escalate_alert');

            // Log activity
            await this.abenaSDK.logActivity({
                userId,
                action: 'escalate_alert',
                resourceType: 'conflict_alert',
                resourceId: alertId,
                details: { escalationReason }
            });

            console.log(`⚠️ Alert ${alertId} escalated`);
            return updatedAlert;

        } catch (error) {
            console.error('❌ Error escalating alert:', error.message);
            throw error;
        }
    }

    /**
     * Get alert statistics
     * @param {Object} filters - Filter criteria
     * @param {string} userId - User requesting statistics
     * @returns {Promise<Object>} Statistics object
     */
    async getStatistics(filters = {}, userId) {
        try {
            // Get user permissions
            const permissions = await this.abenaSDK.getUserPermissions(userId, 'view_statistics');
            
            if (!permissions.canViewStatistics) {
                throw new Error('Insufficient permissions to view statistics');
            }

            // Get all alerts
            const alerts = await this.abenaSDK.getAlertData('conflict_alerts', 'view_statistics') || [];

            // Calculate statistics
            const stats = {
                total: alerts.length,
                byStatus: {},
                byType: {},
                bySeverity: {},
                byAssignee: {},
                recentActivity: alerts
                    .filter(alert => {
                        const daysSinceUpdate = (Date.now() - new Date(alert.updatedAt)) / (1000 * 60 * 60 * 24);
                        return daysSinceUpdate <= 7;
                    })
                    .length,
                averageResolutionTime: 0
            };

            // Calculate status distribution
            alerts.forEach(alert => {
                stats.byStatus[alert.status] = (stats.byStatus[alert.status] || 0) + 1;
                stats.byType[alert.conflictType] = (stats.byType[alert.conflictType] || 0) + 1;
                stats.bySeverity[alert.severity] = (stats.bySeverity[alert.severity] || 0) + 1;
                
                if (alert.assignedTo) {
                    stats.byAssignee[alert.assignedTo] = (stats.byAssignee[alert.assignedTo] || 0) + 1;
                }
            });

            // Calculate average resolution time
            const resolvedAlerts = alerts.filter(alert => alert.status === 'resolved' && alert.resolvedAt);
            if (resolvedAlerts.length > 0) {
                const totalResolutionTime = resolvedAlerts.reduce((total, alert) => {
                    return total + (new Date(alert.resolvedAt) - new Date(alert.createdAt));
                }, 0);
                stats.averageResolutionTime = totalResolutionTime / resolvedAlerts.length / (1000 * 60 * 60); // in hours
            }

            // Log activity
            await this.abenaSDK.logActivity({
                userId,
                action: 'view_statistics',
                resourceType: 'conflict_alerts',
                details: { filters }
            });

            return stats;

        } catch (error) {
            console.error('❌ Error getting statistics:', error.message);
            throw error;
        }
    }

    /**
     * Clean up expired alerts
     * @param {string} userId - User performing cleanup
     * @returns {Promise<Object>} Cleanup results
     */
    async cleanupExpiredAlerts(userId) {
        try {
            // Get user permissions
            const permissions = await this.abenaSDK.getUserPermissions(userId, 'cleanup_alerts');
            
            if (!permissions.canCleanupAlerts) {
                throw new Error('Insufficient permissions to cleanup alerts');
            }

            // Get all alerts
            const alerts = await this.abenaSDK.getAlertData('conflict_alerts', 'cleanup_alerts') || [];
            
            const now = new Date();
            const expiredAlerts = alerts.filter(alert => {
                return new Date(alert.expiresAt) < now && alert.status !== 'resolved';
            });

            let cleanedCount = 0;
            for (const alert of expiredAlerts) {
                await this.abenaSDK.deleteAlertData(alert.id, 'cleanup_expired_alert');
                cleanedCount++;
            }

            // Log activity
            await this.abenaSDK.logActivity({
                userId,
                action: 'cleanup_expired_alerts',
                resourceType: 'conflict_alerts',
                details: { cleanedCount }
            });

            console.log(`🧹 Cleaned up ${cleanedCount} expired alerts`);
            return { cleanedCount, totalExpired: expiredAlerts.length };

        } catch (error) {
            console.error('❌ Error cleaning up expired alerts:', error.message);
            throw error;
        }
    }

    /**
     * Subscribe to alert notifications
     * @param {Object} subscriptionData - Subscription configuration
     * @param {string} userId - User subscribing
     * @returns {Promise<string>} Subscription ID
     */
    async subscribeToAlerts(subscriptionData, userId) {
        try {
            // Get user permissions
            const permissions = await this.abenaSDK.getUserPermissions(userId, 'subscribe_alerts');
            
            if (!permissions.canSubscribeAlerts) {
                throw new Error('Insufficient permissions to subscribe to alerts');
            }

            // Create subscription through Abena SDK
            const subscriptionId = await this.abenaSDK.subscribeToNotifications({
                userId,
                type: 'conflict_alerts',
                ...subscriptionData
            });

            // Log activity
            await this.abenaSDK.logActivity({
                userId,
                action: 'subscribe_to_alerts',
                resourceType: 'notification_subscription',
                resourceId: subscriptionId,
                details: subscriptionData
            });

            console.log(`🔔 User ${userId} subscribed to alert notifications`);
            return subscriptionId;

        } catch (error) {
            console.error('❌ Error subscribing to alerts:', error.message);
            throw error;
        }
    }

    /**
     * Unsubscribe from alert notifications
     * @param {string} subscriptionId - Subscription ID
     * @param {string} userId - User unsubscribing
     * @returns {Promise<boolean>} Success status
     */
    async unsubscribeFromAlerts(subscriptionId, userId) {
        try {
            // Get user permissions
            const permissions = await this.abenaSDK.getUserPermissions(userId, 'subscribe_alerts');
            
            if (!permissions.canSubscribeAlerts) {
                throw new Error('Insufficient permissions to manage alert subscriptions');
            }

            // Remove subscription through Abena SDK
            await this.abenaSDK.unsubscribeFromNotifications(subscriptionId, userId);

            // Log activity
            await this.abenaSDK.logActivity({
                userId,
                action: 'unsubscribe_from_alerts',
                resourceType: 'notification_subscription',
                resourceId: subscriptionId
            });

            console.log(`🔕 User ${userId} unsubscribed from alert notifications`);
            return true;

        } catch (error) {
            console.error('❌ Error unsubscribing from alerts:', error.message);
            throw error;
        }
    }

    /**
     * Get alerts for a specific patient
     * @param {string} patientId - Patient ID
     * @param {string} userId - User requesting patient alerts
     * @returns {Promise<Array>} Array of patient alerts
     */
    async getPatientAlerts(patientId, userId) {
        try {
            // Get user permissions
            const permissions = await this.abenaSDK.getUserPermissions(userId, 'view_patient_alerts');
            
            if (!permissions.canViewPatientAlerts) {
                throw new Error('Insufficient permissions to view patient alerts');
            }

            // Verify patient exists
            const patientData = await this.abenaSDK.getPatientData(patientId, 'view_patient_alerts');
            
            if (!patientData) {
                throw new Error('Patient not found');
            }

            // Get alerts for patient
            const alerts = await this.abenaSDK.getAlertData('conflict_alerts', 'view_patient_alerts') || [];
            const patientAlerts = alerts.filter(alert => alert.patientId === patientId);

            // Log activity
            await this.abenaSDK.logActivity({
                userId,
                action: 'view_patient_alerts',
                resourceType: 'conflict_alerts',
                details: { patientId, count: patientAlerts.length }
            });

            return patientAlerts;

        } catch (error) {
            console.error('❌ Error getting patient alerts:', error.message);
            throw error;
        }
    }

    /**
     * Get Abena SDK instance for advanced operations
     * @returns {Object} Abena SDK instance
     */
    getAbenaSDK() {
        return this.abenaSDK;
    }
}

export default ConflictAlertModule; 