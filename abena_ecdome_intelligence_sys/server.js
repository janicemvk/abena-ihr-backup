const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 4005;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

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

// Start server
app.listen(PORT, () => {
  console.log(`🚀 eCDome Intelligence started on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});
