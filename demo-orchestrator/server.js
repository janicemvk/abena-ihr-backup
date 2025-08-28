const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const http = require('http');
const socketIo = require('socket.io');
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Demo Configuration - Existing Services
const DEMO_SERVICES = {
  telemedicine: { port: 8000, url: 'http://localhost:8000', name: 'Telemedicine Platform' },
  ecdome: { port: 4005, url: 'http://localhost:4005', name: 'eCDome Intelligence' },
  provider: { port: 4008, url: 'http://localhost:4008', name: 'Provider Dashboard' },
  patient: { port: 4009, url: 'http://localhost:4009', name: 'Patient Dashboard' },
  ihr: { port: 4002, url: 'http://localhost:4002', name: 'ABENA IHR' },
  gamification: { port: 4006, url: 'http://localhost:4006', name: 'Gamification System' }
};

// Demo Orchestration Service
class DemoOrchestrator {
  constructor() {
    this.currentDemo = null;
    this.demoSteps = [];
    this.activeConnections = new Map();
  }

  // Demo Scenarios
  getDemoScenarios() {
    return {
      'data-analysis-flow': {
        name: 'Data Analysis & Blockchain Flow',
        description: 'Shows mock data → analysis → recommendations → blockchain',
        steps: [
          {
            id: 'step1',
            title: 'Data Ingestion',
            description: 'Mock patient data from wearables, EMR, and telemedicine',
            service: 'telemedicine',
            action: 'show-data-ingestion',
            duration: 3000
          },
          {
            id: 'step2',
            title: 'eCDome Analysis',
            description: 'Real-time biological system analysis and predictions',
            service: 'ecdome',
            action: 'show-analysis',
            duration: 4000
          },
          {
            id: 'step3',
            title: 'Clinical Recommendations',
            description: 'Science-supported treatment suggestions',
            service: 'provider',
            action: 'show-recommendations',
            duration: 3000
          },
          {
            id: 'step4',
            title: 'Blockchain Storage',
            description: 'Secure data triage and blockchain storage',
            service: 'ihr',
            action: 'show-blockchain',
            duration: 3000
          }
        ]
      },
      'provider-education': {
        name: 'Provider Education Chatbot',
        description: 'Demonstrates AI-powered provider education',
        steps: [
          {
            id: 'step1',
            title: 'Provider Login',
            description: 'Access provider dashboard with role-based authentication',
            service: 'provider',
            action: 'show-provider-login',
            duration: 2000
          },
          {
            id: 'step2',
            title: 'eCDome Chatbot',
            description: 'AI assistant explaining biological metrics and research',
            service: 'ecdome',
            action: 'show-chatbot',
            duration: 5000
          },
          {
            id: 'step3',
            title: 'Clinical Decision Support',
            description: 'Real-time clinical recommendations and alerts',
            service: 'provider',
            action: 'show-decision-support',
            duration: 4000
          }
        ]
      },
      'patient-education': {
        name: 'Patient Education & Engagement',
        description: 'Shows patient education and gamification features',
        steps: [
          {
            id: 'step1',
            title: 'Patient Dashboard',
            description: 'Personal health record and metrics visualization',
            service: 'patient',
            action: 'show-patient-dashboard',
            duration: 3000
          },
          {
            id: 'step2',
            title: 'Health Education',
            description: 'Patient-friendly explanations of health data',
            service: 'patient',
            action: 'show-education',
            duration: 4000
          },
          {
            id: 'step3',
            title: 'Gamification',
            description: 'Engagement through gamified health tracking',
            service: 'gamification',
            action: 'show-gamification',
            duration: 3000
          }
        ]
      }
    };
  }

  async startDemo(scenarioId, socket) {
    const scenarios = this.getDemoScenarios();
    const scenario = scenarios[scenarioId];
    
    if (!scenario) {
      throw new Error(`Demo scenario '${scenarioId}' not found`);
    }

    this.currentDemo = {
      id: uuidv4(),
      scenario: scenario,
      currentStep: 0,
      socket: socket,
      startTime: new Date()
    };

    // Notify all connected clients
    io.emit('demo-started', {
      demoId: this.currentDemo.id,
      scenario: scenario,
      timestamp: new Date().toISOString()
    });

    // Execute demo steps
    await this.executeDemoSteps(scenario.steps, socket);
  }

  async executeDemoSteps(steps, socket) {
    for (let i = 0; i < steps.length; i++) {
      const step = steps[i];
      
      // Update current step
      this.currentDemo.currentStep = i;
      
      // Notify clients of step progress
      io.emit('demo-step-progress', {
        step: step,
        stepNumber: i + 1,
        totalSteps: steps.length,
        timestamp: new Date().toISOString()
      });

      // Execute step action
      await this.executeStepAction(step, socket);
      
      // Wait for step duration
      await this.delay(step.duration);
    }

    // Demo completed
    io.emit('demo-completed', {
      demoId: this.currentDemo.id,
      timestamp: new Date().toISOString()
    });

    this.currentDemo = null;
  }

  async executeStepAction(step, socket) {
    switch (step.action) {
      case 'show-data-ingestion':
        await this.showDataIngestion(socket);
        break;
      case 'show-analysis':
        await this.showECdomeAnalysis(socket);
        break;
      case 'show-recommendations':
        await this.showClinicalRecommendations(socket);
        break;
      case 'show-blockchain':
        await this.showBlockchainStorage(socket);
        break;
      case 'show-provider-login':
        await this.showProviderLogin(socket);
        break;
      case 'show-chatbot':
        await this.showECdomeChatbot(socket);
        break;
      case 'show-decision-support':
        await this.showDecisionSupport(socket);
        break;
      case 'show-patient-dashboard':
        await this.showPatientDashboard(socket);
        break;
      case 'show-education':
        await this.showPatientEducation(socket);
        break;
      case 'show-gamification':
        await this.showGamification(socket);
        break;
    }
  }

  // Step Action Implementations
  async showDataIngestion(socket) {
    const mockData = this.generateMockPatientData();
    socket.emit('data-ingestion', {
      data: mockData,
      source: 'wearables, EMR, telemedicine',
      timestamp: new Date().toISOString()
    });
  }

  async showECdomeAnalysis(socket) {
    const analysis = this.generateECdomeAnalysis();
    socket.emit('ecdome-analysis', {
      analysis: analysis,
      predictions: this.generatePredictions(),
      timestamp: new Date().toISOString()
    });
  }

  async showClinicalRecommendations(socket) {
    const recommendations = this.generateClinicalRecommendations();
    socket.emit('clinical-recommendations', {
      recommendations: recommendations,
      evidence: this.generateScientificEvidence(),
      timestamp: new Date().toISOString()
    });
  }

  async showBlockchainStorage(socket) {
    const blockchainData = this.generateBlockchainData();
    socket.emit('blockchain-storage', {
      transaction: blockchainData,
      triage: this.generateDataTriage(),
      timestamp: new Date().toISOString()
    });
  }

  async showProviderLogin(socket) {
    socket.emit('provider-login', {
      credentials: { email: 'dr.johnson@abena.com', role: 'provider' },
      timestamp: new Date().toISOString()
    });
  }

  async showECdomeChatbot(socket) {
    const chatbotMessages = [
      { type: 'bot', content: 'Hello! I\'m your eCDome analysis assistant. How can I help you understand the patient\'s endocannabinoid system data?' },
      { type: 'user', content: 'Can you explain anandamide levels?' },
      { type: 'bot', content: 'Anandamide is often called the "bliss molecule" because it helps regulate mood and feelings of happiness. Your patient\'s levels are being monitored to help optimize stress response and overall well-being.' }
    ];
    
    socket.emit('ecdome-chatbot', {
      messages: chatbotMessages,
      timestamp: new Date().toISOString()
    });
  }

  async showDecisionSupport(socket) {
    const alerts = this.generateClinicalAlerts();
    socket.emit('decision-support', {
      alerts: alerts,
      recommendations: this.generateTreatmentRecommendations(),
      timestamp: new Date().toISOString()
    });
  }

  async showPatientDashboard(socket) {
    const patientData = this.generatePatientDashboardData();
    socket.emit('patient-dashboard', {
      data: patientData,
      timestamp: new Date().toISOString()
    });
  }

  async showPatientEducation(socket) {
    const educationContent = this.generatePatientEducation();
    socket.emit('patient-education', {
      content: educationContent,
      timestamp: new Date().toISOString()
    });
  }

  async showGamification(socket) {
    const gamificationData = this.generateGamificationData();
    socket.emit('gamification', {
      data: gamificationData,
      timestamp: new Date().toISOString()
    });
  }

  // Mock Data Generators
  generateMockPatientData() {
    return {
      patientId: 'DEMO-001',
      name: 'Sarah Johnson',
      vitalSigns: {
        heartRate: 72 + Math.random() * 20,
        bloodPressure: `${120 + Math.random() * 20}/${80 + Math.random() * 15}`,
        temperature: 98.6 + Math.random() * 2,
        oxygenSaturation: 95 + Math.random() * 5
      },
      ecdomeMetrics: {
        anandamide: 0.65 + Math.random() * 0.3,
        '2-AG': 0.58 + Math.random() * 0.25,
        CB1: 0.72 + Math.random() * 0.18,
        CB2: 0.68 + Math.random() * 0.15
      },
      wearableData: {
        steps: Math.floor(Math.random() * 10000),
        sleepHours: 6 + Math.random() * 4,
        stressLevel: Math.random()
      }
    };
  }

  generateECdomeAnalysis() {
    return {
      overallScore: 0.78 + Math.random() * 0.15,
      systemBalance: 0.75 + Math.random() * 0.2,
      predictions: [
        'Potential stress response within 2-4 hours',
        'Optimal sleep window: 10 PM - 6 AM',
        'Recommended exercise intensity: moderate'
      ]
    };
  }

  generatePredictions() {
    return [
      { type: 'stress', probability: 0.73, timeframe: '2-4 hours' },
      { type: 'inflammation', probability: 0.45, timeframe: '6-8 hours' },
      { type: 'sleep_optimization', probability: 0.88, timeframe: 'tonight' }
    ];
  }

  generateClinicalRecommendations() {
    return [
      {
        type: 'lifestyle',
        priority: 'high',
        description: 'Stress reduction techniques recommended',
        scientificBasis: 'Anandamide deficiency linked to stress disorders'
      },
      {
        type: 'supplementation',
        priority: 'medium',
        description: 'Omega-3 supplementation for anandamide support',
        scientificBasis: 'EPA/DHA precursors to endocannabinoid synthesis'
      }
    ];
  }

  generateScientificEvidence() {
    return [
      'Study: "Endocannabinoid System in Stress Response" (2023)',
      'Meta-analysis: "Omega-3 and Mood Regulation" (2022)',
      'Clinical Trial: "Sleep and Endocannabinoid Function" (2023)'
    ];
  }

  generateBlockchainData() {
    return {
      transactionId: uuidv4(),
      dataHash: '0x' + Math.random().toString(16).substr(2, 64),
      status: 'processing',
      timestamp: new Date().toISOString()
    };
  }

  generateDataTriage() {
    return {
      sensitivityLevel: 'CLINICAL',
      encryptionRequired: true,
      storageDestination: 'SECURE_VAULT',
      complianceFlags: ['HIPAA', 'GDPR']
    };
  }

  generateClinicalAlerts() {
    return [
      {
        id: 'alert-001',
        type: 'ecdome_imbalance',
        severity: 'warning',
        title: 'eCDome System Imbalance Detected',
        message: 'CB1 receptor activity is 15% below optimal range.'
      }
    ];
  }

  generateTreatmentRecommendations() {
    return [
      'Consider lifestyle intervention',
      'Monitor stress levels',
      'Optimize sleep hygiene'
    ];
  }

  generatePatientDashboardData() {
    return {
      ecdomeScore: 82,
      improvementThisWeek: 5,
      weeklyProgress: [78, 80, 79, 82, 85, 83, 82]
    };
  }

  generatePatientEducation() {
    return {
      topics: [
        'Understanding Your Endocannabinoid System',
        'How Sleep Affects Your Health',
        'Stress Management Techniques'
      ],
      currentTopic: 'Understanding Your Endocannabinoid System'
    };
  }

  generateGamificationData() {
    return {
      currentStreak: 12,
      achievements: ['First Week Complete', 'Sleep Goal Met'],
      points: 1250,
      level: 3
    };
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  stopDemo() {
    if (this.currentDemo) {
      io.emit('demo-stopped', {
        demoId: this.currentDemo.id,
        timestamp: new Date().toISOString()
      });
      this.currentDemo = null;
    }
  }
}

const orchestrator = new DemoOrchestrator();

// API Routes
app.get('/api/demo/scenarios', (req, res) => {
  res.json(orchestrator.getDemoScenarios());
});

app.get('/api/demo/status', (req, res) => {
  res.json({
    status: orchestrator.currentDemo ? 'running' : 'idle',
    currentDemo: orchestrator.currentDemo,
    services: DEMO_SERVICES
  });
});

app.post('/api/demo/start', (req, res) => {
  const { scenarioId } = req.body;
  if (!scenarioId) {
    return res.status(400).json({ error: 'scenarioId is required' });
  }
  
  res.json({ message: 'Demo starting...' });
});

app.post('/api/demo/stop', (req, res) => {
  orchestrator.stopDemo();
  res.json({ message: 'Demo stopped' });
});

// Socket.IO Events
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  socket.on('start-demo', async (data) => {
    try {
      await orchestrator.startDemo(data.scenarioId, socket);
    } catch (error) {
      socket.emit('demo-error', { error: error.message });
    }
  });
  
  socket.on('stop-demo', () => {
    orchestrator.stopDemo();
  });
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 4010;
server.listen(PORT, () => {
  console.log(`🎭 ABENA Demo Orchestrator running on port ${PORT}`);
  console.log(`🔗 Access the orchestrator at: http://localhost:${PORT}`);
  console.log(`📋 Available demo scenarios:`);
  Object.entries(orchestrator.getDemoScenarios()).forEach(([id, scenario]) => {
    console.log(`   - ${id}: ${scenario.name}`);
  });
});
