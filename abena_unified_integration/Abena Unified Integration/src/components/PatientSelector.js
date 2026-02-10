import React from 'react';
import { User, Heart, Brain, Activity } from 'lucide-react';

// Mock patient data based on the 5 sample cases
export const mockPatients = {
  patient_001: {
    id: 'ABENA-001',
    name: 'Michael Rodriguez',
    demographics: {
      age: 46,
      sex: 'Male',
      ethnicity: 'Hispanic',
      height: 175,
      weight: 99,
      bmi: 32.3
    },
    medicalHistory: {
      chiefComplaint: 'Occasional shortness of breath',
      conditions: ['Hypertension', 'Obesity', 'Coronary artery disease', 'Obstructive sleep apnea']
    },
    riskLevel: 'HIGH'
  },
  patient_002: {
    id: 'ABENA-002',
    name: 'Sarah Chen',
    demographics: {
      age: 32,
      sex: 'Female',
      ethnicity: 'Asian',
      height: 165,
      weight: 55,
      bmi: 20.2
    },
    medicalHistory: {
      chiefComplaint: 'Chronic low back pain with bilateral lower extremity radiculopathy',
      conditions: ['Chronic low back pain', 'Bilateral lower extremity radiculopathy']
    },
    riskLevel: 'LOW'
  },
  patient_003: {
    id: 'ABENA-003',
    name: 'Margaret Thompson',
    demographics: {
      age: 56,
      sex: 'Female',
      ethnicity: 'Caucasian',
      height: 162,
      weight: 85.5,
      bmi: 32.6
    },
    medicalHistory: {
      chiefComplaint: 'Management of Type 2 Diabetes Mellitus with complications',
      conditions: ['Type 2 Diabetes Mellitus', 'Diabetic peripheral neuropathy', 'Diabetic retinopathy', 'Chronic kidney disease']
    },
    riskLevel: 'HIGH'
  },
  patient_004: {
    id: 'ABENA-004',
    name: 'Robert Williams',
    demographics: {
      age: 72,
      sex: 'Male',
      ethnicity: 'African American',
      height: 178,
      weight: 86.8,
      bmi: 27.4
    },
    medicalHistory: {
      chiefComplaint: 'Multiple chronic conditions management',
      conditions: ['Hypertension', 'Atrial fibrillation', 'Chronic kidney disease', 'Osteoarthritis', 'Type 2 Diabetes', 'Depression']
    },
    riskLevel: 'CRITICAL'
  },
  patient_005: {
    id: 'ABENA-005',
    name: 'Alex Johnson',
    demographics: {
      age: 28,
      sex: 'Non-binary',
      ethnicity: 'Mixed',
      height: 170,
      weight: 63.4,
      bmi: 21.9
    },
    medicalHistory: {
      chiefComplaint: 'Anxiety and depression management',
      conditions: ['Generalized anxiety disorder', 'Major depressive disorder']
    },
    riskLevel: 'MEDIUM'
  }
};

const PatientSelector = ({ selectedPatient, onPatientSelect }) => {
  const patients = Object.values(mockPatients);

  const getRiskColor = (level) => {
    const colors = {
      'LOW': 'bg-green-100 text-green-800 border-green-300',
      'MEDIUM': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'HIGH': 'bg-red-100 text-red-800 border-red-300',
      'CRITICAL': 'bg-purple-100 text-purple-800 border-purple-300'
    };
    return colors[level] || colors['MEDIUM'];
  };

  const getBMICategory = (bmi) => {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal';
    if (bmi < 30) return 'Overweight';
    if (bmi < 35) return 'Obese Class I';
    if (bmi < 40) return 'Obese Class II';
    return 'Obese Class III';
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
      {patients.map((patient) => (
        <div
          key={patient.id}
          onClick={() => onPatientSelect(patient)}
          className={`
            relative p-6 rounded-lg border-2 cursor-pointer transition-all
            hover:shadow-lg hover:scale-105
            ${selectedPatient?.id === patient.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white'}
          `}
        >
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-full">
                <User className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-bold text-lg">{patient.name}</h3>
                <p className="text-sm text-gray-600">{patient.id}</p>
              </div>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getRiskColor(patient.riskLevel)}`}>
              {patient.riskLevel}
            </span>
          </div>

          <div className="space-y-2 mb-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Age:</span>
              <span className="font-medium">{patient.demographics.age} years</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Sex:</span>
              <span className="font-medium">{patient.demographics.sex}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">BMI:</span>
              <span className="font-medium">{patient.demographics.bmi} ({getBMICategory(patient.demographics.bmi)})</span>
            </div>
          </div>

          <div className="mb-4">
            <p className="text-sm font-semibold text-gray-700 mb-2">Chief Complaint:</p>
            <p className="text-sm text-gray-600">{patient.medicalHistory.chiefComplaint}</p>
          </div>

          <div className="flex flex-wrap gap-2">
            {patient.medicalHistory.conditions.slice(0, 2).map((condition, idx) => (
              <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                {condition}
              </span>
            ))}
            {patient.medicalHistory.conditions.length > 2 && (
              <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-xs font-semibold">
                +{patient.medicalHistory.conditions.length - 2} more
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default PatientSelector;

