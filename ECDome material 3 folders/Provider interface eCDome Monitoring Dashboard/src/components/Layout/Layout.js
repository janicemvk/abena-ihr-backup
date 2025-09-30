import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Activity, 
  Users, 
  FileText, 
  Settings, 
  Menu, 
  X,
  Bell,
  User,
  LogOut,
  Home,
  Brain,
  Shield,
  TrendingUp
} from 'lucide-react';
import { useDashboard } from '../../contexts/DashboardContext';
import { usePatient } from '../../contexts/PatientContext';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true); // Start with sidebar open for desktop
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const location = useLocation();
  const { systemStatus, alerts, lastUpdated } = useDashboard();
  const { loading } = usePatient();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home, current: location.pathname === '/dashboard' || location.pathname === '/' },
    { name: 'Patients', href: '/patients', icon: Users, current: location.pathname === '/patients' },
    { name: 'Reports', href: '/reports', icon: FileText, current: location.pathname === '/reports' },
    { name: 'Settings', href: '/settings', icon: Settings, current: location.pathname === '/settings' }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'offline': return 'bg-red-500';
      case 'maintenance': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const sidebarVariants = {
    open: { x: 0 },
    closed: { x: -320 }
  };

  return (
    <div className="h-screen bg-clinical-bg flex overflow-hidden">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
        />
      )}

      {/* Sidebar - Fixed */}
      <motion.div
        variants={sidebarVariants}
        animate={sidebarOpen ? 'open' : 'closed'}
        className="fixed inset-y-0 left-0 z-50 w-80 bg-white shadow-xl md:relative md:translate-x-0 md:z-auto md:flex-shrink-0"
      >
        <div className="flex flex-col h-full">
          {/* Logo and brand */}
          <div className="flex items-center justify-between p-6 border-b border-clinical-border">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">ABENA</h1>
                <p className="text-sm text-gray-600">Clinical Dashboard</p>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="md:hidden p-2 rounded-lg hover:bg-gray-100"
            >
              <X className="h-5 w-5 text-gray-600" />
            </button>
          </div>

          {/* System Status */}
          <div className="p-6 border-b border-clinical-border">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-900">System Status</h3>
              <div className={`h-2 w-2 rounded-full ${getStatusColor(systemStatus)}`} />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">eCDome Intelligence</span>
                <span className="text-green-600 font-medium">Online</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Data Processing</span>
                <span className="text-green-600 font-medium">Active</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Alert System</span>
                <span className="text-green-600 font-medium">Monitoring</span>
              </div>
            </div>
            {lastUpdated && (
              <p className="text-xs text-gray-500 mt-2">
                Last updated: {new Date(lastUpdated).toLocaleTimeString()}
              </p>
            )}
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-6 py-4">
            <div className="space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setSidebarOpen(false)}
                    className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      item.current
                        ? 'bg-ecdome-primary text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="h-5 w-5 mr-3" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </nav>

          {/* Quick Stats */}
          <div className="p-6 border-t border-clinical-border">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Stats</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center">
                <div className="text-2xl font-bold text-ecdome-primary">247</div>
                <div className="text-xs text-gray-600">Active Patients</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">98.5%</div>
                <div className="text-xs text-gray-600">System Uptime</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">{alerts.length}</div>
                <div className="text-xs text-gray-600">Active Alerts</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">1.2M</div>
                <div className="text-xs text-gray-600">Data Points</div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main content - Scrollable */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top header - Fixed */}
        <header className="bg-white shadow-sm border-b border-clinical-border flex-shrink-0 z-30">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              {/* Mobile menu button */}
              <button
                onClick={() => setSidebarOpen(true)}
                className="md:hidden p-2 rounded-lg hover:bg-gray-100"
              >
                <Menu className="h-5 w-5 text-gray-600" />
              </button>

              {/* Page title and breadcrumbs */}
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Shield className="h-5 w-5 text-ecdome-primary" />
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    eCDome Intelligence
                  </span>
                </div>
                {loading && (
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <div className="loading-spinner" />
                    <span>Loading...</span>
                  </div>
                )}
              </div>

              {/* Header actions */}
              <div className="flex items-center space-x-4">
                {/* Real-time indicator */}
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
                  <span className="hidden sm:inline">Live Monitoring</span>
                </div>

                {/* Notifications */}
                <div className="relative">
                  <button className="p-2 text-gray-400 hover:text-gray-600 relative">
                    <Bell className="h-5 w-5" />
                    {alerts.length > 0 && (
                      <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                        {alerts.length}
                      </span>
                    )}
                  </button>
                </div>

                {/* User menu */}
                <div className="relative">
                  <button
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                    className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100"
                  >
                    <div className="h-8 w-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <User className="h-4 w-4 text-white" />
                    </div>
                    <span className="hidden sm:inline text-sm font-medium text-gray-700">
                      Dr. Martinez
                    </span>
                  </button>

                  {/* User dropdown */}
                  {userMenuOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-clinical-border"
                    >
                      <div className="p-3 border-b border-clinical-border">
                        <p className="text-sm font-medium text-gray-900">Dr. Martinez</p>
                        <p className="text-xs text-gray-600">Clinical Provider</p>
                      </div>
                      <div className="p-2">
                        <button className="flex items-center w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md">
                          <Settings className="h-4 w-4 mr-2" />
                          Settings
                        </button>
                        <button className="flex items-center w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md">
                          <LogOut className="h-4 w-4 mr-2" />
                          Sign Out
                        </button>
                      </div>
                    </motion.div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main content area - Scrollable */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout; 