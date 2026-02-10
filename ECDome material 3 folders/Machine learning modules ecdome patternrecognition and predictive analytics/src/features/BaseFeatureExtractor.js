/**
 * BASE FEATURE EXTRACTOR
 * Parent class for all module-specific feature extractors
 */
class BaseFeatureExtractor {
  constructor(moduleName) {
    this.moduleName = moduleName;
    this.featureCount = 12; // Each module contributes 12 features
  }

  /**
   * Extract features from module data
   * @param {Object} moduleData - Raw module data
   * @param {Object} ecbomeData - eCBome-specific data
   * @param {String} patientId - Patient identifier
   * @returns {Array} Array of normalized features
   */
  async extract(moduleData, ecbomeData, patientId) {
    // Override in specific extractors
    return new Array(this.featureCount).fill(0);
  }

  /**
   * Normalize a feature value to [0, 1] range
   * @param {Number} value - Raw feature value
   * @param {Number} min - Minimum expected value
   * @param {Number} max - Maximum expected value
   * @returns {Number} Normalized value between 0 and 1
   */
  normalizeFeature(value, min = 0, max = 1) {
    if (value === null || value === undefined || isNaN(value)) {
      return 0;
    }
    return Math.max(0, Math.min(1, (value - min) / (max - min)));
  }

  /**
   * Apply logarithmic scaling for features with wide ranges
   * @param {Number} value - Raw feature value
   * @param {Number} base - Logarithm base (default: 10)
   * @returns {Number} Log-scaled value
   */
  logScale(value, base = 10) {
    if (value <= 0) return 0;
    return Math.log(value) / Math.log(base);
  }

  /**
   * Calculate statistical features from time series data
   * @param {Array} timeSeries - Array of time series values
   * @returns {Object} Statistical features
   */
  calculateStatisticalFeatures(timeSeries) {
    if (!Array.isArray(timeSeries) || timeSeries.length === 0) {
      return {
        mean: 0,
        std: 0,
        min: 0,
        max: 0,
        trend: 0,
        variance: 0
      };
    }

    const mean = timeSeries.reduce((sum, val) => sum + val, 0) / timeSeries.length;
    const variance = timeSeries.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / timeSeries.length;
    const std = Math.sqrt(variance);
    const min = Math.min(...timeSeries);
    const max = Math.max(...timeSeries);
    
    // Calculate trend (simple linear regression slope)
    const n = timeSeries.length;
    const sumX = (n * (n + 1)) / 2;
    const sumY = timeSeries.reduce((sum, val) => sum + val, 0);
    const sumXY = timeSeries.reduce((sum, val, idx) => sum + val * (idx + 1), 0);
    const sumX2 = (n * (n + 1) * (2 * n + 1)) / 6;
    
    const trend = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);

    return {
      mean,
      std,
      min,
      max,
      trend: isNaN(trend) ? 0 : trend,
      variance
    };
  }

  /**
   * Calculate circadian rhythm features
   * @param {Array} timestampedData - Array of {timestamp, value} objects
   * @returns {Object} Circadian features
   */
  calculateCircadianFeatures(timestampedData) {
    if (!Array.isArray(timestampedData) || timestampedData.length === 0) {
      return {
        amplitude: 0,
        acrophase: 0,
        mesor: 0,
        robustness: 0
      };
    }

    // Group data by hour of day
    const hourlyData = {};
    timestampedData.forEach(item => {
      const hour = new Date(item.timestamp).getHours();
      if (!hourlyData[hour]) hourlyData[hour] = [];
      hourlyData[hour].push(item.value);
    });

    // Calculate mean for each hour
    const hourlyMeans = {};
    Object.keys(hourlyData).forEach(hour => {
      hourlyMeans[hour] = hourlyData[hour].reduce((sum, val) => sum + val, 0) / hourlyData[hour].length;
    });

    const values = Object.values(hourlyMeans);
    const amplitude = Math.max(...values) - Math.min(...values);
    const mesor = values.reduce((sum, val) => sum + val, 0) / values.length;
    
    // Find acrophase (time of peak)
    const maxValue = Math.max(...values);
    const acrophase = Object.keys(hourlyMeans).find(hour => hourlyMeans[hour] === maxValue);
    
    // Calculate robustness (consistency of rhythm)
    const robustness = 1 - (Math.sqrt(values.reduce((sum, val) => sum + Math.pow(val - mesor, 2), 0) / values.length) / amplitude);

    return {
      amplitude,
      acrophase: parseInt(acrophase) || 0,
      mesor,
      robustness: isNaN(robustness) ? 0 : Math.max(0, robustness)
    };
  }

  /**
   * Calculate correlation between two data series
   * @param {Array} series1 - First data series
   * @param {Array} series2 - Second data series
   * @returns {Number} Correlation coefficient
   */
  calculateCorrelation(series1, series2) {
    if (!Array.isArray(series1) || !Array.isArray(series2) || series1.length !== series2.length) {
      return 0;
    }

    const n = series1.length;
    const mean1 = series1.reduce((sum, val) => sum + val, 0) / n;
    const mean2 = series2.reduce((sum, val) => sum + val, 0) / n;

    let numerator = 0;
    let denominator1 = 0;
    let denominator2 = 0;

    for (let i = 0; i < n; i++) {
      const diff1 = series1[i] - mean1;
      const diff2 = series2[i] - mean2;
      numerator += diff1 * diff2;
      denominator1 += diff1 * diff1;
      denominator2 += diff2 * diff2;
    }

    const denominator = Math.sqrt(denominator1 * denominator2);
    return denominator === 0 ? 0 : numerator / denominator;
  }

  /**
   * Calculate ratio features safely
   * @param {Number} numerator - Numerator value
   * @param {Number} denominator - Denominator value
   * @param {Number} defaultValue - Default value if denominator is 0
   * @returns {Number} Ratio value
   */
  calculateRatio(numerator, denominator, defaultValue = 0) {
    if (denominator === 0 || isNaN(denominator) || isNaN(numerator)) {
      return defaultValue;
    }
    return numerator / denominator;
  }

  /**
   * Validate and sanitize input data
   * @param {*} data - Input data to validate
   * @param {*} defaultValue - Default value if invalid
   * @returns {*} Validated data
   */
  validateData(data, defaultValue = 0) {
    if (data === null || data === undefined || isNaN(data)) {
      return defaultValue;
    }
    return data;
  }

  /**
   * Extract temporal patterns from time series
   * @param {Array} timeSeries - Time series data
   * @returns {Object} Temporal pattern features
   */
  extractTemporalPatterns(timeSeries) {
    if (!Array.isArray(timeSeries) || timeSeries.length === 0) {
      return {
        stability: 0,
        volatility: 0,
        momentum: 0,
        cyclicality: 0
      };
    }

    const stats = this.calculateStatisticalFeatures(timeSeries);
    
    // Stability (inverse of coefficient of variation)
    const stability = stats.mean === 0 ? 0 : 1 / (stats.std / stats.mean);
    
    // Volatility (normalized standard deviation)
    const volatility = stats.std / (stats.max - stats.min || 1);
    
    // Momentum (recent trend strength)
    const recentData = timeSeries.slice(-Math.min(7, timeSeries.length));
    const recentStats = this.calculateStatisticalFeatures(recentData);
    const momentum = Math.abs(recentStats.trend);
    
    // Cyclicality (autocorrelation at different lags)
    const cyclicality = this.calculateAutocorrelation(timeSeries, 1);

    return {
      stability: this.normalizeFeature(stability, 0, 10),
      volatility: this.normalizeFeature(volatility, 0, 1),
      momentum: this.normalizeFeature(momentum, 0, 1),
      cyclicality: this.normalizeFeature(cyclicality, -1, 1)
    };
  }

  /**
   * Calculate autocorrelation at specific lag
   * @param {Array} series - Time series data
   * @param {Number} lag - Lag value
   * @returns {Number} Autocorrelation coefficient
   */
  calculateAutocorrelation(series, lag) {
    if (!Array.isArray(series) || series.length <= lag) {
      return 0;
    }

    const series1 = series.slice(0, -lag);
    const series2 = series.slice(lag);
    
    return this.calculateCorrelation(series1, series2);
  }
}

export { BaseFeatureExtractor };
export default BaseFeatureExtractor; 