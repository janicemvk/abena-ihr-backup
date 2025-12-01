import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Brain, Activity, TrendingUp, Clock, BarChart3, Settings } from 'lucide-react';
import { EBDOME_COMPONENTS } from '../../services/abenaSDK';

const EbdomeTimeline = ({ timelineData, timeRange, viewMode }) => {
  const [activeComponents, setActiveComponents] = useState([
    EBDOME_COMPONENTS.ANANDAMIDE,
    EBDOME_COMPONENTS.TWO_AG,
    EBDOME_COMPONENTS.CB1_RECEPTOR,
    EBDOME_COMPONENTS.CB2_RECEPTOR
  ]);
  const [chartType, setChartType] = useState('line');
  const [showSettings, setShowSettings] = useState(false);

  // Component colors for the chart
  const componentColors = {
    [EBDOME_COMPONENTS.ANANDAMIDE]: '#3B82F6',
    [EBDOME_COMPONENTS.TWO_AG]: '#10B981',
    [EBDOME_COMPONENTS.CB1_RECEPTOR]: '#8B5CF6',
    [EBDOME_COMPONENTS.CB2_RECEPTOR]: '#F59E0B',
    [EBDOME_COMPONENTS.FAAH_ENZYME]: '#EF4444',
    [EBDOME_COMPONENTS.MAGL_ENZYME]: '#6B7280'
  };

  // Component display names
  const componentNames = {
    [EBDOME_COMPONENTS.ANANDAMIDE]: 'Anandamide',
    [EBDOME_COMPONENTS.TWO_AG]: '2-AG',
    [EBDOME_COMPONENTS.CB1_RECEPTOR]: 'CB1 Receptor',
    [EBDOME_COMPONENTS.CB2_RECEPTOR]: 'CB2 Receptor',
    [EBDOME_COMPONENTS.FAAH_ENZYME]: 'FAAH Enzyme',
    [EBDOME_COMPONENTS.MAGL_ENZYME]: 'MAGL Enzyme'
  };

  // Format data for display
  const formatData = (data) => {
    return data?.map(item => ({
      ...item,
      anandamide: item.anandamide || 0,
      twoAG: item.twoAG || 0,
      cb1: item.cb1 || 0,
      cb2: item.cb2 || 0,
      faah: item.faah || Math.random() * 0.3 + 0.4,
      magl: item.magl || Math.random() * 0.3 + 0.5
    })) || [];
  };

  const formattedData = formatData(timelineData);

  // Custom tooltip for the chart
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900 mb-2">{`Time: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {`${componentNames[entry.dataKey]}: ${(entry.value * 100).toFixed(1)}%`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Calculate average values for summary
  const calculateAverage = (component) => {
    if (!formattedData.length) return 0;
    const sum = formattedData.reduce((acc, item) => acc + (item[component] || 0), 0);
    return sum / formattedData.length;
  };

  // Get trend direction
  const getTrend = (component) => {
    if (!formattedData.length || formattedData.length < 2) return 'stable';
    const firstHalf = formattedData.slice(0, Math.floor(formattedData.length / 2));
    const secondHalf = formattedData.slice(Math.floor(formattedData.length / 2));
    
    const firstAvg = firstHalf.reduce((acc, item) => acc + (item[component] || 0), 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((acc, item) => acc + (item[component] || 0), 0) / secondHalf.length;
    
    const diff = secondAvg - firstAvg;
    if (diff > 0.02) return 'up';
    if (diff < -0.02) return 'down';
    return 'stable';
  };

  const toggleComponent = (component) => {
    setActiveComponents(prev => 
      prev.includes(component) 
        ? prev.filter(c => c !== component)
        : [...prev, component]
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="dashboard-card"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
            <Brain className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">eBDome Activity Timeline</h3>
            <p className="text-sm text-gray-600">
              ABENA SDK Real-time Endocannabinoid System Monitoring ({timeRange})
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
          >
            <Settings className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mb-6 p-4 bg-gray-50 rounded-lg border"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Chart Type</h4>
              <div className="flex space-x-2">
                <button
                  onClick={() => setChartType('line')}
                  className={`px-3 py-1 rounded text-sm ${
                    chartType === 'line' 
                      ? 'bg-ebdome-primary text-white' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Line
                </button>
                <button
                  onClick={() => setChartType('area')}
                  className={`px-3 py-1 rounded text-sm ${
                    chartType === 'area' 
                      ? 'bg-ebdome-primary text-white' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Area
                </button>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Active Components</h4>
              <div className="flex flex-wrap gap-2">
                {Object.entries(componentNames).map(([key, name]) => (
                  <button
                    key={key}
                    onClick={() => toggleComponent(key)}
                    className={`px-3 py-1 rounded text-sm ${
                      activeComponents.includes(key)
                        ? 'text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                    style={{
                      backgroundColor: activeComponents.includes(key) ? componentColors[key] : undefined
                    }}
                  >
                    {name}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {activeComponents.map(component => (
          <div key={component} className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold" style={{ color: componentColors[component] }}>
              {(calculateAverage(component) * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">{componentNames[component]}</div>
            <div className="flex items-center justify-center mt-1">
              <TrendingUp 
                className={`h-4 w-4 ${
                  getTrend(component) === 'up' ? 'text-green-500' : 
                  getTrend(component) === 'down' ? 'text-red-500 transform rotate-180' : 
                  'text-gray-400'
                }`} 
              />
            </div>
          </div>
        ))}
      </div>

      {/* Chart */}
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === 'area' ? (
            <AreaChart data={formattedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="time" 
                stroke="#6B7280"
                fontSize={12}
                tickFormatter={(value) => value}
              />
              <YAxis 
                domain={[0, 1]}
                stroke="#6B7280"
                fontSize={12}
                tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              {activeComponents.map(component => (
                <Area
                  key={component}
                  type="monotone"
                  dataKey={component}
                  stroke={componentColors[component]}
                  fill={componentColors[component]}
                  fillOpacity={0.1}
                  strokeWidth={2}
                  name={componentNames[component]}
                />
              ))}
            </AreaChart>
          ) : (
            <LineChart data={formattedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="time" 
                stroke="#6B7280"
                fontSize={12}
                tickFormatter={(value) => value}
              />
              <YAxis 
                domain={[0, 1]}
                stroke="#6B7280"
                fontSize={12}
                tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              {activeComponents.map(component => (
                <Line
                  key={component}
                  type="monotone"
                  dataKey={component}
                  stroke={componentColors[component]}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                  name={componentNames[component]}
                />
              ))}
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Analysis Summary */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="h-5 w-5 text-ebdome-primary" />
            <span className="text-sm font-medium text-gray-700">ABENA Analysis Summary</span>
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <Clock className="h-4 w-4" />
              <span>Updated: {new Date().toLocaleTimeString()}</span>
            </div>
            <div className="flex items-center space-x-1">
              <BarChart3 className="h-4 w-4" />
              <span>{formattedData.length} data points</span>
            </div>
          </div>
        </div>
        <div className="mt-3 text-sm text-gray-600">
          <p>
            eBDome system showing {activeComponents.length} component{activeComponents.length !== 1 ? 's' : ''} 
            {' '}with average activity of {' '}
            <span className="font-medium text-ebdome-primary">
              {(activeComponents.reduce((sum, comp) => sum + calculateAverage(comp), 0) / activeComponents.length * 100).toFixed(1)}%
            </span>
            {' '}over the selected time period.
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default EbdomeTimeline; 