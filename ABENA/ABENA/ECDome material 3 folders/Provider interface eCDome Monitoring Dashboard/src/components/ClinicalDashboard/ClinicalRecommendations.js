import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Brain, 
  Heart, 
  Activity, 
  Pill, 
  Apple, 
  Clock, 
  TrendingUp, 
  ChevronRight, 
  CheckCircle, 
  AlertCircle, 
  User, 
  FileText, 
  Target, 
  Zap,
  Shield,
  Droplets
} from 'lucide-react';
import { usePatient } from '../../contexts/PatientContext';
import { useDashboard } from '../../contexts/DashboardContext';

const ClinicalRecommendations = ({ recommendations = [], onRecommendationAction }) => {
  const { selectedPatient, patientData } = usePatient();
  const { realtimeData } = useDashboard();
  const [expandedRecommendation, setExpandedRecommendation] = useState(null);
  const [implementedRecommendations, setImplementedRecommendations] = useState(new Set());

  // Recommendation categories
  const categoryConfig = {
    lifestyle: {
      icon: Activity,
      color: 'bg-green-100 text-green-800',
      borderColor: 'border-green-200'
    },
    nutrition: {
      icon: Apple,
      color: 'bg-orange-100 text-orange-800',
      borderColor: 'border-orange-200'
    },
    supplement: {
      icon: Pill,
      color: 'bg-blue-100 text-blue-800',
      borderColor: 'border-blue-200'
    },
    monitoring: {
      icon: Activity,
      color: 'bg-purple-100 text-purple-800',
      borderColor: 'border-purple-200'
    },
    intervention: {
      icon: Zap,
      color: 'bg-red-100 text-red-800',
      borderColor: 'border-red-200'
    },
    prevention: {
      icon: Shield,
      color: 'bg-indigo-100 text-indigo-800',
      borderColor: 'border-indigo-200'
    }
  };

  // Priority levels
  const priorityConfig = {
    high: {
      label: 'High Priority',
      color: 'bg-red-100 text-red-800',
      dot: 'bg-red-500'
    },
    medium: {
      label: 'Medium Priority',
      color: 'bg-yellow-100 text-yellow-800',
      dot: 'bg-yellow-500'
    },
    low: {
      label: 'Low Priority',
      color: 'bg-green-100 text-green-800',
      dot: 'bg-green-500'
    }
  };

  // Mock recommendations if none provided
  const mockRecommendations = [
    {
      id: 'rec-001',
      title: 'Optimize eCDome Balance',
      category: 'supplement',
      priority: 'high',
      description: 'Patient shows CB1 receptor deficiency. Consider targeted endocannabinoid support.',
      rationale: 'eCDome analysis indicates 15% reduction in CB1 activity over the past 48 hours. Anandamide levels are suboptimal.',
      protocol: {
        intervention: 'Omega-3 supplementation (EPA/DHA 2:1 ratio)',
        dosage: '2000mg daily with meals',
        duration: '8 weeks',
        monitoring: 'Weekly eCDome profile assessment'
      },
      expectedOutcomes: [
        'Improve CB1 receptor sensitivity (15-20%)',
        'Enhance anandamide production',
        'Reduce inflammatory markers'
      ],
      contraindications: ['Blood thinning medications', 'Severe liver disease'],
      evidenceLevel: 'Strong',
      confidenceScore: 0.87,
      affectedModules: ['eCDome', 'Inflammatome', 'Neurological'],
      timeline: '2-4 weeks to see initial benefits',
      cost: '$45-60/month'
    },
    {
      id: 'rec-002',
      title: 'Circadian Rhythm Optimization',
      category: 'lifestyle',
      priority: 'medium',
      description: 'Sleep pattern analysis suggests circadian misalignment affecting multiple systems.',
      rationale: 'Chronobiome data shows 32% deviation from optimal circadian patterns. This impacts metabolic and hormonal function.',
      protocol: {
        intervention: 'Light therapy and sleep hygiene protocol',
        dosage: '10,000 lux light exposure for 30 minutes upon waking',
        duration: '4 weeks',
        monitoring: 'Sleep tracking and weekly assessment'
      },
      expectedOutcomes: [
        'Improve sleep quality (25-30%)',
        'Normalize cortisol rhythm',
        'Enhance metabolic efficiency'
      ],
      contraindications: ['Bipolar disorder', 'Retinal conditions'],
      evidenceLevel: 'Moderate',
      confidenceScore: 0.73,
      affectedModules: ['Chronobiome', 'Hormonal', 'Metabolome'],
      timeline: '1-2 weeks for noticeable improvement',
      cost: '$120-200 (one-time light therapy device)'
    },
    {
      id: 'rec-003',
      title: 'Anti-Inflammatory Nutrition Protocol',
      category: 'nutrition',
      priority: 'high',
      description: 'Inflammatome analysis indicates elevated inflammatory markers requiring dietary intervention.',
      rationale: 'Pro-inflammatory cytokines elevated 40% above baseline. Microbiome diversity reduced by 25%.',
      protocol: {
        intervention: 'Mediterranean-style anti-inflammatory diet',
        dosage: 'Specific macro/micronutrient targets',
        duration: '12 weeks',
        monitoring: 'Monthly inflammatory marker assessment'
      },
      expectedOutcomes: [
        'Reduce CRP levels (30-40%)',
        'Improve microbiome diversity',
        'Enhanced cognitive function'
      ],
      contraindications: ['Food allergies', 'Eating disorders'],
      evidenceLevel: 'Strong',
      confidenceScore: 0.92,
      affectedModules: ['Inflammatome', 'Microbiome', 'Nutriome'],
      timeline: '4-6 weeks for significant changes',
      cost: '$50-80/week (grocery budget increase)'
    },
    {
      id: 'rec-004',
      title: 'Stress Response Modulation',
      category: 'intervention',
      priority: 'medium',
      description: 'HRV analysis shows compromised stress response. Recommend targeted intervention.',
      rationale: 'Heart rate variability decreased 28%. Elevated cortisol patterns indicate chronic stress activation.',
      protocol: {
        intervention: 'Breathwork and mindfulness training',
        dosage: '20 minutes daily structured practice',
        duration: '8 weeks',
        monitoring: 'Weekly HRV and stress marker assessment'
      },
      expectedOutcomes: [
        'Improve HRV (20-25%)',
        'Reduce cortisol levels',
        'Enhanced stress resilience'
      ],
      contraindications: ['Severe anxiety disorders', 'PTSD triggers'],
      evidenceLevel: 'Moderate',
      confidenceScore: 0.68,
      affectedModules: ['Stress Response', 'Cardiovascular', 'Neurological'],
      timeline: '2-3 weeks for initial benefits',
      cost: '$30-50/month (app subscriptions)'
    }
  ];

  const displayRecommendations = recommendations.length > 0 ? recommendations : mockRecommendations;

  const handleRecommendationAction = (recommendationId, action) => {
    if (action === 'implement') {
      setImplementedRecommendations(prev => new Set([...prev, recommendationId]));
    }
    
    if (onRecommendationAction) {
      onRecommendationAction(recommendationId, action);
    }
  };

  const getEvidenceColor = (level) => {
    switch (level) {
      case 'Strong':
        return 'text-green-600 bg-green-100';
      case 'Moderate':
        return 'text-yellow-600 bg-yellow-100';
      case 'Limited':
        return 'text-orange-600 bg-orange-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="dashboard-card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Brain className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Clinical Recommendations
            </h3>
            <p className="text-sm text-gray-500">
              AI-powered personalized intervention protocols
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-600">
            {displayRecommendations.length} recommendations
          </span>
          <div className="w-2 h-2 bg-blue-500 rounded-full" />
        </div>
      </div>

      <div className="space-y-4">
        {displayRecommendations.map((recommendation) => {
          const categoryIcon = categoryConfig[recommendation.category]?.icon || FileText;
          const IconComponent = categoryIcon;
          const isExpanded = expandedRecommendation === recommendation.id;
          const isImplemented = implementedRecommendations.has(recommendation.id);

          return (
            <motion.div
              key={recommendation.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`border rounded-lg p-4 transition-all hover:shadow-md ${
                isImplemented ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className={`p-2 rounded-lg ${categoryConfig[recommendation.category]?.color}`}>
                    <IconComponent className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-medium text-gray-900">
                        {recommendation.title}
                      </h4>
                      {isImplemented && (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 text-xs rounded ${
                        priorityConfig[recommendation.priority]?.color
                      }`}>
                        {priorityConfig[recommendation.priority]?.label}
                      </span>
                      <span className={`px-2 py-1 text-xs rounded ${
                        getEvidenceColor(recommendation.evidenceLevel)
                      }`}>
                        {recommendation.evidenceLevel} Evidence
                      </span>
                      <span className="text-xs text-gray-500">
                        {Math.round(recommendation.confidenceScore * 100)}% confidence
                      </span>
                    </div>

                    <p className="text-sm text-gray-600 mb-3">
                      {recommendation.description}
                    </p>

                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span className="flex items-center space-x-1">
                        <Clock className="w-3 h-3" />
                        <span>{recommendation.timeline}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <Target className="w-3 h-3" />
                        <span>{recommendation.cost}</span>
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setExpandedRecommendation(
                      isExpanded ? null : recommendation.id
                    )}
                    className="p-1 hover:bg-gray-100 rounded transition-colors"
                  >
                    <ChevronRight 
                      className={`w-4 h-4 text-gray-400 transition-transform ${
                        isExpanded ? 'rotate-90' : ''
                      }`}
                    />
                  </button>
                </div>
              </div>

              {isExpanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-4 pt-4 border-t border-gray-200"
                >
                  <div className="space-y-4">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">
                        Clinical Rationale
                      </h5>
                      <p className="text-sm text-gray-600">
                        {recommendation.rationale}
                      </p>
                    </div>

                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">
                        Treatment Protocol
                      </h5>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <p className="text-xs font-medium text-gray-700 mb-1">
                            Intervention
                          </p>
                          <p className="text-sm text-gray-600">
                            {recommendation.protocol.intervention}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-medium text-gray-700 mb-1">
                            Dosage/Frequency
                          </p>
                          <p className="text-sm text-gray-600">
                            {recommendation.protocol.dosage}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-medium text-gray-700 mb-1">
                            Duration
                          </p>
                          <p className="text-sm text-gray-600">
                            {recommendation.protocol.duration}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-medium text-gray-700 mb-1">
                            Monitoring
                          </p>
                          <p className="text-sm text-gray-600">
                            {recommendation.protocol.monitoring}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">
                        Expected Outcomes
                      </h5>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {recommendation.expectedOutcomes.map((outcome, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <TrendingUp className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                            <span>{outcome}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">
                        Affected Systems
                      </h5>
                      <div className="flex flex-wrap gap-2">
                        {recommendation.affectedModules.map((module, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                          >
                            {module}
                          </span>
                        ))}
                      </div>
                    </div>

                    {recommendation.contraindications && (
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">
                          Contraindications
                        </h5>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {recommendation.contraindications.map((contraindication, index) => (
                            <li key={index} className="flex items-start space-x-2">
                              <AlertCircle className="w-3 h-3 text-red-500 mt-0.5 flex-shrink-0" />
                              <span>{contraindication}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="flex space-x-2 pt-3 border-t border-gray-100">
                      {!isImplemented ? (
                        <>
                          <button
                            onClick={() => handleRecommendationAction(recommendation.id, 'implement')}
                            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            Implement Protocol
                          </button>
                          <button
                            onClick={() => handleRecommendationAction(recommendation.id, 'modify')}
                            className="px-4 py-2 border border-gray-300 text-sm rounded-lg hover:bg-gray-50 transition-colors"
                          >
                            Modify Protocol
                          </button>
                        </>
                      ) : (
                        <div className="flex items-center space-x-2 text-green-600">
                          <CheckCircle className="w-4 h-4" />
                          <span className="text-sm font-medium">Protocol Implemented</span>
                        </div>
                      )}
                      <button
                        onClick={() => handleRecommendationAction(recommendation.id, 'view_research')}
                        className="px-4 py-2 text-blue-600 text-sm hover:bg-blue-50 rounded-lg transition-colors"
                      >
                        View Research
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <div className="flex items-start space-x-3">
          <Brain className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900 mb-1">
              Personalized Medicine Approach
            </h4>
            <p className="text-sm text-blue-700">
              These recommendations are generated using AI analysis of your patient's unique 
              eCDome profile, 12 ABENA modules, and real-time biomarker data. Each protocol 
              is tailored to the individual's specific biological patterns and health goals.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClinicalRecommendations; 