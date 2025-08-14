// Mock Abena SDK for demonstration purposes
// This simulates the expected Abena SDK functionality

class MockAbenaSDK {
    constructor(config = {}) {
        this.config = config;
        this.authServiceUrl = config.authServiceUrl || 'http://localhost:3001';
        this.dataServiceUrl = config.dataServiceUrl || 'http://localhost:8001';
        this.privacyServiceUrl = config.privacyServiceUrl || 'http://localhost:8002';
        this.blockchainServiceUrl = config.blockchainServiceUrl || 'http://localhost:8003';
        
        // Mock data storage
        this.mockData = {
            patients: {},
            alerts: [],
            users: {},
            activities: []
        };
        
        console.log('🔐 Mock Abena SDK initialized with config:', config);
    }

    // Authentication middleware
    authMiddleware() {
        return (req, res, next) => {
            // Mock authentication - extract user from Authorization header
            const authHeader = req.headers.authorization;
            if (authHeader && authHeader.startsWith('Bearer ')) {
                const token = authHeader.substring(7);
                // Mock user extraction from token
                req.user = {
                    id: token || 'DEMO_USER',
                    name: 'Demo User',
                    role: 'physician',
                    permissions: ['create_alerts', 'view_alerts', 'assign_alerts', 'review_alerts', 'resolve_alerts', 'escalate_alerts', 'view_statistics', 'cleanup_alerts', 'subscribe_alerts', 'view_patient_alerts']
                };
            } else {
                req.user = null;
            }
            next();
        };
    }

    // Require authentication middleware
    requireAuth(requiredPermissions = []) {
        return (req, res, next) => {
            if (!req.user) {
                return res.status(401).json({
                    success: false,
                    error: 'Unauthorized',
                    message: 'Authentication required'
                });
            }

            if (requiredPermissions.length > 0) {
                const hasPermission = requiredPermissions.some(permission => 
                    req.user.permissions.includes(permission)
                );
                
                if (!hasPermission) {
                    return res.status(403).json({
                        success: false,
                        error: 'Forbidden',
                        message: 'Insufficient permissions'
                    });
                }
            }

            next();
        };
    }

    // Patient data methods
    async getPatientData(patientId, purpose) {
        console.log(`📋 Mock Abena SDK: Getting patient data for ${patientId} (purpose: ${purpose})`);
        
        if (!this.mockData.patients[patientId]) {
            this.mockData.patients[patientId] = {
                id: patientId,
                name: `Patient ${patientId}`,
                dateOfBirth: '1990-01-01',
                gender: 'Unknown',
                medicalRecordNumber: `MRN${patientId}`
            };
        }
        
        return this.mockData.patients[patientId];
    }

    // Alert data methods
    async storeAlertData(alert, purpose) {
        console.log(`💾 Mock Abena SDK: Storing alert data (purpose: ${purpose})`);
        this.mockData.alerts.push(alert);
        return true;
    }

    async getAlertData(identifier, purpose) {
        console.log(`📊 Mock Abena SDK: Getting alert data (purpose: ${purpose})`);
        
        if (identifier === 'conflict_alerts') {
            return this.mockData.alerts;
        } else {
            return this.mockData.alerts.find(alert => alert.id === identifier);
        }
    }

    async updateAlertData(alertId, alertData, purpose) {
        console.log(`🔄 Mock Abena SDK: Updating alert data for ${alertId} (purpose: ${purpose})`);
        
        const index = this.mockData.alerts.findIndex(alert => alert.id === alertId);
        if (index !== -1) {
            this.mockData.alerts[index] = { ...this.mockData.alerts[index], ...alertData };
            return true;
        }
        return false;
    }

    async deleteAlertData(alertId, purpose) {
        console.log(`🗑️ Mock Abena SDK: Deleting alert data for ${alertId} (purpose: ${purpose})`);
        
        const index = this.mockData.alerts.findIndex(alert => alert.id === alertId);
        if (index !== -1) {
            this.mockData.alerts.splice(index, 1);
            return true;
        }
        return false;
    }

    // User permissions
    async getUserPermissions(userId, purpose) {
        console.log(`🔑 Mock Abena SDK: Getting user permissions for ${userId} (purpose: ${purpose})`);
        
        return {
            canAccessAlertType: (alertType) => true,
            canAssignAlerts: true,
            canReviewAllAlerts: true,
            canResolveAlerts: true,
            canEscalateAlerts: true,
            canViewStatistics: true,
            canCleanupAlerts: true,
            canSubscribeAlerts: true,
            canViewPatientAlerts: true
        };
    }

    // Activity logging
    async logActivity(activityData) {
        console.log(`📝 Mock Abena SDK: Logging activity:`, activityData);
        
        const activity = {
            id: `ACT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            timestamp: new Date().toISOString(),
            ...activityData
        };
        
        this.mockData.activities.push(activity);
        return true;
    }

    // Notification methods
    async subscribeToNotifications(subscriptionData) {
        console.log(`🔔 Mock Abena SDK: Creating notification subscription:`, subscriptionData);
        return `sub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async unsubscribeFromNotifications(subscriptionId, userId) {
        console.log(`🔕 Mock Abena SDK: Removing notification subscription: ${subscriptionId}`);
        return true;
    }

    // Utility methods
    getMockData() {
        return this.mockData;
    }

    clearMockData() {
        this.mockData = {
            patients: {},
            alerts: [],
            users: {},
            activities: []
        };
    }
}

export default MockAbenaSDK; 