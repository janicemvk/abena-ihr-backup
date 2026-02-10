const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 4006;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'biomarker-integration',
    timestamp: new Date().toISOString()
  });
});

// Biomarker endpoints
app.get('/biomarkers', (req, res) => {
  res.json({
    biomarkers: [
      'glucose',
      'cholesterol',
      'blood-pressure',
      'heart-rate',
      'oxygen-saturation',
      'temperature'
    ]
  });
});

app.post('/biomarkers/analyze', (req, res) => {
  // Mock biomarker analysis
  res.json({
    success: true,
    message: 'Biomarker analysis endpoint',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Biomarker Integration started on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});
