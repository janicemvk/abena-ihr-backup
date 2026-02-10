import React from 'react';
import { Target, Award, Clock, ChevronRight } from 'lucide-react';
import { Quest } from '../types';

interface MobileQuestCardProps {
  quest: Quest;
  onSelect: (quest: Quest) => void;
}

const MobileQuestCard: React.FC<MobileQuestCardProps> = ({ quest, onSelect }) => {
  const getQuestIcon = (type: string) => {
    switch (type) {
      case 'daily':
        return <Clock className="w-5 h-5" />;
      case 'weekly':
        return <Target className="w-5 h-5" />;
      case 'streak':
        return <Award className="w-5 h-5" />;
      default:
        return <Target className="w-5 h-5" />;
    }
  };

  const progress = (quest.progress / quest.maxProgress) * 100;

  return (
    <div
      onClick={() => onSelect(quest)}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden active:scale-95 transition-transform duration-200"
    >
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              {getQuestIcon(quest.type)}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {quest.title}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {quest.type.charAt(0).toUpperCase() + quest.type.slice(1)} Quest
              </p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-gray-400" />
        </div>

        <p className="text-gray-600 dark:text-gray-300 mb-4">
          {quest.description}
        </p>

        {/* Progress Bar */}
        <div className="mb-2">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">
              Progress: {quest.progress}/{quest.maxProgress}
            </span>
            <span className="text-blue-600 dark:text-blue-400 font-medium">
              {quest.xpReward} XP
            </span>
          </div>
          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Requirements */}
        {quest.requirements && quest.requirements.length > 0 && (
          <div className="mt-3">
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
              Requirements:
            </p>
            <div className="flex flex-wrap gap-2">
              {quest.requirements.map((req, index) => (
                <span
                  key={index}
                  className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full"
                >
                  {req.type}: {req.value || req.id}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MobileQuestCard; 