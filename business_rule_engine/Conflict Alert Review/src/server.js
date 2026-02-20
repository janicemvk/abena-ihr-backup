import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import ConflictAlertModule from './ConflictAlertModule.js';
import MockAbenaSDK from './mocks/AbenaSDK.js';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize Abena SDK
const abena = new MockAbenaSDK();

// Initialize the conflict alert module with Abena SDK
const conflictAlerts = new ConflictAlertModule({
    authServiceUrl: process.env.ABENA_AUTH_SERVICE_URL || 'http://localhost:3001',
    dataServiceUrl: process.env.ABENA_DATA_SERVICE_URL || 'http://localhost:8001',
    privacyServiceUrl: process.env.ABENA_PRIVACY_SERVICE_URL || 'http://localhost:8002',
    blockchainServiceUrl: process.env.ABENA_BLOCKCHAIN_SERVICE_URL || 'http://localhost:8003'
});

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Abena SDK authentication middleware
app.use(abena.authMiddleware());

// Request logging middleware
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path} - User: ${req.user?.id || 'anonymous'}`);
    next();
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Error:', error);
    res.status(500).json({
        success: false,
        error: 'Internal server error',
        message: error.message
    });
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'Abena IHR Conflict Alert Module',
        abenaSDK: 'integrated'
    });
});

// Create new alert
app.post('/api/alerts', abena.requireAuth(['create_alerts']), async (req, res) => {
    try {
        const alertData = req.body;
        const userId = req.user.id; // From Abena SDK auth middleware
        
        // Validate required fields
        if (!alertData.patientId || !alertData.conflictType) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields',
                message: 'Patient ID and conflict type are required'
            });
        }

        const alert = await conflictAlerts.createAlert(alertData, userId);
        
        res.status(201).json({
            success: true,
            data: alert,
            message: 'Alert created successfully'
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: 'Validation error',
            message: error.message
        });
    }
});

// Get all alerts with optional filters
app.get('/api/alerts', abena.requireAuth(['view_alerts']), async (req, res) => {
    try {
        const { 
            status, 
            priority, 
            type, 
            patientId,
            limit = 50,
            offset = 0
        } = req.query;
        
        const userId = req.user.id; // From Abena SDK auth middleware

        const filters = { status, priority, type, patientId };
        const alerts = await conflictAlerts.getAlertsForUser(userId, filters);

        // Apply pagination
        const paginatedAlerts = alerts.slice(parseInt(offset), parseInt(offset) + parseInt(limit));

        res.json({
            success: true,
            data: paginatedAlerts,
            pagination: {
                total: alerts.length,
                limit: parseInt(limit),
                offset: parseInt(offset),
                hasMore: parseInt(offset) + parseInt(limit) < alerts.length
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server error',
            message: error.message
        });
    }
});

// Get specific alert by ID
app.get('/api/alerts/:alertId', abena.requireAuth(['view_alerts']), async (req, res) => {
    try {
        const { alertId } = req.params;
        const userId = req.user.id; // From Abena SDK auth middleware
        
        const alert = await conflictAlerts.getAlertById(alertId, userId);

        if (!alert) {
            return res.status(404).json({
                success: false,
                error: 'Not found',
                message: 'Alert not found'
            });
        }

        res.json({
            success: true,
            data: alert
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server error',
            message: error.message
        });
    }
});

// Assign alert to user
app.patch('/api/alerts/:alertId/assign', abena.requireAuth(['assign_alerts']), async (req, res) => {
    try {
        const { alertId } = req.params;
        const { assigneeUserId } = req.body;
        const assignerUserId = req.user.id; // From Abena SDK auth middleware

        if (!assigneeUserId) {
            return res.status(400).json({
                success: false,
                error: 'Missing required field',
                message: 'Assignee user ID is required'
            });
        }

        const success = await conflictAlerts.assignAlert(alertId, assigneeUserId, assignerUserId);

        if (!success) {
            return res.status(404).json({
                success: false,
                error: 'Assignment failed',
                message: 'Alert not found or cannot be assigned'
            });
        }

        res.json({
            success: true,
            message: 'Alert assigned successfully'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server error',
            message: error.message
        });
    }
});

// Mark alert as reviewed
app.patch('/api/alerts/:alertId/review', abena.requireAuth(['review_alerts']), async (req, res) => {
    try {
        const { alertId } = req.params;
        const { resolution, notes } = req.body;
        const userId = req.user.id; // From Abena SDK auth middleware

        if (!resolution) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields',
                message: 'Resolution is required'
            });
        }

        const success = await conflictAlerts.markAsReviewed(alertId, userId, resolution, notes);

        if (!success) {
            return res.status(404).json({
                success: false,
                error: 'Review failed',
                message: 'Alert not found or user not authorized'
            });
        }

        res.json({
            success: true,
            message: 'Alert marked as reviewed successfully'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server error',
            message: error.message
        });
    }
});

// Resolve alert
app.patch('/api/alerts/:alertId/resolve', abena.requireAuth(['resolve_alerts']), async (req, res) => {
    try {
        const { alertId } = req.params;
        const { resolutionDetails } = req.body;
        const userId = req.user.id; // From Abena SDK auth middleware

        if (!resolutionDetails) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields',
                message: 'Resolution details are required'
            });
        }

        const success = await conflictAlerts.resolveAlert(alertId, userId, resolutionDetails);

        if (!success) {
            return res.status(404).json({
                success: false,
                error: 'Resolution failed',
                message: 'Alert not found'
            });
        }

        res.json({
            success: true,
            message: 'Alert resolved successfully'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server error',
            message: error.message
        });
    }
});

// Escalate alert
app.patch('/api/alerts/:alertId/escalate', abena.requireAuth(['escalate_alerts']), async (req, res) => {
    try {
        const { alertId } = req.params;
        const { escalationReason } = req.body;
        const userId = req.user.id; // From Abena SDK auth middleware

        if (!escalationReason) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields',
                message: 'Escalation reason is required'
            });
        }

        const success = await conflictAlerts.escalateAlert(alertId, userId, escalationReason);

        if (!success) {
            return res.status(404).json({
                success: false,
                error: 'Escalation failed',
                message: 'Alert not found'
            });
        }

        res.json({
            success: true,
            message: 'Alert escalated successfully'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server error',
            message: error.message
        });
    }
});

// Get alert statistics
app.get('/api/alerts/stats', abena.requireAuth(['view_statistics']), async (req, res) => {
    try {
        const { patientId, startDate, endDate } = req.query;
        const userId = req.user.id; // From Abena SDK auth middleware
        
        const filters = {};
        if (patientId) filters.patientId = patientId;
        if (startDate && endDate) {
            filters.dateRange = { start: startDate, end: endDate };
        }

        const stats = await conflictAlerts.getAlertStats(filters, userId);

        res.json({
            success: true,
            data: stats
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server error',
            message: error.message
        });
    }
});

// Get alerts by priority
app.get('/api/alerts/priority/:priority', abena.requireAuth(['view_alerts']), async (req, res) => {
    try {
        const { priority } = req.params;
        const userId = req.user.id; // From Abena SDK auth middleware
        
        const alerts = await conflictAlerts.getAlertsByPriority(priority, userId);

        res.json({
            success: true,
            data: alerts
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server error',
            message: error.message
        });
    }
});

// Get alerts for specific patient
app.get('/api/patients/:patientId/alerts', abena.requireAuth(['view_patient_alerts']), async (req, res) => {
    try {
        const { patientId } = req.params;
        const userId = req.user.id; // From Abena SDK auth middleware
        
        const alerts = await conflictAlerts.getAlertsForPatient(patientId, userId);

        res.json({
            success: true,
            data: alerts
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server error',
            message: error.message
        });
    }
});

// Clear old alerts
app.delete('/api/alerts/cleanup', abena.requireAuth(['cleanup_alerts']), async (req, res) => {
    try {
        const { daysOld = 90 } = req.query;
        const userId = req.user.id; // From Abena SDK auth middleware
        
        const removedCount = await conflictAlerts.clearOldAlerts(parseInt(daysOld), userId);

        res.json({
            success: true,
            data: { removedCount },
            message: `Cleared ${removedCount} old alerts`
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server error',
            message: error.message
        });
    }
});

// Subscribe to alerts
app.post('/api/alerts/subscribe', abena.requireAuth(['subscribe_alerts']), async (req, res) => {
    try {
        const { filters } = req.body;
        const userId = req.user.id; // From Abena SDK auth middleware
        
        const subscriptionId = await conflictAlerts.subscribeToAlerts(userId, filters);

        res.json({
            success: true,
            data: { subscriptionId },
            message: 'Subscription created successfully'
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            error: 'Subscription failed',
            message: error.message
        });
    }
});

// Unsubscribe from alerts
app.delete('/api/alerts/subscribe/:subscriptionId', abena.requireAuth(['subscribe_alerts']), async (req, res) => {
    try {
        const { subscriptionId } = req.params;
        const userId = req.user.id; // From Abena SDK auth middleware
        
        const success = await conflictAlerts.unsubscribeFromAlerts(subscriptionId, userId);

        res.json({
            success: true,
            message: success ? 'Unsubscribed successfully' : 'Subscription not found'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Server error',
            message: error.message
        });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Abena IHR Conflict Alert Module server running on port ${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/health`);
    console.log(`📚 API Documentation: http://localhost:${PORT}/api/alerts`);
    console.log(`🔐 Abena SDK: Integrated for authentication & authorization`);
});

export default app; 