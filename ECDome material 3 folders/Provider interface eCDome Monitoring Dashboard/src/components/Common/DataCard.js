/**
 * DataCard Component
 * Displays data with integrated help information
 */

import React from 'react';
import HelpInfo from './HelpInfo';

const DataCard = ({
  label,
  value,
  unit,
  icon: Icon,
  helpTopic,
  helpContent,
  status, // 'normal', 'warning', 'critical'
  trend, // 'up', 'down', 'stable'
  className = ''
}) => {
  const statusColors = {
    normal: 'bg-green-50 border-green-200 text-green-900',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    critical: 'bg-red-50 border-red-200 text-red-900',
    info: 'bg-blue-50 border-blue-200 text-blue-900'
  };

  const statusColor = status ? statusColors[status] : 'bg-white border-gray-200 text-gray-900';

  return (
    <div className={`relative p-4 rounded-lg border ${statusColor} ${className}`}>
      {Icon && (
        <div className="absolute top-3 right-3 opacity-20">
          <Icon className="w-8 h-8" />
        </div>
      )}
      
      <div className="relative">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium opacity-80">{label}</span>
          {(helpTopic || helpContent) && (
            <HelpInfo 
              topic={helpTopic}
              helpContent={helpContent}
              size="sm"
              position="inline"
            />
          )}
        </div>
        
        <div className="flex items-baseline space-x-2">
          <span className="text-2xl font-bold">
            {value}
          </span>
          {unit && (
            <span className="text-sm opacity-70">{unit}</span>
          )}
        </div>

        {trend && (
          <div className="mt-2 flex items-center space-x-1">
            <span className="text-xs opacity-70">
              {trend === 'up' && '↑ Increasing'}
              {trend === 'down' && '↓ Decreasing'}
              {trend === 'stable' && '→ Stable'}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataCard;

