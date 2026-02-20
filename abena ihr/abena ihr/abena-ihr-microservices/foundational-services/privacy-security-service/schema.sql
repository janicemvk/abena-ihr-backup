-- Abena IHR Privacy & Security Service Database Schema
-- PostgreSQL schema for encryption, access control, and audit functionality

-- Create database if not exists
-- CREATE DATABASE abena_ihr_security;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Encryption Keys Management
CREATE TABLE encryption_keys (
    id SERIAL PRIMARY KEY,
    key_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    encrypted_key TEXT NOT NULL,
    algorithm VARCHAR(50) NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    purpose VARCHAR(100) NOT NULL,
    patient_id VARCHAR(100),
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    rotated_at TIMESTAMP WITH TIME ZONE,
    rotated_by VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);

-- Security Audit Log
CREATE TABLE security_audit_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    additional_data JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    risk_score DECIMAL(3,2),
    success BOOLEAN DEFAULT TRUE
);

-- Access Control Tables
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    resource_type VARCHAR(100),
    action VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by VARCHAR(100),
    UNIQUE(role_id, permission_id)
);

CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, role_id)
);

-- Patient-Provider Relationships
CREATE TABLE patient_provider_relationships (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(100) NOT NULL,
    provider_id VARCHAR(100) NOT NULL,
    relationship_type VARCHAR(50) NOT NULL, -- 'primary', 'specialist', 'consultant'
    established_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(100),
    UNIQUE(patient_id, provider_id, relationship_type)
);

-- Emergency Access Grants
CREATE TABLE emergency_access_grants (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(100) NOT NULL,
    provider_id VARCHAR(100) NOT NULL,
    reason TEXT NOT NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    granted_by VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    audit_reviewed BOOLEAN DEFAULT FALSE,
    review_notes TEXT
);

-- Access Audit Log
CREATE TABLE access_audit_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    granted BOOLEAN NOT NULL,
    risk_score DECIMAL(3,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    additional_context JSONB
);

-- Anonymization and Pseudonymization
CREATE TABLE pseudonym_mappings (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(100) UNIQUE NOT NULL,
    pseudonym VARCHAR(100) UNIQUE NOT NULL,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE anonymization_jobs (
    id SERIAL PRIMARY KEY,
    job_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    dataset_id VARCHAR(100) NOT NULL,
    anonymization_type VARCHAR(50) NOT NULL, -- 'k-anonymity', 'differential-privacy'
    parameters JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    result_location TEXT,
    error_message TEXT
);

-- Data Retention Policies
CREATE TABLE retention_policies (
    id SERIAL PRIMARY KEY,
    data_type VARCHAR(100) NOT NULL,
    retention_period_days INTEGER NOT NULL,
    retention_type VARCHAR(50) NOT NULL, -- 'legal', 'business', 'regulatory'
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data Classification
CREATE TABLE data_classifications (
    id SERIAL PRIMARY KEY,
    data_type VARCHAR(100) NOT NULL,
    sensitivity_level VARCHAR(50) NOT NULL, -- 'public', 'internal', 'confidential', 'restricted'
    classification_reason TEXT,
    classified_by VARCHAR(100) NOT NULL,
    classified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    review_date TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Consent Management
CREATE TABLE consent_records (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(100) NOT NULL,
    consent_type VARCHAR(100) NOT NULL, -- 'data_processing', 'research', 'sharing'
    consent_status VARCHAR(50) NOT NULL, -- 'granted', 'denied', 'withdrawn', 'expired'
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    granted_by VARCHAR(100),
    scope JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    previous_version_id INTEGER REFERENCES consent_records(id),
    audit_trail JSONB
);

-- Key Performance Indicators
CREATE TABLE security_kpis (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    metric_unit VARCHAR(50),
    measurement_date DATE NOT NULL,
    measurement_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    context JSONB
);

-- Create indexes for performance
CREATE INDEX idx_encryption_keys_key_id ON encryption_keys(key_id);
CREATE INDEX idx_encryption_keys_patient_id ON encryption_keys(patient_id);
CREATE INDEX idx_encryption_keys_expires_at ON encryption_keys(expires_at);

CREATE INDEX idx_security_audit_log_user_id ON security_audit_log(user_id);
CREATE INDEX idx_security_audit_log_timestamp ON security_audit_log(timestamp);
CREATE INDEX idx_security_audit_log_action ON security_audit_log(action);

CREATE INDEX idx_access_audit_log_user_id ON access_audit_log(user_id);
CREATE INDEX idx_access_audit_log_timestamp ON access_audit_log(timestamp);
CREATE INDEX idx_access_audit_log_resource_type ON access_audit_log(resource_type);

CREATE INDEX idx_patient_provider_patient_id ON patient_provider_relationships(patient_id);
CREATE INDEX idx_patient_provider_provider_id ON patient_provider_relationships(provider_id);

CREATE INDEX idx_emergency_access_patient_id ON emergency_access_grants(patient_id);
CREATE INDEX idx_emergency_access_expires_at ON emergency_access_grants(expires_at);

CREATE INDEX idx_pseudonym_mappings_patient_id ON pseudonym_mappings(patient_id);
CREATE INDEX idx_pseudonym_mappings_pseudonym ON pseudonym_mappings(pseudonym);

CREATE INDEX idx_consent_records_patient_id ON consent_records(patient_id);
CREATE INDEX idx_consent_records_expires_at ON consent_records(expires_at);

-- Create views for common queries
CREATE VIEW active_encryption_keys AS
SELECT * FROM encryption_keys 
WHERE is_active = TRUE AND (expires_at IS NULL OR expires_at > NOW());

CREATE VIEW recent_security_events AS
SELECT * FROM security_audit_log 
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

CREATE VIEW user_permissions_summary AS
SELECT 
    ur.user_id,
    r.name as role_name,
    p.name as permission_name,
    p.resource_type,
    p.action
FROM user_roles ur
JOIN roles r ON ur.role_id = r.id
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
WHERE ur.is_active = TRUE AND r.is_active = TRUE AND p.is_active = TRUE;

-- Insert default roles and permissions
INSERT INTO roles (name, description) VALUES
('admin', 'System administrator with full access'),
('security_officer', 'Security officer with audit and key management access'),
('provider', 'Healthcare provider with patient data access'),
('researcher', 'Researcher with anonymized data access'),
('patient', 'Patient with own data access')
ON CONFLICT (name) DO NOTHING;

INSERT INTO permissions (name, description, resource_type, action) VALUES
('encrypt.data', 'Encrypt sensitive data', 'data', 'encrypt'),
('decrypt.data', 'Decrypt sensitive data', 'data', 'decrypt'),
('anonymize.dataset', 'Anonymize datasets', 'dataset', 'anonymize'),
('access.audit_log', 'Access audit logs', 'audit_log', 'read'),
('manage.keys', 'Manage encryption keys', 'encryption_key', 'manage'),
('access.patient_data', 'Access patient data', 'patient_data', 'read'),
('modify.patient_data', 'Modify patient data', 'patient_data', 'write'),
('delete.patient_data', 'Delete patient data', 'patient_data', 'delete'),
('export.data', 'Export data', 'data', 'export'),
('share.data', 'Share data', 'data', 'share')
ON CONFLICT (name) DO NOTHING;

-- Grant permissions to roles
INSERT INTO role_permissions (role_id, permission_id, granted_by) 
SELECT r.id, p.id, 'system' 
FROM roles r, permissions p 
WHERE r.name = 'admin' 
ON CONFLICT (role_id, permission_id) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id, granted_by)
SELECT r.id, p.id, 'system'
FROM roles r, permissions p
WHERE r.name = 'security_officer' AND p.name IN (
    'encrypt.data', 'decrypt.data', 'anonymize.dataset', 'access.audit_log', 'manage.keys'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id, granted_by)
SELECT r.id, p.id, 'system'
FROM roles r, permissions p
WHERE r.name = 'provider' AND p.name IN (
    'access.patient_data', 'modify.patient_data'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id, granted_by)
SELECT r.id, p.id, 'system'
FROM roles r, permissions p
WHERE r.name = 'researcher' AND p.name IN (
    'anonymize.dataset'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id, granted_by)
SELECT r.id, p.id, 'system'
FROM roles r, permissions p
WHERE r.name = 'patient' AND p.name IN (
    'access.patient_data'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Insert default retention policies
INSERT INTO retention_policies (data_type, retention_period_days, retention_type, description) VALUES
('patient_medical_records', 2555, 'legal', 'Medical records retention for 7 years'),
('audit_logs', 2555, 'regulatory', 'Security audit logs retention for 7 years'),
('encryption_keys', 365, 'security', 'Encryption key retention for 1 year after rotation'),
('consent_records', 2555, 'legal', 'Consent records retention for 7 years'),
('pseudonym_mappings', 3650, 'business', 'Pseudonym mappings retention for 10 years')
ON CONFLICT (data_type) DO NOTHING;

-- Insert default data classifications
INSERT INTO data_classifications (data_type, sensitivity_level, classification_reason, classified_by) VALUES
('patient_identifiers', 'restricted', 'Contains personally identifiable information', 'system'),
('medical_diagnoses', 'confidential', 'Contains sensitive health information', 'system'),
('lab_results', 'confidential', 'Contains sensitive health information', 'system'),
('medication_history', 'confidential', 'Contains sensitive health information', 'system'),
('audit_logs', 'internal', 'Contains system access information', 'system'),
('anonymized_data', 'internal', 'De-identified data for research', 'system')
ON CONFLICT (data_type) DO NOTHING;

-- Create functions for automatic cleanup
CREATE OR REPLACE FUNCTION cleanup_expired_encryption_keys()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM encryption_keys 
    WHERE expires_at < NOW() - INTERVAL '30 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM security_audit_log 
    WHERE timestamp < NOW() - INTERVAL '7 years';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create a function to calculate security KPIs
CREATE OR REPLACE FUNCTION calculate_security_kpis()
RETURNS VOID AS $$
BEGIN
    -- Encryption operations per day
    INSERT INTO security_kpis (metric_name, metric_value, metric_unit, measurement_date)
    SELECT 
        'encryption_operations_per_day',
        COUNT(*)::DECIMAL,
        'operations',
        DATE(NOW())
    FROM security_audit_log 
    WHERE action = 'ENCRYPTION' AND timestamp >= DATE(NOW());
    
    -- Failed access attempts per day
    INSERT INTO security_kpis (metric_name, metric_value, metric_unit, measurement_date)
    SELECT 
        'failed_access_attempts_per_day',
        COUNT(*)::DECIMAL,
        'attempts',
        DATE(NOW())
    FROM access_audit_log 
    WHERE granted = FALSE AND timestamp >= DATE(NOW());
    
    -- Average risk score per day
    INSERT INTO security_kpis (metric_name, metric_value, metric_unit, measurement_date)
    SELECT 
        'average_risk_score_per_day',
        AVG(risk_score),
        'score',
        DATE(NOW())
    FROM access_audit_log 
    WHERE timestamp >= DATE(NOW()) AND risk_score IS NOT NULL;
END;
$$ LANGUAGE plpgsql; 