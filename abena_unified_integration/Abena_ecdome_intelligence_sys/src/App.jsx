import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ECDomeIntelligenceSystem from './components/ECDomeIntelligenceSystem';
import ECDomeChatbot from './components/ECDomeChatbot';
import ECBomeTestSuite from './components/ECBomeTestSuite';
import backgroundService from './services/backgroundService';

// IHR System Integration Context
const IHRContext = React.createContext();

const IHRProvider = ({ children }) => {
  const [ihrState, setIhrState] = useState({
    isInitialized: false,
    currentPatient: null,
    backgroundProcesses: {
      ecdomeAnalysis: {
        isRunning: false,
        lastUpdate: null,
        status: 'idle'
      },
      dataCollection: {
        isRunning: false,
        lastUpdate: null,
        status: 'idle'
      },
      intelligenceProcessing: {
        isRunning: false,
        lastUpdate: null,
        status: 'idle'
      },
      healthMonitoring: {
        isRunning: false,
        lastUpdate: null,
        status: 'idle'
      },
      continuousAnalysis: {
        isRunning: false,
        lastUpdate: null,
        status: 'idle'
      }
    },
    systemHealth: {
      overall: 'healthy',
      components: {
        ecdome: 'healthy',
        medicalDb: 'healthy',
        intelligence: 'healthy',
        labResults: 'healthy'
      }
    }
  });

  // Initialize IHR system
  useEffect(() => {
    const initializeIHR = async () => {
      try {
        // Simulate IHR system initialization
        console.log('Initializing IHR System...');
        
        // Start background service
        backgroundService.start();
        
        // Start background processes
        setIhrState(prev => ({
          ...prev,
          isInitialized: true,
          backgroundProcesses: {
            ...prev.backgroundProcesses,
            ecdomeAnalysis: {
              ...prev.backgroundProcesses.ecdomeAnalysis,
              isRunning: true,
              status: 'running',
              lastUpdate: new Date().toISOString()
            }
          }
        }));

        console.log('IHR System initialized successfully');
      } catch (error) {
        console.error('Failed to initialize IHR System:', error);
      }
    };

    initializeIHR();

    // Cleanup on unmount
    return () => {
      backgroundService.stop();
    };
  }, []);

  // Listen for background service status updates
  useEffect(() => {
    const handleBackgroundStatusUpdate = (event) => {
      const { processName, status, allProcesses } = event.detail;
      
      setIhrState(prev => ({
        ...prev,
        backgroundProcesses: {
          ...prev.backgroundProcesses,
          [processName]: {
            isRunning: status.isRunning,
            lastUpdate: status.lastUpdate,
            status: status.status
          }
        }
      }));
    };

    window.addEventListener('ihrBackgroundStatusUpdate', handleBackgroundStatusUpdate);
    
    return () => {
      window.removeEventListener('ihrBackgroundStatusUpdate', handleBackgroundStatusUpdate);
    };
  }, []);

  // Background process monitoring
  useEffect(() => {
    const monitorBackgroundProcesses = () => {
      setIhrState(prev => ({
        ...prev,
        backgroundProcesses: {
          ...prev.backgroundProcesses,
          ecdomeAnalysis: {
            ...prev.backgroundProcesses.ecdomeAnalysis,
            lastUpdate: new Date().toISOString()
          }
        }
      }));
    };

    const interval = setInterval(monitorBackgroundProcesses, 30000); // Every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <IHRContext.Provider value={{ ihrState, setIhrState }}>
      {children}
    </IHRContext.Provider>
  );
};

// Main IHR Dashboard Component
const IHRDashboard = () => {
  const { ihrState } = React.useContext(IHRContext);

  if (!ihrState.isInitialized) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700">Initializing IHR System...</h2>
          <p className="text-gray-500 mt-2">Loading background processes and intelligence layer</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* IHR System Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">IHR System</h1>
              <div className="ml-4 flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  ihrState.systemHealth.overall === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
                <span className="text-sm text-gray-600">
                  {ihrState.systemHealth.overall.charAt(0).toUpperCase() + ihrState.systemHealth.overall.slice(1)}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Background Processes: {Object.values(ihrState.backgroundProcesses).filter(p => p.isRunning).length} active
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<IHRMainDashboard />} />
          <Route path="/ecbome-test" element={<ECBomeTestSuite />} />
          <Route path="/ecdome-test" element={<ECBomeTestSuite />} />
          <Route path="/ecbome-analysis" element={<ECDomeIntelligenceSystem />} />
          <Route path="/ecdome-analysis" element={<ECDomeIntelligenceSystem />} />
          <Route path="/chatbot" element={<ECDomeChatbot />} />
        </Routes>
      </main>
    </div>
  );
};

// IHR Main Dashboard
const IHRMainDashboard = () => {
  const { ihrState } = React.useContext(IHRContext);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">IHR System Overview</h2>
        
        {/* Background Processes Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {Object.entries(ihrState.backgroundProcesses).map(([key, process]) => (
            <div key={key} className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-900 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </h3>
                <div className={`w-2 h-2 rounded-full ${
                  process.isRunning ? 'bg-green-500' : 'bg-gray-400'
                }`}></div>
              </div>
              <p className="text-sm text-gray-600">
                Status: {process.status}
              </p>
              {process.lastUpdate && (
                <p className="text-xs text-gray-500 mt-1">
                  Last Update: {new Date(process.lastUpdate).toLocaleTimeString()}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* System Health */}
        <div className="border-t pt-4">
          <h3 className="font-medium text-gray-900 mb-3">System Health</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(ihrState.systemHealth.components).map(([component, status]) => (
              <div key={component} className="text-center">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  {component.toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Access to eCDome Components */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">eCBome Intelligence System</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/ecbome-test"
            className="block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <h3 className="font-medium text-gray-900">Test Suite</h3>
            <p className="text-sm text-gray-600 mt-1">
              Comprehensive testing and validation of eCBome analysis
            </p>
          </a>
          <a
            href="/ecbome-analysis"
            className="block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <h3 className="font-medium text-gray-900">Analysis Dashboard</h3>
            <p className="text-sm text-gray-600 mt-1">
              Real-time endocannabinoid system analysis and insights
            </p>
          </a>
          <a
            href="/chatbot"
            className="block p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
          >
            <h3 className="font-medium text-gray-900">AI Assistant</h3>
            <p className="text-sm text-gray-600 mt-1">
              Intelligent chatbot for eCBome system queries
            </p>
          </a>
        </div>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <IHRProvider>
      <Router>
        <IHRDashboard />
      </Router>
    </IHRProvider>
  );
};

export default App; 