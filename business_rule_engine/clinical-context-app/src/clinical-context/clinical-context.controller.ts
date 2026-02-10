import { Controller, Get, Param, Query } from '@nestjs/common';
import { ClinicalContextService } from './clinical-context.service';

@Controller('clinical-context')
export class ClinicalContextController {
  constructor(private readonly clinicalContextService: ClinicalContextService) {}

  @Get('patient/:patientId')
  async getPatientContext(
    @Param('patientId') patientId: string,
    @Query('userId') userId: string
  ) {
    return await this.clinicalContextService.getPatientContext(patientId, userId);
  }
}
