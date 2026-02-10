import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Atom,
  Activity,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  RefreshCw,
  Zap,
  Brain,
  Heart,
  Pill,
  Leaf
} from 'lucide-react';
// Import quantum service with error handling
let quantumService;
try {
  const quantumServiceModule = require('../../services/quantumService');
  quantumService = quantumServiceModule.quantumService || quantumServiceModule.default;
  console.log('🔬 QuantumService imported successfully');
} catch (e) {
  console.error('🔬 Failed to import quantumService:', e);
  // Create mock service to prevent crashes
  quantumService = {
    getPatientAnalyses: async () => ({ success: true, data: [], count: 0 }),
    analyzePatient: async () => ({ success: false, error: 'Service unavailable' }),
  };
}
import LoadingSpinner from '../Common/LoadingSpinner';
// Using dashboard-card pattern like other components

const QuantumResults = ({ patientId, patientData }) => {
  const [analysisResults, setAnalysisResults] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Debug logging - ALWAYS LOG
  useEffect(() => {
    console.log('🔬🔬🔬 QuantumResults component MOUNTED', { patientId, patientData: !!patientData });
    console.log('🔬 Component props:', { patientId, hasPatientData: !!patientData });
  }, []);

  // Load analysis history on mount
  useEffect(() => {
    console.log('🔬 QuantumResults: patientId changed to:', patientId);
    if (patientId) {
      console.log('🔬 Loading analysis history for:', patientId);
      loadAnalysisHistory();
    } else {
      console.warn('🔬 QuantumResults: No patientId provided - but component will still render');
    }
  }, [patientId]);

  const loadAnalysisHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await quantumService.getPatientAnalyses(patientId, 5);
      if (result.success) {
        setAnalysisHistory(result.data);
        // Set latest as current results
        if (result.data.length > 0) {
          setAnalysisResults(result.data[0]);
        }
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to load analysis history');
    } finally {
      setLoading(false);
    }
  };

  const runQuantumAnalysis = async () => {
    if (!patientId) {
      setError('Patient ID is required');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // Prepare analysis options from patient data
      const options = {
        symptoms: patientData?.symptoms || [],
        biomarkers: patientData?.biomarkers || {},
        medications: patientData?.medications?.map(m => m.name || m.medication) || [],
      };

      const result = await quantumService.analyzePatient(patientId, options);

      if (result.success) {
        setAnalysisResults(result.data);
        // Reload history to include new analysis
        await loadAnalysisHistory();
      } else {
        setError(result.error || 'Analysis failed');
      }
    } catch (err) {
      setError('Failed to run quantum analysis: ' + err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const formatScore = (score) => {
    if (typeof score !== 'number') return 'N/A';
    return (score * 100).toFixed(1) + '%';
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score) => {
    if (score >= 0.8) return 'bg-green-100';
    if (score >= 0.6) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  // Always render - don't hide component
  console.log('🔬🔬🔬 QuantumResults RENDER CALLED:', { 
    loading, 
    hasResults: !!analysisResults, 
    error, 
    patientId, 
    analysisHistoryLength: analysisHistory.length,
    willShowLoading: loading && !analysisResults,
    willShowResults: !!analysisResults,
    willShowEmpty: !loading && !analysisResults
  });
  
  // Always show component for visibility

  if (loading && !analysisResults) {
    return (
      <div className="dashboard-card" style={{ minHeight: '200px', border: '3px solid purple', backgroundColor: '#faf5ff' }}>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Atom className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">🔬 Quantum Health Analysis</h3>
              <p className="text-sm text-gray-500">Advanced quantum computing-based health analysis</p>
            </div>
          </div>
        </div>
        <LoadingSpinner message="Loading quantum analysis..." />
      </div>
    );
  }

  return (
    <div
      className="dashboard-card"
      style={{ 
        minHeight: '300px', 
        border: '3px solid #8B5CF6', 
        backgroundColor: '#faf5ff',
        marginBottom: '24px',
        display: 'block',
        visibility: 'visible',
        opacity: 1
      }}
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Atom className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">🔬 Quantum Health Analysis</h3>
            <p className="text-sm text-gray-500">Advanced quantum computing-based health analysis</p>
          </div>
        </div>
        <button
          onClick={runQuantumAnalysis}
          disabled={isAnalyzing || !patientId}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isAnalyzing ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Zap className="w-4 h-4" />
              Run Quantum Analysis
            </>
          )}
        </button>
      </div>
      <div>
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        )}

        {analysisResults ? (
          <div className="space-y-6">
            {/* Main Scores */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Quantum Health Score */}
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                className={`p-6 rounded-xl ${getScoreBgColor(analysisResults.quantum_health_score)}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Brain className="w-5 h-5 text-blue-600" />
                    <span className="font-semibold text-gray-700">Quantum Health Score</span>
                  </div>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <div className={`text-4xl font-bold ${getScoreColor(analysisResults.quantum_health_score)}`}>
                  {formatScore(analysisResults.quantum_health_score)}
                </div>
                <div className="text-sm text-gray-600 mt-2">
                  Based on comprehensive quantum analysis
                </div>
              </motion.div>

              {/* System Balance */}
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                className={`p-6 rounded-xl ${getScoreBgColor(analysisResults.system_balance)}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Heart className="w-5 h-5 text-red-600" />
                    <span className="font-semibold text-gray-700">System Balance</span>
                  </div>
                  <Activity className="w-5 h-5 text-blue-600" />
                </div>
                <div className={`text-4xl font-bold ${getScoreColor(analysisResults.system_balance)}`}>
                  {formatScore(analysisResults.system_balance)}
                </div>
                <div className="text-sm text-gray-600 mt-2">
                  eCBome system equilibrium
                </div>
              </motion.div>
            </div>

            {/* Analysis Details */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Symptoms Analyzed</div>
                <div className="text-2xl font-bold text-gray-800">
                  {analysisResults.symptoms_analyzed || 0}
                </div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Biomarkers</div>
                <div className="text-2xl font-bold text-gray-800">
                  {analysisResults.biomarkers_analyzed || 0}
                </div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Medications</div>
                <div className="text-2xl font-bold text-gray-800">
                  {analysisResults.medications_checked || 0}
                </div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-1">Herbs Evaluated</div>
                <div className="text-2xl font-bold text-gray-800">
                  {analysisResults.herbs_evaluated || 0}
                </div>
              </div>
            </div>

            {/* Drug Interactions */}
            {analysisResults.drug_interactions && analysisResults.drug_interactions.length > 0 && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <Pill className="w-5 h-5 text-yellow-700" />
                  <span className="font-semibold text-yellow-900">Drug Interactions</span>
                </div>
                <div className="space-y-2">
                  {analysisResults.drug_interactions.map((interaction, idx) => (
                    <div key={idx} className="text-sm text-yellow-800">
                      <span className="font-medium">{interaction.medication1}</span> +{' '}
                      <span className="font-medium">{interaction.medication2}</span>
                      {interaction.severity && (
                        <span className={`ml-2 px-2 py-1 rounded text-xs ${
                          interaction.severity === 'high' ? 'bg-red-200' : 'bg-yellow-200'
                        }`}>
                          {interaction.severity}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {analysisResults.recommendations && analysisResults.recommendations.length > 0 && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="w-5 h-5 text-blue-700" />
                  <span className="font-semibold text-blue-900">Recommendations</span>
                </div>
                <ul className="space-y-2">
                  {analysisResults.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-blue-800">
                      <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Timestamp */}
            {analysisResults.analysis_timestamp && (
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Clock className="w-4 h-4" />
                <span>
                  Analysis completed: {new Date(analysisResults.analysis_timestamp).toLocaleString()}
                </span>
              </div>
            )}

            {/* Analysis History */}
            {analysisHistory.length > 1 && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-semibold text-gray-700">Recent Analyses</span>
                  <button
                    onClick={loadAnalysisHistory}
                    className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Refresh
                  </button>
                </div>
                <div className="space-y-2">
                  {analysisHistory.slice(1, 4).map((analysis, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-gray-50 rounded-lg flex items-center justify-between cursor-pointer hover:bg-gray-100 transition-colors"
                      onClick={() => setAnalysisResults(analysis)}
                    >
                      <div>
                        <div className="text-sm font-medium text-gray-700">
                          {formatScore(analysis.quantum_health_score)} Health Score
                        </div>
                        <div className="text-xs text-gray-500">
                          {analysis.analysis_timestamp
                            ? new Date(analysis.analysis_timestamp).toLocaleString()
                            : 'Unknown date'}
                        </div>
                      </div>
                      <TrendingUp className="w-4 h-4 text-gray-400" />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <Atom className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No quantum analysis available</p>
            <button
              onClick={runQuantumAnalysis}
              disabled={isAnalyzing || !patientId}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isAnalyzing ? 'Analyzing...' : 'Run First Analysis'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuantumResults;



