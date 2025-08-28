const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 4003;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'business-rule-engine',
    timestamp: new Date().toISOString()
  });
});

// Business rule endpoints
app.get('/rules', (req, res) => {
  res.json({
    rules: [
      'prescription-validation',
      'patient-data-access',
      'appointment-scheduling',
      'billing-validation',
      'clinical-decision-support'
    ]
  });
});

app.post('/rules/validate', (req, res) => {
  // Mock rule validation
  res.json({
    success: true,
    message: 'Rule validation endpoint',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Business Rule Engine started on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});
