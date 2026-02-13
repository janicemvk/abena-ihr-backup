import React, { useState, useEffect } from 'react';
import {
  Trophy, Star, Target, Heart, Activity,
  Plus, CheckCircle, Lock,
  Crown, Medal, Flame, Sparkles, Moon,
  TrendingUp, Award, Zap
} from 'lucide-react';

// Badge rarity configuration
const BADGE_TYPES = {
  COMMON: { color: 'bg-gray-500', textColor: 'text-gray-700', border: 'border-gray-300' },
  RARE: { color: 'bg-blue-500', textColor: 'text-blue-700', border: 'border-blue-400' },
  EPIC: { color: 'bg-purple-500', textColor: 'text-purple-700', border: 'border-purple-400' },
  LEGENDARY: { color: 'bg-yellow-500', textColor: 'text-yellow-700', border: 'border-yellow-400' }
};

// Initial quests for patient health data collection
const INITIAL_QUESTS = [
  {
    id: 'daily_mood',
    title: 'Daily Mood Check',
    description: 'Log your mood and energy level - critical for eCBome tracking',
    type: 'daily',
    xpReward: 50,
    progress: 0,
    maxProgress: 1,
    category: 'wellness',
    icon: Heart
  },
  {
    id: 'weekly_symptoms',
    title: 'Weekly Symptom Tracker',
    description: 'Complete 7 days of symptom logging - essential health data',
    type: 'weekly',
    xpReward: 300,
    progress: 0,
    maxProgress: 7,
    category: 'health',
    icon: Activity
  },
  {
    id: 'consistency_streak',
    title: 'Build Your Streak',
    description: 'Maintain a 5-day data entry streak - consistent data improves analysis',
    type: 'streak',
    xpReward: 500,
    progress: 0,
    maxProgress: 5,
    category: 'consistency',
    icon: Flame
  },
  {
    id: 'sleep_logging',
    title: 'Sleep Pattern Logger',
    description: 'Log your sleep quality for 7 days - critical for eCBome balance',
    type: 'weekly',
    xpReward: 250,
    progress: 0,
    maxProgress: 7,
    category: 'sleep',
    icon: Moon
  }
];

// Initial badges
const INITIAL_BADGES = [
  { id: 'first_entry', name: 'First Steps', description: 'Made your first health data entry', icon: '🌱', rarity: 'COMMON', unlocked: false },
  { id: 'week_warrior', name: 'Week Warrior', description: '7-day streak achieved', icon: '⚡', rarity: 'RARE', unlocked: false },
  { id: 'data_master', name: 'Data Master', description: '100 health entries completed', icon: '📊', rarity: 'EPIC', unlocked: false },
  { id: 'health_legend', name: 'Health Legend', description: '30-day streak champion', icon: '👑', rarity: 'LEGENDARY', unlocked: false },
  { id: 'ecbome_expert', name: 'eCBome Expert', description: 'Completed comprehensive eCBome data collection', icon: '🧬', rarity: 'EPIC', unlocked: false }
];

// XP Animation Component
const XPAnimation = ({ amount, onComplete }) => {
  useEffect(() => {
    const timer = setTimeout(onComplete, 2000);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 animate-bounce">
      <div className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-8 py-4 rounded-full shadow-2xl">
        <div className="flex items-center gap-3">
          <Sparkles className="w-6 h-6 animate-pulse" />
          <span className="font-bold text-xl">+{amount} XP</span>
          <Sparkles className="w-6 h-6 animate-pulse" />
        </div>
      </div>
    </div>
  );
};

// Progress Bar Component
const ProgressBar = ({ current, max, className = '' }) => {
  const percentage = Math.min((current / max) * 100, 100);
  
  return (
    <div className={`w-full bg-gray-200 rounded-full h-2.5 ${className}`}>
      <div 
        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2.5 rounded-full transition-all duration-500 ease-out"
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
};

// Badge Component
const BadgeCard = ({ badge }) => {
  const { color, border } = BADGE_TYPES[badge.rarity];
  
  return (
    <div className={`relative p-4 rounded-lg border-2 ${badge.unlocked ? `${border} bg-white shadow-md` : 'border-gray-200 bg-gray-50'} transition-all hover:scale-105`}>
      {!badge.unlocked && (
        <div className="absolute inset-0 bg-gray-500 bg-opacity-70 rounded-lg flex items-center justify-center backdrop-blur-sm">
          <Lock className="w-8 h-8 text-gray-300" />
        </div>
      )}
      <div className="text-center">
        <div className="text-4xl mb-2">{badge.icon}</div>
        <div className={`inline-block text-xs px-3 py-1 rounded-full ${color} text-white font-semibold mb-2`}>
          {badge.rarity}
        </div>
        <h4 className="font-bold text-sm mb-1">{badge.name}</h4>
        <p className="text-xs text-gray-600">{badge.description}</p>
      </div>
    </div>
  );
};

// Quest Card Component
const QuestCard = ({ quest, onProgress }) => {
  const isComplete = quest.progress >= quest.maxProgress;
  const Icon = quest.icon;
  
  return (
    <div className={`p-5 border-2 rounded-xl transition-all ${isComplete ? 'bg-gradient-to-br from-green-50 to-green-100 border-green-300' : 'bg-white border-gray-200 hover:border-blue-300'} shadow-sm hover:shadow-md`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${isComplete ? 'bg-green-200' : 'bg-blue-100'}`}>
            <Icon className={`w-5 h-5 ${isComplete ? 'text-green-700' : 'text-blue-700'}`} />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h4 className="font-bold text-gray-900">{quest.title}</h4>
              {isComplete && <CheckCircle className="w-5 h-5 text-green-500" />}
            </div>
            <span className={`text-xs font-medium px-2 py-1 rounded-full ${isComplete ? 'bg-green-200 text-green-700' : 'bg-gray-200 text-gray-600'}`}>
              {quest.category}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-1 text-yellow-600 font-bold">
          <Star className="w-4 h-4 fill-current" />
          <span>{quest.xpReward}</span>
        </div>
      </div>
      
      <p className="text-sm text-gray-600 mb-4">{quest.description}</p>
      
      <div className="space-y-2">
        <div className="flex justify-between text-sm font-medium">
          <span className="text-gray-700">Progress: {quest.progress}/{quest.maxProgress}</span>
          <span className="text-blue-600">{Math.round((quest.progress / quest.maxProgress) * 100)}%</span>
        </div>
        <ProgressBar current={quest.progress} max={quest.maxProgress} />
      </div>
      
      {!isComplete && (
        <button
          onClick={() => onProgress(quest.id)}
          className="mt-4 w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white py-2.5 px-4 rounded-lg text-sm font-bold transition-all transform hover:scale-105 shadow-md"
        >
          Log Health Data ({quest.category})
        </button>
      )}
    </div>
  );
};

// Main Gamification Panel Component
const GamificationPanel = ({ onDataLogged }) => {
  const [user, setUser] = useState({
    id: 'patient_' + Math.random().toString(36).substr(2, 9),
    level: 1,
    xp: 0,
    totalXP: 0,
    streak: 0,
    lastEntry: null,
    badges: INITIAL_BADGES,
    completedQuests: [],
    totalDataEntries: 0
  });

  const [quests, setQuests] = useState(INITIAL_QUESTS);
  const [recentActivity, setRecentActivity] = useState([]);
  const [showXPAnimation, setShowXPAnimation] = useState(false);
  const [xpAmount, setXPAmount] = useState(0);
  const [activeTab, setActiveTab] = useState('quests');

  const nextLevelXP = 1000;

  // Get level from total XP
  const getLevelFromXP = (xp) => Math.floor(xp / 1000) + 1;

  // Add XP and handle level ups
  const addXP = (amount, source = 'Data Entry') => {
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
          message: `🎉 Level up! Now level ${newLevel}`,
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
      
      // Check streak badges
      if (newStreak >= 7) unlockBadge('week_warrior');
      if (newStreak >= 30) unlockBadge('health_legend');
      
      return {
        ...prev,
        streak: newStreak,
        lastEntry: today
      };
    });
  };

  // Complete quest
  const completeQuest = (questId) => {
    setQuests(prev => prev.map(quest => {
      if (quest.id === questId && quest.progress < quest.maxProgress) {
        const newProgress = quest.progress + 1;
        const isComplete = newProgress >= quest.maxProgress;
        
        if (isComplete) {
          setXPAmount(quest.xpReward);
          setShowXPAnimation(true);
          addXP(quest.xpReward, `Quest: ${quest.title}`);
          setUser(userPrev => ({
            ...userPrev,
            completedQuests: [...userPrev.completedQuests, questId]
          }));

          // Quest completion activity
          setRecentActivity(prev => [{
            id: Date.now(),
            type: 'quest_complete',
            message: `✅ Quest completed: ${quest.title}`,
            timestamp: new Date().toISOString()
          }, ...prev.slice(0, 9)]);
        }
        
        return { ...quest, progress: newProgress };
      }
      return quest;
    }));
  };

  // Unlock badge
  const unlockBadge = (badgeId) => {
    setUser(prev => {
      const alreadyUnlocked = prev.badges.find(b => b.id === badgeId)?.unlocked;
      if (alreadyUnlocked) return prev;

      const badge = prev.badges.find(b => b.id === badgeId);
      if (badge) {
        setRecentActivity(activity => [{
          id: Date.now(),
          type: 'badge_unlocked',
          message: `🏆 Badge unlocked: ${badge.name} (${badge.rarity})`,
          timestamp: new Date().toISOString(),
          badge: badge
        }, ...activity.slice(0, 9)]);
      }

      return {
        ...prev,
        badges: prev.badges.map(badge => 
          badge.id === badgeId ? { ...badge, unlocked: true } : badge
        )
      };
    });
  };

  // Handle health data entry
  const handleDataEntry = (category) => {
    updateStreak();
    
    // Award XP for data entry
    setXPAmount(50);
    setShowXPAnimation(true);
    addXP(50, `${category} data entry`);
    
    // Update quest progress based on category
    if (category === 'wellness') completeQuest('daily_mood');
    if (category === 'health') completeQuest('weekly_symptoms');
    if (category === 'sleep') completeQuest('sleep_logging');
    if (user.streak >= 4) completeQuest('consistency_streak');
    
    // Update total entries
    setUser(prev => {
      const newTotal = prev.totalDataEntries + 1;
      
      // Check entry-based badges
      if (newTotal === 1) unlockBadge('first_entry');
      if (newTotal >= 100) unlockBadge('data_master');
      if (newTotal >= 50 && user.streak >= 7) unlockBadge('ecbome_expert');
      
      return { ...prev, totalDataEntries: newTotal };
    });

    // Notify parent component about data entry
    if (onDataLogged) {
      onDataLogged({ category, timestamp: new Date().toISOString(), user });
    }
  };

  return (
    <div className="space-y-6">
      {showXPAnimation && (
        <XPAnimation 
          amount={xpAmount} 
          onComplete={() => setShowXPAnimation(false)} 
        />
      )}

      {/* Header Card - User Progress */}
      <div className="bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-2xl shadow-xl p-6 text-white">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold mb-1">Health Rewards</h2>
            <p className="text-indigo-100">Track progress • Earn rewards • Improve health</p>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-2 mb-2">
              <Crown className="w-7 h-7 text-yellow-300" />
              <span className="text-3xl font-bold">Level {user.level}</span>
            </div>
            <div className="flex items-center gap-2 justify-end">
              <Flame className="w-5 h-5 text-orange-300" />
              <span className="text-lg font-semibold">{user.streak} day streak 🔥</span>
            </div>
          </div>
        </div>

        {/* XP Progress Bar */}
        <div className="space-y-2 bg-white bg-opacity-20 rounded-lg p-4 backdrop-blur-sm">
          <div className="flex justify-between text-sm font-semibold">
            <span>XP Progress to Next Level</span>
            <span>{user.xp}/{nextLevelXP} XP</span>
          </div>
          <div className="w-full bg-white bg-opacity-30 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-yellow-300 to-orange-400 h-3 rounded-full transition-all duration-500 ease-out shadow-lg"
              style={{ width: `${(user.xp / nextLevelXP) * 100}%` }}
            />
          </div>
          <div className="text-xs text-indigo-100">
            Total Entries: {user.totalDataEntries} | Total XP: {user.totalXP.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-2 bg-white p-2 rounded-xl shadow-sm">
        {[
          { id: 'quests', label: 'Active Quests', icon: Target },
          { id: 'badges', label: 'Badges', icon: Award },
          { id: 'activity', label: 'Activity', icon: TrendingUp }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg text-sm font-bold transition-all ${
              activeTab === tab.id 
                ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-md' 
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            <tab.icon className="w-5 h-5" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content Sections */}
      {activeTab === 'quests' && (
        <div className="space-y-4">
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-blue-900">Why Gamification Matters</h3>
            </div>
            <p className="text-sm text-blue-800">
              Complete quests by logging your health data regularly. This data is <span className="font-bold">critical for your eCBome analysis</span>, quantum health optimization, and personalized treatment plans. The more consistent you are, the better insights we can provide!
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {quests.map(quest => (
              <QuestCard 
                key={quest.id} 
                quest={quest} 
                onProgress={handleDataEntry.bind(null, quest.category)}
              />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'badges' && (
        <div className="space-y-4">
          <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Trophy className="w-5 h-5 text-yellow-600" />
              <h3 className="font-bold text-yellow-900">Badge Collection</h3>
            </div>
            <p className="text-sm text-yellow-800">
              Unlock badges by consistently logging health data. Each badge represents a milestone in your health journey!
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {user.badges.map(badge => (
              <BadgeCard key={badge.id} badge={badge} />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'activity' && (
        <div className="space-y-4">
          <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <h3 className="font-bold text-green-900">Recent Activity</h3>
            </div>
            <p className="text-sm text-green-800">
              Your recent progress and achievements. Keep up the great work!
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="space-y-3">
              {recentActivity.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Activity className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>No activity yet. Start logging health data to see your progress!</p>
                </div>
              ) : (
                recentActivity.map(activity => (
                  <div key={activity.id} className="flex items-center gap-4 p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border border-gray-200">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      activity.type === 'xp_gained' ? 'bg-yellow-100' :
                      activity.type === 'level_up' ? 'bg-purple-100' :
                      activity.type === 'quest_complete' ? 'bg-green-100' :
                      'bg-blue-100'
                    }`}>
                      {activity.type === 'xp_gained' && <Star className="w-5 h-5 text-yellow-600" />}
                      {activity.type === 'level_up' && <Crown className="w-5 h-5 text-purple-600" />}
                      {activity.type === 'quest_complete' && <CheckCircle className="w-5 h-5 text-green-600" />}
                      {activity.type === 'badge_unlocked' && <Medal className="w-5 h-5 text-blue-600" />}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{activity.message}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(activity.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GamificationPanel;

