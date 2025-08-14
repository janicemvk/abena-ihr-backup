// Conflict Alert/Review Module
// Handles notifications and alerts for conflicts requiring manual review
// Uses Abena SDK for authentication, authorization, and data handling

import AbenaSDK from '@abena/sdk';

class ConflictAlertModule {
    constructor(config = {}) {
        // Initialize Abena SDK with service URLs
        this.abena = new AbenaSDK({
            authServiceUrl: config.authServiceUrl || 'http://localhost:3001',
            dataServiceUrl: config.dataServiceUrl || 'http://localhost:8001',
            privacyServiceUrl: config.privacyServiceUrl || 'http://localhost:8002',
            blockchainServiceUrl: config.blockchainServiceUrl || 'http://localhost:8003'
        });

        // Alert type constants
        this.alertTypes = {
            CRITICAL: 'critical',
            WARNING: 'warning',
            INFO: 'info'
        };

        this.priorities = {
            LOW: 'low',
            MEDIUM: 'medium',
            HIGH: 'high',
            CRITICAL: 'critical'
        };

        this.statuses = {
            PENDING: 'pending',
            ASSIGNED: 'assigned',
            IN_REVIEW: 'in_review',
            REVIEWED: 'reviewed',
            RESOLVED: 'resolved',
            ESCALATED: 'escalated'
        };
    }

    // Create new conflict alert
    async createAlert(conflictData, userId) {
        try {
            // Validate required fields
            if (!conflictData.patientId || !conflictData.conflictType) {
                throw new Error('Patient ID and conflict type are required');
            }

            // Get patient data through Abena SDK (auto-handles auth & permissions)
            const patientData = await this.abena.getPatientData(conflictData.patientId, 'conflict_alert_creation');

            // Create alert object
            const alert = {
                id: this.generateAlertId(),
                timestamp: new Date().toISOString(),
                type: this.determineAlertType(conflictData),
                priority: this.validatePriority(conflictData.priority) || 'medium',
                patientId: conflictData.patientId,
                conflictType: conflictData.conflictType,
                description: conflictData.description || 'No description provided',
                affectedData: conflictData.affectedData || [],
                suggestedResolution: conflictData.suggestedResolution || 'Manual review required',
                status: this.statuses.PENDING,
                assignedTo: null,
                createdBy: userId,
                escalationLevel: 0,
                reviewHistory: [],
                metadata: {
                    source: conflictData.source || 'unknown',
                    confidence: conflictData.confidence || 0.8,
                    tags: conflictData.tags || []
                }
            };

            // Store alert through Abena SDK (auto-handles privacy & encryption)
            await this.abena.storeAlertData(alert, 'conflict_alert_creation');

            // Log alert creation through Abena SDK (auto-handles audit logging)
            await this.abena.logActivity({
                action: 'alert_created',
                userId: userId,
                patientId: conflictData.patientId,
                alertId: alert.id,
                details: `Created ${alert.type} alert for ${conflictData.conflictType}`
            });

            return alert;
        } catch (error) {
            console.error('Error creating alert:', error.message);
            throw error;
        }
    }

    // Get alerts for specific user/role
    async getAlertsForUser(userId, filters = {}) {
        try {
            // Get user permissions through Abena SDK
            const userPermissions = await this.abena.getUserPermissions(userId, 'conflict_alert_access');

            // Get alerts through Abena SDK (auto-handles auth & data access)
            const allAlerts = await this.abena.getAlertData('conflict_alerts', 'conflict_alert_access');

            // Filter alerts based on user permissions and assignments
            let filteredAlerts = allAlerts.filter(alert => {
                // Check if user is assigned to the alert
                if (alert.assignedTo === userId) return true;
                
                // Check user permissions for alert types
                if (userPermissions.canAccessAlertType(alert.type)) return true;
                
                return false;
            });

            // Apply additional filters
            if (filters.status) {
                filteredAlerts = filteredAlerts.filter(alert => alert.status === filters.status);
            }
            if (filters.priority) {
                filteredAlerts = filteredAlerts.filter(alert => alert.priority === filters.priority);
            }
            if (filters.type) {
                filteredAlerts = filteredAlerts.filter(alert => alert.type === filters.type);
            }
            if (filters.patientId) {
                filteredAlerts = filteredAlerts.filter(alert => alert.patientId === filters.patientId);
            }

            // Sort by priority and timestamp
            return this.sortAlertsByPriority(filteredAlerts);
        } catch (error) {
            console.error('Error getting alerts for user:', error.message);
            return [];
        }
    }

    // Get alerts by priority
    async getAlertsByPriority(priority, userId) {
        try {
            const validPriority = this.validatePriority(priority);
            if (!validPriority) {
                throw new Error('Invalid priority level');
            }

            // Get alerts through Abena SDK
            const allAlerts = await this.abena.getAlertData('conflict_alerts', 'conflict_alert_access');

            return allAlerts
                .filter(alert => alert.priority === validPriority)
                .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        } catch (error) {
            console.error('Error getting alerts by priority:', error.message);
            return [];
        }
    }

    // Assign alert to user
    async assignAlert(alertId, assigneeUserId, assignerUserId) {
        try {
            // Get alert through Abena SDK
            const alert = await this.abena.getAlertData(alertId, 'conflict_alert_assignment');
            
            if (!alert) {
                throw new Error('Alert not found');
            }

            if (alert.status === this.statuses.REVIEWED || alert.status === this.statuses.RESOLVED) {
                throw new Error('Cannot assign reviewed or resolved alert');
            }

            // Check assigner permissions through Abena SDK
            const assignerPermissions = await this.abena.getUserPermissions(assignerUserId, 'conflict_alert_assignment');
            if (!assignerPermissions.canAssignAlerts) {
                throw new Error('User not authorized to assign alerts');
            }

            // Update alert
            alert.assignedTo = assigneeUserId;
            alert.status = this.statuses.ASSIGNED;
            alert.assignedAt = new Date().toISOString();
            alert.assignedBy = assignerUserId;

            // Add to review history
            alert.reviewHistory.push({
                action: 'assigned',
                userId: assignerUserId,
                timestamp: new Date().toISOString(),
                details: `Assigned to ${assigneeUserId}`
            });

            // Store updated alert through Abena SDK
            await this.abena.updateAlertData(alertId, alert, 'conflict_alert_assignment');

            // Log assignment through Abena SDK
            await this.abena.logActivity({
                action: 'alert_assigned',
                userId: assignerUserId,
                patientId: alert.patientId,
                alertId: alertId,
                assigneeUserId: assigneeUserId,
                details: `Alert assigned to ${assigneeUserId}`
            });

            return true;
        } catch (error) {
            console.error('Error assigning alert:', error.message);
            return false;
        }
    }

    // Mark alert as reviewed
    async markAsReviewed(alertId, userId, resolution, notes = '') {
        try {
            // Get alert through Abena SDK
            const alert = await this.abena.getAlertData(alertId, 'conflict_alert_review');
            
            if (!alert) {
                throw new Error('Alert not found');
            }

            // Check user permissions through Abena SDK
            const userPermissions = await this.abena.getUserPermissions(userId, 'conflict_alert_review');
            if (alert.assignedTo !== userId && !userPermissions.canReviewAllAlerts) {
                throw new Error('User not authorized to review this alert');
            }

            // Update alert
            alert.status = this.statuses.REVIEWED;
            alert.reviewedBy = userId;
            alert.reviewedAt = new Date().toISOString();
            alert.resolution = resolution;
            alert.notes = notes;

            // Add to review history
            alert.reviewHistory.push({
                action: 'reviewed',
                userId: userId,
                timestamp: new Date().toISOString(),
                details: `Reviewed with resolution: ${resolution}`,
                notes: notes
            });

            // Store updated alert through Abena SDK
            await this.abena.updateAlertData(alertId, alert, 'conflict_alert_review');

            // Log review through Abena SDK
            await this.abena.logActivity({
                action: 'alert_reviewed',
                userId: userId,
                patientId: alert.patientId,
                alertId: alertId,
                resolution: resolution,
                details: `Alert reviewed with resolution: ${resolution}`
            });

            return true;
        } catch (error) {
            console.error('Error marking alert as reviewed:', error.message);
            return false;
        }
    }

    // Resolve alert
    async resolveAlert(alertId, userId, resolutionDetails) {
        try {
            // Get alert through Abena SDK
            const alert = await this.abena.getAlertData(alertId, 'conflict_alert_resolution');
            
            if (!alert) {
                throw new Error('Alert not found');
            }

            // Check user permissions through Abena SDK
            const userPermissions = await this.abena.getUserPermissions(userId, 'conflict_alert_resolution');
            if (!userPermissions.canResolveAlerts) {
                throw new Error('User not authorized to resolve alerts');
            }

            // Update alert
            alert.status = this.statuses.RESOLVED;
            alert.resolvedBy = userId;
            alert.resolvedAt = new Date().toISOString();
            alert.resolutionDetails = resolutionDetails;

            // Add to review history
            alert.reviewHistory.push({
                action: 'resolved',
                userId: userId,
                timestamp: new Date().toISOString(),
                details: `Resolved: ${resolutionDetails}`
            });

            // Store updated alert through Abena SDK
            await this.abena.updateAlertData(alertId, alert, 'conflict_alert_resolution');

            // Log resolution through Abena SDK
            await this.abena.logActivity({
                action: 'alert_resolved',
                userId: userId,
                patientId: alert.patientId,
                alertId: alertId,
                resolutionDetails: resolutionDetails,
                details: `Alert resolved: ${resolutionDetails}`
            });

            return true;
        } catch (error) {
            console.error('Error resolving alert:', error.message);
            return false;
        }
    }

    // Escalate alert
    async escalateAlert(alertId, userId, escalationReason) {
        try {
            // Get alert through Abena SDK
            const alert = await this.abena.getAlertData(alertId, 'conflict_alert_escalation');
            
            if (!alert) {
                throw new Error('Alert not found');
            }

            // Check user permissions through Abena SDK
            const userPermissions = await this.abena.getUserPermissions(userId, 'conflict_alert_escalation');
            if (!userPermissions.canEscalateAlerts) {
                throw new Error('User not authorized to escalate alerts');
            }

            // Update alert
            alert.status = this.statuses.ESCALATED;
            alert.escalationLevel += 1;
            alert.escalatedBy = userId;
            alert.escalatedAt = new Date().toISOString();
            alert.escalationReason = escalationReason;

            // Add to review history
            alert.reviewHistory.push({
                action: 'escalated',
                userId: userId,
                timestamp: new Date().toISOString(),
                details: `Escalated: ${escalationReason}`
            });

            // Store updated alert through Abena SDK
            await this.abena.updateAlertData(alertId, alert, 'conflict_alert_escalation');

            // Log escalation through Abena SDK
            await this.abena.logActivity({
                action: 'alert_escalated',
                userId: userId,
                patientId: alert.patientId,
                alertId: alertId,
                escalationReason: escalationReason,
                details: `Alert escalated: ${escalationReason}`
            });

            return true;
        } catch (error) {
            console.error('Error escalating alert:', error.message);
            return false;
        }
    }

    // Get alert by ID
    async getAlertById(alertId, userId) {
        try {
            // Get alert through Abena SDK (auto-handles permissions)
            const alert = await this.abena.getAlertData(alertId, 'conflict_alert_access');
            return alert;
        } catch (error) {
            console.error('Error getting alert by ID:', error.message);
            return null;
        }
    }

    // Get alerts for patient
    async getAlertsForPatient(patientId, userId) {
        try {
            // Get patient data through Abena SDK (auto-handles auth & permissions)
            const patientData = await this.abena.getPatientData(patientId, 'conflict_alert_access');
            
            // Get alerts through Abena SDK
            const allAlerts = await this.abena.getAlertData('conflict_alerts', 'conflict_alert_access');
            
            const patientAlerts = allAlerts
                .filter(alert => alert.patientId === patientId)
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

            return patientAlerts;
        } catch (error) {
            console.error('Error getting alerts for patient:', error.message);
            return [];
        }
    }

    // Get alert statistics
    async getAlertStats(filters = {}, userId) {
        try {
            // Get user permissions through Abena SDK
            const userPermissions = await this.abena.getUserPermissions(userId, 'conflict_alert_statistics');
            if (!userPermissions.canViewStatistics) {
                throw new Error('User not authorized to view statistics');
            }

            // Get alerts through Abena SDK
            let allAlerts = await this.abena.getAlertData('conflict_alerts', 'conflict_alert_statistics');

            // Apply filters if provided
            if (filters.patientId) {
                allAlerts = allAlerts.filter(alert => alert.patientId === filters.patientId);
            }
            if (filters.dateRange) {
                const { start, end } = filters.dateRange;
                allAlerts = allAlerts.filter(alert => {
                    const alertDate = new Date(alert.timestamp);
                    return alertDate >= new Date(start) && alertDate <= new Date(end);
                });
            }

            const stats = {
                total: allAlerts.length,
                pending: allAlerts.filter(a => a.status === this.statuses.PENDING).length,
                assigned: allAlerts.filter(a => a.status === this.statuses.ASSIGNED).length,
                inReview: allAlerts.filter(a => a.status === this.statuses.IN_REVIEW).length,
                reviewed: allAlerts.filter(a => a.status === this.statuses.REVIEWED).length,
                resolved: allAlerts.filter(a => a.status === this.statuses.RESOLVED).length,
                escalated: allAlerts.filter(a => a.status === this.statuses.ESCALATED).length,
                byType: {},
                byPriority: {},
                averageResolutionTime: this.calculateAverageResolutionTime(allAlerts),
                escalationRate: this.calculateEscalationRate(allAlerts)
            };

            // Count by type
            Object.values(this.alertTypes).forEach(type => {
                stats.byType[type] = allAlerts.filter(a => a.type === type).length;
            });

            // Count by priority
            Object.values(this.priorities).forEach(priority => {
                stats.byPriority[priority] = allAlerts.filter(a => a.priority === priority).length;
            });

            return stats;
        } catch (error) {
            console.error('Error getting alert stats:', error.message);
            return {};
        }
    }

    // Subscribe to alerts (using Abena SDK notification system)
    async subscribeToAlerts(userId, filters = {}) {
        try {
            // Subscribe through Abena SDK notification system
            const subscriptionId = await this.abena.subscribeToNotifications({
                userId: userId,
                notificationType: 'conflict_alerts',
                filters: filters,
                callback: this.handleAlertNotification.bind(this)
            });

            return subscriptionId;
        } catch (error) {
            console.error('Error creating subscription:', error.message);
            throw error;
        }
    }

    // Unsubscribe from alerts
    async unsubscribeFromAlerts(subscriptionId, userId) {
        try {
            // Unsubscribe through Abena SDK notification system
            await this.abena.unsubscribeFromNotifications(subscriptionId, userId);
            return true;
        } catch (error) {
            console.error('Error unsubscribing:', error.message);
            return false;
        }
    }

    // Handle alert notifications from Abena SDK
    async handleAlertNotification(notification) {
        // Process alert notifications as needed
        console.log('Alert notification received:', notification);
    }

    // Clear old alerts
    async clearOldAlerts(daysOld = 90, userId) {
        try {
            // Check user permissions through Abena SDK
            const userPermissions = await this.abena.getUserPermissions(userId, 'conflict_alert_cleanup');
            if (!userPermissions.canCleanupAlerts) {
                throw new Error('User not authorized to cleanup alerts');
            }

            // Get alerts through Abena SDK
            const allAlerts = await this.abena.getAlertData('conflict_alerts', 'conflict_alert_cleanup');
            
            const cutoffDate = new Date(Date.now() - daysOld * 24 * 60 * 60 * 1000);
            const alertsToRemove = allAlerts.filter(alert => {
                const alertDate = new Date(alert.timestamp);
                return alertDate < cutoffDate && alert.status !== this.statuses.PENDING;
            });

            // Remove old alerts through Abena SDK
            for (const alert of alertsToRemove) {
                await this.abena.deleteAlertData(alert.id, 'conflict_alert_cleanup');
            }

            // Log cleanup through Abena SDK
            await this.abena.logActivity({
                action: 'alerts_cleaned_up',
                userId: userId,
                removedCount: alertsToRemove.length,
                details: `Cleaned up ${alertsToRemove.length} old alerts`
            });

            return alertsToRemove.length;
        } catch (error) {
            console.error('Error clearing old alerts:', error.message);
            return 0;
        }
    }

    // Private methods
    generateAlertId() {
        return `ALERT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    determineAlertType(conflictData) {
        if (conflictData.severity === 'critical' || conflictData.affectsPatientSafety) {
            return this.alertTypes.CRITICAL;
        }
        if (conflictData.severity === 'warning' || conflictData.requiresReview) {
            return this.alertTypes.WARNING;
        }
        return this.alertTypes.INFO;
    }

    validatePriority(priority) {
        const validPriorities = Object.values(this.priorities);
        return validPriorities.includes(priority) ? priority : null;
    }

    sortAlertsByPriority(alerts) {
        const priorityOrder = {
            [this.priorities.CRITICAL]: 4,
            [this.priorities.HIGH]: 3,
            [this.priorities.MEDIUM]: 2,
            [this.priorities.LOW]: 1
        };

        return alerts.sort((a, b) => {
            const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
            if (priorityDiff !== 0) return priorityDiff;
            return new Date(a.timestamp) - new Date(b.timestamp);
        });
    }

    calculateAverageResolutionTime(alerts) {
        const resolvedAlerts = alerts.filter(alert => 
            alert.status === this.statuses.RESOLVED && alert.resolvedAt
        );

        if (resolvedAlerts.length === 0) return 0;

        const totalTime = resolvedAlerts.reduce((sum, alert) => {
            const created = new Date(alert.timestamp);
            const resolved = new Date(alert.resolvedAt);
            return sum + (resolved - created);
        }, 0);

        return totalTime / resolvedAlerts.length;
    }

    calculateEscalationRate(alerts) {
        if (alerts.length === 0) return 0;
        const escalatedCount = alerts.filter(alert => alert.status === this.statuses.ESCALATED).length;
        return (escalatedCount / alerts.length) * 100;
    }
}

export default ConflictAlertModule; 