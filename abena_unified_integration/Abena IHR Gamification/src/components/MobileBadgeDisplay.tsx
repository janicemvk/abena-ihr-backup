import React from 'react';
import { Badge } from '../types';
import { Trophy, Star, Zap, Crown } from 'lucide-react';

// ✅ Correct - uses Abena SDK for auth & data handling:
// import AbenaSDK from '@abena/sdk';
// 
// class BadgeService {
//   constructor() {
//     this.abena = new AbenaSDK({
//       authServiceUrl: 'http://localhost:3001',
//       dataServiceUrl: 'http://localhost:8001',
//       privacyServiceUrl: 'http://localhost:8002',
//       blockchainServiceUrl: 'http://localhost:8003'
//     });
//   }
//   
//   async getBadges(userId) {
//     // 1. Auto-handled auth & permissions
//     const badges = await this.abena.getUserBadges(userId, 'gamification_module');
//     
//     // 2. Auto-handled privacy & encryption
//     // 3. Auto-handled audit logging
//     
//     // 4. Focus on your business logic
//     return this.processBadges(badges);
//   }
// }

interface MobileBadgeDisplayProps {
  badge: Badge;
  onSelect?: (badge: Badge) => void;
}

const MobileBadgeDisplay: React.FC<MobileBadgeDisplayProps> = ({ badge, onSelect }) => {
  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'COMMON':
        return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300';
      case 'RARE':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400';
      case 'EPIC':
        return 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400';
      case 'LEGENDARY':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300';
    }
  };

  const getRarityIcon = (rarity: string) => {
    switch (rarity) {
      case 'COMMON':
        return <Star className="w-4 h-4" />;
      case 'RARE':
        return <Zap className="w-4 h-4" />;
      case 'EPIC':
        return <Trophy className="w-4 h-4" />;
      case 'LEGENDARY':
        return <Crown className="w-4 h-4" />;
      default:
        return <Star className="w-4 h-4" />;
    }
  };

  return (
    <div
      onClick={() => onSelect?.(badge)}
      className={`relative group ${
        onSelect ? 'cursor-pointer active:scale-95' : ''
      } transition-all duration-200`}
    >
      <div className="relative">
        {/* Badge Icon */}
        <div
          className={`w-20 h-20 rounded-full flex items-center justify-center ${
            badge.unlocked
              ? getRarityColor(badge.rarity)
              : 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-600'
          }`}
        >
          <img
            src={badge.icon}
            alt={badge.name}
            className={`w-12 h-12 ${
              !badge.unlocked && 'opacity-50 grayscale'
            }`}
          />
        </div>

        {/* Rarity Indicator */}
        <div
          className={`absolute -top-1 -right-1 p-1 rounded-full ${
            badge.unlocked ? getRarityColor(badge.rarity) : 'bg-gray-200 dark:bg-gray-700'
          }`}
        >
          {getRarityIcon(badge.rarity)}
        </div>

        {/* Unlock Date */}
        {badge.unlocked && badge.unlockedAt && (
          <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 bg-white dark:bg-gray-800 px-2 py-1 rounded-full text-xs text-gray-500 dark:text-gray-400 shadow-sm">
            {new Date(badge.unlockedAt).toLocaleDateString()}
          </div>
        )}
      </div>

      {/* Badge Info */}
      <div className="mt-2 text-center">
        <h3
          className={`text-sm font-medium ${
            badge.unlocked
              ? 'text-gray-900 dark:text-white'
              : 'text-gray-500 dark:text-gray-400'
          }`}
        >
          {badge.name}
        </h3>
        <p
          className={`text-xs ${
            badge.unlocked
              ? 'text-gray-600 dark:text-gray-300'
              : 'text-gray-400 dark:text-gray-500'
          }`}
        >
          {badge.description}
        </p>
      </div>

      {/* Hover Effect */}
      {onSelect && (
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-5 dark:group-hover:bg-opacity-10 rounded-xl transition-opacity duration-200" />
      )}
    </div>
  );
};

export default MobileBadgeDisplay; 