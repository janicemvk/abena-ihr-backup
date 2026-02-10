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
  Archive,
  Stethoscope,
  DollarSign,
  Edit,
  Trash2
} from 'lucide-react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';
import PaymentForm from './components/PaymentForm';

// Initialize Stripe with your real test public key
const stripePromise = loadStripe('pk_test_mtu5IaBaufMduJaucUsR52f700ehQf34ZB');

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
        authServiceUrl: 'http://138.68.24.154:4002',
        dataServiceUrl: 'http://138.68.24.154:4001'
      });

      console.log('📡 Calling authentication API...');
      const authResult = await abenaSDK.authenticate({
        email: credentials.email,
        password: credentials.password
      });

      console.log('✅ Authentication successful:', authResult);

      // Check if the authenticated user type matches the selected user type
      if (authResult.userType !== userType) {
        throw new Error(`You selected ${userType} but your account is registered as ${authResult.userType}. Please select the correct user type.`);
      }

      // Pass the authenticated SDK instance to the main app
      onLogin(authResult.userType, credentials, abenaSDK, authResult);
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
                onClick={() => setUserType('provider')}
                className={`flex-1 py-2 px-4 rounded-md border-2 transition-colors ${
                  userType === 'provider' 
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
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);

  // Get current active menu from URL path
  const getActiveMenu = () => {
    const path = location.pathname;
    if (path === '/dashboard') return 'dashboard';
    if (path === '/appointments') return 'appointments';
    if (path === '/video-consults') return 'video-consults';
    if (path === '/prescriptions') return 'prescriptions';
    if (path === '/lab-results') return 'lab-results';
    if (path === '/wearable-devices') return 'wearable-devices';
    if (path === '/documents') return 'documents';
    if (path === '/my-records') return 'my-records';
    if (path === '/messages') return 'messages';
    if (path === '/my-vitals') return 'my-vitals';
    if (path === '/settings') return 'settings';
    return 'dashboard';
  };

  const activeMenu = getActiveMenu();

  const handleMenuClick = (menu) => {
    navigate(`/${menu}`);
  };

  const handleLogout = () => {
    localStorage.removeItem('abena_token');
    localStorage.removeItem('user_type');
    localStorage.removeItem('current_user');
    navigate('/');
  };

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.dropdown-container')) {
        setShowNotifications(false);
        setShowUserDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Update page title
  useEffect(() => {
    const pageTitle = activeMenu.charAt(0).toUpperCase() + activeMenu.slice(1);
    const portalType = userType === 'provider' ? 'Provider Portal' : 'Patient Portal';
    document.title = `${pageTitle} - ${portalType}`;
  }, [activeMenu, userType]);

  // Mock notifications data
  const notifications = [
    { id: 1, title: 'Appointment Reminder', message: 'Your appointment is in 30 minutes', time: '2 min ago', unread: true },
    { id: 2, title: 'Lab Results Ready', message: 'Your blood work results are available', time: '1 hour ago', unread: true },
    { id: 3, title: 'Prescription Update', message: 'Your prescription has been renewed', time: '3 hours ago', unread: false }
  ];

  return (
    <div className="App">
      <div className="flex h-screen bg-gray-100">
        {/* Header */}
        <div className="fixed top-0 left-0 right-0 bg-white shadow-sm border-b px-6 py-4 z-10">
          <div className="flex items-center justify-between">
            {/* Left side - Portal Title */}
            <div className="flex items-center">
              <h1 className="text-lg font-semibold text-gray-800">
                {userType === 'provider' ? 'Provider Portal' : 'Patient Portal'}
              </h1>
          </div>

            {/* Center - Page Title */}
            <div className="absolute left-1/2 transform -translate-x-1/2 flex items-center">
              <h2 className="text-lg font-semibold text-gray-800">
                {activeMenu.charAt(0).toUpperCase() + activeMenu.slice(1)}
              </h2>
            </div>

            {/* Right side - Notifications, Messages, User */}
            <div className="flex items-center space-x-4">
              {/* Notifications Dropdown */}
              <div className="relative dropdown-container">
                <button 
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="p-2 text-gray-400 hover:text-gray-500 relative"
                >
                  <Bell className="w-5 h-5" />
                  <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
                </button>
                
                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
                    <div className="p-4 border-b border-gray-200">
                      <h3 className="text-sm font-semibold text-gray-800">Notifications</h3>
                    </div>
                    <div className="max-h-64 overflow-y-auto">
                      {notifications.map((notification) => (
                        <div key={notification.id} className={`p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${notification.unread ? 'bg-blue-50' : ''}`}>
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <p className="text-sm font-medium text-gray-800">{notification.title}</p>
                              <p className="text-xs text-gray-600 mt-1">{notification.message}</p>
                              <p className="text-xs text-gray-500 mt-1">{notification.time}</p>
                            </div>
                            {notification.unread && (
                              <div className="w-2 h-2 bg-blue-500 rounded-full ml-2"></div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="p-3 border-t border-gray-200">
                      <button className="text-sm text-blue-600 hover:text-blue-800 w-full text-center">
                        View All Notifications
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Messages Button */}
              <button
                onClick={() => setShowMessages(true)}
                className="p-2 text-gray-400 hover:text-gray-500 relative"
              >
                <MessageCircle className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full"></span>
              </button>

              {/* User Dropdown */}
              <div className="relative dropdown-container">
                <button 
                  onClick={() => setShowUserDropdown(!showUserDropdown)}
                  className="flex items-center space-x-2 p-2 text-gray-600 hover:text-gray-800 rounded-lg hover:bg-gray-100"
                >
                  <User className="w-4 h-4" />
                  <span className="text-sm font-medium">{currentUser?.name || 'John Doe'}</span>
                  <ChevronDown className="w-4 h-4" />
                </button>
                
                {showUserDropdown && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
                    <div className="py-2">
                      <div className="px-4 py-2 text-sm text-gray-700 border-b border-gray-100">
                        <p className="font-medium">{currentUser?.name || 'John Doe'}</p>
                        <p className="text-gray-500">{userType}</p>
                      </div>
                      <button
                        onClick={() => {
                          setShowSettings(true);
                          setShowUserDropdown(false);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                      >
                        <Settings className="w-4 h-4" />
                        <span>Settings</span>
                      </button>
                      <button
                        onClick={handleLogout}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
                      >
                        <LogOut className="w-4 h-4" />
                        <span>Logout</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="w-64 bg-gray-100 shadow-lg mt-16">
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
                {userType === 'provider' ? 'Provider Dashboard' : 'Dashboard'}
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
                {userType === 'provider' ? 'Patient Appointments' : 'Appointments'}
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
                {userType === 'provider' ? 'Manage Prescriptions' : 'Prescriptions'}
              </button>

              {userType === 'provider' && (
                <button
                  onClick={() => handleMenuClick('lab-requests')}
                  className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    activeMenu === 'lab-requests'
                      ? 'bg-blue-50 text-blue-600 border border-blue-200'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <FlaskConical className="w-5 h-5 mr-3" />
                  Lab Requests
                </button>
              )}

              {userType === 'patient' && (
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
              )}

              {userType === 'provider' && (
                <button
                  onClick={() => handleMenuClick('my-patients')}
                  className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    activeMenu === 'my-patients'
                      ? 'bg-blue-50 text-blue-600 border border-blue-200'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Users className="w-5 h-5 mr-3" />
                  My Patients
                </button>
              )}

              {userType === 'provider' && (
                <button
                  onClick={() => handleMenuClick('earnings')}
                  className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    activeMenu === 'earnings'
                      ? 'bg-blue-50 text-blue-600 border border-blue-200'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <TrendingUp className="w-5 h-5 mr-3" />
                  Earnings
                </button>
              )}

              {userType === 'provider' && (
                <button
                  onClick={() => handleMenuClick('wearable-data')}
                  className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    activeMenu === 'wearable-data'
                      ? 'bg-blue-50 text-blue-600 border border-blue-200'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Watch className="w-5 h-5 mr-3" />
                  Wearable Data
                </button>
              )}

              {userType === 'patient' && (
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
              )}

              <button
                onClick={() => handleMenuClick('documents')}
                className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                  activeMenu === 'documents'
                    ? 'bg-blue-50 text-blue-600 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <FileText className="w-5 h-5 mr-3" />
                {userType === 'provider' ? 'Patient Documents' : 'Documents'}
              </button>

              {userType === 'provider' && (
                <button
                  onClick={() => handleMenuClick('medical-records')}
                  className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    activeMenu === 'medical-records'
                      ? 'bg-blue-50 text-blue-600 border border-blue-200'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <FileText className="w-5 h-5 mr-3" />
                  Medical Records
                </button>
              )}

              {userType === 'patient' && (
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
              )}

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

              {userType === 'patient' && (
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
              )}

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
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden mt-16">
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

        let dashboardData;
        
        if (userType === 'provider') {
          // Use provider dashboard endpoint
          console.log('📊 Loading provider dashboard data for:', currentUser.id);
          const response = await fetch(`http://localhost:4002/api/v1/provider-dashboard/${currentUser.id}`);
          if (!response.ok) {
            throw new Error('Failed to fetch provider dashboard data');
          }
          dashboardData = await response.json();
          
          // Transform provider dashboard data
          const upcomingAppointments = dashboardData.upcoming_appointments.map(apt => ({
            id: apt.appointment_id,
            provider: `Patient: ${apt.patient_name}`,
            date: apt.appointment_date,
            time: apt.appointment_time
          }));
          
          const stats = {
            nextAppointment: upcomingAppointments.length > 0 ? upcomingAppointments[0].date : 'No upcoming appointments',
            activePrescriptions: dashboardData.quick_stats.pending_prescriptions,
            pendingLabResults: 0, // Not applicable for providers
            todayAppointments: dashboardData.quick_stats.today_appointments,
            pendingPrescriptions: dashboardData.quick_stats.pending_prescriptions,
            labRequests: dashboardData.quick_stats.lab_requests
          };
          
          const recentActivity = dashboardData.recent_activity.map(activity => ({
            type: activity.icon === 'pill' ? 'prescription' : 'lab',
            text: activity.action,
            time: activity.timestamp,
            icon: activity.icon === 'pill' ? <Pill className="w-4 h-4 text-green-600" /> : <FlaskConical className="w-4 h-4 text-blue-600" />
          }));
          
          setDashboardData({
            quickStats: stats,
            appointments: upcomingAppointments,
            recentActivity: recentActivity
          });
        } else {
          // Use existing patient dashboard logic
        const [patients, doctors, appointments] = await Promise.all([
          abenaSDK.getAllPatients().catch(() => []),
          abenaSDK.getAllDoctors().catch(() => []),
            abenaSDK.getAppointments(currentUser.id, userType).catch(() => [])
        ]);

        console.log('📊 Fetched data:', { patients: patients.length, doctors: doctors.length, appointments: appointments.length });

        // Process appointments
        const upcomingAppointments = appointments
          .filter(apt => new Date(apt.date) > new Date())
          .slice(0, 3)
          .map(apt => ({
            id: apt.id,
               provider: `Dr. ${apt.provider_name || 'Smith'}`,
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
         }

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
            {userType === 'provider' ? (
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
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    documentName: '',
    documentType: 'lab_results',
    isConfidential: false,
    tags: ''
  });

  // Load documents from real API
  useEffect(() => {
    const loadDocuments = async () => {
      try {
        setLoading(true);
        
        // Get auth token from localStorage
        const token = localStorage.getItem('abena_token');
        if (!token) {
          console.error('No authentication token found');
          return;
        }

        // Get logged-in user data
        const userData = localStorage.getItem('abena_user_data');
        console.log('🔍 User data from localStorage:', userData);
        const currentUser = userData ? JSON.parse(userData) : null;
        console.log('🔍 Parsed currentUser:', currentUser);
        
        if (!currentUser) {
          console.error('No user data found in localStorage');
          return;
        }
        
        // Check for different possible user ID field names
        const userId = currentUser.userId || currentUser.id || currentUser.patient_id || currentUser.user_id;
        console.log('🔍 Found userId:', userId);
        
        if (!userId) {
          console.error('No user ID found in user data. Available fields:', Object.keys(currentUser));
          return;
        }

        // Fetch documents from real backend API for the logged-in user only
        const response = await fetch(`http://localhost:4002/api/v1/documents?patient_id=${userId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch documents');
        }

        const documentsData = await response.json();
        console.log('✅ Real documents data loaded:', documentsData.documents?.length || 0, 'documents');
        setDocuments(documentsData.documents || []);
        
      } catch (error) {
        console.error('❌ Failed to fetch documents from real API:', error);
        // Fallback to mock data for development
        const mockDocuments = [
          { id: 1, document_name: 'Lab Results - Blood Test.pdf', document_type: 'lab_results', upload_date: '2024-01-15', is_confidential: false },
          { id: 2, document_name: 'Prescription - Antibiotics.pdf', document_type: 'prescription', upload_date: '2024-01-14', is_confidential: false },
          { id: 3, document_name: 'Medical Records Summary.pdf', document_type: 'medical_records', upload_date: '2024-01-13', is_confidential: true }
        ];
        setDocuments(mockDocuments);
      } finally {
        setLoading(false);
      }
    };

    loadDocuments();
  }, []);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setUploadForm({ ...uploadForm, documentName: file.name });
      setShowUploadModal(true);
    }
  };

  const handleUploadSubmit = async () => {
    try {
      setLoading(true);
      
      // Get auth token from localStorage
      const token = localStorage.getItem('abena_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Get logged-in user data
      const userData = localStorage.getItem('abena_user_data');
      const currentUser = userData ? JSON.parse(userData) : null;
      const userId = currentUser?.userId || currentUser?.id || currentUser?.patient_id || currentUser?.user_id;
      
      if (!userId) {
        throw new Error('No user ID found');
      }

      // Create FormData for file upload
      const formData = new FormData();
      formData.append('patient_id', userId);
      formData.append('document_name', uploadForm.documentName);
      formData.append('document_type', uploadForm.documentType);
      formData.append('file', selectedFile);
      formData.append('is_confidential', uploadForm.isConfidential);
      formData.append('tags', uploadForm.tags);

      // Upload document
      const response = await fetch('http://localhost:4002/api/v1/documents/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to upload document');
      }

      const result = await response.json();
      console.log('Document uploaded successfully:', result);
      
      // Refresh documents list
      const refreshResponse = await fetch(`http://localhost:4002/api/v1/documents?patient_id=${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (refreshResponse.ok) {
        const data = await refreshResponse.json();
        setDocuments(data.documents || []);
      }
      
      setShowUploadModal(false);
      setSelectedFile(null);
      setUploadForm({
        documentName: '',
        documentType: 'lab_results',
        isConfidential: false,
        tags: ''
      });
      
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('Failed to upload document. Please try again.');
    } finally {
      setLoading(false);
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
          </div>
        </CardContent>
      </Card>

      {/* Documents List */}
      <Card>
        <CardHeader>
          <CardTitle>Documents</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading documents...</p>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <File className="w-5 h-5 text-blue-500" />
                    <div>
                      <p className="font-medium">{doc.document_name}</p>
                      <p className="text-sm text-gray-500">{new Date(doc.upload_date).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {!doc.is_confidential && (
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">Shared</span>
                    )}
                    {doc.is_confidential && (
                      <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded">Confidential</span>
                    )}
                    <button className="p-2 text-gray-400 hover:text-gray-600" title="View document">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-gray-600" title="Download document">
                      <Download className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-gray-600" title="Share document">
                      <Share2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Modal */}
      {showUploadModal && selectedFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Upload Document</h3>
              <button 
                onClick={() => setShowUploadModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Document Name</label>
                <input
                  type="text"
                  value={uploadForm.documentName}
                  onChange={(e) => setUploadForm({...uploadForm, documentName: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter document name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Document Type</label>
                <select
                  value={uploadForm.documentType}
                  onChange={(e) => setUploadForm({...uploadForm, documentType: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="lab_results">Lab Results</option>
                  <option value="prescription">Prescription</option>
                  <option value="medical_records">Medical Records</option>
                  <option value="visit_summary">Visit Summary</option>
                  <option value="treatment_plan">Treatment Plan</option>
                  <option value="consent_form">Consent Form</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tags (Optional)</label>
                <input
                  type="text"
                  value={uploadForm.tags}
                  onChange={(e) => setUploadForm({...uploadForm, tags: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter tags separated by commas"
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="confidential"
                  checked={uploadForm.isConfidential}
                  onChange={(e) => setUploadForm({...uploadForm, isConfidential: e.target.checked})}
                  className="mr-2"
                />
                <label htmlFor="confidential" className="text-sm text-gray-700">
                  Mark as confidential
                </label>
              </div>
            </div>
            <div className="flex justify-end mt-6 space-x-3">
              <button 
                onClick={() => setShowUploadModal(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button 
                onClick={handleUploadSubmit}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Uploading...' : 'Upload Document'}
              </button>
            </div>
          </div>
        </div>
      )}
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
            if (userType === 'provider') {
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
                        {userType === 'provider' ? 'Patient: John Doe' : 'Dr. Smith'}
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
  const [showPrescriptionDetails, setShowPrescriptionDetails] = useState(false);
  const [selectedPrescription, setSelectedPrescription] = useState(null);
  const [loading, setLoading] = useState(false);
  const [newPrescription, setNewPrescription] = useState({
    patient_id: '',
    medication_name: '',
    dosage: '',
    frequency: '',
    start_date: '',
    end_date: '',
    pharmacy_id: '',
    instructions: ''
  });
  const [patients, setPatients] = useState([]);
  const [pharmacies, setPharmacies] = useState([]);
  const [showEditPrescription, setShowEditPrescription] = useState(false);
  const [editingPrescription, setEditingPrescription] = useState(null);
  const [showSendPrescriptionModal, setShowSendPrescriptionModal] = useState(false);
  const [sendingPrescription, setSendingPrescription] = useState(false);

  // Load prescriptions, patients, and pharmacies using real backend APIs
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // Get auth token from localStorage
        const token = localStorage.getItem('abena_token');
        if (!token) {
          console.error('No authentication token found');
          return;
        }

        // Get logged-in user data
        const userData = localStorage.getItem('abena_user_data');
        console.log('🔍 User data from localStorage:', userData);
        const currentUser = userData ? JSON.parse(userData) : null;
        console.log('🔍 Parsed currentUser:', currentUser);
        
        if (!currentUser) {
          console.error('No user data found in localStorage');
          return;
        }
        
        // Check for different possible user ID field names
        const userId = currentUser.userId || currentUser.id || currentUser.patient_id || currentUser.user_id;
        console.log('🔍 Found userId:', userId);
        
        if (!userId) {
          console.error('No user ID found in user data. Available fields:', Object.keys(currentUser));
          return;
        }

        // Load data based on user type
        if (userType === 'provider') {
          // For providers: load their prescriptions, all patients, and pharmacies
          const [prescriptionsRes, patientsRes, pharmaciesRes] = await Promise.all([
            fetch(`http://localhost:4002/api/v1/prescriptions/provider/${currentUser.userId}`, {
              headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
            }),
            fetch(`http://localhost:4002/api/v1/providers/${currentUser.userId}/patients`, {
              headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
            }),
            fetch(`http://localhost:4002/api/v1/pharmacies`, {
              headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
            })
          ]);

          const [prescriptionData, patientsData, pharmaciesData] = await Promise.all([
            prescriptionsRes.json(),
            patientsRes.json(),
            pharmaciesRes.json()
          ]);

          console.log('✅ Provider data loaded:', {
            prescriptions: prescriptionData.prescriptions?.length || 0,
            patients: patientsData.patients?.length || 0,
            pharmacies: pharmaciesData.pharmacies?.length || 0
          });
          console.log('🔍 Raw patients data:', patientsData);

          setPrescriptions(prescriptionData.prescriptions || []);
          setPatients(patientsData.patients || []);
          setPharmacies(pharmaciesData.pharmacies || []);
        } else {
          // For patients: load only their prescriptions
          const response = await fetch(`http://localhost:4002/api/v1/prescriptions?patient_id=${userId}`, {
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
          });

          if (!response.ok) {
            throw new Error('Failed to fetch prescriptions');
          }

          const prescriptionData = await response.json();
          console.log('✅ Patient prescription data loaded:', prescriptionData.prescriptions?.length || 0, 'prescriptions');
          setPrescriptions(prescriptionData.prescriptions || []);
        }
        
      } catch (error) {
        console.error('❌ Failed to fetch data from real API:', error);
        // Fallback to mock data for development
        const mockPrescriptions = [
          { id: 1, patient_name: 'John Doe', medication_name: 'Amoxicillin 500mg', dosage: '1 capsule 3x daily', frequency: '3 times daily', status: 'active', prescribed_date: '2024-01-15' },
          { id: 2, patient_name: 'Alice Johnson', medication_name: 'Ibuprofen 400mg', dosage: '1 tablet as needed', frequency: 'as needed', status: 'active', prescribed_date: '2024-01-14' }
        ];
        setPrescriptions(mockPrescriptions);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [userType]);

  const handleSubmitPrescription = async () => {
    try {
      setLoading(true);
      
      // Get auth token from localStorage
      const token = localStorage.getItem('abena_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Get logged-in user data
      const userData = localStorage.getItem('abena_user_data');
      const currentUser = userData ? JSON.parse(userData) : null;
      
      if (!currentUser) {
        throw new Error('No user data found in localStorage');
      }

      // Validate required fields
      if (!newPrescription.patient_id || !newPrescription.medication_name || !newPrescription.dosage) {
        alert('Please fill in all required fields (Patient, Medication Name, and Dosage)');
        return;
      }

      // Prepare prescription data
      const prescriptionData = {
        ...newPrescription,
        prescribing_physician: currentUser.userId,
        status: 'active',
        start_date: newPrescription.start_date || new Date().toISOString().split('T')[0]
      };

      const response = await fetch('http://localhost:4002/api/v1/prescriptions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(prescriptionData)
      });

      if (!response.ok) {
        throw new Error('Failed to create prescription');
      }

      const result = await response.json();
      console.log('✅ Prescription created successfully:', result);

      // Add the new prescription to the list
      const patient = patients.find(p => p.patient_id === newPrescription.patient_id);
      const pharmacy = pharmacies.find(ph => ph.id === newPrescription.pharmacy_id);
      
      const prescription = {
        id: result.medication_id,
        medication_name: newPrescription.medication_name,
        dosage: newPrescription.dosage,
        frequency: newPrescription.frequency,
        patient_name: patient ? `${patient.first_name} ${patient.last_name}` : 'Unknown Patient',
        patient_id: newPrescription.patient_id,
        pharmacy_name: pharmacy ? pharmacy.pharmacy_name : 'Not specified',
        status: 'active',
        prescribed_date: prescriptionData.start_date
      };
      setPrescriptions([prescription, ...prescriptions]);

      // Reset form
      setNewPrescription({
        patient_id: '',
        medication_name: '',
        dosage: '',
        frequency: '',
        start_date: '',
        end_date: '',
        pharmacy_id: '',
        instructions: ''
      });
      setShowNewPrescription(false);

    } catch (error) {
      console.error('❌ Error creating prescription:', error);
      alert('Failed to create prescription. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Eye function - View prescription details
  const handleViewPrescription = (prescription) => {
    setSelectedPrescription(prescription);
    setShowPrescriptionDetails(true);
    console.log('Viewing prescription details:', prescription);
  };

  // Edit prescription function
  const handleEditPrescription = (prescription) => {
    setEditingPrescription(prescription);
    setNewPrescription({
      patient_id: prescription.patient_id,
      medication_name: prescription.medication_name,
      dosage: prescription.dosage,
      frequency: prescription.frequency,
      start_date: prescription.prescribed_date,
      end_date: prescription.end_date,
      pharmacy_id: prescription.pharmacy_id,
      instructions: prescription.instructions || ''
    });
    setShowEditPrescription(true);
  };

  // Update prescription function
  const handleUpdatePrescription = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('abena_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`http://localhost:4002/api/v1/prescriptions/${editingPrescription.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newPrescription)
      });

      if (!response.ok) {
        throw new Error('Failed to update prescription');
      }

      const result = await response.json();
      console.log('✅ Prescription updated successfully:', result);

      // Update the prescription in the list
      const updatedPrescriptions = prescriptions.map(p => 
        p.id === editingPrescription.id 
          ? { ...p, ...newPrescription }
          : p
      );
      setPrescriptions(updatedPrescriptions);

      setShowEditPrescription(false);
      setEditingPrescription(null);
      setNewPrescription({
        patient_id: '',
        medication_name: '',
        dosage: '',
        frequency: '',
        start_date: '',
        end_date: '',
        pharmacy_id: '',
        instructions: ''
      });

    } catch (error) {
      console.error('❌ Error updating prescription:', error);
      alert('Failed to update prescription. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Delete prescription function
  const handleDeletePrescription = async (prescriptionId) => {
    if (!window.confirm('Are you sure you want to delete this prescription?')) {
      return;
    }

    try {
      setLoading(true);
      
      const token = localStorage.getItem('abena_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`http://localhost:4002/api/v1/prescriptions/${prescriptionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete prescription');
      }

      const result = await response.json();
      console.log('✅ Prescription deleted successfully:', result);

      // Remove the prescription from the list
      setPrescriptions(prescriptions.filter(p => p.id !== prescriptionId));

    } catch (error) {
      console.error('❌ Error deleting prescription:', error);
      alert('Failed to delete prescription. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // State for pharmacy contact modal
  const [showPharmacyModal, setShowPharmacyModal] = useState(false);
  const [selectedPrescriptionForSending, setSelectedPrescriptionForSending] = useState(null);
  const [pharmacyContact, setPharmacyContact] = useState('');
  const [contactType, setContactType] = useState('email'); // 'email' or 'phone'

  // Send function - Send prescription to pharmacy
  const handleSendPrescription = async (prescription) => {
    // Show pharmacy contact modal first
    setSelectedPrescriptionForSending(prescription);
    setShowPharmacyModal(true);
  };

  const handleConfirmSendPrescription = async () => {
    if (!pharmacyContact.trim()) {
      alert('Please enter pharmacy contact information');
      return;
    }

    try {
      setLoading(true);
      
      // Get auth token from localStorage
      const token = localStorage.getItem('abena_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Send prescription to pharmacy using real backend API
      const response = await fetch(`http://localhost:4002/api/v1/prescriptions/${selectedPrescriptionForSending.id}/send`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          pharmacyName: `Pharmacy (${contactType})`,
          pharmacyContact: pharmacyContact,
          contactType: contactType,
          sendDate: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send prescription');
      }

      const updatedPrescription = await response.json();
      console.log('✅ Prescription sent successfully:', updatedPrescription);

      // Update local state
      const updatedPrescriptions = prescriptions.map(p => 
        p.id === selectedPrescriptionForSending.id ? { ...p, status: 'sent' } : p
      );
      setPrescriptions(updatedPrescriptions);

      // Show success message
      alert(`Prescription for ${selectedPrescriptionForSending.medication_name} sent to pharmacy successfully!`);

      // Close modal and reset state
      setShowPharmacyModal(false);
      setSelectedPrescriptionForSending(null);
      setPharmacyContact('');
      setContactType('email');

    } catch (error) {
      console.error('❌ Error sending prescription:', error);
      alert('Failed to send prescription. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with New Prescription Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Prescriptions</h2>
        {userType === 'provider' && (
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
                        <p className="font-medium">{prescription.medication_name}</p>
                        <p className="text-sm text-gray-500">Patient: {prescription.patient_name || 'Unknown Patient'}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 text-xs rounded ${
                        prescription.status === 'active' ? 'bg-green-100 text-green-800' : 
                        prescription.status === 'discontinued' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {prescription.status === 'active' ? 'Active' : 
                         prescription.status === 'discontinued' ? 'Discontinued' : prescription.status}
                      </span>
                      <button 
                        onClick={() => handleViewPrescription(prescription)}
                        className="p-2 text-gray-400 hover:text-gray-600"
                        title="View prescription details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      {userType === 'provider' && (
                        <>
                          <button 
                            onClick={() => handleEditPrescription(prescription)}
                            className="p-2 text-blue-400 hover:text-blue-600"
                            title="Edit prescription"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button 
                            onClick={() => handleDeletePrescription(prescription.id)}
                            className="p-2 text-red-400 hover:text-red-600"
                            title="Delete prescription"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
                      <button 
                        onClick={() => handleSendPrescription(prescription)}
                        className={`p-2 ${
                          prescription.status === 'sent' 
                            ? 'text-green-500 hover:text-green-600' 
                            : 'text-gray-400 hover:text-gray-600'
                        }`}
                        title={prescription.status === 'sent' ? 'Resend prescription to pharmacy' : 'Send prescription to pharmacy'}
                      >
                        <Send className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Dosage:</span> {prescription.dosage}
                    </div>
                    <div>
                      <span className="font-medium">Duration:</span> {prescription.frequency}
                    </div>
                  </div>
                  <div className="mt-3 text-xs text-gray-500">
                    Date: {prescription.prescribed_date}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Prescription Details Modal */}
      {showPrescriptionDetails && selectedPrescription && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Prescription Details</h3>
              <button 
                onClick={() => setShowPrescriptionDetails(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Patient</label>
                  <p className="p-3 bg-gray-50 rounded-md">{selectedPrescription.patient_name || 'Unknown Patient'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Medication</label>
                  <p className="p-3 bg-gray-50 rounded-md">{selectedPrescription.medication_name}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Dosage</label>
                  <p className="p-3 bg-gray-50 rounded-md">{selectedPrescription.dosage}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Duration</label>
                  <p className="p-3 bg-gray-50 rounded-md">{selectedPrescription.frequency}</p>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Instructions</label>
                <p className="p-3 bg-gray-50 rounded-md">{selectedPrescription.instructions || 'No special instructions'}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Pharmacy</label>
                  <p className="p-3 bg-gray-50 rounded-md">{selectedPrescription.pharmacy || 'Not specified'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                  <span className={`px-3 py-1 text-sm rounded-full ${
                    selectedPrescription.status === 'sent' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {selectedPrescription.status === 'sent' ? 'Sent' : 'Pending'}
                  </span>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                <p className="p-3 bg-gray-50 rounded-md">{selectedPrescription.prescribed_date || 'Not specified'}</p>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button 
                onClick={() => setShowPrescriptionDetails(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Close
              </button>
              {selectedPrescription.status !== 'sent' && (
                <button 
                  onClick={() => {
                    handleSendPrescription(selectedPrescription);
                    setShowPrescriptionDetails(false);
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
                >
                  <Send className="w-4 h-4" />
                  <span>Send to Pharmacy</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Pharmacy Contact Modal */}
      {showPharmacyModal && selectedPrescriptionForSending && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                {selectedPrescriptionForSending?.status === 'sent' ? 'Resend' : 'Send'} Prescription to Pharmacy
              </h3>
              <button 
                onClick={() => {
                  setShowPharmacyModal(false);
                  setSelectedPrescriptionForSending(null);
                  setPharmacyContact('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prescription
                </label>
                <p className="p-3 bg-gray-50 rounded-md text-sm">
                  {selectedPrescriptionForSending.medication_name} - {selectedPrescriptionForSending.dosage}
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contact Type
                </label>
                <div className="flex space-x-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="email"
                      checked={contactType === 'email'}
                      onChange={(e) => setContactType(e.target.value)}
                      className="mr-2"
                    />
                    Email
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="phone"
                      checked={contactType === 'phone'}
                      onChange={(e) => setContactType(e.target.value)}
                      className="mr-2"
                    />
                    Phone
                  </label>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Pharmacy {contactType === 'email' ? 'Email' : 'Phone Number'}
                </label>
                <input
                  type={contactType === 'email' ? 'email' : 'tel'}
                  value={pharmacyContact}
                  onChange={(e) => setPharmacyContact(e.target.value)}
                  placeholder={contactType === 'email' ? 'pharmacy@example.com' : '+1 (555) 123-4567'}
                  className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button 
                onClick={() => {
                  setShowPharmacyModal(false);
                  setSelectedPrescriptionForSending(null);
                  setPharmacyContact('');
                }}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button 
                onClick={handleConfirmSendPrescription}
                disabled={loading || !pharmacyContact.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Sending...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>{selectedPrescriptionForSending?.status === 'sent' ? 'Resend' : 'Send'} Prescription</span>
                  </>
                )}
              </button>
            </div>
          </div>
                </div>
      )}

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
                <label className="block text-sm font-medium text-gray-700 mb-2">Patient *</label>
                <select 
                  value={newPrescription.patient_id}
                  onChange={(e) => setNewPrescription({...newPrescription, patient_id: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  disabled={loading}
                  required
                >
                  <option value="">Select a patient</option>
                  {patients.map(patient => (
                    <option key={patient.patient_id} value={patient.patient_id}>
                      {patient.first_name} {patient.last_name} - {patient.email}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Medication Name *</label>
                <input 
                  type="text" 
                  value={newPrescription.medication_name}
                  onChange={(e) => setNewPrescription({...newPrescription, medication_name: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  placeholder="e.g., Amoxicillin 500mg"
                  disabled={loading}
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Dosage *</label>
                  <input 
                    type="text" 
                    value={newPrescription.dosage}
                    onChange={(e) => setNewPrescription({...newPrescription, dosage: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    placeholder="e.g., 1 tablet"
                    disabled={loading}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Frequency</label>
                  <input 
                    type="text" 
                    value={newPrescription.frequency}
                    onChange={(e) => setNewPrescription({...newPrescription, frequency: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    placeholder="e.g., 3 times daily"
                    disabled={loading}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
                  <input 
                    type="date" 
                    value={newPrescription.start_date}
                    onChange={(e) => setNewPrescription({...newPrescription, start_date: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    disabled={loading}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
                  <input 
                    type="date" 
                    value={newPrescription.end_date}
                    onChange={(e) => setNewPrescription({...newPrescription, end_date: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    disabled={loading}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Pharmacy</label>
                <select 
                  value={newPrescription.pharmacy_id}
                  onChange={(e) => setNewPrescription({...newPrescription, pharmacy_id: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  disabled={loading}
                >
                  <option value="">Select a pharmacy</option>
                  {pharmacies.map(pharmacy => (
                    <option key={pharmacy.id} value={pharmacy.id}>
                      {pharmacy.pharmacy_name} - {pharmacy.address}
                    </option>
                  ))}
                </select>
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
                <Plus className="w-4 h-4" />
                <span>{loading ? 'Creating...' : 'Create Prescription'}</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Prescription Modal */}
      {showEditPrescription && editingPrescription && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Edit Prescription</h3>
              <button 
                onClick={() => setShowEditPrescription(false)}
                className="text-gray-400 hover:text-gray-600"
                disabled={loading}
              >
                ×
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Patient *</label>
                <select 
                  value={newPrescription.patient_id}
                  onChange={(e) => setNewPrescription({...newPrescription, patient_id: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  disabled={loading}
                  required
                >
                  <option value="">Select a patient</option>
                  {patients.map(patient => (
                    <option key={patient.patient_id} value={patient.patient_id}>
                      {patient.first_name} {patient.last_name} - {patient.email}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Medication Name *</label>
                <input 
                  type="text" 
                  value={newPrescription.medication_name}
                  onChange={(e) => setNewPrescription({...newPrescription, medication_name: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  placeholder="e.g., Amoxicillin 500mg"
                  disabled={loading}
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Dosage *</label>
                  <input 
                    type="text" 
                    value={newPrescription.dosage}
                    onChange={(e) => setNewPrescription({...newPrescription, dosage: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    placeholder="e.g., 1 tablet"
                    disabled={loading}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Frequency</label>
                  <input 
                    type="text" 
                    value={newPrescription.frequency}
                    onChange={(e) => setNewPrescription({...newPrescription, frequency: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    placeholder="e.g., 3 times daily"
                    disabled={loading}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
                  <input 
                    type="date" 
                    value={newPrescription.start_date}
                    onChange={(e) => setNewPrescription({...newPrescription, start_date: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    disabled={loading}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
                  <input 
                    type="date" 
                    value={newPrescription.end_date}
                    onChange={(e) => setNewPrescription({...newPrescription, end_date: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    disabled={loading}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Pharmacy</label>
                <select 
                  value={newPrescription.pharmacy_id}
                  onChange={(e) => setNewPrescription({...newPrescription, pharmacy_id: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  disabled={loading}
                >
                  <option value="">Select a pharmacy</option>
                  {pharmacies.map(pharmacy => (
                    <option key={pharmacy.id} value={pharmacy.id}>
                      {pharmacy.pharmacy_name} - {pharmacy.address}
                    </option>
                  ))}
                </select>
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
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button 
                onClick={() => setShowEditPrescription(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                onClick={handleUpdatePrescription}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
                disabled={loading}
              >
                <Save className="w-4 h-4" />
                <span>{loading ? 'Updating...' : 'Update Prescription'}</span>
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
        {userType === 'provider' && (
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
  const [labResults, setLabResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showLabResultDetails, setShowLabResultDetails] = useState(false);
  const [selectedLabResult, setSelectedLabResult] = useState(null);

  // Load lab results from real API
  useEffect(() => {
    const loadLabResults = async () => {
      try {
        setLoading(true);
        
        // Get auth token from localStorage
        const token = localStorage.getItem('abena_token');
        if (!token) {
          console.error('No authentication token found');
          return;
        }

        // Get logged-in user data
        const userData = localStorage.getItem('abena_user_data');
        console.log('🔍 User data from localStorage:', userData);
        const currentUser = userData ? JSON.parse(userData) : null;
        console.log('🔍 Parsed currentUser:', currentUser);
        
        if (!currentUser) {
          console.error('No user data found in localStorage');
          return;
        }
        
        // Check for different possible user ID field names
        const userId = currentUser.userId || currentUser.id || currentUser.patient_id || currentUser.user_id;
        console.log('🔍 Found userId:', userId);
        
        if (!userId) {
          console.error('No user ID found in user data. Available fields:', Object.keys(currentUser));
          return;
        }

        // Fetch lab results from real backend API for the logged-in user only
        const response = await fetch(`http://localhost:4002/api/v1/lab-results?patient_id=${userId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch lab results');
        }

        const labResultsData = await response.json();
        console.log('✅ Real lab results data loaded:', labResultsData.lab_results?.length || 0, 'lab results');
        setLabResults(labResultsData.lab_results || []);
        
      } catch (error) {
        console.error('❌ Failed to fetch lab results from real API:', error);
        // Fallback to mock data for development
        const mockLabResults = [
          { id: 1, test_name: 'Complete Blood Count (CBC)', test_date: '2024-01-15', abnormal_flag: 'N', lab_name: 'LabCorp' },
          { id: 2, test_name: 'Lipid Panel', test_date: '2024-01-10', abnormal_flag: 'N', lab_name: 'Quest Diagnostics' },
          { id: 3, test_name: 'Thyroid Function Test', test_date: '2024-01-05', abnormal_flag: 'N', lab_name: 'LabCorp' }
        ];
        setLabResults(mockLabResults);
      } finally {
        setLoading(false);
      }
    };

    loadLabResults();
  }, []);

  // Handle view lab result details
  const handleViewLabResult = async (labResult) => {
    try {
      setLoading(true);
      
      // Get auth token from localStorage
      const token = localStorage.getItem('abena_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Fetch detailed lab result from backend API
      const response = await fetch(`http://localhost:4002/api/v1/lab-results/${labResult.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch lab result details');
      }

      const labResultData = await response.json();
      console.log('✅ Lab result details loaded:', labResultData.lab_result);
      setSelectedLabResult(labResultData.lab_result);
      setShowLabResultDetails(true);
      
    } catch (error) {
      console.error('❌ Error fetching lab result details:', error);
      alert('Failed to load lab result details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Lab Results</h2>
      
      <Card>
        <CardHeader>
          <CardTitle>My Lab Results</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading lab results...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {labResults.map((result) => (
                <div key={result.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <FlaskConical className="w-5 h-5 text-blue-500" />
                      <div>
                        <p className="font-medium">{result.test_name}</p>
                        <p className="text-sm text-gray-500">Lab: {result.lab_name}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 text-xs rounded ${
                        result.abnormal_flag === 'N' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {result.abnormal_flag === 'N' ? 'Completed' : 'Pending'}
                      </span>
                      <button 
                        onClick={() => handleViewLabResult(result)}
                        className="p-2 text-gray-400 hover:text-gray-600"
                        title="View lab result details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    Date: {new Date(result.test_date).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Lab Result Details Modal */}
      {showLabResultDetails && selectedLabResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Lab Result Details</h3>
              <button 
                onClick={() => setShowLabResultDetails(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Patient</label>
                  <p className="p-3 bg-gray-50 rounded-md">{selectedLabResult.patient_name || 'Unknown Patient'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Test Name</label>
                  <p className="p-3 bg-gray-50 rounded-md">{selectedLabResult.test_name}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Test Code</label>
                  <p className="p-3 bg-gray-50 rounded-md">{selectedLabResult.test_code || 'Not specified'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Lab Name</label>
                  <p className="p-3 bg-gray-50 rounded-md">{selectedLabResult.lab_name}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Result Value</label>
                  <p className="p-3 bg-gray-50 rounded-md">
                    {selectedLabResult.result_value ? `${selectedLabResult.result_value} ${selectedLabResult.unit || ''}` : selectedLabResult.result_text || 'Not specified'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Reference Range</label>
                  <p className="p-3 bg-gray-50 rounded-md">{selectedLabResult.reference_range || 'Not specified'}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                  <span className={`px-3 py-1 text-sm rounded-full ${
                    selectedLabResult.abnormal_flag === 'N' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {selectedLabResult.abnormal_flag === 'N' ? 'Normal' : 'Abnormal'}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Test Date</label>
                  <p className="p-3 bg-gray-50 rounded-md">{new Date(selectedLabResult.test_date).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
            <div className="flex justify-end mt-6">
              <button 
                onClick={() => setShowLabResultDetails(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
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
                <p className="font-medium">{userType === 'provider' ? 'Dr. Smith' : 'John Doe'}</p>
                <p className="text-sm text-gray-500">{userType === 'provider' ? 'Cardiologist' : 'Patient'}</p>
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
  const [isAuthChecked, setIsAuthChecked] = useState(false); // Add this to track auth check completion

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
    setIsAuthChecked(true); // Mark auth check as complete
  }, []);

  const handleLogin = (type, credentials, sdkInstance, authResult) => {
    console.log('Login successful:', authResult);
    setUserType(type);
    setCurrentUser(authResult.user);
    setAbenaSDK(sdkInstance);
    setIsLoggedIn(true);
    
    // Store authentication data in localStorage for persistence
    localStorage.setItem('abena_user_type', type);
    localStorage.setItem('abena_user_data', JSON.stringify(authResult));
    localStorage.setItem('abena_token', authResult.token);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserType('patient');
    setCurrentUser(null);
    setAbenaSDK(null);
    
    // Clear authentication data from localStorage
    localStorage.removeItem('abena_user_type');
    localStorage.removeItem('abena_user_data');
    localStorage.removeItem('abena_token');
    localStorage.removeItem('abena_user');
  };

  // Don't render anything until auth check is complete
  if (!isAuthChecked) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

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
          path="/my-patients" 
          element={
            isLoggedIn ? (
              <DashboardLayout userType={userType} onLogout={handleLogout} currentUser={currentUser} abenaSDK={abenaSDK}>
                <MyPatientsPanel userType={userType} />
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
  const [selectedDate, setSelectedDate] = useState(null); // Changed to null to show all dates initially
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'calendar'
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  
  // Provider action modals
  const [showPostponeModal, setShowPostponeModal] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [showRefundModal, setShowRefundModal] = useState(false);
  const [selectedActionAppointment, setSelectedActionAppointment] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      setLoading(true);
      
      // Get current user info from localStorage
      const currentUser = JSON.parse(localStorage.getItem('abena_user') || '{}');
      const userType = localStorage.getItem('abena_user_type') || 'patient';
      
      // Fetch appointments based on user type
      let url;
      if (userType === 'provider') {
        const providerId = currentUser.id;
        url = providerId 
          ? `http://localhost:4002/api/v1/appointments?provider_id=${providerId}`
          : 'http://localhost:4002/api/v1/appointments';
      } else {
        const patientId = currentUser.patient_id || currentUser.id;
        url = patientId 
        ? `http://localhost:4002/api/v1/appointments?patient_id=${patientId}`
        : 'http://localhost:4002/api/v1/appointments';
      }
        
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('abena_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        console.log('📅 Fetched real appointments for user:', data);
        setAppointments(data);
      } else {
        console.error('❌ Failed to fetch appointments:', response.status);
        // Fallback to mock data if API fails
        const mockAppointments = [
          {
            appointment_id: 1,
            patient_id: 'P001',
            patient_name: 'John Smith',
            appointment_date: '2024-01-15',
            appointment_time: '10:00:00',
            appointment_type: 'Follow-up',
            status: 'confirmed',
            notes: 'Regular checkup'
          },
          {
            appointment_id: 2,
            patient_id: 'P001',
            patient_name: 'John Smith',
            appointment_date: '2024-01-15',
            appointment_time: '14:30:00',
            appointment_type: 'Consultation',
            status: 'pending',
            notes: 'New patient consultation'
          },
          {
            appointment_id: 3,
            patient_id: 'P001',
            patient_name: 'John Smith',
            appointment_date: '2024-01-16',
            appointment_time: '09:00:00',
            appointment_type: 'Emergency',
            status: 'confirmed',
            notes: 'Urgent care needed'
          }
        ];
        setAppointments(mockAppointments);
      }
    } catch (error) {
      console.error('❌ Error fetching appointments:', error);
      // Fallback to mock data
      const mockAppointments = [
        {
          appointment_id: 1,
          patient_id: 'P001',
          patient_name: 'John Smith',
          appointment_date: '2024-01-15',
          appointment_time: '10:00:00',
          appointment_type: 'Follow-up',
          status: 'confirmed',
          notes: 'Regular checkup'
        },
        {
          appointment_id: 2,
          patient_id: 'P001',
          patient_name: 'John Smith',
          appointment_date: '2024-01-15',
          appointment_time: '14:30:00',
          appointment_type: 'Consultation',
          status: 'pending',
          notes: 'New patient consultation'
        },
        {
          appointment_id: 3,
          patient_id: 'P001',
          patient_name: 'John Smith',
          appointment_date: '2024-01-16',
          appointment_time: '09:00:00',
          appointment_type: 'Emergency',
          status: 'confirmed',
          notes: 'Urgent care needed'
        }
      ];
      setAppointments(mockAppointments);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (appointmentId, newStatus) => {
    try {
      // Update appointment status in the database
      const response = await fetch(`http://localhost:4002/api/v1/appointments/${appointmentId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('abena_token')}`
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        console.log('✅ Appointment status updated successfully');
        // Update local state
        setAppointments(prev => 
          prev.map(apt => 
            apt.appointment_id === appointmentId ? { ...apt, status: newStatus } : apt
          )
        );
      } else {
        console.error('❌ Failed to update appointment status:', response.status);
        // Still update local state for better UX
        setAppointments(prev => 
          prev.map(apt => 
            apt.appointment_id === appointmentId ? { ...apt, status: newStatus } : apt
          )
        );
      }
    } catch (error) {
      console.error('❌ Error updating appointment status:', error);
      // Update local state for better UX even if API fails
      setAppointments(prev => 
        prev.map(apt => 
          apt.appointment_id === appointmentId ? { ...apt, status: newStatus } : apt
        )
      );
    }
  };

  const handleAppointmentCreated = (newAppointment) => {
    // Add the new appointment to the list
    setAppointments(prev => [newAppointment, ...prev]);
    console.log('✅ New appointment added to list:', newAppointment);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const fetchAppointmentDetails = async (appointmentId) => {
    try {
      setDetailsLoading(true);
      const response = await fetch(`http://localhost:4002/api/v1/appointments/${appointmentId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('abena_token')}`
        }
      });

      if (response.ok) {
        const appointment = await response.json();
        setSelectedAppointment(appointment);
        setShowDetailsModal(true);
      } else {
        console.error('Failed to fetch appointment details');
        alert('Failed to fetch appointment details');
      }
    } catch (error) {
      console.error('Error fetching appointment details:', error);
      alert('Error fetching appointment details');
    } finally {
      setDetailsLoading(false);
    }
  };

  // Provider-specific appointment actions
  const handlePostponeAppointment = async (appointmentId) => {
    const appointment = appointments.find(apt => apt.appointment_id === appointmentId);
    setSelectedActionAppointment(appointment);
    setShowPostponeModal(true);
  };

  const handleCancelAppointment = async (appointmentId) => {
    const appointment = appointments.find(apt => apt.appointment_id === appointmentId);
    setSelectedActionAppointment(appointment);
    setShowCancelModal(true);
  };

  const handleRefundPayment = async (appointmentId) => {
    const appointment = appointments.find(apt => apt.appointment_id === appointmentId);
    setSelectedActionAppointment(appointment);
    setShowRefundModal(true);
  };



  // Filter appointments based on selected filters (no date restriction initially)
  const filteredAppointments = appointments.filter(appointment => {
    const matchesStatus = filterStatus === 'all' || appointment.status === filterStatus;
    const matchesType = filterType === 'all' || appointment.appointment_type === filterType;
    const matchesDate = !selectedDate || selectedDate.toISOString().split('T')[0] === appointment.appointment_date;
    return matchesStatus && matchesType && matchesDate;
  });

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
          <button 
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            + New Appointment
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border">
        <div className="flex space-x-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date (Optional)</label>
            <input
              type="date"
              value={selectedDate ? selectedDate.toISOString().split('T')[0] : ''}
              onChange={(e) => setSelectedDate(e.target.value ? new Date(e.target.value) : null)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="All dates"
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
              <option value="confirmed">Confirmed</option>
              <option value="pending">Pending</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select 
              value={filterType} 
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Types</option>
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
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            My Appointments ({filteredAppointments.length})
          </h2>
          {filteredAppointments.length > 0 ? (
            <div className="space-y-4">
              {filteredAppointments.map((appointment) => (
                <div key={appointment.appointment_id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <Calendar className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">
                        {userType === 'provider' 
                          ? (appointment.patient_name || (appointment.patient_id ? `Patient ${appointment.patient_id}` : 'Unknown Patient'))
                          : (appointment.provider_name || (appointment.provider_id ? `Provider ${appointment.provider_id}` : 'Unknown Provider'))
                        }
                      </h3>
                      <p className="text-sm text-gray-600">ID: {userType === 'provider' ? appointment.patient_id : appointment.provider_id}</p>
                      <p className="text-sm text-gray-600">{appointment.appointment_date} at {appointment.appointment_time}</p>
                      <p className="text-sm text-gray-600">{appointment.notes}</p>
                      
                      {/* Provider-specific payment information */}
                      {userType === 'provider' && (
                        <div className="mt-2">
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Fee Paid:</span> ${appointment.payment_amount || '200.00'}
                          </p>
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Payment Status:</span> 
                            <span className={`ml-1 px-2 py-1 text-xs rounded-full ${
                              appointment.payment_status === 'paid' ? 'bg-green-100 text-green-800' : 
                              appointment.payment_status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                              'bg-red-100 text-red-800'
                            }`}>
                              {appointment.payment_status || 'pending'}
                            </span>
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(appointment.status)}`}>
                      {appointment.status}
                    </span>
                    
                    {/* Provider-specific action buttons */}
                    {userType === 'provider' ? (
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handlePostponeAppointment(appointment.appointment_id)}
                          className="px-3 py-1 text-sm bg-yellow-600 text-white rounded hover:bg-yellow-700"
                          disabled={appointment.status === 'cancelled'}
                        >
                          Postpone
                        </button>
                        <button
                          onClick={() => handleCancelAppointment(appointment.appointment_id)}
                          className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                          disabled={appointment.status === 'cancelled'}
                        >
                          Cancel
                        </button>
                        {appointment.status === 'cancelled' && appointment.payment_status === 'paid' && (
                          <button
                            onClick={() => handleRefundPayment(appointment.appointment_id)}
                            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                          >
                            Refund
                          </button>
                        )}
                      </div>
                    ) : (
                    <select
                      value={appointment.status}
                      onChange={(e) => handleStatusChange(appointment.appointment_id, e.target.value)}
                      className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="confirmed">Confirmed</option>
                      <option value="pending">Pending</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                    )}
                    
                    <button 
                      onClick={() => fetchAppointmentDetails(appointment.appointment_id)}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No appointments found</p>
            </div>
          )}
        </div>
      </div>

      {/* Appointment Creation Modal */}
      <AppointmentCreationModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onAppointmentCreated={handleAppointmentCreated}
          onRefreshAppointments={fetchAppointments}
        />

      {/* Appointment Details Modal */}
      {showDetailsModal && selectedAppointment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Appointment Details</h2>
                  <p className="text-sm text-gray-600">ID: {selectedAppointment.appointment_id}</p>
                </div>
              </div>
              <button
                onClick={() => setShowDetailsModal(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Patient & Provider Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <User className="w-4 h-4 mr-2" />
                    Patient Information
                  </h3>
                  <p className="text-sm text-gray-600">Name: {selectedAppointment.patient_name}</p>
                  <p className="text-sm text-gray-600">ID: {selectedAppointment.patient_id}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <Stethoscope className="w-4 h-4 mr-2" />
                    Provider Information
                  </h3>
                  <p className="text-sm text-gray-600">Name: {selectedAppointment.provider_name}</p>
                  <p className="text-sm text-gray-600">ID: {selectedAppointment.provider_id}</p>
                </div>
              </div>

              {/* Appointment Details */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                  <Clock className="w-4 h-4 mr-2" />
                  Appointment Details
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-700">Date</p>
                    <p className="text-sm text-gray-600">{selectedAppointment.appointment_date}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">Time</p>
                    <p className="text-sm text-gray-600">{selectedAppointment.appointment_time}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">Type</p>
                    <p className="text-sm text-gray-600 capitalize">{selectedAppointment.appointment_type}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">Status</p>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(selectedAppointment.status)}`}>
                      {selectedAppointment.status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Notes */}
              {selectedAppointment.notes && (
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <FileText className="w-4 h-4 mr-2" />
                    Notes
                  </h3>
                  <p className="text-sm text-gray-700">{selectedAppointment.notes}</p>
                </div>
              )}

              {/* Timestamps */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <Calendar className="w-4 h-4 mr-2" />
                  Timestamps
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="font-medium text-gray-700">Created</p>
                    <p className="text-gray-600">{new Date(selectedAppointment.created_at).toLocaleString()}</p>
                  </div>
                  {selectedAppointment.updated_at && (
                    <div>
                      <p className="font-medium text-gray-700">Last Updated</p>
                      <p className="text-gray-600">{new Date(selectedAppointment.updated_at).toLocaleString()}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
              <button
                onClick={() => setShowDetailsModal(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => {
                  // TODO: Add edit functionality
                  alert('Edit functionality coming soon!');
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Edit Appointment
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Provider Action Modals */}
      <PostponeAppointmentModal
        isOpen={showPostponeModal}
        onClose={() => setShowPostponeModal(false)}
        appointment={selectedActionAppointment}
        onSuccess={() => {
          fetchAppointments();
          setShowPostponeModal(false);
        }}
      />

      <CancelAppointmentModal
        isOpen={showCancelModal}
        onClose={() => setShowCancelModal(false)}
        appointment={selectedActionAppointment}
        onSuccess={() => {
          fetchAppointments();
          setShowCancelModal(false);
        }}
      />

      <RefundAppointmentModal
        isOpen={showRefundModal}
        onClose={() => setShowRefundModal(false)}
        appointment={selectedActionAppointment}
        onSuccess={() => {
          fetchAppointments();
          setShowRefundModal(false);
        }}
      />
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

// Provider Earnings Dashboard Component
const ProviderEarningsDashboard = ({ providerId }) => {
  const [earnings, setEarnings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalEarnings, setTotalEarnings] = useState(0);

  useEffect(() => {
    if (providerId) {
      fetchProviderEarnings();
    }
  }, [providerId]);

  const fetchProviderEarnings = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:4002/api/v1/payments/provider/${providerId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('abena_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setEarnings(data);
        const total = data.reduce((sum, payment) => sum + (payment.amount / 100), 0);
        setTotalEarnings(total);
      } else {
        console.error('Failed to fetch provider earnings');
      }
    } catch (error) {
      console.error('Error fetching provider earnings:', error);
    } finally {
      setLoading(false);
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
      {/* Earnings Summary */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Total Earnings</h2>
            <p className="text-green-100">All time earnings from appointments</p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold">${totalEarnings.toFixed(2)}</p>
            <p className="text-green-100">{earnings.length} appointments</p>
          </div>
        </div>
      </div>

      {/* Recent Payments */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Payments</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {earnings.slice(0, 10).map((payment, index) => (
            <div key={index} className="p-6 flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">
                  {payment.metadata?.patient_name || 'Unknown Patient'}
                </p>
                <p className="text-sm text-gray-600">
                  {new Date(payment.created).toLocaleDateString()}
                </p>
                <p className="text-xs text-gray-500">
                  ID: {payment.payment_intent_id}
                </p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-green-600">
                  ${(payment.amount / 100).toFixed(2)}
                </p>
                <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                  payment.status === 'succeeded' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {payment.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Simple Appointment Creation Modal Component
  const AppointmentCreationModal = ({ isOpen, onClose, onAppointmentCreated, onRefreshAppointments }) => {
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [appointmentType, setAppointmentType] = useState('consultation');
  const [notes, setNotes] = useState('');
  const [providers, setProviders] = useState([]);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [paymentIntent, setPaymentIntent] = useState(null);
  const [showPaymentForm, setShowPaymentForm] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchProviders();
    }
  }, [isOpen]);

  useEffect(() => {
    if (selectedProvider && selectedDate) {
      fetchAvailableSlots();
    }
  }, [selectedProvider, selectedDate]);

  const fetchProviders = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:4002/api/v1/providers', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('abena_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProviders(data);
      } else {
        console.error('Failed to fetch providers');
      }
    } catch (error) {
      console.error('Error fetching providers:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableSlots = async () => {
    try {
      setLoading(true);
      // Use the new single-date endpoint format
      const response = await fetch(
        `http://localhost:4002/api/v1/providers/${selectedProvider}/availability?appointment_date=${selectedDate}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('abena_token')}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAvailableSlots(data.available_slots);
      } else {
        console.error('Failed to fetch available slots');
      }
    } catch (error) {
      console.error('Error fetching available slots:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAppointment = async () => {
    try {
      setLoading(true);
      setError('');

      const currentUser = JSON.parse(localStorage.getItem('abena_user') || '{}');
      const patientId = currentUser.patient_id || currentUser.id;

      const appointmentData = {
        patient_id: patientId,
        provider_id: selectedProvider,
        appointment_date: selectedDate,
        appointment_time: selectedTime + ':00', // Add seconds
        appointment_type: appointmentType,
        notes: notes,
        status: 'pending'
      };

      // Step 1: Create payment intent
      console.log('💳 Creating payment intent...');
      const paymentResponse = await fetch('http://localhost:4002/api/v1/appointments/payment-intent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('abena_token')}`
        },
        body: JSON.stringify(appointmentData)
      });

      if (!paymentResponse.ok) {
        const errorData = await paymentResponse.json();
        throw new Error(errorData.detail || 'Failed to create payment intent');
      }

      const paymentData = await paymentResponse.json();
      console.log('✅ Payment intent created:', paymentData);

      // Store payment intent and show payment form
      setPaymentIntent(paymentData.payment_intent);
      setShowPaymentForm(true);
    } catch (error) {
      console.error('❌ Error creating payment intent:', error);
      setError(error.message || 'Failed to create payment intent. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentSuccess = async () => {
    try {
      setLoading(true);
      
      const currentUser = JSON.parse(localStorage.getItem('abena_user') || '{}');
      const patientId = currentUser.patient_id || currentUser.id;

      const appointmentData = {
        patient_id: patientId,
        provider_id: selectedProvider,
        appointment_date: selectedDate,
        appointment_time: selectedTime + ':00',
        appointment_type: appointmentType,
        notes: notes,
        status: 'pending'
      };

      // Confirm payment and create appointment
      console.log('✅ Payment successful, creating appointment...');
      const confirmResponse = await fetch('http://localhost:4002/api/v1/appointments/confirm-payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('abena_token')}`
        },
        body: JSON.stringify({
          payment_intent_id: paymentIntent.payment_intent_id,
          appointment_data: appointmentData
        })
      });

      if (confirmResponse.ok) {
        const result = await confirmResponse.json();
        console.log('✅ Appointment created successfully after payment:', result);
        
        // Refresh the appointments list
        if (onRefreshAppointments) {
          await onRefreshAppointments();
        }
        
        onAppointmentCreated(result);
        onClose();
        resetForm();
        alert('🎉 Appointment booked successfully! Payment of $200 has been processed.');
      } else {
        const errorData = await confirmResponse.json();
        throw new Error(errorData.detail || 'Failed to confirm appointment');
      }
    } catch (error) {
      console.error('❌ Error confirming appointment:', error);
      setError(error.message || 'Failed to confirm appointment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentError = (errorMessage) => {
    setError(errorMessage);
    setShowPaymentForm(false);
    setPaymentIntent(null);
  };

  const resetForm = () => {
    setSelectedProvider('');
    setSelectedDate('');
    setSelectedTime('');
    setAppointmentType('consultation');
    setNotes('');
    setAvailableSlots([]);
    setError('');
    setPaymentIntent(null);
    setShowPaymentForm(false);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const getTimeSlotsForDate = (date) => {
    // The backend already returns slots for the specific date, so just filter by availability
    return availableSlots.filter(slot => slot.available === true);
  };



  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">Create New Appointment</h2>
          <button onClick={handleClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {/* Payment Information */}
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <div className="w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-xs font-bold">$</span>
            </div>
            <h3 className="font-semibold text-blue-900">Payment Information</h3>
          </div>
          <p className="text-sm text-blue-700">
            Appointment fee: <span className="font-bold">$200.00</span>
          </p>
          <p className="text-xs text-blue-600 mt-1">
            Payment will be processed securely via Stripe
          </p>
        </div>

        {/* Form */}
        {!showPaymentForm ? (
        <div className="space-y-4">
          {/* Provider Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
            {loading ? (
              <div className="animate-pulse bg-gray-200 h-10 rounded"></div>
            ) : (
              <select
                value={selectedProvider}
                onChange={(e) => setSelectedProvider(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a provider</option>
                {providers.map((provider) => (
                  <option key={provider.provider_id} value={provider.provider_id}>
                    {provider.first_name} {provider.last_name} - {provider.specialization}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Date Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Time Selection */}
          {selectedDate && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Time</label>
              {loading ? (
                <div className="animate-pulse bg-gray-200 h-10 rounded"></div>
              ) : (
                <select
                  value={selectedTime}
                  onChange={(e) => setSelectedTime(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select a time</option>
                  {getTimeSlotsForDate(selectedDate).map((slot) => (
                    <option key={slot.time} value={slot.time}>
                      {slot.time} - {slot.end_time}
                    </option>
                  ))}
                </select>
              )}
            </div>
          )}

          {/* Appointment Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={appointmentType}
              onChange={(e) => setAppointmentType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="consultation">Consultation</option>
              <option value="follow-up">Follow-up</option>
              <option value="emergency">Emergency</option>
              <option value="routine">Routine Checkup</option>
            </select>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes (Optional)</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Add any additional notes..."
            />
          </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-5 h-5 bg-green-600 rounded-full flex items-center justify-center">
                </div>
                  <span className="text-white text-xs font-bold">✓</span>
                <h3 className="font-semibold text-green-900">Appointment Details Confirmed</h3>
              </div>
              <p className="text-sm text-green-700">
                Please complete your payment to book the appointment.
              </p>
        </div>
            
            <Elements stripe={stripePromise}>
              <PaymentForm
                onPaymentSuccess={handlePaymentSuccess}
                onPaymentError={handlePaymentError}
                amount={20000}
                clientSecret={paymentIntent.client_secret}
              />
            </Elements>
          </div>
        )}

        {/* Actions */}
        {!showPaymentForm && (
        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={handleClose}
            className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleCreateAppointment}
            disabled={loading || !selectedProvider || !selectedDate || !selectedTime}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700"
          >
              {loading ? 'Creating Payment Intent...' : 'Continue to Payment'}
          </button>
        </div>
        )}
      </div>
    </div>
  );
};

// Provider Action Modals
const PostponeAppointmentModal = ({ isOpen, onClose, appointment, onSuccess }) => {
  const [newDate, setNewDate] = useState('');
  const [newTime, setNewTime] = useState('');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newDate || !newTime || !reason) {
      alert('All fields are required for postponement');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:4002/api/v1/appointments/${appointment.appointment_id}/postpone`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('abena_token')}`
        },
        body: JSON.stringify({
          new_date: newDate,
          new_time: newTime,
          reason: reason
        })
      });

      if (response.ok) {
        console.log('✅ Appointment postponed successfully');
        onSuccess();
        onClose();
      } else {
        console.error('❌ Failed to postpone appointment:', response.status);
        alert('Failed to postpone appointment');
      }
    } catch (error) {
      console.error('❌ Error postponing appointment:', error);
      alert('Error postponing appointment');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !appointment) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Postpone Appointment</h2>
              <p className="text-sm text-gray-600">Patient: {appointment.patient_name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">New Date</label>
            <input
              type="date"
              value={newDate}
              onChange={(e) => setNewDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">New Time</label>
            <input
              type="time"
              value={newTime}
              onChange={(e) => setNewTime(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Reason for Postponement</label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter reason for postponement..."
              required
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-yellow-600 text-white rounded-lg disabled:opacity-50 hover:bg-yellow-700"
            >
              {loading ? 'Postponing...' : 'Postpone Appointment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const CancelAppointmentModal = ({ isOpen, onClose, appointment, onSuccess }) => {
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!reason) {
      alert('Reason is required for cancellation');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:4002/api/v1/appointments/${appointment.appointment_id}/cancel`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('abena_token')}`
        },
        body: JSON.stringify({
          reason: reason
        })
      });

      if (response.ok) {
        console.log('✅ Appointment cancelled successfully');
        onSuccess();
        onClose();
      } else {
        console.error('❌ Failed to cancel appointment:', response.status);
        alert('Failed to cancel appointment');
      }
    } catch (error) {
      console.error('❌ Error cancelling appointment:', error);
      alert('Error cancelling appointment');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !appointment) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <X className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Cancel Appointment</h2>
              <p className="text-sm text-gray-600">Patient: {appointment.patient_name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Reason for Cancellation</label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter reason for cancellation..."
              required
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-red-600 text-white rounded-lg disabled:opacity-50 hover:bg-red-700"
            >
              {loading ? 'Cancelling...' : 'Cancel Appointment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const RefundAppointmentModal = ({ isOpen, onClose, appointment, onSuccess }) => {
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:4002/api/v1/appointments/${appointment.appointment_id}/refund`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('abena_token')}`
        }
      });

      if (response.ok) {
        console.log('✅ Refund processed successfully');
        onSuccess();
        onClose();
      } else {
        console.error('❌ Failed to process refund:', response.status);
        alert('Failed to process refund');
      }
    } catch (error) {
      console.error('❌ Error processing refund:', error);
      alert('Error processing refund');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !appointment) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <DollarSign className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Process Refund</h2>
              <p className="text-sm text-gray-600">Patient: {appointment.patient_name}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
              <h3 className="font-semibold text-yellow-900">Confirm Refund</h3>
            </div>
            <p className="text-sm text-yellow-700">
              Are you sure you want to process a refund for this appointment? This action cannot be undone.
            </p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2">Appointment Details</h3>
            <p className="text-sm text-gray-600">Date: {appointment.appointment_date}</p>
            <p className="text-sm text-gray-600">Time: {appointment.appointment_time}</p>
            <p className="text-sm text-gray-600">Amount: ${appointment.payment_amount || '200.00'}</p>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg disabled:opacity-50 hover:bg-green-700"
            >
              {loading ? 'Processing...' : 'Process Refund'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// My Patients Panel Component for Providers
const MyPatientsPanel = ({ userType }) => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddPatient, setShowAddPatient] = useState(false);
  const [newPatient, setNewPatient] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    date_of_birth: '',
    gender: '',
    address: ''
  });

  // Load provider's patients
  useEffect(() => {
    const loadPatients = async () => {
      try {
        setLoading(true);
        
        // Get auth token from localStorage
        const token = localStorage.getItem('abena_token');
        if (!token) {
          console.error('No authentication token found');
          return;
        }

        // Get logged-in user data
        const userData = localStorage.getItem('abena_user_data');
        const currentUser = userData ? JSON.parse(userData) : null;
        
        if (!currentUser) {
          console.error('No user data found in localStorage');
          return;
        }

        // Fetch provider's patients from backend
        const response = await fetch(`http://localhost:4002/api/v1/providers/${currentUser.userId}/patients`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          console.log('✅ Provider patients loaded:', data.patients?.length || 0, 'patients');
          setPatients(data.patients || []);
        } else {
          console.error('Failed to fetch provider patients');
          // Fallback to all patients for now
          const allPatientsResponse = await fetch(`http://localhost:4002/api/v1/patients`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          if (allPatientsResponse.ok) {
            const allPatientsData = await allPatientsResponse.json();
            setPatients(allPatientsData.patients || []);
          }
        }
        
      } catch (error) {
        console.error('❌ Failed to fetch patients:', error);
        // Fallback to mock data
        const mockPatients = [
          { patient_id: '1', first_name: 'John', last_name: 'Doe', email: 'john.doe@email.com', phone: '(555) 123-4567', date_of_birth: '1985-03-15', gender: 'Male', last_visit: '2024-01-15' },
          { patient_id: '2', first_name: 'Alice', last_name: 'Johnson', email: 'alice.johnson@email.com', phone: '(555) 234-5678', date_of_birth: '1990-07-22', gender: 'Female', last_visit: '2024-01-10' },
          { patient_id: '3', first_name: 'Bob', last_name: 'Smith', email: 'bob.smith@email.com', phone: '(555) 345-6789', date_of_birth: '1978-11-08', gender: 'Male', last_visit: '2024-01-08' }
        ];
        setPatients(mockPatients);
      } finally {
        setLoading(false);
      }
    };

    if (userType === 'provider') {
      loadPatients();
    }
  }, [userType]);

  const handleAddPatient = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('abena_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const userData = localStorage.getItem('abena_user_data');
      const currentUser = userData ? JSON.parse(userData) : null;
      
      if (!currentUser) {
        throw new Error('No user data found in localStorage');
      }

      // Add provider_id to the patient data
      const patientData = {
        ...newPatient,
        provider_id: currentUser.userId,
        is_active: true
      };

      const response = await fetch('http://localhost:4002/api/v1/patients', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(patientData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Patient added successfully:', result);
        
        // Add the new patient to the list
        const newPatientWithId = {
          patient_id: result.patient_id,
          ...newPatient,
          last_visit: new Date().toISOString().split('T')[0]
        };
        setPatients([newPatientWithId, ...patients]);

        // Show login credentials to provider
        if (result.login_credentials) {
          const credentials = result.login_credentials;
          const message = `Patient created successfully!\n\nLogin Credentials:\nUsername: ${credentials.username}\nPassword: ${credentials.password}\n\nPlease share these credentials with the patient.`;
          alert(message);
        }

        // Reset form
        setNewPatient({
          first_name: '',
          last_name: '',
          email: '',
          phone: '',
          date_of_birth: '',
          gender: '',
          address: ''
        });
        setShowAddPatient(false);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add patient');
      }
    } catch (error) {
      console.error('❌ Error adding patient:', error);
      alert(`Failed to add patient: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleViewPatient = (patient) => {
    console.log('Viewing patient details:', patient);
    // TODO: Implement patient details view
  };

  const handleEditPatient = (patient) => {
    console.log('Editing patient:', patient);
    // TODO: Implement patient edit functionality
  };

  const handleDeletePatient = async (patientId) => {
    if (!window.confirm('Are you sure you want to remove this patient from your list?')) {
      return;
    }

    try {
      setLoading(true);
      
      const token = localStorage.getItem('abena_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`http://localhost:4002/api/v1/patients/${patientId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        console.log('✅ Patient removed successfully');
        setPatients(patients.filter(p => p.patient_id !== patientId));
      } else {
        throw new Error('Failed to remove patient');
      }
    } catch (error) {
      console.error('❌ Error removing patient:', error);
      alert('Failed to remove patient. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Add Patient Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">My Patients</h2>
        {userType === 'provider' && (
          <button 
            onClick={() => setShowAddPatient(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md flex items-center space-x-2 hover:bg-blue-700"
            disabled={loading}
          >
            <Plus className="w-4 h-4" />
            <span>{loading ? 'Processing...' : 'Add Patient'}</span>
          </button>
        )}
      </div>

      {/* Patients List */}
      <Card>
        <CardHeader>
          <CardTitle>Patients ({patients.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading patients...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {patients.map((patient) => (
                <div key={patient.patient_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium">{patient.first_name} {patient.last_name}</p>
                        <p className="text-sm text-gray-500">{patient.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button 
                        onClick={() => handleViewPatient(patient)}
                        className="p-2 text-gray-400 hover:text-gray-600"
                        title="View patient details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleEditPatient(patient)}
                        className="p-2 text-blue-400 hover:text-blue-600"
                        title="Edit patient"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleDeletePatient(patient.patient_id)}
                        className="p-2 text-red-400 hover:text-red-600"
                        title="Remove patient"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Phone:</span> {patient.phone}
                    </div>
                    <div>
                      <span className="font-medium">Gender:</span> {patient.gender}
                    </div>
                    <div>
                      <span className="font-medium">DOB:</span> {patient.date_of_birth}
                    </div>
                    <div>
                      <span className="font-medium">Last Visit:</span> {patient.last_visit || 'Never'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Patient Modal */}
      {showAddPatient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Add New Patient</h3>
              <button 
                onClick={() => setShowAddPatient(false)}
                className="text-gray-400 hover:text-gray-600"
                disabled={loading}
              >
                ×
              </button>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">First Name *</label>
                  <input 
                    type="text" 
                    value={newPatient.first_name}
                    onChange={(e) => setNewPatient({...newPatient, first_name: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    placeholder="First name"
                    disabled={loading}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Last Name *</label>
                  <input 
                    type="text" 
                    value={newPatient.last_name}
                    onChange={(e) => setNewPatient({...newPatient, last_name: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    placeholder="Last name"
                    disabled={loading}
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                <input 
                  type="email" 
                  value={newPatient.email}
                  onChange={(e) => setNewPatient({...newPatient, email: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-md"
                  placeholder="email@example.com"
                  disabled={loading}
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                  <input 
                    type="tel" 
                    value={newPatient.phone}
                    onChange={(e) => setNewPatient({...newPatient, phone: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    placeholder="(555) 123-4567"
                    disabled={loading}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Date of Birth</label>
                  <input 
                    type="date" 
                    value={newPatient.date_of_birth}
                    onChange={(e) => setNewPatient({...newPatient, date_of_birth: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    disabled={loading}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
                  <select 
                    value={newPatient.gender}
                    onChange={(e) => setNewPatient({...newPatient, gender: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    disabled={loading}
                  >
                    <option value="">Select gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Address</label>
                  <input 
                    type="text" 
                    value={newPatient.address}
                    onChange={(e) => setNewPatient({...newPatient, address: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-md"
                    placeholder="Address"
                    disabled={loading}
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button 
                onClick={() => setShowAddPatient(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                onClick={handleAddPatient}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
                disabled={loading}
              >
                <Plus className="w-4 h-4" />
                <span>{loading ? 'Adding...' : 'Add Patient'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App; 