const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 4007;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'provider-workflow',
    timestamp: new Date().toISOString()
  });
});

// Provider workflow endpoints
app.get('/workflows', (req, res) => {
  res.json({
    workflows: [
      'patient-intake',
      'consultation',
      'prescription-management',
      'follow-up',
      'referral'
    ]
  });
});

app.post('/workflows/execute', (req, res) => {
  // Mock workflow execution
  res.json({
    success: true,
    message: 'Workflow execution endpoint',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Provider Workflow Integration started on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});
