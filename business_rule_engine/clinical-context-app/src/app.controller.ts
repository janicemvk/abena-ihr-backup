import { Controller, Get, Query } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getHello(): string {
    return this.appService.getHello();
  }

  @Get('patient')
  async getPatientData(
    @Query('patientId') patientId: string,
    @Query('userId') userId: string
  ) {
    return await this.appService.getPatientData(patientId, userId);
  }
}
