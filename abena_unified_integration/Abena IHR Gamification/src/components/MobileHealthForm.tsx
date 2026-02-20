import React, { useState } from 'react';
import { Activity, Heart, Moon, Thermometer } from 'lucide-react';
import { HealthData } from '../types';

interface MobileHealthFormProps {
  onSubmit: (data: HealthData) => void;
  onCancel: () => void;
}

const MobileHealthForm: React.FC<MobileHealthFormProps> = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<Partial<HealthData>>({
    type: 'mood',
    value: '',
    notes: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.type) {
      newErrors.type = 'Please select a health data type';
    }

    if (!formData.value) {
      newErrors.value = 'Please enter a value';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit({
        id: Date.now().toString(),
        userId: 'current-user',
        type: formData.type as 'mood' | 'symptoms' | 'medication' | 'sleep',
        value: formData.value,
        timestamp: new Date().toISOString(),
        notes: formData.notes,
      });
    }
  };

  const healthTypes = [
    { id: 'mood' as const, icon: Activity, label: 'Mood' },
    { id: 'symptoms' as const, icon: Thermometer, label: 'Symptoms' },
    { id: 'medication' as const, icon: Heart, label: 'Medication' },
    { id: 'sleep' as const, icon: Moon, label: 'Sleep' },
  ];

  return (
    <div className="fixed inset-0 bg-white dark:bg-gray-900 z-50 overflow-y-auto">
      <div className="min-h-screen px-4 py-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              Log Health Data
            </h2>

            {/* Health Type Selection */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              {healthTypes.map((type) => {
                const Icon = type.icon;
                const isSelected = formData.type === type.id;
                return (
                  <button
                    key={type.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, type: type.id })}
                    className={`flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-colors duration-200 ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700'
                    }`}
                  >
                    <Icon
                      className={`w-8 h-8 mb-2 ${
                        isSelected ? 'text-blue-500' : 'text-gray-500 dark:text-gray-400'
                      }`}
                    />
                    <span
                      className={`text-sm font-medium ${
                        isSelected ? 'text-blue-500' : 'text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      {type.label}
                    </span>
                  </button>
                );
              })}
            </div>
            {errors.type && (
              <p className="text-red-500 text-sm mt-1">{errors.type}</p>
            )}

            {/* Value Input */}
            <div className="mb-6">
              <label
                htmlFor="value"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Value
              </label>
              <input
                type="text"
                id="value"
                value={formData.value}
                onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter value..."
              />
              {errors.value && (
                <p className="text-red-500 text-sm mt-1">{errors.value}</p>
              )}
            </div>

            {/* Notes Input */}
            <div className="mb-6">
              <label
                htmlFor="notes"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Notes (Optional)
              </label>
              <textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={4}
                placeholder="Add any additional notes..."
              />
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={onCancel}
                className="flex-1 px-6 py-3 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-6 py-3 rounded-lg bg-blue-500 text-white hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200"
              >
                Save
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MobileHealthForm; 