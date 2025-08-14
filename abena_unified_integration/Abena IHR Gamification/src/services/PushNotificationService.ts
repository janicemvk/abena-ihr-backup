import { User } from '../types';

// ✅ Correct - uses Abena SDK for auth & data handling:
// import AbenaSDK from '@abena/sdk';
// 
// class PushNotificationService {
//   constructor() {
//     this.abena = new AbenaSDK({
//       authServiceUrl: 'http://localhost:3001',
//       dataServiceUrl: 'http://localhost:8001',
//       privacyServiceUrl: 'http://localhost:8002',
//       blockchainServiceUrl: 'http://localhost:8003'
//     });
//   }
//   
//   async sendPushNotification(userId, patientId, notification) {
//     // 1. Auto-handled auth & permissions
//     await this.abena.sendPushNotification(patientId, notification, 'health_alerts');
//     
//     // 2. Auto-handled privacy & encryption
//     // 3. Auto-handled audit logging
//     
//     // 4. Focus on your business logic
//     return this.processPushNotification(notification);
//   }
// }

// REMOVED: Custom push notification and permission APIs
// All functionality should use Abena SDK instead

export default class PushNotificationService {
  // This class is deprecated - use Abena SDK instead
  // All push notification and permission handling should go through Abena SDK
} 