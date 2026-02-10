import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Users, 
  Search, 
  Filter, 
  User, 
  Activity, 
  Heart, 
  AlertTriangle,
  ChevronRight,
  TrendingUp,
  TrendingDown,
  Calendar,
  Phone,
  Mail
} from 'lucide-react';
import { usePatient } from '../../contexts/PatientContext';
import { mockPatients } from '../../services/mockPatientData';
import HelpInfo from '../Common/HelpInfo';

const PatientList = () => {
  const navigate = useNavigate();
  const { selectedPatient, actions: patientActions } = usePatient();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRisk, setFilterRisk] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filteredPatients, setFilteredPatients] = useState(mockPatients);

  // Filter patients
  useEffect(() => {
    let filtered = [...mockPatients];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(patient => 
        patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        patient.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        patient.mrn.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Risk level filter
    if (filterRisk !== 'all') {
      filtered = filtered.filter(patient => patient.riskLevel === filterRisk);
    }

    // Status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(patient => patient.status === filterStatus);
    }

    setFilteredPatients(filtered);
  }, [searchTerm, filterRisk, filterStatus]);

  const handlePatientClick = (patientId) => {
    patientActions.selectPatient(patientId);
    navigate('/dashboard');
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'critical': return 'bg-red-100 text-red-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskBadgeColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-700 border-red-300';
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'low': return 'bg-green-100 text-green-700 border-green-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const geteCBomeScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    if (score >= 0.4) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="w-7 h-7 text-blue-600" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-3xl font-bold text-gray-900">Patient Management</h1>
                <HelpInfo 
                  helpContent={{
                    title: 'Patient Management System',
                    subtitle: 'Comprehensive Patient Registry',
                    medical: 'The Patient Management system provides a centralized registry of all patients under care. It enables rapid patient identification, risk stratification, and access to complete medical records. The system integrates real-time eCBome monitoring data, clinical alerts, and treatment protocols for each patient. Providers can quickly filter by risk level, status, or search by demographics to prioritize care and manage patient panels efficiently.',
                    simple: 'This is your complete patient list - all the people you\'re caring for in one place. You can search for any patient by name or ID, filter by who needs urgent attention (high risk), and see at-a-glance how everyone is doing. Click on any patient to see their full health information and history. It\'s like a digital patient chart organizer.',
                    significance: 'PURPOSE: Centralized patient registry for efficient care coordination. BENEFITS: Quick patient lookup, risk-based prioritization, real-time health status visibility, streamlined workflow. USE CASES: Daily patient rounding, emergency patient identification, risk stratification, care team coordination, population health management. CLINICAL VALUE: Reduces patient lookup time by 80%, enables proactive care for high-risk patients, improves care coordination across teams.',
                    relatedTopics: ['Risk Stratification', 'Clinical Workflow', 'Population Health', 'eCBome Monitoring']
                  }}
                  size="sm"
                  position="modal"
                />
              </div>
              <p className="text-gray-600">Manage and monitor your patient panel</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-600">{filteredPatients.length} of {mockPatients.length} patients</span>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
            {/* Search */}
            <div className="md:col-span-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by name, ID, or MRN..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Risk Filter */}
            <div className="md:col-span-3">
              <select
                value={filterRisk}
                onChange={(e) => setFilterRisk(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Risk Levels</option>
                <option value="high">High Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="low">Low Risk</option>
              </select>
            </div>

            {/* Status Filter */}
            <div className="md:col-span-3">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="critical">Critical</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          {/* Active Filters */}
          {(searchTerm || filterRisk !== 'all' || filterStatus !== 'all') && (
            <div className="mt-3 flex items-center space-x-2">
              <span className="text-sm text-gray-600">Active filters:</span>
              {searchTerm && (
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  Search: "{searchTerm}"
                </span>
              )}
              {filterRisk !== 'all' && (
                <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                  Risk: {filterRisk}
                </span>
              )}
              {filterStatus !== 'all' && (
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                  Status: {filterStatus}
                </span>
              )}
              <button
                onClick={() => {
                  setSearchTerm('');
                  setFilterRisk('all');
                  setFilterStatus('all');
                }}
                className="text-xs text-blue-600 hover:text-blue-800"
              >
                Clear all
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Patient List Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Patient</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Status</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Risk Level</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">eCBome Score</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Last Visit</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Provider</th>
              <th className="px-6 py-4 text-right text-xs font-medium text-gray-700 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredPatients.map((patient, index) => (
              <motion.tr
                key={patient.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03 }}
                onClick={() => handlePatientClick(patient.id)}
                className={`cursor-pointer transition-colors hover:bg-blue-50 ${
                  selectedPatient === patient.id ? 'bg-blue-50' : ''
                }`}
              >
                {/* Patient Info */}
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{patient.name}</div>
                      <div className="text-sm text-gray-600">{patient.id} • Age {patient.age} • {patient.gender}</div>
                      <div className="text-xs text-gray-500">MRN: {patient.mrn}</div>
                    </div>
                  </div>
                </td>

                {/* Status */}
                <td className="px-6 py-4">
                  <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${getStatusColor(patient.status)}`}>
                    {patient.status.toUpperCase()}
                  </span>
                </td>

                {/* Risk Level */}
                <td className="px-6 py-4">
                  <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full border ${getRiskBadgeColor(patient.riskLevel)}`}>
                    {patient.riskLevel.toUpperCase()}
                  </span>
                </td>

                {/* eCBome Score */}
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-2">
                    <div className={`text-xl font-bold ${geteCBomeScoreColor(patient.ecbomeScore)}`}>
                      {(patient.ecbomeScore * 100).toFixed(0)}%
                    </div>
                    <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${geteCBomeScoreColor(patient.ecbomeScore).replace('text-', 'bg-')}`}
                        style={{ width: `${(patient.ecbomeScore * 100).toFixed(0)}%` }}
                      />
                    </div>
                  </div>
                </td>

                {/* Last Visit */}
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-1 text-sm text-gray-600">
                    <Calendar className="w-4 h-4" />
                    <span>{new Date(patient.lastVisit).toLocaleDateString()}</span>
                  </div>
                </td>

                {/* Provider */}
                <td className="px-6 py-4 text-sm text-gray-600">
                  {patient.provider}
                </td>

                {/* Actions */}
                <td className="px-6 py-4">
                  <div className="flex items-center justify-end space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handlePatientClick(patient.id);
                      }}
                      className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors flex items-center space-x-1"
                    >
                      <Activity className="w-3 h-3" />
                      <span>View</span>
                    </button>
                    <button
                      onClick={(e) => e.stopPropagation()}
                      className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      title="Call Patient"
                    >
                      <Phone className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => e.stopPropagation()}
                      className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      title="Message Patient"
                    >
                      <Mail className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* No Results */}
      {filteredPatients.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No patients found</h3>
          <p className="text-gray-600 mb-4">
            No patients match your current filters or search criteria.
          </p>
          <button
            onClick={() => {
              setSearchTerm('');
              setFilterRisk('all');
              setFilterStatus('all');
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Summary Stats */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Patients</p>
              <p className="text-2xl font-bold text-gray-900">{mockPatients.length}</p>
            </div>
            <Users className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">High Risk</p>
              <p className="text-2xl font-bold text-red-600">
                {mockPatients.filter(p => p.riskLevel === 'high').length}
              </p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Critical Status</p>
              <p className="text-2xl font-bold text-orange-600">
                {mockPatients.filter(p => p.status === 'critical').length}
              </p>
            </div>
            <Activity className="w-8 h-8 text-orange-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Avg eCBome Score</p>
              <p className="text-2xl font-bold text-purple-600">
                {(mockPatients.reduce((sum, p) => sum + p.ecbomeScore, 0) / mockPatients.length * 100).toFixed(0)}%
              </p>
            </div>
            <Heart className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientList; 