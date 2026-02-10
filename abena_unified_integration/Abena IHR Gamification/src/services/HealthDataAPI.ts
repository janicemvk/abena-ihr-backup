import { HealthData, User, Quest, Badge } from '../types';

// ✅ Correct - uses Abena SDK for auth & data handling:
// import AbenaSDK from '@abena/sdk';
// 
// class HealthDataService {
//   constructor() {
//     this.abena = new AbenaSDK({
//       authServiceUrl: 'http://localhost:3001',
//       dataServiceUrl: 'http://localhost:8001',
//       privacyServiceUrl: 'http://localhost:8002',
//       blockchainServiceUrl: 'http://localhost:8003'
//     });
//   }
//   
//   async getHealthData(userId, patientId) {
//     // 1. Auto-handled auth & permissions
//     const healthData = await this.abena.getPatientData(patientId, 'health_monitoring');
//     
//     // 2. Auto-handled privacy & encryption
//     // 3. Auto-handled audit logging
//     
//     // 4. Focus on your business logic
//     return this.processHealthData(healthData);
//   }
// }

interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// REMOVED: Custom authentication, authorization, and data handling APIs
// All functionality should use Abena SDK instead

export default class HealthDataAPI {
  // This class is deprecated - use Abena SDK instead
  // All authentication, authorization, and data handling should go through Abena SDK
} 