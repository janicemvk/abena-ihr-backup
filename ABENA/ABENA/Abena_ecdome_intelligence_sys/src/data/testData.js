// Simulated IHR intelligence layer data
export const testIntelligenceData = [
  // Initial baseline data
  {
    timestamp: '2024-03-20T10:00:00Z',
    endocannabinoidLevels: {
      anandamide: 0.75,
      '2-AG': 0.65,
      PEA: 0.60,
      OEA: 0.55
    },
    receptorActivity: {
      CB1: 0.70,
      CB2: 0.65,
      TRPV1: 0.60,
      GPR18: 0.55
    },
    microbiomeHealth: 0.80,
    inflammationMarkers: 0.30,
    stressResponse: 0.35
  },
  // Simulated anomaly in endocannabinoid levels
  {
    timestamp: '2024-03-20T11:00:00Z',
    endocannabinoidLevels: {
      anandamide: 0.95, // Elevated
      '2-AG': 0.65,
      PEA: 0.60,
      OEA: 0.55
    },
    receptorActivity: {
      CB1: 0.70,
      CB2: 0.65,
      TRPV1: 0.60,
      GPR18: 0.55
    },
    microbiomeHealth: 0.80,
    inflammationMarkers: 0.30,
    stressResponse: 0.35
  },
  // Simulated inflammation response
  {
    timestamp: '2024-03-20T12:00:00Z',
    endocannabinoidLevels: {
      anandamide: 0.75,
      '2-AG': 0.65,
      PEA: 0.60,
      OEA: 0.55
    },
    receptorActivity: {
      CB1: 0.70,
      CB2: 0.85, // Elevated
      TRPV1: 0.60,
      GPR18: 0.55
    },
    microbiomeHealth: 0.80,
    inflammationMarkers: 0.75, // Elevated
    stressResponse: 0.35
  },
  // Simulated stress response
  {
    timestamp: '2024-03-20T13:00:00Z',
    endocannabinoidLevels: {
      anandamide: 0.75,
      '2-AG': 0.65,
      PEA: 0.60,
      OEA: 0.55
    },
    receptorActivity: {
      CB1: 0.70,
      CB2: 0.65,
      TRPV1: 0.60,
      GPR18: 0.55
    },
    microbiomeHealth: 0.80,
    inflammationMarkers: 0.30,
    stressResponse: 0.85 // Elevated
  },
  // Simulated microbiome disruption
  {
    timestamp: '2024-03-20T14:00:00Z',
    endocannabinoidLevels: {
      anandamide: 0.75,
      '2-AG': 0.65,
      PEA: 0.60,
      OEA: 0.55
    },
    receptorActivity: {
      CB1: 0.70,
      CB2: 0.65,
      TRPV1: 0.60,
      GPR18: 0.55
    },
    microbiomeHealth: 0.25, // Low
    inflammationMarkers: 0.30,
    stressResponse: 0.35
  }
];

// Test patient data
export const testPatientData = {
  id: 'TEST001',
  age: 45,
  gender: 'Female',
  metrics: {
    endocannabinoidLevels: {
      anandamide: 0.75,
      '2-AG': 0.65,
      PEA: 0.60,
      OEA: 0.55
    },
    receptorActivity: {
      CB1: 0.70,
      CB2: 0.65,
      TRPV1: 0.60,
      GPR18: 0.55
    },
    microbiomeHealth: 0.80,
    inflammationMarkers: 0.30,
    stressResponse: 0.35
  }
}; 