/**
 * SectionHeader Component
 * Reusable section header with integrated help info
 */

import React from 'react';
import HelpInfo from './HelpInfo';

const SectionHeader = ({ 
  icon: Icon, 
  title, 
  subtitle, 
  helpTopic,
  helpContent,
  helpPosition = 'modal',
  actions,
  className = ''
}) => {
  return (
    <div className={`flex items-start justify-between mb-4 ${className}`}>
      <div className="flex items-start space-x-3 flex-1">
        {Icon && (
          <div className="p-2 bg-indigo-100 rounded-lg mt-0.5">
            <Icon className="w-5 h-5 text-indigo-600" />
          </div>
        )}
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            {(helpTopic || helpContent) && (
              <HelpInfo 
                topic={helpTopic} 
                helpContent={helpContent}
                position={helpPosition}
                size="sm"
              />
            )}
          </div>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>
          )}
        </div>
      </div>
      {actions && (
        <div className="flex items-center space-x-2 ml-4">
          {actions}
        </div>
      )}
    </div>
  );
};

export default SectionHeader;

