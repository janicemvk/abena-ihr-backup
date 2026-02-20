import { Test, TestingModule } from '@nestjs/testing';
import { ClinicalContextService } from './clinical-context.service';

describe('ClinicalContextService', () => {
  let service: ClinicalContextService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [ClinicalContextService],
    }).compile();

    service = module.get<ClinicalContextService>(ClinicalContextService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });
});
