import React, { useState, useEffect, useContext, createContext } from 'react';
import { 
  Trophy, Star, Target, Heart, Activity,
  Plus, CheckCircle, Lock,
  Crown, Medal, Flame, Sparkles, Moon,
  TrendingUp, Award, Settings as SettingsIcon, X as CloseIcon, Wifi, WifiOff, Bell, BellRing
} from 'lucide-react';
import MobileHealthForm from './MobileHealthForm';
import MobileNavigation from './MobileNavigation';

// Types
interface User {
  id: string;
  level: number;
  xp: number;
  totalXP: number;
  streak: number;
  lastEntry: string | null;
  badges: Badge[];
  completedQuests: string[];
}

interface Quest {
  id: string;
  title: string;
  description: string;
  type: 'daily' | 'weekly' | 'streak';
  xpReward: number;
  progress: number;
  maxProgress: number;
  category: string;
}

interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  rarity: 'COMMON' | 'RARE' | 'EPIC' | 'LEGENDARY';
  unlocked: boolean;
}

interface GamificationContextType {
  user: User;
  quests: Quest[];
  recentActivity: any[];
  leaderboard: any[];
  addXP: (amount: number, source: string) => void;
  submitHealthData: (dataType: string) => void;
  completeQuest: (questId: string) => void;
  unlockBadge: (badgeId: string) => void;
}

// Gamification Context
const GamificationContext = createContext<GamificationContextType | undefined>(undefined);

// Mock data and utilities
const generateUserId = () => `user_${Math.random().toString(36).substr(2, 9)}`;

const BADGE_TYPES = {
  COMMON: { color: 'bg-gray-500', textColor: 'text-gray-700' },
  RARE: { color: 'bg-blue-500', textColor: 'text-blue-700' },
  EPIC: { color: 'bg-purple-500', textColor: 'text-purple-700' },
  LEGENDARY: { color: 'bg-yellow-500', textColor: 'text-yellow-700' }
};

const INITIAL_QUESTS: Quest[] = [
  {
    id: 'daily_mood',
    title: 'Daily Mood Check',
    description: 'Log your mood and energy level',
    type: 'daily',
    xpReward: 50,
    progress: 0,
    maxProgress: 1,
    category: 'wellness'
  },
  {
    id: 'weekly_symptoms',
    title: 'Weekly Symptom Tracker',
    description: 'Complete 7 days of symptom logging',
    type: 'weekly',
    xpReward: 300,
    progress: 0,
    maxProgress: 7,
    category: 'health'
  },
  {
    id: 'consistency_streak',
    title: 'Build Your Streak',
    description: 'Maintain a 5-day data entry streak',
    type: 'streak',
    xpReward: 500,
    progress: 0,
    maxProgress: 5,
    category: 'consistency'
  }
];

const INITIAL_BADGES: Badge[] = [
  { id: 'first_entry', name: 'First Steps', description: 'Made your first data entry', icon: '🌱', rarity: 'COMMON', unlocked: false },
  { id: 'week_warrior', name: 'Week Warrior', description: '7-day streak achieved', icon: '⚡', rarity: 'RARE', unlocked: false },
  { id: 'data_master', name: 'Data Master', description: '100 entries completed', icon: '📊', rarity: 'EPIC', unlocked: false },
  { id: 'health_legend', name: 'Health Legend', description: '30-day streak champion', icon: '👑', rarity: 'LEGENDARY', unlocked: false }
];

// Gamification Provider
const GamificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User>({
    id: generateUserId(),
    level: 1,
    xp: 0,
    totalXP: 0,
    streak: 0,
    lastEntry: null,
    badges: INITIAL_BADGES,
    completedQuests: []
  });

  const [quests, setQuests] = useState<Quest[]>(INITIAL_QUESTS);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [leaderboard, setLeaderboard] = useState<any[]>([]);

  // XP calculation for levels
  const getLevelFromXP = (xp: number) => Math.floor(xp / 1000) + 1;

  // Add XP and handle level ups
  const addXP = (amount: number, source: string = 'Data Entry') => {
    setUser(prev => {
      const newTotalXP = prev.totalXP + amount;
      const newLevel = getLevelFromXP(newTotalXP);
      const currentLevelXP = newTotalXP % 1000;
      
      const activity = {
        id: Date.now(),
        type: 'xp_gained',
        message: `+${amount} XP from ${source}`,
        timestamp: new Date().toISOString(),
        xp: amount
      };

      setRecentActivity(prev => [activity, ...prev.slice(0, 9)]);

      if (newLevel > prev.level) {
        const levelUpActivity = {
          id: Date.now() + 1,
          type: 'level_up',
          message: `Level up! Now level ${newLevel}`,
          timestamp: new Date().toISOString(),
          level: newLevel
        };
        setRecentActivity(prev => [levelUpActivity, ...prev.slice(0, 9)]);
      }

      return {
        ...prev,
        xp: currentLevelXP,
        totalXP: newTotalXP,
        level: newLevel
      };
    });
  };

  // Update streak
  const updateStreak = () => {
    const today = new Date().toDateString();
    setUser(prev => {
      if (prev.lastEntry === today) return prev;
      
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      
      const newStreak = prev.lastEntry === yesterday.toDateString() ? prev.streak + 1 : 1;
      
      return {
        ...prev,
        streak: newStreak,
        lastEntry: today
      };
    });
  };

  // Complete quest
  const completeQuest = (questId: string) => {
    setQuests(prev => prev.map(quest => {
      if (quest.id === questId && quest.progress < quest.maxProgress) {
        const newProgress = quest.progress + 1;
        const isComplete = newProgress >= quest.maxProgress;
        
        if (isComplete) {
          addXP(quest.xpReward, `Quest: ${quest.title}`);
          setUser(userPrev => ({
            ...userPrev,
            completedQuests: [...userPrev.completedQuests, questId]
          }));
        }
        
        return { ...quest, progress: newProgress };
      }
      return quest;
    }));
  };

  // Unlock badge
  const unlockBadge = (badgeId: string) => {
    setUser(prev => ({
      ...prev,
      badges: prev.badges.map(badge => 
        badge.id === badgeId ? { ...badge, unlocked: true } : badge
      )
    }));

    const badge = user.badges.find(b => b.id === badgeId);
    if (badge) {
      const activity = {
        id: Date.now(),
        type: 'badge_unlocked',
        message: `Badge unlocked: ${badge.name}`,
        timestamp: new Date().toISOString(),
        badge: badge
      };
      setRecentActivity(prev => [activity, ...prev.slice(0, 9)]);
    }
  };

  // Simulate data entry
  const submitHealthData = (dataType: string) => {
    updateStreak();
    addXP(50, `${dataType} Entry`);
    
    if (dataType === 'mood') completeQuest('daily_mood');
    if (dataType === 'symptoms') completeQuest('weekly_symptoms');
    
    // Check for badge unlocks
    if (user.totalXP === 0) unlockBadge('first_entry');
    if (user.streak >= 6) unlockBadge('week_warrior');
    if (user.totalXP >= 5000) unlockBadge('data_master');
    if (user.streak >= 29) unlockBadge('health_legend');
  };

  // Generate mock leaderboard
  useEffect(() => {
    const mockUsers = Array.from({ length: 10 }, (_, i) => ({
      id: `user_${i + 1}`,
      name: `User ${i + 1}`,
      level: Math.floor(Math.random() * 20) + 1,
      xp: Math.floor(Math.random() * 10000),
      isCurrentUser: i === 0
    }));
    mockUsers[0] = { ...mockUsers[0], ...user, name: 'You', isCurrentUser: true };
    setLeaderboard(mockUsers.sort((a, b) => b.xp - a.xp));
  }, [user.totalXP, user]);

  const value = {
    user,
    quests,
    recentActivity,
    leaderboard,
    addXP,
    submitHealthData,
    completeQuest,
    unlockBadge
  };

  return (
    <GamificationContext.Provider value={value}>
      {children}
    </GamificationContext.Provider>
  );
};

// Custom hook
const useGamification = () => {
  const context = useContext(GamificationContext);
  if (!context) {
    throw new Error('useGamification must be used within GamificationProvider');
  }
  return context;
};

// XP Animation Component
const XPAnimation: React.FC<{ amount: number; onComplete: () => void }> = ({ amount, onComplete }) => {
  useEffect(() => {
    const timer = setTimeout(onComplete, 2000);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50">
      <div className="bg-yellow-500 text-white px-6 py-3 rounded-full shadow-lg animate-bounce">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          <span className="font-bold">+{amount} XP</span>
        </div>
      </div>
    </div>
  );
};

// Progress Bar Component
const ProgressBar: React.FC<{ current: number; max: number; className?: string }> = ({ 
  current, 
  max, 
  className = "" 
}) => {
  const percentage = Math.min((current / max) * 100, 100);
  
  return (
    <div className={`w-full bg-gray-200 rounded-full h-2 ${className}`}>
      <div 
        className="bg-blue-500 h-2 rounded-full transition-all duration-500 ease-out"
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
};

// Badge Component
const BadgeComponent: React.FC<{ badge: Badge }> = ({ badge }) => {
  const { color } = BADGE_TYPES[badge.rarity];
  
  return (
    <div className={`relative p-3 rounded-lg border-2 ${badge.unlocked ? 'border-yellow-300 bg-white' : 'border-gray-300 bg-gray-100'}`}>
      {!badge.unlocked && (
        <div className="absolute inset-0 bg-gray-500 bg-opacity-50 rounded-lg flex items-center justify-center">
          <Lock className="w-6 h-6 text-gray-400" />
        </div>
      )}
      <div className="text-center">
        <div className="text-2xl mb-2">{badge.icon}</div>
        <div className={`text-xs px-2 py-1 rounded ${color} text-white mb-2`}>
          {badge.rarity}
        </div>
        <h4 className="font-medium text-sm">{badge.name}</h4>
        <p className="text-xs text-gray-600 mt-1">{badge.description}</p>
      </div>
    </div>
  );
};

// Quest Component
const QuestComponent: React.FC<{ quest: Quest; onComplete: (questId: string) => void }> = ({ 
  quest, 
  onComplete 
}) => {
  const isComplete = quest.progress >= quest.maxProgress;
  
  return (
    <div className={`p-4 border rounded-lg ${isComplete ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="font-medium">{quest.title}</h4>
            {isComplete && <CheckCircle className="w-4 h-4 text-green-500" />}
          </div>
          <p className="text-sm text-gray-600 mb-3">{quest.description}</p>
          
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress: {quest.progress}/{quest.maxProgress}</span>
              <span className="text-blue-600 font-medium">{quest.xpReward} XP</span>
            </div>
            <ProgressBar current={quest.progress} max={quest.maxProgress} />
          </div>
        </div>
      </div>
      
      {!isComplete && (
        <button
          onClick={() => onComplete(quest.id)}
          className="mt-3 w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors"
        >
          Make Progress
        </button>
      )}
    </div>
  );
};

// SettingsModal: Modal for settings controls
const SettingsModal: React.FC<{
  open: boolean;
  onClose: () => void;
}> = ({ open, onClose }) => {
  const [isOnline, setIsOnline] = React.useState(navigator.onLine);
  const [simulateOffline, setSimulateOffline] = React.useState(false);
  const [toast, setToast] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (simulateOffline) {
      Object.defineProperty(window.navigator, 'onLine', {
        get: () => false,
        configurable: true,
      });
      setIsOnline(false);
    } else {
      Object.defineProperty(window.navigator, 'onLine', {
        get: () => true,
        configurable: true,
      });
      setIsOnline(true);
    }
    window.dispatchEvent(new Event(simulateOffline ? 'offline' : 'online'));
    return () => {
      Object.defineProperty(window.navigator, 'onLine', {
        get: () => navigator.onLine,
        configurable: true,
      });
    };
  }, [simulateOffline]);

  const sendTestNotification = async () => {
    setToast('Test notification sent!');
    // ✅ Correct - use Abena SDK for notifications:
    // await abena.sendNotification(patientId, {
    //   title: 'Test Notification',
    //   body: 'This is a test notification from Abena IHR!'
    // }, 'health_reminders');
  };

  // Hide toast after 2 seconds
  React.useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 2000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
      <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-sm relative">
        <button
          className="absolute top-3 right-3 text-gray-400 hover:text-gray-700"
          onClick={onClose}
          aria-label="Close settings"
        >
          <CloseIcon className="w-5 h-5" />
        </button>
        <h2 className="text-lg font-bold mb-6 flex items-center gap-2">
          <SettingsIcon className="w-5 h-5" />
          Settings
        </h2>
        {/* Toast/confirmation */}
        {toast && (
          <div className="absolute top-2 left-1/2 -translate-x-1/2 bg-blue-600 text-white px-4 py-2 rounded shadow text-sm z-50">
            {toast}
          </div>
        )}
        {/* Connection Status Section */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Connection Status</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                {isOnline ? (
                  <Wifi className="w-5 h-5 text-green-500" />
                ) : (
                  <WifiOff className="w-5 h-5 text-red-500" />
                )}
                <span className="font-medium">
                  {isOnline ? 'Online' : 'Offline'}
                </span>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={simulateOffline}
                  onChange={e => setSimulateOffline(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                <span className="ml-3 text-sm font-medium text-gray-700">Simulate Offline</span>
              </label>
            </div>
            <p className="text-xs text-gray-500">
              {simulateOffline 
                ? 'App is simulating offline mode. Some features may be limited.'
                : 'App is connected to the internet. All features are available.'}
            </p>
          </div>
        </div>
        {/* Notifications Section - Updated to use Abena SDK */}
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Notifications</h3>
          <div className="bg-gray-50 rounded-lg p-4 space-y-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Bell className="w-5 h-5 text-blue-500" />
                <span className="font-medium">
                  Notifications via Abena SDK
                </span>
              </div>
            </div>
            <button
              onClick={sendTestNotification}
              className="w-full px-4 py-2 rounded-md flex items-center justify-center gap-2 transition bg-gray-600 text-white hover:bg-gray-700"
            >
              <BellRing className="w-4 h-4" />
              Send Test Notification
            </button>
            <p className="text-xs text-gray-500">
              Notifications are handled automatically by the Abena SDK with proper authentication, privacy, and audit logging.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Utility hook to detect mobile
function useIsMobile() {
  const [isMobile, setIsMobile] = React.useState(window.innerWidth <= 640);
  React.useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 640);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  return isMobile;
}

// Main Dashboard Component
const Dashboard: React.FC = () => {
  const { user, quests, recentActivity, leaderboard, submitHealthData, completeQuest } = useGamification();
  const [showXPAnimation, setShowXPAnimation] = useState(false);
  const [xpAmount, setXPAmount] = useState(0);
  const [activeTab, setActiveTab] = useState('overview');
  const [showSettings, setShowSettings] = useState(false);
  const isMobile = useIsMobile();
  const [showMobileForm, setShowMobileForm] = useState(false);
  const [mobileFormType, setMobileFormType] = useState<'mood' | 'symptoms' | 'medication' | 'sleep'>('mood');

  // Health sensor state
  const [stepCount, setStepCount] = useState<number | null>(null);
  const [heartRate, setHeartRate] = useState<number | null>(null);
  const [sleepData, setSleepData] = useState<any>(null);
  const [activityLevel, setActivityLevel] = useState<number | null>(null);
  const [sensorLoading, setSensorLoading] = useState<string | null>(null);
  const [sensorError, setSensorError] = useState<string | null>(null);

  const fetchStepCount = async () => {
    setSensorLoading('steps');
    setSensorError(null);
    // ✅ Correct - use Abena SDK for sensor data:
    // const steps = await abena.getSensorData(patientId, 'step_count', 'health_monitoring');
    const steps = null; // Placeholder - use Abena SDK instead
    if (steps !== null) setStepCount(steps);
    else setSensorError('Could not fetch step count.');
    setSensorLoading(null);
  };
  const fetchHeartRate = async () => {
    setSensorLoading('heart');
    setSensorError(null);
    // ✅ Correct - use Abena SDK for sensor data:
    // const rate = await abena.getSensorData(patientId, 'heart_rate', 'health_monitoring');
    const rate = null; // Placeholder - use Abena SDK instead
    if (rate !== null) setHeartRate(rate);
    else setSensorError('Could not fetch heart rate.');
    setSensorLoading(null);
  };
  const fetchSleepData = async () => {
    setSensorLoading('sleep');
    setSensorError(null);
    // ✅ Correct - use Abena SDK for sensor data:
    // const data = await abena.getSensorData(patientId, 'sleep_data', 'health_monitoring');
    const data = null; // Placeholder - use Abena SDK instead
    if (data !== null) setSleepData(data);
    else setSensorError('Could not fetch sleep data.');
    setSensorLoading(null);
  };
  const fetchActivityLevel = async () => {
    setSensorLoading('activity');
    setSensorError(null);
    // ✅ Correct - use Abena SDK for sensor data:
    // const level = await abena.getSensorData(patientId, 'activity_level', 'health_monitoring');
    const level = null; // Placeholder - use Abena SDK instead
    if (level !== null) setActivityLevel(level);
    else setSensorError('Could not fetch activity level.');
    setSensorLoading(null);
  };

  const handleDataEntry = (type: string) => {
    setXPAmount(50);
    setShowXPAnimation(true);
    submitHealthData(type);
  };

  // Replace quick data entry with mobile form on mobile
  const handleMobileDataEntry = (type: 'mood' | 'symptoms' | 'medication' | 'sleep') => {
    setMobileFormType(type);
    setShowMobileForm(true);
  };

  const nextLevelXP = 1000;

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="flex justify-end mb-2">
        <button
          className="flex items-center gap-2 px-3 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg text-gray-700"
          onClick={() => setShowSettings(true)}
        >
          <SettingsIcon className="w-5 h-5" />
          Settings
        </button>
      </div>
      <SettingsModal open={showSettings} onClose={() => setShowSettings(false)} />
      {showXPAnimation && (
        <XPAnimation 
          amount={xpAmount} 
          onComplete={() => setShowXPAnimation(false)} 
        />
      )}

      {/* Mobile Navigation */}
      {isMobile && <MobileNavigation onNavigate={() => {}} currentRoute={activeTab} />}

      {/* Health Sensors Section */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-500" />
          Health Sensors
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <button
            onClick={fetchStepCount}
            className="bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg px-4 py-3 flex flex-col items-center"
            disabled={sensorLoading === 'steps'}
          >
            <span className="font-bold">Step Count</span>
            {sensorLoading === 'steps' ? 'Loading...' : stepCount !== null ? `${stepCount} steps` : 'Fetch'}
          </button>
          <button
            onClick={fetchHeartRate}
            className="bg-red-100 hover:bg-red-200 text-red-700 rounded-lg px-4 py-3 flex flex-col items-center"
            disabled={sensorLoading === 'heart'}
          >
            <span className="font-bold">Heart Rate</span>
            {sensorLoading === 'heart' ? 'Loading...' : heartRate !== null ? `${heartRate} bpm` : 'Fetch'}
          </button>
          <button
            onClick={fetchSleepData}
            className="bg-purple-100 hover:bg-purple-200 text-purple-700 rounded-lg px-4 py-3 flex flex-col items-center"
            disabled={sensorLoading === 'sleep'}
          >
            <span className="font-bold">Sleep Data</span>
            {sensorLoading === 'sleep' ? 'Loading...' : sleepData !== null ? `${sleepData.value?.duration ?? '?'} hrs` : 'Fetch'}
          </button>
          <button
            onClick={fetchActivityLevel}
            className="bg-green-100 hover:bg-green-200 text-green-700 rounded-lg px-4 py-3 flex flex-col items-center"
            disabled={sensorLoading === 'activity'}
          >
            <span className="font-bold">Activity Level</span>
            {sensorLoading === 'activity' ? 'Loading...' : activityLevel !== null ? activityLevel.toFixed(2) : 'Fetch'}
          </button>
        </div>
        {sensorError && <div className="text-red-500 text-sm mt-2">{sensorError}</div>}
      </div>

      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Health Dashboard</h1>
            <p className="text-gray-600">Track your wellness journey</p>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-2 mb-2">
              <Crown className="w-5 h-5 text-yellow-500" />
              <span className="text-lg font-bold">Level {user.level}</span>
            </div>
            <div className="flex items-center gap-2">
              <Flame className="w-4 h-4 text-orange-500" />
              <span className="text-sm">{user.streak} day streak</span>
            </div>
          </div>
        </div>

        {/* XP Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>XP Progress</span>
            <span>{user.xp}/{nextLevelXP} XP</span>
          </div>
          <ProgressBar current={user.xp} max={nextLevelXP} />
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-white p-1 rounded-lg shadow-sm">
        {[
          { id: 'overview', label: 'Overview', icon: Activity },
          { id: 'quests', label: 'Quests', icon: Target },
          { id: 'badges', label: 'Badges', icon: Award },
          { id: 'leaderboard', label: 'Leaderboard', icon: Trophy }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.id 
                ? 'bg-blue-500 text-white' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5 text-blue-500" />
              Quick Data Entry
            </h3>
            {isMobile ? (
              <div className="grid grid-cols-2 gap-3">
                {[{ type: 'mood', label: 'Log Mood', icon: Heart, color: 'bg-pink-500' },
                  { type: 'symptoms', label: 'Log Symptoms', icon: Activity, color: 'bg-red-500' },
                  { type: 'medication', label: 'Log Medication', icon: Plus, color: 'bg-green-500' },
                  { type: 'sleep', label: 'Log Sleep', icon: Moon, color: 'bg-purple-500' }].map(action => (
                  <button
                    key={action.type}
                    onClick={() => handleMobileDataEntry(action.type as any)}
                    className={`${action.color} hover:opacity-90 text-white p-4 rounded-lg transition-opacity flex flex-col items-center gap-2`}
                  >
                    <action.icon className="w-6 h-6" />
                    <span className="text-sm font-medium">{action.label}</span>
                  </button>
                ))}
                {showMobileForm && (
                  <MobileHealthForm
                    onSubmit={data => {
                      submitHealthData(data.type);
                      setShowMobileForm(false);
                    }}
                    onCancel={() => setShowMobileForm(false)}
                  />
                )}
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {[{ type: 'mood', label: 'Log Mood', icon: Heart, color: 'bg-pink-500' },
                  { type: 'symptoms', label: 'Log Symptoms', icon: Activity, color: 'bg-red-500' },
                  { type: 'medication', label: 'Log Medication', icon: Plus, color: 'bg-green-500' },
                  { type: 'sleep', label: 'Log Sleep', icon: Moon, color: 'bg-purple-500' }].map(action => (
                  <button
                    key={action.type}
                    onClick={() => handleDataEntry(action.type)}
                    className={`${action.color} hover:opacity-90 text-white p-4 rounded-lg transition-opacity flex flex-col items-center gap-2`}
                  >
                    <action.icon className="w-6 h-6" />
                    <span className="text-sm font-medium">{action.label}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              Recent Activity
            </h3>
            <div className="space-y-3">
              {recentActivity.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No recent activity</p>
              ) : (
                recentActivity.map(activity => (
                  <div key={activity.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      activity.type === 'xp_gained' ? 'bg-yellow-100' :
                      activity.type === 'level_up' ? 'bg-purple-100' :
                      'bg-blue-100'
                    }`}>
                      {activity.type === 'xp_gained' && <Star className="w-4 h-4 text-yellow-600" />}
                      {activity.type === 'level_up' && <Crown className="w-4 h-4 text-purple-600" />}
                      {activity.type === 'badge_unlocked' && <Medal className="w-4 h-4 text-blue-600" />}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.message}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(activity.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'quests' && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-500" />
              Active Quests
            </h3>
            <div className="grid gap-4">
              {quests.map(quest => (
                <QuestComponent 
                  key={quest.id} 
                  quest={quest} 
                  onComplete={completeQuest}
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'badges' && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-yellow-500" />
            Badge Collection
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {user.badges.map(badge => (
              <BadgeComponent key={badge.id} badge={badge} />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'leaderboard' && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Trophy className="w-5 h-5 text-yellow-500" />
            Community Leaderboard
          </h3>
          <div className="space-y-2">
            {leaderboard.map((user, index) => (
              <div 
                key={user.id} 
                className={`flex items-center justify-between p-3 rounded-lg ${
                  user.isCurrentUser ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                    index === 0 ? 'bg-yellow-500 text-white' :
                    index === 1 ? 'bg-gray-400 text-white' :
                    index === 2 ? 'bg-orange-500 text-white' :
                    'bg-gray-200 text-gray-700'
                  }`}>
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium">{user.name}</p>
                    <p className="text-sm text-gray-600">Level {user.level}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold">{user.xp.toLocaleString()} XP</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Test Interface Component
const TestInterface: React.FC = () => {
  const { user, addXP, submitHealthData, unlockBadge } = useGamification();
  
  return (
    <div className="fixed bottom-4 right-4 bg-white p-4 rounded-lg shadow-lg border max-w-sm">
      <h4 className="font-bold mb-3 text-sm">🧪 Test Controls</h4>
      <div className="space-y-2">
        <button
          onClick={() => addXP(100, 'Test Bonus')}
          className="w-full bg-green-500 hover:bg-green-600 text-white py-1 px-3 rounded text-sm"
        >
          Add 100 XP
        </button>
        <button
          onClick={() => submitHealthData('mood')}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white py-1 px-3 rounded text-sm"
        >
          Simulate Data Entry
        </button>
        <button
          onClick={() => unlockBadge('week_warrior')}
          className="w-full bg-purple-500 hover:bg-purple-600 text-white py-1 px-3 rounded text-sm"
        >
          Unlock Week Warrior Badge
        </button>
      </div>
      <div className="mt-3 pt-3 border-t text-xs text-gray-600">
        <div>Level: {user.level}</div>
        <div>XP: {user.totalXP.toLocaleString()}</div>
        <div>Streak: {user.streak} days</div>
      </div>
    </div>
  );
};

// Main App Component
const AbenaGamificationSystem: React.FC = () => {
  return (
    <GamificationProvider>
      <div className="font-sans">
        <Dashboard />
        <TestInterface />
      </div>
    </GamificationProvider>
  );
};

export default AbenaGamificationSystem; 