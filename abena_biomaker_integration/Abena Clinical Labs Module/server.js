const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 4012;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'biomarker-gui',
    timestamp: new Date().toISOString()
  });
});

// Biomarker GUI endpoints
app.get('/lab/tests', (req, res) => {
  res.json({
    tests: [
      'blood-test',
      'urine-test',
      'genetic-test',
      'microbiome-test',
      'metabolic-test'
    ]
  });
});

app.post('/lab/analyze', (req, res) => {
  // Mock lab analysis
  res.json({
    success: true,
    message: 'Lab analysis endpoint',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Biomarker GUI started on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});
