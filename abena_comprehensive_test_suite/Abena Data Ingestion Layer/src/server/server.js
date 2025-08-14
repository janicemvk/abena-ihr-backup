const express = require('express');
const { abenaMiddleware, onDataIngested } = require('./middleware');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware for parsing JSON
app.use(express.json());

// Use Abena SDK middleware for all API routes - handles auth, privacy, and audit automatically
app.use('/api/v1/data', abenaMiddleware);

// Example data ingestion endpoint using pure Abena SDK
app.post('/api/v1/data/ingest', async (req, res) => {
  try {
    const data = req.body;
    const patientId = req.body.patientId || req.abenaContext?.patientId;
    const userId = req.abenaContext?.userId;
    
    // Validate required parameters
    if (!patientId || !userId) {
      return res.status(400).json({
        success: false,
        error: 'patientId and userId are required'
      });
    }
    
    // Process the ingested data
    console.log('Data ingested:', data);
    
    // Trigger eCBome correlation analysis using Abena SDK
    await onDataIngested(data, patientId, userId);
    
    res.status(200).json({
      success: true,
      message: 'Data ingested successfully',
      timestamp: new Date().toISOString(),
      patientId,
      userId
    });
  } catch (error) {
    console.error('Data ingestion error:', error);
    res.status(500).json({
      success: false,
      error: 'Data ingestion failed'
    });
  }
});

// Example endpoint using Abena SDK context
app.get('/api/v1/data/health', (req, res) => {
  res.json({
    status: 'healthy',
    abenaContext: req.abenaContext,
    timestamp: new Date().toISOString()
  });
});

// New endpoint demonstrating pure Abena SDK pattern
app.post('/api/v1/data/patient/:patientId/ecbome', async (req, res) => {
  try {
    const { patientId } = req.params;
    const userId = req.abenaContext?.userId;
    const healthData = req.body;
    
    if (!userId) {
      return res.status(401).json({
        success: false,
        error: 'User authentication required'
      });
    }
    
    // This demonstrates the pure Abena SDK pattern in action
    // 1. Auto-handled auth & permissions (via middleware)
    // 2. Auto-handled privacy & encryption (via SDK)
    // 3. Auto-handled audit logging (via SDK)
    // 4. Focus on your business logic
    
    await onDataIngested(healthData, patientId, userId);
    
    res.status(200).json({
      success: true,
      message: 'eCBome analysis completed',
      patientId,
      userId,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('eCBome analysis error:', error);
    res.status(500).json({
      success: false,
      error: 'eCBome analysis failed'
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log('Using pure Abena SDK for all operations');
  console.log('No custom auth, security, or data handling APIs');
});

module.exports = app; 