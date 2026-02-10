// orchestrator.controller.js
import BackgroundModuleOrchestrator from '../../src/orchestrator/BackgroundModuleOrchestrator.js';
import { abenaLogger } from "../../src/utils/logger.js";


export const runAllModules = async (req, res) => {
  try {
    const { patientId, userId, patientData } = req.body;

    // Pass patientData to the orchestrator
    const orchestrator = new BackgroundModuleOrchestrator(patientData, abenaLogger);

    const result = await orchestrator.startAllBackgroundModules(patientId, userId);
    res.json(result);
  } catch (error) {
    console.error('Error running orchestrator:', error);
    res.status(500).json({ error: error.message });
  }
};

export const analyzeModules = async (req, res) => {
  try {
    const result = await orchestrator.getComprehensiveAnalysis();
    res.json(result);
  } catch (error) {
    console.error('Error analyzing modules:', error);
    res.status(500).json({ error: error.message });
  }
};