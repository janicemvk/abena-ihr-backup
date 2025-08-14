import BackgroundModuleOrchestrator from './orchestrator/BackgroundModuleOrchestrator.js';
import BaseBackgroundModule from './core/BaseBackgroundModule.js';

// Import all 12 individual modules
import MetabolomeBackgroundModule from './modules/MetabolomeBackgroundModule.js';
import MicrobiomeBackgroundModule from './modules/MicrobiomeBackgroundModule.js';
import InflammatomeBackgroundModule from './modules/InflammatomeBackgroundModule.js';
import ImmunomeBackgroundModule from './modules/ImmunomeBackgroundModule.js';
import ChronobiomeBackgroundModule from './modules/ChronobiomeBackgroundModule.js';
import NutriomeBackgroundModule from './modules/NutriomeBackgroundModule.js';
import ToxicomeBackgroundModule from './modules/ToxicomeBackgroundModule.js';
import PharmacomedBackgroundModule from './modules/PharmacomedBackgroundModule.js';
import StressResponseBackgroundModule from './modules/StressResponseBackgroundModule.js';
import CardiovascularBackgroundModule from './modules/CardiovascularBackgroundModule.js';
import NeurologicalBackgroundModule from './modules/NeurologicalBackgroundModule.js';
import HormonalBackgroundModule from './modules/HormonalBackgroundModule.js';

/**
 * 12 CORE BACKGROUND MODULES SYSTEM
 * Complete implementation with Abena SDK integration
 * 
 * @description
 * This system provides comprehensive real-time monitoring of 12 biological systems
 * with eCBome correlation and advanced pattern recognition capabilities.
 * 
 * @features
 * - 12 specialized background modules for different biological systems
 * - Real-time monitoring with configurable intervals
 * - eCBome correlation and analysis
 * - Cross-module pattern recognition
 * - Predictive health indicators
 * - Automated alert generation
 * - Comprehensive health scoring
 * - Intervention opportunity identification
 * 
 * @usage
 * ```javascript
 * import { BackgroundModuleOrchestrator } from '@abena/12-core-background-modules';
 * 
 * const orchestrator = new BackgroundModuleOrchestrator();
 * await orchestrator.startAllBackgroundModules(patientId, userId);
 * ```
 */

// Create and export a default orchestrator instance
const defaultOrchestrator = new BackgroundModuleOrchestrator();

/**
 * Quick start function for immediate use
 */
export async function startAllModules(patientId, userId) {
  return await defaultOrchestrator.startAllBackgroundModules(patientId, userId);
}

/**
 * Quick stop function
 */
export async function stopAllModules() {
  return await defaultOrchestrator.stopAllBackgroundModules();
}

/**
 * Get comprehensive analysis from all modules
 */
export async function getComprehensiveAnalysis() {
  return await defaultOrchestrator.getComprehensiveAnalysis();
}

/**
 * Get orchestrator status
 */
export function getOrchestratorStatus() {
  return defaultOrchestrator.getOrchestratorStatus();
}

// Export all classes for advanced usage
export {
  // Main orchestrator
  BackgroundModuleOrchestrator,
  
  // Base class
  BaseBackgroundModule,
  
  // All 12 individual modules
  MetabolomeBackgroundModule,
  MicrobiomeBackgroundModule,
  InflammatomeBackgroundModule,
  ImmunomeBackgroundModule,
  ChronobiomeBackgroundModule,
  NutriomeBackgroundModule,
  ToxicomeBackgroundModule,
  PharmacomedBackgroundModule,
  StressResponseBackgroundModule,
  CardiovascularBackgroundModule,
  NeurologicalBackgroundModule,
  HormonalBackgroundModule,
  
  // Default orchestrator instance
  defaultOrchestrator
};

// Export as default for ES6 import
export default BackgroundModuleOrchestrator;

// Module information
export const moduleInfo = {
  name: '12 Core Background Modules',
  version: '2.0.0',
  description: 'Comprehensive biological system monitoring with eCBome correlation',
  moduleCount: 12,
  modules: [
    'metabolome',
    'microbiome', 
    'inflammatome',
    'immunome',
    'chronobiome',
    'nutriome',
    'toxicome',
    'pharmacome',
    'stressResponse',
    'cardiovascular',
    'neurological',
    'hormonal'
  ],
  features: [
    'Real-time monitoring',
    'eCBome correlation',
    'Cross-module pattern recognition',
    'Predictive health indicators',
    'Automated alerts',
    'Comprehensive health scoring',
    'Intervention opportunities'
  ],
  compatibleWith: ['Abena SDK v3.0+'],
  author: 'Abena Health Systems',
  license: 'MIT'
};

// Console startup message
console.log(`
🧬 12 Core Background Modules System v2.0.0 Loaded
📊 ${moduleInfo.moduleCount} specialized modules ready for deployment
🔬 Features: ${moduleInfo.features.join(', ')}
🚀 Use startAllModules(patientId, userId) to begin monitoring
`); 