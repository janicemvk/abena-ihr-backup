-- Migration: 001_initial_schema.sql
-- Description: Initial schema creation for Abena IHR Unified Data Service
-- Version: 1.0.0
-- Created: 2024
-- Applied: 2024

-- This migration creates the initial database schema for the Abena IHR system
-- It includes all core tables, indexes, triggers, and views

-- ======================================================
-- MIGRATION START
-- ======================================================

-- Log migration start
DO $$
BEGIN
    RAISE NOTICE 'Starting migration: 001_initial_schema.sql';
    RAISE NOTICE 'Creating initial database schema for Abena IHR Unified Data Service';
END $$;

-- ======================================================
-- APPLY MASTER SCHEMA
-- ======================================================

-- Include the master schema file
\i /schemas/master_schema.sql

-- ======================================================
-- MIGRATION COMPLETE
-- ======================================================

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 001_initial_schema.sql completed successfully!';
    RAISE NOTICE 'Database schema created with all tables, indexes, and views';
END $$; 