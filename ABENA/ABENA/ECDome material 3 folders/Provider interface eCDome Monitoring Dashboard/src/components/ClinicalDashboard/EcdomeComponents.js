import React from 'react';
import { motion } from 'framer-motion';
import { RadialBarChart, RadialBar, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';
import { Brain, Activity, TrendingUp, Info, Zap } from 'lucide-react';

const EcdomeComponents = ({ ecdomeProfile, realtimeData }) => {
  if (!ecdomeProfile) return null;

  // Component data for radial charts
  const componentData = [
    {
      name: 'Anandamide',
      value: Math.round(ecdomeProfile.anandamideLevels * 100),
      color: '#3B82F6',
      description: 'Bliss Molecule',
      icon: '🧠',
      optimal: 70,
      current: ecdomeProfile.anandamideLevels
    },
    {
      name: '2-AG',
      value: Math.round(ecdomeProfile.twoAGLevels * 100),
      color: '#10B981',
      description: '2-Arachidonoylglycerol',
      icon: '🌿',
      optimal: 65,
      current: ecdomeProfile.twoAGLevels
    },
    {
      name: 'CB1 Activity',
      value: Math.round(ecdomeProfile.cb1Activity * 100),
      color: '#8B5CF6',
      description: 'Cannabinoid Receptor 1',
      icon: '🔗',
      optimal: 75,
      current: ecdomeProfile.cb1Activity
    },
    {
      name: 'CB2 Activity',
      value: Math.round(ecdomeProfile.cb2Activity * 100),
      color: '#F59E0B',
      description: 'Cannabinoid Receptor 2',
      icon: '🛡️',
      optimal: 70,
      current: ecdomeProfile.cb2Activity
    },
    {
      name: 'System Balance',
      value: Math.round(ecdomeProfile.systemBalance * 100),
      color: '#EF4444',
      description: 'Overall Harmony',
      icon: '⚖️',
      optimal: 80,
      current: ecdomeProfile.systemBalance
    }
  ];

  // System balance pie chart data
  const balanceData = [
    { name: 'Balanced', value: ecdomeProfile.systemBalance * 100, fill: '#10B981' },
    { name: 'Imbalanced', value: 100 - (ecdomeProfile.systemBalance * 100), fill: '#E5E7EB' }
  ];

  const getStatusColor = (current, optimal) => {
    const percentage = (current * 100) / optimal;
    if (percentage >= 90) return 'text-green-600';
    if (percentage >= 70) return 'text-blue-600';
    if (percentage >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusText = (current, optimal) => {
    const percentage = (current * 100) / optimal;
    if (percentage >= 90) return 'Excellent';
    if (percentage >= 70) return 'Good';
    if (percentage >= 50) return 'Moderate';
    return 'Needs Attention';
  };

  const ComponentCard = ({ component, index }) => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.1 }}
      className="bg-white rounded-lg p-6 border border-gray-200 hover:shadow-md transition-shadow"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="text-2xl">{component.icon}</div>
          <div>
            <h4 className="font-medium text-gray-900">{component.name}</h4>
            <p className="text-sm text-gray-600">{component.description}</p>
          </div>
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold ${getStatusColor(component.current, component.optimal / 100)}`}>
            {component.value}%
          </div>
          <div className="text-sm text-gray-500">
            Target: {component.optimal}%
          </div>
        </div>
      </div>

      {/* Radial Chart */}
      <div className="relative h-32">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="60%"
            outerRadius="90%"
            data={[{ value: component.value, fill: component.color }]}
            startAngle={90}
            endAngle={-270}
          >
            <RadialBar dataKey="value" cornerRadius={10} fill={component.color} />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-lg font-bold text-gray-900">
              {component.value}%
            </div>
            <div className="text-xs text-gray-500">
              {getStatusText(component.current, component.optimal / 100)}
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mt-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Activity Level</span>
          <span>{component.value}% of target</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="h-2 rounded-full transition-all duration-300"
            style={{ 
              width: `${Math.min(component.value, 100)}%`,
              backgroundColor: component.color
            }}
          />
        </div>
      </div>
    </motion.div>
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="dashboard-card"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg">
            <Brain className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">eCDome Component Analysis</h3>
            <p className="text-sm text-gray-600">
              ABENA SDK Endocannabinoid System Components
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 text-sm text-gray-600">
            <Activity className="h-4 w-4" />
            <span>Live Data</span>
          </div>
        </div>
      </div>

      {/* Overall System Balance */}
      <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-semibold text-gray-900 mb-1">Overall eCDome Health Score</h4>
            <p className="text-sm text-gray-600">
              Comprehensive endocannabinoid system balance assessment
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-ecdome-primary">
              {Math.round(ecdomeProfile.overallScore * 100)}%
            </div>
            <div className="text-sm text-gray-600">
              {getStatusText(ecdomeProfile.overallScore, 0.8)}
            </div>
          </div>
        </div>
        
        {/* System Balance Pie Chart */}
        <div className="mt-4 flex items-center justify-center">
          <div className="h-24 w-24">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={balanceData}
                  cx="50%"
                  cy="50%"
                  innerRadius={25}
                  outerRadius={40}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {balanceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Component Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {componentData.map((component, index) => (
          <ComponentCard key={component.name} component={component} index={index} />
        ))}
      </div>

      {/* Real-time Updates */}
      {realtimeData && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-medium text-gray-900 flex items-center">
              <Zap className="h-5 w-5 mr-2 text-ecdome-primary" />
              Real-time Activity
            </h4>
            <div className="text-sm text-gray-500">
              Last updated: {new Date().toLocaleTimeString()}
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-xl font-bold text-ecdome-primary">
                {Math.round((realtimeData.ecdomeActivity || 0.82) * 100)}%
              </div>
              <div className="text-sm text-gray-600">Current Activity</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-xl font-bold text-green-600">
                {Math.round((ecdomeProfile.systemBalance || 0.75) * 100)}%
              </div>
              <div className="text-sm text-gray-600">System Balance</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-xl font-bold text-blue-600">
                {Math.round((ecdomeProfile.anandamideLevels || 0.68) * 100)}%
              </div>
              <div className="text-sm text-gray-600">Anandamide</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-xl font-bold text-purple-600">
                {Math.round((ecdomeProfile.cb1Activity || 0.72) * 100)}%
              </div>
              <div className="text-sm text-gray-600">CB1 Activity</div>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Summary */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Info className="h-5 w-5 text-ecdome-primary" />
            <span className="text-sm font-medium text-gray-700">ABENA Analysis Summary</span>
          </div>
          <div className="flex items-center space-x-1">
            <TrendingUp className="h-4 w-4 text-green-500" />
            <span className="text-sm text-gray-600">System trending positively</span>
          </div>
        </div>
        <div className="mt-2 text-sm text-gray-600">
          <p>
            eCDome system showing balanced endocannabinoid activity with {' '}
            <span className="font-medium text-ecdome-primary">
              {Math.round(ecdomeProfile.overallScore * 100)}%
            </span>
            {' '}overall health score. Primary components within optimal ranges.
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default EcdomeComponents; 