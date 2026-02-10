import React from 'react';
import { motion } from 'framer-motion';
import { Loader2, Activity, Brain } from 'lucide-react';

const LoadingSpinner = ({ 
  size = 'medium', 
  message = 'Loading...', 
  type = 'default', 
  className = '' 
}) => {
  const sizes = {
    small: 'h-4 w-4',
    medium: 'h-6 w-6',
    large: 'h-8 w-8',
    xl: 'h-12 w-12'
  };

  const containerSizes = {
    small: 'space-y-2',
    medium: 'space-y-3',
    large: 'space-y-4',
    xl: 'space-y-6'
  };

  const textSizes = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg',
    xl: 'text-xl'
  };

  const getIcon = () => {
    switch (type) {
      case 'activity':
        return <Activity className={`${sizes[size]} text-blue-500`} />;
      case 'brain':
        return <Brain className={`${sizes[size]} text-purple-500`} />;
      default:
        return <Loader2 className={`${sizes[size]} text-blue-500`} />;
    }
  };

  const spinVariants = {
    animate: {
      rotate: 360,
      transition: {
        duration: 1,
        repeat: Infinity,
        ease: "linear"
      }
    }
  };

  const pulseVariants = {
    animate: {
      scale: [1, 1.1, 1],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <div className={`flex flex-col items-center justify-center ${containerSizes[size]} ${className}`}>
      <motion.div
        variants={type === 'activity' || type === 'brain' ? pulseVariants : spinVariants}
        animate="animate"
        className="flex items-center justify-center"
      >
        {getIcon()}
      </motion.div>
      
      {message && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className={`${textSizes[size]} text-gray-600 font-medium`}
        >
          {message}
        </motion.p>
      )}
    </div>
  );
};

// Inline spinner for buttons or small spaces
export const InlineSpinner = ({ size = 'small', className = '' }) => (
  <motion.div
    animate={{ rotate: 360 }}
    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
    className={`inline-block ${className}`}
  >
    <Loader2 className={`${
      size === 'small' ? 'h-4 w-4' : 
      size === 'medium' ? 'h-5 w-5' : 
      'h-6 w-6'
    } text-current`} />
  </motion.div>
);

// Skeleton loader for content
export const SkeletonLoader = ({ 
  lines = 3, 
  className = '', 
  height = 'h-4' 
}) => (
  <div className={`animate-pulse space-y-3 ${className}`}>
    {Array.from({ length: lines }).map((_, index) => (
      <div
        key={index}
        className={`bg-gray-200 rounded ${height} ${
          index === lines - 1 ? 'w-3/4' : 'w-full'
        }`}
      />
    ))}
  </div>
);

// Card skeleton loader
export const CardSkeleton = ({ className = '' }) => (
  <div className={`dashboard-card animate-pulse ${className}`}>
    <div className="space-y-4">
      <div className="h-6 bg-gray-200 rounded w-1/3" />
      <div className="space-y-2">
        <div className="h-4 bg-gray-200 rounded" />
        <div className="h-4 bg-gray-200 rounded w-5/6" />
        <div className="h-4 bg-gray-200 rounded w-4/6" />
      </div>
    </div>
  </div>
);

// Chart skeleton loader
export const ChartSkeleton = ({ className = '' }) => (
  <div className={`dashboard-card animate-pulse ${className}`}>
    <div className="space-y-4">
      <div className="h-6 bg-gray-200 rounded w-1/4" />
      <div className="h-64 bg-gray-200 rounded" />
      <div className="flex space-x-4">
        <div className="h-4 bg-gray-200 rounded w-20" />
        <div className="h-4 bg-gray-200 rounded w-20" />
        <div className="h-4 bg-gray-200 rounded w-20" />
      </div>
    </div>
  </div>
);

export default LoadingSpinner; 