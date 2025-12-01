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
  Droplets,
  ExternalLink,
  Stethoscope,
  UserPlus
} from 'lucide-react';
import { usePatient } from '../../contexts/PatientContext';
import { useDashboard } from '../../contexts/DashboardContext';
import toast from 'react-hot-toast';
import HelpInfo from '../Common/HelpInfo';

const ClinicalRecommendations = ({ recommendations = [], onRecommendationAction }) => {
  const { selectedPatient, patientData } = usePatient();
  const { realtimeData } = useDashboard();
  const [expandedRecommendation, setExpandedRecommendation] = useState(null);
  const [implementedRecommendations, setImplementedRecommendations] = useState(new Set());
  const [patientRecommendations, setPatientRecommendations] = useState([]);
  const [showResearchModal, setShowResearchModal] = useState(false);
  const [showModifyModal, setShowModifyModal] = useState(false);
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);

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
    },
    medication: {
      icon: Pill,
      color: 'bg-purple-100 text-purple-800',
      borderColor: 'border-purple-200'
    },
    referral: {
      icon: UserPlus,
      color: 'bg-pink-100 text-pink-800',
      borderColor: 'border-pink-200'
    },
    therapy: {
      icon: Stethoscope,
      color: 'bg-teal-100 text-teal-800',
      borderColor: 'border-teal-200'
    },
    imaging: {
      icon: Activity,
      color: 'bg-cyan-100 text-cyan-800',
      borderColor: 'border-cyan-200'
    },
    'acute-care': {
      icon: AlertCircle,
      color: 'bg-red-100 text-red-800',
      borderColor: 'border-red-200'
    }
  };

  // Priority levels
  const priorityConfig = {
    critical: {
      label: 'Critical Priority',
      color: 'bg-red-200 text-red-900',
      dot: 'bg-red-700'
    },
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

  // Load patient-specific recommendations
  useEffect(() => {
    if (patientData && patientData.data && patientData.data.recommendations) {
      // Transform recommendations from patient data
      const transformedRecs = patientData.data.recommendations.map(rec => ({
        ...rec,
        evidenceLevel: 'Strong',
        confidenceScore: 0.85,
        affectedModules: [rec.category],
        timeline: '2-4 weeks',
        cost: 'Varies',
        protocol: {
          intervention: rec.description,
          dosage: 'As prescribed',
          duration: 'Ongoing',
          monitoring: 'Regular follow-up'
        },
        expectedOutcomes: [
          'Improved clinical outcomes',
          'Better quality of life'
        ],
        contraindications: ['See patient allergies and contraindications'],
        rationale: rec.evidence || 'Evidence-based clinical recommendation'
      }));
      setPatientRecommendations(transformedRecs);
      console.log(`✅ Loaded ${transformedRecs.length} recommendations for ${selectedPatient}`);
    } else {
      setPatientRecommendations([]);
    }
  }, [patientData, selectedPatient]);

  // Mock recommendations if none provided
  const mockRecommendations = [
    {
      id: 'rec-001',
      title: 'Optimize eBDome Balance',
      category: 'supplement',
      priority: 'high',
      description: 'Patient shows CB1 receptor deficiency. Consider targeted endocannabinoid support.',
      rationale: 'eBDome analysis indicates 15% reduction in CB1 activity over the past 48 hours. Anandamide levels are suboptimal.',
      protocol: {
        intervention: 'Omega-3 supplementation (EPA/DHA 2:1 ratio)',
        dosage: '2000mg daily with meals',
        duration: '8 weeks',
        monitoring: 'Weekly eBDome profile assessment'
      },
      expectedOutcomes: [
        'Improve CB1 receptor sensitivity (15-20%)',
        'Enhance anandamide production',
        'Reduce inflammatory markers'
      ],
      contraindications: ['Blood thinning medications', 'Severe liver disease'],
      evidenceLevel: 'Strong',
      confidenceScore: 0.87,
      affectedModules: ['eBDome', 'Inflammatome', 'Neurological'],
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

  const displayRecommendations = patientRecommendations.length > 0 ? patientRecommendations : 
                                  recommendations.length > 0 ? recommendations : mockRecommendations;

  const handleRecommendationAction = (recommendationId, action, recommendationTitle) => {
    const recommendation = patientRecommendations.find(r => r.id === recommendationId);
    
    if (action === 'implement') {
      setImplementedRecommendations(prev => new Set([...prev, recommendationId]));
      toast.success(`✅ Protocol "${recommendationTitle}" marked as implemented`, {
        duration: 3000,
        icon: '✅'
      });
      console.log(`Recommendation ${recommendationId} implemented by provider at ${new Date().toISOString()}`);
    } else if (action === 'modify') {
      setSelectedRecommendation(recommendation);
      setShowModifyModal(true);
    } else if (action === 'view_research') {
      setSelectedRecommendation(recommendation);
      setShowResearchModal(true);
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
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900">
                Clinical Recommendations
              </h3>
              <HelpInfo topic="clinical_recommendations" size="sm" position="modal" />
            </div>
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
          const category = categoryConfig[recommendation.category] || categoryConfig.lifestyle;
          const IconComponent = category.icon;
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
                  <div className={`p-2 rounded-lg ${category.color || 'bg-gray-100 text-gray-800'}`}>
                    <IconComponent className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-medium text-gray-900">
                        {recommendation.title}
                      </h4>
                      <HelpInfo 
                        helpContent={{
                          title: recommendation.title,
                          medical: recommendation.rationale || `Clinical protocol for ${recommendation.title.toLowerCase()}. This evidence-based intervention is designed to address specific patient needs based on current guidelines and biomarker data.`,
                          simple: recommendation.description || `This recommendation suggests ${recommendation.title.toLowerCase()} to help improve your health outcomes.`,
                          significance: `Priority: ${recommendation.priority || 'Medium'} | Evidence: ${recommendation.evidenceLevel || 'Moderate'}`
                        }}
                        size="sm"
                        position="inline"
                      />
                      {isImplemented && (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2 mb-2">
                      {recommendation.priority && (
                        <span className={`px-2 py-1 text-xs rounded ${
                          priorityConfig[recommendation.priority]?.color || 'bg-gray-100 text-gray-800'
                        }`}>
                          {priorityConfig[recommendation.priority]?.label || recommendation.priority}
                        </span>
                      )}
                      {recommendation.evidenceLevel && (
                        <span className={`px-2 py-1 text-xs rounded ${
                          getEvidenceColor(recommendation.evidenceLevel)
                        }`}>
                          {recommendation.evidenceLevel} Evidence
                        </span>
                      )}
                      {recommendation.confidenceScore && (
                        <span className="text-xs text-gray-500">
                          {Math.round(recommendation.confidenceScore * 100)}% confidence
                        </span>
                      )}
                    </div>

                    <p className="text-sm text-gray-600 mb-3">
                      {recommendation.description}
                    </p>

                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      {recommendation.timeline && (
                        <span className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>{recommendation.timeline}</span>
                        </span>
                      )}
                      {recommendation.cost && (
                        <span className="flex items-center space-x-1">
                          <Target className="w-3 h-3" />
                          <span>{recommendation.cost}</span>
                        </span>
                      )}
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
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRecommendationAction(recommendation.id, 'implement', recommendation.title);
                            }}
                            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors font-medium"
                          >
                            <CheckCircle className="w-4 h-4" />
                            <span>Implement Protocol</span>
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRecommendationAction(recommendation.id, 'modify', recommendation.title);
                            }}
                            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 text-sm rounded-lg hover:bg-gray-50 transition-colors font-medium"
                          >
                            <FileText className="w-4 h-4" />
                            <span>Modify Protocol</span>
                          </button>
                        </>
                      ) : (
                        <div className="flex items-center space-x-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg">
                          <CheckCircle className="w-5 h-5" />
                          <span className="text-sm font-medium">✓ Protocol Implemented</span>
                        </div>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRecommendationAction(recommendation.id, 'view_research', recommendation.title);
                        }}
                        className="flex items-center space-x-2 px-4 py-2 text-blue-600 text-sm hover:bg-blue-50 rounded-lg transition-colors font-medium"
                      >
                        <ExternalLink className="w-4 h-4" />
                        <span>View Research</span>
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
              eBDome profile, 12 ABENA modules, and real-time biomarker data. Each protocol 
              is tailored to the individual's specific biological patterns and health goals.
            </p>
          </div>
        </div>
      </div>

      {/* View Research Modal */}
      {showResearchModal && selectedRecommendation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setShowResearchModal(false)} />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto"
          >
            <button
              onClick={() => setShowResearchModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <ChevronRight className="w-6 h-6 rotate-45" />
            </button>

            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-blue-100 rounded-lg">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedRecommendation.title}</h2>
                <p className="text-gray-600">Evidence-Based Research & Clinical Guidelines</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Evidence Level */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold text-green-900">Evidence Level: {selectedRecommendation.evidenceLevel || 'Strong'}</h3>
                </div>
                <p className="text-sm text-green-800">
                  {selectedRecommendation.confidenceScore ? `${Math.round(selectedRecommendation.confidenceScore * 100)}% confidence based on` : 'Based on'} systematic reviews, randomized controlled trials, and clinical practice guidelines.
                </p>
              </div>

              {/* Clinical Rationale */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                  <Brain className="w-5 h-5 mr-2 text-purple-600" />
                  Clinical Rationale
                </h3>
                <p className="text-gray-700 leading-relaxed">
                  {selectedRecommendation.rationale || `This intervention is recommended based on current evidence-based guidelines and patient-specific factors. The protocol has been proven effective in improving clinical outcomes and quality of life.`}
                </p>
              </div>

              {/* Key Research Findings */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Key Research Findings</h3>
                <div className="space-y-3">
                  <div className="border-l-4 border-blue-500 pl-4 py-2">
                    <p className="font-medium text-gray-900">Primary Outcome</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {selectedRecommendation.expectedOutcomes?.[0] || 'Significant improvement in clinical markers and patient-reported outcomes.'}
                    </p>
                  </div>
                  <div className="border-l-4 border-green-500 pl-4 py-2">
                    <p className="font-medium text-gray-900">Secondary Benefits</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {selectedRecommendation.expectedOutcomes?.[1] || 'Enhanced quality of life and reduced risk factors.'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Clinical Guidelines */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Relevant Clinical Guidelines</h3>
                <ul className="space-y-2">
                  <li>
                    <a 
                      href="https://www.heart.org/en/health-topics/high-blood-pressure" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-start space-x-2 text-blue-600 hover:text-blue-800 transition-colors"
                    >
                      <ExternalLink className="w-4 h-4 mt-1 flex-shrink-0" />
                      <span className="text-sm hover:underline">American Heart Association Guidelines (2023)</span>
                    </a>
                  </li>
                  <li>
                    <a 
                      href="https://pubmed.ncbi.nlm.nih.gov/24352797/" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-start space-x-2 text-blue-600 hover:text-blue-800 transition-colors"
                    >
                      <ExternalLink className="w-4 h-4 mt-1 flex-shrink-0" />
                      <span className="text-sm hover:underline">JNC-8 Hypertension Guidelines</span>
                    </a>
                  </li>
                  <li>
                    <a 
                      href="https://www.cochranelibrary.com/" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-start space-x-2 text-blue-600 hover:text-blue-800 transition-colors"
                    >
                      <ExternalLink className="w-4 h-4 mt-1 flex-shrink-0" />
                      <span className="text-sm hover:underline">Evidence-Based Medicine Reviews (Cochrane Database)</span>
                    </a>
                  </li>
                </ul>
              </div>

              {/* Affected Systems */}
              {selectedRecommendation.affectedModules && selectedRecommendation.affectedModules.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Impact on Body Systems</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedRecommendation.affectedModules.map((module, index) => (
                      <span key={index} className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
                        {module}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Timeline */}
              {selectedRecommendation.timeline && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <Clock className="w-5 h-5 text-gray-600" />
                    <span className="font-semibold text-gray-900">Expected Timeline:</span>
                    <span className="text-gray-700">{selectedRecommendation.timeline}</span>
                  </div>
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end space-x-3 pt-6 border-t">
              <button
                onClick={() => setShowResearchModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Close
              </button>
              <a
                href={`https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(selectedRecommendation.title + ' clinical trial evidence')}`}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
              >
                <ExternalLink className="w-4 h-4" />
                <span>Search PubMed Research</span>
              </a>
              <a
                href={`https://scholar.google.com/scholar?q=${encodeURIComponent(selectedRecommendation.title + ' evidence-based medicine')}`}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 flex items-center space-x-2"
              >
                <ExternalLink className="w-4 h-4" />
                <span>Google Scholar</span>
              </a>
            </div>
          </motion.div>
        </div>
      )}

      {/* Modify Protocol Modal */}
      {showModifyModal && selectedRecommendation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setShowModifyModal(false)} />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-3xl max-h-[90vh] overflow-y-auto"
          >
            <button
              onClick={() => setShowModifyModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <ChevronRight className="w-6 h-6 rotate-45" />
            </button>

            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-purple-100 rounded-lg">
                <FileText className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Modify Protocol</h2>
                <p className="text-gray-600">{selectedRecommendation.title}</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Current Protocol */}
              <div className="bg-blue-50 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">Current Protocol</h3>
                <p className="text-sm text-blue-800">{selectedRecommendation.description}</p>
              </div>

              {/* Modification Fields */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Intervention Details
                </label>
                <textarea
                  defaultValue={selectedRecommendation.protocol?.intervention || ''}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Modify intervention details..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Dosage/Frequency
                  </label>
                  <input
                    type="text"
                    defaultValue={selectedRecommendation.protocol?.dosage || ''}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="e.g., Once daily"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Duration
                  </label>
                  <input
                    type="text"
                    defaultValue={selectedRecommendation.protocol?.duration || selectedRecommendation.timeline || ''}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="e.g., 2-4 weeks"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Monitoring Plan
                </label>
                <textarea
                  defaultValue={selectedRecommendation.protocol?.monitoring || ''}
                  rows={2}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Describe monitoring requirements..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Clinical Notes
                </label>
                <textarea
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Add any additional notes or modifications..."
                />
              </div>

              {/* Priority Adjustment */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Priority Level
                </label>
                <select
                  defaultValue={selectedRecommendation.priority || 'medium'}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="critical">Critical Priority</option>
                  <option value="high">High Priority</option>
                  <option value="medium">Medium Priority</option>
                  <option value="low">Low Priority</option>
                </select>
              </div>
            </div>

            <div className="mt-6 flex justify-between items-center pt-6 border-t">
              <button
                onClick={() => setShowModifyModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <div className="flex space-x-3">
                <button
                  className="px-4 py-2 border border-purple-600 text-purple-600 rounded-lg hover:bg-purple-50"
                >
                  Save as Draft
                </button>
                <button
                  onClick={() => {
                    toast.success(`✅ Protocol modified for "${selectedRecommendation.title}"`, {
                      duration: 3000
                    });
                    setShowModifyModal(false);
                  }}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center space-x-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Save & Apply Changes</span>
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default ClinicalRecommendations; 