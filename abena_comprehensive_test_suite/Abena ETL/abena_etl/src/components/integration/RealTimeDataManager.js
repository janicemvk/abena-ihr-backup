/**
 * Real-Time Data Manager for Abena IHR Frontend Integration
 * Handles WebSocket connections, real-time data streams, and state synchronization
 * This is separate from the Python backend integration system
 */

export class RealTimeDataManager {
  constructor() {
    this.connections = new Map();
    this.streams = new Map();
    this.listeners = new Map();
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  // Initialize WebSocket connections for real-time data
  initializeConnections(endpoints) {
    endpoints.forEach(endpoint => {
      this.createConnection(endpoint);
    });
  }

  createConnection(endpoint) {
    try {
      // In a real implementation, this would be actual WebSocket connections
      // For now, we'll simulate with intervals
      const connection = {
        endpoint,
        status: 'connected',
        lastHeartbeat: new Date(),
        dataBuffer: [],
        listeners: []
      };

      this.connections.set(endpoint, connection);
      this.startDataSimulation(endpoint);
      
      return connection;
    } catch (error) {
      console.error(`Failed to create connection to ${endpoint}:`, error);
      return null;
    }
  }

  // Simulate real-time data streams
  startDataSimulation(endpoint) {
    const interval = setInterval(() => {
      const connection = this.connections.get(endpoint);
      if (!connection) {
        clearInterval(interval);
        return;
      }

      // Generate simulated data based on endpoint type
      const data = this.generateSimulatedData(endpoint);
      this.processIncomingData(endpoint, data);
    }, 1000 + Math.random() * 4000); // Random intervals between 1-5 seconds

    // Store interval reference for cleanup
    const connection = this.connections.get(endpoint);
    if (connection) {
      connection.interval = interval;
    }
  }

  generateSimulatedData(endpoint) {
    const timestamp = new Date();
    
    switch (endpoint) {
      case 'heart-rate':
        return {
          timestamp,
          heartRate: 65 + Math.floor(Math.random() * 25),
          hrv: 35 + Math.floor(Math.random() * 20),
          stress: Math.random() > 0.7 ? 'elevated' : 'normal'
        };
        
      case 'glucose':
        return {
          timestamp,
          glucose: 80 + Math.floor(Math.random() * 40),
          trend: ['rising', 'stable', 'falling'][Math.floor(Math.random() * 3)],
          timeInRange: 70 + Math.floor(Math.random() * 25)
        };
        
      case 'sleep':
        return {
          timestamp,
          sleepStage: ['wake', 'light', 'deep', 'rem'][Math.floor(Math.random() * 4)],
          efficiency: 75 + Math.floor(Math.random() * 20),
          duration: 6.5 + Math.random() * 2
        };
        
      case 'ecdome':
        return {
          timestamp,
          aeaLevel: 0.2 + Math.random() * 0.4,
          cb1Activity: 70 + Math.floor(Math.random() * 25),
          balance: 80 + Math.floor(Math.random() * 20),
          inflammation: Math.random() > 0.6 ? 'elevated' : 'normal'
        };
        
      default:
        return {
          timestamp,
          value: Math.random() * 100,
          status: 'active'
        };
    }
  }

  processIncomingData(endpoint, data) {
    const connection = this.connections.get(endpoint);
    if (!connection) return;

    // Add to buffer (keep last 100 data points)
    connection.dataBuffer.push(data);
    if (connection.dataBuffer.length > 100) {
      connection.dataBuffer.shift();
    }

    // Update last heartbeat
    connection.lastHeartbeat = new Date();

    // Notify listeners
    this.notifyListeners(endpoint, data);
  }

  // Subscribe to data stream
  subscribe(endpoint, callback) {
    if (!this.listeners.has(endpoint)) {
      this.listeners.set(endpoint, []);
    }
    
    this.listeners.get(endpoint).push(callback);
    
    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(endpoint);
      if (listeners) {
        const index = listeners.indexOf(callback);
        if (index > -1) {
          listeners.splice(index, 1);
        }
      }
    };
  }

  notifyListeners(endpoint, data) {
    const listeners = this.listeners.get(endpoint);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in listener for ${endpoint}:`, error);
        }
      });
    }
  }

  // Get latest data for an endpoint
  getLatestData(endpoint) {
    const connection = this.connections.get(endpoint);
    if (!connection || connection.dataBuffer.length === 0) {
      return null;
    }
    
    return connection.dataBuffer[connection.dataBuffer.length - 1];
  }

  // Get historical data for an endpoint
  getHistoricalData(endpoint, count = 10) {
    const connection = this.connections.get(endpoint);
    if (!connection) return [];
    
    return connection.dataBuffer.slice(-count);
  }

  // Connection status monitoring
  getConnectionStatus() {
    const status = {};
    
    this.connections.forEach((connection, endpoint) => {
      const timeSinceHeartbeat = new Date() - connection.lastHeartbeat;
      status[endpoint] = {
        connected: timeSinceHeartbeat < 10000, // 10 seconds timeout
        lastSeen: connection.lastHeartbeat,
        dataPoints: connection.dataBuffer.length
      };
    });
    
    return status;
  }

  // Cleanup
  disconnect(endpoint) {
    const connection = this.connections.get(endpoint);
    if (connection && connection.interval) {
      clearInterval(connection.interval);
    }
    
    this.connections.delete(endpoint);
    this.listeners.delete(endpoint);
  }

  disconnectAll() {
    this.connections.forEach((connection, endpoint) => {
      this.disconnect(endpoint);
    });
  }

  // Export data for analysis
  exportData(endpoint, format = 'json') {
    const connection = this.connections.get(endpoint);
    if (!connection) return null;
    
    const data = {
      endpoint,
      exportTime: new Date().toISOString(),
      dataPoints: connection.dataBuffer,
      summary: {
        totalPoints: connection.dataBuffer.length,
        timeRange: {
          start: connection.dataBuffer[0]?.timestamp,
          end: connection.dataBuffer[connection.dataBuffer.length - 1]?.timestamp
        }
      }
    };
    
    if (format === 'csv') {
      return this.convertToCSV(data);
    }
    
    return JSON.stringify(data, null, 2);
  }

  convertToCSV(data) {
    if (data.dataPoints.length === 0) return '';
    
    const headers = Object.keys(data.dataPoints[0]);
    const rows = data.dataPoints.map(point => 
      headers.map(header => point[header]).join(',')
    );
    
    return [headers.join(','), ...rows].join('\n');
  }
}

// Singleton instance for global use
export const realTimeDataManager = new RealTimeDataManager();

export default RealTimeDataManager; 