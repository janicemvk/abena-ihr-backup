import { Test, TestingModule } from '@nestjs/testing';
import { ClinicalContextController } from './clinical-context.controller';

describe('ClinicalContextController', () => {
  let controller: ClinicalContextController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [ClinicalContextController],
    }).compile();

    controller = module.get<ClinicalContextController>(ClinicalContextController);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });
});
