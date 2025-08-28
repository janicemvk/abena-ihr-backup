const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'admin-dashboard',
    timestamp: new Date().toISOString()
  });
});

// Admin dashboard endpoints
app.get('/admin/overview', (req, res) => {
  res.json({
    overview: {
      totalPatients: 150,
      totalProviders: 25,
      activeAppointments: 45,
      systemHealth: 'excellent'
    }
  });
});

app.get('/admin/services', (req, res) => {
  res.json({
    services: [
      'auth-service',
      'sdk-service',
      'module-registry',
      'background-modules',
      'abena-ihr',
      'business-rules',
      'telemedicine',
      'ecdome-intelligence',
      'biomarker-integration',
      'provider-workflow',
      'unified-integration',
      'data-ingestion',
      'biomarker-gui'
    ]
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Admin Dashboard started on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});
