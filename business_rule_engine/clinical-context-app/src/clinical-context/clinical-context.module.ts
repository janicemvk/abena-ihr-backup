import { Module } from '@nestjs/common';
import { ClinicalContextController } from './clinical-context.controller';
import { ClinicalContextService } from './clinical-context.service';

@Module({
  controllers: [ClinicalContextController],
  providers: [ClinicalContextService]
})
export class ClinicalContextModule {}
