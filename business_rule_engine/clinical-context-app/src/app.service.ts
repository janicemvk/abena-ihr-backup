import { Injectable } from '@nestjs/common';
import AbenaSDK from './abena-sdk';

@Injectable()
export class AppService {
  private abena: AbenaSDK;

  constructor() {
    this.abena = new AbenaSDK({
      authServiceUrl: 'http://localhost:3001',
      dataServiceUrl: 'http://localhost:8001',
      privacyServiceUrl: 'http://localhost:8002',
      blockchainServiceUrl: 'http://localhost:8003'
    });
  }

  getHello(): string {
    return 'Hello World!';
  }

  async getPatientData(patientId: string, userId: string) {
    const patientData = await this.abena.getPatientData(patientId, 'app_module');
    return {
      patientId: patientData.id,
      patientName: patientData.name,
      medicalHistory: patientData.medicalHistory,
      context: 'App module patient data',
      timestamp: new Date().toISOString()
    };
  }
}
