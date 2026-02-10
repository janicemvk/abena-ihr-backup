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

// Mock patient data for eCBome Intelligence System
export const mockPatients = {
  patient_001: {
    id: 'ABENA-001',
    demographics: {
      firstName: 'Michael',
      lastName: 'Rodriguez',
      age: 46,
      gender: 'Male',
      bmi: 32.3,
      bmiCategory: 'Obese Class I'
    },
    medicalHistory: {
      chiefComplaint: 'Occasional shortness of breath',
      conditions: ['Hypertension', 'Obesity', 'Coronary artery disease', 'Obstructive sleep apnea']
    },
    endocannabinoidData: {
      levels: {
        anandamide: 0.35,
        '2-AG': 0.28,
        PEA: 0.42,
        OEA: 0.38
      },
      receptorActivity: {
        CB1: 0.85,
        CB2: 0.72,
        TRPV1: 0.68,
        GPR18: 0.75
      },
      biomarkers: {
        microbiomeHealth: 0.65,
        inflammationMarkers: 0.45,
        stressResponse: 0.55
      }
    }
  },
  patient_002: {
    id: 'ABENA-002',
    demographics: {
      firstName: 'Sarah',
      lastName: 'Chen',
      age: 32,
      gender: 'Female',
      bmi: 20.2,
      bmiCategory: 'Normal'
    },
    medicalHistory: {
      chiefComplaint: 'Chronic low back pain with bilateral lower extremity radiculopathy',
      conditions: ['Chronic low back pain', 'Bilateral lower extremity radiculopathy']
    },
    endocannabinoidData: {
      levels: {
        anandamide: 0.42,
        '2-AG': 0.35,
        PEA: 0.48,
        OEA: 0.41
      },
      receptorActivity: {
        CB1: 0.78,
        CB2: 0.82,
        TRPV1: 0.75,
        GPR18: 0.68
      },
      biomarkers: {
        microbiomeHealth: 0.78,
        inflammationMarkers: 0.35,
        stressResponse: 0.42
      }
    }
  },
  patient_003: {
    id: 'ABENA-003',
    demographics: {
      firstName: 'Margaret',
      lastName: 'Thompson',
      age: 56,
      gender: 'Female',
      bmi: 32.6,
      bmiCategory: 'Obese Class I'
    },
    medicalHistory: {
      chiefComplaint: 'Management of Type 2 Diabetes Mellitus with complications',
      conditions: ['Type 2 Diabetes Mellitus', 'Diabetic peripheral neuropathy', 'Hypertension', 'GERD', 'Obesity']
    },
    endocannabinoidData: {
      levels: {
        anandamide: 0.28,
        '2-AG': 0.22,
        PEA: 0.35,
        OEA: 0.31
      },
      receptorActivity: {
        CB1: 0.65,
        CB2: 0.58,
        TRPV1: 0.62,
        GPR18: 0.55
      },
      biomarkers: {
        microbiomeHealth: 0.45,
        inflammationMarkers: 0.68,
        stressResponse: 0.72
      }
    }
  },
  patient_004: {
    id: 'ABENA-004',
    demographics: {
      firstName: 'Robert',
      lastName: 'Williams',
      age: 72,
      gender: 'Male',
      bmi: 27.4,
      bmiCategory: 'Overweight'
    },
    medicalHistory: {
      chiefComplaint: 'Multiple chronic conditions management',
      conditions: ['Hypertension', 'Atrial fibrillation', 'Chronic kidney disease', 'Osteoarthritis', 'Depression', 'Anxiety']
    },
    endocannabinoidData: {
      levels: {
        anandamide: 0.25,
        '2-AG': 0.18,
        PEA: 0.32,
        OEA: 0.28
      },
      receptorActivity: {
        CB1: 0.58,
        CB2: 0.52,
        TRPV1: 0.55,
        GPR18: 0.48
      },
      biomarkers: {
        microbiomeHealth: 0.38,
        inflammationMarkers: 0.75,
        stressResponse: 0.68
      }
    }
  },
  patient_005: {
    id: 'ABENA-005',
    demographics: {
      firstName: 'Alex',
      lastName: 'Johnson',
      age: 28,
      gender: 'Non-binary',
      bmi: 21.9,
      bmiCategory: 'Normal'
    },
    medicalHistory: {
      chiefComplaint: 'Anxiety and depression management',
      conditions: ['Generalized anxiety disorder', 'Major depressive disorder']
    },
    endocannabinoidData: {
      levels: {
        anandamide: 0.38,
        '2-AG': 0.32,
        PEA: 0.45,
        OEA: 0.39
      },
      receptorActivity: {
        CB1: 0.72,
        CB2: 0.68,
        TRPV1: 0.65,
        GPR18: 0.62
      },
      biomarkers: {
        microbiomeHealth: 0.72,
        inflammationMarkers: 0.28,
        stressResponse: 0.85
      }
    }
  }
};

// Use Case 2: Young Active Female with Low Back Pain as default
export const testPatientData = {
  id: mockPatients.patient_002.id,
  age: mockPatients.patient_002.demographics.age,
  gender: mockPatients.patient_002.demographics.gender,
  firstName: mockPatients.patient_002.demographics.firstName,
  lastName: mockPatients.patient_002.demographics.lastName,
  metrics: {
    endocannabinoidLevels: mockPatients.patient_002.endocannabinoidData.levels,
    receptorActivity: mockPatients.patient_002.endocannabinoidData.receptorActivity,
    microbiomeHealth: mockPatients.patient_002.endocannabinoidData.biomarkers.microbiomeHealth,
    inflammationMarkers: mockPatients.patient_002.endocannabinoidData.biomarkers.inflammationMarkers,
    stressResponse: mockPatients.patient_002.endocannabinoidData.biomarkers.stressResponse
  },
  medications: mockPatients.patient_002.medications,
  medicalHistory: mockPatients.patient_002.medicalHistory,
  vitalSigns: mockPatients.patient_002.vitalSigns
}; 