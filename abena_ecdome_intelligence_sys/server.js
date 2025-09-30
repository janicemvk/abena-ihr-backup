const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 4005;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Serve static files from React build
app.use(express.static(path.join(__dirname, 'Abena_ecdome_intelligence_sys/build')));

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'ecdome-intelligence',
    timestamp: new Date().toISOString()
  });
});

// eCDome endpoints
app.get('/ecdome/analysis', (req, res) => {
  res.json({
    analysis: {
      modules: [
        'cardiovascular',
        'respiratory',
        'metabolic',
        'neurological',
        'immunological'
      ],
      status: 'active'
    }
  });
});

app.post('/ecdome/analyze', (req, res) => {
  // Mock analysis endpoint
  res.json({
    success: true,
    message: 'eCDome analysis endpoint',
    timestamp: new Date().toISOString()
  });
});

// Serve React app for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'Abena_ecdome_intelligence_sys/build/index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 eCDome Intelligence started on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});
