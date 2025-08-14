import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { ClinicalContextModule } from './clinical-context/clinical-context.module';

@Module({
  imports: [ClinicalContextModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
