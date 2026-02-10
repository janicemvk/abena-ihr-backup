// ABENA IHR Platform - Realistic Mock Patient Data
// Based on provided medical cases for demonstration

export const mockPatients = {
  // Case 1: Cardiovascular Risk with Sleep Apnea
  patient_001: {
    id: 'ABENA-001',
    demographics: {
      firstName: 'Michael',
      lastName: 'Rodriguez',
      age: 46,
      gender: 'Male',
      height: '5\'10"',
      weight: 225,
      bmi: 32.3,
      bmiCategory: 'Obese Class I'
    },
    medicalHistory: {
      chiefComplaint: 'Occasional shortness of breath',
      conditions: [
        'Hypertension',
        'Obesity', 
        'Coronary artery disease',
        'Obstructive sleep apnea with heavy snoring'
      ],
      allergies: ['No known drug allergies (NKDA)']
    },
    medications: [
      { name: 'Atorvastatin', type: 'statin', purpose: 'cholesterol management' },
      { name: 'Lisinopril', type: 'ACE inhibitor', purpose: 'hypertension' },
      { name: 'HCTZ', type: 'diuretic', purpose: 'hypertension' }
    ],
    vitalSigns: {
      bloodPressure: '188/90 mmHg',
      heartRate: 88,
      temperature: 98.6,
      oxygenSaturation: 95
    },
    socialHistory: {
      occupation: 'Office job, sedentary',
      tobacco: '1 pack per day (PPD)',
      alcohol: '2 beers per week',
      exercise: 'Minimal physical activity',
      diet: 'Standard American diet'
    },
    endocannabinoidData: {
      levels: {
        anandamide: 0.45, // Low due to cardiovascular stress
        '2-AG': 0.38,     // Low due to inflammation
        PEA: 0.42,        // Low due to metabolic dysfunction
        OEA: 0.35         // Low due to obesity
      },
      receptorActivity: {
        CB1: 0.55,        // Reduced due to cardiovascular issues
        CB2: 0.48,        // Reduced due to inflammation
        TRPV1: 0.62,      // Elevated due to pain/inflammation
        GPR18: 0.40       // Low due to metabolic dysfunction
      },
      biomarkers: {
        inflammationMarkers: 0.75,  // High due to cardiovascular disease
        stressResponse: 0.68,       // High due to sleep apnea
        microbiomeHealth: 0.35,     // Poor due to diet and lifestyle
        metabolicHealth: 0.42        // Poor due to obesity and diabetes risk
      }
    },
    labResults: {
      cholesterol: { total: 245, ldl: 165, hdl: 35, triglycerides: 280 },
      glucose: { fasting: 110, hba1c: 5.8 },
      inflammatory: { crp: 4.2, esr: 28 },
      sleep: { apneaIndex: 25, oxygenDesaturation: 15 }
    }
  },

  // Case 2: Young Active Female with Low Back Pain
  patient_002: {
    id: 'ABENA-002',
    demographics: {
      firstName: 'Sarah',
      lastName: 'Chen',
      age: 32,
      gender: 'Female',
      height: '5\'6"',
      weight: 125,
      bmi: 20.2,
      bmiCategory: 'Normal'
    },
    medicalHistory: {
      chiefComplaint: 'Chronic low back pain with bilateral lower extremity radiculopathy',
      conditions: [
        'Chronic low back pain',
        'Bilateral lower extremity radiculopathy'
      ],
      allergies: ['No known drug allergies (NKDA)']
    },
    medications: [],
    vitalSigns: {
      bloodPressure: '110/74 mmHg',
      heartRate: 74,
      temperature: 98.4,
      oxygenSaturation: 98
    },
    socialHistory: {
      occupation: 'Works outside the home',
      tobacco: 'Non-smoker',
      alcohol: 'Not documented',
      exercise: 'Active lifestyle - regular walking, Pilates, and yoga',
      diet: 'Vegetarian, prepares meals at home',
      sleep: '5-6 hours per night, wakes at 6:00 AM'
    },
    endocannabinoidData: {
      levels: {
        anandamide: 0.72, // Good due to active lifestyle
        '2-AG': 0.68,     // Good due to regular exercise
        PEA: 0.75,        // Good due to vegetarian diet
        OEA: 0.70         // Good due to healthy lifestyle
      },
      receptorActivity: {
        CB1: 0.78,        // Good due to active lifestyle
        CB2: 0.82,        // Good due to exercise and diet
        TRPV1: 0.45,      // Elevated due to chronic pain
        GPR18: 0.70       // Good due to healthy lifestyle
      },
      biomarkers: {
        inflammationMarkers: 0.25,  // Low due to healthy lifestyle
        stressResponse: 0.35,       // Moderate due to pain
        microbiomeHealth: 0.85,     // Excellent due to vegetarian diet
        metabolicHealth: 0.88       // Excellent due to active lifestyle
      }
    },
    labResults: {
      inflammatory: { crp: 1.2, esr: 8 },
      pain: { painScore: 7, mobilityScore: 4 },
      musculoskeletal: { flexibility: 0.75, strength: 0.82 }
    }
  },

  // Case 3: Type 2 Diabetes with Complications
  patient_003: {
    id: 'ABENA-003',
    demographics: {
      firstName: 'Margaret',
      lastName: 'Thompson',
      age: 56,
      gender: 'Female',
      height: '5\'4"',
      weight: 190,
      bmi: 32.6,
      bmiCategory: 'Obese Class I'
    },
    medicalHistory: {
      chiefComplaint: 'Management of Type 2 Diabetes Mellitus with complications',
      conditions: [
        'Type 2 Diabetes Mellitus',
        'Diabetic peripheral neuropathy',
        'Hypertension',
        'Gastroesophageal reflux disease (GERD)',
        'Obesity'
      ],
      allergies: ['Iodine allergy (important for contrast studies)']
    },
    medications: [
      { name: 'Insulin', type: 'hormone', purpose: 'diabetes management' },
      { name: 'Atorvastatin', type: 'statin', purpose: 'cholesterol' },
      { name: 'Metoprolol', type: 'beta-blocker', purpose: 'hypertension' },
      { name: 'HCTZ', type: 'diuretic', purpose: 'hypertension' },
      { name: 'Amlodipine', type: 'calcium channel blocker', purpose: 'hypertension' }
    ],
    vitalSigns: {
      bloodPressure: '130/88 mmHg',
      heartRate: 80,
      temperature: 98.7,
      oxygenSaturation: 96
    },
    socialHistory: {
      occupation: 'Homemaker',
      tobacco: 'Non-smoker',
      alcohol: '1 glass of wine with dinner, 5 days per week',
      exercise: 'Sedentary, rarely exercises',
      diet: 'Standard diet including fish, beef, chicken, salads, breads, sweets'
    },
    endocannabinoidData: {
      levels: {
        anandamide: 0.38, // Low due to diabetes and metabolic dysfunction
        '2-AG': 0.42,     // Low due to diabetes complications
        PEA: 0.35,        // Low due to neuropathy
        OEA: 0.40         // Low due to metabolic dysfunction
      },
      receptorActivity: {
        CB1: 0.45,        // Reduced due to diabetes
        CB2: 0.52,        // Reduced due to complications
        TRPV1: 0.75,      // Elevated due to neuropathy pain
        GPR18: 0.38       // Low due to metabolic dysfunction
      },
      biomarkers: {
        inflammationMarkers: 0.68,  // High due to diabetes
        stressResponse: 0.55,        // High due to chronic disease
        microbiomeHealth: 0.45,      // Poor due to diet
        metabolicHealth: 0.25        // Very poor due to diabetes
      }
    },
    labResults: {
      diabetes: { hba1c: 7.0, fastingGlucose: 150, randomGlucose: 180 },
      cholesterol: { total: 220, ldl: 140, hdl: 38, triglycerides: 320 },
      kidney: { creatinine: 1.2, bun: 18, egfr: 58 },
      neuropathy: { nerveConduction: 0.35, sensation: 0.28 }
    }
  },

  // Case 4: Elderly with Multiple Comorbidities
  patient_004: {
    id: 'ABENA-004',
    demographics: {
      firstName: 'Robert',
      lastName: 'Williams',
      age: 72,
      gender: 'Male',
      height: '5\'8"',
      weight: 180,
      bmi: 27.4,
      bmiCategory: 'Overweight'
    },
    medicalHistory: {
      chiefComplaint: 'Multiple chronic conditions management',
      conditions: [
        'Hypertension',
        'Atrial fibrillation',
        'Chronic kidney disease stage 3',
        'Osteoarthritis',
        'Depression',
        'Mild cognitive impairment'
      ],
      allergies: ['Penicillin allergy']
    },
    medications: [
      { name: 'Warfarin', type: 'anticoagulant', purpose: 'atrial fibrillation' },
      { name: 'Metoprolol', type: 'beta-blocker', purpose: 'heart rate control' },
      { name: 'Lisinopril', type: 'ACE inhibitor', purpose: 'hypertension' },
      { name: 'Sertraline', type: 'SSRI', purpose: 'depression' },
      { name: 'Acetaminophen', type: 'analgesic', purpose: 'pain management' }
    ],
    vitalSigns: {
      bloodPressure: '145/85 mmHg',
      heartRate: 65,
      temperature: 98.2,
      oxygenSaturation: 94
    },
    socialHistory: {
      occupation: 'Retired',
      tobacco: 'Former smoker (quit 10 years ago)',
      alcohol: '1-2 glasses wine per week',
      exercise: 'Light walking, 2-3 times per week',
      diet: 'Mediterranean diet, reduced sodium'
    },
    endocannabinoidData: {
      levels: {
        anandamide: 0.52, // Moderate due to age and conditions
        '2-AG': 0.48,     // Moderate due to chronic conditions
        PEA: 0.55,        // Moderate due to inflammation
        OEA: 0.50         // Moderate due to metabolic changes
      },
      receptorActivity: {
        CB1: 0.58,        // Reduced due to age and conditions
        CB2: 0.62,        // Moderate due to inflammation
        TRPV1: 0.65,      // Elevated due to chronic pain
        GPR18: 0.52       // Moderate due to age
      },
      biomarkers: {
        inflammationMarkers: 0.55,  // Moderate due to chronic conditions
        stressResponse: 0.45,       // Moderate due to depression
        microbiomeHealth: 0.60,     // Moderate due to age
        metabolicHealth: 0.55       // Moderate due to kidney disease
      }
    },
    labResults: {
      cardiac: { inr: 2.3, bnp: 450, troponin: 0.02 },
      kidney: { creatinine: 1.8, bun: 28, egfr: 35 },
      cognitive: { mmse: 24, clockDrawing: 3 },
      inflammatory: { crp: 3.5, esr: 22 }
    }
  },

  // Case 5: Young Adult with Mental Health Focus
  patient_005: {
    id: 'ABENA-005',
    demographics: {
      firstName: 'Alex',
      lastName: 'Johnson',
      age: 28,
      gender: 'Non-binary',
      height: '5\'7"',
      weight: 140,
      bmi: 21.9,
      bmiCategory: 'Normal'
    },
    medicalHistory: {
      chiefComplaint: 'Anxiety and depression management',
      conditions: [
        'Generalized anxiety disorder',
        'Major depressive disorder',
        'Insomnia',
        'Irritable bowel syndrome'
      ],
      allergies: ['No known drug allergies (NKDA)']
    },
    medications: [
      { name: 'Sertraline', type: 'SSRI', purpose: 'depression and anxiety' },
      { name: 'Lorazepam', type: 'benzodiazepine', purpose: 'anxiety (as needed)' },
      { name: 'Melatonin', type: 'supplement', purpose: 'sleep' }
    ],
    vitalSigns: {
      bloodPressure: '118/76 mmHg',
      heartRate: 82,
      temperature: 98.5,
      oxygenSaturation: 97
    },
    socialHistory: {
      occupation: 'Software developer',
      tobacco: 'Non-smoker',
      alcohol: 'Occasional social drinking',
      exercise: 'Yoga and meditation, irregular',
      diet: 'Plant-based, organic when possible',
      sleep: 'Irregular sleep schedule, 6-8 hours'
    },
    endocannabinoidData: {
      levels: {
        anandamide: 0.65, // Good due to young age
        '2-AG': 0.62,     // Good due to active lifestyle
        PEA: 0.70,        // Good due to plant-based diet
        OEA: 0.68         // Good due to healthy choices
      },
      receptorActivity: {
        CB1: 0.72,        // Good due to young age
        CB2: 0.75,        // Good due to healthy lifestyle
        TRPV1: 0.55,      // Elevated due to anxiety/stress
        GPR18: 0.68       // Good due to young age
      },
      biomarkers: {
        inflammationMarkers: 0.30,  // Low due to healthy lifestyle
        stressResponse: 0.75,       // High due to anxiety
        microbiomeHealth: 0.78,     // Good due to plant-based diet
        metabolicHealth: 0.82       // Good due to young age and lifestyle
      }
    },
    labResults: {
      mentalHealth: { phq9: 12, gad7: 15, sleepQuality: 4 },
      inflammatory: { crp: 1.8, esr: 12 },
      gastrointestinal: { calprotectin: 45, ibsScore: 8 }
    }
  }
};

// Real-time metrics for dashboard display
export const realTimeMetrics = {
  systemHealth: {
    overall: 'healthy',
    components: {
      ecbome: 'healthy',
      medicalDb: 'healthy', 
      intelligence: 'healthy',
      labResults: 'healthy'
    }
  },
  activePatients: Object.keys(mockPatients).length,
  alerts: [
    { id: 1, patient: 'ABENA-001', type: 'critical', message: 'Blood pressure elevated - 188/90 mmHg' },
    { id: 2, patient: 'ABENA-003', type: 'warning', message: 'HbA1c above target - 7.0%' },
    { id: 3, patient: 'ABENA-004', type: 'info', message: 'Medication review due' }
  ],
  recentActivity: [
    { time: '10:30 AM', patient: 'ABENA-002', action: 'Endocannabinoid analysis completed' },
    { time: '10:15 AM', patient: 'ABENA-001', action: 'Vital signs updated' },
    { time: '09:45 AM', patient: 'ABENA-003', action: 'Lab results received' }
  ]
};

export default mockPatients;
