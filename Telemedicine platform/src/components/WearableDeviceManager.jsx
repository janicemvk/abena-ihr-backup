import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import abenaIntegration from '../services/AbenaIntegration';
import { 
  Activity, 
  Heart, 
  Moon, 
  Watch, 
  TrendingUp, 
  AlertTriangle,
  Plus,
  Settings,
  Download,
  Eye,
  Smartphone,
  Wifi,
  Battery,
  Signal
} from 'lucide-react';

const WearableDeviceManager = ({ userType, patientId = 'patient_123' }) => {
  const [wearableData, setWearableData] = useState(null);
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [showDeviceRegistration, setShowDeviceRegistration] = useState(false);
  const [newDevice, setNewDevice] = useState({
    name: '',
    type: '',
    model: '',
    serialNumber: ''
  });

  // Load wearable data and devices
  useEffect(() => {
    const loadWearableData = async () => {
      try {
        setLoading(true);
        
        // Get wearable data
        const data = await abenaIntegration.getWearableData(patientId, null, selectedTimeRange);
        setWearableData(data);
        
        // Get registered devices
        const registeredDevices = await abenaIntegration.getRegisteredDevices(patientId);
        setDevices(registeredDevices);
        
      } catch (error) {
        console.error('Error loading wearable data:', error);
        // For demo purposes, use mock data
        setWearableData({
          vitalSigns: {
            heartRate: { current: 72, average: 68, min: 55, max: 120 },
            bloodPressure: { systolic: 120, diastolic: 80 },
            temperature: 98.6,
            oxygenSaturation: 98
          },
          activity: {
            steps: 8542,
            calories: 420,
            distance: 3.2,
            activeMinutes: 45
          },
          sleep: {
            totalHours: 7.5,
            deepSleep: 2.1,
            lightSleep: 4.2,
            remSleep: 1.2,
            sleepScore: 85
          }
        });
        
        setDevices([
          { id: 1, name: 'Apple Watch Series 7', type: 'smartwatch', status: 'active', battery: 85 },
          { id: 2, name: 'Fitbit Charge 5', type: 'fitness_tracker', status: 'active', battery: 92 },
          { id: 3, name: 'Oura Ring', type: 'smart_ring', status: 'inactive', battery: 0 }
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadWearableData();
  }, [patientId, selectedTimeRange]);

  const handleDeviceRegistration = async () => {
    try {
      setLoading(true);
      
      const registeredDevice = await abenaIntegration.registerWearableDevice(patientId, newDevice);
      setDevices([...devices, registeredDevice]);
      setShowDeviceRegistration(false);
      setNewDevice({ name: '', type: '', model: '', serialNumber: '' });
      
      // Log activity
      await abenaIntegration.logActivity({
        action: 'device_registered',
        patientId,
        deviceInfo: newDevice,
        details: `New wearable device ${newDevice.name} registered`
      });
      
    } catch (error) {
      console.error('Error registering device:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeviceStatusUpdate = async (deviceId, newStatus) => {
    try {
      const updatedDevice = await abenaIntegration.updateDeviceStatus(patientId, deviceId, newStatus);
      setDevices(devices.map(device => 
        device.id === deviceId ? updatedDevice : device
      ));
    } catch (error) {
      console.error('Error updating device status:', error);
    }
  };

  const generateHealthReport = async () => {
    try {
      setLoading(true);
      const report = await abenaIntegration.generateHealthReport(patientId, 'comprehensive', selectedTimeRange);
      // Handle report generation (download, display, etc.)
      console.log('Health report generated:', report);
    } catch (error) {
      console.error('Error generating health report:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Wearable Devices & Health Data</h2>
        <div className="flex space-x-2">
          <select 
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
          {userType === 'patient' && (
            <button 
              onClick={() => setShowDeviceRegistration(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-md flex items-center space-x-2 hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              <span>Add Device</span>
            </button>
          )}
        </div>
      </div>

      {/* Registered Devices */}
      <Card>
        <CardHeader>
          <CardTitle>Connected Devices</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading devices...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {devices.map((device) => (
                <div key={device.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <Watch className="w-6 h-6 text-blue-500" />
                      <div>
                        <p className="font-medium">{device.name}</p>
                        <p className="text-sm text-gray-500">{device.type}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 text-xs rounded ${
                        device.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {device.status}
                      </span>
                      {device.battery > 0 && (
                        <span className="text-xs text-gray-500">{device.battery}%</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-1">
                      <Battery className="w-4 h-4" />
                      <span>{device.battery}%</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Wifi className="w-4 h-4" />
                      <span>Connected</span>
                    </div>
                  </div>
                  {userType === 'patient' && (
                    <div className="mt-3 flex space-x-2">
                      <button 
                        onClick={() => handleDeviceStatusUpdate(device.id, device.status === 'active' ? 'inactive' : 'active')}
                        className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                      >
                        {device.status === 'active' ? 'Disconnect' : 'Connect'}
                      </button>
                      <button className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200">
                        Settings
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Health Metrics Dashboard */}
      {wearableData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Vital Signs */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Heart className="w-5 h-5 text-red-500" />
                <span>Vital Signs</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Heart Rate</span>
                  <div className="text-right">
                    <span className="text-2xl font-bold text-red-500">{wearableData.vitalSigns.heartRate.current} bpm</span>
                    <p className="text-xs text-gray-500">Avg: {wearableData.vitalSigns.heartRate.average} bpm</p>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Blood Pressure</span>
                  <span className="text-lg font-semibold">{wearableData.vitalSigns.bloodPressure.systolic}/{wearableData.vitalSigns.bloodPressure.diastolic} mmHg</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Temperature</span>
                  <span className="text-lg font-semibold">{wearableData.vitalSigns.temperature}°F</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Oxygen Saturation</span>
                  <span className="text-lg font-semibold">{wearableData.vitalSigns.oxygenSaturation}%</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Activity Tracking */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-green-500" />
                <span>Activity</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Steps</span>
                  <span className="text-2xl font-bold text-green-500">{wearableData.activity.steps.toLocaleString()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Calories</span>
                  <span className="text-lg font-semibold">{wearableData.activity.calories} kcal</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Distance</span>
                  <span className="text-lg font-semibold">{wearableData.activity.distance} mi</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Active Minutes</span>
                  <span className="text-lg font-semibold">{wearableData.activity.activeMinutes} min</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Sleep Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Moon className="w-5 h-5 text-purple-500" />
                <span>Sleep</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Total Sleep</span>
                  <span className="text-2xl font-bold text-purple-500">{wearableData.sleep.totalHours}h</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Deep Sleep</span>
                  <span className="text-lg font-semibold">{wearableData.sleep.deepSleep}h</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Light Sleep</span>
                  <span className="text-lg font-semibold">{wearableData.sleep.lightSleep}h</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">REM Sleep</span>
                  <span className="text-lg font-semibold">{wearableData.sleep.remSleep}h</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Sleep Score</span>
                  <span className="text-lg font-semibold text-purple-500">{wearableData.sleep.sleepScore}/100</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Health Trends */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-blue-500" />
                <span>Health Trends</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Heart Rate Trend</span>
                  <span className="text-green-500 text-sm">↓ Stable</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Activity Level</span>
                  <span className="text-green-500 text-sm">↑ Increasing</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Sleep Quality</span>
                  <span className="text-yellow-500 text-sm">→ Consistent</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Overall Health</span>
                  <span className="text-green-500 text-sm">↑ Improving</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between items-center">
        <div className="flex space-x-2">
          <button 
            onClick={generateHealthReport}
            disabled={loading}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>{loading ? 'Generating...' : 'Generate Health Report'}</span>
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2">
            <Eye className="w-4 h-4" />
            <span>View Detailed Analytics</span>
          </button>
        </div>
      </div>

      {/* Device Registration Modal */}
      {showDeviceRegistration && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Register New Device</h3>
              <button 
                onClick={() => setShowDeviceRegistration(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Device Name</label>
                <input 
                  type="text" 
                  value={newDevice.name}
                  onChange={(e) => setNewDevice({...newDevice, name: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  placeholder="e.g., Apple Watch"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Device Type</label>
                <select 
                  value={newDevice.type}
                  onChange={(e) => setNewDevice({...newDevice, type: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                >
                  <option value="">Select device type</option>
                  <option value="smartwatch">Smartwatch</option>
                  <option value="fitness_tracker">Fitness Tracker</option>
                  <option value="smart_ring">Smart Ring</option>
                  <option value="blood_pressure_monitor">Blood Pressure Monitor</option>
                  <option value="glucose_monitor">Glucose Monitor</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Model</label>
                <input 
                  type="text" 
                  value={newDevice.model}
                  onChange={(e) => setNewDevice({...newDevice, model: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  placeholder="e.g., Series 7"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Serial Number</label>
                <input 
                  type="text" 
                  value={newDevice.serialNumber}
                  onChange={(e) => setNewDevice({...newDevice, serialNumber: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  placeholder="Device serial number"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button 
                onClick={() => setShowDeviceRegistration(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button 
                onClick={handleDeviceRegistration}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                {loading ? 'Registering...' : 'Register Device'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WearableDeviceManager; 