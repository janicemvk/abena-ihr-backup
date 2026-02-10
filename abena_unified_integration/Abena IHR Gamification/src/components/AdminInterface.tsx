import React, { useState, useEffect } from 'react';
import { 
  Users, Settings, Award, Target, Gift, 
  Plus, Edit, Trash2, Save, X, Search,
  BarChart3, Eye, Shield, AlertTriangle,
  Calendar, Clock, TrendingUp, Filter
} from 'lucide-react';
import { User, Quest, Badge } from '../types';

interface AdminQuest extends Quest {
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
  participantCount: number;
  completionRate: number;
}

interface AdminReward {
  id: string;
  name: string;
  description: string;
  category: string;
  xpCost: number;
  originalValue: number;
  stock: number;
  totalRedeemed: number;
  isActive: boolean;
  createdAt: string;
  supplier: string;
}

interface AdminUser extends User {
  email: string;
  joinedAt: string;
  lastActive: string;
  status: 'active' | 'suspended' | 'pending';
  totalSubmissions: number;
  settings: {
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
  };
}

interface SystemMetrics {
  totalUsers: number;
  activeUsers: number;
  totalQuests: number;
  completedQuests: number;
  totalRewards: number;
  redeemedRewards: number;
  averageStreak: number;
  topLevel: number;
}

const AdminInterface: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'quests' | 'rewards' | 'settings'>('overview');
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [quests, setQuests] = useState<AdminQuest[]>([]);
  const [rewards, setRewards] = useState<AdminReward[]>([]);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState<'quest' | 'reward' | 'user'>('quest');
  const [editingItem, setEditingItem] = useState<any>(null);

  // Mock data initialization
  useEffect(() => {
    loadMockData();
  }, []);

  const loadMockData = () => {
    setLoading(true);
    
    // Mock metrics
    setMetrics({
      totalUsers: 1247,
      activeUsers: 823,
      totalQuests: 45,
      completedQuests: 12847,
      totalRewards: 28,
      redeemedRewards: 456,
      averageStreak: 8.3,
      topLevel: 47
    });

    // Mock users
    const mockUsers: AdminUser[] = Array.from({ length: 10 }, (_, i) => ({
      id: `user_${i + 1}`,
      level: Math.floor(Math.random() * 20) + 1,
      xp: Math.floor(Math.random() * 1000),
      totalXP: Math.floor(Math.random() * 10000),
      streak: Math.floor(Math.random() * 30),
      lastEntry: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      badges: [],
      completedQuests: [],
      email: `user${i + 1}@example.com`,
      joinedAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
      lastActive: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      status: ['active', 'suspended', 'pending'][Math.floor(Math.random() * 3)] as any,
      totalSubmissions: Math.floor(Math.random() * 100),
      settings: {
        notifications: {
          enabled: true,
          healthReminders: true,
          questAlerts: true,
          achievementAlerts: true
        },
        privacy: {
          shareProgress: true,
          showOnLeaderboard: true
        },
        theme: 'light' as const
      }
    }));
    setUsers(mockUsers);

    // Mock quests
    const mockQuests: AdminQuest[] = [
      {
        id: 'admin_quest_1',
        title: 'Daily Wellness Check',
        description: 'Complete your daily health assessment',
        type: 'daily',
        xpReward: 50,
        progress: 0,
        maxProgress: 1,
        category: 'wellness',
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-15T00:00:00Z',
        isActive: true,
        participantCount: 345,
        completionRate: 78.5
      },
      {
        id: 'admin_quest_2',
        title: 'Weekly Symptom Tracker',
        description: 'Log symptoms for 7 consecutive days',
        type: 'weekly',
        xpReward: 200,
        progress: 0,
        maxProgress: 7,
        category: 'health',
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-15T00:00:00Z',
        isActive: true,
        participantCount: 156,
        completionRate: 45.2
      }
    ];
    setQuests(mockQuests);

    // Mock rewards
    const mockRewards: AdminReward[] = [
      {
        id: 'admin_reward_1',
        name: 'CBD Sample Pack',
        description: 'Premium CBD tincture samples',
        category: 'cbd',
        xpCost: 2500,
        originalValue: 45.99,
        stock: 50,
        totalRedeemed: 23,
        isActive: true,
        createdAt: '2024-01-01T00:00:00Z',
        supplier: 'Abena Wellness'
      },
      {
        id: 'admin_reward_2',
        name: 'Wellness Consultation',
        description: '1-on-1 consultation with health expert',
        category: 'services',
        xpCost: 5000,
        originalValue: 149.99,
        stock: 10,
        totalRedeemed: 5,
        isActive: true,
        createdAt: '2024-01-01T00:00:00Z',
        supplier: 'Abena Experts'
      }
    ];
    setRewards(mockRewards);

    setLoading(false);
  };

  // Quest Management
  const createQuest = (questData: Partial<AdminQuest>) => {
    const newQuest: AdminQuest = {
      id: `quest_${Date.now()}`,
      title: questData.title || '',
      description: questData.description || '',
      type: questData.type || 'daily',
      xpReward: questData.xpReward || 50,
      progress: 0,
      maxProgress: questData.maxProgress || 1,
      category: questData.category || 'general',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isActive: true,
      participantCount: 0,
      completionRate: 0
    };
    
    setQuests(prev => [...prev, newQuest]);
    setShowModal(false);
    setEditingItem(null);
  };

  const updateQuest = (questId: string, updates: Partial<AdminQuest>) => {
    setQuests(prev => prev.map(quest => 
      quest.id === questId 
        ? { ...quest, ...updates, updatedAt: new Date().toISOString() }
        : quest
    ));
    setShowModal(false);
    setEditingItem(null);
  };

  const deleteQuest = (questId: string) => {
    setQuests(prev => prev.filter(quest => quest.id !== questId));
  };

  // Reward Management
  const createReward = (rewardData: Partial<AdminReward>) => {
    const newReward: AdminReward = {
      id: `reward_${Date.now()}`,
      name: rewardData.name || '',
      description: rewardData.description || '',
      category: rewardData.category || 'general',
      xpCost: rewardData.xpCost || 1000,
      originalValue: rewardData.originalValue || 0,
      stock: rewardData.stock || 0,
      totalRedeemed: 0,
      isActive: true,
      createdAt: new Date().toISOString(),
      supplier: rewardData.supplier || 'Unknown'
    };
    
    setRewards(prev => [...prev, newReward]);
    setShowModal(false);
    setEditingItem(null);
  };

  const updateReward = (rewardId: string, updates: Partial<AdminReward>) => {
    setRewards(prev => prev.map(reward => 
      reward.id === rewardId ? { ...reward, ...updates } : reward
    ));
    setShowModal(false);
    setEditingItem(null);
  };

  const deleteReward = (rewardId: string) => {
    setRewards(prev => prev.filter(reward => reward.id !== rewardId));
  };

  // User Management
  const updateUserStatus = (userId: string, status: 'active' | 'suspended' | 'pending') => {
    setUsers(prev => prev.map(user => 
      user.id === userId ? { ...user, status } : user
    ));
  };

  const filteredUsers = users.filter(user => 
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredQuests = quests.filter(quest =>
    quest.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    quest.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredRewards = rewards.filter(reward =>
    reward.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    reward.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Modal Components
  const QuestModal: React.FC = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-lg max-w-2xl w-full m-4 p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold">
            {editingItem ? 'Edit Quest' : 'Create New Quest'}
          </h3>
          <button 
            onClick={() => { setShowModal(false); setEditingItem(null); }}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <form onSubmit={(e) => {
          e.preventDefault();
          const formData = new FormData(e.target as HTMLFormElement);
          const questData = {
            title: formData.get('title') as string,
            description: formData.get('description') as string,
            type: formData.get('type') as 'daily' | 'weekly' | 'streak',
            xpReward: parseInt(formData.get('xpReward') as string),
            maxProgress: parseInt(formData.get('maxProgress') as string),
            category: formData.get('category') as string,
          };
          
          if (editingItem) {
            updateQuest(editingItem.id, questData);
          } else {
            createQuest(questData);
          }
        }}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
              <input
                name="title"
                type="text"
                defaultValue={editingItem?.title || ''}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                name="category"
                defaultValue={editingItem?.category || 'wellness'}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="wellness">Wellness</option>
                <option value="health">Health</option>
                <option value="fitness">Fitness</option>
                <option value="mental">Mental Health</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
              <select
                name="type"
                defaultValue={editingItem?.type || 'daily'}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="streak">Streak</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">XP Reward</label>
              <input
                name="xpReward"
                type="number"
                defaultValue={editingItem?.xpReward || 50}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Max Progress</label>
              <input
                name="maxProgress"
                type="number"
                defaultValue={editingItem?.maxProgress || 1}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              name="description"
              rows={3}
              defaultValue={editingItem?.description || ''}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => { setShowModal(false); setEditingItem(null); }}
              className="flex-1 py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
            >
              {editingItem ? 'Update Quest' : 'Create Quest'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Shield className="w-8 h-8 text-blue-500" />
              Admin Dashboard
            </h1>
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex space-x-1 py-4">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'users', label: 'Users', icon: Users },
            { id: 'quests', label: 'Quests', icon: Target },
            { id: 'rewards', label: 'Rewards', icon: Gift },
            { id: 'settings', label: 'Settings', icon: Settings }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === tab.id 
                  ? 'bg-blue-500 text-white' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        {activeTab === 'overview' && metrics && (
          <div className="space-y-6">
            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { label: 'Total Users', value: metrics.totalUsers, icon: Users, color: 'blue' },
                { label: 'Active Users', value: metrics.activeUsers, icon: TrendingUp, color: 'green' },
                { label: 'Total Quests', value: metrics.totalQuests, icon: Target, color: 'purple' },
                { label: 'Rewards Redeemed', value: metrics.redeemedRewards, icon: Gift, color: 'orange' }
              ].map((metric, index) => (
                <div key={index} className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">{metric.label}</p>
                      <p className="text-2xl font-bold text-gray-900">{metric.value.toLocaleString()}</p>
                    </div>
                    <div className={`w-12 h-12 rounded-lg bg-${metric.color}-100 flex items-center justify-center`}>
                      <metric.icon className={`w-6 h-6 text-${metric.color}-600`} />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
              <div className="space-y-3">
                {[
                  { action: 'New user registration', user: 'user_123@example.com', time: '2 minutes ago' },
                  { action: 'Quest completed', user: 'user_456@example.com', time: '5 minutes ago' },
                  { action: 'Reward redeemed', user: 'user_789@example.com', time: '12 minutes ago' }
                ].map((activity, index) => (
                  <div key={index} className="flex items-center justify-between py-2 border-b last:border-b-0">
                    <div>
                      <p className="font-medium">{activity.action}</p>
                      <p className="text-sm text-gray-600">{activity.user}</p>
                    </div>
                    <span className="text-sm text-gray-500">{activity.time}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold">User Management</h3>
                  <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    Add User
                  </button>
                </div>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Level</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Streak</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Active</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {filteredUsers.map(user => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-medium text-gray-900">{user.email}</div>
                            <div className="text-sm text-gray-500">{user.id}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">{user.level}</td>
                        <td className="px-6 py-4 text-sm text-gray-900">{user.streak} days</td>
                        <td className="px-6 py-4">
                          <select
                            value={user.status}
                            onChange={(e) => updateUserStatus(user.id, e.target.value as any)}
                            className={`text-sm px-2 py-1 rounded-full ${
                              user.status === 'active' ? 'bg-green-100 text-green-800' :
                              user.status === 'suspended' ? 'bg-red-100 text-red-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}
                          >
                            <option value="active">Active</option>
                            <option value="suspended">Suspended</option>
                            <option value="pending">Pending</option>
                          </select>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {new Date(user.lastActive).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <button className="text-blue-600 hover:text-blue-800">
                              <Eye className="w-4 h-4" />
                            </button>
                            <button className="text-gray-600 hover:text-gray-800">
                              <Edit className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'quests' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold">Quest Management</h3>
                  <button 
                    onClick={() => { setModalType('quest'); setShowModal(true); }}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2"
                  >
                    <Plus className="w-4 h-4" />
                    Create Quest
                  </button>
                </div>
              </div>
              
              <div className="p-6">
                <div className="grid gap-4">
                  {filteredQuests.map(quest => (
                    <div key={quest.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h4 className="font-semibold text-lg">{quest.title}</h4>
                          <p className="text-gray-600 text-sm">{quest.description}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 rounded-full text-xs ${quest.isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                            {quest.isActive ? 'Active' : 'Inactive'}
                          </span>
                          <button 
                            onClick={() => { setEditingItem(quest); setModalType('quest'); setShowModal(true); }}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button 
                            onClick={() => deleteQuest(quest.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Type:</span>
                          <div className="font-medium">{quest.type}</div>
                        </div>
                        <div>
                          <span className="text-gray-500">XP Reward:</span>
                          <div className="font-medium">{quest.xpReward}</div>
                        </div>
                        <div>
                          <span className="text-gray-500">Participants:</span>
                          <div className="font-medium">{quest.participantCount}</div>
                        </div>
                        <div>
                          <span className="text-gray-500">Completion Rate:</span>
                          <div className="font-medium">{quest.completionRate}%</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'rewards' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm">
              <div className="p-6 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold">Reward Management</h3>
                  <button 
                    onClick={() => { setModalType('reward'); setShowModal(true); }}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2"
                  >
                    <Plus className="w-4 h-4" />
                    Add Reward
                  </button>
                </div>
              </div>
              
              <div className="p-6">
                <div className="grid gap-4">
                  {filteredRewards.map(reward => (
                    <div key={reward.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h4 className="font-semibold text-lg">{reward.name}</h4>
                          <p className="text-gray-600 text-sm">{reward.description}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 rounded-full text-xs ${reward.isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                            {reward.isActive ? 'Active' : 'Inactive'}
                          </span>
                          <button 
                            onClick={() => { setEditingItem(reward); setModalType('reward'); setShowModal(true); }}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button 
                            onClick={() => deleteReward(reward.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Category:</span>
                          <div className="font-medium">{reward.category}</div>
                        </div>
                        <div>
                          <span className="text-gray-500">XP Cost:</span>
                          <div className="font-medium">{reward.xpCost}</div>
                        </div>
                        <div>
                          <span className="text-gray-500">Stock:</span>
                          <div className="font-medium">{reward.stock}</div>
                        </div>
                        <div>
                          <span className="text-gray-500">Redeemed:</span>
                          <div className="font-medium">{reward.totalRedeemed}</div>
                        </div>
                        <div>
                          <span className="text-gray-500">Supplier:</span>
                          <div className="font-medium">{reward.supplier}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-6">System Settings</h3>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">XP per Level</label>
                  <input
                    type="number"
                    defaultValue={1000}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-sm text-gray-500 mt-1">Amount of XP required to level up</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Default Quest Reward</label>
                  <input
                    type="number"
                    defaultValue={50}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-sm text-gray-500 mt-1">Default XP reward for new quests</p>
                </div>
                
                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      defaultChecked
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Enable notifications</span>
                  </label>
                </div>
                
                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      defaultChecked
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Auto-approve new users</span>
                  </label>
                </div>
                
                <button className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg">
                  Save Settings
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {showModal && modalType === 'quest' && <QuestModal />}
      
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-25 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 flex items-center gap-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span>Loading...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminInterface; 