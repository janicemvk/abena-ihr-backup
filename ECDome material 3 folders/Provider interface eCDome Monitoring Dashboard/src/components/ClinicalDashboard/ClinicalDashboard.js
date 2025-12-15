import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { usePatient } from '../../contexts/PatientContext';
import { useDashboard } from '../../contexts/DashboardContext';
import PatientSelector from './PatientSelector';
import PatientOverview from './PatientOverview';
import EbdomeTimeline from './EcdomeTimeline';
import ModuleAnalysis from './ModuleAnalysis';
import EbdomeComponents from './EcdomeComponents';
import RealtimeMonitoring from './RealtimeMonitoring';
import PredictiveAlerts from './PredictiveAlerts';
import ClinicalRecommendations from './ClinicalRecommendations';
import QuickActions from './QuickActions';
import DashboardControls from './DashboardControls';
import MedicalHistory from './MedicalHistory';
import QuantumResults from './QuantumResults';
import LoadingSpinner from '../Common/LoadingSpinner';
import ErrorBoundary from '../Common/ErrorBoundary';
import { Activity, AlertTriangle, TrendingUp, Eye, Settings } from 'lucide-react';
import { generateEcdomeTimeline } from '../../services/mockPatientData';

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
  const [timelineData, setTimelineData] = useState([]);
  const [moduleData, setModuleData] = useState(null);

  // Initialize with default patient if none selected
  useEffect(() => {
    if (!selectedPatient) {
      patientActions.selectPatient('PAT-001');
    }
  }, [selectedPatient, patientActions]);

  // Generate timeline data when patient or timeRange changes
  useEffect(() => {
    if (selectedPatient) {
      const hours = timeRange === '24h' ? 24 : timeRange === '7d' ? 168 : timeRange === '30d' ? 720 : 24;
      const timeline = generateEcdomeTimeline(selectedPatient, Math.min(hours, 48)); // Limit to 48 hours for performance
      setTimelineData(timeline);
      console.log(`✅ Generated ${timeline.length} timeline data points for ${selectedPatient}`);
    }
  }, [selectedPatient, timeRange]);

  // Extract 12-module data from patient data
  useEffect(() => {
    if (patientData && patientData.data && patientData.data.ebdomeProfile) {
      const components = patientData.data.ebdomeProfile.components;
      if (components) {
        // Transform data structure: "reading" field to "score" field
        const transformedData = {};
        Object.keys(components).forEach(key => {
          transformedData[key] = {
            ...components[key],
            score: components[key].reading || 0.5 // Map "reading" to "score"
          };
        });
        setModuleData(transformedData);
        console.log(`✅ Loaded 12-module data for ${selectedPatient}:`, Object.keys(transformedData).length, 'modules');
      }
    }
  }, [patientData, selectedPatient]);

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
      <>
        {/* TEST: Yellow box in early return */}
        <div style={{ border: '10px solid red', padding: '30px', margin: '30px', backgroundColor: 'yellow', minHeight: '300px', zIndex: 9999, position: 'relative' }}>
          <h1 style={{ color: 'red', fontSize: '32px', fontWeight: 'bold' }}>🔬 EARLY RETURN: NO PATIENT DATA</h1>
        </div>
        <div className="flex-1 flex items-center justify-center min-h-screen">
          <div className="text-center">
            <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No patient selected</h3>
            <p className="text-gray-600">Please select a patient to view their clinical dashboard.</p>
          </div>
        </div>
      </>
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
                <p className="text-gray-600 mt-1">Real-time patient monitoring and eBDome analysis</p>
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

            {/* Row 3: Medical History & Records - Full Width */}
            <motion.div variants={itemVariants}>
              <MedicalHistory
                patientData={patientData}
              />
            </motion.div>

            {/* Row 4: Real-time Monitoring - Full Width */}
            <motion.div variants={itemVariants}>
              <RealtimeMonitoring
                patientId={selectedPatient}
                realtimeData={realtimeData}
              />
            </motion.div>

            {/* Row 5: eBDome Components - Full Width */}
            <motion.div variants={itemVariants}>
              <EbdomeComponents
                patientData={patientData}
                realtimeData={realtimeData}
              />
            </motion.div>

            {/* Row 6: eBDome Timeline - Full Width */}
            <motion.div variants={itemVariants}>
              <EbdomeTimeline 
                patientId={selectedPatient}
                timeRange={timeRange}
                timelineData={timelineData}
                viewMode={viewMode}
              />
            </motion.div>

            {/* Row 7: Module Analysis - Full Width */}
            <motion.div variants={itemVariants}>
              <ModuleAnalysis
                patientId={selectedPatient}
                moduleData={moduleData}
                selectedModules={selectedModules}
                viewMode={viewMode}
                onModuleSelect={setSelectedModules}
                timeRange={timeRange}
              />
            </motion.div>

            {/* Row 8: Quantum Health Analysis - Full Width */}
            <motion.div variants={itemVariants}>
              <QuantumResults
                patientId={selectedPatient}
                patientData={patientData}
              />
            </motion.div>

            {/* Row 9: Predictive Alerts - Full Width */}
            <motion.div variants={itemVariants}>
              <PredictiveAlerts
                patientId={selectedPatient}
                alerts={patientData?.data?.alerts || alerts}
              />
            </motion.div>

            {/* Row 10: Clinical Recommendations - Full Width */}
            <motion.div variants={itemVariants}>
              <ClinicalRecommendations
                patientData={patientData}
                recommendations={patientData?.data?.recommendations || []}
                realtimeData={realtimeData}
              />
            </motion.div>

            {/* Row 11: Quick Actions - Full Width */}
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