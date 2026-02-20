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

const QuickActions = ({ onActionComplete }) => {
  const { selectedPatient, patientData } = usePatient();
  const { realtimeData } = useDashboard();
  const [activeAction, setActiveAction] = useState(null);
  const [showInterventionForm, setShowInterventionForm] = useState(false);

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
      id: 'ecdome_optimization',
      title: 'eCDome Optimization',
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
          toast.success('Message sent successfully');
          break;
        case 'schedule_call':
          toast.success('Call scheduled for tomorrow at 2:00 PM');
          break;
        case 'send_email':
          toast.success('Email notification sent');
          break;
        case 'emergency_alert':
          toast.error('Emergency alert triggered! Response team notified.');
          break;
        case 'intervention':
          setShowInterventionForm(true);
          break;
        case 'medication_adjust':
          toast.success('Medication adjustment logged');
          break;
        case 'schedule_appointment':
          toast.success('Appointment scheduled for next week');
          break;
        case 'increase_monitoring':
          toast.success('Monitoring frequency increased to every 5 minutes');
          break;
        case 'request_data':
          toast.success('Data request sent to patient');
          break;
        case 'set_alert':
          toast.success('Custom alert configured');
          break;
        case 'generate_report':
          toast.success('Report generated successfully');
          break;
        case 'update_notes':
          toast.success('Clinical notes updated');
          break;
        case 'export_data':
          toast.success('Data export initiated');
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

  return (
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
              <span className="text-blue-700">eCDome Score:</span>
              <span className="font-medium text-blue-900 ml-2">
                {patientData.ecdomeScore || 'N/A'}
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
  );
};

export default QuickActions; 