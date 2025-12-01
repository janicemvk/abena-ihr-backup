import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Activity, 
  Heart, 
  Brain, 
  Droplets, 
  Shield, 
  Clock, 
  Apple, 
  AlertTriangle, 
  Pill,
  Zap
} from 'lucide-react';
import { ABENA_MODULES } from '../../services/abenaSDK';

const ModuleAnalysis = ({ moduleData, selectedModules, viewMode, onModuleSelect }) => {
  const [expandedModule, setExpandedModule] = useState(null);

  // Module icons mapping
  const moduleIcons = {
    [ABENA_MODULES.METABOLOME]: Activity,
    [ABENA_MODULES.MICROBIOME]: Droplets,
    [ABENA_MODULES.INFLAMMATOME]: AlertTriangle,
    [ABENA_MODULES.IMMUNOME]: Shield,
    [ABENA_MODULES.CHRONOBIOME]: Clock,
    [ABENA_MODULES.NUTRIOME]: Apple,
    [ABENA_MODULES.TOXICOME]: AlertTriangle,
    [ABENA_MODULES.PHARMACOME]: Pill,
    [ABENA_MODULES.STRESS_RESPONSE]: Zap,
    [ABENA_MODULES.CARDIOVASCULAR]: Heart,
    [ABENA_MODULES.NEUROLOGICAL]: Brain,
    [ABENA_MODULES.HORMONAL]: Activity
  };

  // Module display names
  const moduleNames = {
    [ABENA_MODULES.METABOLOME]: 'Metabolome',
    [ABENA_MODULES.MICROBIOME]: 'Microbiome',
    [ABENA_MODULES.INFLAMMATOME]: 'Inflammatome',
    [ABENA_MODULES.IMMUNOME]: 'Immunome',
    [ABENA_MODULES.CHRONOBIOME]: 'Chronobiome',
    [ABENA_MODULES.NUTRIOME]: 'Nutriome',
    [ABENA_MODULES.TOXICOME]: 'Toxicome',
    [ABENA_MODULES.PHARMACOME]: 'Pharmacome',
    [ABENA_MODULES.STRESS_RESPONSE]: 'Stress Response',
    [ABENA_MODULES.CARDIOVASCULAR]: 'Cardiovascular',
    [ABENA_MODULES.NEUROLOGICAL]: 'Neurological',
    [ABENA_MODULES.HORMONAL]: 'Hormonal'
  };

  const getStatusColor = (status) => {
    const colors = {
      'excellent': 'text-green-600 bg-green-100 border-green-200',
      'optimal': 'text-green-600 bg-green-100 border-green-200',
      'good': 'text-blue-600 bg-blue-100 border-blue-200',
      'moderate': 'text-yellow-600 bg-yellow-100 border-yellow-200',
      'suboptimal': 'text-orange-600 bg-orange-100 border-orange-200',
      'concerning': 'text-red-600 bg-red-100 border-red-200'
    };
    return colors[status] || 'text-gray-600 bg-gray-100 border-gray-200';
  };

  const getTrendIcon = (trend) => {
    if (trend === 'improving') return <TrendingUp className="h-4 w-4 text-green-500" />;
    if (trend === 'declining') return <TrendingDown className="h-4 w-4 text-red-500" />;
    return <Minus className="h-4 w-4 text-gray-500" />;
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-blue-600';
    if (score >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Format data for chart
  const chartData = moduleData ? Object.entries(moduleData).map(([key, data]) => ({
    name: moduleNames[key] || key,
    score: Math.round(data.score * 100),
    status: data.status,
    trend: data.trend
  })) : [];

  // Filter modules based on selection
  const filteredModules = selectedModules.length > 0 
    ? Object.entries(moduleData || {}).filter(([key]) => selectedModules.includes(key))
    : Object.entries(moduleData || {});

  const handleModuleToggle = (moduleKey) => {
    if (selectedModules.includes(moduleKey)) {
      onModuleSelect(selectedModules.filter(m => m !== moduleKey));
    } else {
      onModuleSelect([...selectedModules, moduleKey]);
    }
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
            <Activity className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">12 Core Module Analysis</h3>
            <p className="text-sm text-gray-600">
              ABENA SDK Comprehensive Biological Module Assessment
            </p>
          </div>
        </div>
        <div className="text-sm text-gray-500">
          {filteredModules.length} of {Object.keys(moduleData || {}).length} modules shown
        </div>
      </div>

      {/* Chart View */}
      {viewMode === 'detailed' && (
        <div className="mb-6">
          <h4 className="text-md font-medium text-gray-900 mb-4">Module Score Distribution</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis 
                  dataKey="name" 
                  stroke="#6B7280"
                  fontSize={12}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  stroke="#6B7280"
                  fontSize={12}
                  tickFormatter={(value) => `${value}%`}
                />
                <Tooltip 
                  formatter={(value) => [`${value}%`, 'Score']}
                  labelFormatter={(label) => `Module: ${label}`}
                />
                <Bar 
                  dataKey="score" 
                  fill="#3B82F6"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Module Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {filteredModules.map(([moduleKey, moduleInfo]) => {
          const Icon = moduleIcons[moduleKey] || Activity;
          const isSelected = selectedModules.includes(moduleKey);
          const isExpanded = expandedModule === moduleKey;
          
          return (
            <motion.div
              key={moduleKey}
              layout
              className={`border rounded-lg p-4 cursor-pointer transition-all ${
                isSelected 
                  ? 'border-ebdome-primary bg-blue-50' 
                  : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
              }`}
              onClick={() => handleModuleToggle(moduleKey)}
              onDoubleClick={() => setExpandedModule(isExpanded ? null : moduleKey)}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <Icon className={`h-5 w-5 ${isSelected ? 'text-ebdome-primary' : 'text-gray-600'}`} />
                  <h4 className="font-medium text-gray-900 text-sm">
                    {moduleNames[moduleKey] || moduleKey}
                  </h4>
                </div>
                {getTrendIcon(moduleInfo.trend)}
              </div>

              <div className="space-y-2">
                {/* Score */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Score</span>
                  <span className={`font-semibold ${getScoreColor(moduleInfo.score)}`}>
                    {Math.round(moduleInfo.score * 100)}%
                  </span>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-ebdome-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${moduleInfo.score * 100}%` }}
                  />
                </div>

                {/* Status */}
                <div className="flex items-center justify-center">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(moduleInfo.status)}`}>
                    {moduleInfo.status}
                  </span>
                </div>

                {/* Expanded Info */}
                {isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mt-3 pt-3 border-t border-gray-200"
                  >
                    <div className="text-xs text-gray-600 space-y-1">
                      <div>Trend: {moduleInfo.trend}</div>
                      <div>Status: {moduleInfo.status}</div>
                      <div>Last Updated: {new Date().toLocaleTimeString()}</div>
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Summary Statistics */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {Object.values(moduleData || {}).filter(m => m.status === 'excellent' || m.status === 'optimal').length}
            </div>
            <div className="text-sm text-gray-600">Optimal</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {Object.values(moduleData || {}).filter(m => m.status === 'good' || m.status === 'moderate').length}
            </div>
            <div className="text-sm text-gray-600">Good</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {Object.values(moduleData || {}).filter(m => m.status === 'suboptimal').length}
            </div>
            <div className="text-sm text-gray-600">Needs Attention</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {Object.values(moduleData || {}).filter(m => m.status === 'concerning').length}
            </div>
            <div className="text-sm text-gray-600">Critical</div>
          </div>
        </div>
      </div>

      {/* Analysis Footer */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div>
            ABENA Module Analysis • {Object.keys(moduleData || {}).length} modules monitored
          </div>
          <div>
            Average Score: {' '}
            <span className="font-medium text-ebdome-primary">
              {Math.round(Object.values(moduleData || {}).reduce((sum, m) => sum + m.score, 0) / Object.keys(moduleData || {}).length * 100)}%
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ModuleAnalysis; 