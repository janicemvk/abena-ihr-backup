import express from 'express';
import { createOutcome } from '../controllers/outcome.controller.js';

const router = express.Router();

router.post('/', createOutcome);

export default router;
