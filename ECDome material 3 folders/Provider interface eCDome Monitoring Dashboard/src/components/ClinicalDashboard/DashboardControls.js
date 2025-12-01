import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, Grid, List, Eye, Filter, Settings, Clock } from 'lucide-react';

const DashboardControls = ({ 
  viewMode, 
  setViewMode, 
  timeRange, 
  onTimeRangeChange, 
  selectedModules, 
  setSelectedModules 
}) => {
  const timeRangeOptions = [
    { value: '24h', label: '24 Hours', icon: Clock },
    { value: '7d', label: '7 Days', icon: Calendar },
    { value: '30d', label: '30 Days', icon: Calendar }
  ];

  const viewModeOptions = [
    { value: 'overview', label: 'Overview', icon: Grid },
    { value: 'detailed', label: 'Detailed', icon: List },
    { value: 'comparison', label: 'Comparison', icon: Eye }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="dashboard-card"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Settings className="h-5 w-5 mr-2 text-ebdome-primary" />
          Dashboard Controls
        </h3>
        <div className="text-sm text-gray-500">
          Configure your dashboard view
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Time Range Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Time Range
          </label>
          <div className="flex space-x-2">
            {timeRangeOptions.map((option) => {
              const Icon = option.icon;
              return (
                <button
                  key={option.value}
                  onClick={() => onTimeRangeChange(option.value)}
                  className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    timeRange === option.value
                      ? 'bg-ebdome-primary text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {option.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* View Mode Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            View Mode
          </label>
          <div className="flex space-x-2">
            {viewModeOptions.map((option) => {
              const Icon = option.icon;
              return (
                <button
                  key={option.value}
                  onClick={() => setViewMode(option.value)}
                  className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    viewMode === option.value
                      ? 'bg-ebdome-primary text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {option.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Module Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Module Filter
          </label>
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <select
              value={selectedModules.length > 0 ? 'custom' : 'all'}
              onChange={(e) => {
                if (e.target.value === 'all') {
                  setSelectedModules([]);
                } else if (e.target.value === 'core') {
                  setSelectedModules(['metabolome', 'microbiome', 'inflammatome', 'immunome']);
                } else if (e.target.value === 'lifestyle') {
                  setSelectedModules(['chronobiome', 'nutriome', 'stressResponse']);
                }
              }}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-ebdome-primary focus:border-transparent"
            >
              <option value="all">All Modules</option>
              <option value="core">Core Modules</option>
              <option value="lifestyle">Lifestyle Modules</option>
              <option value="custom">Custom Selection</option>
            </select>
          </div>
        </div>
      </div>

      {/* Additional Controls */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Showing {timeRange} data in {viewMode} mode
            {selectedModules.length > 0 && (
              <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                {selectedModules.length} modules selected
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <button className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800">
              Reset
            </button>
            <button className="px-3 py-1 text-sm bg-ebdome-primary text-white rounded hover:bg-blue-700">
              Apply
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default DashboardControls; 