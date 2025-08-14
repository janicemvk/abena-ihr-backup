#!/usr/bin/env node

import MLEngineAPI from './src/api/MLEngineAPI.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

console.log('🧬 eCdome ML Engine - Starting Server...\n');

// Create and start the API server
const api = new MLEngineAPI();
await api.start();

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('\n📴 Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\n📴 Received SIGINT, shutting down gracefully...');
  process.exit(0);
});

console.log('🎯 Server is running! Use Ctrl+C to stop.'); 