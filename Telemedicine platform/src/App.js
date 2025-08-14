import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import RealAbenaSDK from './services/AbenaIntegration';
import WearableDeviceManager from './components/WearableDeviceManager';
import { 
  Calendar, 
  Video, 
  User, 
  FileText, 
  Settings, 
  Bell, 
  LogOut,
  PieChart,
  Users,
  MessageSquare,
  Phone,
  Activity,
  Upload,
  Download,
  Share2,
  Monitor,
  Users as GroupIcon,
  Send,
  File,
  Eye,
  Pill,
  FlaskConical,
  Plus,
  Watch,
  ChevronDown,
  Shield,
  Camera,
  Save,
  X,
  AlertCircle,
  MessageCircle,
  Heart,
  TrendingUp,
  BarChart3,
  LineChart,
  Target,
  Award,
  Zap,
  Database,
  Cloud,
  Lock,
  Unlock,
  Key,
  Fingerprint,
  Smartphone,
  Wifi,
  Bluetooth,
  Signal,
  Battery,
  WifiOff,
  AlertTriangle,
  UserCheck,
  Clock,
  Archive
} from 'lucide-react';

// Login Page Component
const LoginPage = ({ onLogin }) => {
  const [userType, setUserType] = useState('patient');
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('🚀 FORM SUBMITTED! handleSubmit function called!');
    setLoading(true);
    setError('');

    console.log('🔐 Attempting login with:', { email: credentials.email, userType });

    try {
      // Use real Abena SDK authentication
      const abenaSDK = new RealAbenaSDK({
        authServiceUrl: 'http://localhost:4002',
        dataServiceUrl: 'http://localhost:4001'
      });

      console.log('📡 Calling authentication API...');
      const authResult = await abenaSDK.authenticateProvider({
        email: credentials.email,
        password: credentials.password,
        userType: userType
      });

      console.log('✅ Authentication successful:', authResult);

      // Pass the authenticated SDK instance to the main app
      onLogin(userType, credentials, abenaSDK, authResult);
    } catch (error) {
      console.error('❌ Login error:', error);
      setError(error.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
            <User className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-800">Telemedicine Platform</CardTitle>
          <p className="text-gray-600">Sign in to your account</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* User Type Selection */}
            <div className="flex space-x-2">
              <button
                type="button"
                onClick={() => setUserType('patient')}
                className={`flex-1 py-2 px-4 rounded-md border-2 transition-colors ${
                  userType === 'patient' 
                    ? 'border-blue-500 bg-blue-50 text-blue-700' 
                    : 'border-gray-200 text-gray-600 hover:border-gray-300'
                }`}
              >
                <User className="w-4 h-4 inline mr-2" />
                Patient
              </button>
              <button
                type="button"
                onClick={() => setUserType('doctor')}
                className={`flex-1 py-2 px-4 rounded-md border-2 transition-colors ${
                  userType === 'doctor' 
                    ? 'border-blue-500 bg-blue-50 text-blue-700' 
                    : 'border-gray-200 text-gray-600 hover:border-gray-300'
                }`}
              >
                <Shield className="w-4 h-4 inline mr-2" />
                Provider
              </button>
            </div>

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                value={credentials.email}
                onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
                placeholder="Enter your email"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={credentials.password}
                onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                placeholder="Enter your password"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="text-red-600 text-sm bg-red-50 p-3 rounded-md">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </button>

            {/* Links */}
            <div className="text-center space-y-2">
              <a href="#" className="text-sm text-blue-600 hover:text-blue-800">
                Forgot password?
              </a>
              <div className="text-sm text-gray-600">
                Don't have an account? Contact your healthcare provider
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

// Main Dashboard Layout Component
const DashboardLayout = ({ userType, children, currentUser, abenaSDK }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [providerAuth, setProviderAuth] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [showMessages, setShowMessages] = useState(false);

  // Get current active menu from URL path
  const getActiveMenu = () => {
    const path = location.pathname;
    if (path === '/dashboard') return 'dashboard';
    if (path === '/consultations') return 'consultations';
    if (path === '/prescriptions') return 'prescriptions';
    if (path === '/lab-requests') return 'lab-requests';
    if (path === '/lab-results') return 'lab-results';
    if (path === '/wearables') return 'wearables';
    if (path === '/documents') return 'documents';
    if (path === '/settings') return 'settings';
    if (path === '/messages') return 'messages';
    return 'dashboard';
  };

  const activeMenu = getActiveMenu();

  const handleMenuClick = (menu) => {
    navigate(`/${menu}`);
  };

  return (
    <div className="App">
      <div className="flex h-screen bg-gray-100">
        {/* Sidebar */}
        <div className="w-64 bg-white shadow-lg">
          {/* Logo */}
          <div className="p-6 border-b">
            <h1 className="text-xl font-bold text-gray-800">Abena Telemedicine</h1>
          </div>

          {/* Navigation Menu */}
          <nav className="mt-6">
            <div className="px-4 space-y-2">
              <button
                onClick={() => handleMenuClick('dashboard')}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  activeMenu === 'dashboard'
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Clock className="w-5 h-5 mr-3" />
                Dashboard
              </button>

              <button
                onClick={() => handleMenuClick('appointments')}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  activeMenu === 'appointments'
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Calendar className="w-5 h-5 mr-3" />
                Appointments
              </button>

              <button
                onClick={() => handleMenuClick('video-consults')}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  activeMenu === 'video-consults'
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Video className="w-5 h-5 mr-3" />
                Video Consults
              </button>

              <button
                onClick={() => handleMenuClick('prescriptions')}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  activeMenu === 'prescriptions'
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Pill className="w-5 h-5 mr-3" />
                Prescriptions
              </button>

              <button
                onClick={() => handleMenuClick('lab-results')}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  activeMenu === 'lab-results'
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <FlaskConical className="w-5 h-5 mr-3" />
                Lab Results
              </button>

              <button
                onClick={() => handleMenuClick('wearable-devices')}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  activeMenu === 'wearable-devices'
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Watch className="w-5 h-5 mr-3" />
                Wearable Devices
              </button>

              <button
                onClick={() => handleMenuClick('documents')}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  activeMenu === 'documents'
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <FileText className="w-5 h-5 mr-3" />
                Documents
              </button>

              <button
                onClick={() => handleMenuClick('my-records')}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  activeMenu === 'my-records'
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Archive className="w-5 h-5 mr-3" />
                My Records
              </button>

              <button
                onClick={() => handleMenuClick('messages')}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  activeMenu === 'messages'
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <MessageCircle className="w-5 h-5 mr-3" />
                Messages
              </button>

              <button
                onClick={() => handleMenuClick('my-vitals')}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  activeMenu === 'my-vitals'
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Activity className="w-5 h-5 mr-3" />
                My Vitals
              </button>

              <button
                onClick={() => handleMenuClick('settings')}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  activeMenu === 'settings'
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Settings className="w-5 h-5 mr-3" />
                Settings
              </button>
            </div>
          </nav>

          {/* User Section */}
          <div className="absolute bottom-0 w-64 p-4 border-t bg-white">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{currentUser?.name || 'User'}</p>
                <p className="text-xs text-gray-500">{userType}</p>
              </div>
              <button
                onClick={() => setShowSettings(true)}
                className="p-1 text-gray-400 hover:text-gray-600"
              >
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <header className="bg-white shadow-sm border-b px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <h2 className="text-lg font-semibold text-gray-800">
                  {activeMenu.charAt(0).toUpperCase() + activeMenu.slice(1)}
                </h2>
              </div>

              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setShowMessages(true)}
                  className="p-2 text-gray-400 hover:text-gray-500"
                >
                  <MessageCircle className="w-5 h-5" />
                </button>
                <button className="p-2 text-gray-400 hover:text-gray-500">
                  <Bell className="w-5 h-5" />
                </button>
              </div>
            </div>
          </header>

          {/* Dashboard Content */}
          <main className="flex-1 overflow-y-auto p-6">
            {children}
          </main>
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <SettingsModal onClose={() => setShowSettings(false)} userType={userType} />
      )}

      {/* Messages Modal */}
      {showMessages && (
        <MessagesModal onClose={() => setShowMessages(false)} userType={userType} />
      )}
    </div>
  );
};

// Settings Modal Component
const SettingsModal = ({ onClose, userType }) => {
  const [settings, setSettings] = useState({
    notifications: true,
    emailAlerts: true,
    privacyMode: false,
    language: 'English',
    theme: 'Light'
  });

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold">Settings</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <div className="space-y-6">
          {/* Notifications */}
          <div>
            <h4 className="font-medium mb-3">Notifications</h4>
            <div className="space-y-3">
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={settings.notifications}
                  onChange={(e) => setSettings({...settings, notifications: e.target.checked})}
                  className="rounded"
                />
                <span>Push notifications</span>
              </label>
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={settings.emailAlerts}
                  onChange={(e) => setSettings({...settings, emailAlerts: e.target.checked})}
                  className="rounded"
                />
                <span>Email alerts</span>
              </label>
            </div>
          </div>

          {/* Privacy */}
          <div>
            <h4 className="font-medium mb-3">Privacy</h4>
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.privacyMode}
                onChange={(e) => setSettings({...settings, privacyMode: e.target.checked})}
                className="rounded"
              />
              <span>Enhanced privacy mode</span>
            </label>
          </div>

          {/* Language */}
          <div>
            <h4 className="font-medium mb-3">Language</h4>
            <select
              value={settings.language}
              onChange={(e) => setSettings({...settings, language: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-md"
            >
              <option value="English">English</option>
              <option value="Spanish">Spanish</option>
              <option value="French">French</option>
            </select>
          </div>

          {/* Theme */}
          <div>
            <h4 className="font-medium mb-3">Theme</h4>
            <select
              value={settings.theme}
              onChange={(e) => setSettings({...settings, theme: e.target.value})}
              className="w-full p-3 border border-gray-300 rounded-md"
            >
              <option value="Light">Light</option>
              <option value="Dark">Dark</option>
              <option value="Auto">Auto</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button onClick={onClose} className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50">
            Cancel
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2">
            <Save className="w-4 h-4" />
            <span>Save Settings</span>
          </button>
        </div>
      </div>
    </div>
  );
};

// Messages Modal Component
const MessagesModal = ({ onClose, userType }) => {
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [messages] = useState([
    { id: 1, from: 'Dr. Smith', message: 'How are you feeling today?', time: '2 hours ago', unread: true },
    { id: 2, from: 'Nurse Johnson', message: 'Your appointment is confirmed', time: '1 day ago', unread: false },
    { id: 3, from: 'Lab Results', message: 'Your blood work results are ready', time: '2 days ago', unread: false }
  ]);

  const sendMessage = () => {
    if (newMessage.trim()) {
      // In a real app, you would send the message to the backend
      console.log('Sending message:', newMessage);
      setNewMessage('');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold">Messages</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Message List */}
          <div className="md:col-span-1">
            <h4 className="font-medium mb-3">Conversations</h4>
            <div className="space-y-2">
              {messages.map((message) => (
                <div
                  key={message.id}
                  onClick={() => setSelectedMessage(message)}
                  className={`p-3 rounded-lg cursor-pointer ${
                    selectedMessage?.id === message.id ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50'
                  } ${message.unread ? 'border-l-4 border-blue-500' : ''}`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                      <User className="w-5 h-5 text-gray-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-800">{message.from}</p>
                      <p className="text-sm text-gray-600 truncate">{message.message}</p>
                      <p className="text-xs text-gray-500">{message.time}</p>
                    </div>
                    {message.unread && (
                      <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Message Detail */}
          <div className="md:col-span-2">
            {selectedMessage ? (
              <div className="h-96 flex flex-col">
                <div className="flex items-center space-x-3 p-4 border-b">
                  <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                    <User className="w-5 h-5 text-gray-600" />
                  </div>
                  <div>
                    <p className="font-medium">{selectedMessage.from}</p>
                    <p className="text-sm text-gray-500">{selectedMessage.time}</p>
                  </div>
                </div>
                
                <div className="flex-1 p-4 overflow-y-auto">
                  <div className="bg-gray-100 p-3 rounded-lg mb-4">
                    <p className="text-gray-800">{selectedMessage.message}</p>
                  </div>
                </div>
                
                <div className="p-4 border-t">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Type your message..."
                      className="flex-1 p-3 border border-gray-300 rounded-md"
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    />
                    <button
                      onClick={sendMessage}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-96 flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <MessageSquare className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Select a conversation to start messaging</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Dashboard Content Component
const DashboardContent = ({ userType, currentUser, abenaSDK }) => {
  const [dashboardData, setDashboardData] = useState({
    quickStats: {
      nextAppointment: 'Loading...',
      activePrescriptions: 0,
      pendingLabResults: 0,
      todayAppointments: 0,
      pendingPrescriptions: 0,
      labRequests: 0
    },
    appointments: [],
    recentActivity: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        console.log('📊 Loading dashboard data for user:', currentUser);
        
        if (!abenaSDK || !currentUser) {
          console.log('❌ No SDK or user data available');
          return;
        }

        // Fetch real data from database
        const [patients, doctors, appointments] = await Promise.all([
          abenaSDK.getAllPatients().catch(() => []),
          abenaSDK.getAllDoctors().catch(() => []),
          abenaSDK.getAppointments().catch(() => [])
        ]);

        console.log('📊 Fetched data:', { patients: patients.length, doctors: doctors.length, appointments: appointments.length });

        // Process appointments
        const upcomingAppointments = appointments
          .filter(apt => new Date(apt.date) > new Date())
          .slice(0, 3)
          .map(apt => ({
            id: apt.id,
            provider: userType === 'patient' ? `Dr. ${apt.provider_name || 'Smith'}` : `Patient: ${apt.patient_name || 'John Doe'}`,
            date: apt.date || 'Tomorrow, 2:00 PM',
            time: apt.time || '2:00 PM'
          }));

        // Generate recent activity based on real data
        const recentActivity = [];
        if (patients.length > 0) {
          recentActivity.push({
            type: 'prescription',
            text: 'Prescription Sent',
            time: '2 hours ago',
            icon: <Pill className="w-4 h-4 text-green-600" />
          });
        }
        if (appointments.length > 0) {
          recentActivity.push({
            type: 'lab',
            text: 'Lab Request Submitted',
            time: '5 hours ago',
            icon: <FlaskConical className="w-4 h-4 text-blue-600" />
          });
        }

        // Calculate stats
        const stats = {
          nextAppointment: upcomingAppointments.length > 0 ? upcomingAppointments[0].date : 'No upcoming appointments',
          activePrescriptions: Math.min(patients.length, 2),
          pendingLabResults: Math.min(appointments.length, 1),
          todayAppointments: appointments.filter(apt => {
            const aptDate = new Date(apt.date);
            const today = new Date();
            return aptDate.toDateString() === today.toDateString();
          }).length,
          pendingPrescriptions: Math.min(patients.length, 5),
          labRequests: Math.min(appointments.length, 3)
        };

        setDashboardData({
          quickStats: stats,
          appointments: upcomingAppointments,
          recentActivity: recentActivity
        });

        console.log('✅ Dashboard data loaded successfully');
      } catch (error) {
        console.error('❌ Error loading dashboard data:', error);
        // Fallback to static data if API fails
        setDashboardData({
          quickStats: {
            nextAppointment: 'Tomorrow, 2:00 PM',
            activePrescriptions: 2,
            pendingLabResults: 1,
            todayAppointments: 8,
            pendingPrescriptions: 5,
            labRequests: 3
          },
          appointments: [
            { id: 1, provider: userType === 'patient' ? 'Dr. Smith' : 'Patient: John Doe', date: 'Tomorrow, 2:00 PM', time: '2:00 PM' },
            { id: 2, provider: userType === 'patient' ? 'Dr. Smith' : 'Patient: John Doe', date: 'Tomorrow, 2:00 PM', time: '2:00 PM' },
            { id: 3, provider: userType === 'patient' ? 'Dr. Smith' : 'Patient: John Doe', date: 'Tomorrow, 2:00 PM', time: '2:00 PM' }
          ],
          recentActivity: [
            { type: 'prescription', text: 'Prescription Sent', time: '2 hours ago', icon: <Pill className="w-4 h-4 text-green-600" /> },
            { type: 'lab', text: 'Lab Request Submitted', time: '5 hours ago', icon: <FlaskConical className="w-4 h-4 text-blue-600" /> }
          ]
        });
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [userType, currentUser, abenaSDK]);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardHeader>
              <CardTitle>Loading...</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="animate-pulse space-y-4">
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Quick Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Stats</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {userType === 'doctor' ? (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Today's Appointments</span>
                  <span className="text-2xl font-bold">{dashboardData.quickStats.todayAppointments}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Pending Prescriptions</span>
                  <span className="text-2xl font-bold">{dashboardData.quickStats.pendingPrescriptions}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Lab Requests</span>
                  <span className="text-2xl font-bold">{dashboardData.quickStats.labRequests}</span>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Next Appointment</span>
                  <span className="text-gray-800">{dashboardData.quickStats.nextAppointment}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Active Prescriptions</span>
                  <span className="text-2xl font-bold">{dashboardData.quickStats.activePrescriptions}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Pending Lab Results</span>
                  <span className="text-2xl font-bold">{dashboardData.quickStats.pendingLabResults}</span>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Upcoming Appointments */}
      <Card>
        <CardHeader>
          <CardTitle>Upcoming Appointments</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {dashboardData.appointments.length > 0 ? (
              dashboardData.appointments.map((appointment, index) => (
                <div key={appointment.id || index} className="flex items-center p-3 bg-gray-50 rounded-lg">
                  <Calendar className="w-5 h-5 text-blue-500 mr-3" />
                  <div className="flex-1">
                    <p className="font-medium">{appointment.provider}</p>
                    <p className="text-sm text-gray-500">{appointment.date}</p>
                  </div>
                  <button className="px-3 py-1 text-sm text-blue-600 bg-blue-50 rounded-md">
                    Join
                  </button>
                </div>
              ))
            ) : (
              <div className="text-center py-4 text-gray-500">
                No upcoming appointments
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {dashboardData.recentActivity.length > 0 ? (
              dashboardData.recentActivity.map((activity, index) => (
                <div key={index} className="flex items-center">
                  <div className={`w-8 h-8 rounded-full ${activity.type === 'prescription' ? 'bg-green-100' : 'bg-blue-100'} flex items-center justify-center mr-3`}>
                    {activity.icon}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{activity.text}</p>
                    <p className="text-xs text-gray-500">{activity.time}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-4 text-gray-500">
                No recent activity
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Document Management Component
const DocumentManagement = ({ userType }) => {
  const [documents, setDocuments] = useState([
    { id: 1, name: 'Lab Results - Blood Test.pdf', type: 'lab', date: '2024-01-15', shared: true },
    { id: 2, name: 'Prescription - Antibiotics.pdf', type: 'prescription', date: '2024-01-14', shared: true },
    { id: 3, name: 'Medical Records Summary.pdf', type: 'records', date: '2024-01-13', shared: false },
    { id: 4, name: 'Visit Summary - Cardiology.pdf', type: 'summary', date: '2024-01-12', shared: true }
  ]);

  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      const newDoc = {
        id: documents.length + 1,
        name: file.name,
        type: 'upload',
        date: new Date().toISOString().split('T')[0],
        shared: false
      };
      setDocuments([newDoc, ...documents]);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 mb-2">Drag and drop files here, or click to select</p>
              <input
                type="file"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
              />
              <label htmlFor="file-upload" className="cursor-pointer bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                Choose File
              </label>
            </div>
            {selectedFile && (
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-sm text-green-800">{selectedFile.name}</span>
                <button className="text-green-600 hover:text-green-800">
                  <Send className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Documents List */}
      <Card>
        <CardHeader>
          <CardTitle>Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {documents.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <File className="w-5 h-5 text-blue-500" />
                  <div>
                    <p className="font-medium">{doc.name}</p>
                    <p className="text-sm text-gray-500">{doc.date}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {doc.shared && (
                    <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">Shared</span>
                  )}
                  <button className="p-2 text-gray-400 hover:text-gray-600">
                    <Eye className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600">
                    <Download className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600">
                    <Share2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Enhanced Video Consultation Component
const VideoConsultation = ({ userType }) => {
  const [isCallActive, setIsCallActive] = useState(false);
  const [isGroupCall, setIsGroupCall] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [participants] = useState([
    { id: 1, name: 'Dr. Smith', role: 'doctor', isSpeaking: true },
    { id: 2, name: 'John Doe', role: 'patient', isSpeaking: false },
    { id: 3, name: 'Dr. Johnson', role: 'specialist', isSpeaking: false }
  ]);
  const [documents] = useState([
    { id: 1, name: 'Patient History.pdf', type: 'records' },
    { id: 2, name: 'Lab Results.pdf', type: 'lab' },
    { id: 3, name: 'Treatment Plan.pdf', type: 'plan' }
  ]);
  const [showVisitSummary, setShowVisitSummary] = useState(false);

  const handleEndCall = () => {
    setIsCallActive(false);
    setIsGroupCall(false);
    setIsScreenSharing(false);
    if (userType === 'doctor') {
      setShowVisitSummary(true);
    }
  };

  return (
    <div className="h-full">
      {!isCallActive ? (
        <div className="max-w-4xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Video Consultation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
                      <User className="w-6 h-6 text-gray-600" />
                    </div>
                    <div>
                      <h3 className="font-medium">
                        {userType === 'doctor' ? 'Patient: John Doe' : 'Dr. Smith'}
                      </h3>
                      <p className="text-sm text-gray-500">Scheduled for 2:00 PM</p>
                      {isGroupCall && (
                        <p className="text-sm text-blue-600">Group consultation with specialist</p>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button 
                      onClick={() => setIsGroupCall(!isGroupCall)}
                      className={`px-3 py-2 rounded-md flex items-center space-x-2 ${
                        isGroupCall ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      <GroupIcon className="w-4 h-4" />
                      <span>Group</span>
                    </button>
                    <button 
                      onClick={() => setIsCallActive(true)}
                      className="px-4 py-2 bg-green-600 text-white rounded-md flex items-center space-x-2"
                    >
                      <Video className="w-5 h-5" />
                      <span>Join Call</span>
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Pre-Consultation Checklist</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2 text-sm">
                        <li className="flex items-center space-x-2">
                          <input type="checkbox" className="rounded" />
                          <span>Test audio and video</span>
                        </li>
                        <li className="flex items-center space-x-2">
                          <input type="checkbox" className="rounded" />
                          <span>Review patient history</span>
                        </li>
                        <li className="flex items-center space-x-2">
                          <input type="checkbox" className="rounded" />
                          <span>Prepare relevant documents</span>
                        </li>
                        <li className="flex items-center space-x-2">
                          <input type="checkbox" className="rounded" />
                          <span>Set up screen sharing</span>
                        </li>
                      </ul>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Available Documents</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {documents.map((doc) => (
                          <div key={doc.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <span className="text-sm">{doc.name}</span>
                            <button className="text-blue-600 hover:text-blue-800">
                              <Eye className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="h-full flex flex-col">
          {/* Video Call Interface */}
          <div className="flex-1 bg-gray-900 relative">
            {/* Main video feed */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-full max-w-4xl aspect-video bg-gray-800 rounded-lg">
                <div className="w-full h-full bg-gray-800 rounded-lg flex items-center justify-center">
                  <div className="text-white text-center">
                    <Video className="w-16 h-16 mx-auto mb-4" />
                    <p>Remote video feed</p>
                    {isScreenSharing && (
                      <div className="mt-4 p-2 bg-yellow-600 rounded">
                        <Monitor className="w-6 h-6 mx-auto" />
                        <p className="text-sm">Screen sharing active</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Participants (for group calls) */}
            {isGroupCall && (
              <div className="absolute top-4 left-4 bg-black bg-opacity-50 rounded-lg p-3">
                <h4 className="text-white text-sm font-medium mb-2">Participants</h4>
                <div className="space-y-2">
                  {participants.map((participant) => (
                    <div key={participant.id} className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${participant.isSpeaking ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                      <span className="text-white text-xs">{participant.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Picture-in-picture self view */}
            <div className="absolute bottom-4 right-4 w-48 aspect-video bg-gray-800 rounded-lg shadow-lg">
              <div className="w-full h-full bg-gray-800 rounded-lg flex items-center justify-center">
                <div className="text-white text-center">
                  <User className="w-8 h-8 mx-auto mb-2" />
                  <p className="text-xs">Local video</p>
                </div>
              </div>
            </div>

            {/* Enhanced Call Controls */}
            <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex items-center space-x-4">
              <button 
                onClick={() => setIsScreenSharing(!isScreenSharing)}
                className={`p-4 rounded-full ${isScreenSharing ? 'bg-yellow-600' : 'bg-gray-600'} text-white hover:opacity-80`}
              >
                <Monitor className="w-6 h-6" />
              </button>
              <button className="p-4 bg-red-600 text-white rounded-full hover:bg-red-700">
                <Phone className="w-6 h-6" />
              </button>
              <button className="p-4 bg-gray-600 text-white rounded-full hover:bg-gray-700">
                <Settings className="w-6 h-6" />
              </button>
              <button 
                onClick={handleEndCall}
                className="p-4 bg-gray-600 text-white rounded-full hover:bg-gray-700"
              >
                <LogOut className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Visit Summary Modal */}
      {showVisitSummary && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Visit Summary</h3>
              <button 
                onClick={() => setShowVisitSummary(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Diagnosis</label>
                <textarea className="w-full p-3 border border-gray-300 rounded-md" rows="3" placeholder="Enter diagnosis..."></textarea>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Treatment Plan</label>
                <textarea className="w-full p-3 border border-gray-300 rounded-md" rows="3" placeholder="Enter treatment plan..."></textarea>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Prescriptions</label>
                <textarea className="w-full p-3 border border-gray-300 rounded-md" rows="2" placeholder="Enter prescriptions..."></textarea>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Follow-up</label>
                <input type="date" className="w-full p-3 border border-gray-300 rounded-md" />
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button 
                onClick={() => setShowVisitSummary(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2">
                <Send className="w-4 h-4" />
                <span>Send to Patient</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Enhanced Prescription Management with Abena SDK
const PrescriptionManagement = ({ userType }) => {
  const [prescriptions, setPrescriptions] = useState([]);
  const [showNewPrescription, setShowNewPrescription] = useState(false);
  const [loading, setLoading] = useState(false);
  const [newPrescription, setNewPrescription] = useState({
    patient: '',
    medication: '',
    dosage: '',
    duration: '',
    instructions: '',
    pharmacy: ''
  });

  const pharmacies = [
    { id: 1, name: 'CVS Pharmacy', address: '123 Main St, City, State' },
    { id: 2, name: 'Walgreens', address: '456 Oak Ave, City, State' },
    { id: 3, name: 'Rite Aid', address: '789 Pine Rd, City, State' }
  ];

  // Load prescriptions using Abena SDK
  useEffect(() => {
    const loadPrescriptions = async () => {
      try {
        setLoading(true);
        // In a real implementation, you would fetch prescriptions from Abena SDK
        const mockPrescriptions = [
          { id: 1, patient: 'John Doe', medication: 'Amoxicillin 500mg', dosage: '1 capsule 3x daily', duration: '7 days', status: 'sent', date: '2024-01-15' },
          { id: 2, patient: 'Jane Smith', medication: 'Ibuprofen 400mg', dosage: '1 tablet as needed', duration: '10 days', status: 'pending', date: '2024-01-14' }
        ];
        setPrescriptions(mockPrescriptions);
      } catch (error) {
        console.error('Error loading prescriptions:', error);
      } finally {
        setLoading(false);
      }
    };

    loadPrescriptions();
  }, []);

  const handleSubmitPrescription = async () => {
    try {
      setLoading(true);
      
      // Create prescription using Abena SDK
      const prescriptionData = {
        patientId: newPrescription.patient,
        medication: newPrescription.medication,
        dosage: newPrescription.dosage,
        duration: newPrescription.duration,
        instructions: newPrescription.instructions,
        pharmacy: newPrescription.pharmacy
      };

      // For now, create a mock prescription since we need to implement the real API
      const prescription = {
        id: `prescription_${Date.now()}`,
        ...prescriptionData,
        status: 'created',
        createdAt: new Date().toISOString()
      };

      console.log('Prescription created:', prescription);

      // Update local state
      setPrescriptions([prescription, ...prescriptions]);
      setShowNewPrescription(false);
      setNewPrescription({ patient: '', medication: '', dosage: '', duration: '', instructions: '', pharmacy: '' });

    } catch (error) {
      console.error('Error creating prescription:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with New Prescription Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Prescriptions</h2>
        {userType === 'doctor' && (
          <button 
            onClick={() => setShowNewPrescription(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md flex items-center space-x-2 hover:bg-blue-700"
            disabled={loading}
          >
            <Plus className="w-4 h-4" />
            <span>{loading ? 'Processing...' : 'New Prescription'}</span>
          </button>
        )}
      </div>

      {/* Prescriptions List */}
      <Card>
        <CardHeader>
          <CardTitle>Prescriptions</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading prescriptions...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {prescriptions.map((prescription) => (
                <div key={prescription.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <Pill className="w-5 h-5 text-blue-500" />
                      <div>
                        <p className="font-medium">{prescription.medication}</p>
                        <p className="text-sm text-gray-500">Patient: {prescription.patient}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 text-xs rounded ${
                        prescription.status === 'sent' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {prescription.status === 'sent' ? 'Sent' : 'Pending'}
                      </span>
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Dosage:</span> {prescription.dosage}
                    </div>
                    <div>
                      <span className="font-medium">Duration:</span> {prescription.duration}
                    </div>
                  </div>
                  <div className="mt-3 text-xs text-gray-500">
                    Date: {prescription.date}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* New Prescription Modal */}
      {showNewPrescription && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">New Prescription</h3>
              <button 
                onClick={() => setShowNewPrescription(false)}
                className="text-gray-400 hover:text-gray-600"
                disabled={loading}
              >
                ×
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Patient</label>
                <input 
                  type="text" 
                  value={newPrescription.patient}
                  onChange={(e) => setNewPrescription({...newPrescription, patient: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  placeholder="Patient name"
                  disabled={loading}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Medication</label>
                <input 
                  type="text" 
                  value={newPrescription.medication}
                  onChange={(e) => setNewPrescription({...newPrescription, medication: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  placeholder="Medication name and strength"
                  disabled={loading}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Dosage</label>
                  <input 
                    type="text" 
                    value={newPrescription.dosage}
                    onChange={(e) => setNewPrescription({...newPrescription, dosage: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    placeholder="e.g., 1 tablet 3x daily"
                    disabled={loading}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Duration</label>
                  <input 
                    type="text" 
                    value={newPrescription.duration}
                    onChange={(e) => setNewPrescription({...newPrescription, duration: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    placeholder="e.g., 7 days"
                    disabled={loading}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Special Instructions</label>
                <textarea 
                  value={newPrescription.instructions}
                  onChange={(e) => setNewPrescription({...newPrescription, instructions: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  rows="3"
                  placeholder="Any special instructions..."
                  disabled={loading}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Pharmacy</label>
                <select 
                  value={newPrescription.pharmacy}
                  onChange={(e) => setNewPrescription({...newPrescription, pharmacy: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  disabled={loading}
                >
                  <option value="">Select a pharmacy</option>
                  {pharmacies.map(pharmacy => (
                    <option key={pharmacy.id} value={pharmacy.name}>
                      {pharmacy.name} - {pharmacy.address}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button 
                onClick={() => setShowNewPrescription(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                onClick={handleSubmitPrescription}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
                disabled={loading}
              >
                <Send className="w-4 h-4" />
                <span>{loading ? 'Sending...' : 'Send to Pharmacy'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Enhanced Lab Request Management with Abena SDK
const LabRequestManagement = ({ userType }) => {
  const [labRequests, setLabRequests] = useState([]);
  const [showNewRequest, setShowNewRequest] = useState(false);
  const [loading, setLoading] = useState(false);
  const [newRequest, setNewRequest] = useState({
    patient: '',
    test: '',
    lab: '',
    notes: '',
    priority: 'routine'
  });

  const availableTests = [
    'Complete Blood Count (CBC)',
    'Comprehensive Metabolic Panel (CMP)',
    'Lipid Panel',
    'Thyroid Function Test',
    'Hemoglobin A1C',
    'Urinalysis',
    'Chest X-Ray',
    'Electrocardiogram (ECG)'
  ];

  const laboratories = [
    { id: 1, name: 'LabCorp', address: '123 Medical Center Dr' },
    { id: 2, name: 'Quest Diagnostics', address: '456 Health Plaza' },
    { id: 3, name: 'BioReference Laboratories', address: '789 Lab Way' }
  ];

  // Load lab requests using Abena SDK
  useEffect(() => {
    const loadLabRequests = async () => {
      try {
        setLoading(true);
        // In a real implementation, you would fetch lab requests from Abena SDK
        const mockRequests = [
          { id: 1, patient: 'John Doe', test: 'Complete Blood Count (CBC)', lab: 'LabCorp', status: 'sent', date: '2024-01-15' },
          { id: 2, patient: 'Jane Smith', test: 'Lipid Panel', lab: 'Quest Diagnostics', status: 'pending', date: '2024-01-14' }
        ];
        setLabRequests(mockRequests);
      } catch (error) {
        console.error('Error loading lab requests:', error);
      } finally {
        setLoading(false);
      }
    };

    loadLabRequests();
  }, []);

  const handleSubmitLabRequest = async () => {
    try {
      setLoading(true);
      
      // Create lab request data
      const labRequestData = {
        patientId: newRequest.patient,
        testType: newRequest.test,
        laboratory: newRequest.lab,
        notes: newRequest.notes,
        priority: newRequest.priority
      };

      // For now, create a mock lab request since we need to implement the real API
      const labRequest = {
        id: `lab_request_${Date.now()}`,
        ...labRequestData,
        status: 'created',
        createdAt: new Date().toISOString()
      };

      console.log('Lab request created:', labRequest);

      // Update local state
      setLabRequests([labRequest, ...labRequests]);
      setShowNewRequest(false);
      setNewRequest({ patient: '', test: '', lab: '', notes: '', priority: 'routine' });

    } catch (error) {
      console.error('Error creating lab request:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with New Request Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Lab Requests</h2>
        {userType === 'doctor' && (
          <button 
            onClick={() => setShowNewRequest(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md flex items-center space-x-2 hover:bg-blue-700"
            disabled={loading}
          >
            <Plus className="w-4 h-4" />
            <span>{loading ? 'Processing...' : 'New Lab Request'}</span>
          </button>
        )}
      </div>

      {/* Lab Requests List */}
      <Card>
        <CardHeader>
          <CardTitle>Lab Requests</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading lab requests...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {labRequests.map((request) => (
                <div key={request.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <FlaskConical className="w-5 h-5 text-blue-500" />
                      <div>
                        <p className="font-medium">{request.test}</p>
                        <p className="text-sm text-gray-500">Patient: {request.patient}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 text-xs rounded ${
                        request.status === 'sent' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {request.status === 'sent' ? 'Sent' : 'Pending'}
                      </span>
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Laboratory:</span> {request.lab}
                    </div>
                    <div>
                      <span className="font-medium">Date:</span> {request.date}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* New Lab Request Modal */}
      {showNewRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">New Lab Request</h3>
              <button 
                onClick={() => setShowNewRequest(false)}
                className="text-gray-400 hover:text-gray-600"
                disabled={loading}
              >
                ×
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Patient</label>
                <input 
                  type="text" 
                  value={newRequest.patient}
                  onChange={(e) => setNewRequest({...newRequest, patient: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  placeholder="Patient name"
                  disabled={loading}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Test Type</label>
                <select 
                  value={newRequest.test}
                  onChange={(e) => setNewRequest({...newRequest, test: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  disabled={loading}
                >
                  <option value="">Select a test</option>
                  {availableTests.map(test => (
                    <option key={test} value={test}>{test}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Laboratory</label>
                <select 
                  value={newRequest.lab}
                  onChange={(e) => setNewRequest({...newRequest, lab: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  disabled={loading}
                >
                  <option value="">Select a laboratory</option>
                  {laboratories.map(lab => (
                    <option key={lab.id} value={lab.name}>
                      {lab.name} - {lab.address}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                <select 
                  value={newRequest.priority}
                  onChange={(e) => setNewRequest({...newRequest, priority: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  disabled={loading}
                >
                  <option value="routine">Routine</option>
                  <option value="urgent">Urgent</option>
                  <option value="stat">STAT</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Clinical Notes</label>
                <textarea 
                  value={newRequest.notes}
                  onChange={(e) => setNewRequest({...newRequest, notes: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  rows="3"
                  placeholder="Clinical notes or special instructions..."
                  disabled={loading}
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button 
                onClick={() => setShowNewRequest(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                onClick={handleSubmitLabRequest}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
                disabled={loading}
              >
                <Send className="w-4 h-4" />
                <span>{loading ? 'Sending...' : 'Send to Laboratory'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Lab Results View Component (for patients)
const LabResultsView = ({ userType }) => {
  const [labResults] = useState([
    { id: 1, test: 'Complete Blood Count (CBC)', date: '2024-01-15', status: 'completed', lab: 'LabCorp' },
    { id: 2, test: 'Lipid Panel', date: '2024-01-10', status: 'completed', lab: 'Quest Diagnostics' },
    { id: 3, test: 'Thyroid Function Test', date: '2024-01-05', status: 'pending', lab: 'LabCorp' }
  ]);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Lab Results</h2>
      
      <Card>
        <CardHeader>
          <CardTitle>My Lab Results</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {labResults.map((result) => (
              <div key={result.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <FlaskConical className="w-5 h-5 text-blue-500" />
                    <div>
                      <p className="font-medium">{result.test}</p>
                      <p className="text-sm text-gray-500">Lab: {result.lab}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded ${
                      result.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {result.status === 'completed' ? 'Completed' : 'Pending'}
                    </span>
                    {result.status === 'completed' && (
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <Eye className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
                <div className="text-sm text-gray-500">
                  Date: {result.date}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Settings Panel Component
const SettingsPanel = ({ userType }) => {
  const [settings, setSettings] = useState({
    notifications: true,
    emailAlerts: true,
    privacyMode: false,
    language: 'English',
    theme: 'Light',
    autoSave: true,
    dataSharing: false
  });

  const handleSaveSettings = () => {
    // In a real app, you would save settings to backend
    console.log('Saving settings:', settings);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Settings</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Notifications */}
        <Card>
          <CardHeader>
            <CardTitle>Notifications</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.notifications}
                onChange={(e) => setSettings({...settings, notifications: e.target.checked})}
                className="rounded"
              />
              <span>Push notifications</span>
            </label>
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.emailAlerts}
                onChange={(e) => setSettings({...settings, emailAlerts: e.target.checked})}
                className="rounded"
              />
              <span>Email alerts</span>
            </label>
          </CardContent>
        </Card>

        {/* Privacy */}
        <Card>
          <CardHeader>
            <CardTitle>Privacy & Security</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.privacyMode}
                onChange={(e) => setSettings({...settings, privacyMode: e.target.checked})}
                className="rounded"
              />
              <span>Enhanced privacy mode</span>
            </label>
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={settings.dataSharing}
                onChange={(e) => setSettings({...settings, dataSharing: e.target.checked})}
                className="rounded"
              />
              <span>Allow data sharing for research</span>
            </label>
          </CardContent>
        </Card>

        {/* Preferences */}
        <Card>
          <CardHeader>
            <CardTitle>Preferences</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
              <select
                value={settings.language}
                onChange={(e) => setSettings({...settings, language: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-md"
              >
                <option value="English">English</option>
                <option value="Spanish">Spanish</option>
                <option value="French">French</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
              <select
                value={settings.theme}
                onChange={(e) => setSettings({...settings, theme: e.target.value})}
                className="w-full p-3 border border-gray-300 rounded-md"
              >
                <option value="Light">Light</option>
                <option value="Dark">Dark</option>
                <option value="Auto">Auto</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Account */}
        <Card>
          <CardHeader>
            <CardTitle>Account</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
                <User className="w-6 h-6 text-gray-600" />
              </div>
              <div>
                <p className="font-medium">{userType === 'doctor' ? 'Dr. Smith' : 'John Doe'}</p>
                <p className="text-sm text-gray-500">{userType === 'doctor' ? 'Cardiologist' : 'Patient'}</p>
              </div>
            </div>
            <button className="w-full px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
              Change Password
            </button>
            <button className="w-full px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
              Update Profile
            </button>
          </CardContent>
        </Card>
      </div>

      <div className="flex justify-end">
        <button 
          onClick={handleSaveSettings}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
        >
          <Save className="w-4 h-4" />
          <span>Save Settings</span>
        </button>
      </div>
    </div>
  );
};

// Messages Panel Component
const MessagesPanel = ({ userType }) => {
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [conversations] = useState([
    { id: 1, name: 'Dr. Smith', lastMessage: 'How are you feeling today?', time: '2 hours ago', unread: true },
    { id: 2, name: 'Nurse Johnson', lastMessage: 'Your appointment is confirmed', time: '1 day ago', unread: false },
    { id: 3, name: 'Lab Results', lastMessage: 'Your blood work results are ready', time: '2 days ago', unread: false }
  ]);

  const sendMessage = () => {
    if (newMessage.trim()) {
      console.log('Sending message:', newMessage);
      setNewMessage('');
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Messages</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Conversations List */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Conversations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {conversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    onClick={() => setSelectedConversation(conversation)}
                    className={`p-3 rounded-lg cursor-pointer ${
                      selectedConversation?.id === conversation.id ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50'
                    } ${conversation.unread ? 'border-l-4 border-blue-500' : ''}`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                        <User className="w-5 h-5 text-gray-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-800">{conversation.name}</p>
                        <p className="text-sm text-gray-600 truncate">{conversation.lastMessage}</p>
                        <p className="text-xs text-gray-500">{conversation.time}</p>
                      </div>
                      {conversation.unread && (
                        <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Message Detail */}
        <div className="lg:col-span-2">
          <Card className="h-96">
            {selectedConversation ? (
              <div className="h-full flex flex-col">
                <CardHeader className="border-b">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                      <User className="w-5 h-5 text-gray-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{selectedConversation.name}</CardTitle>
                      <p className="text-sm text-gray-500">{selectedConversation.time}</p>
                    </div>
                  </div>
                </CardHeader>
                
                <div className="flex-1 p-4 overflow-y-auto">
                  <div className="bg-gray-100 p-3 rounded-lg mb-4">
                    <p className="text-gray-800">{selectedConversation.lastMessage}</p>
                  </div>
                </div>
                
                <CardContent className="border-t">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Type your message..."
                      className="flex-1 p-3 border border-gray-300 rounded-md"
                      onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    />
                    <button
                      onClick={sendMessage}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </CardContent>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <MessageSquare className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Select a conversation to start messaging</p>
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userType, setUserType] = useState('doctor');
  const [currentUser, setCurrentUser] = useState(null);
  const [abenaSDK, setAbenaSDK] = useState(null);

  // Check for existing authentication on app load
  useEffect(() => {
    const savedUserType = localStorage.getItem('abena_user_type');
    const savedUserData = localStorage.getItem('abena_user_data');
    const savedToken = localStorage.getItem('abena_token');
    
    if (savedUserType && savedUserData && savedToken) {
      try {
        setUserType(savedUserType);
        setCurrentUser(JSON.parse(savedUserData));
        setIsLoggedIn(true);
        
        // Recreate SDK instance
        const sdkInstance = new RealAbenaSDK();
        setAbenaSDK(sdkInstance);
      } catch (error) {
        console.error('Error restoring authentication:', error);
        // Clear invalid data
        localStorage.removeItem('abena_user_type');
        localStorage.removeItem('abena_user_data');
        localStorage.removeItem('abena_token');
        localStorage.removeItem('abena_user');
      }
    }
  }, []);

  const handleLogin = (type, credentials, sdkInstance, authResult) => {
    console.log('Login successful:', authResult);
    setUserType(type);
    setCurrentUser(authResult.user);
    setAbenaSDK(sdkInstance);
    setIsLoggedIn(true);
    
    // Store authentication data in localStorage for persistence
    localStorage.setItem('abena_user_type', type);
    localStorage.setItem('abena_user_data', JSON.stringify(authResult.user));
    localStorage.setItem('abena_token', authResult.token);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserType('doctor');
    setCurrentUser(null);
    setAbenaSDK(null);
    
    // Clear authentication data from localStorage
    localStorage.removeItem('abena_user_type');
    localStorage.removeItem('abena_user_data');
    localStorage.removeItem('abena_token');
    localStorage.removeItem('abena_user');
  };

  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={
            isLoggedIn ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <LoginPage onLogin={handleLogin} />
            )
          } 
        />
        <Route 
          path="/login" 
          element={
            isLoggedIn ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <LoginPage onLogin={handleLogin} />
            )
          } 
        />
        <Route 
          path="/dashboard" 
          element={
            isLoggedIn ? (
              <DashboardLayout userType={userType} onLogout={handleLogout} currentUser={currentUser} abenaSDK={abenaSDK}>
                <DashboardContent userType={userType} currentUser={currentUser} abenaSDK={abenaSDK} />
              </DashboardLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        <Route 
          path="/appointments" 
          element={
            isLoggedIn ? (
              <DashboardLayout userType={userType} onLogout={handleLogout} currentUser={currentUser} abenaSDK={abenaSDK}>
                <AppointmentsPanel userType={userType} />
              </DashboardLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        <Route 
          path="/video-consults" 
          element={
            isLoggedIn ? (
              <DashboardLayout userType={userType} onLogout={handleLogout} currentUser={currentUser} abenaSDK={abenaSDK}>
                <VideoConsultation userType={userType} />
              </DashboardLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        <Route 
          path="/prescriptions" 
          element={
            isLoggedIn ? (
              <DashboardLayout userType={userType} onLogout={handleLogout} currentUser={currentUser} abenaSDK={abenaSDK}>
                <PrescriptionManagement userType={userType} />
              </DashboardLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        <Route 
          path="/lab-results" 
          element={
            isLoggedIn ? (
              <DashboardLayout userType={userType} onLogout={handleLogout} currentUser={currentUser} abenaSDK={abenaSDK}>
                <LabResultsView userType={userType} />
              </DashboardLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        <Route 
          path="/wearable-devices" 
          element={
            isLoggedIn ? (
              <DashboardLayout userType={userType} onLogout={handleLogout} currentUser={currentUser} abenaSDK={abenaSDK}>
                <WearableDeviceManager userType={userType} />
              </DashboardLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        <Route 
          path="/documents" 
          element={
            isLoggedIn ? (
              <DashboardLayout userType={userType} onLogout={handleLogout} currentUser={currentUser} abenaSDK={abenaSDK}>
                <DocumentManagement userType={userType} />
              </DashboardLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        <Route 
          path="/my-records" 
          element={
            isLoggedIn ? (
              <DashboardLayout userType={userType} onLogout={handleLogout} currentUser={currentUser} abenaSDK={abenaSDK}>
                <MyRecordsPanel userType={userType} />
              </DashboardLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        <Route 
          path="/messages" 
          element={
            isLoggedIn ? (
              <DashboardLayout userType={userType} onLogout={handleLogout} currentUser={currentUser} abenaSDK={abenaSDK}>
                <MessagesPanel userType={userType} />
              </DashboardLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        <Route 
          path="/my-vitals" 
          element={
            isLoggedIn ? (
              <DashboardLayout userType={userType} onLogout={handleLogout} currentUser={currentUser} abenaSDK={abenaSDK}>
                <MyVitalsPanel userType={userType} />
              </DashboardLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        <Route 
          path="/settings" 
          element={
            isLoggedIn ? (
              <DashboardLayout userType={userType} onLogout={handleLogout} currentUser={currentUser} abenaSDK={abenaSDK}>
                <SettingsPanel userType={userType} />
              </DashboardLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          } 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

// My Records Panel Component
const MyRecordsPanel = ({ userType }) => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        // In a real app, you would fetch medical records from the backend
        const mockRecords = [
          {
            id: 1,
            type: 'Medical History',
            date: '2024-01-15',
            provider: 'Dr. Smith',
            status: 'Complete',
            description: 'Complete medical history and physical examination'
          },
          {
            id: 2,
            type: 'Lab Report',
            date: '2024-01-10',
            provider: 'Quest Diagnostics',
            status: 'Complete',
            description: 'Blood work and metabolic panel results'
          },
          {
            id: 3,
            type: 'Imaging Report',
            date: '2024-01-08',
            provider: 'Radiology Associates',
            status: 'Complete',
            description: 'Chest X-ray and CT scan results'
          }
        ];
        setRecords(mockRecords);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching records:', error);
        setLoading(false);
      }
    };

    fetchRecords();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Records</h1>
          <p className="text-gray-600">View and manage your medical records</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
          Request Records
        </button>
      </div>

      {/* Records List */}
      <div className="bg-white rounded-lg border">
        <div className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Medical Records</h2>
          {records.length > 0 ? (
            <div className="space-y-4">
              {records.map((record) => (
                <div key={record.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Archive className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{record.type}</h3>
                      <p className="text-sm text-gray-600">Date: {record.date}</p>
                      <p className="text-sm text-gray-600">Provider: {record.provider}</p>
                      <p className="text-sm text-gray-600">{record.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                      {record.status}
                    </span>
                    <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
                      View
                    </button>
                    <button className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700">
                      Download
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Archive className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No medical records found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// My Vitals Panel Component
const MyVitalsPanel = ({ userType }) => {
  const [vitals, setVitals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchVitals = async () => {
      try {
        // In a real app, you would fetch vital signs from the backend
        const mockVitals = [
          {
            id: 1,
            type: 'Blood Pressure',
            value: '120/80',
            unit: 'mmHg',
            date: '2024-01-15',
            time: '10:30 AM',
            status: 'Normal',
            trend: 'stable'
          },
          {
            id: 2,
            type: 'Heart Rate',
            value: '72',
            unit: 'bpm',
            date: '2024-01-15',
            time: '10:30 AM',
            status: 'Normal',
            trend: 'stable'
          },
          {
            id: 3,
            type: 'Temperature',
            value: '98.6',
            unit: '°F',
            date: '2024-01-15',
            time: '10:30 AM',
            status: 'Normal',
            trend: 'stable'
          },
          {
            id: 4,
            type: 'Oxygen Saturation',
            value: '98',
            unit: '%',
            date: '2024-01-15',
            time: '10:30 AM',
            status: 'Normal',
            trend: 'stable'
          }
        ];
        setVitals(mockVitals);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching vitals:', error);
        setLoading(false);
      }
    };

    fetchVitals();
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Normal': return 'bg-green-100 text-green-800';
      case 'High': return 'bg-red-100 text-red-800';
      case 'Low': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Vitals</h1>
          <p className="text-gray-600">Monitor your vital signs and health metrics</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
          + Add Reading
        </button>
      </div>

      {/* Vitals Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {vitals.map((vital) => (
          <div key={vital.id} className="bg-white p-6 rounded-lg border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-gray-900">{vital.type}</h3>
              <Activity className="w-5 h-5 text-blue-600" />
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900 mb-2">
                {vital.value}
                <span className="text-lg text-gray-600 ml-1">{vital.unit}</span>
              </div>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(vital.status)}`}>
                {vital.status}
              </span>
            </div>
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-600">{vital.date} at {vital.time}</p>
              <p className="text-sm text-gray-500">Trend: {vital.trend}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Vitals History */}
      <div className="bg-white rounded-lg border">
        <div className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Vitals History</h2>
          <div className="space-y-4">
            {vitals.map((vital) => (
              <div key={vital.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Activity className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-900">{vital.type}</p>
                    <p className="text-sm text-gray-600">{vital.date} at {vital.time}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="font-medium text-gray-900">{vital.value} {vital.unit}</span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(vital.status)}`}>
                    {vital.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Appointments Panel Component
const AppointmentsPanel = ({ userType }) => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'calendar'

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        // In a real app, you would fetch appointments from the backend
        const mockAppointments = [
          {
            id: 1,
            patientName: 'John Smith',
            patientId: 'P001',
            date: '2024-01-15',
            time: '10:00 AM',
            type: 'Follow-up',
            status: 'confirmed',
            notes: 'Regular checkup'
          },
          {
            id: 2,
            patientName: 'Sarah Johnson',
            patientId: 'P002',
            date: '2024-01-15',
            time: '2:30 PM',
            type: 'Consultation',
            status: 'pending',
            notes: 'New patient consultation'
          },
          {
            id: 3,
            patientName: 'Mike Wilson',
            patientId: 'P003',
            date: '2024-01-16',
            time: '9:00 AM',
            type: 'Emergency',
            status: 'confirmed',
            notes: 'Urgent care needed'
          }
        ];
        setAppointments(mockAppointments);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching appointments:', error);
        setLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  const handleStatusChange = (appointmentId, newStatus) => {
    setAppointments(prev => 
      prev.map(apt => 
        apt.id === appointmentId ? { ...apt, status: newStatus } : apt
      )
    );
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Appointments</h1>
          <p className="text-gray-600">Manage patient appointments and schedules</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setViewMode('list')}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              viewMode === 'list' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            List View
          </button>
          <button
            onClick={() => setViewMode('calendar')}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              viewMode === 'calendar' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Calendar View
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
            + New Appointment
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border">
        <div className="flex space-x-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input
              type="date"
              value={selectedDate.toISOString().split('T')[0]}
              onChange={(e) => setSelectedDate(new Date(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">All Status</option>
              <option value="confirmed">Confirmed</option>
              <option value="pending">Pending</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">All Types</option>
              <option value="consultation">Consultation</option>
              <option value="follow-up">Follow-up</option>
              <option value="emergency">Emergency</option>
            </select>
          </div>
        </div>
      </div>

      {/* Appointments List */}
      <div className="bg-white rounded-lg border">
        <div className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Today's Appointments</h2>
          {appointments.length > 0 ? (
            <div className="space-y-4">
              {appointments.map((appointment) => (
                <div key={appointment.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Calendar className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{appointment.patientName}</h3>
                      <p className="text-sm text-gray-600">ID: {appointment.patientId}</p>
                      <p className="text-sm text-gray-600">{appointment.date} at {appointment.time}</p>
                      <p className="text-sm text-gray-600">{appointment.notes}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(appointment.status)}`}>
                      {appointment.status}
                    </span>
                    <select
                      value={appointment.status}
                      onChange={(e) => handleStatusChange(appointment.id, e.target.value)}
                      className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="confirmed">Confirmed</option>
                      <option value="pending">Pending</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                    <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
                      View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No appointments scheduled for today</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Patients Panel Component
const PatientsPanel = ({ userType }) => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        // In a real app, you would fetch patients from the backend
        const mockPatients = [
          {
            id: 'P001',
            name: 'John Smith',
            age: 45,
            gender: 'Male',
            email: 'john.smith@email.com',
            phone: '+1-555-0123',
            status: 'active',
            lastVisit: '2024-01-10',
            nextAppointment: '2024-01-20'
          },
          {
            id: 'P002',
            name: 'Sarah Johnson',
            age: 32,
            gender: 'Female',
            email: 'sarah.johnson@email.com',
            phone: '+1-555-0124',
            status: 'active',
            lastVisit: '2024-01-12',
            nextAppointment: '2024-01-18'
          },
          {
            id: 'P003',
            name: 'Mike Wilson',
            age: 28,
            gender: 'Male',
            email: 'mike.wilson@email.com',
            phone: '+1-555-0125',
            status: 'inactive',
            lastVisit: '2023-12-15',
            nextAppointment: null
          }
        ];
        setPatients(mockPatients);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching patients:', error);
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  const filteredPatients = patients.filter(patient => {
    const matchesSearch = patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         patient.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         patient.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || patient.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Patients</h1>
          <p className="text-gray-600">Manage patient records and information</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
          + Add Patient
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border">
        <div className="flex space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search by name, email, or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select 
              value={filterStatus} 
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>
      </div>

      {/* Patients List */}
      <div className="bg-white rounded-lg border">
        <div className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Patient Records ({filteredPatients.length})</h2>
          {filteredPatients.length > 0 ? (
            <div className="space-y-4">
              {filteredPatients.map((patient) => (
                <div key={patient.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Users className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{patient.name}</h3>
                      <p className="text-sm text-gray-600">ID: {patient.id} | Age: {patient.age} | {patient.gender}</p>
                      <p className="text-sm text-gray-600">{patient.email} | {patient.phone}</p>
                      <p className="text-sm text-gray-600">Last Visit: {patient.lastVisit}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(patient.status)}`}>
                      {patient.status}
                    </span>
                    {patient.nextAppointment && (
                      <span className="text-sm text-gray-600">
                        Next: {patient.nextAppointment}
                      </span>
                    )}
                    <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
                      View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No patients found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Doctors Panel Component
const DoctorsPanel = ({ userType }) => {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSpecialty, setFilterSpecialty] = useState('all');

  useEffect(() => {
    const fetchDoctors = async () => {
      try {
        // In a real app, you would fetch doctors from the backend
        const mockDoctors = [
          {
            id: 'D001',
            name: 'Dr. Emily Martinez',
            specialty: 'Cardiology',
            email: 'emily.martinez@clinic.com',
            phone: '+1-555-0201',
            status: 'active',
            patients: 45,
            availability: 'Mon-Fri 9AM-5PM'
          },
          {
            id: 'D002',
            name: 'Dr. Robert Chen',
            specialty: 'Neurology',
            email: 'robert.chen@clinic.com',
            phone: '+1-555-0202',
            status: 'active',
            patients: 38,
            availability: 'Mon-Thu 10AM-6PM'
          },
          {
            id: 'D003',
            name: 'Dr. Lisa Thompson',
            specialty: 'Pediatrics',
            email: 'lisa.thompson@clinic.com',
            phone: '+1-555-0203',
            status: 'active',
            patients: 52,
            availability: 'Mon-Fri 8AM-4PM'
          }
        ];
        setDoctors(mockDoctors);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching doctors:', error);
        setLoading(false);
      }
    };

    fetchDoctors();
  }, []);

  const filteredDoctors = doctors.filter(doctor => {
    const matchesSearch = doctor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doctor.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doctor.specialty.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSpecialty = filterSpecialty === 'all' || doctor.specialty === filterSpecialty;
    return matchesSearch && matchesSpecialty;
  });

  const specialties = [...new Set(doctors.map(doctor => doctor.specialty))];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Doctors</h1>
          <p className="text-gray-600">Manage doctor profiles and schedules</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
          + Add Doctor
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border">
        <div className="flex space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              placeholder="Search by name, email, or specialty..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Specialty</label>
            <select 
              value={filterSpecialty} 
              onChange={(e) => setFilterSpecialty(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Specialties</option>
              {specialties.map(specialty => (
                <option key={specialty} value={specialty}>{specialty}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Doctors List */}
      <div className="bg-white rounded-lg border">
        <div className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Doctor Profiles ({filteredDoctors.length})</h2>
          {filteredDoctors.length > 0 ? (
            <div className="space-y-4">
              {filteredDoctors.map((doctor) => (
                <div key={doctor.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                      <UserCheck className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{doctor.name}</h3>
                      <p className="text-sm text-gray-600">ID: {doctor.id} | {doctor.specialty}</p>
                      <p className="text-sm text-gray-600">{doctor.email} | {doctor.phone}</p>
                      <p className="text-sm text-gray-600">Patients: {doctor.patients} | Availability: {doctor.availability}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                      {doctor.status}
                    </span>
                    <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
                      View Schedule
                    </button>
                    <button className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700">
                      Edit Profile
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <UserCheck className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No doctors found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App; 