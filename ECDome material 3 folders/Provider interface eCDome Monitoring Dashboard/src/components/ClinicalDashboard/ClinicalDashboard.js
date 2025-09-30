import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { usePatient } from '../../contexts/PatientContext';
import { useDashboard } from '../../contexts/DashboardContext';
import PatientSelector from './PatientSelector';
import PatientOverview from './PatientOverview';
import EcdomeTimeline from './EcdomeTimeline';
import ModuleAnalysis from './ModuleAnalysis';
import EcdomeComponents from './EcdomeComponents';
import RealtimeMonitoring from './RealtimeMonitoring';
import PredictiveAlerts from './PredictiveAlerts';
import ClinicalRecommendations from './ClinicalRecommendations';
import QuickActions from './QuickActions';
import DashboardControls from './DashboardControls';
import LoadingSpinner from '../Common/LoadingSpinner';
import ErrorBoundary from '../Common/ErrorBoundary';
import { Activity, AlertTriangle, TrendingUp, Eye, Settings } from 'lucide-react';

const ClinicalDashboard = () => {
  const { 
    patientData, 
    selectedPatient, 
    loading, 
    error, 
    actions: patientActions 
  } = usePatient();
  
  const { 
    activeModule, 
    timeRange, 
    realtimeData, 
    alerts, 
    actions: dashboardActions 
  } = useDashboard();

  const [viewMode, setViewMode] = useState('overview'); // overview, detailed, comparison
  const [selectedModules, setSelectedModules] = useState([]);

  // Initialize with default patient if none selected
  useEffect(() => {
    if (!selectedPatient) {
      patientActions.selectPatient('PAT-001');
    }
  }, [selectedPatient, patientActions]);

  // Container animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 15
      }
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-screen">
        <LoadingSpinner size="large" message="Loading patient data..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load patient data</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!patientData) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No patient selected</h3>
          <p className="text-gray-600">Please select a patient to view their clinical dashboard.</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="p-6 bg-clinical-bg"
      >
        <div className="max-w-7xl mx-auto">
          {/* Dashboard Header */}
          <motion.div variants={itemVariants} className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Clinical Dashboard</h1>
                <p className="text-gray-600 mt-1">Real-time patient monitoring and eCDome analysis</p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-gray-600">Live Monitoring</span>
                </div>
                <button className="p-2 text-gray-400 hover:text-gray-600">
                  <Eye className="h-5 w-5" />
                </button>
                <button className="p-2 text-gray-400 hover:text-gray-600">
                  <Settings className="h-5 w-5" />
                </button>
              </div>
            </div>
          </motion.div>

          {/* Dashboard Controls */}
          <motion.div variants={itemVariants} className="mb-6">
            <DashboardControls
              timeRange={timeRange}
              setTimeRange={dashboardActions.setTimeRange}
              viewMode={viewMode}
              setViewMode={setViewMode}
              selectedModules={selectedModules}
              setSelectedModules={setSelectedModules}
            />
          </motion.div>

          {/* Main Dashboard - Row-based Layout */}
          <motion.div 
            variants={containerVariants}
            className="space-y-6"
          >
            {/* Row 1: Patient Selection */}
            <motion.div variants={itemVariants}>
              <PatientSelector
                selectedPatient={selectedPatient}
                onPatientSelect={patientActions.selectPatient}
              />
            </motion.div>

            {/* Row 2: Patient Overview - Full Width */}
            <motion.div variants={itemVariants}>
              <PatientOverview 
                patientData={patientData} 
                realtimeData={realtimeData}
              />
            </motion.div>

            {/* Row 3: Real-time Monitoring - Full Width */}
            <motion.div variants={itemVariants}>
              <RealtimeMonitoring
                patientId={selectedPatient}
                realtimeData={realtimeData}
              />
            </motion.div>

            {/* Row 4: eCDome Components - Full Width */}
            <motion.div variants={itemVariants}>
              <EcdomeComponents
                patientData={patientData}
                realtimeData={realtimeData}
              />
            </motion.div>

            {/* Row 5: eCDome Timeline - Full Width */}
            <motion.div variants={itemVariants}>
              <EcdomeTimeline 
                patientId={selectedPatient}
                timeRange={timeRange}
              />
            </motion.div>

            {/* Row 6: Module Analysis - Full Width */}
            <motion.div variants={itemVariants}>
              <ModuleAnalysis
                patientId={selectedPatient}
                selectedModules={selectedModules}
                timeRange={timeRange}
              />
            </motion.div>

            {/* Row 7: Predictive Alerts - Full Width */}
            <motion.div variants={itemVariants}>
              <PredictiveAlerts
                patientId={selectedPatient}
                alerts={alerts}
              />
            </motion.div>

            {/* Row 8: Clinical Recommendations - Full Width */}
            <motion.div variants={itemVariants}>
              <ClinicalRecommendations
                patientData={patientData}
                realtimeData={realtimeData}
              />
            </motion.div>

            {/* Row 9: Quick Actions - Full Width */}
            <motion.div variants={itemVariants}>
              <QuickActions
                patientId={selectedPatient}
                patientData={patientData}
              />
            </motion.div>
          </motion.div>
        </div>
      </motion.div>
    </ErrorBoundary>
  );
};

export default ClinicalDashboard;