import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, User, Users, ChevronDown, Clock, Activity } from 'lucide-react';
import { usePatient } from '../../contexts/PatientContext';

const PatientSelector = ({ selectedPatient, onPatientSelect }) => {
  const { patients, loading } = usePatient();
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [filteredPatients, setFilteredPatients] = useState([]);

  // Filter patients based on search term
  useEffect(() => {
    if (searchTerm) {
      const filtered = patients.filter(patient => 
        patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        patient.id.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredPatients(filtered);
    } else {
      setFilteredPatients(patients.slice(0, 10)); // Show first 10 patients
    }
  }, [searchTerm, patients]);

  // Get selected patient data
  const selectedPatientData = patients.find(p => p.id === selectedPatient);

  const handlePatientSelect = (patientId) => {
    onPatientSelect(patientId);
    setIsOpen(false);
    setSearchTerm('');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'critical': return 'bg-red-100 text-red-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskLevelColor = (riskLevel) => {
    switch (riskLevel) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="relative">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="dashboard-card"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Users className="h-5 w-5 mr-2 text-ecbome-primary" />
            Patient Selection
          </h3>
          <div className="text-sm text-gray-500">
            {patients.length} patients available
          </div>
        </div>

        {/* Current Patient Display */}
        {selectedPatientData && (
          <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="h-12 w-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <User className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">{selectedPatientData.name}</h4>
                  <div className="flex items-center space-x-3 text-sm text-gray-600">
                    <span>ID: {selectedPatientData.id}</span>
                    <span>•</span>
                    <span>Age: {selectedPatientData.age}</span>
                    <span>•</span>
                    <span className={`font-medium ${getRiskLevelColor(selectedPatientData.riskLevel)}`}>
                      {selectedPatientData.riskLevel?.toUpperCase()} Risk
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`status-badge ${getStatusColor(selectedPatientData.status)}`}>
                  {selectedPatientData.status}
                </span>
                {selectedPatientData.ecbomeScore && (
                  <div className="flex items-center space-x-1 text-sm">
                    <Activity className="h-4 w-4 text-ecbome-primary" />
                    <span className="font-medium">{Math.round(selectedPatientData.ecbomeScore * 100)}%</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Patient Selector */}
        <div className="relative">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="w-full flex items-center justify-between p-3 border border-gray-300 rounded-lg hover:border-ecbome-primary focus:outline-none focus:ring-2 focus:ring-ecbome-primary focus:border-transparent transition-colors"
          >
            <div className="flex items-center space-x-2">
              <Search className="h-4 w-4 text-gray-400" />
              <span className="text-gray-700">
                {selectedPatientData ? 'Change Patient' : 'Select Patient'}
              </span>
            </div>
            <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Dropdown */}
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-xl z-50 max-h-96 overflow-hidden"
            >
              {/* Search Input */}
              <div className="p-3 border-b border-gray-200">
                <div className="relative">
                  <Search className="h-4 w-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="Search patients..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-ecbome-primary focus:border-transparent"
                  />
                </div>
              </div>

              {/* Patient List */}
              <div className="max-h-80 overflow-y-auto scrollbar-thin">
                {loading ? (
                  <div className="p-4 text-center text-gray-500">
                    <div className="loading-spinner mx-auto mb-2"></div>
                    Loading patients...
                  </div>
                ) : filteredPatients.length === 0 ? (
                  <div className="p-4 text-center text-gray-500">
                    No patients found
                  </div>
                ) : (
                  filteredPatients.map((patient) => (
                    <motion.button
                      key={patient.id}
                      onClick={() => handlePatientSelect(patient.id)}
                      className={`w-full p-4 text-left hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0 ${
                        selectedPatient === patient.id ? 'bg-blue-50' : ''
                      }`}
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="h-10 w-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                            <User className="h-5 w-5 text-white" />
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{patient.name}</div>
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <span>{patient.id}</span>
                              <span>•</span>
                              <span>{patient.age}y</span>
                              <span>•</span>
                              <span>{patient.gender}</span>
                              {patient.lastVisit && (
                                <>
                                  <span>•</span>
                                  <div className="flex items-center space-x-1">
                                    <Clock className="h-3 w-3" />
                                    <span>{patient.lastVisit}</span>
                                  </div>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`status-badge ${getStatusColor(patient.status)}`}>
                            {patient.status}
                          </span>
                          {patient.ecbomeScore && (
                            <div className="flex items-center space-x-1 text-sm">
                              <Activity className="h-4 w-4 text-ecbome-primary" />
                              <span className="font-medium">{Math.round(patient.ecbomeScore * 100)}%</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.button>
                  ))
                )}
              </div>
            </motion.div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-ecbome-primary">{patients.length}</div>
            <div className="text-sm text-gray-600">Total Patients</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {patients.filter(p => p.status === 'active').length}
            </div>
            <div className="text-sm text-gray-600">Active</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {patients.filter(p => p.status === 'critical').length}
            </div>
            <div className="text-sm text-gray-600">Critical</div>
          </div>
        </div>
      </motion.div>

      {/* Click outside to close */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default PatientSelector; 