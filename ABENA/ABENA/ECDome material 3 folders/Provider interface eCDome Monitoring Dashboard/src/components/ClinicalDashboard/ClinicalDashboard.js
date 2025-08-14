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
          <p className="text-gray-600">Please select a patient to view their data</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="flex-1 p-6 space-y-6">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          {/* Dashboard Controls */}
          <motion.div variants={itemVariants}>
            <DashboardControls
              viewMode={viewMode}
              setViewMode={setViewMode}
              timeRange={timeRange}
              onTimeRangeChange={dashboardActions.setTimeRange}
              selectedModules={selectedModules}
              setSelectedModules={setSelectedModules}
            />
          </motion.div>

          {/* Patient Selector */}
          <motion.div variants={itemVariants}>
            <PatientSelector
              selectedPatient={selectedPatient}
              onPatientSelect={patientActions.selectPatient}
            />
          </motion.div>

          {/* Patient Overview */}
          <motion.div variants={itemVariants}>
            <PatientOverview
              patientData={patientData}
              realtimeData={realtimeData}
            />
          </motion.div>

          {/* Critical Alerts */}
          {alerts.length > 0 && (
            <motion.div variants={itemVariants}>
              <PredictiveAlerts
                alerts={alerts}
                patientData={patientData}
                onAlertDismiss={dashboardActions.removeAlert}
              />
            </motion.div>
          )}

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Charts and Analysis */}
            <div className="lg:col-span-2 space-y-6">
              {/* eCDome Timeline */}
              <motion.div variants={itemVariants}>
                <EcdomeTimeline
                  timelineData={patientData.timelineData}
                  timeRange={timeRange}
                  viewMode={viewMode}
                />
              </motion.div>

              {/* Module Analysis */}
              <motion.div variants={itemVariants}>
                <ModuleAnalysis
                  moduleData={patientData.moduleData}
                  selectedModules={selectedModules}
                  viewMode={viewMode}
                  onModuleSelect={setSelectedModules}
                />
              </motion.div>

              {/* eCDome Components */}
              <motion.div variants={itemVariants}>
                <EcdomeComponents
                  ecdomeProfile={patientData.ecdomeProfile}
                  realtimeData={realtimeData}
                />
              </motion.div>
            </div>

            {/* Right Column - Monitoring and Actions */}
            <div className="space-y-6">
              {/* Real-time Monitoring */}
              <motion.div variants={itemVariants}>
                <RealtimeMonitoring
                  realtimeData={realtimeData}
                  patientData={patientData}
                />
              </motion.div>

              {/* Clinical Recommendations */}
              <motion.div variants={itemVariants}>
                <ClinicalRecommendations
                  recommendations={patientData.recommendations}
                  patientData={patientData}
                />
              </motion.div>

              {/* Quick Actions */}
              <motion.div variants={itemVariants}>
                <QuickActions
                  patientId={selectedPatient}
                  patientData={patientData}
                />
              </motion.div>
            </div>
          </div>

          {/* Performance Metrics Footer */}
          <motion.div variants={itemVariants} className="mt-8">
            <div className="dashboard-card">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-6">
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="h-4 w-4 text-green-500" />
                    <span className="text-sm text-gray-600">Dashboard Performance</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    Data refresh: {realtimeData.timestamp ? 
                      new Date(realtimeData.timestamp).toLocaleTimeString() : 
                      'Loading...'
                    }
                  </div>
                </div>
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <span>Latency: ~200ms</span>
                  <span>Uptime: 99.98%</span>
                  <div className="flex items-center space-x-1">
                    <Eye className="h-4 w-4" />
                    <span>Live</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </ErrorBoundary>
  );
};

export default ClinicalDashboard; 