const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 4003;

// Configure CORS with specific origins
app.use(cors({
    origin: [
        'http://localhost:3000',
        'http://localhost:4005',  // eCDome Intelligence
        'http://localhost:4006',  // Gamification
        'http://localhost:4007',  // Unified Integration
        'http://localhost:4008',  // Provider Dashboard
        'http://localhost:4009',  // Patient Dashboard
        'http://localhost:4011',  // Data Ingestion
        'http://localhost:4012',  // Biomarker GUI
        'http://localhost:8000',  // Telemedicine Platform
        'http://localhost:8080',  // API Gateway
    ],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        module: 'business-rules',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// Module info endpoint
app.get('/info', (req, res) => {
    res.json({
        id: 'business-rules',
        name: 'Business Rule Engine',
        version: '1.0.0',
        description: 'Conflict resolution and clinical decision support',
        endpoints: {
            health: '/health',
            info: '/info',
            api: '/api/v1'
        },
        dependencies: ['sdk-service'],
        capabilities: ['rule-management', 'conflict-resolution', 'decision-support']
    });
});

// Mock API endpoints
app.get('/api/v1/rules', (req, res) => {
    res.json({
        success: true,
        data: [
            { id: 'rule-001', name: 'Pain Management Rule', status: 'active' },
            { id: 'rule-002', name: 'Medication Interaction Rule', status: 'active' },
            { id: 'rule-003', name: 'Alert Threshold Rule', status: 'active' }
        ]
    });
});

app.post('/api/v1/conflicts/process', (req, res) => {
    res.json({
        success: true,
        data: {
            conflictId: 'conflict-001',
            resolution: 'automated-resolution',
            actions: ['alert-provider', 'update-patient-record'],
            timestamp: new Date().toISOString()
        }
    });
});

app.listen(PORT, () => {
    console.log(`Business Rules Health Server running on port ${PORT}`);
}); 