const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 4008;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'unified-integration',
    timestamp: new Date().toISOString()
  });
});

// Unified integration endpoints
app.get('/integrations', (req, res) => {
  res.json({
    integrations: [
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

app.post('/integrations/sync', (req, res) => {
  // Mock integration sync
  res.json({
    success: true,
    message: 'Integration sync endpoint',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Unified Integration started on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});
