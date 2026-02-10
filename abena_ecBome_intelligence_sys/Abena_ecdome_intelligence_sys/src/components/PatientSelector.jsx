import React from 'react';
import { mockPatients } from '../data/testData';

const PatientSelector = ({ selectedPatient, onPatientSelect }) => {
  const patients = Object.values(mockPatients);

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Select Patient for Analysis</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {patients.map((patient) => (
          <div
            key={patient.id}
            onClick={() => onPatientSelect(patient)}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              selectedPatient?.id === patient.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">
                {patient.demographics.firstName} {patient.demographics.lastName}
              </h4>
              <span className="text-sm text-gray-500">{patient.id}</span>
            </div>
            <div className="text-sm text-gray-600 space-y-1">
              <p><strong>Age:</strong> {patient.demographics.age} years, {patient.demographics.gender}</p>
              <p><strong>BMI:</strong> {patient.demographics.bmi} ({patient.demographics.bmiCategory})</p>
              <p><strong>Chief Complaint:</strong> {patient.medicalHistory.chiefComplaint}</p>
              <div className="mt-2">
                <div className="flex flex-wrap gap-1">
                  {patient.medicalHistory.conditions.slice(0, 2).map((condition, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                      {condition}
                    </span>
                  ))}
                  {patient.medicalHistory.conditions.length > 2 && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                      +{patient.medicalHistory.conditions.length - 2} more
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PatientSelector;
