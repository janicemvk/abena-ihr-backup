import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
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
  AlertCircle
} from 'lucide-react';
import { usePatient } from '../../contexts/PatientContext';
import { useDashboard } from '../../contexts/DashboardContext';

const PredictiveAlerts = ({ alerts = [], onAlertAction }) => {
  const { selectedPatient } = usePatient();
  const { actions: dashboardActions } = useDashboard();
  const [expandedAlert, setExpandedAlert] = useState(null);
  const [dismissedAlerts, setDismissedAlerts] = useState(new Set());

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

  // Mock alerts if none provided
  const mockAlerts = [
    {
      id: 'alert-001',
      type: 'ecdome_imbalance',
      severity: 'warning',
      title: 'eCDome System Imbalance Detected',
      message: 'CB1 receptor activity is 15% below optimal range. Anandamide levels showing declining trend.',
      timestamp: new Date(Date.now() - 30 * 60 * 1000),
      module: 'eCDome',
      probability: 0.87,
      recommendation: 'Consider lifestyle intervention or supplement protocol.',
      trend: 'declining',
      affectedSystems: ['Neurological', 'Stress Response']
    },
    {
      id: 'alert-002',
      type: 'inflammatory_spike',
      severity: 'critical',
      title: 'Inflammatory Cascade Predicted',
      message: 'Machine learning model predicts 73% probability of inflammatory response within 2-4 hours.',
      timestamp: new Date(Date.now() - 15 * 60 * 1000),
      module: 'Inflammatome',
      probability: 0.73,
      recommendation: 'Immediate intervention recommended. Consider anti-inflammatory protocol.',
      trend: 'increasing',
      affectedSystems: ['Immune System', 'Cardiovascular']
    },
    {
      id: 'alert-003',
      type: 'metabolic_optimization',
      severity: 'info',
      title: 'Metabolic Enhancement Opportunity',
      message: 'Current metabolic state shows potential for 12% efficiency improvement.',
      timestamp: new Date(Date.now() - 45 * 60 * 1000),
      module: 'Metabolome',
      probability: 0.65,
      recommendation: 'Optimize nutrition timing and composition.',
      trend: 'stable',
      affectedSystems: ['Metabolic', 'Nutriome']
    },
    {
      id: 'alert-004',
      type: 'circadian_disruption',
      severity: 'warning',
      title: 'Circadian Rhythm Disruption Risk',
      message: 'Sleep pattern analysis indicates 68% risk of circadian misalignment.',
      timestamp: new Date(Date.now() - 60 * 60 * 1000),
      module: 'Chronobiome',
      probability: 0.68,
      recommendation: 'Adjust light exposure and sleep schedule.',
      trend: 'increasing',
      affectedSystems: ['Chronobiome', 'Hormonal']
    }
  ];

  const displayAlerts = alerts.length > 0 ? alerts : mockAlerts;
  const activeAlerts = displayAlerts.filter(alert => !dismissedAlerts.has(alert.id));

  const handleAlertAction = (alertId, action) => {
    if (action === 'dismiss') {
      setDismissedAlerts(prev => new Set([...prev, alertId]));
    } else if (action === 'acknowledge') {
      dashboardActions.removeAlert(alertId);
    }
    
    if (onAlertAction) {
      onAlertAction(alertId, action);
    }
  };

  const formatTimestamp = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    
    if (minutes < 60) {
      return `${minutes} minutes ago`;
    } else if (hours < 24) {
      return `${hours} hours ago`;
    } else {
      return timestamp.toLocaleDateString();
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
            <h3 className="text-lg font-semibold text-gray-900">
              Predictive Alerts
            </h3>
            <p className="text-sm text-gray-500">
              AI-powered health predictions based on eCDome analysis
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
            const config = severityConfig[alert.severity];
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
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                          {alert.module}
                        </span>
                        <span className="text-xs text-gray-500">
                          {Math.round(alert.probability * 100)}% confidence
                        </span>
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
                            handleAlertAction(alert.id, 'acknowledge');
                          }}
                          className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors"
                        >
                          Acknowledge
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAlertAction(alert.id, 'view_details');
                          }}
                          className="px-3 py-1 border border-gray-300 text-xs rounded hover:bg-gray-50 transition-colors"
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
            Alerts are generated using AI analysis of eCDome patterns and 12 ABENA modules.
            <br />
            Predictions are based on current patient data and historical patterns.
          </p>
        </div>
      )}
    </div>
  );
};

export default PredictiveAlerts; 