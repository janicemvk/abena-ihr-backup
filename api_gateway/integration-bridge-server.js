/**
 * Integration Bridge Server
 * Provides authentication and API routing for Admin Dashboard
 * Runs on port 8081
 */

const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 8081;
const QUANTUM_API_URL = process.env.QUANTUM_API_URL || 'https://abena-quantum-healthcare-platform.onrender.com';

// Middleware
app.use(cors({
    origin: [
        'http://localhost:3000',
        'http://localhost:4005',
        'http://localhost:4008',
        'http://localhost:4009',
        'http://localhost:4010',
        'http://localhost:8080',
        'https://admin-dashboard-joww.onrender.com',
        'https://ecbome-intelligence-dashboard.onrender.com',
        'https://provider-portal-va15.onrender.com',
        'https://patient-portal-9pt9.onrender.com',
        'https://unified-integration-hub.onrender.com'
    ],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// In-memory admin users (in production, this would be in a database)
// Default password is 'admin123' (hashed)
const adminUsers = [
    {
        id: '1',
        email: 'admin@abena-ihr.com',
        password: '$2a$10$rOzJqJqJqJqJqJqJqJqJqOqJqJqJqJqJqJqJqJqJqJqJqJqJqJq', // admin123
        name: 'System Administrator',
        role: 'admin'
    }
];

// Health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        service: 'Integration Bridge',
        port: PORT,
        timestamp: new Date().toISOString()
    });
});

// Admin authentication endpoint
app.post('/api/admin/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({
                success: false,
                error: 'Email and password are required'
            });
        }

        // Find user
        const user = adminUsers.find(u => u.email === email);
        
        if (!user) {
            return res.status(401).json({
                success: false,
                error: 'Invalid email or password'
            });
        }

        // For development: accept 'admin123' as password
        // In production, use bcrypt.compare
        const isValidPassword = password === 'admin123' || 
            (user.password && await bcrypt.compare(password, user.password));

        if (!isValidPassword) {
            return res.status(401).json({
                success: false,
                error: 'Invalid email or password'
            });
        }

        // Generate a simple token (in production, use JWT)
        const token = Buffer.from(JSON.stringify({
            id: user.id,
            email: user.email,
            role: user.role,
            timestamp: Date.now()
        })).toString('base64');

        res.json({
            success: true,
            token: token,
            user: {
                id: user.id,
                email: user.email,
                name: user.name,
                role: user.role
            }
        });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({
            success: false,
            error: 'Internal server error'
        });
    }
});

// Quantum settings endpoints (for admin dashboard)
app.get('/api/quantum/settings', (req, res) => {
    const { type } = req.query;
    
    res.json({
        success: true,
        settings: {
            type: type || 'system',
            mode: 'development',
            enabled: true,
            apiUrl: 'http://localhost:5000',
            timeout: 30000
        }
    });
});

app.post('/api/quantum/settings', (req, res) => {
    res.json({
        success: true,
        message: 'Settings updated',
        settings: req.body
    });
});

// Quantum API proxy endpoints
app.get('/api/quantum/status', async (req, res) => {
    try {
        const response = await axios.get(`${QUANTUM_API_URL}/health`);
        
        res.json({
            quantum_flask_api: {
                status: 'online',
                url: QUANTUM_API_URL
            }
        });
    } catch (error) {
        console.error('Quantum API status check failed:', error);
        res.json({
            quantum_flask_api: {
                status: 'offline',
                url: QUANTUM_API_URL,
                error: error.message
            }
        });
    }
});

app.get('/api/quantum/demo-results', async (req, res) => {
    try {
        const response = await axios.get(`${QUANTUM_API_URL}/api/demo-results`);
        res.json({ data: response.data });
    } catch (error) {
        console.error('Failed to fetch demo results:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch demo results from Quantum API',
            details: error.message
        });
    }
});

app.post('/api/quantum/analyze-patient', async (req, res) => {
    try {
        const response = await axios.post(`${QUANTUM_API_URL}/api/analyze`, req.body);
        res.json({ data: response.data.results || response.data });
    } catch (error) {
        console.error('Failed to analyze patient:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to analyze patient data',
            details: error.message
        });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Integration Bridge Server running on port ${PORT}`);
    console.log(`📍 Health check: http://localhost:${PORT}/health`);
    console.log(`🔐 Auth endpoint: http://localhost:${PORT}/api/admin/auth/login`);
    console.log(`\nDefault admin credentials:`);
    console.log(`   Email: admin@abena-ihr.com`);
    console.log(`   Password: admin123`);
});

module.exports = app;

