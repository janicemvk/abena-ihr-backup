-- Quantum Healthcare Database Schema
-- Tables for quantum analysis, drug interactions, and herbal compatibility

-- Create extension for UUID support if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Quantum Analysis Results Table
CREATE TABLE IF NOT EXISTS quantum_analysis_results (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(100) NOT NULL,
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quantum_health_score FLOAT NOT NULL,
    system_balance FLOAT NOT NULL,
    analysis_data JSONB,
    drug_interactions JSONB,
    herbal_recommendations JSONB,
    biomarker_analysis JSONB,
    recommendations TEXT[],
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster patient queries
CREATE INDEX IF NOT EXISTS idx_quantum_results_patient_id ON quantum_analysis_results(patient_id);
CREATE INDEX IF NOT EXISTS idx_quantum_results_timestamp ON quantum_analysis_results(analysis_timestamp DESC);

-- Quantum Analysis History Table
CREATE TABLE IF NOT EXISTS quantum_analysis_history (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(100) NOT NULL,
    analysis_id INTEGER REFERENCES quantum_analysis_results(id),
    analysis_type VARCHAR(50) DEFAULT 'full_analysis',
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    computation_time_ms INTEGER,
    input_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for history queries
CREATE INDEX IF NOT EXISTS idx_quantum_history_patient_id ON quantum_analysis_history(patient_id);
CREATE INDEX IF NOT EXISTS idx_quantum_history_analysis_id ON quantum_analysis_history(analysis_id);

-- Drug Interactions Cache Table
CREATE TABLE IF NOT EXISTS quantum_drug_interactions (
    id SERIAL PRIMARY KEY,
    medication1 VARCHAR(200) NOT NULL,
    medication2 VARCHAR(200) NOT NULL,
    interaction_score FLOAT NOT NULL,
    severity VARCHAR(50) NOT NULL,
    recommendation TEXT,
    quantum_model_version VARCHAR(20) DEFAULT '1.0',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(medication1, medication2)
);

-- Index for drug interaction lookups
CREATE INDEX IF NOT EXISTS idx_drug_interactions_meds ON quantum_drug_interactions(medication1, medication2);

-- Herbal Compatibility Cache Table
CREATE TABLE IF NOT EXISTS quantum_herbal_compatibility (
    id SERIAL PRIMARY KEY,
    herb_name VARCHAR(200) NOT NULL,
    medication VARCHAR(200),
    compatibility_score FLOAT NOT NULL,
    benefits TEXT[],
    warnings TEXT[],
    contraindications TEXT[],
    quantum_model_version VARCHAR(20) DEFAULT '1.0',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(herb_name, medication)
);

-- Index for herbal compatibility lookups
CREATE INDEX IF NOT EXISTS idx_herbal_compat_herb ON quantum_herbal_compatibility(herb_name);
CREATE INDEX IF NOT EXISTS idx_herbal_compat_medication ON quantum_herbal_compatibility(medication);

-- Quantum Settings Table
CREATE TABLE IF NOT EXISTS quantum_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value JSONB NOT NULL,
    setting_type VARCHAR(50) DEFAULT 'system',
    description TEXT,
    updated_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for settings lookups
CREATE INDEX IF NOT EXISTS idx_quantum_settings_key ON quantum_settings(setting_key);
CREATE INDEX IF NOT EXISTS idx_quantum_settings_type ON quantum_settings(setting_type);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic updated_at updates
DROP TRIGGER IF EXISTS update_quantum_results_updated_at ON quantum_analysis_results;
CREATE TRIGGER update_quantum_results_updated_at
    BEFORE UPDATE ON quantum_analysis_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_quantum_settings_updated_at ON quantum_settings;
CREATE TRIGGER update_quantum_settings_updated_at
    BEFORE UPDATE ON quantum_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default quantum settings
INSERT INTO quantum_settings (setting_key, setting_value, setting_type, description)
VALUES 
    ('quantum_enabled', '{"enabled": true}', 'system', 'Enable quantum computing features'),
    ('analysis_timeout', '{"timeout_ms": 30000}', 'system', 'Maximum time for quantum analysis'),
    ('cache_enabled', '{"enabled": true}', 'system', 'Enable caching for drug interactions and herbal compatibility'),
    ('model_version', '{"version": "1.0"}', 'system', 'Current quantum model version')
ON CONFLICT (setting_key) DO NOTHING;

-- Grant permissions (adjust as needed for your user)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO abena_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO abena_user;

-- Display created tables
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
  AND table_name LIKE 'quantum_%'
ORDER BY table_name;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Quantum Healthcare database schema created successfully!';
    RAISE NOTICE 'Tables created: quantum_analysis_results, quantum_analysis_history, quantum_drug_interactions, quantum_herbal_compatibility, quantum_settings';
END $$;

