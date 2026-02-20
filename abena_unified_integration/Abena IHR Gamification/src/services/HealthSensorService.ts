import { HealthData } from '../types';

// ✅ Correct - uses Abena SDK for auth & data handling:
// import AbenaSDK from '@abena/sdk';
// 
// class HealthSensorService {
//   constructor() {
//     this.abena = new AbenaSDK({
//       authServiceUrl: 'http://localhost:3001',
//       dataServiceUrl: 'http://localhost:8001',
//       privacyServiceUrl: 'http://localhost:8002',
//       blockchainServiceUrl: 'http://localhost:8003'
//     });
//   }
//   
//   async getSensorData(patientId, sensorType) {
//     // 1. Auto-handled auth & permissions
//     const sensorData = await this.abena.getSensorData(patientId, sensorType, 'health_monitoring');
//     
//     // 2. Auto-handled privacy & encryption
//     // 3. Auto-handled audit logging
//     
//     // 4. Focus on your business logic
//     return this.processSensorData(sensorData);
//   }
// }

// REMOVED: Custom sensor permission and data handling APIs
// All functionality should use Abena SDK instead

export default class HealthSensorService {
  // This class is deprecated - use Abena SDK instead
  // All sensor permission and data handling should go through Abena SDK
} 