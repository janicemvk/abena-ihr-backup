import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Heart, Activity, Thermometer, Droplets, Brain, Eye, AlertCircle } from 'lucide-react';

const RealtimeMonitoring = ({ realtimeData, patientData }) => {
  const [connectionStatus, setConnectionStatus] = useState('connected');
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    setLastUpdate(new Date());
  }, [realtimeData]);

  const vitals = [
    {
      name: 'Heart Rate',
      value: realtimeData?.heartRate ? `${Math.round(realtimeData.heartRate)}` : '--',
      unit: 'bpm',
      icon: Heart,
      color: 'text-red-500',
      bgColor: 'bg-red-50',
      normal: [60, 100],
      current: realtimeData?.heartRate
    },
    {
      name: 'Blood Pressure',
      value: realtimeData?.bloodPressure ? 
        `${Math.round(realtimeData.bloodPressure.systolic)}/${Math.round(realtimeData.bloodPressure.diastolic)}` : 
        '--/--',
      unit: 'mmHg',
      icon: Activity,
      color: 'text-blue-500',
      bgColor: 'bg-blue-50',
      normal: [120, 80],
      current: realtimeData?.bloodPressure?.systolic
    },
    {
      name: 'Temperature',
      value: realtimeData?.temperature ? `${realtimeData.temperature.toFixed(1)}` : '--',
      unit: '°F',
      icon: Thermometer,
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-50',
      normal: [97.0, 99.5],
      current: realtimeData?.temperature
    },
    {
      name: 'eCDome Activity',
      value: realtimeData?.ecdomeActivity ? `${Math.round(realtimeData.ecdomeActivity * 100)}` : '--',
      unit: '%',
      icon: Brain,
      color: 'text-purple-500',
      bgColor: 'bg-purple-50',
      normal: [70, 90],
      current: realtimeData?.ecdomeActivity * 100
    }
  ];

  const getStatusColor = (current, normal) => {
    if (!current || !normal) return 'text-gray-500';
    
    const [min, max] = normal;
    if (current >= min && current <= max) return 'text-green-600';
    if (current < min * 0.9 || current > max * 1.1) return 'text-red-600';
    return 'text-yellow-600';
  };

  const getStatusText = (current, normal) => {
    if (!current || !normal) return 'No Data';
    
    const [min, max] = normal;
    if (current >= min && current <= max) return 'Normal';
    if (current < min * 0.9 || current > max * 1.1) return 'Critical';
    return 'Caution';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="dashboard-card"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-br from-green-500 to-blue-600 rounded-lg">
            <Eye className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Real-time Monitoring</h3>
            <p className="text-sm text-gray-600">ABENA SDK Live Patient Data</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`h-2 w-2 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' :
            connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' :
            'bg-red-500'
          }`}></div>
          <span className="text-sm text-gray-600 capitalize">{connectionStatus}</span>
        </div>
      </div>

      {/* Vital Signs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {vitals.map((vital, index) => {
          const Icon = vital.icon;
          const statusColor = getStatusColor(vital.current, vital.normal);
          const statusText = getStatusText(vital.current, vital.normal);
          
          return (
            <motion.div
              key={vital.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg border-2 ${
                statusColor === 'text-red-600' ? 'border-red-200 bg-red-50' :
                statusColor === 'text-yellow-600' ? 'border-yellow-200 bg-yellow-50' :
                'border-green-200 bg-green-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${vital.bgColor}`}>
                    <Icon className={`h-5 w-5 ${vital.color}`} />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{vital.name}</h4>
                    <p className="text-sm text-gray-600">{statusText}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-2xl font-bold ${statusColor}`}>
                    {vital.value}
                  </div>
                  <div className="text-sm text-gray-500">{vital.unit}</div>
                </div>
              </div>
              
              {/* Normal Range Indicator */}
              {vital.normal && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="flex justify-between text-xs text-gray-600">
                    <span>Normal Range</span>
                    <span>{vital.normal[0]} - {vital.normal[1]} {vital.unit}</span>
                  </div>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-xl font-bold text-blue-600">
            {realtimeData?.oxygenSaturation ? `${Math.round(realtimeData.oxygenSaturation)}` : '--'}%
          </div>
          <div className="text-sm text-gray-600">O2 Saturation</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-xl font-bold text-green-600">
            {realtimeData?.respirationRate ? `${Math.round(realtimeData.respirationRate)}` : '--'}
          </div>
          <div className="text-sm text-gray-600">Respiration</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-xl font-bold text-purple-600">
            {realtimeData?.stressLevel ? `${Math.round(realtimeData.stressLevel)}` : '--'}
          </div>
          <div className="text-sm text-gray-600">Stress Level</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-xl font-bold text-yellow-600">
            {realtimeData?.sleepQuality ? `${Math.round(realtimeData.sleepQuality * 100)}` : '--'}%
          </div>
          <div className="text-sm text-gray-600">Sleep Quality</div>
        </div>
      </div>

      {/* Environmental Factors */}
      {realtimeData?.environmentalFactors && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-3">Environmental Factors</h4>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-lg font-bold text-blue-600">
                {Math.round(realtimeData.environmentalFactors.airQuality * 100)}%
              </div>
              <div className="text-sm text-gray-600">Air Quality</div>
            </div>
            <div className="text-center p-3 bg-yellow-50 rounded-lg">
              <div className="text-lg font-bold text-yellow-600">
                {Math.round(realtimeData.environmentalFactors.noiseLevel)}dB
              </div>
              <div className="text-sm text-gray-600">Noise Level</div>
            </div>
            <div className="text-center p-3 bg-orange-50 rounded-lg">
              <div className="text-lg font-bold text-orange-600">
                {Math.round(realtimeData.environmentalFactors.lightExposure * 100)}%
              </div>
              <div className="text-sm text-gray-600">Light Exposure</div>
            </div>
          </div>
        </div>
      )}

      {/* Status Footer */}
      <div className="pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </span>
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <Droplets className="h-4 w-4" />
              <span>Data Quality: 99.2%</span>
            </div>
            <div className="flex items-center space-x-1">
              <Activity className="h-4 w-4" />
              <span>Connection: Strong</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default RealtimeMonitoring; 