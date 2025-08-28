const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 3002;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'sdk-service',
    timestamp: new Date().toISOString()
  });
});

// SDK endpoints
app.get('/sdk/version', (req, res) => {
  res.json({
    version: '1.0.0',
    name: '@abena/sdk',
    description: 'Universal SDK for all Abena IHR modules'
  });
});

app.post('/sdk/authenticate', (req, res) => {
  // Mock authentication endpoint
  res.json({
    success: true,
    message: 'SDK authentication endpoint',
    timestamp: new Date().toISOString()
  });
});

app.get('/sdk/modules', (req, res) => {
  // Return available modules
  res.json({
    modules: [
      'authentication',
      'patient-management',
      'prescription-management',
      'appointment-management',
      'biomarker-integration',
      'ecdome-intelligence',
      'blockchain-audit',
      'privacy-controls'
    ]
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 SDK service started on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});
