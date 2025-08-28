const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 4011;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'data-ingestion',
    timestamp: new Date().toISOString()
  });
});

// Data ingestion endpoints
app.get('/ingestion/status', (req, res) => {
  res.json({
    status: 'active',
    pipelines: [
      'patient-data',
      'clinical-data',
      'biomarker-data',
      'appointment-data'
    ]
  });
});

app.post('/ingestion/process', (req, res) => {
  // Mock data processing
  res.json({
    success: true,
    message: 'Data ingestion processing endpoint',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Data Ingestion started on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});
