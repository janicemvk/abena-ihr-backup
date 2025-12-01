import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown, 
  Brain, 
  Heart, 
  Activity, 
  Clock, 
  ChevronRight, 
  X, 
  CheckCircle, 
  Bell,
  Info,
  AlertCircle,
  FileText,
  User,
  Calendar,
  Target
} from 'lucide-react';
import { usePatient } from '../../contexts/PatientContext';
import { useDashboard } from '../../contexts/DashboardContext';
import toast from 'react-hot-toast';
import HelpInfo from '../Common/HelpInfo';

const PredictiveAlerts = ({ alerts = [], onAlertAction }) => {
  const { selectedPatient, patientData } = usePatient();
  const { actions: dashboardActions } = useDashboard();
  const [expandedAlert, setExpandedAlert] = useState(null);
  const [dismissedAlerts, setDismissedAlerts] = useState(new Set());
  const [acknowledgedAlerts, setAcknowledgedAlerts] = useState(new Set());
  const [showDetailModal, setShowDetailModal] = useState(null);
  const [patientAlerts, setPatientAlerts] = useState([]);

  // Alert severity levels
  const severityConfig = {
    critical: {
      color: 'border-red-500 bg-red-50',
      textColor: 'text-red-700',
      icon: AlertTriangle,
      iconColor: 'text-red-600'
    },
    warning: {
      color: 'border-yellow-500 bg-yellow-50',
      textColor: 'text-yellow-700',
      icon: AlertCircle,
      iconColor: 'text-yellow-600'
    },
    info: {
      color: 'border-blue-500 bg-blue-50',
      textColor: 'text-blue-700',
      icon: Info,
      iconColor: 'text-blue-600'
    },
    success: {
      color: 'border-green-500 bg-green-50',
      textColor: 'text-green-700',
      icon: CheckCircle,
      iconColor: 'text-green-600'
    }
  };

  // Load patient-specific alerts
  useEffect(() => {
    if (patientData && patientData.data && patientData.data.alerts) {
      // Transform alerts from patient data to match expected format
      const transformedAlerts = patientData.data.alerts.map(alert => {
        // Ensure timestamp is a valid Date object
        let alertTimestamp;
        if (alert.timestamp instanceof Date) {
          alertTimestamp = alert.timestamp;
        } else if (alert.timestamp) {
          alertTimestamp = new Date(alert.timestamp);
        } else {
          alertTimestamp = new Date();
        }
        
        // Validate the date
        if (isNaN(alertTimestamp.getTime())) {
          alertTimestamp = new Date();
        }
        
        return {
          ...alert,
          severity: alert.severity || alert.type || 'info', // Ensure severity is set
          probability: alert.probability || 0.85, // Default confidence level
          trend: alert.trend || 'stable',
          module: alert.module || 'General',
          affectedSystems: alert.recommendations || alert.affectedSystems || [],
          timestamp: alertTimestamp
        };
      });
      setPatientAlerts(transformedAlerts);
      console.log(`✅ Loaded ${transformedAlerts.length} alerts for patient ${selectedPatient}`);
    } else {
      setPatientAlerts([]);
    }
  }, [patientData, selectedPatient]);

  const displayAlerts = patientAlerts.length > 0 ? patientAlerts : alerts;
  const activeAlerts = displayAlerts.filter(alert => 
    !dismissedAlerts.has(alert.id) && !acknowledgedAlerts.has(alert.id)
  );

  const handleAlertAction = (alertId, action, alertTitle) => {
    if (action === 'dismiss') {
      setDismissedAlerts(prev => new Set([...prev, alertId]));
      toast.success(`Alert dismissed`, {
        icon: '✓'
      });
    } else if (action === 'acknowledge') {
      setAcknowledgedAlerts(prev => new Set([...prev, alertId]));
      toast.success(`Alert acknowledged and marked as reviewed`, {
        icon: '✅',
        duration: 3000
      });
      // Optional: Log to patient chart
      console.log(`Alert ${alertId} acknowledged by provider at ${new Date().toISOString()}`);
    } else if (action === 'view_details') {
      const alert = displayAlerts.find(a => a.id === alertId);
      setShowDetailModal(alert);
    }
    
    if (onAlertAction) {
      onAlertAction(alertId, action);
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    // Convert to Date object if it's a string
    const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
    
    // Check if valid date
    if (isNaN(date.getTime())) {
      return 'Invalid date';
    }
    
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    
    if (minutes < 60) {
      return `${minutes} minutes ago`;
    } else if (hours < 24) {
      return `${hours} hours ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing':
        return TrendingUp;
      case 'declining':
        return TrendingDown;
      default:
        return Activity;
    }
  };

  return (
    <div className="dashboard-card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-orange-100 rounded-lg">
            <Bell className="w-5 h-5 text-orange-600" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900">
                Predictive Alerts
              </h3>
              <HelpInfo topic="predictive_alerts" size="sm" position="modal" />
            </div>
            <p className="text-sm text-gray-500">
              AI-powered health predictions based on eBDome analysis
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-600">
            {activeAlerts.length} active
          </span>
          <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
        </div>
      </div>

      <div className="space-y-4">
        {activeAlerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-500" />
            <p>No active alerts. All systems optimal.</p>
          </div>
        ) : (
          activeAlerts.map((alert) => {
            const config = severityConfig[alert.severity] || severityConfig.info;
            const IconComponent = config.icon;
            const TrendIcon = getTrendIcon(alert.trend);
            const isExpanded = expandedAlert === alert.id;

            return (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={`border-l-4 ${config.color} rounded-lg p-4 cursor-pointer transition-all hover:shadow-md`}
                onClick={() => setExpandedAlert(isExpanded ? null : alert.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <IconComponent className={`w-5 h-5 ${config.iconColor} mt-0.5`} />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className={`font-medium ${config.textColor}`}>
                          {alert.title}
                        </h4>
                        {alert.module && (
                          <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                            {alert.module}
                          </span>
                        )}
                        {alert.probability && (
                          <span className="text-xs text-gray-500">
                            {Math.round(alert.probability * 100)}% confidence
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-2">
                        {alert.message}
                      </p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>{formatTimestamp(alert.timestamp)}</span>
                        </span>
                        <span className="flex items-center space-x-1">
                          <TrendIcon className="w-3 h-3" />
                          <span>{alert.trend}</span>
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAlertAction(alert.id, 'dismiss');
                      }}
                      className="p-1 hover:bg-gray-100 rounded transition-colors"
                    >
                      <X className="w-4 h-4 text-gray-400" />
                    </button>
                    <ChevronRight 
                      className={`w-4 h-4 text-gray-400 transition-transform ${
                        isExpanded ? 'rotate-90' : ''
                      }`}
                    />
                  </div>
                </div>

                {isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-4 pt-4 border-t border-gray-200"
                  >
                    <div className="space-y-3">
                      <div>
                        <h5 className="font-medium text-gray-900 mb-1">
                          Clinical Recommendation
                        </h5>
                        <p className="text-sm text-gray-600">
                          {alert.recommendation}
                        </p>
                      </div>
                      
                      <div>
                        <h5 className="font-medium text-gray-900 mb-1">
                          Affected Systems
                        </h5>
                        <div className="flex flex-wrap gap-2">
                          {alert.affectedSystems.map((system, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-gray-100 text-xs rounded"
                            >
                              {system}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="flex space-x-2 pt-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAlertAction(alert.id, 'acknowledge', alert.title);
                          }}
                          className={`px-4 py-2 text-sm rounded font-medium transition-colors ${
                            acknowledgedAlerts.has(alert.id)
                              ? 'bg-green-100 text-green-700 cursor-not-allowed'
                              : 'bg-blue-600 text-white hover:bg-blue-700'
                          }`}
                          disabled={acknowledgedAlerts.has(alert.id)}
                        >
                          {acknowledgedAlerts.has(alert.id) ? '✓ Acknowledged' : 'Acknowledge'}
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAlertAction(alert.id, 'view_details', alert.title);
                          }}
                          className="px-4 py-2 border border-gray-300 text-sm rounded hover:bg-gray-50 transition-colors font-medium"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            );
          })
        )}
      </div>

      {activeAlerts.length > 0 && (
        <div className="mt-6 p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-600 text-center">
            Alerts are generated using AI analysis of eBDome patterns and 12 ABENA modules.
            <br />
            Predictions are based on current patient data and historical patterns.
          </p>
        </div>
      )}

      {/* Alert Detail Modal */}
      <AnimatePresence>
        {showDetailModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black bg-opacity-50"
              onClick={() => setShowDetailModal(null)}
            />

            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col"
            >
              {/* Header */}
              <div className={`px-6 py-4 border-l-4 ${(severityConfig[showDetailModal.severity] || severityConfig.info).color}`}>
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    {React.createElement((severityConfig[showDetailModal.severity] || severityConfig.info).icon, {
                      className: `w-8 h-8 ${(severityConfig[showDetailModal.severity] || severityConfig.info).iconColor}`
                    })}
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 mb-1">
                        {showDetailModal.title}
                      </h3>
                      <div className="flex items-center space-x-3 text-sm text-gray-600">
                        <span className="flex items-center space-x-1">
                          <User className="w-4 h-4" />
                          <span>{patientData?.data?.patientInfo?.name}</span>
                        </span>
                        <span>•</span>
                        <span className="flex items-center space-x-1">
                          <Calendar className="w-4 h-4" />
                          <span>{formatTimestamp(showDetailModal.timestamp)}</span>
                        </span>
                        <span>•</span>
                        <span className="uppercase font-medium text-orange-600">
                          {showDetailModal.type || showDetailModal.severity}
                        </span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowDetailModal(null)}
                    className="text-gray-400 hover:text-gray-600 rounded-full p-2 hover:bg-gray-100"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
                {/* Alert Description */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                    <Info className="w-5 h-5 text-blue-600" />
                    <span>Alert Description</span>
                  </h4>
                  <p className="text-gray-700 leading-relaxed">
                    {showDetailModal.message}
                  </p>
                </div>

                {/* Clinical Recommendation */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                    <Target className="w-5 h-5 text-green-600" />
                    <span>Clinical Recommendation</span>
                  </h4>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-gray-700">
                      {showDetailModal.recommendation || 'No specific recommendation available.'}
                    </p>
                    {showDetailModal.recommendations && showDetailModal.recommendations.length > 0 && (
                      <ul className="mt-3 space-y-2">
                        {showDetailModal.recommendations.map((rec, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <CheckCircle className="w-4 h-4 text-green-600 mt-0.5" />
                            <span className="text-sm text-gray-700">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>

                {/* Affected Systems */}
                {showDetailModal.affectedSystems && showDetailModal.affectedSystems.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Affected Systems</h4>
                    <div className="flex flex-wrap gap-2">
                      {showDetailModal.affectedSystems.map((system, index) => (
                        <span
                          key={index}
                          className="px-3 py-1.5 bg-gray-100 text-gray-700 text-sm rounded-lg font-medium"
                        >
                          {system}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Severity & Confidence */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h5 className="text-sm font-medium text-gray-600 mb-1">Severity Level</h5>
                    <p className={`text-2xl font-bold ${(severityConfig[showDetailModal.severity] || severityConfig.info).textColor}`}>
                      {showDetailModal.severity?.toUpperCase() || 'INFO'}
                    </p>
                  </div>
                  {showDetailModal.probability && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h5 className="text-sm font-medium text-gray-600 mb-1">Confidence Level</h5>
                      <p className="text-2xl font-bold text-blue-600">
                        {Math.round(showDetailModal.probability * 100)}%
                      </p>
                    </div>
                  )}
                </div>

                {/* Patient Context */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Patient Context</h4>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Patient:</span>
                      <span className="font-medium text-gray-900">
                        {patientData?.data?.patientInfo?.name} ({patientData?.data?.patientInfo?.id})
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Age / Gender:</span>
                      <span className="font-medium text-gray-900">
                        {patientData?.data?.patientInfo?.age}y / {patientData?.data?.patientInfo?.gender}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">eBDome Score:</span>
                      <span className="font-medium text-gray-900">
                        {Math.round((patientData?.data?.ebdomeProfile?.score || 0) * 100)}%
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Risk Level:</span>
                      <span className={`font-medium ${
                        patientData?.data?.patientInfo?.riskLevel === 'high' ? 'text-red-600' :
                        patientData?.data?.patientInfo?.riskLevel === 'medium' ? 'text-yellow-600' :
                        'text-green-600'
                      }`}>
                        {patientData?.data?.patientInfo?.riskLevel?.toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Alert Metadata */}
                <div className="border-t pt-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Alert ID:</span>
                      <span className="ml-2 font-mono text-gray-900">{showDetailModal.id}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Generated:</span>
                      <span className="ml-2 text-gray-900">
                        {new Date(showDetailModal.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Module:</span>
                      <span className="ml-2 font-medium text-gray-900">{showDetailModal.module || 'General'}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Trend:</span>
                      <span className="ml-2 text-gray-900 capitalize">{showDetailModal.trend || 'Stable'}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Footer Actions */}
              <div className="border-t px-6 py-4 bg-gray-50 flex justify-between items-center">
                <button
                  onClick={() => setShowDetailModal(null)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-200 rounded transition-colors"
                >
                  Close
                </button>
                <div className="flex space-x-3">
                  <button
                    onClick={() => {
                      handleAlertAction(showDetailModal.id, 'acknowledge', showDetailModal.title);
                      setShowDetailModal(null);
                    }}
                    className={`px-6 py-2 rounded font-medium transition-colors ${
                      acknowledgedAlerts.has(showDetailModal.id)
                        ? 'bg-green-100 text-green-700 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                    disabled={acknowledgedAlerts.has(showDetailModal.id)}
                  >
                    {acknowledgedAlerts.has(showDetailModal.id) ? '✓ Acknowledged' : 'Acknowledge & Close'}
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default PredictiveAlerts; 