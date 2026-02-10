import React from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  Calendar, 
  Activity, 
  Heart, 
  TrendingUp, 
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  Phone,
  Mail
} from 'lucide-react';

const PatientOverview = ({ patientData, realtimeData }) => {
  if (!patientData) return null;

  const { patientInfo, ecdomeProfile } = patientData;

  const getHealthScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getHealthScoreIcon = (score) => {
    if (score >= 0.8) return <CheckCircle className="h-5 w-5 text-green-600" />;
    if (score >= 0.6) return <Clock className="h-5 w-5 text-yellow-600" />;
    return <AlertTriangle className="h-5 w-5 text-red-600" />;
  };

  const getHealthScoreText = (score) => {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    return 'Needs Attention';
  };

  const vitalCards = [
    {
      label: 'Heart Rate',
      value: realtimeData?.heartRate ? `${Math.round(realtimeData.heartRate)} bpm` : '-- bpm',
      icon: <Heart className="h-5 w-5 text-red-500" />,
      trend: realtimeData?.heartRate > 75 ? 'up' : 'stable'
    },
    {
      label: 'Blood Pressure',
      value: realtimeData?.bloodPressure ? 
        `${Math.round(realtimeData.bloodPressure.systolic)}/${Math.round(realtimeData.bloodPressure.diastolic)}` : 
        '-- / --',
      icon: <Activity className="h-5 w-5 text-blue-500" />,
      trend: 'stable'
    },
    {
      label: 'eCDome Activity',
      value: realtimeData?.ecdomeActivity ? 
        `${Math.round(realtimeData.ecdomeActivity * 100)}%` : 
        '--%',
      icon: <Activity className="h-5 w-5 text-purple-500" />,
      trend: realtimeData?.ecdomeActivity > 0.8 ? 'up' : 'stable'
    }
  ];

  const getTrendIcon = (trend) => {
    if (trend === 'up') return <TrendingUp className="h-4 w-4 text-green-500" />;
    if (trend === 'down') return <TrendingDown className="h-4 w-4 text-red-500" />;
    return <div className="h-4 w-4 bg-gray-400 rounded-full"></div>;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="dashboard-card"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Patient Info */}
        <div className="lg:col-span-4">
          <div className="flex items-start space-x-4">
            <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <User className="h-8 w-8 text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900">
                {patientInfo.name}
              </h2>
              <div className="space-y-1 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <span>ID: {patientInfo.id}</span>
                  <span>•</span>
                  <span>Age: {patientInfo.age}</span>
                  <span>•</span>
                  <span>{patientInfo.gender}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Calendar className="h-4 w-4" />
                  <span>Last Visit: {patientInfo.lastVisit}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4" />
                  <span>Provider: {patientInfo.provider}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* eCDome Health Score */}
        <div className="lg:col-span-3">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              {getHealthScoreIcon(ecdomeProfile.overallScore)}
              <span className="text-sm font-medium text-gray-700">eCDome Health Score</span>
            </div>
            <div className="relative">
              <div className="text-4xl font-bold text-gray-900">
                {Math.round(ecdomeProfile.overallScore * 100)}%
              </div>
              <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium mt-2 ${getHealthScoreColor(ecdomeProfile.overallScore)}`}>
                {getHealthScoreText(ecdomeProfile.overallScore)}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="lg:col-span-2">
          <div className="space-y-2">
            <button className="w-full flex items-center justify-center space-x-2 px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
              <Phone className="h-4 w-4" />
              <span>Call Patient</span>
            </button>
            <button className="w-full flex items-center justify-center space-x-2 px-3 py-2 text-sm font-medium text-green-600 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
              <Mail className="h-4 w-4" />
              <span>Send Message</span>
            </button>
          </div>
        </div>

        {/* Real-time Vitals */}
        <div className="lg:col-span-3">
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-gray-700">Real-time Vitals</h3>
            {vitalCards.map((vital, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  {vital.icon}
                  <div>
                    <div className="text-sm font-medium text-gray-900">{vital.value}</div>
                    <div className="text-xs text-gray-600">{vital.label}</div>
                  </div>
                </div>
                {getTrendIcon(vital.trend)}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Status Bar */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Live Monitoring Active</span>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4" />
              <span>
                Last Update: {realtimeData?.timestamp ? 
                  new Date(realtimeData.timestamp).toLocaleTimeString() : 
                  'Loading...'
                }
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span>Connection: Strong</span>
            <span>Data Quality: 99.2%</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default PatientOverview; 