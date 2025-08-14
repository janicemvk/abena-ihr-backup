import { User } from '../types';

// ✅ Correct - uses Abena SDK for auth & data handling:
// import AbenaSDK from '@abena/sdk';
// 
// class NotificationService {
//   constructor() {
//     this.abena = new AbenaSDK({
//       authServiceUrl: 'http://localhost:3001',
//       dataServiceUrl: 'http://localhost:8001',
//       privacyServiceUrl: 'http://localhost:8002',
//       blockchainServiceUrl: 'http://localhost:8003'
//     });
//   }
//   
//   async sendNotification(userId, patientId, notification) {
//     // 1. Auto-handled auth & permissions
//     await this.abena.sendNotification(patientId, notification, 'health_reminders');
//     
//     // 2. Auto-handled privacy & encryption
//     // 3. Auto-handled audit logging
//     
//     // 4. Focus on your business logic
//     return this.processNotification(notification);
//   }
// }

// REMOVED: Custom notification and permission APIs
// All functionality should use Abena SDK instead

export default class NotificationService {
  // This class is deprecated - use Abena SDK instead
  // All notification and permission handling should go through Abena SDK
} 