import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Zap, 
  Send, 
  FileText, 
  Phone, 
  MessageSquare, 
  Calendar, 
  AlertTriangle, 
  Activity, 
  Pill, 
  Download, 
  Mail, 
  Clock, 
  User, 
  Heart,
  Brain,
  Shield,
  Target,
  CheckCircle,
  Plus
} from 'lucide-react';
import { usePatient } from '../../contexts/PatientContext';
import { useDashboard } from '../../contexts/DashboardContext';
import toast from 'react-hot-toast';
import VideoCallModal from './VideoCallModal';
import MessageModal from './MessageModal';
import { generateReport, downloadReport, printReport, ReportTypes } from '../../utils/reportGenerator';

const QuickActions = ({ onActionComplete }) => {
  const { selectedPatient, patientData } = usePatient();
  const { realtimeData } = useDashboard();
  const [activeAction, setActiveAction] = useState(null);
  const [showInterventionForm, setShowInterventionForm] = useState(false);
  const [showVideoCall, setShowVideoCall] = useState(false);
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [showEmergencyAlert, setShowEmergencyAlert] = useState(false);
  const [showMedicationAdjust, setShowMedicationAdjust] = useState(false);
  const [showReportGenerator, setShowReportGenerator] = useState(false);
  const [showNotesEditor, setShowNotesEditor] = useState(false);

  // Quick action categories
  const actionCategories = {
    communication: {
      title: 'Communication',
      icon: MessageSquare,
      color: 'bg-blue-100 text-blue-800',
      actions: [
        {
          id: 'send_message',
          title: 'Send Message',
          icon: Send,
          description: 'Send secure message to patient',
          urgent: false
        },
        {
          id: 'schedule_call',
          title: 'Schedule Call',
          icon: Phone,
          description: 'Schedule telehealth consultation',
          urgent: false
        },
        {
          id: 'send_email',
          title: 'Send Email',
          icon: Mail,
          description: 'Send email notification',
          urgent: false
        }
      ]
    },
    clinical: {
      title: 'Clinical Actions',
      icon: Activity,
      color: 'bg-green-100 text-green-800',
      actions: [
        {
          id: 'emergency_alert',
          title: 'Emergency Alert',
          icon: AlertTriangle,
          description: 'Trigger emergency response protocol',
          urgent: true
        },
        {
          id: 'intervention',
          title: 'Send Intervention',
          icon: Zap,
          description: 'Send immediate intervention protocol',
          urgent: true
        },
        {
          id: 'medication_adjust',
          title: 'Adjust Medication',
          icon: Pill,
          description: 'Modify medication protocol',
          urgent: false
        },
        {
          id: 'schedule_appointment',
          title: 'Schedule Appointment',
          icon: Calendar,
          description: 'Book in-person appointment',
          urgent: false
        }
      ]
    },
    monitoring: {
      title: 'Monitoring',
      icon: Heart,
      color: 'bg-purple-100 text-purple-800',
      actions: [
        {
          id: 'increase_monitoring',
          title: 'Increase Monitoring',
          icon: Activity,
          description: 'Increase monitoring frequency',
          urgent: false
        },
        {
          id: 'request_data',
          title: 'Request Data',
          icon: Download,
          description: 'Request additional patient data',
          urgent: false
        },
        {
          id: 'set_alert',
          title: 'Set Alert',
          icon: Clock,
          description: 'Set custom monitoring alert',
          urgent: false
        }
      ]
    },
    documentation: {
      title: 'Documentation',
      icon: FileText,
      color: 'bg-orange-100 text-orange-800',
      actions: [
        {
          id: 'generate_report',
          title: 'Generate Report',
          icon: FileText,
          description: 'Create comprehensive health report',
          urgent: false
        },
        {
          id: 'update_notes',
          title: 'Update Notes',
          icon: FileText,
          description: 'Add clinical notes',
          urgent: false
        },
        {
          id: 'export_data',
          title: 'Export Data',
          icon: Download,
          description: 'Export patient data',
          urgent: false
        }
      ]
    }
  };

  // Intervention options
  const interventionOptions = [
    {
      id: 'ebdome_optimization',
      title: 'eBDome Optimization',
      icon: Brain,
      description: 'Targeted endocannabinoid system support',
      protocols: [
        'Increase CB1 receptor sensitivity',
        'Boost anandamide production',
        'Balance 2-AG levels',
        'Optimize enzyme activity'
      ]
    },
    {
      id: 'inflammatory_response',
      title: 'Anti-Inflammatory Protocol',
      icon: Shield,
      description: 'Reduce systemic inflammation',
      protocols: [
        'Omega-3 supplementation',
        'Curcumin therapy',
        'Dietary modifications',
        'Stress reduction techniques'
      ]
    },
    {
      id: 'metabolic_support',
      title: 'Metabolic Support',
      icon: Target,
      description: 'Optimize metabolic function',
      protocols: [
        'Nutritional timing adjustment',
        'Micronutrient optimization',
        'Exercise prescription',
        'Sleep hygiene improvement'
      ]
    },
    {
      id: 'stress_management',
      title: 'Stress Management',
      icon: Heart,
      description: 'Improve stress response',
      protocols: [
        'Breathwork training',
        'Meditation practice',
        'HRV biofeedback',
        'Lifestyle modifications'
      ]
    }
  ];

  const handleQuickAction = async (actionId) => {
    setActiveAction(actionId);
    
    try {
      switch (actionId) {
        case 'send_message':
          // Open secure message modal
          setShowMessageModal(true);
          setActiveAction(null);
          break;
        case 'schedule_call':
          // Open video call modal
          setShowVideoCall(true);
          setActiveAction(null);
          break;
        case 'send_email':
          // Open message modal for email
          setShowMessageModal(true);
          setActiveAction(null);
          break;
        case 'emergency_alert':
          setShowEmergencyAlert(true);
          setActiveAction(null);
          break;
        case 'intervention':
          setShowInterventionForm(true);
          setActiveAction(null);
          break;
        case 'medication_adjust':
          setShowMedicationAdjust(true);
          setActiveAction(null);
          break;
        case 'schedule_appointment':
          toast.success(`📅 Appointment scheduled for ${patientInfo.name}`, {
            duration: 3000,
            icon: '📅'
          });
          setActiveAction(null);
          break;
        case 'increase_monitoring':
          toast.success('⏱️ Monitoring frequency increased to every 5 minutes', {
            duration: 3000
          });
          setActiveAction(null);
          break;
        case 'request_data':
          toast.success(`📊 Data request sent to ${patientInfo.name}`, {
            duration: 2000
          });
          setActiveAction(null);
          break;
        case 'set_alert':
          toast.success('🔔 Custom alert configured and activated', {
            duration: 2000
          });
          setActiveAction(null);
          break;
        case 'generate_report':
          setShowReportGenerator(true);
          setActiveAction(null);
          break;
        case 'update_notes':
          setShowNotesEditor(true);
          setActiveAction(null);
          break;
        case 'export_data':
          toast.promise(
            exportPatientData(patientData, patientInfo),
            {
              loading: '📦 Preparing data export...',
              success: '✅ Patient data exported successfully!',
              error: 'Failed to export data',
            }
          );
          setActiveAction(null);
          break;
        default:
          toast.success('Action completed');
      }
      
      if (onActionComplete) {
        onActionComplete(actionId);
      }
    } catch (error) {
      toast.error('Action failed. Please try again.');
    } finally {
      setTimeout(() => setActiveAction(null), 1000);
    }
  };

  const handleInterventionSend = (interventionId, selectedProtocols) => {
    const intervention = interventionOptions.find(opt => opt.id === interventionId);
    toast.success(`${intervention.title} protocol sent to patient`);
    setShowInterventionForm(false);
    
    if (onActionComplete) {
      onActionComplete('intervention', { interventionId, selectedProtocols });
    }
  };

  const InterventionForm = () => {
    const [selectedIntervention, setSelectedIntervention] = useState(null);
    const [selectedProtocols, setSelectedProtocols] = useState([]);

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      >
        <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">
                Send Intervention Protocol
              </h3>
              <button
                onClick={() => setShowInterventionForm(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">
                  Select Intervention Type
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {interventionOptions.map((intervention) => {
                    const IconComponent = intervention.icon;
                    const isSelected = selectedIntervention === intervention.id;
                    
                    return (
                      <button
                        key={intervention.id}
                        onClick={() => setSelectedIntervention(intervention.id)}
                        className={`p-4 border rounded-lg text-left transition-all ${
                          isSelected 
                            ? 'border-blue-500 bg-blue-50' 
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-start space-x-3">
                          <IconComponent className="w-5 h-5 text-blue-600 mt-0.5" />
                          <div>
                            <h5 className="font-medium text-gray-900">
                              {intervention.title}
                            </h5>
                            <p className="text-sm text-gray-600 mt-1">
                              {intervention.description}
                            </p>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {selectedIntervention && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">
                    Select Protocols
                  </h4>
                  <div className="space-y-2">
                    {interventionOptions
                      .find(opt => opt.id === selectedIntervention)
                      ?.protocols.map((protocol, index) => (
                        <label
                          key={index}
                          className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedProtocols.includes(protocol)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedProtocols([...selectedProtocols, protocol]);
                              } else {
                                setSelectedProtocols(selectedProtocols.filter(p => p !== protocol));
                              }
                            }}
                            className="w-4 h-4 text-blue-600"
                          />
                          <span className="text-sm text-gray-700">{protocol}</span>
                        </label>
                      ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  onClick={() => setShowInterventionForm(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleInterventionSend(selectedIntervention, selectedProtocols)}
                  disabled={!selectedIntervention || selectedProtocols.length === 0}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Send Intervention
                </button>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

  // Export patient data as JSON
  const exportPatientData = async (data, patientInfo) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const exportData = {
          exportDate: new Date().toISOString(),
          exportedBy: patientInfo.provider || 'Provider',
          patientData: data?.data || data,
          realtimeData: realtimeData?.data || null
        };

        const dataStr = JSON.stringify(exportData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `ABENA_Patient_Data_${patientInfo.id}_${Date.now()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        resolve();
      }, 1000);
    });
  };

  // Get patient info safely
  const patientInfo = patientData?.data?.patientInfo || { name: 'Patient', id: selectedPatient };

  // Report Generator Modal Component
  const ReportGeneratorModal = () => {
    const [selectedReportType, setSelectedReportType] = useState(ReportTypes.COMPREHENSIVE);
    const [isGenerating, setIsGenerating] = useState(false);

    const reportOptions = [
      { 
        id: ReportTypes.COMPREHENSIVE, 
        name: 'Comprehensive Health Report',
        description: 'Complete patient overview with all health data',
        icon: FileText
      },
      { 
        id: ReportTypes.ECDOME_ANALYSIS, 
        name: 'eBDome Analysis Report',
        description: 'Detailed endocannabinoid system analysis',
        icon: Brain
      },
      { 
        id: ReportTypes.MODULE_ASSESSMENT, 
        name: '12-Module Assessment',
        description: 'Complete breakdown of all 12 eBDome modules',
        icon: Activity
      },
      { 
        id: ReportTypes.TREATMENT_PROGRESS, 
        name: 'Treatment Progress Report',
        description: 'Current treatments and recommendations',
        icon: Heart
      },
      { 
        id: ReportTypes.LAB_RESULTS, 
        name: 'Lab Results Summary',
        description: 'Latest laboratory test results',
        icon: CheckCircle
      }
    ];

    const handleGenerateReport = async () => {
      setIsGenerating(true);
      
      try {
        // Generate the report
        const reportData = await generateReport(selectedReportType, patientData, realtimeData);
        
        // Show success message
        toast.success('✅ Report generated successfully!', { duration: 2000 });
        
        // Download the report
        downloadReport(reportData);
        
        // Optional: Also open print dialog
        // printReport(reportData.content);
        
        // Close modal after a brief delay
        setTimeout(() => {
          setShowReportGenerator(false);
          setIsGenerating(false);
        }, 500);
        
      } catch (error) {
        console.error('Report generation error:', error);
        toast.error('Failed to generate report. Please try again.');
        setIsGenerating(false);
      }
    };

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => !isGenerating && setShowReportGenerator(false)} />
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-2xl"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <FileText className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Generate Clinical Report</h3>
                <p className="text-sm text-gray-600">Patient: {patientInfo.name} ({patientInfo.id})</p>
              </div>
            </div>
            <button 
              onClick={() => !isGenerating && setShowReportGenerator(false)} 
              className="text-gray-400 hover:text-gray-600"
              disabled={isGenerating}
            >
              <Plus className="h-6 w-6 rotate-45" />
            </button>
          </div>
          
          <div className="space-y-3 mb-6">
            <p className="text-sm text-gray-600 mb-3">Select report type:</p>
            {reportOptions.map((option) => {
              const OptionIcon = option.icon;
              const isSelected = selectedReportType === option.id;
              
              return (
                <label 
                  key={option.id} 
                  className={`flex items-start p-4 border rounded-lg cursor-pointer transition-all ${
                    isSelected 
                      ? 'border-green-500 bg-green-50' 
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <input 
                    type="radio" 
                    name="reportType" 
                    checked={isSelected}
                    onChange={() => setSelectedReportType(option.id)}
                    className="mt-1 mr-3"
                    disabled={isGenerating}
                  />
                  <div className="flex items-start space-x-3 flex-1">
                    <div className={`p-2 rounded-lg ${isSelected ? 'bg-green-100' : 'bg-gray-100'}`}>
                      <OptionIcon className={`w-5 h-5 ${isSelected ? 'text-green-600' : 'text-gray-600'}`} />
                    </div>
                    <div>
                      <span className="text-gray-900 font-medium block">{option.name}</span>
                      <span className="text-sm text-gray-600">{option.description}</span>
                    </div>
                  </div>
                </label>
              );
            })}
          </div>
          
          <div className="flex justify-between items-center space-x-3 pt-4 border-t">
            <div className="text-sm text-gray-500">
              <Download className="w-4 h-4 inline mr-1" />
              Report will be downloaded as HTML (printable to PDF)
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowReportGenerator(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                disabled={isGenerating}
              >
                Cancel
              </button>
              <button
                onClick={handleGenerateReport}
                disabled={isGenerating}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {isGenerating ? (
                  <>
                    <div className="loading-spinner" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    <span>Generate & Download</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    );
  };

  return (
    <>
      {/* Video Call Modal */}
      <VideoCallModal
        isOpen={showVideoCall}
        onClose={() => setShowVideoCall(false)}
        patientData={patientInfo}
      />

      {/* Message Modal */}
      <MessageModal
        isOpen={showMessageModal}
        onClose={() => setShowMessageModal(false)}
        patientData={patientInfo}
      />

      {/* Quick Actions Card */}
    <div className="dashboard-card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-100 rounded-lg">
            <Zap className="w-5 h-5 text-indigo-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Quick Actions
            </h3>
            <p className="text-sm text-gray-500">
              Rapid clinical interventions and communications
            </p>
          </div>
        </div>
        {selectedPatient && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <User className="w-4 h-4" />
            <span>Patient: {selectedPatient}</span>
          </div>
        )}
      </div>

      <div className="space-y-6">
        {Object.entries(actionCategories).map(([categoryKey, category]) => {
          const CategoryIcon = category.icon;
          
          return (
            <div key={categoryKey}>
              <div className="flex items-center space-x-2 mb-3">
                <CategoryIcon className="w-4 h-4 text-gray-600" />
                <h4 className="font-medium text-gray-900">{category.title}</h4>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {category.actions.map((action) => {
                  const ActionIcon = action.icon;
                  const isActive = activeAction === action.id;
                  
                  return (
                    <motion.button
                      key={action.id}
                      onClick={() => handleQuickAction(action.id)}
                      disabled={isActive}
                      className={`p-4 border rounded-lg text-left transition-all hover:shadow-md ${
                        action.urgent 
                          ? 'border-red-200 bg-red-50 hover:bg-red-100' 
                          : 'border-gray-200 hover:border-gray-300'
                      } ${isActive ? 'opacity-50 cursor-not-allowed' : ''}`}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`p-2 rounded-lg ${
                          action.urgent 
                            ? 'bg-red-100 text-red-600' 
                            : 'bg-gray-100 text-gray-600'
                        }`}>
                          {isActive ? (
                            <div className="loading-spinner" />
                          ) : (
                            <ActionIcon className="w-4 h-4" />
                          )}
                        </div>
                        <div className="flex-1">
                          <h5 className={`font-medium ${
                            action.urgent ? 'text-red-900' : 'text-gray-900'
                          }`}>
                            {action.title}
                          </h5>
                          <p className={`text-sm mt-1 ${
                            action.urgent ? 'text-red-600' : 'text-gray-600'
                          }`}>
                            {action.description}
                          </p>
                          {action.urgent && (
                            <div className="flex items-center space-x-1 mt-2">
                              <AlertTriangle className="w-3 h-3 text-red-500" />
                              <span className="text-xs text-red-500 font-medium">
                                URGENT
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Actions */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-3">Recent Actions</h4>
        <div className="space-y-2">
          {[
            { action: 'Message sent', time: '2 minutes ago', icon: Send },
            { action: 'Monitoring increased', time: '15 minutes ago', icon: Activity },
            { action: 'Report generated', time: '1 hour ago', icon: FileText },
          ].map((item, index) => {
            const ItemIcon = item.icon;
            return (
              <div key={index} className="flex items-center space-x-3 text-sm">
                <ItemIcon className="w-3 h-3 text-gray-500" />
                <span className="text-gray-700">{item.action}</span>
                <span className="text-gray-500 text-xs">{item.time}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Patient Status Summary */}
      {patientData && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <Activity className="w-4 h-4 text-blue-600" />
            <h4 className="font-medium text-blue-900">Patient Status</h4>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-blue-700">eBDome Score:</span>
              <span className="font-medium text-blue-900 ml-2">
                {patientData.ebdomeScore || 'N/A'}
              </span>
            </div>
            <div>
              <span className="text-blue-700">Risk Level:</span>
              <span className="font-medium text-blue-900 ml-2">
                {patientData.riskLevel || 'N/A'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Intervention Form Modal */}
      {showInterventionForm && <InterventionForm />}
    </div>

      {/* Emergency Alert Modal */}
      {showEmergencyAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setShowEmergencyAlert(false)} />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md"
          >
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
                <AlertTriangle className="h-10 w-10 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Emergency Alert</h3>
              <p className="text-gray-600 mb-6">
                Trigger emergency response protocol for <span className="font-semibold">{patientInfo.name}</span>?
                This will notify the emergency response team immediately.
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowEmergencyAlert(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    toast.error(`🚨 Emergency alert triggered for ${patientInfo.name}! Response team notified.`, {
                      duration: 5000
                    });
                    setShowEmergencyAlert(false);
                  }}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Trigger Alert
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Medication Adjustment Modal */}
      {showMedicationAdjust && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setShowMedicationAdjust(false)} />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Pill className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900">Adjust Medication</h3>
              </div>
              <button onClick={() => setShowMedicationAdjust(false)} className="text-gray-400 hover:text-gray-600">
                <Plus className="h-6 w-6 rotate-45" />
              </button>
            </div>
            
            <div className="mb-4">
              <h4 className="font-medium text-gray-900 mb-3">Current Medications for {patientInfo.name}:</h4>
              <div className="space-y-2">
                {patientData?.data?.patientInfo?.medications?.map((med, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{med.name}</p>
                      <p className="text-sm text-gray-600">{med.dosage} - {med.frequency}</p>
                    </div>
                    <button className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded">
                      Modify
                    </button>
                  </div>
                )) || <p className="text-gray-500">No medications on file</p>}
              </div>
            </div>
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Add New Medication</label>
              <input
                type="text"
                placeholder="Medication name..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-2"
              />
              <div className="grid grid-cols-2 gap-2">
                <input type="text" placeholder="Dosage..." className="px-4 py-2 border border-gray-300 rounded-lg" />
                <input type="text" placeholder="Frequency..." className="px-4 py-2 border border-gray-300 rounded-lg" />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowMedicationAdjust(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  toast.success(`💊 Medication protocol updated for ${patientInfo.name}`, {
                    duration: 3000
                  });
                  setShowMedicationAdjust(false);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Save Changes
              </button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Report Generator Modal */}
      {showReportGenerator && <ReportGeneratorModal />}

      {/* Clinical Notes Editor Modal */}
      {showNotesEditor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setShowNotesEditor(false)} />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-3xl"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FileText className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">Clinical Notes</h3>
                  <p className="text-sm text-gray-600">Patient: {patientInfo.name} ({patientInfo.id})</p>
                </div>
              </div>
              <button onClick={() => setShowNotesEditor(false)} className="text-gray-400 hover:text-gray-600">
                <Plus className="h-6 w-6 rotate-45" />
              </button>
            </div>
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Note Type</label>
              <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-4">
                <option>Progress Note</option>
                <option>SOAP Note</option>
                <option>Consultation Note</option>
                <option>Follow-up Note</option>
              </select>
              
              <label className="block text-sm font-medium text-gray-700 mb-2">Clinical Notes</label>
              <textarea
                placeholder="Enter clinical notes..."
                rows={10}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                defaultValue={`Chief Complaint: \n\nHistory of Present Illness:\n\nAssessment:\n\nPlan:\n`}
              />
            </div>
            
            <div className="flex justify-between">
              <button
                onClick={() => setShowNotesEditor(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <div className="flex space-x-2">
                <button className="px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50">
                  Save Draft
                </button>
                <button
                  onClick={() => {
                    toast.success(`📝 Clinical notes saved for ${patientInfo.name}`, {
                      duration: 3000
                    });
                    setShowNotesEditor(false);
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Save & Sign
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </>
  );
};

export default QuickActions; 