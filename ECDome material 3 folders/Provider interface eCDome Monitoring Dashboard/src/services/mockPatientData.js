/**
 * Mock Patient Data Service
 * Based on 5 realistic patient cases for ABENA IHR Platform
 * This file contains comprehensive mock data to make all dashboard elements functional
 */

// Helper function to generate timestamps
const getTimestamp = (hoursAgo = 0) => {
  const date = new Date();
  date.setHours(date.getHours() - hoursAgo);
  return date.toISOString();
};

// Helper function to generate random vitals within range
const generateVitals = (baseHR, baseSystolic, baseDiastolic, baseTemp, baseO2) => ({
  heartRate: baseHR + Math.floor(Math.random() * 10 - 5),
  bloodPressure: `${baseSystolic + Math.floor(Math.random() * 10 - 5)}/${baseDiastolic + Math.floor(Math.random() * 10 - 5)}`,
  temperature: (baseTemp + (Math.random() * 1 - 0.5)).toFixed(1),
  oxygenSaturation: Math.min(100, baseO2 + Math.floor(Math.random() * 4 - 2)),
  respiratoryRate: 16 + Math.floor(Math.random() * 4)
});

/**
 * Mock Patients - Based on 5 real patient cases
 */
export const mockPatients = [
  {
    id: 'JANE_001',
    name: 'Jane (Investor Demo)',
    age: 44,
    gender: 'Female',
    status: 'active',
    riskLevel: 'high',
    lastVisit: getTimestamp(2),
    provider: 'Dr. Martinez',
    ecbomeScore: 0.62,
    mrn: 'MRN-DEMO-0001'
  },
  {
    id: 'PAT-001',
    name: 'James Wilson',
    age: 46,
    gender: 'Male',
    status: 'active',
    riskLevel: 'high',
    lastVisit: getTimestamp(24),
    provider: 'Dr. Martinez',
    ecbomeScore: 0.58,
    mrn: 'MRN-1001'
  },
  {
    id: 'PAT-002',
    name: 'Sarah Chen',
    age: 32,
    gender: 'Female',
    status: 'active',
    riskLevel: 'low',
    lastVisit: getTimestamp(48),
    provider: 'Dr. Martinez',
    ecbomeScore: 0.85,
    mrn: 'MRN-1002'
  },
  {
    id: 'PAT-003',
    name: 'Margaret Davis',
    age: 56,
    gender: 'Female',
    status: 'active',
    riskLevel: 'high',
    lastVisit: getTimestamp(12),
    provider: 'Dr. Martinez',
    ecbomeScore: 0.62,
    mrn: 'MRN-1003'
  },
  {
    id: 'PAT-004',
    name: 'Robert Thompson',
    age: 78,
    gender: 'Male',
    status: 'critical',
    riskLevel: 'high',
    lastVisit: getTimestamp(6),
    provider: 'Dr. Martinez',
    ecbomeScore: 0.45,
    mrn: 'MRN-1004'
  },
  {
    id: 'PAT-005',
    name: 'Emily Rodriguez',
    age: 28,
    gender: 'Female',
    status: 'active',
    riskLevel: 'medium',
    lastVisit: getTimestamp(72),
    provider: 'Dr. Martinez',
    ecbomeScore: 0.71,
    mrn: 'MRN-1005'
  }
];

/**
 * Detailed Patient Data - Full medical profiles
 */
export const mockPatientDetails = {
  'PAT-001': {
    // Case 1: Cardiovascular Risk with Sleep Apnea
    patientInfo: {
      id: 'PAT-001',
      name: 'James Wilson',
      age: 46,
      gender: 'Male',
      height: "5'10\"",
      weight: '225 lbs',
      bmi: 32.3,
      lastVisit: getTimestamp(24),
      provider: 'Dr. Martinez',
      status: 'active',
      riskLevel: 'high',
      ecbomeScore: 0.58,
      chiefComplaint: 'Occasional shortness of breath',
      vitalSigns: {
        heartRate: 88,
        bloodPressure: '188/90',
        temperature: 98.2,
        oxygenSaturation: 93,
        respiratoryRate: 18,
        bpCategory: 'Stage 2 Hypertension'
      },
      medications: [
        { name: 'Atorvastatin', dosage: '40mg', frequency: 'Once daily', indication: 'Cholesterol management' },
        { name: 'Lisinopril', dosage: '20mg', frequency: 'Once daily', indication: 'Hypertension' },
        { name: 'HCTZ', dosage: '25mg', frequency: 'Once daily', indication: 'Hypertension/Diuretic' }
      ],
      allergies: ['No known drug allergies (NKDA)'],
      conditions: [
        'Hypertension',
        'Obesity (Class I)',
        'Coronary artery disease',
        'Obstructive sleep apnea'
      ],
      socialHistory: {
        occupation: 'Office job, sedentary',
        tobacco: '1 pack per day (PPD)',
        alcohol: '2 beers per week',
        exercise: 'Minimal physical activity',
        diet: 'Standard American diet'
      },
      labResults: {
        lastUpdated: getTimestamp(168), // 1 week ago
        testDate: new Date(Date.now() - 168 * 60 * 60 * 1000).toLocaleDateString(),
        results: {
          // Lipid Panel - Cardiovascular Risk
          'Total Cholesterol': { value: 245, unit: 'mg/dL', status: 'high', reference: '<200' },
          'LDL Cholesterol': { value: 165, unit: 'mg/dL', status: 'high', reference: '<100' },
          'HDL Cholesterol': { value: 38, unit: 'mg/dL', status: 'low', reference: '>40' },
          'Triglycerides': { value: 210, unit: 'mg/dL', status: 'high', reference: '<150' },
          'Cholesterol/HDL Ratio': { value: 6.4, unit: 'ratio', status: 'high', reference: '<5.0' },
          
          // Metabolic Panel
          'Fasting Glucose': { value: 102, unit: 'mg/dL', status: 'borderline', reference: '70-99' },
          'HbA1c': { value: 5.8, unit: '%', status: 'prediabetic', reference: '<5.7' },
          'Insulin': { value: 18, unit: 'μU/mL', status: 'elevated', reference: '2.6-24.9' },
          
          // Cardiovascular Markers
          'hs-CRP': { value: 4.2, unit: 'mg/L', status: 'high', reference: '<3.0' },
          'Homocysteine': { value: 14, unit: 'μmol/L', status: 'elevated', reference: '<13' },
          'BNP': { value: 125, unit: 'pg/mL', status: 'borderline', reference: '<100' },
          
          // Liver Function - Statin Monitoring
          'ALT': { value: 42, unit: 'U/L', status: 'normal', reference: '7-56' },
          'AST': { value: 38, unit: 'U/L', status: 'normal', reference: '10-40' },
          
          // Kidney Function - Hypertension Impact
          'Creatinine': { value: 1.1, unit: 'mg/dL', status: 'normal', reference: '0.7-1.3' },
          'eGFR': { value: 78, unit: 'mL/min', status: 'mildly decreased', reference: '>90' },
          'BUN': { value: 22, unit: 'mg/dL', status: 'normal', reference: '7-20' },
          
          // Complete Blood Count
          'WBC': { value: 7.8, unit: '10³/μL', status: 'normal', reference: '4.5-11.0' },
          'Hemoglobin': { value: 15.2, unit: 'g/dL', status: 'normal', reference: '13.5-17.5' },
          'Platelets': { value: 245, unit: '10³/μL', status: 'normal', reference: '150-400' }
        }
      },
      medicalHistory: {
        pastMedicalHistory: [
          { condition: 'Hypertension', diagnosedDate: '2018-03-15', diagnosedBy: 'Dr. Martinez', status: 'Active', severity: 'Stage 2', notes: 'Requires triple therapy for control' },
          { condition: 'Obesity Class I', diagnosedDate: '2015-06-20', diagnosedBy: 'Dr. Martinez', status: 'Active', severity: 'BMI 32.3', notes: 'Weight management counseling ongoing' },
          { condition: 'Coronary Artery Disease', diagnosedDate: '2019-11-08', diagnosedBy: 'Dr. Cardiology Specialist', status: 'Active', severity: 'Moderate stenosis', notes: '40% LAD stenosis on catheterization' },
          { condition: 'Obstructive Sleep Apnea', diagnosedDate: '2020-02-12', diagnosedBy: 'Dr. Sleep Specialist', status: 'Active', severity: 'Moderate-Severe (AHI 35)', notes: 'CPAP therapy - compliance variable' },
          { condition: 'Hyperlipidemia', diagnosedDate: '2017-08-22', diagnosedBy: 'Dr. Martinez', status: 'Active', severity: 'High', notes: 'On statin therapy, LDL remains elevated' }
        ],
        surgicalHistory: [
          { procedure: 'Cardiac Catheterization with Angiography', date: '2019-11-15', facility: 'St. Mary\'s Medical Center', surgeon: 'Dr. Interventional Cardiologist', outcome: 'Successful - No stent placed', complications: 'None', notes: 'Revealed 40% LAD stenosis, medical management recommended. Femoral access site, no complications.' },
          { procedure: 'Polysomnography (Sleep Study)', date: '2020-02-08', facility: 'Regional Sleep Medicine Center', provider: 'Dr. Sleep Specialist', outcome: 'Diagnosed severe OSA', notes: 'AHI 35 events/hour, multiple oxygen desaturations. CPAP therapy initiated at 10-12 cmH2O.' },
          { procedure: 'Dental Extraction (Wisdom Teeth)', date: '2010-07-22', facility: 'Dental Associates', provider: 'Dr. Oral Surgeon', outcome: 'Uncomplicated', notes: 'All four wisdom teeth removed, healed without issues' }
        ],
        allergiesDetailed: [
          { allergen: 'No Known Drug Allergies', type: 'Medication', reaction: 'None', severity: 'N/A', dateReported: '2018-03-15', verifiedBy: 'Dr. Martinez' }
        ],
        familyHistory: {
          father: { conditions: 'Myocardial infarction at age 52 (deceased age 65), Type 2 Diabetes, Hypertension', alive: false },
          mother: { conditions: 'Hypertension, Stroke at age 68, currently living with residual weakness', alive: true, age: 72 },
          siblings: { summary: 'One brother - Hypertension diagnosed at age 44, on medication' },
          children: { summary: 'Two children - ages 18 and 20, healthy' },
          notes: 'Strong family history of premature cardiovascular disease and metabolic disorders. Significant genetic risk factors.'
        },
        previousReports: [
          { 
            id: 'RPT-PAT001-001',
            type: 'Cardiac Stress Test Report',
            date: '2023-09-15',
            provider: 'Dr. Robert Cardiovascular, MD - Cardiology',
            facility: 'Heart Center Cardiology',
            summary: 'Bruce protocol stress test terminated at 8 minutes due to chest discomfort and significant ST depressions. Peak HR 155 bpm (85% predicted max). Blood pressure response appropriate.',
            findings: [
              'Test terminated early due to chest discomfort',
              'ST segment depression 2mm in leads V4-V6 at peak exercise',
              'No ventricular arrhythmias observed',
              'Duke Treadmill Score: -4 (intermediate risk)',
              'Recommend cardiac catheterization for further evaluation'
            ],
            impression: 'Positive stress test for inducible myocardial ischemia. High probability of significant coronary artery disease.',
            downloadable: true,
            fileSize: '245 KB'
          },
          {
            id: 'RPT-PAT001-002',
            type: 'Echocardiogram Report',
            date: '2023-09-20',
            provider: 'Dr. Sarah Johnson, MD - Cardiology',
            facility: 'Heart Center Cardiology',
            summary: 'Transthoracic echocardiogram demonstrates preserved left ventricular systolic function with ejection fraction of 55%. Mild concentric left ventricular hypertrophy noted.',
            findings: [
              'Left ventricular ejection fraction: 55% (normal)',
              'Mild concentric LV hypertrophy (wall thickness 12mm)',
              'Grade I diastolic dysfunction (impaired relaxation)',
              'Aortic valve: Trileaflet, mild sclerosis, no stenosis',
              'Mitral valve: Normal structure and function',
              'No pericardial effusion',
              'Right ventricular size and function normal'
            ],
            impression: 'Normal systolic function. Mild LVH consistent with hypertensive heart disease. Grade I diastolic dysfunction.',
            downloadable: true,
            fileSize: '512 KB'
          },
          {
            id: 'RPT-PAT001-003',
            type: 'Sleep Study Report (Polysomnography)',
            date: '2020-02-10',
            provider: 'Dr. Michael Sleep, MD - Sleep Medicine',
            facility: 'Regional Sleep Medicine Center',
            summary: 'Overnight polysomnography demonstrates severe obstructive sleep apnea with frequent oxygen desaturations and sleep fragmentation. CPAP titration study recommended.',
            findings: [
              'Total sleep time: 6.2 hours',
              'Sleep efficiency: 72% (low)',
              'AHI (Apnea-Hypopnea Index): 35 events/hour (severe OSA)',
              'Lowest oxygen saturation: 82%',
              'Average oxygen saturation: 91%',
              'REM sleep severely fragmented',
              'Multiple arousals due to respiratory events',
              'CPAP pressure 10-12 cmH2O recommended'
            ],
            impression: 'Severe obstructive sleep apnea requiring CPAP therapy. Significant cardiovascular risk if untreated.',
            recommendations: 'CPAP therapy initiated, follow-up compliance check in 4 weeks',
            downloadable: true,
            fileSize: '1.2 MB'
          },
          {
            id: 'RPT-PAT001-004',
            type: 'Annual Physical Examination',
            date: '2024-10-15',
            provider: 'Dr. Martinez, MD - Internal Medicine',
            facility: 'ABENA Healthcare Clinic',
            summary: 'Comprehensive annual physical examination. Multiple cardiovascular risk factors poorly controlled. Smoking cessation counseling provided.',
            findings: [
              'Blood pressure: 188/90 mmHg (Stage 2 Hypertension)',
              'Weight: 225 lbs, BMI 32.3 (Class I Obesity)',
              'Heart: Regular rate and rhythm, no murmurs',
              'Lungs: Clear to auscultation bilaterally',
              'Extremities: No edema, pulses 2+ bilaterally',
              'Neurological: Grossly intact',
              'Skin: No concerning lesions'
            ],
            impression: 'Uncontrolled hypertension, obesity, active smoking, CAD, OSA. Requires medication adjustment and intensive lifestyle modification.',
            recommendations: 'Increase Lisinopril to 40mg, add Amlodipine 5mg, smoking cessation program referral, weight loss program, CPAP compliance check',
            downloadable: true,
            fileSize: '386 KB'
          }
        ],
        immunizations: [
          { vaccine: 'Influenza (Quadrivalent)', date: '2024-10-01', lot: 'FL2024-456789', manufacturer: 'Moderna', site: 'Left deltoid', provider: 'Dr. Martinez' },
          { vaccine: 'COVID-19 Booster (Bivalent)', date: '2024-09-15', lot: 'CV2024-789456', manufacturer: 'Pfizer', site: 'Left deltoid', provider: 'Dr. Martinez' },
          { vaccine: 'Pneumococcal (PPSV23)', date: '2023-03-20', lot: 'PN2023-123456', manufacturer: 'Merck', site: 'Right deltoid', provider: 'Dr. Martinez' },
          { vaccine: 'Tdap (Tetanus/Diphtheria/Pertussis)', date: '2022-06-10', lot: 'TD2022-456789', manufacturer: 'GSK', site: 'Left deltoid', provider: 'Nurse Practitioner' }
        ],
        hospitalizations: [
          { 
            admissionDate: '2019-11-08',
            dischargeDate: '2019-11-11',
            facility: 'St. Mary\'s Medical Center',
            reason: 'Chest pain - Rule out MI',
            diagnosis: 'Unstable angina, coronary artery disease',
            procedures: ['Cardiac catheterization', 'Angiography'],
            outcome: 'Stable, discharged on medical therapy',
            lengthOfStay: '3 days'
          }
        ]
      }
    },
    ecbomeProfile: {
      score: 0.58,
      status: 'Compromised',
      components: {
        endocannabinoid: { status: 'low', reading: 0.52, trend: 'declining' },
        metabolome: { status: 'low', reading: 0.58, trend: 'stable' },
        inflammatome: { status: 'elevated', reading: 0.42, trend: 'worsening' },
        immunome: { status: 'moderate', reading: 0.65, trend: 'stable' },
        chronobiome: { status: 'disrupted', reading: 0.48, trend: 'declining' },
        cardiovascular: { status: 'at-risk', reading: 0.45, trend: 'declining' },
        stress: { status: 'elevated', reading: 0.55, trend: 'stable' },
        microbiome: { status: 'imbalanced', reading: 0.60, trend: 'stable' },
        nutriome: { status: 'poor', reading: 0.50, trend: 'stable' },
        toxicome: { status: 'elevated', reading: 0.40, trend: 'worsening' },
        pharmacome: { status: 'active', reading: 0.70, trend: 'stable' },
        hormonal: { status: 'moderate', reading: 0.62, trend: 'stable' }
      }
    },
    alerts: [
      {
        id: 'ALT-001-1',
        type: 'critical',
        severity: 'high',
        title: 'Severe Hypertension Detected',
        message: 'Blood pressure 188/90 indicates Stage 2 Hypertension requiring immediate attention',
        timestamp: getTimestamp(2),
        recommendations: ['Medication adjustment', 'Lifestyle modifications', 'Close monitoring']
      },
      {
        id: 'ALT-001-2',
        type: 'warning',
        severity: 'medium',
        title: 'Sleep Apnea Impact on Cardiovascular Health',
        message: 'Untreated sleep apnea contributing to cardiovascular risk',
        timestamp: getTimestamp(24),
        recommendations: ['CPAP compliance check', 'Sleep study follow-up']
      },
      {
        id: 'ALT-001-3',
        type: 'warning',
        severity: 'medium',
        title: 'Tobacco Use - High Risk Factor',
        message: '1 PPD smoking significantly increases cardiovascular risk',
        timestamp: getTimestamp(24),
        recommendations: ['Smoking cessation program', 'Nicotine replacement therapy']
      }
    ],
    recommendations: [
      {
        id: 'REC-001-1',
        category: 'medication',
        priority: 'high',
        title: 'Consider Blood Pressure Medication Adjustment',
        description: 'Current BP 188/90 indicates inadequate control. Consider increasing Lisinopril or adding additional agent.',
        evidence: 'Based on JNC-8 guidelines for Stage 2 Hypertension'
      },
      {
        id: 'REC-001-2',
        category: 'lifestyle',
        priority: 'high',
        title: 'Smoking Cessation Program',
        description: 'Refer to tobacco cessation program. Smoking is a major modifiable risk factor.',
        evidence: 'Smoking cessation reduces cardiovascular events by 30-50%'
      },
      {
        id: 'REC-001-3',
        category: 'referral',
        priority: 'medium',
        title: 'Sleep Medicine Consultation',
        description: 'Optimize OSA treatment. Consider CPAP compliance assessment.',
        evidence: 'Treated OSA reduces cardiovascular morbidity'
      },
      {
        id: 'REC-001-4',
        category: 'lifestyle',
        priority: 'medium',
        title: 'Weight Management Program',
        description: 'BMI 32.3 - refer to structured weight loss program. Target 10% weight reduction.',
        evidence: 'Weight loss improves BP, lipids, and reduces cardiovascular risk'
      }
    ],
    timestamp: getTimestamp(0)
  },

  'PAT-002': {
    // Case 2: Young Active Female with Low Back Pain
    patientInfo: {
      id: 'PAT-002',
      name: 'Sarah Chen',
      age: 32,
      gender: 'Female',
      height: "5'6\"",
      weight: '125 lbs',
      bmi: 20.2,
      lastVisit: getTimestamp(48),
      provider: 'Dr. Martinez',
      status: 'active',
      riskLevel: 'low',
      ecbomeScore: 0.85,
      chiefComplaint: 'Chronic low back pain with bilateral lower extremity radiculopathy, progressively worsening',
      vitalSigns: {
        heartRate: 74,
        bloodPressure: '110/74',
        temperature: 98.4,
        oxygenSaturation: 99,
        respiratoryRate: 14,
        bpCategory: 'Normal'
      },
      medications: [
        { name: 'Ibuprofen', dosage: '400mg', frequency: 'As needed', indication: 'Pain management' }
      ],
      allergies: ['No known drug allergies (NKDA)'],
      conditions: [
        'Chronic low back pain',
        'Bilateral lower extremity radiculopathy'
      ],
      socialHistory: {
        occupation: 'Works outside the home',
        tobacco: 'Non-smoker',
        alcohol: 'Occasional',
        exercise: 'Active - walking, Pilates, yoga',
        diet: 'Vegetarian, home-cooked meals',
        sleep: '5-6 hours per night, wakes at 6:00 AM'
      },
      labResults: {
        lastUpdated: getTimestamp(720), // 30 days ago
        testDate: new Date(Date.now() - 720 * 60 * 60 * 1000).toLocaleDateString(),
        results: {
          // Lipid Panel - Healthy Profile
          'Total Cholesterol': { value: 165, unit: 'mg/dL', status: 'optimal', reference: '<200' },
          'LDL Cholesterol': { value: 95, unit: 'mg/dL', status: 'optimal', reference: '<100' },
          'HDL Cholesterol': { value: 58, unit: 'mg/dL', status: 'optimal', reference: '>40' },
          'Triglycerides': { value: 85, unit: 'mg/dL', status: 'optimal', reference: '<150' },
          
          // Metabolic Panel - Healthy
          'Fasting Glucose': { value: 88, unit: 'mg/dL', status: 'normal', reference: '70-99' },
          'HbA1c': { value: 5.2, unit: '%', status: 'normal', reference: '<5.7' },
          
          // Inflammatory Markers - Chronic Pain Related
          'hs-CRP': { value: 2.1, unit: 'mg/L', status: 'elevated', reference: '<1.0' },
          'ESR': { value: 18, unit: 'mm/hr', status: 'elevated', reference: '<20' },
          'IL-6': { value: 3.8, unit: 'pg/mL', status: 'elevated', reference: '<1.8' },
          
          // Vitamin D - Low Sleep Impact
          'Vitamin D': { value: 22, unit: 'ng/mL', status: 'insufficient', reference: '30-100' },
          'Vitamin B12': { value: 425, unit: 'pg/mL', status: 'normal', reference: '200-900' },
          
          // Complete Blood Count - Normal
          'WBC': { value: 6.2, unit: '10³/μL', status: 'normal', reference: '4.5-11.0' },
          'Hemoglobin': { value: 13.8, unit: 'g/dL', status: 'normal', reference: '12.0-16.0' },
          'Platelets': { value: 225, unit: '10³/μL', status: 'normal', reference: '150-400' },
          
          // Thyroid - Energy Levels
          'TSH': { value: 2.4, unit: 'mIU/L', status: 'normal', reference: '0.4-4.0' },
          'Free T4': { value: 1.2, unit: 'ng/dL', status: 'normal', reference: '0.8-1.8' }
        }
      },
      medicalHistory: {
        pastMedicalHistory: [
          { condition: 'Chronic Low Back Pain', diagnosedDate: '2022-01-10', diagnosedBy: 'Dr. Orthopedic Specialist', status: 'Active', severity: 'Moderate-Severe', notes: 'Bilateral lower extremity radiculopathy, progressively worsening' },
          { condition: 'Vitamin D Deficiency', diagnosedDate: '2023-06-15', diagnosedBy: 'Dr. Martinez', status: 'Active', severity: 'Insufficient (22 ng/mL)', notes: 'Likely contributing to fatigue and pain' }
        ],
        surgicalHistory: [
          { procedure: 'Lumbar MRI', date: '2022-01-25', facility: 'Imaging Center', provider: 'Dr. Radiologist', outcome: 'Completed', notes: 'Revealed L4-L5 and L5-S1 disc bulges without significant stenosis. Mild degenerative changes.' },
          { procedure: 'Physical Therapy Evaluation', date: '2022-02-10', facility: 'Sports Medicine Clinic', provider: 'Physical Therapist', outcome: 'Ongoing treatment', notes: '12-week PT program for core strengthening and flexibility. Moderate improvement noted.' }
        ],
        allergiesDetailed: [
          { allergen: 'No Known Drug Allergies', type: 'Medication', reaction: 'None', severity: 'N/A', dateReported: '2022-01-10', verifiedBy: 'Dr. Martinez' }
        ],
        familyHistory: {
          father: { conditions: 'Healthy, no significant medical history', alive: true, age: 58 },
          mother: { conditions: 'Osteoarthritis, managed with NSAIDs', alive: true, age: 56 },
          siblings: { summary: 'One sister - age 28, healthy' },
          children: { summary: 'No children' },
          notes: 'No significant family history of chronic disease. Mother has musculoskeletal issues.'
        },
        previousReports: [
          {
            id: 'RPT-PAT002-001',
            type: 'MRI Lumbar Spine Report',
            date: '2022-01-25',
            provider: 'Dr. James Radiologist, MD - Radiology',
            facility: 'Advanced Imaging Center',
            summary: 'MRI of the lumbar spine without contrast demonstrates multilevel degenerative disc disease with disc bulges at L4-L5 and L5-S1. No significant spinal stenosis or nerve root compression.',
            findings: [
              'L4-L5: Broad-based disc bulge, no significant canal stenosis',
              'L5-S1: Posterior disc bulge with mild bilateral foraminal narrowing',
              'Mild facet joint arthropathy L4-L5',
              'No disc herniation or extrusion',
              'Conus medullaris terminates normally at L1',
              'No evidence of infection or malignancy'
            ],
            impression: 'Multilevel degenerative disc disease, most pronounced at L4-L5 and L5-S1. Findings correlate with radicular symptoms.',
            recommendations: 'Conservative management with physical therapy. Consider epidural steroid injection if symptoms persist.',
            downloadable: true,
            fileSize: '2.8 MB'
          },
          {
            id: 'RPT-PAT002-002',
            type: 'Physical Therapy Progress Note',
            date: '2022-05-20',
            provider: 'Sarah Thompson, PT, DPT - Physical Therapy',
            facility: 'Sports Medicine and Rehabilitation Clinic',
            summary: 'Patient has completed 12 weeks of physical therapy focusing on core stabilization, flexibility, and posture correction. Moderate improvement in pain levels and function.',
            findings: [
              'Pain level decreased from 7/10 to 4/10',
              'Improved lumbar flexion range of motion',
              'Core strength improved (plank test: 30s → 90s)',
              'Better posture awareness',
              'Return to modified yoga practice',
              'Still experiences morning stiffness'
            ],
            impression: 'Moderate functional improvement with PT. Recommend continued home exercise program and periodic maintenance sessions.',
            recommendations: 'Continue home exercises 3x/week, maintain active lifestyle, avoid prolonged sitting, consider ergonomic workspace assessment',
            downloadable: true,
            fileSize: '128 KB'
          },
          {
            id: 'RPT-PAT002-003',
            type: 'Annual Wellness Visit',
            date: '2024-10-12',
            provider: 'Dr. Martinez, MD - Internal Medicine',
            facility: 'ABENA Healthcare Clinic',
            summary: 'Annual wellness examination. Patient is active and healthy overall. Back pain improved with exercise and PT. Vitamin D supplementation needed.',
            findings: [
              'Vital signs all within normal limits',
              'Weight stable at 125 lbs, BMI 20.2',
              'Back pain improved to 3/10 with exercise',
              'Excellent cardiovascular health',
              'Lipid panel optimal',
              'Vitamin D still low despite supplementation'
            ],
            impression: 'Healthy 32-year-old female with well-managed chronic back pain. Vitamin D deficiency requires higher dose supplementation.',
            recommendations: 'Increase Vitamin D to 5000 IU daily, continue active lifestyle, maintain PT home exercise program',
            downloadable: true,
            fileSize: '245 KB'
          }
        ],
        immunizations: [
          { vaccine: 'Influenza (Quadrivalent)', date: '2024-10-05', lot: 'FL2024-789123', manufacturer: 'Sanofi', site: 'Left deltoid', provider: 'Dr. Martinez' },
          { vaccine: 'COVID-19 Booster', date: '2024-04-10', lot: 'CV2024-456123', manufacturer: 'Moderna', site: 'Right deltoid', provider: 'Pharmacist' },
          { vaccine: 'Tdap', date: '2020-08-15', lot: 'TD2020-789456', manufacturer: 'GSK', site: 'Left deltoid', provider: 'Dr. Martinez' },
          { vaccine: 'HPV (Gardasil 9)', date: '2018-06-20', lot: 'HPV2018-123456', manufacturer: 'Merck', site: 'Left deltoid', provider: 'Dr. OB/GYN' }
        ],
        hospitalizations: []
      }
    },
    ecbomeProfile: {
      score: 0.85,
      status: 'Good',
      components: {
        endocannabinoid: { status: 'active', reading: 0.82, trend: 'stable' },
        metabolome: { status: 'optimal', reading: 0.88, trend: 'improving' },
        inflammatome: { status: 'moderate', reading: 0.65, trend: 'stable' },
        immunome: { status: 'strong', reading: 0.90, trend: 'stable' },
        chronobiome: { status: 'suboptimal', reading: 0.72, trend: 'stable' },
        cardiovascular: { status: 'healthy', reading: 0.92, trend: 'stable' },
        stress: { status: 'moderate', reading: 0.75, trend: 'stable' },
        microbiome: { status: 'balanced', reading: 0.85, trend: 'stable' },
        nutriome: { status: 'good', reading: 0.88, trend: 'stable' },
        toxicome: { status: 'low', reading: 0.90, trend: 'stable' },
        pharmacome: { status: 'minimal', reading: 0.95, trend: 'stable' },
        hormonal: { status: 'balanced', reading: 0.86, trend: 'stable' }
      }
    },
    alerts: [
      {
        id: 'ALT-002-1',
        type: 'info',
        severity: 'low',
        title: 'Sleep Deficit Detected',
        message: 'Chronic sleep restriction (5-6 hours) may impact recovery and pain perception',
        timestamp: getTimestamp(12),
        recommendations: ['Sleep hygiene counseling', 'Target 7-9 hours of sleep']
      }
    ],
    recommendations: [
      {
        id: 'REC-002-1',
        category: 'referral',
        priority: 'high',
        title: 'Neurology/Spine Specialist Referral',
        description: 'Progressive bilateral radiculopathy warrants imaging and specialist evaluation.',
        evidence: 'Early intervention for radiculopathy improves outcomes'
      },
      {
        id: 'REC-002-2',
        category: 'therapy',
        priority: 'high',
        title: 'Physical Therapy Evaluation',
        description: 'Structured PT program for core strengthening and pain management.',
        evidence: 'PT is first-line treatment for chronic low back pain'
      },
      {
        id: 'REC-002-3',
        category: 'imaging',
        priority: 'medium',
        title: 'MRI Lumbar Spine',
        description: 'Consider MRI to evaluate for disc herniation or nerve root compression.',
        evidence: 'Progressive radiculopathy indicates need for imaging'
      },
      {
        id: 'REC-002-4',
        category: 'lifestyle',
        priority: 'low',
        title: 'Sleep Optimization',
        description: 'Increase sleep duration to 7-9 hours. Poor sleep impacts pain and recovery.',
        evidence: 'Sleep improves pain tolerance and healing'
      }
    ],
    timestamp: getTimestamp(0)
  },

  'PAT-003': {
    // Case 3: Type 2 Diabetes with Complications
    patientInfo: {
      id: 'PAT-003',
      name: 'Margaret Davis',
      age: 56,
      gender: 'Female',
      height: "5'4\"",
      weight: '190 lbs',
      bmi: 32.6,
      lastVisit: getTimestamp(12),
      provider: 'Dr. Martinez',
      status: 'active',
      riskLevel: 'high',
      ecbomeScore: 0.62,
      chiefComplaint: 'Management of Type 2 Diabetes Mellitus with complications',
      vitalSigns: {
        heartRate: 80,
        bloodPressure: '130/88',
        temperature: 98.6,
        oxygenSaturation: 97,
        respiratoryRate: 16,
        bpCategory: 'Elevated'
      },
      medications: [
        { name: 'Insulin (Lantus)', dosage: '30 units', frequency: 'Once daily', indication: 'Diabetes' },
        { name: 'Atorvastatin', dosage: '40mg', frequency: 'Once daily', indication: 'Cholesterol' },
        { name: 'Metoprolol', dosage: '50mg', frequency: 'Twice daily', indication: 'Hypertension/Heart rate' },
        { name: 'HCTZ', dosage: '25mg', frequency: 'Once daily', indication: 'Hypertension' },
        { name: 'Amlodipine', dosage: '10mg', frequency: 'Once daily', indication: 'Hypertension' }
      ],
      allergies: ['Iodine allergy (important for contrast studies)'],
      conditions: [
        'Type 2 Diabetes Mellitus',
        'Diabetic peripheral neuropathy (bilateral feet/toes)',
        'Hypertension',
        'Gastroesophageal reflux disease (GERD)',
        'Obesity (Class I)'
      ],
      socialHistory: {
        occupation: 'Homemaker',
        tobacco: 'Non-smoker',
        alcohol: '1 glass of wine with dinner, 5 days per week',
        exercise: 'Sedentary, rarely exercises',
        diet: 'Standard diet - fish, beef, chicken, salads, breads, sweets'
      },
      labResults: {
        lastUpdated: getTimestamp(72), // 3 days ago
        testDate: new Date(Date.now() - 72 * 60 * 60 * 1000).toLocaleDateString(),
        results: {
          // Diabetes Panel - Comprehensive
          'Fasting Glucose': { value: 150, unit: 'mg/dL', status: 'high', reference: '70-99' },
          'HbA1c': { value: 7.0, unit: '%', status: 'suboptimal', reference: '<5.7 (normal), <7.0 (diabetic)' },
          'Fructosamine': { value: 285, unit: 'μmol/L', status: 'high', reference: '205-285' },
          'C-Peptide': { value: 2.8, unit: 'ng/mL', status: 'elevated', reference: '0.8-3.1' },
          'Insulin': { value: 24, unit: 'μU/mL', status: 'high', reference: '2.6-24.9' },
          
          // Lipid Panel - Diabetic Dyslipidemia
          'Total Cholesterol': { value: 198, unit: 'mg/dL', status: 'borderline', reference: '<200' },
          'LDL Cholesterol': { value: 115, unit: 'mg/dL', status: 'high', reference: '<70 (diabetic)' },
          'HDL Cholesterol': { value: 45, unit: 'mg/dL', status: 'low', reference: '>50 (female)' },
          'Triglycerides': { value: 190, unit: 'mg/dL', status: 'high', reference: '<150' },
          'VLDL': { value: 38, unit: 'mg/dL', status: 'high', reference: '<30' },
          
          // Kidney Function - Diabetic Nephropathy Screening
          'Creatinine': { value: 1.1, unit: 'mg/dL', status: 'borderline', reference: '0.6-1.2' },
          'eGFR': { value: 68, unit: 'mL/min', status: 'decreased', reference: '>90' },
          'BUN': { value: 24, unit: 'mg/dL', status: 'elevated', reference: '7-20' },
          'Microalbumin': { value: 45, unit: 'mg/24hr', status: 'elevated', reference: '<30' },
          'Urine Albumin/Creatinine': { value: 42, unit: 'mg/g', status: 'microalbuminuria', reference: '<30' },
          
          // Liver Function
          'ALT': { value: 48, unit: 'U/L', status: 'elevated', reference: '7-56' },
          'AST': { value: 44, unit: 'U/L', status: 'elevated', reference: '10-40' },
          'Bilirubin': { value: 0.9, unit: 'mg/dL', status: 'normal', reference: '0.1-1.2' },
          
          // Thyroid - Metabolic Function
          'TSH': { value: 3.2, unit: 'mIU/L', status: 'normal', reference: '0.4-4.0' },
          'Free T4': { value: 1.1, unit: 'ng/dL', status: 'normal', reference: '0.8-1.8' },
          
          // Complete Blood Count
          'WBC': { value: 8.2, unit: '10³/μL', status: 'normal', reference: '4.5-11.0' },
          'Hemoglobin': { value: 12.8, unit: 'g/dL', status: 'normal', reference: '12.0-16.0' },
          'Hemoglobin A1c': { value: 7.0, unit: '%', status: 'suboptimal', reference: '<5.7' },
          'Platelets': { value: 268, unit: '10³/μL', status: 'normal', reference: '150-400' }
        }
      },
      medicalHistory: {
        pastMedicalHistory: [
          { condition: 'Type 2 Diabetes Mellitus', diagnosedDate: '2015-08-10', diagnosedBy: 'Dr. Martinez', status: 'Active', severity: 'Moderate control (HbA1c 7.0%)', notes: 'On insulin therapy, struggles with diet compliance' },
          { condition: 'Diabetic Peripheral Neuropathy', diagnosedDate: '2019-03-22', diagnosedBy: 'Dr. Endocrinologist', status: 'Active', severity: 'Moderate', notes: 'Bilateral feet and toes, burning/tingling sensation' },
          { condition: 'Hypertension', diagnosedDate: '2016-02-15', diagnosedBy: 'Dr. Martinez', status: 'Active', severity: 'Stage 1', notes: 'On triple therapy, well controlled' },
          { condition: 'GERD', diagnosedDate: '2018-05-20', diagnosedBy: 'Dr. Gastroenterologist', status: 'Active', severity: 'Mild', notes: 'Controlled with PPI therapy' },
          { condition: 'Obesity Class I', diagnosedDate: '2014-01-15', diagnosedBy: 'Dr. Martinez', status: 'Active', severity: 'BMI 32.6', notes: 'Weight stable but not losing' }
        ],
        surgicalHistory: [
          { procedure: 'Upper Endoscopy (EGD)', date: '2018-06-10', facility: 'Gastroenterology Center', provider: 'Dr. GI Specialist', outcome: 'Normal findings', notes: 'Performed for GERD evaluation. No ulcers, Barrett\'s, or malignancy. Mild gastritis.' },
          { procedure: 'Ophthalmology Exam (Diabetic Retinopathy Screening)', date: '2024-08-15', facility: 'Eye Care Center', provider: 'Dr. Ophthalmologist', outcome: 'Mild non-proliferative diabetic retinopathy', notes: 'Annual screening shows early retinal changes. Close monitoring needed.' }
        ],
        allergiesDetailed: [
          { allergen: 'Iodine', type: 'Contrast Agent', reaction: 'Hives, itching', severity: 'Moderate', dateReported: '2017-04-12', verifiedBy: 'Dr. Radiologist', notes: 'Important for contrast studies - pre-medication protocol required' }
        ],
        familyHistory: {
          father: { conditions: 'Type 2 Diabetes (age 50), Hypertension, died at age 70 from stroke', alive: false },
          mother: { conditions: 'Type 2 Diabetes (age 55), Obesity, alive', alive: true, age: 78 },
          siblings: { summary: 'Two sisters - both with Type 2 Diabetes, one with hypertension' },
          children: { summary: 'Three adult children - one has prediabetes' },
          notes: 'Very strong family history of Type 2 Diabetes and metabolic syndrome. High genetic predisposition.'
        },
        previousReports: [
          {
            id: 'RPT-PAT003-001',
            type: 'Diabetes Management Review',
            date: '2024-06-15',
            provider: 'Dr. Emily Endocrine, MD - Endocrinology',
            facility: 'Diabetes Care Center',
            summary: 'Comprehensive diabetes review. HbA1c trending upward despite insulin therapy. Evidence of microvascular complications (neuropathy, early nephropathy). Intensification of therapy recommended.',
            findings: [
              'HbA1c 7.0% (target <7.0%)',
              'Fasting glucose average 140-160 mg/dL',
              'Postprandial spikes to 200+ mg/dL',
              'Microalbuminuria present (42 mg/g)',
              'Peripheral neuropathy symptoms bilateral feet',
              'Blood pressure 130/88 (elevated)',
              'Weight unchanged from last visit'
            ],
            impression: 'Type 2 Diabetes with emerging microvascular complications. Suboptimal glycemic control despite insulin therapy.',
            recommendations: 'Increase insulin dose, add GLP-1 agonist, dietary counseling, nephrology referral for microalbuminuria',
            downloadable: true,
            fileSize: '425 KB'
          },
          {
            id: 'RPT-PAT003-002',
            type: 'Ophthalmology Diabetic Eye Exam',
            date: '2024-08-15',
            provider: 'Dr. Vision Expert, MD - Ophthalmology',
            facility: 'Comprehensive Eye Care',
            summary: 'Dilated fundus examination reveals mild non-proliferative diabetic retinopathy in both eyes. No macular edema. Annual follow-up recommended.',
            findings: [
              'Visual acuity: 20/25 both eyes',
              'Intraocular pressure: Normal (14 mmHg OD, 13 mmHg OS)',
              'Mild non-proliferative diabetic retinopathy (NPDR)',
              'Few microaneurysms in peripheral retina',
              'No hemorrhages or exudates',
              'No macular edema',
              'Optic nerves: Normal cup-to-disc ratio'
            ],
            impression: 'Mild NPDR without macular involvement. Stable for now but requires annual monitoring.',
            recommendations: 'Continue tight glucose control, annual dilated exam, report any vision changes immediately',
            downloadable: true,
            fileSize: '890 KB'
          }
        ],
        immunizations: [
          { vaccine: 'Influenza', date: '2024-10-01', lot: 'FL2024-123456', manufacturer: 'Sanofi', site: 'Left deltoid', provider: 'Dr. Martinez' },
          { vaccine: 'COVID-19 Booster', date: '2024-05-20', lot: 'CV2024-654321', manufacturer: 'Moderna', site: 'Right deltoid', provider: 'Pharmacist' },
          { vaccine: 'Pneumococcal (PPSV23)', date: '2022-04-15', lot: 'PN2022-789456', manufacturer: 'Merck', site: 'Left deltoid', provider: 'Dr. Martinez' },
          { vaccine: 'Hepatitis B Series (Complete)', date: '2020-12-10', lot: 'HEP2020-456789', manufacturer: 'GSK', site: 'Right deltoid', provider: 'Dr. Martinez' }
        ],
        hospitalizations: [
          {
            admissionDate: '2021-06-15',
            dischargeDate: '2021-06-18',
            facility: 'Regional Medical Center',
            reason: 'Hyperglycemic crisis - Blood glucose >400 mg/dL',
            diagnosis: 'Diabetic ketoacidosis (DKA), dehydration',
            procedures: ['IV insulin drip', 'Fluid resuscitation', 'Electrolyte replacement'],
            outcome: 'Stabilized, insulin regimen adjusted',
            lengthOfStay: '3 days'
          }
        ]
      }
    },
    ecbomeProfile: {
      score: 0.62,
      status: 'Compromised',
      components: {
        endocannabinoid: { status: 'low', reading: 0.58, trend: 'stable' },
        metabolome: { status: 'disrupted', reading: 0.48, trend: 'stable' },
        inflammatome: { status: 'elevated', reading: 0.50, trend: 'stable' },
        immunome: { status: 'moderate', reading: 0.68, trend: 'stable' },
        chronobiome: { status: 'moderate', reading: 0.70, trend: 'stable' },
        cardiovascular: { status: 'at-risk', reading: 0.58, trend: 'stable' },
        stress: { status: 'moderate', reading: 0.72, trend: 'stable' },
        microbiome: { status: 'imbalanced', reading: 0.62, trend: 'stable' },
        nutriome: { status: 'poor', reading: 0.55, trend: 'stable' },
        toxicome: { status: 'moderate', reading: 0.68, trend: 'stable' },
        pharmacome: { status: 'active', reading: 0.65, trend: 'stable' },
        hormonal: { status: 'imbalanced', reading: 0.60, trend: 'stable' }
      }
    },
    alerts: [
      {
        id: 'ALT-003-1',
        type: 'warning',
        severity: 'medium',
        title: 'Suboptimal Diabetes Control',
        message: 'HbA1C 7.0% at goal but fasting glucose 150 mg/dL suggests glycemic variability',
        timestamp: getTimestamp(72),
        recommendations: ['Consider CGM', 'Insulin adjustment', 'Dietary counseling']
      },
      {
        id: 'ALT-003-2',
        type: 'warning',
        severity: 'medium',
        title: 'Peripheral Neuropathy Monitoring',
        message: 'Diabetic neuropathy present - requires ongoing assessment',
        timestamp: getTimestamp(12),
        recommendations: ['Foot care education', 'Podiatry referral', 'Pain management']
      },
      {
        id: 'ALT-003-3',
        type: 'info',
        severity: 'low',
        title: 'Sedentary Lifestyle',
        message: 'Physical activity could significantly improve diabetes management',
        timestamp: getTimestamp(12),
        recommendations: ['Exercise prescription', 'Cardiac clearance if needed']
      }
    ],
    recommendations: [
      {
        id: 'REC-003-1',
        category: 'medication',
        priority: 'medium',
        title: 'Consider GLP-1 Agonist Addition',
        description: 'Adding GLP-1 agonist could improve glycemic control and promote weight loss.',
        evidence: 'GLP-1 agonists reduce HbA1C and cardiovascular events in T2DM'
      },
      {
        id: 'REC-003-2',
        category: 'monitoring',
        priority: 'high',
        title: 'Continuous Glucose Monitoring',
        description: 'CGM would help identify glycemic variability and optimize insulin dosing.',
        evidence: 'CGM improves glycemic control in insulin-treated T2DM'
      },
      {
        id: 'REC-003-3',
        category: 'referral',
        priority: 'medium',
        title: 'Diabetes Education and Nutrition Counseling',
        description: 'Comprehensive diabetes education focusing on nutrition and carbohydrate management.',
        evidence: 'DSMES improves outcomes in diabetes management'
      },
      {
        id: 'REC-003-4',
        category: 'referral',
        priority: 'medium',
        title: 'Podiatry Referral for Neuropathy',
        description: 'Regular foot exams essential with peripheral neuropathy.',
        evidence: 'Podiatry reduces amputation risk in diabetic neuropathy'
      },
      {
        id: 'REC-003-5',
        category: 'lifestyle',
        priority: 'high',
        title: 'Structured Exercise Program',
        description: 'Supervised exercise program targeting 150 minutes per week.',
        evidence: 'Exercise improves glycemic control and reduces cardiovascular risk'
      }
    ],
    timestamp: getTimestamp(0)
  },

  'PAT-004': {
    // Case 4: Elderly Patient with CHF and Multiple Comorbidities
    patientInfo: {
      id: 'PAT-004',
      name: 'Robert Thompson',
      age: 78,
      gender: 'Male',
      height: "5'8\"",
      weight: '168 lbs',
      bmi: 25.5,
      lastVisit: getTimestamp(6),
      provider: 'Dr. Martinez',
      status: 'critical',
      riskLevel: 'high',
      ecbomeScore: 0.45,
      chiefComplaint: 'Increasing fatigue and shortness of breath with minimal exertion, bilateral ankle swelling',
      vitalSigns: {
        heartRate: 92,
        bloodPressure: '118/68',
        temperature: 97.8,
        oxygenSaturation: 93,
        respiratoryRate: 22,
        bpCategory: 'Normal'
      },
      medications: [
        { name: 'Furosemide (Lasix)', dosage: '40mg', frequency: 'Twice daily', indication: 'CHF/Diuretic' },
        { name: 'Carvedilol', dosage: '12.5mg', frequency: 'Twice daily', indication: 'CHF/Beta-blocker' },
        { name: 'Lisinopril', dosage: '10mg', frequency: 'Once daily', indication: 'CHF/ACE inhibitor' },
        { name: 'Warfarin', dosage: '5mg', frequency: 'Once daily', indication: 'AFib anticoagulation' },
        { name: 'Atorvastatin', dosage: '40mg', frequency: 'Once daily', indication: 'Cholesterol' },
        { name: 'Potassium Chloride', dosage: '20mEq', frequency: 'Once daily', indication: 'Supplement' },
        { name: 'Aspirin', dosage: '81mg', frequency: 'Once daily', indication: 'Cardioprotective' },
        { name: 'Acetaminophen', dosage: '500mg', frequency: 'As needed', indication: 'Arthritis pain' }
      ],
      allergies: ['Penicillin (rash)'],
      conditions: [
        'Congestive Heart Failure (EF 35%)',
        'Atrial Fibrillation',
        'Chronic Kidney Disease Stage 3',
        'Hypertension',
        'Hyperlipidemia',
        'Osteoarthritis',
        'History of myocardial infarction (5 years ago)'
      ],
      socialHistory: {
        occupation: 'Retired postal worker',
        livingSituation: 'Lives with spouse, adult children nearby',
        tobacco: 'Former smoker, quit 10 years ago (40 pack-year history)',
        alcohol: 'None',
        exercise: 'Limited - short walks, uses cane',
        diet: 'Low sodium diet (2g/day), struggles with compliance',
        functionalStatus: 'Needs assistance with some ADLs'
      },
      labResults: {
        lastUpdated: getTimestamp(24), // 1 day ago
        testDate: new Date(Date.now() - 24 * 60 * 60 * 1000).toLocaleDateString(),
        results: {
          // Cardiac Markers - CHF Monitoring
          'BNP': { value: 850, unit: 'pg/mL', status: 'elevated', reference: '<100 (normal), <400 (stable CHF)' },
          'Troponin I': { value: 0.08, unit: 'ng/mL', status: 'borderline', reference: '<0.04' },
          'NT-proBNP': { value: 2100, unit: 'pg/mL', status: 'elevated', reference: '<125' },
          
          // Kidney Function - CKD Stage 3
          'Creatinine': { value: 1.8, unit: 'mg/dL', status: 'elevated', reference: '0.7-1.3' },
          'eGFR': { value: 42, unit: 'mL/min', status: 'stage 3 CKD', reference: '>90' },
          'BUN': { value: 32, unit: 'mg/dL', status: 'elevated', reference: '7-20' },
          'BUN/Creatinine Ratio': { value: 17.8, unit: 'ratio', status: 'normal', reference: '10-20' },
          'Cystatin C': { value: 1.8, unit: 'mg/L', status: 'elevated', reference: '0.5-1.0' },
          
          // Anticoagulation - Warfarin Monitoring
          'INR': { value: 2.3, unit: 'ratio', status: 'therapeutic', reference: '2.0-3.0 (AFib)' },
          'PT': { value: 23, unit: 'seconds', status: 'prolonged', reference: '11-13.5' },
          
          // Electrolytes - Diuretic Monitoring
          'Sodium': { value: 138, unit: 'mEq/L', status: 'low-normal', reference: '136-145' },
          'Potassium': { value: 4.2, unit: 'mEq/L', status: 'normal', reference: '3.5-5.0' },
          'Chloride': { value: 102, unit: 'mEq/L', status: 'normal', reference: '98-107' },
          'Magnesium': { value: 1.9, unit: 'mg/dL', status: 'normal', reference: '1.7-2.2' },
          
          // Lipid Panel - On Statin
          'Total Cholesterol': { value: 175, unit: 'mg/dL', status: 'good', reference: '<200' },
          'LDL Cholesterol': { value: 92, unit: 'mg/dL', status: 'good', reference: '<100' },
          'HDL Cholesterol': { value: 48, unit: 'mg/dL', status: 'borderline', reference: '>40' },
          'Triglycerides': { value: 175, unit: 'mg/dL', status: 'borderline', reference: '<150' },
          
          // Metabolic
          'Fasting Glucose': { value: 94, unit: 'mg/dL', status: 'normal', reference: '70-99' },
          'HbA1c': { value: 5.6, unit: '%', status: 'normal', reference: '<5.7' },
          
          // Liver Function
          'ALT': { value: 28, unit: 'U/L', status: 'normal', reference: '7-56' },
          'AST': { value: 32, unit: 'U/L', status: 'normal', reference: '10-40' },
          'Albumin': { value: 3.8, unit: 'g/dL', status: 'normal', reference: '3.5-5.5' },
          
          // Complete Blood Count
          'WBC': { value: 7.2, unit: '10³/μL', status: 'normal', reference: '4.5-11.0' },
          'Hemoglobin': { value: 12.8, unit: 'g/dL', status: 'low-normal', reference: '13.5-17.5' },
          'Hematocrit': { value: 38, unit: '%', status: 'low', reference: '41-50' },
          'Platelets': { value: 185, unit: '10³/μL', status: 'normal', reference: '150-400' }
        }
      },
      medicalHistory: {
        pastMedicalHistory: [
          { condition: 'Congestive Heart Failure', diagnosedDate: '2018-05-12', diagnosedBy: 'Dr. Cardiologist', status: 'Active', severity: 'Stage C, NYHA Class III, EF 35%', notes: 'Ischemic cardiomyopathy, requires multiple medications' },
          { condition: 'Atrial Fibrillation', diagnosedDate: '2019-03-08', diagnosedBy: 'Dr. Cardiologist', status: 'Active', severity: 'Permanent AF', notes: 'On warfarin anticoagulation, INR goal 2-3' },
          { condition: 'Chronic Kidney Disease Stage 3', diagnosedDate: '2020-01-15', diagnosedBy: 'Dr. Nephrologist', status: 'Active', severity: 'eGFR 42 mL/min', notes: 'Secondary to hypertension and age, stable' },
          { condition: 'Myocardial Infarction (History of)', diagnosedDate: '2019-10-20', diagnosedBy: 'Dr. ER Physician', status: 'Resolved', severity: 'Anterior STEMI', notes: '5 years ago, led to reduced EF and CHF' },
          { condition: 'Osteoarthritis', diagnosedDate: '2015-06-10', diagnosedBy: 'Dr. Orthopedist', status: 'Active', severity: 'Moderate - bilateral knees', notes: 'Limits mobility, uses cane' }
        ],
        surgicalHistory: [
          { procedure: 'Coronary Angioplasty with Stent Placement', date: '2019-10-21', facility: 'Cardiac Center', surgeon: 'Dr. Interventional Cardiologist', outcome: 'Successful - 2 stents LAD', complications: 'None', notes: 'Emergency procedure post-STEMI. Drug-eluting stents placed in LAD. Post-procedure EF 35%.' },
          { procedure: 'Pacemaker/ICD Implantation', date: '2020-08-15', facility: 'Cardiac Center', surgeon: 'Dr. Electrophysiologist', outcome: 'Successful', complications: 'None', notes: 'Dual-chamber ICD for primary prevention. EF <35%, history of sustained VT.' },
          { procedure: 'Cataract Surgery (Right Eye)', date: '2022-03-10', facility: 'Eye Surgery Center', surgeon: 'Dr. Ophthalmologist', outcome: 'Successful', notes: 'Uncomplicated phacoemulsification with IOL implantation' },
          { procedure: 'Cataract Surgery (Left Eye)', date: '2022-04-20', facility: 'Eye Surgery Center', surgeon: 'Dr. Ophthalmologist', outcome: 'Successful', notes: 'Uncomplicated, vision much improved' }
        ],
        allergiesDetailed: [
          { allergen: 'Penicillin', type: 'Medication', reaction: 'Rash, hives', severity: 'Moderate', dateReported: '1965-05-10', verifiedBy: 'Multiple providers', notes: 'Childhood allergy, avoid all penicillin derivatives' }
        ],
        familyHistory: {
          father: { conditions: 'MI at age 62, died at age 68 from heart failure', alive: false },
          mother: { conditions: 'Stroke at age 75, died at age 82', alive: false },
          siblings: { summary: 'Two brothers - both with CAD, one deceased from MI at age 72' },
          children: { summary: 'Three adult children - ages 48, 45, 42; one son has hypertension' },
          notes: 'Strong family history of cardiovascular disease. Both parents and sibling deceased from cardiac/cerebrovascular events.'
        },
        previousReports: [
          {
            id: 'RPT-PAT004-001',
            type: 'Echocardiogram - Heart Failure Monitoring',
            date: '2024-09-10',
            provider: 'Dr. Cardiac Imaging, MD - Cardiology',
            facility: 'Heart Center',
            summary: 'Serial echocardiogram shows stable but severely reduced LV systolic function. EF remains at 35%. Moderate mitral regurgitation. No change from prior study.',
            findings: [
              'LV ejection fraction: 35% (severely reduced)',
              'LV dilated with global hypokinesis',
              'Moderate mitral regurgitation (MR grade II)',
              'Moderate tricuspid regurgitation',
              'Elevated right ventricular systolic pressure (45 mmHg)',
              'Left atrium severely dilated',
              'ICD/pacemaker leads in good position'
            ],
            impression: 'Stable ischemic cardiomyopathy with severely reduced EF. MR and TR secondary to ventricular dilation.',
            downloadable: true,
            fileSize: '1.1 MB'
          },
          {
            id: 'RPT-PAT004-002',
            type: 'Cardiology Consultation Note',
            date: '2024-10-25',
            provider: 'Dr. Heart Specialist, MD - Cardiology',
            facility: 'ABENA Cardiology Clinic',
            summary: 'Patient with advanced heart failure, EF 35%, on optimal medical therapy. Recent worsening of dyspnea and fatigue. BNP elevated at 850. Discussed advanced therapies.',
            findings: [
              'NYHA Class III symptoms (SOB with minimal exertion)',
              'Bilateral ankle edema 2+',
              'JVD elevated to angle of jaw',
              'Lung sounds: Bibasilar crackles',
              'Heart: Irregularly irregular (AF), S3 gallop',
              'BNP 850 pg/mL (significantly elevated)'
            ],
            impression: 'Decompensated heart failure requiring optimization. Consider diuretic increase, close monitoring.',
            recommendations: 'Increase Furosemide to 60mg BID, daily weights, low sodium diet <2g/day, consider LVAD evaluation if no improvement',
            downloadable: true,
            fileSize: '386 KB'
          }
        ],
        immunizations: [
          { vaccine: 'Influenza (High-Dose)', date: '2024-09-20', lot: 'FL2024-HD-123', manufacturer: 'Sanofi', site: 'Left deltoid', provider: 'Dr. Martinez' },
          { vaccine: 'Pneumococcal (PPSV23)', date: '2020-03-15', lot: 'PN2020-456789', manufacturer: 'Merck', site: 'Right deltoid', provider: 'Dr. Martinez' },
          { vaccine: 'Pneumococcal (PCV13)', date: '2019-03-10', lot: 'PC2019-789123', manufacturer: 'Pfizer', site: 'Left deltoid', provider: 'Dr. Martinez' },
          { vaccine: 'Shingles (Shingrix - Series Complete)', date: '2022-07-20', lot: 'SH2022-123789', manufacturer: 'GSK', site: 'Right deltoid', provider: 'Pharmacist' }
        ],
        hospitalizations: [
          {
            admissionDate: '2019-10-20',
            dischargeDate: '2019-10-25',
            facility: 'Regional Medical Center - CCU',
            reason: 'Anterior STEMI - Acute myocardial infarction',
            diagnosis: 'ST-elevation myocardial infarction, cardiogenic shock',
            procedures: ['Emergency cardiac catheterization', 'PCI with 2 stents to LAD', 'IABP placement'],
            outcome: 'Survived, reduced EF 35%, developed CHF',
            lengthOfStay: '5 days'
          },
          {
            admissionDate: '2023-12-08',
            dischargeDate: '2023-12-12',
            facility: 'Regional Medical Center',
            reason: 'Acute decompensated heart failure',
            diagnosis: 'CHF exacerbation, volume overload',
            procedures: ['IV diuresis', 'Medication optimization'],
            outcome: 'Improved with diuresis, discharged on increased Furosemide',
            lengthOfStay: '4 days'
          }
        ]
      }
    },
    ecbomeProfile: {
      score: 0.45,
      status: 'Critical',
      components: {
        endocannabinoid: { status: 'very-low', reading: 0.38, trend: 'declining' },
        metabolome: { status: 'disrupted', reading: 0.42, trend: 'declining' },
        inflammatome: { status: 'elevated', reading: 0.35, trend: 'worsening' },
        immunome: { status: 'compromised', reading: 0.48, trend: 'declining' },
        chronobiome: { status: 'disrupted', reading: 0.40, trend: 'stable' },
        cardiovascular: { status: 'critical', reading: 0.32, trend: 'declining' },
        stress: { status: 'elevated', reading: 0.45, trend: 'stable' },
        microbiome: { status: 'imbalanced', reading: 0.50, trend: 'stable' },
        nutriome: { status: 'poor', reading: 0.48, trend: 'stable' },
        toxicome: { status: 'moderate', reading: 0.55, trend: 'improving' },
        pharmacome: { status: 'complex', reading: 0.52, trend: 'stable' },
        hormonal: { status: 'low', reading: 0.45, trend: 'stable' }
      }
    },
    alerts: [
      {
        id: 'ALT-004-1',
        type: 'critical',
        severity: 'high',
        title: 'Heart Failure Exacerbation',
        message: 'Elevated BNP (850), increased dyspnea, bilateral edema suggest CHF decompensation',
        timestamp: getTimestamp(1),
        recommendations: ['Consider hospitalization', 'Diuretic adjustment', 'Fluid restriction', 'Daily weights']
      },
      {
        id: 'ALT-004-2',
        type: 'critical',
        severity: 'high',
        title: 'Low Oxygen Saturation',
        message: 'O2 sat 93% on room air, tachypnea (RR 22) indicate respiratory compromise',
        timestamp: getTimestamp(1),
        recommendations: ['Supplemental oxygen', 'Chest X-ray', 'Consider hospitalization']
      },
      {
        id: 'ALT-004-3',
        type: 'warning',
        severity: 'medium',
        title: 'Chronic Kidney Disease Stage 3',
        message: 'eGFR 42, Creatinine 1.8 - monitor renal function closely with diuretic use',
        timestamp: getTimestamp(24),
        recommendations: ['Monitor electrolytes', 'Adjust medications for renal function']
      },
      {
        id: 'ALT-004-4',
        type: 'info',
        severity: 'low',
        title: 'INR in Therapeutic Range',
        message: 'INR 2.3 is therapeutic for AFib (target 2.0-3.0)',
        timestamp: getTimestamp(24),
        recommendations: ['Continue current warfarin dose', 'Routine INR monitoring']
      }
    ],
    recommendations: [
      {
        id: 'REC-004-1',
        category: 'acute-care',
        priority: 'critical',
        title: 'Consider Hospital Admission',
        description: 'CHF exacerbation with hypoxia may require inpatient management.',
        evidence: 'Decompensated heart failure often requires IV diuresis'
      },
      {
        id: 'REC-004-2',
        category: 'medication',
        priority: 'high',
        title: 'Increase Furosemide Dose',
        description: 'Consider increasing Lasix to 60mg BID or adding metolazone for diuresis.',
        evidence: 'Loop diuretics are first-line for CHF volume overload'
      },
      {
        id: 'REC-004-3',
        category: 'monitoring',
        priority: 'high',
        title: 'Daily Weight and Fluid Monitoring',
        description: 'Patient/caregiver should monitor daily weights and report gain >2lbs in 24h or >5lbs in week.',
        evidence: 'Daily weights help detect early CHF exacerbation'
      },
      {
        id: 'REC-004-4',
        category: 'referral',
        priority: 'medium',
        title: 'Home Health Services',
        description: 'Home health for medication management, daily weights, dietary counseling.',
        evidence: 'Home health reduces CHF readmissions'
      },
      {
        id: 'REC-004-5',
        category: 'lifestyle',
        priority: 'high',
        title: 'Strict Sodium and Fluid Restriction',
        description: 'Reinforce 2g sodium diet and fluid restriction to 1.5-2L per day.',
        evidence: 'Sodium/fluid restriction essential in CHF management'
      }
    ],
    timestamp: getTimestamp(0)
  },

  'PAT-005': {
    // Case 5: Young Adult with Anxiety and Metabolic Syndrome
    patientInfo: {
      id: 'PAT-005',
      name: 'Emily Rodriguez',
      age: 28,
      gender: 'Female',
      height: "5'3\"",
      weight: '172 lbs',
      bmi: 30.5,
      lastVisit: getTimestamp(72),
      provider: 'Dr. Martinez',
      status: 'active',
      riskLevel: 'medium',
      ecbomeScore: 0.71,
      chiefComplaint: 'Persistent anxiety, difficulty sleeping, weight gain, concerns about family history of diabetes',
      vitalSigns: {
        heartRate: 84,
        bloodPressure: '128/82',
        temperature: 98.5,
        oxygenSaturation: 98,
        respiratoryRate: 16,
        bpCategory: 'Elevated/Stage 1'
      },
      medications: [
        { name: 'Sertraline (Zoloft)', dosage: '100mg', frequency: 'Once daily', indication: 'Generalized Anxiety Disorder' },
        { name: 'Oral Contraceptive', dosage: 'Standard', frequency: 'Daily', indication: 'PCOS/Cycle regulation' },
        { name: 'Vitamin D', dosage: '2000 IU', frequency: 'Once daily', indication: 'Deficiency' },
        { name: 'Multivitamin', dosage: 'Standard', frequency: 'Once daily', indication: 'General health' }
      ],
      allergies: ['Sulfa drugs (hives)'],
      conditions: [
        'Generalized Anxiety Disorder (GAD)',
        'Prediabetes',
        'Polycystic Ovary Syndrome (PCOS)',
        'Irregular menstrual cycles',
        'Obesity (Class I)',
        'Family history of Type 2 Diabetes',
        'Family history of cardiovascular disease'
      ],
      socialHistory: {
        occupation: 'Software developer, works from home',
        tobacco: 'Non-smoker',
        alcohol: '1-2 glasses of wine, 2-3 times per week',
        exercise: 'Sedentary, sits 10+ hours/day, no regular exercise',
        diet: 'Irregular eating, frequent fast food/takeout, high carbs, stress eating',
        sleep: '5-6 hours per night, difficulty falling asleep, poor quality',
        stress: 'High work stress, deadlines, poor work-life balance'
      },
      labResults: {
        lastUpdated: getTimestamp(168), // 1 week ago
        testDate: new Date(Date.now() - 168 * 60 * 60 * 1000).toLocaleDateString(),
        results: {
          // Metabolic Syndrome Panel
          'Fasting Glucose': { value: 108, unit: 'mg/dL', status: 'prediabetic', reference: '70-99' },
          'HbA1c': { value: 5.9, unit: '%', status: 'prediabetic', reference: '<5.7' },
          'Insulin (Fasting)': { value: 22, unit: 'μU/mL', status: 'insulin resistance', reference: '2.6-24.9' },
          'HOMA-IR': { value: 5.9, unit: 'index', status: 'insulin resistant', reference: '<2.0' },
          
          // Lipid Panel - Metabolic Syndrome Pattern
          'Total Cholesterol': { value: 215, unit: 'mg/dL', status: 'borderline high', reference: '<200' },
          'LDL Cholesterol': { value: 138, unit: 'mg/dL', status: 'high', reference: '<100' },
          'HDL Cholesterol': { value: 42, unit: 'mg/dL', status: 'low', reference: '>50 (female)' },
          'Triglycerides': { value: 175, unit: 'mg/dL', status: 'borderline high', reference: '<150' },
          'Triglyceride/HDL Ratio': { value: 4.2, unit: 'ratio', status: 'insulin resistance', reference: '<2.0' },
          
          // PCOS Hormonal Panel
          'Testosterone (Total)': { value: 68, unit: 'ng/dL', status: 'elevated', reference: '8-60 (female)' },
          'Free Testosterone': { value: 2.8, unit: 'pg/mL', status: 'elevated', reference: '0.0-2.2' },
          'DHEA-S': { value: 420, unit: 'μg/dL', status: 'elevated', reference: '65-380' },
          'LH': { value: 18, unit: 'mIU/mL', status: 'elevated', reference: '1.9-12.5' },
          'FSH': { value: 4.2, unit: 'mIU/mL', status: 'low-normal', reference: '3.5-12.5' },
          'LH/FSH Ratio': { value: 4.3, unit: 'ratio', status: 'PCOS pattern', reference: '<2.0' },
          'Prolactin': { value: 18, unit: 'ng/mL', status: 'normal', reference: '4-23' },
          
          // Thyroid Function
          'TSH': { value: 2.4, unit: 'mIU/L', status: 'normal', reference: '0.4-4.0' },
          'Free T4': { value: 1.0, unit: 'ng/dL', status: 'normal', reference: '0.8-1.8' },
          'Free T3': { value: 2.9, unit: 'pg/mL', status: 'normal', reference: '2.0-4.4' },
          
          // Inflammatory Markers
          'hs-CRP': { value: 3.8, unit: 'mg/L', status: 'high', reference: '<3.0' },
          'ESR': { value: 22, unit: 'mm/hr', status: 'elevated', reference: '<20' },
          
          // Vitamins - Mental Health Related
          'Vitamin D': { value: 18, unit: 'ng/mL', status: 'deficient', reference: '30-100' },
          'Vitamin B12': { value: 312, unit: 'pg/mL', status: 'low-normal', reference: '200-900' },
          'Folate': { value: 8.5, unit: 'ng/mL', status: 'normal', reference: '>5.4' },
          
          // Liver Function - NAFLD Screening
          'ALT': { value: 52, unit: 'U/L', status: 'elevated', reference: '7-56' },
          'AST': { value: 45, unit: 'U/L', status: 'elevated', reference: '10-40' },
          'GGT': { value: 58, unit: 'U/L', status: 'elevated', reference: '9-48' },
          
          // Complete Blood Count
          'WBC': { value: 7.5, unit: '10³/μL', status: 'normal', reference: '4.5-11.0' },
          'Hemoglobin': { value: 13.2, unit: 'g/dL', status: 'normal', reference: '12.0-16.0' },
          'Platelets': { value: 242, unit: '10³/μL', status: 'normal', reference: '150-400' },
          
          // Cortisol - Stress Assessment
          'Cortisol (AM)': { value: 22, unit: 'μg/dL', status: 'elevated', reference: '6-23' },
          'Cortisol (PM)': { value: 12, unit: 'μg/dL', status: 'high', reference: '2-14' }
        }
      },
      medicalHistory: {
        pastMedicalHistory: [
          { condition: 'Generalized Anxiety Disorder', diagnosedDate: '2021-03-15', diagnosedBy: 'Dr. Psychiatrist', status: 'Active', severity: 'Moderate (GAD-7: 14)', notes: 'On SSRI therapy, also seeing therapist' },
          { condition: 'Polycystic Ovary Syndrome (PCOS)', diagnosedDate: '2019-06-20', diagnosedBy: 'Dr. OB/GYN', status: 'Active', severity: 'Moderate', notes: 'Irregular cycles, elevated androgens, insulin resistance' },
          { condition: 'Prediabetes', diagnosedDate: '2023-08-10', diagnosedBy: 'Dr. Martinez', status: 'Active', severity: 'HbA1c 5.9%, HOMA-IR 5.9', notes: 'High risk for progression to diabetes' },
          { condition: 'Obesity Class I', diagnosedDate: '2020-02-15', diagnosedBy: 'Dr. Martinez', status: 'Active', severity: 'BMI 30.5', notes: 'Weight gained 30 lbs over 3 years, sedentary lifestyle' },
          { condition: 'Vitamin D Deficiency', diagnosedDate: '2022-01-10', diagnosedBy: 'Dr. Martinez', status: 'Active', severity: 'Deficient (18 ng/mL)', notes: 'May contribute to mood symptoms and fatigue' }
        ],
        surgicalHistory: [
          { procedure: 'Ovarian Ultrasound', date: '2019-07-05', facility: 'Women\'s Health Imaging', provider: 'Dr. Radiologist', outcome: 'PCOS confirmed', notes: 'Multiple small follicles (>12 per ovary), polycystic appearance, ovarian volume increased' },
          { procedure: 'Psychiatric Evaluation', date: '2021-03-10', facility: 'Mental Health Center', provider: 'Dr. Psychiatrist', outcome: 'GAD diagnosed', notes: 'Recommended SSRI therapy and cognitive behavioral therapy' }
        ],
        allergiesDetailed: [
          { allergen: 'Sulfa Drugs (Sulfamethoxazole)', type: 'Medication', reaction: 'Hives, urticaria', severity: 'Moderate', dateReported: '2018-08-15', verifiedBy: 'Dr. Urgent Care', notes: 'Occurred with Bactrim for UTI. Avoid all sulfonamide antibiotics.' }
        ],
        familyHistory: {
          father: { conditions: 'Type 2 Diabetes (age 58), Hypertension, CAD', alive: true, age: 60 },
          mother: { conditions: 'PCOS, Obesity, Hypothyroidism', alive: true, age: 56 },
          siblings: { summary: 'One sister - age 25, also has PCOS and anxiety' },
          children: { summary: 'No children' },
          notes: 'Strong family history of metabolic syndrome, PCOS, and mental health conditions. Mother and sister both affected by PCOS.'
        },
        previousReports: [
          {
            id: 'RPT-PAT005-001',
            type: 'PCOS Diagnostic Workup',
            date: '2019-07-10',
            provider: 'Dr. Reproductive Health, MD - OB/GYN',
            facility: 'Women\'s Health Center',
            summary: 'Comprehensive PCOS evaluation. Rotterdam criteria met: irregular cycles, hyperandrogenism (elevated testosterone), polycystic ovaries on ultrasound. Insulin resistance present.',
            findings: [
              'Menstrual history: Irregular cycles, 6-8 per year',
              'Hirsutism score: 12 (mild)',
              'Testosterone elevated: 68 ng/dL',
              'LH/FSH ratio: 4.3 (elevated)',
              'Pelvic ultrasound: Polycystic ovaries bilateral',
              'HOMA-IR: 5.9 (insulin resistant)',
              'BMI: 27.5 at time of diagnosis'
            ],
            impression: 'Polycystic ovary syndrome with metabolic features. High risk for Type 2 Diabetes.',
            recommendations: 'Lifestyle modification, consider metformin, OCPs for cycle regulation, monitor glucose annually',
            downloadable: true,
            fileSize: '512 KB'
          },
          {
            id: 'RPT-PAT005-002',
            type: 'Mental Health Assessment',
            date: '2024-02-20',
            provider: 'Dr. Mind Health, PsyD - Psychology',
            facility: 'Behavioral Health Center',
            summary: 'Comprehensive psychological evaluation. Moderate generalized anxiety (GAD-7: 14), mild depression (PHQ-9: 8). Anxiety primarily related to work stress and health concerns. Responds well to SSRI therapy.',
            findings: [
              'GAD-7 score: 14 (moderate anxiety)',
              'PHQ-9 score: 8 (mild depression)',
              'Sleep quality poor (5-6 hours, difficulty falling asleep)',
              'High work stress (software developer, long hours)',
              'Social anxiety in work settings',
              'No suicidal ideation',
              'Good response to Sertraline 100mg'
            ],
            impression: 'Generalized anxiety disorder with comorbid mild depression and insomnia. Work-related stress significant factor.',
            recommendations: 'Continue Sertraline, weekly CBT sessions, stress management techniques, consider sleep hygiene counseling',
            downloadable: true,
            fileSize: '298 KB'
          }
        ],
        immunizations: [
          { vaccine: 'Influenza', date: '2024-10-10', lot: 'FL2024-987654', manufacturer: 'Moderna', site: 'Left deltoid', provider: 'Pharmacist' },
          { vaccine: 'COVID-19 Booster', date: '2024-06-01', lot: 'CV2024-123987', manufacturer: 'Pfizer', site: 'Right deltoid', provider: 'Pharmacist' },
          { vaccine: 'HPV (Gardasil 9 - Series Complete)', date: '2015-09-20', lot: 'HPV2015-456123', manufacturer: 'Merck', site: 'Left deltoid', provider: 'School Nurse' },
          { vaccine: 'Tdap', date: '2020-05-15', lot: 'TD2020-654987', manufacturer: 'GSK', site: 'Right deltoid', provider: 'Dr. Martinez' }
        ],
        hospitalizations: []
      },
      screeningScores: {
        GAD7: 14, // Moderate anxiety
        PHQ9: 8 // Mild depression
      }
    },
    ecbomeProfile: {
      score: 0.71,
      status: 'Fair',
      components: {
        endocannabinoid: { status: 'low', reading: 0.65, trend: 'declining' },
        metabolome: { status: 'disrupted', reading: 0.62, trend: 'declining' },
        inflammatome: { status: 'elevated', reading: 0.60, trend: 'worsening' },
        immunome: { status: 'good', reading: 0.78, trend: 'stable' },
        chronobiome: { status: 'disrupted', reading: 0.58, trend: 'declining' },
        cardiovascular: { status: 'moderate', reading: 0.72, trend: 'declining' },
        stress: { status: 'elevated', reading: 0.52, trend: 'worsening' },
        microbiome: { status: 'imbalanced', reading: 0.68, trend: 'stable' },
        nutriome: { status: 'poor', reading: 0.60, trend: 'stable' },
        toxicome: { status: 'good', reading: 0.85, trend: 'stable' },
        pharmacome: { status: 'active', reading: 0.75, trend: 'stable' },
        hormonal: { status: 'imbalanced', reading: 0.64, trend: 'stable' }
      }
    },
    alerts: [
      {
        id: 'ALT-005-1',
        type: 'warning',
        severity: 'medium',
        title: 'Prediabetes with Strong Family History',
        message: 'HbA1C 5.9%, fasting glucose 108 - prediabetic with high risk of progression',
        timestamp: getTimestamp(168),
        recommendations: ['Diabetes prevention program', 'Lifestyle modification', 'Metformin consideration']
      },
      {
        id: 'ALT-005-2',
        type: 'warning',
        severity: 'medium',
        title: 'Metabolic Syndrome Risk',
        message: 'Elevated BP, triglycerides, low HDL, central obesity, and prediabetes indicate metabolic syndrome',
        timestamp: getTimestamp(168),
        recommendations: ['Comprehensive lifestyle intervention', 'Cardiovascular risk assessment']
      },
      {
        id: 'ALT-005-3',
        type: 'info',
        severity: 'low',
        title: 'Sleep Deprivation Impact',
        message: 'Chronic sleep restriction (5-6 hours) worsens anxiety, metabolic health, and weight',
        timestamp: getTimestamp(72),
        recommendations: ['Sleep hygiene counseling', 'CBT for insomnia', 'Target 7-9 hours']
      },
      {
        id: 'ALT-005-4',
        type: 'info',
        severity: 'low',
        title: 'Vitamin D Deficiency',
        message: 'Vitamin D level 18 ng/mL (normal >30) - supplement dose may need adjustment',
        timestamp: getTimestamp(168),
        recommendations: ['Increase vitamin D to 4000 IU daily', 'Recheck in 3 months']
      }
    ],
    recommendations: [
      {
        id: 'REC-005-1',
        category: 'referral',
        priority: 'high',
        title: 'Diabetes Prevention Program (DPP)',
        description: 'Refer to structured DPP for lifestyle modification and weight loss.',
        evidence: 'DPP reduces diabetes incidence by 58% in prediabetes'
      },
      {
        id: 'REC-005-2',
        category: 'medication',
        priority: 'medium',
        title: 'Consider Metformin for Prediabetes',
        description: 'Metformin 500mg BID reduces diabetes risk, helps with PCOS and weight.',
        evidence: 'Metformin reduces diabetes by 31% and beneficial for PCOS'
      },
      {
        id: 'REC-005-3',
        category: 'therapy',
        priority: 'high',
        title: 'Cognitive Behavioral Therapy',
        description: 'CBT for anxiety and insomnia. Current sertraline helping but breakthrough symptoms.',
        evidence: 'CBT is first-line for GAD and insomnia'
      },
      {
        id: 'REC-005-4',
        category: 'lifestyle',
        priority: 'high',
        title: 'Structured Exercise Program',
        description: 'Target 150 minutes moderate exercise weekly. Critical given sedentary job.',
        evidence: 'Exercise improves anxiety, sleep, weight, and metabolic health'
      },
      {
        id: 'REC-005-5',
        category: 'referral',
        priority: 'medium',
        title: 'Nutrition Counseling',
        description: 'Registered dietitian for meal planning, stress eating, and PCOS dietary management.',
        evidence: 'Nutrition counseling improves outcomes in metabolic syndrome'
      },
      {
        id: 'REC-005-6',
        category: 'lifestyle',
        priority: 'medium',
        title: 'Sleep Hygiene and Stress Management',
        description: 'Sleep hygiene education, mindfulness, and work-life balance strategies.',
        evidence: 'Sleep and stress management improve anxiety and metabolic health'
      }
    ],
    timestamp: getTimestamp(0)
  }
};

// Demo alias so both portals can standardize on a single investor-demo patient id.
// This intentionally reuses the rich PAT-001 profile so all dashboard modules remain populated.
mockPatientDetails['JANE_001'] = {
  ...mockPatientDetails['PAT-001'],
  patientInfo: {
    ...mockPatientDetails['PAT-001'].patientInfo,
    id: 'JANE_001',
    name: 'Jane (Investor Demo)',
    mrn: 'MRN-DEMO-0001'
  }
};

/**
 * Generate real-time vital signs for a patient
 */
export const generateRealtimeVitals = (patientId) => {
  const baseVitals = {
    'JANE_001': { hr: 88, sys: 188, dia: 90, temp: 98.2, o2: 93 },
    'PAT-001': { hr: 88, sys: 188, dia: 90, temp: 98.2, o2: 93 },
    'PAT-002': { hr: 74, sys: 110, dia: 74, temp: 98.4, o2: 99 },
    'PAT-003': { hr: 80, sys: 130, dia: 88, temp: 98.6, o2: 97 },
    'PAT-004': { hr: 92, sys: 118, dia: 68, temp: 97.8, o2: 93 },
    'PAT-005': { hr: 84, sys: 128, dia: 82, temp: 98.5, o2: 98 }
  };

  const base = baseVitals[patientId] || baseVitals['PAT-001'];
  return generateVitals(base.hr, base.sys, base.dia, base.temp, base.o2);
};

/**
 * Generate eCBome timeline data for 24 hours with circadian rhythm patterns
 */
export const generateEcbomeTimeline = (patientId, hours = 24) => {
  const timeline = [];
  const patientData = mockPatientDetails[patientId];
  
  if (!patientData) return [];

  const components = patientData.ecbomeProfile.components;
  
  // Helper function to apply circadian rhythm (peaks in afternoon, dips at night)
  const getCircadianMultiplier = (hourOfDay) => {
    // Morning rise (6am-12pm): gradual increase
    if (hourOfDay >= 6 && hourOfDay < 12) {
      return 0.95 + (hourOfDay - 6) * 0.02; // 0.95 to 1.07
    }
    // Afternoon peak (12pm-6pm): highest activity
    if (hourOfDay >= 12 && hourOfDay < 18) {
      return 1.05 + Math.sin((hourOfDay - 12) * Math.PI / 6) * 0.05; // 1.05 to 1.10
    }
    // Evening decline (6pm-10pm): gradual decrease
    if (hourOfDay >= 18 && hourOfDay < 22) {
      return 1.05 - (hourOfDay - 18) * 0.05; // 1.05 to 0.85
    }
    // Night/sleep (10pm-6am): lowest activity
    return 0.80 + Math.random() * 0.1; // 0.80 to 0.90
  };

  // Helper to add meal spikes (breakfast 7am, lunch 12pm, dinner 6pm)
  const getMealSpike = (hourOfDay) => {
    if (hourOfDay === 7 || hourOfDay === 12 || hourOfDay === 18) {
      return 0.10; // 10% boost after meals (especially for 2-AG)
    }
    if (hourOfDay === 8 || hourOfDay === 13 || hourOfDay === 19) {
      return 0.05; // Lingering effect
    }
    return 0;
  };
  
  for (let i = hours; i >= 0; i--) {
    const currentHour = new Date().getHours() - i;
    const hourOfDay = ((currentHour % 24) + 24) % 24; // Ensure 0-23 range
    const timestamp = getTimestamp(i);
    
    const circadianMultiplier = getCircadianMultiplier(hourOfDay);
    const mealBoost = getMealSpike(hourOfDay);
    
    const timePoint = {
      time: `${hourOfDay.toString().padStart(2, '0')}:00`,
      timestamp,
      hour: hours - i
    };

    // ANANDAMIDE - "Bliss molecule", mood regulator
    const anandamideBase = components.endocannabinoid?.reading || 0.70;
    timePoint.anandamide = Math.max(0.3, Math.min(1.0, 
      anandamideBase * circadianMultiplier + (Math.random() * 0.06 - 0.03)
    ));

    // 2-AG - Inflammation/immune, spikes with meals (lipid-based)
    const twoAGBase = components.metabolome?.reading || 0.75;
    timePoint.twoAG = Math.max(0.3, Math.min(1.0,
      twoAGBase * circadianMultiplier + mealBoost + (Math.random() * 0.08 - 0.04)
    ));

    // CB1 RECEPTOR - Brain/CNS, follows cognitive activity
    const cb1Base = components.endocannabinoid?.reading || 0.72;
    const cognitiveBoost = (hourOfDay >= 9 && hourOfDay <= 17) ? 0.05 : 0; // Work hours
    timePoint.cb1 = Math.max(0.3, Math.min(1.0,
      cb1Base * circadianMultiplier + cognitiveBoost + (Math.random() * 0.05 - 0.025)
    ));

    // CB2 RECEPTOR - Immune/inflammation, higher during sleep (repair)
    const cb2Base = components.immunome?.reading || 0.68;
    const sleepRepairBoost = (hourOfDay >= 22 || hourOfDay <= 6) ? 0.08 : 0; // Night repair
    const inflammationFactor = components.inflammatome?.reading < 0.5 ? 0.10 : 0; // High if inflammation
    timePoint.cb2 = Math.max(0.3, Math.min(1.0,
      cb2Base * circadianMultiplier + sleepRepairBoost + inflammationFactor + (Math.random() * 0.06 - 0.03)
    ));

    // FAAH ENZYME - Breaks down Anandamide (inverse relationship)
    timePoint.faah = Math.max(0.3, Math.min(0.8,
      0.60 - (timePoint.anandamide - 0.70) * 0.5 + (Math.random() * 0.08 - 0.04)
    ));

    // MAGL ENZYME - Breaks down 2-AG (inverse relationship)
    timePoint.magl = Math.max(0.3, Math.min(0.8,
      0.55 - (timePoint.twoAG - 0.75) * 0.5 + (Math.random() * 0.08 - 0.04)
    ));

    timeline.push(timePoint);
  }

  return timeline;
};

/**
 * Get patient statistics
 */
export const getPatientStats = () => {
  const activeCount = mockPatients.filter(p => p.status === 'active').length;
  const criticalCount = mockPatients.filter(p => p.status === 'critical').length;
  const avgEcbomeScore = mockPatients.reduce((sum, p) => sum + p.ecbomeScore, 0) / mockPatients.length;

  return {
    totalPatients: mockPatients.length,
    activePatients: activeCount,
    criticalPatients: criticalCount,
    averageEcbomeScore: avgEcbomeScore.toFixed(2),
    systemUptime: 98.5,
    dataPoints: '1.2M',
    lastUpdated: getTimestamp(0)
  };
};

export default {
  mockPatients,
  mockPatientDetails,
  generateRealtimeVitals,
  generateEcbomeTimeline,
  getPatientStats
};

