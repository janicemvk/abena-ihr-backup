import React, { useState } from 'react';
import { Home, Trophy, Target, Settings, Menu } from 'lucide-react';

interface MobileNavigationProps {
  onNavigate: (route: string) => void;
  currentRoute: string;
}

const MobileNavigation: React.FC<MobileNavigationProps> = ({ onNavigate, currentRoute }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navItems = [
    { id: 'home', icon: Home, label: 'Home' },
    { id: 'quests', icon: Target, label: 'Quests' },
    { id: 'achievements', icon: Trophy, label: 'Achievements' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      <div className="flex justify-around items-center h-16 px-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentRoute === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`flex flex-col items-center justify-center w-full h-full transition-colors duration-200 ${
                isActive
                  ? 'text-blue-600 dark:text-blue-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-blue-500 dark:hover:text-blue-300'
              }`}
            >
              <Icon className="w-6 h-6" />
              <span className="text-xs mt-1">{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Pull to refresh indicator */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-blue-500 transform -translate-y-full transition-transform duration-300" />

      {/* Swipe menu */}
      <div
        className={`fixed top-0 left-0 h-full w-64 bg-white dark:bg-gray-800 transform transition-transform duration-300 ease-in-out ${
          isMenuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-4">
          <button
            onClick={() => setIsMenuOpen(false)}
            className="absolute top-4 right-4 text-gray-600 dark:text-gray-400"
          >
            <Menu className="w-6 h-6" />
          </button>
          <div className="mt-8">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">Menu</h2>
            <nav className="mt-4">
              <ul className="space-y-2">
                <li>
                  <button
                    onClick={() => {
                      onNavigate('profile');
                      setIsMenuOpen(false);
                    }}
                    className="w-full text-left px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                  >
                    Profile
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => {
                      onNavigate('health-data');
                      setIsMenuOpen(false);
                    }}
                    className="w-full text-left px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                  >
                    Health Data
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => {
                      onNavigate('leaderboard');
                      setIsMenuOpen(false);
                    }}
                    className="w-full text-left px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                  >
                    Leaderboard
                  </button>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MobileNavigation; 