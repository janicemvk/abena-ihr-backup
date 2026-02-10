import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadialBarChart, RadialBar, AreaChart, Area } from 'recharts';
import { Activity, Heart, Brain, Droplets, Shield, Clock, Sun, Moon, Zap, Target, TrendingUp, Bell, Calendar, Book, Settings, User } from 'lucide-react';

// Patient Interface - eCBome Monitoring Dashboard
// Simplified, patient-friendly view of their eCBome health data
// ABENA SDK compliant with real-time monitoring

const PatientDashboard = () => {
  // State management
  const [patientData, setPatientData] = useState(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('today');
  const [notifications, setNotifications] = useState([]);
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock patient data - In production, comes from ABENA SDK
  useEffect(() => {
    const loadPatientData = async () => {
      setLoading(true);
      
      // Simulate API call: await abena.getPatientData(patientId, 'patient-dashboard')
      const mockData = {
        patientInfo: {
          firstName: 'Sarah',
          ecbomeScore: 82,
          improvementThisWeek: 5,
          streakDays: 12
        },
        ecbomeMetrics: {
          overall: 82,
          balance: 79,
          anandamide: 75,
          twoAG: 68,
          cb1Activity: 84,
          cb2Activity: 71
        },
        dailyTrends: [
          { time: '6AM', energy: 65, mood: 70, stress: 40 },
          { time: '9AM', energy: 78, mood: 82, stress: 35 },
          { time: '12PM', energy: 85, mood: 88, stress: 30 },
          { time: '3PM', energy: 80, mood: 85, stress: 45 },
          { time: '6PM', energy: 75, mood: 80, stress: 55 },
          { time: '9PM', energy: 60, mood: 75, stress: 35 }
        ],
        weeklyProgress: [
          { day: 'Mon', score: 78 },
          { day: 'Tue', score: 80 },
          { day: 'Wed', score: 79 },
          { day: 'Thu', score: 82 },
          { day: 'Fri', score: 85 },
          { day: 'Sat', score: 83 },
          { day: 'Sun', score: 82 }
        ],
        systemHealth: {
          metabolism: { score: 85, status: 'excellent' },
          immunity: { score: 78, status: 'good' },
          sleep: { score: 65, status: 'needs attention' },
          stress: { score: 58, status: 'needs attention' },
          nutrition: { score: 88, status: 'excellent' },
          activity: { score: 76, status: 'good' }
        },
        todaysGoals: [
          { id: 1, title: 'Take morning omega-3', completed: true, category: 'nutrition' },
          { id: 2, title: '15-minute meditation', completed: true, category: 'stress' },
          { id: 3, title: 'Evening walk', completed: false, category: 'activity' },
          { id: 4, title: 'Sleep by 10:30 PM', completed: false, category: 'sleep' }
        ],
        insights: [
          {
            type: 'positive',
            title: 'Great Progress!',
            message: 'Your eCBome balance has improved 5% this week through consistent sleep habits.'
          },
          {
            type: 'suggestion',
            title: 'Optimization Tip',
            message: 'Consider adding 10 minutes of morning sunlight exposure to boost your circadian rhythm.'
          },
          {
            type: 'alert',
            title: 'Attention Needed',
            message: 'Your stress levels have been elevated for 3 days. Try the recommended breathing exercises.'
          }
        ],
        upcomingReminders: [
          { time: '8:00 PM', action: 'Take evening supplements' },
          { time: '10:00 PM', action: 'Begin wind-down routine' },
          { time: '10:30 PM', action: 'Lights out for optimal sleep' }
        ]
      };

      setPatientData(mockData);
      setGoals(mockData.todaysGoals);
      setNotifications(mockData.insights);
      setLoading(false);
    };

    loadPatientData();

    // Real-time updates every 30 seconds
    const interval = setInterval(() => {
      // Simulate live updates
      setPatientData(prev => prev ? {
        ...prev,
        ecbomeMetrics: {
          ...prev.ecbomeMetrics,
          overall: Math.max(75, Math.min(90, prev.ecbomeMetrics.overall + (Math.random() - 0.5) * 2))
        }
      } : null);
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  // Helper functions
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getStatusIcon = (status) => {
    if (status === 'excellent') return <Target className="h-4 w-4 text-green-500" />;
    if (status === 'good') return <TrendingUp className="h-4 w-4 text-blue-500" />;
    if (status === 'needs attention') return <Bell className="h-4 w-4 text-yellow-500" />;
    return <Activity className="h-4 w-4 text-gray-500" />;
  };

  const toggleGoal = (goalId) => {
    setGoals(goals.map(goal => 
      goal.id === goalId ? { ...goal, completed: !goal.completed } : goal
    ));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your eCBome dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="h-10 w-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Welcome back, {patientData.patientInfo.firstName}!</h1>
                <p className="text-sm text-gray-600">Your eCBome wellness journey</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Live monitoring</span>
              </div>
              <button className="p-2 text-gray-400 hover:text-gray-600">
                <Settings className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Main Score Card */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full -mr-16 -mt-16 opacity-10"></div>
          <div className="relative">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-3xl font-bold text-gray-900">Your eCBome Score</h2>
                <p className="text-gray-600">Overall endocannabinoid system health</p>
              </div>
              <div className="text-right">
                <div className="text-5xl font-bold text-green-600">{patientData.ecbomeMetrics.overall}</div>
                <div className="flex items-center text-green-600 text-sm">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  +{patientData.patientInfo.improvementThisWeek} this week
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-xl">
                <div className="relative w-16 h-16 mx-auto mb-2">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadialBarChart cx="50%" cy="50%" innerRadius="70%" outerRadius="90%" data={[{ value: patientData.ecbomeMetrics.anandamide }]}>
                      <RadialBar dataKey="value" fill="#3B82F6" />
                    </RadialBarChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xs font-bold text-gray-700">{patientData.ecbomeMetrics.anandamide}</span>
                  </div>
                </div>
                <p className="text-sm font-medium text-gray-900">Anandamide</p>
                <p className="text-xs text-gray-600">Bliss factor</p>
              </div>

              <div className="text-center p-4 bg-green-50 rounded-xl">
                <div className="relative w-16 h-16 mx-auto mb-2">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadialBarChart cx="50%" cy="50%" innerRadius="70%" outerRadius="90%" data={[{ value: patientData.ecbomeMetrics.twoAG }]}>
                      <RadialBar dataKey="value" fill="#10B981" />
                    </RadialBarChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xs font-bold text-gray-700">{patientData.ecbomeMetrics.twoAG}</span>
                  </div>
                </div>
                <p className="text-sm font-medium text-gray-900">2-AG</p>
                <p className="text-xs text-gray-600">Balance</p>
              </div>

              <div className="text-center p-4 bg-purple-50 rounded-xl">
                <div className="relative w-16 h-16 mx-auto mb-2">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadialBarChart cx="50%" cy="50%" innerRadius="70%" outerRadius="90%" data={[{ value: patientData.ecbomeMetrics.cb1Activity }]}>
                      <RadialBar dataKey="value" fill="#8B5CF6" />
                    </RadialBarChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xs font-bold text-gray-700">{patientData.ecbomeMetrics.cb1Activity}</span>
                  </div>
                </div>
                <p className="text-sm font-medium text-gray-900">CB1</p>
                <p className="text-xs text-gray-600">Brain receptors</p>
              </div>

              <div className="text-center p-4 bg-indigo-50 rounded-xl">
                <div className="relative w-16 h-16 mx-auto mb-2">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadialBarChart cx="50%" cy="50%" innerRadius="70%" outerRadius="90%" data={[{ value: patientData.ecbomeMetrics.cb2Activity }]}>
                      <RadialBar dataKey="value" fill="#6366F1" />
                    </RadialBarChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xs font-bold text-gray-700">{patientData.ecbomeMetrics.cb2Activity}</span>
                  </div>
                </div>
                <p className="text-sm font-medium text-gray-900">CB2</p>
                <p className="text-xs text-gray-600">Body receptors</p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Daily Trends */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Today's Wellness Journey</h3>
                <div className="flex space-x-2">
                  {['today', 'week', 'month'].map((timeframe) => (
                    <button
                      key={timeframe}
                      onClick={() => setSelectedTimeframe(timeframe)}
                      className={`px-3 py-1 rounded-lg text-sm font-medium ${
                        selectedTimeframe === timeframe
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      {timeframe.charAt(0).toUpperCase() + timeframe.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={patientData.dailyTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Area type="monotone" dataKey="energy" stackId="1" stroke="#F59E0B" fill="#FEF3C7" name="Energy" />
                  <Area type="monotone" dataKey="mood" stackId="2" stroke="#10B981" fill="#D1FAE5" name="Mood" />
                  <Area type="monotone" dataKey="stress" stackId="3" stroke="#EF4444" fill="#FEE2E2" name="Stress" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* System Health Overview */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Body Systems</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {Object.entries(patientData.systemHealth).map(([system, data]) => (
                  <div key={system} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center space-x-3 mb-2">
                      {system === 'metabolism' && <Zap className="h-5 w-5 text-orange-500" />}
                      {system === 'immunity' && <Shield className="h-5 w-5 text-green-500" />}
                      {system === 'sleep' && <Moon className="h-5 w-5 text-purple-500" />}
                      {system === 'stress' && <Heart className="h-5 w-5 text-red-500" />}
                      {system === 'nutrition' && <Droplets className="h-5 w-5 text-blue-500" />}
                      {system === 'activity' && <Activity className="h-5 w-5 text-indigo-500" />}
                      <h4 className="font-medium text-gray-900 capitalize">{system}</h4>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                        <div 
                          className={`h-2 rounded-full ${
                            data.score >= 80 ? 'bg-green-500' :
                            data.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${data.score}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-700">{data.score}</span>
                    </div>
                    <div className="flex items-center mt-2">
                      {getStatusIcon(data.status)}
                      <span className={`text-xs ml-1 ${
                        data.status === 'excellent' ? 'text-green-600' :
                        data.status === 'good' ? 'text-blue-600' : 'text-yellow-600'
                      }`}>
                        {data.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Weekly Progress */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Progress</h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={patientData.weeklyProgress}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis domain={[70, 90]} />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#3B82F6" 
                    strokeWidth={3}
                    dot={{ fill: '#3B82F6', strokeWidth: 2, r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Today's Goals */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Target className="h-5 w-5 text-blue-500" />
                <h3 className="text-lg font-semibold text-gray-900">Today's Goals</h3>
              </div>
              <div className="space-y-3">
                {goals.map((goal) => (
                  <div key={goal.id} className="flex items-center space-x-3">
                    <button
                      onClick={() => toggleGoal(goal.id)}
                      className={`h-5 w-5 rounded-full border-2 flex items-center justify-center ${
                        goal.completed
                          ? 'bg-green-500 border-green-500 text-white'
                          : 'border-gray-300 hover:border-green-400'
                      }`}
                    >
                      {goal.completed && <span className="text-xs">✓</span>}
                    </button>
                    <span className={`flex-1 ${goal.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                      {goal.title}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      goal.category === 'nutrition' ? 'bg-blue-100 text-blue-700' :
                      goal.category === 'stress' ? 'bg-purple-100 text-purple-700' :
                      goal.category === 'activity' ? 'bg-green-100 text-green-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {goal.category}
                    </span>
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Progress</span>
                  <span className="font-medium text-gray-900">
                    {goals.filter(g => g.completed).length}/{goals.length} completed
                  </span>
                </div>
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(goals.filter(g => g.completed).length / goals.length) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Insights & Tips */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Brain className="h-5 w-5 text-purple-500" />
                <h3 className="text-lg font-semibold text-gray-900">Insights & Tips</h3>
              </div>
              <div className="space-y-3">
                {notifications.map((notification, index) => (
                  <div key={index} className={`p-3 rounded-lg border-l-4 ${
                    notification.type === 'positive' ? 'border-green-500 bg-green-50' :
                    notification.type === 'suggestion' ? 'border-blue-500 bg-blue-50' :
                    'border-yellow-500 bg-yellow-50'
                  }`}>
                    <h4 className="font-medium text-gray-900 text-sm mb-1">{notification.title}</h4>
                    <p className="text-xs text-gray-600">{notification.message}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Upcoming Reminders */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Clock className="h-5 w-5 text-indigo-500" />
                <h3 className="text-lg font-semibold text-gray-900">Upcoming</h3>
              </div>
              <div className="space-y-3">
                {patientData.upcomingReminders.map((reminder, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className="h-8 w-8 bg-indigo-100 rounded-full flex items-center justify-center">
                      <Bell className="h-4 w-4 text-indigo-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{reminder.action}</p>
                      <p className="text-xs text-gray-600">{reminder.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <button className="w-full px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all duration-200 flex items-center justify-center space-x-2">
                  <Book className="h-4 w-4" />
                  <span>View Wellness Plan</span>
                </button>
                <button className="w-full px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center space-x-2">
                  <Calendar className="h-4 w-4" />
                  <span>Schedule Check-in</span>
                </button>
                <button className="w-full px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center space-x-2">
                  <User className="h-4 w-4" />
                  <span>Contact Provider</span>
                </button>
              </div>
            </div>

            {/* Streak Tracker */}
            <div className="bg-gradient-to-r from-green-400 to-blue-500 rounded-xl shadow-sm p-6 text-white">
              <div className="text-center">
                <div className="text-3xl font-bold mb-2">{patientData.patientInfo.streakDays}</div>
                <p className="text-green-100">Day Streak</p>
                <p className="text-sm text-green-200 mt-2">Keep up the great work!</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientDashboard; 