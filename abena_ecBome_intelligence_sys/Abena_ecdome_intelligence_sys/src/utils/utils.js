import { receptorNetwork } from '../data/receptorNetwork';
import { drugInteractions, geneticPolymorphisms } from '../data/drugData';

export const calculateHealthScore = (metrics) => {
  const weights = {
    endocannabinoidLevels: 0.3,
    receptorActivity: 0.3,
    microbiomeHealth: 0.2,
    inflammationMarkers: 0.1,
    stressResponse: 0.1
  };

  let score = 0;
  
  // Calculate endocannabinoid levels score
  const ecLevels = Object.values(metrics.endocannabinoidLevels);
  const ecScore = ecLevels.reduce((sum, val) => sum + val, 0) / ecLevels.length;
  
  // Calculate receptor activity score
  const receptorActivity = Object.values(metrics.receptorActivity);
  const receptorScore = receptorActivity.reduce((sum, val) => sum + val, 0) / receptorActivity.length;
  
  // Calculate overall score
  score = (
    ecScore * weights.endocannabinoidLevels +
    receptorScore * weights.receptorActivity +
    metrics.microbiomeHealth * weights.microbiomeHealth +
    (1 - metrics.inflammationMarkers) * weights.inflammationMarkers +
    (1 - metrics.stressResponse) * weights.stressResponse
  ) * 100;

  return Math.round(score);
};

export const analyzeECBomeState = (metrics) => {
  const analysis = {
    status: 'Normal',
    recommendations: [],
    riskFactors: [],
    potentialInteractions: []
  };

  // Analyze endocannabinoid levels
  Object.entries(metrics.endocannabinoidLevels).forEach(([key, value]) => {
    if (value < 0.4) {
      analysis.recommendations.push(`Consider interventions to increase ${key} levels`);
      analysis.riskFactors.push(`Low ${key} levels may impact system function`);
    } else if (value > 0.9) {
      analysis.recommendations.push(`Monitor ${key} levels for potential excess`);
    }
  });

  // Analyze receptor activity
  Object.entries(metrics.receptorActivity).forEach(([key, value]) => {
    if (value < 0.4) {
      analysis.recommendations.push(`Consider strategies to enhance ${key} receptor activity`);
    } else if (value > 0.9) {
      analysis.recommendations.push(`Monitor ${key} receptor activity for potential overstimulation`);
    }
  });

  // Analyze microbiome health
  if (metrics.microbiomeHealth < 0.6) {
    analysis.recommendations.push('Consider probiotic supplementation and dietary modifications');
    analysis.riskFactors.push('Suboptimal microbiome health may affect endocannabinoid system function');
  }

  // Analyze inflammation markers
  if (metrics.inflammationMarkers > 0.7) {
    analysis.status = 'Elevated Inflammation';
    analysis.recommendations.push('Implement anti-inflammatory strategies');
    analysis.riskFactors.push('Elevated inflammation may impact system homeostasis');
  }

  // Analyze stress response
  if (metrics.stressResponse > 0.7) {
    analysis.status = 'Elevated Stress';
    analysis.recommendations.push('Implement stress management techniques');
    analysis.riskFactors.push('Elevated stress may affect endocannabinoid system function');
  }

  return analysis;
};

export const validatePatientData = (data) => {
  const requiredFields = ['id', 'age', 'gender', 'metrics'];
  const missingFields = requiredFields.filter(field => !data[field]);
  
  if (missingFields.length > 0) {
    throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
  }

  if (typeof data.age !== 'number' || data.age < 0 || data.age > 120) {
    throw new Error('Invalid age value');
  }

  if (!['Male', 'Female', 'Other'].includes(data.gender)) {
    throw new Error('Invalid gender value');
  }

  // Validate metrics
  const requiredMetrics = ['endocannabinoidLevels', 'receptorActivity', 'microbiomeHealth', 'inflammationMarkers', 'stressResponse'];
  const missingMetrics = requiredMetrics.filter(metric => !data.metrics[metric]);
  
  if (missingMetrics.length > 0) {
    throw new Error(`Missing required metrics: ${missingMetrics.join(', ')}`);
  }

  return true;
};

export const checkDrugInteractions = (currentMeds, cannabinoids) => {
  const interactions = [];
  
  currentMeds.forEach(med => {
    Object.entries(drugInteractions).forEach(([cannabinoid, data]) => {
      if (cannabinoids.includes(cannabinoid)) {
        data.interactions.forEach(interaction => {
          if (interaction.drug === med) {
            interactions.push({
              cannabinoid,
              medication: med,
              effect: interaction.effect,
              severity: interaction.severity
            });
          }
        });
      }
    });
  });

  return interactions;
};

export const analyzeGeneticProfile = (geneticData) => {
  const analysis = {
    polymorphisms: [],
    recommendations: [],
    riskFactors: []
  };

  Object.entries(geneticPolymorphisms).forEach(([gene, variants]) => {
    Object.entries(variants).forEach(([rsID, data]) => {
      if (geneticData[rsID]) {
        analysis.polymorphisms.push({
          gene,
          rsID,
          effect: data.effect,
          clinicalSignificance: data.clinicalSignificance
        });

        if (data.clinicalSignificance.includes('risk')) {
          analysis.riskFactors.push(`${gene} ${rsID} may affect treatment response`);
        }

        analysis.recommendations.push(`Consider ${gene} ${rsID} in treatment planning`);
      }
    });
  });

  return analysis;
};

export const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

export const calculateTrend = (data) => {
  if (data.length < 2) return 'Insufficient data';

  const firstValue = data[0];
  const lastValue = data[data.length - 1];
  const percentChange = ((lastValue - firstValue) / firstValue) * 100;

  if (percentChange > 10) return 'Significant increase';
  if (percentChange < -10) return 'Significant decrease';
  if (percentChange > 0) return 'Slight increase';
  if (percentChange < 0) return 'Slight decrease';
  return 'Stable';
};

export const processIntelligenceData = async (data) => {
  // Validate incoming data
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid data format received from intelligence layer');
  }

  // Process and normalize the data
  const processedData = {
    endocannabinoidLevels: normalizeEndocannabinoidLevels(data.endocannabinoidLevels),
    receptorActivity: normalizeReceptorActivity(data.receptorActivity),
    microbiomeHealth: normalizeMetric(data.microbiomeHealth),
    inflammationMarkers: normalizeMetric(data.inflammationMarkers),
    stressResponse: normalizeMetric(data.stressResponse)
  };

  // Perform real-time analysis
  const analysis = analyzeECBomeState(processedData);
  const healthScore = calculateHealthScore(processedData);

  return {
    ...processedData,
    analysis,
    healthScore,
    timestamp: new Date().toISOString()
  };
};

export const normalizeEndocannabinoidLevels = (levels) => {
  if (!levels) return {};
  
  return {
    anandamide: normalizeMetric(levels.anandamide),
    '2-AG': normalizeMetric(levels['2-AG']),
    PEA: normalizeMetric(levels.PEA),
    OEA: normalizeMetric(levels.OEA)
  };
};

export const normalizeReceptorActivity = (activity) => {
  if (!activity) return {};
  
  return {
    CB1: normalizeMetric(activity.CB1),
    CB2: normalizeMetric(activity.CB2),
    TRPV1: normalizeMetric(activity.TRPV1),
    GPR18: normalizeMetric(activity.GPR18)
  };
};

export const normalizeMetric = (value) => {
  if (typeof value !== 'number') return 0;
  return Math.max(0, Math.min(1, value));
};

export const detectAnomalies = (data) => {
  const anomalies = [];
  
  // Check for sudden changes in endocannabinoid levels
  Object.entries(data.endocannabinoidLevels).forEach(([key, value]) => {
    if (value > 0.9 || value < 0.1) {
      anomalies.push({
        type: 'endocannabinoid',
        metric: key,
        value,
        severity: value > 0.9 ? 'high' : 'low'
      });
    }
  });

  // Check for unusual receptor activity patterns
  Object.entries(data.receptorActivity).forEach(([key, value]) => {
    if (value > 0.9 || value < 0.1) {
      anomalies.push({
        type: 'receptor',
        metric: key,
        value,
        severity: value > 0.9 ? 'high' : 'low'
      });
    }
  });

  // Check for system health anomalies
  if (data.microbiomeHealth < 0.3) {
    anomalies.push({
      type: 'system',
      metric: 'microbiomeHealth',
      value: data.microbiomeHealth,
      severity: 'low'
    });
  }

  if (data.inflammationMarkers > 0.7) {
    anomalies.push({
      type: 'system',
      metric: 'inflammationMarkers',
      value: data.inflammationMarkers,
      severity: 'high'
    });
  }

  if (data.stressResponse > 0.7) {
    anomalies.push({
      type: 'system',
      metric: 'stressResponse',
      value: data.stressResponse,
      severity: 'high'
    });
  }

  return anomalies;
};

export const generateIntelligenceReport = (data, anomalies) => {
  return {
    timestamp: new Date().toISOString(),
    healthScore: calculateHealthScore(data),
    analysis: analyzeECBomeState(data),
    anomalies,
    recommendations: generateRecommendations(data, anomalies)
  };
};

export const generateRecommendations = (data, anomalies) => {
  const recommendations = [];

  // Add recommendations based on anomalies
  anomalies.forEach(anomaly => {
    switch (anomaly.type) {
      case 'endocannabinoid':
        recommendations.push(`Consider ${anomaly.severity === 'high' ? 'reducing' : 'increasing'} ${anomaly.metric} levels`);
        break;
      case 'receptor':
        recommendations.push(`Monitor ${anomaly.metric} receptor activity for potential ${anomaly.severity === 'high' ? 'overstimulation' : 'underactivity'}`);
        break;
      case 'system':
        if (anomaly.metric === 'microbiomeHealth') {
          recommendations.push('Implement probiotic supplementation and dietary modifications');
        } else if (anomaly.metric === 'inflammationMarkers') {
          recommendations.push('Consider anti-inflammatory interventions');
        } else if (anomaly.metric === 'stressResponse') {
          recommendations.push('Implement stress management techniques');
        }
        break;
    }
  });

  return recommendations;
}; 