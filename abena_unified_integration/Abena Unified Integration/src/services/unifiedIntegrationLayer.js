// Unified Integration Layer
// Central hub for integrating real-time correlation data across the eCDome system

class UnifiedIntegrationLayer {
  constructor() {
    this.correlationData = new Map();
    this.subscribers = new Map();
    this.dataHistory = [];
    this.maxHistorySize = 100;
  }

  // Add real-time correlations from various sources
  addRealTimeCorrelations(correlationData) {
    const { source, data, confidence, patterns } = correlationData;
    
    // Store correlation data
    this.correlationData.set(source, {
      data,
      confidence,
      patterns,
      timestamp: new Date().toISOString()
    });

    // Add to history
    this.dataHistory.push({
      source,
      data,
      confidence,
      patterns,
      timestamp: new Date().toISOString()
    });

    // Maintain history size
    if (this.dataHistory.length > this.maxHistorySize) {
      this.dataHistory.shift();
    }

    // Notify subscribers
    this.notifySubscribers(source, { data, confidence, patterns });

    console.log(`[UnifiedIntegrationLayer] Received correlation data from ${source}:`, {
      correlations: data?.correlations?.length || 0,
      confidence: confidence?.averageConfidence || 0,
      patterns: patterns?.patterns?.length || 0
    });
  }

  // Subscribe to correlation updates
  subscribe(source, callback) {
    if (!this.subscribers.has(source)) {
      this.subscribers.set(source, []);
    }
    this.subscribers.get(source).push(callback);
  }

  // Unsubscribe from correlation updates
  unsubscribe(source, callback) {
    if (this.subscribers.has(source)) {
      const callbacks = this.subscribers.get(source);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  // Notify subscribers of new data
  notifySubscribers(source, data) {
    if (this.subscribers.has(source)) {
      this.subscribers.get(source).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`[UnifiedIntegrationLayer] Error in subscriber callback:`, error);
        }
      });
    }
  }

  // Get correlation data for a specific source
  getCorrelationData(source) {
    return this.correlationData.get(source);
  }

  // Get all correlation data
  getAllCorrelationData() {
    return Object.fromEntries(this.correlationData);
  }

  // Get correlation history
  getCorrelationHistory(source = null) {
    if (source) {
      return this.dataHistory.filter(entry => entry.source === source);
    }
    return this.dataHistory;
  }

  // Get system-wide correlation summary
  getSystemCorrelationSummary() {
    const summary = {
      totalSources: this.correlationData.size,
      totalCorrelations: 0,
      averageConfidence: 0,
      systemHealth: 'healthy',
      sources: []
    };

    let totalConfidence = 0;
    let sourceCount = 0;

    this.correlationData.forEach((data, source) => {
      const sourceSummary = {
        source,
        correlations: data.data?.correlations?.length || 0,
        confidence: data.confidence?.averageConfidence || 0,
        patterns: data.patterns?.patterns?.length || 0,
        lastUpdate: data.timestamp
      };

      summary.sources.push(sourceSummary);
      summary.totalCorrelations += sourceSummary.correlations;
      totalConfidence += sourceSummary.confidence;
      sourceCount++;
    });

    summary.averageConfidence = sourceCount > 0 ? totalConfidence / sourceCount : 0;
    summary.systemHealth = summary.averageConfidence > 0.7 ? 'healthy' : 'degraded';

    return summary;
  }

  // Export correlation data for external systems
  exportCorrelationData(format = 'json') {
    const exportData = {
      timestamp: new Date().toISOString(),
      systemSummary: this.getSystemCorrelationSummary(),
      correlationData: this.getAllCorrelationData(),
      history: this.getCorrelationHistory()
    };

    switch (format) {
      case 'json':
        return JSON.stringify(exportData, null, 2);
      case 'csv':
        return this.convertToCSV(exportData);
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  }

  // Convert correlation data to CSV format
  convertToCSV(data) {
    const rows = [];
    
    // Header
    rows.push(['Timestamp', 'Source', 'Correlations', 'Average Confidence', 'Patterns', 'System Health']);
    
    // Data rows
    data.systemSummary.sources.forEach(source => {
      rows.push([
        source.lastUpdate,
        source.source,
        source.correlations,
        source.confidence.toFixed(3),
        source.patterns,
        data.systemSummary.systemHealth
      ]);
    });
    
    return rows.map(row => row.join(',')).join('\n');
  }

  // Reset integration layer
  reset() {
    this.correlationData.clear();
    this.subscribers.clear();
    this.dataHistory = [];
  }

  // Get integration layer status
  getStatus() {
    return {
      timestamp: new Date().toISOString(),
      activeSources: this.correlationData.size,
      totalSubscribers: Array.from(this.subscribers.values()).reduce((sum, callbacks) => sum + callbacks.length, 0),
      historySize: this.dataHistory.length,
      systemSummary: this.getSystemCorrelationSummary()
    };
  }

  // Module registry functions (required by React app)
  getModuleRegistry() {
    return {
      modules: [
        { id: 'ecdome-analysis', name: 'eCDome Analysis', status: 'active' },
        { id: 'clinical-workflow', name: 'Clinical Workflow', status: 'active' },
        { id: 'biomarker-integration', name: 'Biomarker Integration', status: 'active' },
        { id: 'ihr-system', name: 'IHR System', status: 'active' }
      ],
      totalModules: 4,
      activeModules: 4
    };
  }

  // Process module analytics (required by React app)
  processModuleAnalytics(moduleData) {
    try {
      const analytics = {
        timestamp: new Date().toISOString(),
        moduleId: moduleData?.id || 'unknown',
        performance: {
          responseTime: Math.random() * 100 + 50, // Mock data
          successRate: 0.95 + Math.random() * 0.05,
          errorRate: Math.random() * 0.05
        },
        usage: {
          requests: Math.floor(Math.random() * 1000) + 100,
          activeUsers: Math.floor(Math.random() * 50) + 10
        }
      };
      
      console.log(`[UnifiedIntegrationLayer] Processed analytics for module ${analytics.moduleId}:`, analytics);
      return analytics;
    } catch (error) {
      console.error('[UnifiedIntegrationLayer] Error processing module analytics:', error);
      return null;
    }
  }
}

// Create singleton instance
const unifiedIntegrationLayer = new UnifiedIntegrationLayer();

// Export for use across the system
export default unifiedIntegrationLayer;

// Export the class for testing
export { UnifiedIntegrationLayer }; 