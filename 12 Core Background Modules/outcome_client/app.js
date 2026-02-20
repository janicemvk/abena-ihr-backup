import express from "express";
import cors from "cors";
import orchestratorRoutes from "./routes/orchestrator.routes.js";

const app = express();

app.use(cors());
app.use(express.json());
app.use("/api", orchestratorRoutes);

export default app;
