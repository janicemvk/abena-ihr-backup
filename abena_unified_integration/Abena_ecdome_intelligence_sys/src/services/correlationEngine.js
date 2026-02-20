// eCDome Correlation Engine
// Advanced real-time correlation analysis for endocannabinoid system data

class ECDomeCorrelationEngine {
  constructor() {
    this.correlationData = new Map();
    this.patterns = new Map();
    this.confidenceScores = new Map();
    this.historicalData = [];
    this.maxHistorySize = 1000;
    this.correlationThreshold = 0.7;
    this.confidenceThreshold = 0.8;
  }

  // Add new data point to correlation analysis
  addDataPoint(timestamp, metrics) {
    const dataPoint = {
      timestamp,
      metrics: {
        endocannabinoidLevels: { ...metrics.endocannabinoidLevels },
        receptorActivity: { ...metrics.receptorActivity },
        systemHealth: {
          microbiomeHealth: metrics.microbiomeHealth,
          inflammationMarkers: metrics.inflammationMarkers,
          stressResponse: metrics.stressResponse
        }
      }
    };

    this.historicalData.push(dataPoint);
    
    // Maintain history size
    if (this.historicalData.length > this.maxHistorySize) {
      this.historicalData.shift();
    }

    // Update correlations
    this.updateCorrelations();
    
    return this.getRealtimeData();
  }

  // Calculate correlations between different metrics
  updateCorrelations() {
    if (this.historicalData.length < 10) return;

    const correlations = new Map();
    const patterns = new Map();
    const confidenceScores = new Map();

    // Get all metric names
    const allMetrics = this.getAllMetricNames();
    
    // Calculate pairwise correlations
    for (let i = 0; i < allMetrics.length; i++) {
      for (let j = i + 1; j < allMetrics.length; j++) {
        const metric1 = allMetrics[i];
        const metric2 = allMetrics[j];
        
        const correlation = this.calculatePearsonCorrelation(metric1, metric2);
        const confidence = this.calculateConfidence(metric1, metric2);
        
        if (Math.abs(correlation) >= this.correlationThreshold) {
          const key = `${metric1}_${metric2}`;
          correlations.set(key, {
            metric1,
            metric2,
            correlation,
            confidence,
            timestamp: new Date().toISOString(),
            type: this.getCorrelationType(metric1, metric2)
          });
          
          // Store pattern information
          patterns.set(key, this.identifyPattern(metric1, metric2));
          confidenceScores.set(key, confidence);
        }
      }
    }

    this.correlationData = correlations;
    this.patterns = patterns;
    this.confidenceScores = confidenceScores;
  }

  // Get all metric names from the data structure
  getAllMetricNames() {
    const metrics = [];
    
    // Endocannabinoid levels
    metrics.push('anandamide', '2-AG', 'PEA', 'OEA');
    
    // Endocannabinoid receptors
    metrics.push('CB1', 'CB2', 'TRPV1', 'GPR18');
    
    // PPAR receptors
    metrics.push('PPARα', 'PPARγ', 'PPARδ');
    
    // 5-HT receptors
    metrics.push('5-HT1A', '5-HT2A', '5-HT3', '5-HT4', '5-HT6', '5-HT7');
    
    // Dopamine receptors
    metrics.push('D1', 'D2', 'D3', 'D4', 'D5');
    
    // Adrenergic receptors
    metrics.push('α1A', 'α1B', 'α1D', 'α2A', 'α2B', 'α2C', 'β1', 'β2', 'β3');
    
    // System health metrics
    metrics.push('microbiomeHealth', 'inflammationMarkers', 'stressResponse');
    
    return metrics;
  }

  // Calculate Pearson correlation coefficient
  calculatePearsonCorrelation(metric1, metric2) {
    const values1 = this.getMetricValues(metric1);
    const values2 = this.getMetricValues(metric2);
    
    if (values1.length !== values2.length || values1.length < 5) {
      return 0;
    }

    const n = values1.length;
    const sum1 = values1.reduce((a, b) => a + b, 0);
    const sum2 = values2.reduce((a, b) => a + b, 0);
    const sum1Sq = values1.reduce((a, b) => a + b * b, 0);
    const sum2Sq = values2.reduce((a, b) => a + b * b, 0);
    const pSum = values1.reduce((a, b, i) => a + b * values2[i], 0);
    
    const num = pSum - (sum1 * sum2 / n);
    const den = Math.sqrt((sum1Sq - sum1 * sum1 / n) * (sum2Sq - sum2 * sum2 / n));
    
    return den === 0 ? 0 : num / den;
  }

  // Get values for a specific metric
  getMetricValues(metricName) {
    return this.historicalData.map(dataPoint => {
      if (metricName === 'microbiomeHealth' || metricName === 'inflammationMarkers' || metricName === 'stressResponse') {
        return dataPoint.metrics.systemHealth[metricName];
      } else if (['anandamide', '2-AG', 'PEA', 'OEA'].includes(metricName)) {
        return dataPoint.metrics.endocannabinoidLevels[metricName];
      } else {
        return dataPoint.metrics.receptorActivity[metricName];
      }
    }).filter(val => val !== undefined && !isNaN(val));
  }

  // Calculate confidence score for correlation
  calculateConfidence(metric1, metric2) {
    const values1 = this.getMetricValues(metric1);
    const values2 = this.getMetricValues(metric2);
    
    if (values1.length < 10 || values2.length < 10) {
      return 0.5; // Low confidence for insufficient data
    }

    // Calculate confidence based on data quality and consistency
    const variance1 = this.calculateVariance(values1);
    const variance2 = this.calculateVariance(values2);
    const dataQuality = Math.min(1, values1.length / 50); // Higher confidence with more data
    
    // Lower variance indicates more consistent data
    const consistency = 1 - Math.min(1, (variance1 + variance2) / 2);
    
    return Math.min(1, (dataQuality + consistency) / 2);
  }

  // Calculate variance
  calculateVariance(values) {
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    return values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
  }

  // Identify correlation type based on metric categories
  getCorrelationType(metric1, metric2) {
    const endocannabinoids = ['anandamide', '2-AG', 'PEA', 'OEA'];
    const endocannabinoidReceptors = ['CB1', 'CB2', 'TRPV1', 'GPR18'];
    const pparReceptors = ['PPARα', 'PPARγ', 'PPARδ'];
    const serotoninReceptors = ['5-HT1A', '5-HT2A', '5-HT3', '5-HT4', '5-HT6', '5-HT7'];
    const dopamineReceptors = ['D1', 'D2', 'D3', 'D4', 'D5'];
    const adrenergicReceptors = ['α1A', 'α1B', 'α1D', 'α2A', 'α2B', 'α2C', 'β1', 'β2', 'β3'];
    const systemHealth = ['microbiomeHealth', 'inflammationMarkers', 'stressResponse'];

    if (endocannabinoids.includes(metric1) && endocannabinoidReceptors.includes(metric2)) {
      return 'endocannabinoid_receptor';
    } else if (endocannabinoids.includes(metric1) && pparReceptors.includes(metric2)) {
      return 'endocannabinoid_ppar';
    } else if (serotoninReceptors.includes(metric1) && dopamineReceptors.includes(metric2)) {
      return 'neurotransmitter_cross';
    } else if (adrenergicReceptors.includes(metric1) && adrenergicReceptors.includes(metric2)) {
      return 'adrenergic_internal';
    } else if (systemHealth.includes(metric1) || systemHealth.includes(metric2)) {
      return 'system_health';
    } else {
      return 'cross_system';
    }
  }

  // Identify patterns in correlated metrics
  identifyPattern(metric1, metric2) {
    const values1 = this.getMetricValues(metric1);
    const values2 = this.getMetricValues(metric2);
    
    if (values1.length < 10 || values2.length < 10) {
      return { type: 'insufficient_data', description: 'Not enough data for pattern analysis' };
    }

    // Calculate trend patterns
    const trend1 = this.calculateTrend(values1);
    const trend2 = this.calculateTrend(values2);
    
    // Check for synchronous patterns
    const isSynchronous = this.checkSynchronousPattern(values1, values2);
    
    // Check for lagged patterns
    const lagPattern = this.checkLaggedPattern(values1, values2);
    
    return {
      type: 'correlation_pattern',
      synchronous: isSynchronous,
      lagged: lagPattern,
      trend1,
      trend2,
      description: this.generatePatternDescription(trend1, trend2, isSynchronous, lagPattern, metric1, metric2)
    };
  }

  // Calculate trend direction
  calculateTrend(values) {
    const recent = values.slice(-5);
    const older = values.slice(-10, -5);
    
    if (recent.length === 0 || older.length === 0) {
      return 'stable';
    }
    
    const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
    const olderAvg = older.reduce((a, b) => a + b, 0) / older.length;
    
    const change = ((recentAvg - olderAvg) / olderAvg) * 100;
    
    if (Math.abs(change) < 5) return 'stable';
    return change > 0 ? 'increasing' : 'decreasing';
  }

  // Check for synchronous patterns
  checkSynchronousPattern(values1, values2) {
    const recent1 = values1.slice(-10);
    const recent2 = values2.slice(-10);
    
    if (recent1.length !== recent2.length) return false;
    
    // Check if both metrics move in the same direction
    const directionChanges1 = this.getDirectionChanges(recent1);
    const directionChanges2 = this.getDirectionChanges(recent2);
    
    const matchingDirections = directionChanges1.filter((change, index) => 
      directionChanges2[index] === change
    ).length;
    
    return matchingDirections / directionChanges1.length > 0.7;
  }

  // Get direction changes in a series
  getDirectionChanges(values) {
    const changes = [];
    for (let i = 1; i < values.length; i++) {
      if (values[i] > values[i-1]) {
        changes.push('up');
      } else if (values[i] < values[i-1]) {
        changes.push('down');
      } else {
        changes.push('stable');
      }
    }
    return changes;
  }

  // Check for lagged patterns
  checkLaggedPattern(values1, values2) {
    const maxLag = 5;
    let bestLag = 0;
    let bestCorrelation = 0;
    
    for (let lag = 1; lag <= maxLag; lag++) {
      const lagged1 = values1.slice(0, -lag);
      const lagged2 = values2.slice(lag);
      
      if (lagged1.length < 5 || lagged2.length < 5) continue;
      
      const correlation = this.calculatePearsonCorrelationArrays(lagged1, lagged2);
      if (Math.abs(correlation) > Math.abs(bestCorrelation)) {
        bestCorrelation = correlation;
        bestLag = lag;
      }
    }
    
    return Math.abs(bestCorrelation) > 0.6 ? {
      lag: bestLag,
      correlation: bestCorrelation,
      direction: bestCorrelation > 0 ? 'positive' : 'negative'
    } : null;
  }

  // Calculate correlation between two arrays
  calculatePearsonCorrelationArrays(arr1, arr2) {
    const n = Math.min(arr1.length, arr2.length);
    if (n < 5) return 0;
    
    const sum1 = arr1.slice(0, n).reduce((a, b) => a + b, 0);
    const sum2 = arr2.slice(0, n).reduce((a, b) => a + b, 0);
    const sum1Sq = arr1.slice(0, n).reduce((a, b) => a + b * b, 0);
    const sum2Sq = arr2.slice(0, n).reduce((a, b) => a + b * b, 0);
    const pSum = arr1.slice(0, n).reduce((a, b, i) => a + b * arr2[i], 0);
    
    const num = pSum - (sum1 * sum2 / n);
    const den = Math.sqrt((sum1Sq - sum1 * sum1 / n) * (sum2Sq - sum2 * sum2 / n));
    
    return den === 0 ? 0 : num / den;
  }

  // Generate pattern description
  generatePatternDescription(trend1, trend2, synchronous, lagPattern, metric1, metric2) {
    let description = `Trends: ${metric1} is ${trend1}, ${metric2} is ${trend2}. `;
    
    if (synchronous) {
      description += 'Metrics show synchronous movement patterns. ';
    }
    
    if (lagPattern) {
      description += `${metric1} leads ${metric2} by ${lagPattern.lag} time periods with ${lagPattern.direction} correlation. `;
    }
    
    return description;
  }

  // Get real-time correlation data
  getRealtimeData() {
    const correlations = Array.from(this.correlationData.values());
    
    return {
      timestamp: new Date().toISOString(),
      correlations: correlations.map(corr => ({
        ...corr,
        pattern: this.patterns.get(`${corr.metric1}_${corr.metric2}`),
        significance: this.calculateSignificance(corr.correlation, corr.confidence)
      })),
      summary: {
        totalCorrelations: correlations.length,
        strongCorrelations: correlations.filter(c => Math.abs(c.correlation) > 0.8).length,
        highConfidence: correlations.filter(c => c.confidence > 0.9).length,
        systemHealth: this.assessSystemHealth()
      }
    };
  }

  // Calculate significance of correlation
  calculateSignificance(correlation, confidence) {
    const strength = Math.abs(correlation);
    const significance = (strength * 0.6) + (confidence * 0.4);
    
    if (significance > 0.9) return 'very_high';
    if (significance > 0.8) return 'high';
    if (significance > 0.7) return 'medium';
    if (significance > 0.6) return 'low';
    return 'very_low';
  }

  // Assess overall system health based on correlations
  assessSystemHealth() {
    const correlations = Array.from(this.correlationData.values());
    
    // Count correlations by type
    const typeCounts = {};
    correlations.forEach(corr => {
      typeCounts[corr.type] = (typeCounts[corr.type] || 0) + 1;
    });
    
    // Calculate health score
    const expectedCorrelations = {
      endocannabinoid_receptor: 4,
      endocannabinoid_ppar: 3,
      neurotransmitter_cross: 5,
      adrenergic_internal: 6,
      system_health: 3,
      cross_system: 8
    };
    
    let healthScore = 0;
    let totalExpected = 0;
    
    Object.entries(expectedCorrelations).forEach(([type, expected]) => {
      const actual = typeCounts[type] || 0;
      const ratio = Math.min(actual / expected, 1);
      healthScore += ratio;
      totalExpected += 1;
    });
    
    return {
      score: healthScore / totalExpected,
      status: healthScore / totalExpected > 0.7 ? 'healthy' : 'degraded',
      typeDistribution: typeCounts
    };
  }

  // Get confidence scores
  getConfidence() {
    return {
      timestamp: new Date().toISOString(),
      scores: Array.from(this.confidenceScores.entries()).map(([key, score]) => ({
        correlation: key,
        confidence: score,
        level: score > 0.9 ? 'very_high' : score > 0.8 ? 'high' : score > 0.7 ? 'medium' : 'low'
      })),
      averageConfidence: Array.from(this.confidenceScores.values()).reduce((a, b) => a + b, 0) / this.confidenceScores.size
    };
  }

  // Get identified patterns
  getPatterns() {
    return {
      timestamp: new Date().toISOString(),
      patterns: Array.from(this.patterns.entries()).map(([key, pattern]) => ({
        correlation: key,
        pattern: pattern,
        complexity: this.calculatePatternComplexity(pattern)
      })),
      patternTypes: this.analyzePatternTypes()
    };
  }

  // Calculate pattern complexity
  calculatePatternComplexity(pattern) {
    if (pattern.type === 'insufficient_data') return 0;
    
    let complexity = 1;
    if (pattern.synchronous) complexity += 1;
    if (pattern.lagged) complexity += 2;
    if (pattern.trend1 !== 'stable' || pattern.trend2 !== 'stable') complexity += 1;
    
    return Math.min(complexity, 5);
  }

  // Analyze pattern types
  analyzePatternTypes() {
    const patterns = Array.from(this.patterns.values());
    const types = {
      synchronous: 0,
      lagged: 0,
      trending: 0,
      stable: 0
    };
    
    patterns.forEach(pattern => {
      if (pattern.type === 'insufficient_data') return;
      if (pattern.synchronous) types.synchronous++;
      if (pattern.lagged) types.lagged++;
      if (pattern.trend1 !== 'stable' || pattern.trend2 !== 'stable') types.trending++;
      else types.stable++;
    });
    
    return types;
  }

  // Reset correlation engine
  reset() {
    this.correlationData.clear();
    this.patterns.clear();
    this.confidenceScores.clear();
    this.historicalData = [];
  }

  // Get engine status
  getStatus() {
    return {
      timestamp: new Date().toISOString(),
      dataPoints: this.historicalData.length,
      activeCorrelations: this.correlationData.size,
      patterns: this.patterns.size,
      averageConfidence: this.getConfidence().averageConfidence,
      systemHealth: this.assessSystemHealth()
    };
  }
}

// Create singleton instance
const eCDomeCorrelationEngine = new ECDomeCorrelationEngine();

// Export for integration with main system
export default eCDomeCorrelationEngine;

// Integration function for feeding data to main system
export const feedCorrelationDataToMainSystem = (unifiedIntegrationLayer) => {
  if (unifiedIntegrationLayer && typeof unifiedIntegrationLayer.addRealTimeCorrelations === 'function') {
    unifiedIntegrationLayer.addRealTimeCorrelations({
      source: 'eCDomeCorrelationEngine',
      data: eCDomeCorrelationEngine.getRealtimeData(),
      confidence: eCDomeCorrelationEngine.getConfidence(),
      patterns: eCDomeCorrelationEngine.getPatterns()
    });
  }
}; 