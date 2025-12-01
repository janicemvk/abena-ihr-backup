import React, { createContext, useContext, useReducer, useEffect } from 'react';
// import { dashboardService } from '../services/dashboardService'; // DISABLED - Using pure mock data
import toast from 'react-hot-toast';

// Initial state
const initialState = {
  activeModule: 'overview',
  realtimeData: {},
  alerts: [],
  timeRange: '24h',
  refreshInterval: 15000, // 15 seconds
  chartSettings: {
    showGrid: true,
    showLegend: true,
    showTooltip: true,
    chartType: 'line'
  },
  notifications: {
    enabled: true,
    sound: true,
    desktop: true
  },
  lastUpdated: null,
  systemStatus: 'online'
};

// Action types
const ActionTypes = {
  SET_ACTIVE_MODULE: 'SET_ACTIVE_MODULE',
  SET_REALTIME_DATA: 'SET_REALTIME_DATA',
  SET_ALERTS: 'SET_ALERTS',
  ADD_ALERT: 'ADD_ALERT',
  REMOVE_ALERT: 'REMOVE_ALERT',
  SET_TIME_RANGE: 'SET_TIME_RANGE',
  SET_REFRESH_INTERVAL: 'SET_REFRESH_INTERVAL',
  SET_CHART_SETTINGS: 'SET_CHART_SETTINGS',
  SET_NOTIFICATIONS: 'SET_NOTIFICATIONS',
  SET_LAST_UPDATED: 'SET_LAST_UPDATED',
  SET_SYSTEM_STATUS: 'SET_SYSTEM_STATUS'
};

// Reducer
const dashboardReducer = (state, action) => {
  switch (action.type) {
    case ActionTypes.SET_ACTIVE_MODULE:
      return { ...state, activeModule: action.payload };
    
    case ActionTypes.SET_REALTIME_DATA:
      return { 
        ...state, 
        realtimeData: { ...state.realtimeData, ...action.payload },
        lastUpdated: new Date().toISOString()
      };
    
    case ActionTypes.SET_ALERTS:
      return { ...state, alerts: action.payload };
    
    case ActionTypes.ADD_ALERT:
      return { 
        ...state, 
        alerts: [...state.alerts, action.payload] 
      };
    
    case ActionTypes.REMOVE_ALERT:
      return { 
        ...state, 
        alerts: state.alerts.filter(alert => alert.id !== action.payload) 
      };
    
    case ActionTypes.SET_TIME_RANGE:
      return { ...state, timeRange: action.payload };
    
    case ActionTypes.SET_REFRESH_INTERVAL:
      return { ...state, refreshInterval: action.payload };
    
    case ActionTypes.SET_CHART_SETTINGS:
      return { 
        ...state, 
        chartSettings: { ...state.chartSettings, ...action.payload } 
      };
    
    case ActionTypes.SET_NOTIFICATIONS:
      return { 
        ...state, 
        notifications: { ...state.notifications, ...action.payload } 
      };
    
    case ActionTypes.SET_LAST_UPDATED:
      return { ...state, lastUpdated: action.payload };
    
    case ActionTypes.SET_SYSTEM_STATUS:
      return { ...state, systemStatus: action.payload };
    
    default:
      return state;
  }
};

// Context
const DashboardContext = createContext();

// Provider component
export const DashboardProvider = ({ children }) => {
  const [state, dispatch] = useReducer(dashboardReducer, initialState);

  // Actions
  const actions = {
    setActiveModule: (module) => {
      dispatch({ type: ActionTypes.SET_ACTIVE_MODULE, payload: module });
    },
    
    updateRealtimeData: (data) => {
      dispatch({ type: ActionTypes.SET_REALTIME_DATA, payload: data });
    },
    
    setAlerts: (alerts) => {
      dispatch({ type: ActionTypes.SET_ALERTS, payload: alerts });
    },
    
    addAlert: (alert) => {
      const alertWithId = { ...alert, id: Date.now(), timestamp: new Date().toISOString() };
      dispatch({ type: ActionTypes.ADD_ALERT, payload: alertWithId });
      
      // Show notification if enabled
      if (state.notifications.enabled) {
        toast.error(`${alert.type}: ${alert.message}`, {
          duration: 6000,
          icon: '⚠️'
        });
      }
      
      // Desktop notification
      if (state.notifications.desktop && 'Notification' in window) {
        new Notification('eBDome Alert', {
          body: `${alert.type}: ${alert.message}`,
          icon: '/favicon.ico'
        });
      }
    },
    
    removeAlert: (alertId) => {
      dispatch({ type: ActionTypes.REMOVE_ALERT, payload: alertId });
    },
    
    setTimeRange: (timeRange) => {
      dispatch({ type: ActionTypes.SET_TIME_RANGE, payload: timeRange });
    },
    
    setRefreshInterval: (interval) => {
      dispatch({ type: ActionTypes.SET_REFRESH_INTERVAL, payload: interval });
    },
    
    setChartSettings: (settings) => {
      dispatch({ type: ActionTypes.SET_CHART_SETTINGS, payload: settings });
    },
    
    setNotifications: (settings) => {
      dispatch({ type: ActionTypes.SET_NOTIFICATIONS, payload: settings });
    },
    
    setSystemStatus: (status) => {
      dispatch({ type: ActionTypes.SET_SYSTEM_STATUS, payload: status });
    }
  };

  // Real-time data updates - PURE MOCK DATA
  useEffect(() => {
    if (state.refreshInterval > 0) {
      const interval = setInterval(async () => {
        try {
          // Pure mock real-time data - FLATTENED STRUCTURE for PatientOverview
          const mockRealtimeData = {
            patientId: 'PAT-001',
            timestamp: new Date().toISOString(),
            // Flattened vital signs for easy access
            heartRate: Math.floor(Math.random() * 20) + 60, // 60-80
            bloodPressure: {
              systolic: Math.floor(Math.random() * 20) + 110,
              diastolic: Math.floor(Math.random() * 10) + 70
            },
            temperature: parseFloat((Math.random() * 2 + 97).toFixed(1)), // 97-99
            oxygenSaturation: Math.floor(Math.random() * 5) + 95, // 95-99
            ebdomeActivity: parseFloat((Math.random() * 0.4 + 0.6).toFixed(2)), // 0.6-1.0
            // Additional vital metrics
            respirationRate: Math.floor(Math.random() * 6) + 12, // 12-18 breaths/min (normal range)
            stressLevel: Math.floor(Math.random() * 30) + 20, // 20-50 (stress index)
            sleepQuality: parseFloat((Math.random() * 0.3 + 0.65).toFixed(2)), // 0.65-0.95 (sleep quality score)
            // Additional eBDome readings
            ebdomeReadings: {
              endocannabinoid: parseFloat((Math.random() * 0.4 + 0.6).toFixed(2)),
              metabolic: parseFloat((Math.random() * 0.4 + 0.6).toFixed(2)),
              immune: parseFloat((Math.random() * 0.4 + 0.6).toFixed(2)),
              hormonal: parseFloat((Math.random() * 0.4 + 0.6).toFixed(2))
            },
            alerts: [],
            status: 'stable'
          };
          console.log('✅ Mock real-time data updated:', mockRealtimeData.heartRate, 'bpm');
          actions.updateRealtimeData(mockRealtimeData);
          actions.setSystemStatus('online');
        } catch (error) {
          console.error('Failed to generate mock real-time data:', error);
          actions.setSystemStatus('offline');
        }
      }, state.refreshInterval);

      return () => clearInterval(interval);
    }
  }, [state.refreshInterval]);

  // Request notification permission
  useEffect(() => {
    if (state.notifications.desktop && 'Notification' in window) {
      Notification.requestPermission();
    }
  }, [state.notifications.desktop]);

  return (
    <DashboardContext.Provider value={{ ...state, actions }}>
      {children}
    </DashboardContext.Provider>
  );
};

// Custom hook
export const useDashboard = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within a DashboardProvider');
  }
  return context;
}; 