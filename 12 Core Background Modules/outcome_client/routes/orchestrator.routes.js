import express from "express";
import { runAllModules } from "../controllers/orchestrator.controller.js";

const router = express.Router();

// POST /api/analyze
router.post("/analyze", runAllModules);

export default router;
