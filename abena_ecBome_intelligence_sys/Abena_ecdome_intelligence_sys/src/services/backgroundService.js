import { ihrIntelligenceService, labResultsService } from './api';

class BackgroundService {
  constructor() {
    this.isRunning = false;
    this.processes = new Map();
    this.healthCheckInterval = null;
    this.dataCollectionInterval = null;
    this.analysisInterval = null;
  }

  // Start all background processes
  start() {
    if (this.isRunning) {
      console.warn('Background service is already running');
      return;
    }

    console.log('Starting IHR Background Service...');
    this.isRunning = true;

    // Start health monitoring
    this.startHealthMonitoring();
    
    // Start data collection
    this.startDataCollection();
    
    // Start continuous analysis
    this.startContinuousAnalysis();

    console.log('IHR Background Service started successfully');
  }

  // Stop all background processes
  stop() {
    if (!this.isRunning) {
      console.warn('Background service is not running');
      return;
    }

    console.log('Stopping IHR Background Service...');
    this.isRunning = false;

    // Clear all intervals
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    if (this.dataCollectionInterval) {
      clearInterval(this.dataCollectionInterval);
    }
    if (this.analysisInterval) {
      clearInterval(this.analysisInterval);
    }

    console.log('IHR Background Service stopped');
  }

  // Health monitoring process
  startHealthMonitoring() {
    this.healthCheckInterval = setInterval(async () => {
      try {
        // Check IHR intelligence service health
        const ihrHealth = await this.checkIHRHealth();
        
        // Check lab results service health
        const labHealth = await this.checkLabHealth();
        
        // Update process status
        this.updateProcessStatus('healthMonitoring', {
          isRunning: true,
          lastUpdate: new Date().toISOString(),
          status: 'healthy',
          details: {
            ihr: ihrHealth,
            lab: labHealth
          }
        });

      } catch (error) {
        console.error('Health monitoring error:', error);
        this.updateProcessStatus('healthMonitoring', {
          isRunning: true,
          lastUpdate: new Date().toISOString(),
          status: 'error',
          error: error.message
        });
      }
    }, 30000); // Every 30 seconds
  }

  // Data collection process
  startDataCollection() {
    this.dataCollectionInterval = setInterval(async () => {
      try {
        // Collect real-time metrics from IHR
        const metrics = await this.collectRealTimeMetrics();
        
        // Store collected data
        this.storeCollectedData(metrics);
        
        // Update process status
        this.updateProcessStatus('dataCollection', {
          isRunning: true,
          lastUpdate: new Date().toISOString(),
          status: 'collecting',
          dataPoints: metrics.length
        });

      } catch (error) {
        console.error('Data collection error:', error);
        this.updateProcessStatus('dataCollection', {
          isRunning: true,
          lastUpdate: new Date().toISOString(),
          status: 'error',
          error: error.message
        });
      }
    }, 60000); // Every minute
  }

  // Continuous analysis process
  startContinuousAnalysis() {
    this.analysisInterval = setInterval(async () => {
      try {
        // Perform continuous eCBome analysis
        const analysis = await this.performContinuousAnalysis();
        
        // Update process status
        this.updateProcessStatus('continuousAnalysis', {
          isRunning: true,
          lastUpdate: new Date().toISOString(),
          status: 'analyzing',
          insights: analysis.insights?.length || 0
        });

      } catch (error) {
        console.error('Continuous analysis error:', error);
        this.updateProcessStatus('continuousAnalysis', {
          isRunning: true,
          lastUpdate: new Date().toISOString(),
          status: 'error',
          error: error.message
        });
      }
    }, 120000); // Every 2 minutes
  }

  // Check IHR health
  async checkIHRHealth() {
    try {
      const response = await ihrIntelligenceService.getRealTimeMetrics('SYSTEM_HEALTH');
      return {
        status: 'healthy',
        responseTime: Date.now(),
        data: response
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message,
        responseTime: Date.now()
      };
    }
  }

  // Check lab health
  async checkLabHealth() {
    try {
      const response = await labResultsService.getEndocannabinoidLevels('SYSTEM_HEALTH');
      return {
        status: 'healthy',
        responseTime: Date.now(),
        data: response
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        error: error.message,
        responseTime: Date.now()
      };
    }
  }

  // Collect real-time metrics
  async collectRealTimeMetrics() {
    const metrics = [];
    
    try {
      // Collect from multiple sources
      const ihrMetrics = await ihrIntelligenceService.getRealTimeMetrics('ALL');
      const labMetrics = await labResultsService.getEndocannabinoidLevels('ALL');
      
      metrics.push({
        source: 'ihr',
        timestamp: new Date().toISOString(),
        data: ihrMetrics
      });
      
      metrics.push({
        source: 'lab',
        timestamp: new Date().toISOString(),
        data: labMetrics
      });
      
    } catch (error) {
      console.error('Error collecting metrics:', error);
    }
    
    return metrics;
  }

  // Store collected data
  storeCollectedData(metrics) {
    try {
      // Store in localStorage for persistence
      const existingData = JSON.parse(localStorage.getItem('ihrBackgroundData') || '[]');
      const newData = [...existingData, ...metrics];
      
      // Keep only last 1000 data points
      if (newData.length > 1000) {
        newData.splice(0, newData.length - 1000);
      }
      
      localStorage.setItem('ihrBackgroundData', JSON.stringify(newData));
    } catch (error) {
      console.error('Error storing collected data:', error);
    }
  }

  // Perform continuous analysis
  async performContinuousAnalysis() {
    try {
      // Get recent data
      const recentData = JSON.parse(localStorage.getItem('ihrBackgroundData') || '[]');
      
      if (recentData.length === 0) {
        return { insights: [] };
      }
      
      // Analyze recent data for trends and anomalies
      const insights = this.analyzeDataForInsights(recentData);
      
      // Store analysis results
      this.storeAnalysisResults(insights);
      
      return { insights };
      
    } catch (error) {
      console.error('Error performing continuous analysis:', error);
      return { insights: [], error: error.message };
    }
  }

  // Analyze data for insights
  analyzeDataForInsights(data) {
    const insights = [];
    
    try {
      // Group data by source
      const ihrData = data.filter(d => d.source === 'ihr');
      const labData = data.filter(d => d.source === 'lab');
      
      // Analyze trends
      if (ihrData.length > 5) {
        const trends = this.calculateTrends(ihrData);
        if (trends.length > 0) {
          insights.push({
            type: 'trend',
            source: 'ihr',
            data: trends,
            timestamp: new Date().toISOString()
          });
        }
      }
      
      // Detect anomalies
      if (labData.length > 5) {
        const anomalies = this.detectAnomalies(labData);
        if (anomalies.length > 0) {
          insights.push({
            type: 'anomaly',
            source: 'lab',
            data: anomalies,
            timestamp: new Date().toISOString()
          });
        }
      }
      
    } catch (error) {
      console.error('Error analyzing data for insights:', error);
    }
    
    return insights;
  }

  // Calculate trends
  calculateTrends(data) {
    const trends = [];
    
    try {
      // Simple trend calculation based on recent vs older data
      const recent = data.slice(-5);
      const older = data.slice(-10, -5);
      
      if (recent.length > 0 && older.length > 0) {
        // Calculate average values and compare for multiple metrics
        const metrics = [
          'anandamide',
          'PPARα',
          'PPARγ',
          '5-HT1A',
          '5-HT2A',
          'D1',
          'D2',
          'β1',
          'α2A'
        ];
        
        metrics.forEach(metric => {
          let recentAvg, olderAvg;
          
          if (metric === 'anandamide') {
            recentAvg = recent.reduce((sum, item) => sum + (item.data?.metrics?.endocannabinoidLevels?.anandamide || 0), 0) / recent.length;
            olderAvg = older.reduce((sum, item) => sum + (item.data?.metrics?.endocannabinoidLevels?.anandamide || 0), 0) / older.length;
          } else {
            recentAvg = recent.reduce((sum, item) => sum + (item.data?.metrics?.receptorActivity?.[metric] || 0), 0) / recent.length;
            olderAvg = older.reduce((sum, item) => sum + (item.data?.metrics?.receptorActivity?.[metric] || 0), 0) / older.length;
          }
          
          if (Math.abs(recentAvg - olderAvg) > 0.1) {
            trends.push({
              metric: metric,
              change: ((recentAvg - olderAvg) / olderAvg) * 100,
              direction: recentAvg > olderAvg ? 'increasing' : 'decreasing'
            });
          }
        });
      }
    } catch (error) {
      console.error('Error calculating trends:', error);
    }
    
    return trends;
  }

  // Detect anomalies
  detectAnomalies(data) {
    const anomalies = [];
    
    try {
      // Anomaly detection for multiple metrics
      const metrics = [
        'anandamide',
        'PPARα',
        'PPARγ',
        '5-HT1A',
        '5-HT2A',
        'D1',
        'D2',
        'β1',
        'α2A'
      ];
      
      metrics.forEach(metric => {
        let values;
        
        if (metric === 'anandamide') {
          values = data.map(item => item.data?.metrics?.endocannabinoidLevels?.anandamide || 0);
        } else {
          values = data.map(item => item.data?.metrics?.receptorActivity?.[metric] || 0);
        }
        
        if (values.length > 5) {
          const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
          const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
          const stdDev = Math.sqrt(variance);
          
          values.forEach((value, index) => {
            if (Math.abs(value - mean) > 2 * stdDev) {
              anomalies.push({
                metric: metric,
                index,
                value,
                expected: mean,
                deviation: Math.abs(value - mean) / stdDev
              });
            }
          });
        }
      });
    } catch (error) {
      console.error('Error detecting anomalies:', error);
    }
    
    return anomalies;
  }

  // Store analysis results
  storeAnalysisResults(insights) {
    try {
      const existingInsights = JSON.parse(localStorage.getItem('ihrAnalysisInsights') || '[]');
      const newInsights = [...existingInsights, ...insights];
      
      // Keep only last 100 insights
      if (newInsights.length > 100) {
        newInsights.splice(0, newInsights.length - 100);
      }
      
      localStorage.setItem('ihrAnalysisInsights', JSON.stringify(newInsights));
    } catch (error) {
      console.error('Error storing analysis results:', error);
    }
  }

  // Update process status
  updateProcessStatus(processName, status) {
    this.processes.set(processName, status);
    
    // Emit status update event
    const event = new CustomEvent('ihrBackgroundStatusUpdate', {
      detail: {
        processName,
        status,
        allProcesses: Object.fromEntries(this.processes)
      }
    });
    window.dispatchEvent(event);
  }

  // Get all process statuses
  getProcessStatuses() {
    return Object.fromEntries(this.processes);
  }

  // Get specific process status
  getProcessStatus(processName) {
    return this.processes.get(processName);
  }
}

// Create singleton instance
const backgroundService = new BackgroundService();

export default backgroundService; 