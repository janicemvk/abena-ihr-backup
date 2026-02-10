export interface User {
  id: string;
  level: number;
  xp: number;
  totalXP: number;
  streak: number;
  lastEntry: string | null;
  badges: Badge[];
  completedQuests: string[];
  settings: UserSettings;
}

export interface UserSettings {
  notifications: {
    enabled: boolean;
    healthReminders: boolean;
    questAlerts: boolean;
    achievementAlerts: boolean;
  };
  privacy: {
    shareProgress: boolean;
    showOnLeaderboard: boolean;
  };
  theme: 'light' | 'dark' | 'system';
}

export interface Quest {
  id: string;
  title: string;
  description: string;
  type: 'daily' | 'weekly' | 'streak';
  xpReward: number;
  progress: number;
  maxProgress: number;
  category: string;
  requirements?: QuestRequirement[];
}

export interface QuestRequirement {
  type: 'level' | 'badge' | 'quest';
  id: string;
  value?: number;
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  rarity: 'COMMON' | 'RARE' | 'EPIC' | 'LEGENDARY';
  unlocked: boolean;
  unlockedAt?: string;
}

export interface HealthData {
  id: string;
  userId: string;
  type: 'mood' | 'symptoms' | 'medication' | 'sleep';
  value: any;
  timestamp: string;
  notes?: string;
}

export interface Notification {
  id: string;
  userId: string;
  title: string;
  body: string;
  type: 'reminder' | 'achievement' | 'quest';
  read: boolean;
  createdAt: string;
  data?: {
    url?: string;
    questId?: string;
    badgeId?: string;
  };
} 