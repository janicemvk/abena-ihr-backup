/**
 * ECBomeScoreWithHelp Component
 * Shows eCBome score and components with integrated help information
 */

import React from 'react';
import { Brain, TrendingUp, Activity } from 'lucide-react';
import SectionHeader from '../Common/SectionHeader';
import HelpInfo from '../Common/HelpInfo';

const ECBomeScoreWithHelp = ({ ecbomeProfile }) => {
  if (!ecbomeProfile) return null;

  const overallScore = ecbomeProfile.overallScore || ecbomeProfile.score || 0;
  const components = ecbomeProfile.components || {};

  // Helper to format component names
  const formatName = (name) => {
    return name
      .replace(/([A-Z])/g, ' $1')
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')
      .trim();
  };

  // Helper to get score color
  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50';
    if (score >= 0.4) return 'text-orange-600 bg-orange-50';
    return 'text-red-600 bg-red-50';
  };

  // Helper to get status color
  const getStatusColor = (status) => {
    const statusMap = {
      'optimal': 'text-green-700 bg-green-100',
      'good': 'text-green-600 bg-green-50',
      'active': 'text-blue-600 bg-blue-50',
      'normal': 'text-blue-600 bg-blue-50',
      'warning': 'text-yellow-700 bg-yellow-100',
      'elevated': 'text-orange-700 bg-orange-100',
      'critical': 'text-red-700 bg-red-100',
      'low': 'text-red-600 bg-red-50'
    };
    return statusMap[status?.toLowerCase()] || 'text-gray-600 bg-gray-50';
  };

  // Get help topic for specific components
  const getComponentHelpTopic = (componentKey) => {
    const helpTopics = {
      'anandamide': 'anandamide',
      'endocannabinoid': 'anandamide',
      'cb1': 'cb1_receptors',
      'cb1Receptors': 'cb1_receptors',
      'cb1_receptors': 'cb1_receptors',
      'cb2': 'cb2_receptors',
      'cb2Receptors': 'cb2_receptors',
      'cb2_receptors': 'cb2_receptors',
      '2ag': '2ag',
      'twoAG': '2ag'
    };
    return helpTopics[componentKey] || null;
  };

  return (
    <div className="dashboard-card">
      {/* Section Header */}
      <SectionHeader
        icon={Brain}
        title="eCBome Profile Analysis"
        subtitle="Endocannabinoid System Health Assessment"
        helpTopic="ecbome_score"
        helpPosition="modal"
      />

      {/* Overall Score Display */}
      <div className={`mt-6 p-6 rounded-xl ${getScoreColor(overallScore)} border-2 ${getScoreColor(overallScore).replace('bg-', 'border-').replace('-50', '-200')}`}>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h4 className="text-sm font-medium opacity-80">Overall eCBome Score</h4>
              <HelpInfo topic="ecbome_score" size="sm" position="inline" />
            </div>
            <div className="flex items-baseline space-x-3">
              <span className="text-5xl font-bold">{overallScore.toFixed(2)}</span>
              <span className="text-lg font-semibold opacity-70">
                {ecbomeProfile.status || (overallScore >= 0.8 ? 'Excellent' : overallScore >= 0.6 ? 'Good' : 'Needs Attention')}
              </span>
            </div>
          </div>
          <div className="p-4 bg-white bg-opacity-50 rounded-full">
            <Brain className="w-12 h-12" />
          </div>
        </div>
      </div>

      {/* Component Breakdown */}
      {Object.keys(components).length > 0 && (
        <div className="mt-6">
          <div className="flex items-center space-x-2 mb-4">
            <h4 className="font-semibold text-gray-900">Component Analysis</h4>
            <HelpInfo 
              helpContent={{
                title: '12-Module eCBome Components',
                medical: 'The eCBome system evaluates 12 interconnected physiological modules to assess endocannabinoid system function. Each module represents a specific aspect of ECS regulation including receptor activity, endocannabinoid levels, metabolic enzymes, and downstream physiological effects.',
                simple: 'Think of these components as different parts of your body\'s balance system. Each one measures how well a specific part is working. Together, they give a complete picture of your body\'s internal regulation.',
                relatedTopics: ['Anandamide', 'CB1 Receptors', 'CB2 Receptors', '2-AG', 'Homeostasis']
              }}
              size="sm"
              position="inline"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(components).map(([key, component]) => {
              const reading = component.reading || component.score || 0;
              const status = component.status || 'normal';
              const helpTopic = getComponentHelpTopic(key);

              return (
                <div 
                  key={key}
                  className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  {/* Component Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h5 className="font-medium text-gray-900 text-sm">
                          {formatName(key)}
                        </h5>
                        {helpTopic && (
                          <HelpInfo topic={helpTopic} size="xs" position="inline" />
                        )}
                      </div>
                    </div>
                    <span className={`text-lg font-bold ${getScoreColor(reading).split(' ')[0]}`}>
                      {(reading * 100).toFixed(0)}%
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden mb-2">
                    <div 
                      className={`h-full rounded-full transition-all duration-500 ${getScoreColor(reading).split(' ')[1]}`}
                      style={{ width: `${(reading * 100).toFixed(0)}%` }}
                    />
                  </div>

                  {/* Status Badge */}
                  <div className="flex items-center justify-between">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(status)}`}>
                      {status.toUpperCase()}
                    </span>
                    {component.trend && (
                      <span className="text-xs text-gray-500 flex items-center">
                        {component.trend === 'up' && <TrendingUp className="w-3 h-3 mr-1" />}
                        {component.trend === 'down' && <Activity className="w-3 h-3 mr-1" />}
                        {component.trend}
                      </span>
                    )}
                  </div>

                  {/* Notes if available */}
                  {component.notes && (
                    <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                      {component.notes}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Summary Message */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-900">
          <strong>Clinical Note:</strong> The eCBome score provides a holistic view of endocannabinoid system function. 
          Scores above 0.8 indicate optimal homeostatic regulation, while lower scores may suggest areas for therapeutic intervention.
          {' '}
          <button className="text-blue-600 hover:text-blue-800 font-medium underline">
            View detailed analysis →
          </button>
        </p>
      </div>
    </div>
  );
};

export default ECBomeScoreWithHelp;

