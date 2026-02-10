import React, { useState, useEffect } from 'react';
import ECBomeChatbot from './ECBomeChatbot';
import PatientSelector from './PatientSelector';
import { testPatientData, mockPatients } from '../data/testData';

const ECBomeIntelligenceSystem = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [data, setData] = useState(null);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [showChatbot, setShowChatbot] = useState(false);

  useEffect(() => {
    // Simulate data loading
    setTimeout(() => {
      setData({
        status: 'active',
        modules: ['cardiovascular', 'respiratory', 'metabolic', 'neurological', 'immunological']
      });
      // Set default patient (Case 2: Young Active Female)
      setSelectedPatient(mockPatients.patient_002);
      setIsLoading(false);
    }, 1000);
  }, []);

  const handlePatientSelect = (patient) => {
    setSelectedPatient(patient);
    setShowChatbot(false); // Close chatbot when switching patients
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading eCBome Intelligence System...</p>
        </div>
                </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">
            eCBome Intelligence System
          </h1>
          
          {/* Patient Selector */}
          <PatientSelector 
            selectedPatient={selectedPatient} 
            onPatientSelect={handlePatientSelect} 
          />

          {/* Selected Patient Info */}
          {selectedPatient && (
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                Current Patient: {selectedPatient.demographics.firstName} {selectedPatient.demographics.lastName}
                </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                  <h4 className="font-medium text-gray-700">Demographics</h4>
                  <p className="text-sm text-gray-600">
                    {selectedPatient.demographics.age} years, {selectedPatient.demographics.gender}<br/>
                    BMI: {selectedPatient.demographics.bmi} ({selectedPatient.demographics.bmiCategory})
            </p>
          </div>
                <div>
                  <h4 className="font-medium text-gray-700">Chief Complaint</h4>
                  <p className="text-sm text-gray-600">{selectedPatient.medicalHistory.chiefComplaint}</p>
                      </div>
                <div>
                  <h4 className="font-medium text-gray-700">Endocannabinoid Status</h4>
                  <p className="text-sm text-gray-600">
                    Anandamide: {(selectedPatient.endocannabinoidData.levels.anandamide * 100).toFixed(1)}%<br/>
                    CB1 Activity: {(selectedPatient.endocannabinoidData.receptorActivity.CB1 * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.modules.map((module, index) => (
              <div key={index} className="bg-blue-50 rounded-lg p-4">
                <h3 className="font-semibold text-blue-800 capitalize">
                  {module.replace(/([A-Z])/g, ' $1').trim()}
              </h3>
                <p className="text-sm text-blue-600 mt-2">
                  Status: Active
                </p>
                </div>
              ))}
          </div>

          <div className="mt-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-gray-800">
                eCBome AI Assistant
              </h2>
              <button
                onClick={() => setShowChatbot(!showChatbot)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                {showChatbot ? 'Hide' : 'Open'} Chatbot
              </button>
                </div>

            {showChatbot && selectedPatient && (
              <ECBomeChatbot 
                patientData={selectedPatient} 
                onClose={() => setShowChatbot(false)}
              />
            )}
                  </div>
                  </div>
                </div>
    </div>
  );
};

export default ECBomeIntelligenceSystem; 