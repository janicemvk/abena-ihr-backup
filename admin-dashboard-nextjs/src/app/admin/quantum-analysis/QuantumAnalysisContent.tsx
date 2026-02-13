'use client'

import { useState, useEffect } from 'react'
import {
  CpuChipIcon,
  BoltIcon,
  ServerIcon,
  CubeIcon,
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ShieldCheckIcon,
  BeakerIcon,
  DocumentTextIcon,
  LinkIcon,
} from '@heroicons/react/24/outline'
import { quantumAnalysisService, QuantumAnalysisResult, QuantumSystemStatus } from '@/lib/services/quantumAnalysisService'

interface DataFlowStep {
  id: string
  name: string
  status: 'active' | 'complete' | 'pending'
  description: string
  icon: React.ComponentType<{ className?: string }>
  data?: any
}

export default function QuantumAnalysisContent() {
  const [analysisResult, setAnalysisResult] = useState<QuantumAnalysisResult | null>(null)
  const [systemStatus, setSystemStatus] = useState<QuantumSystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    loadData()
    
    if (autoRefresh) {
      const interval = setInterval(loadData, 30000) // Refresh every 30 seconds
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // First check if API is available
      const apiAvailable = await quantumAnalysisService.checkApiStatus()
      if (!apiAvailable) {
        setError('Quantum Analysis API is not running. Please start the API server on port 5000.')
        setSystemStatus({
          api_status: 'offline',
          blockchain_status: 'disconnected',
          analysis_engine: 'maintenance',
          last_analysis: null,
          total_analyses: 0,
          average_processing_time: 0,
        })
        setLoading(false)
        return
      }
      
      const [result, status] = await Promise.all([
        quantumAnalysisService.getDemoResults(),
        quantumAnalysisService.getSystemStatus(),
      ])
      
      setAnalysisResult(result)
      setSystemStatus(status)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load quantum analysis data'
      if (errorMessage.includes('fetch') || errorMessage.includes('network')) {
        setError('Cannot connect to Quantum Analysis API. Please ensure the API server is running on port 5000.')
      } else {
        setError(errorMessage)
      }
      console.error('Error loading quantum data:', err)
    } finally {
      setLoading(false)
    }
  }

  const getDataFlowSteps = (): DataFlowStep[] => {
    if (!analysisResult) return []
    
    return [
      {
        id: 'input',
        name: 'Data Input',
        status: 'complete',
        description: 'Patient data, biomarkers, symptoms, medications',
        icon: DocumentTextIcon,
        data: {
          patient_id: analysisResult.patient_id,
          biomarkers: analysisResult.biomarker_analysis?.length || 0,
          medications: analysisResult.interaction_analysis?.medications?.length || 0,
        },
      },
      {
        id: 'vqe',
        name: 'VQE Optimization',
        status: 'complete',
        description: 'Variational Quantum Eigensolver',
        icon: CpuChipIcon,
        data: {
          score: analysisResult.vqe_analysis.treatment_score,
          energy: analysisResult.vqe_analysis.final_energy,
        },
      },
      {
        id: 'pattern',
        name: 'Pattern Recognition',
        status: 'complete',
        description: 'Quantum Machine Learning',
        icon: BeakerIcon,
        data: {
          confidence: analysisResult.pattern_analysis.pattern_confidence,
          patterns: analysisResult.pattern_analysis.patterns_detected,
        },
      },
      {
        id: 'interaction',
        name: 'Drug Interaction',
        status: 'complete',
        description: 'QAOA Analysis',
        icon: ShieldCheckIcon,
        data: {
          safety_score: analysisResult.interaction_analysis?.safety_score || 0,
          level: analysisResult.interaction_analysis?.interaction_level || 'Unknown',
        },
      },
      {
        id: 'blockchain',
        name: 'Blockchain Storage',
        status: systemStatus?.blockchain_status === 'connected' ? 'complete' : 'pending',
        description: 'Quantum-secured record',
        icon: CubeIcon,
        data: {
          status: systemStatus?.blockchain_status,
        },
      },
    ]
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'connected':
      case 'operational':
      case 'complete':
        return 'text-green-600 bg-green-100'
      case 'offline':
      case 'disconnected':
      case 'maintenance':
      case 'pending':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-yellow-600 bg-yellow-100'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
      case 'connected':
      case 'operational':
      case 'complete':
        return CheckCircleIcon
      case 'offline':
      case 'disconnected':
      case 'maintenance':
      case 'pending':
        return XCircleIcon
      default:
        return ClockIcon
    }
  }

  if (loading && !analysisResult) {
    return (
      <div className="min-h-screen bg-clinical-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ecbome-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Quantum Analysis System...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-clinical-bg">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg">
                <CpuChipIcon className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight text-gray-900">
                  Quantum Analysis Command Center
                </h1>
                <p className="text-gray-600 mt-1">
                  Real-time monitoring of quantum healthcare analysis system
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="rounded border-gray-300 text-ecbome-primary focus:ring-ecbome-primary"
                />
                <span className="text-sm text-gray-600">Auto-refresh</span>
              </label>
              <button
                onClick={loadData}
                className="px-4 py-2 bg-ecbome-primary text-white rounded-lg hover:opacity-90 transition-opacity"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-6 bg-red-50 border-2 border-red-200 rounded-lg">
            <div className="flex items-start space-x-3">
              <XCircleIcon className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-red-900 mb-2">Connection Error</h3>
                <p className="text-red-800 mb-3">{error}</p>
                <div className="bg-white p-4 rounded border border-red-200">
                  <p className="text-sm font-semibold text-gray-900 mb-2">To start the Quantum API:</p>
                  <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
                    <li>Open a new terminal/PowerShell window</li>
                    <li>Navigate to: <code className="bg-gray-100 px-2 py-1 rounded">abena-quantum-healthcare</code></li>
                    <li>Run: <code className="bg-gray-100 px-2 py-1 rounded">python app.py</code></li>
                    <li>Wait for: <code className="bg-gray-100 px-2 py-1 rounded">Running on http://127.0.0.1:5000</code></li>
                    <li>Click Refresh button above</li>
                  </ol>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* System Status Cards */}
        {systemStatus && (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            <div className="dashboard-card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">API Status</p>
                  <div className="flex items-center space-x-2 mt-2">
                    {(() => {
                      const StatusIcon = getStatusIcon(systemStatus.api_status)
                      return (
                        <>
                          <StatusIcon className={`h-5 w-5 ${getStatusColor(systemStatus.api_status).split(' ')[0]}`} />
                          <span className={`text-sm font-medium ${getStatusColor(systemStatus.api_status).split(' ')[0]}`}>
                            {systemStatus.api_status.toUpperCase()}
                          </span>
                        </>
                      )
                    })()}
                  </div>
                </div>
                <ServerIcon className="h-8 w-8 text-gray-400" />
              </div>
            </div>

            <div className="dashboard-card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Blockchain</p>
                  <div className="flex items-center space-x-2 mt-2">
                    {(() => {
                      const StatusIcon = getStatusIcon(systemStatus.blockchain_status)
                      return (
                        <>
                          <StatusIcon className={`h-5 w-5 ${getStatusColor(systemStatus.blockchain_status).split(' ')[0]}`} />
                          <span className={`text-sm font-medium ${getStatusColor(systemStatus.blockchain_status).split(' ')[0]}`}>
                            {systemStatus.blockchain_status.toUpperCase()}
                          </span>
                        </>
                      )
                    })()}
                  </div>
                </div>
                <CubeIcon className="h-8 w-8 text-gray-400" />
              </div>
            </div>

            <div className="dashboard-card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Analysis Engine</p>
                  <div className="flex items-center space-x-2 mt-2">
                    {(() => {
                      const StatusIcon = getStatusIcon(systemStatus.analysis_engine)
                      return (
                        <>
                          <StatusIcon className={`h-5 w-5 ${getStatusColor(systemStatus.analysis_engine).split(' ')[0]}`} />
                          <span className={`text-sm font-medium ${getStatusColor(systemStatus.analysis_engine).split(' ')[0]}`}>
                            {systemStatus.analysis_engine.toUpperCase()}
                          </span>
                        </>
                      )
                    })()}
                  </div>
                </div>
                <BoltIcon className="h-8 w-8 text-gray-400" />
              </div>
            </div>

            <div className="dashboard-card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Analyses</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {systemStatus.total_analyses}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Avg: {systemStatus.average_processing_time}s
                  </p>
                </div>
                <ChartBarIcon className="h-8 w-8 text-gray-400" />
              </div>
            </div>
          </div>
        )}

        {/* Data Flow Visualization */}
        {analysisResult && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Data Flow Pipeline</h2>
            <div className="dashboard-card">
              <div className="flex items-center justify-between overflow-x-auto pb-4">
                {getDataFlowSteps().map((step, index) => {
                  const StepIcon = step.icon
                  const isLast = index === getDataFlowSteps().length - 1
                  return (
                    <div key={step.id} className="flex items-center flex-shrink-0">
                      <div className="flex flex-col items-center">
                        <div
                          className={`
                            p-4 rounded-lg border-2 transition-all
                            ${step.status === 'complete' 
                              ? 'bg-green-50 border-green-500' 
                              : step.status === 'active'
                              ? 'bg-blue-50 border-blue-500 animate-pulse'
                              : 'bg-gray-50 border-gray-300'
                            }
                          `}
                        >
                          <StepIcon
                            className={`
                              h-8 w-8
                              ${step.status === 'complete' 
                                ? 'text-green-600' 
                                : step.status === 'active'
                                ? 'text-blue-600'
                                : 'text-gray-400'
                              }
                            `}
                          />
                        </div>
                        <div className="mt-3 text-center">
                          <p className="text-sm font-semibold text-gray-900">{step.name}</p>
                          <p className="text-xs text-gray-500 mt-1">{step.description}</p>
                          {step.data && (
                            <div className="mt-2 text-xs text-gray-600">
                              {step.id === 'input' && (
                                <div>
                                  <p>Patient: {step.data.patient_id}</p>
                                  <p>{step.data.biomarkers} biomarkers</p>
                                </div>
                              )}
                              {step.id === 'vqe' && (
                                <div>
                                  <p>Score: {step.data.score}%</p>
                                  <p>Energy: {step.data.energy.toFixed(3)}</p>
                                </div>
                              )}
                              {step.id === 'pattern' && (
                                <div>
                                  <p>Confidence: {step.data.confidence}%</p>
                                  <p>{step.data.patterns} patterns</p>
                                </div>
                              )}
                              {step.id === 'interaction' && (
                                <div>
                                  <p>Safety: {step.data.safety_score}%</p>
                                  <p>Level: {step.data.level}</p>
                                </div>
                              )}
                              {step.id === 'blockchain' && (
                                <div>
                                  <p>Status: {step.data.status}</p>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                      {!isLast && (
                        <div className="mx-4 flex-shrink-0">
                          <LinkIcon className="h-6 w-6 text-gray-400" />
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {/* Analysis Results */}
        {analysisResult && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Overall Scores */}
            <div className="dashboard-card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Scores</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Overall Quantum Score</span>
                    <span className="text-sm font-bold text-ecbome-primary">
                      {analysisResult.scores.overall_score}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-indigo-600 h-3 rounded-full transition-all"
                      style={{ width: `${analysisResult.scores.overall_score}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Treatment Score</span>
                    <span className="text-sm font-bold text-green-600">
                      {analysisResult.scores.treatment_score}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-green-500 h-3 rounded-full transition-all"
                      style={{ width: `${analysisResult.scores.treatment_score}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Safety Score</span>
                    <span className="text-sm font-bold text-blue-600">
                      {analysisResult.scores.safety_score}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-500 h-3 rounded-full transition-all"
                      style={{ width: `${analysisResult.scores.safety_score}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Confidence Level</span>
                    <span className="text-sm font-bold text-yellow-600">
                      {analysisResult.scores.confidence_level}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-yellow-500 h-3 rounded-full transition-all"
                      style={{ width: `${analysisResult.scores.confidence_level}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* VQE Optimization Progress */}
            <div className="dashboard-card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">VQE Optimization Progress</h3>
              <div className="space-y-3">
                {analysisResult.vqe_analysis.optimization_progress.map((step, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className="w-16 text-xs text-gray-600">Step {step.step}</div>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-purple-500 to-indigo-600 h-2 rounded-full"
                        style={{ width: `${Math.abs(step.energy) * 50}%` }}
                      />
                    </div>
                    <div className="w-20 text-xs text-gray-600 text-right">
                      {step.energy.toFixed(3)}
                    </div>
                  </div>
                ))}
                <div className="mt-4 pt-4 border-t border-clinical-border">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">Final Energy</span>
                    <span className="text-lg font-bold text-ecbome-primary">
                      {analysisResult.vqe_analysis.final_energy.toFixed(3)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-sm font-medium text-gray-700">Protocol</span>
                    <span className="text-sm text-gray-600">
                      {analysisResult.vqe_analysis.protocol}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Detailed Analysis Sections */}
        {analysisResult && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Pattern Recognition */}
            <div className="dashboard-card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Pattern Recognition</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Detected Pattern</p>
                  <p className="text-base font-semibold text-gray-900 mt-1">
                    {analysisResult.pattern_analysis.detected_pattern}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Confidence</p>
                  <p className="text-2xl font-bold text-ecbome-primary mt-1">
                    {analysisResult.pattern_analysis.pattern_confidence}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Patterns Detected</p>
                  <p className="text-base font-semibold text-gray-900 mt-1">
                    {analysisResult.pattern_analysis.patterns_detected}
                  </p>
                </div>
                <div className="pt-3 border-t border-clinical-border">
                  <p className="text-xs text-gray-500">{analysisResult.pattern_analysis.tcm_recommendation}</p>
                  <p className="text-xs text-gray-500 mt-1">{analysisResult.pattern_analysis.ayurveda_correlation}</p>
                </div>
              </div>
            </div>

            {/* Drug Interaction */}
            {analysisResult.interaction_analysis && (
              <div className="dashboard-card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Drug Interaction Analysis</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600">Safety Score</p>
                    <p className="text-2xl font-bold text-blue-600 mt-1">
                      {analysisResult.interaction_analysis.safety_score}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Interaction Level</p>
                    <p className={`text-base font-semibold mt-1 ${
                      analysisResult.interaction_analysis.interaction_level === 'Low' 
                        ? 'text-green-600' 
                        : analysisResult.interaction_analysis.interaction_level === 'Moderate'
                        ? 'text-yellow-600'
                        : 'text-red-600'
                    }`}>
                      {analysisResult.interaction_analysis.interaction_level}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Molecular Energy</p>
                    <p className="text-base font-semibold text-gray-900 mt-1">
                      {analysisResult.interaction_analysis.molecular_interaction_energy}
                    </p>
                  </div>
                  <div className="pt-3 border-t border-clinical-border">
                    <p className="text-xs text-gray-500">{analysisResult.interaction_analysis.clinical_recommendation}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Recommendations */}
            <div className="dashboard-card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
              <div className="space-y-3">
                {analysisResult.recommendations.map((rec, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-start space-x-2">
                      <span className="text-xs font-bold text-ecbome-primary">#{rec.priority}</span>
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-gray-900">{rec.title}</p>
                        <p className="text-xs text-gray-600 mt-1">{rec.description}</p>
                        <span className={`inline-block mt-2 px-2 py-1 text-xs rounded ${
                          rec.status === 'proceed' 
                            ? 'bg-green-100 text-green-800'
                            : rec.status === 'caution'
                            ? 'bg-yellow-100 text-yellow-800'
                            : rec.status === 'required'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {rec.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Quantum Circuit Diagrams */}
        {analysisResult && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Quantum Circuit Diagrams</h2>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* VQE Circuit */}
              {analysisResult.vqe_analysis.circuit_diagram && (
                <div className="dashboard-card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">VQE Circuit</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Qubits:</span>
                      <span className="font-semibold">{analysisResult.vqe_analysis.circuit_diagram.qubits}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Depth:</span>
                      <span className="font-semibold">{analysisResult.vqe_analysis.circuit_diagram.depth}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Total Gates:</span>
                      <span className="font-semibold">{analysisResult.vqe_analysis.circuit_diagram.total_gates}</span>
                    </div>
                    {analysisResult.vqe_analysis.quantum_metrics && (
                      <div className="mt-3 pt-3 border-t border-clinical-border">
                        <p className="text-xs text-gray-600 mb-1">Quantum Metrics</p>
                        <p className="text-xs text-gray-700">Hardware Time: {analysisResult.vqe_analysis.quantum_metrics.estimated_hardware_time}</p>
                        <p className="text-xs text-gray-700">Classical Time: {analysisResult.vqe_analysis.quantum_metrics.classical_equivalent_time}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* QML Circuit */}
              {analysisResult.pattern_analysis.circuit_diagram && (
                <div className="dashboard-card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Pattern Recognition Circuit</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Qubits:</span>
                      <span className="font-semibold">{analysisResult.pattern_analysis.circuit_diagram.qubits}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Depth:</span>
                      <span className="font-semibold">{analysisResult.pattern_analysis.circuit_diagram.depth}</span>
                    </div>
                    {analysisResult.pattern_analysis.quantum_metrics && (
                      <div className="mt-3 pt-3 border-t border-clinical-border">
                        <p className="text-xs text-gray-600 mb-1">Quantum Advantage</p>
                        <p className="text-xs text-gray-700">Feature Space: {analysisResult.pattern_analysis.quantum_metrics.quantum_feature_map_dimension}x</p>
                        <p className="text-xs text-gray-700">Classical Advantage: {analysisResult.pattern_analysis.quantum_metrics.classical_advantage}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* QAOA Circuit */}
              {analysisResult.interaction_analysis?.circuit_diagram && (
                <div className="dashboard-card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">QAOA Drug Interaction Circuit</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Qubits:</span>
                      <span className="font-semibold">{analysisResult.interaction_analysis.circuit_diagram.qubits}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Layers:</span>
                      <span className="font-semibold">{analysisResult.interaction_analysis.circuit_diagram.layers || 'N/A'}</span>
                    </div>
                    {analysisResult.interaction_analysis.quantum_metrics && (
                      <div className="mt-3 pt-3 border-t border-clinical-border">
                        <p className="text-xs text-gray-600 mb-1">Complexity Comparison</p>
                        <p className="text-xs text-gray-700">Classical: {analysisResult.interaction_analysis.quantum_metrics.classical_complexity}</p>
                        <p className="text-xs text-gray-700">Quantum: {analysisResult.interaction_analysis.quantum_metrics.quantum_complexity}</p>
                        <p className="text-xs text-purple-600 font-semibold">Speedup: {analysisResult.interaction_analysis.quantum_metrics.speedup_estimate}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Enhanced Pattern Recognition */}
        {analysisResult && analysisResult.pattern_analysis.all_pattern_matches && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">TCM Pattern Matches</h2>
            <div className="dashboard-card">
              <div className="space-y-4">
                {analysisResult.pattern_analysis.all_pattern_matches.map((match, index) => (
                  <div key={index} className={`p-4 rounded-lg border-2 ${
                    index === 0 ? 'bg-purple-50 border-purple-300' : 'bg-gray-50 border-gray-200'
                  }`}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-semibold text-gray-900">{match.pattern_name}</h4>
                          {index === 0 && (
                            <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                              Best Match
                            </span>
                          )}
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                          <div>
                            <p className="text-gray-600">Confidence</p>
                            <p className="font-semibold text-gray-900">{match.combined_confidence}%</p>
                          </div>
                          <div>
                            <p className="text-gray-600">eCBome Correlation</p>
                            <p className="font-semibold text-gray-900">{match.ecbome_correlation}%</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Quantum Measurement</p>
                            <p className="font-semibold text-gray-900">{(match.quantum_measurement_probability * 100).toFixed(1)}%</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Formulas</p>
                            <p className="font-semibold text-gray-900">{match.herbal_formulas.length}</p>
                          </div>
                        </div>
                        {match.herbal_formulas.length > 0 && (
                          <div className="mt-3">
                            <p className="text-xs text-gray-600 mb-1">Recommended Formulas:</p>
                            <div className="flex flex-wrap gap-2">
                              {match.herbal_formulas.map((formula, idx) => (
                                <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                                  {formula}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Enhanced Drug Interactions */}
        {analysisResult && analysisResult.interaction_analysis?.interactions_detected && analysisResult.interaction_analysis.interactions_detected.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Drug Interaction Alerts</h2>
            <div className="dashboard-card">
              <div className="space-y-3">
                {analysisResult.interaction_analysis.interactions_detected.map((interaction, index) => (
                  <div key={index} className={`p-4 rounded-lg border-2 ${
                    interaction.severity === 'high' ? 'bg-red-50 border-red-300' :
                    interaction.severity === 'moderate' ? 'bg-yellow-50 border-yellow-300' :
                    'bg-gray-50 border-gray-200'
                  }`}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-semibold text-gray-900">
                            {interaction.medication} + {interaction.herb}
                          </h4>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            interaction.severity === 'high' ? 'bg-red-100 text-red-800' :
                            interaction.severity === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {interaction.severity.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mb-2">
                          <span className="font-medium">Type:</span> {interaction.type.replace('_', ' ').toUpperCase()}
                        </p>
                        <p className="text-sm text-gray-700">
                          <span className="font-medium">Recommendation:</span> {interaction.recommendation}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Blockchain Transaction */}
        {analysisResult && analysisResult.blockchain && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Blockchain Storage</h2>
            <div className="dashboard-card bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Transaction Hash</p>
                  <p className="text-xs font-mono text-gray-900 break-all">
                    {analysisResult.blockchain.transaction.transaction_hash}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Block Number</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {analysisResult.blockchain.transaction.block_number.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Quantum Proof</p>
                  <p className="text-sm font-semibold text-purple-600">
                    {analysisResult.blockchain.transaction.quantum_proof}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Post-Quantum Signature</p>
                  <p className="text-sm font-semibold text-blue-600">
                    {analysisResult.blockchain.transaction.post_quantum_signature}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Storage Method</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {analysisResult.blockchain.storage_method}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Access Control</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {analysisResult.blockchain.access_control}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Summary */}
        {analysisResult && (
          <div className="mt-8 dashboard-card bg-gradient-to-r from-purple-50 to-indigo-50 border-2 border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Analysis Summary</h3>
                <p className="text-gray-700">{analysisResult.summary.final_recommendation}</p>
                <div className="mt-4 flex items-center space-x-4">
                  <div>
                    <p className="text-xs text-gray-600">Integration Quality</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {analysisResult.summary.integration_quality}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Quantum Advantage</p>
                    <p className="text-sm font-semibold text-green-600">
                      {analysisResult.summary.quantum_advantage_status ? 'Active' : 'Inactive'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Hardware Ready</p>
                    <p className={`text-sm font-semibold ${
                      analysisResult.summary.hardware_ready ? 'text-green-600' : 'text-yellow-600'
                    }`}>
                      {analysisResult.summary.hardware_ready ? 'Yes' : 'Pending'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Mode</p>
                    <p className="text-sm font-semibold text-purple-600">
                      {analysisResult.summary.simulation_mode ? 'Simulation' : 'Hardware'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Ready for Deployment</p>
                    <p className={`text-sm font-semibold ${
                      analysisResult.summary.ready_for_deployment ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {analysisResult.summary.ready_for_deployment ? 'Yes' : 'No'}
                    </p>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-600">Last Analysis</p>
                <p className="text-sm font-semibold text-gray-900">
                  {new Date(analysisResult.analysis_timestamp).toLocaleString()}
                </p>
                {analysisResult.quantum_backend && (
                  <p className="text-xs text-gray-500 mt-1">
                    {analysisResult.quantum_backend}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
