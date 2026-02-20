-- Abena IHR Unified Data Service - Master Database Schema
-- ======================================================
-- 
-- This schema defines the master database structure for the Abena IHR system,
-- serving as the single source of truth for all healthcare data across
-- multiple microservices and applications.
--
-- Schema Version: 1.0.0
-- Created: 2024
-- Last Updated: 2024

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ======================================================
-- CORE ENTITY TABLES
-- ======================================================

-- Patients table - Core patient information
CREATE TABLE patients (
    patient_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mrn VARCHAR(50) UNIQUE NOT NULL, -- Medical Record Number
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other', 'unknown')),
    ethnicity VARCHAR(100),
    race VARCHAR(100),
    marital_status VARCHAR(20),
    primary_language VARCHAR(50),
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relationship VARCHAR(100),
    insurance_provider VARCHAR(100),
    insurance_policy_number VARCHAR(100),
    insurance_group_number VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- Providers table - Healthcare providers
CREATE TABLE providers (
    provider_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    npi VARCHAR(20) UNIQUE, -- National Provider Identifier
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    title VARCHAR(100),
    specialty VARCHAR(200),
    license_number VARCHAR(100),
    license_state VARCHAR(2),
    email VARCHAR(255),
    phone VARCHAR(20),
    fax VARCHAR(20),
    organization_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- Organizations table - Healthcare organizations
CREATE TABLE organizations (
    organization_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    type VARCHAR(100), -- hospital, clinic, laboratory, pharmacy, etc.
    tax_id VARCHAR(20),
    npi VARCHAR(20),
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    country VARCHAR(100) DEFAULT 'USA',
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- ======================================================
-- CLINICAL DATA TABLES
-- ======================================================

-- Encounters table - Patient encounters/visits
CREATE TABLE encounters (
    encounter_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(patient_id),
    provider_id UUID REFERENCES providers(provider_id),
    organization_id UUID REFERENCES organizations(organization_id),
    encounter_type VARCHAR(100), -- inpatient, outpatient, emergency, etc.
    encounter_class VARCHAR(100), -- ambulatory, emergency, inpatient, etc.
    status VARCHAR(50) DEFAULT 'active', -- active, finished, cancelled, etc.
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    reason_code VARCHAR(100),
    reason_text TEXT,
    priority VARCHAR(20), -- routine, urgent, emergent, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- Diagnoses table - Patient diagnoses
CREATE TABLE diagnoses (
    diagnosis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(patient_id),
    encounter_id UUID REFERENCES encounters(encounter_id),
    diagnosis_code VARCHAR(20), -- ICD-10 code
    diagnosis_text TEXT NOT NULL,
    diagnosis_type VARCHAR(50), -- primary, secondary, etc.
    status VARCHAR(50) DEFAULT 'active', -- active, resolved, chronic, etc.
    onset_date DATE,
    resolved_date DATE,
    severity VARCHAR(20), -- mild, moderate, severe
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- Medications table - Patient medications
CREATE TABLE medications (
    medication_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(patient_id),
    encounter_id UUID REFERENCES encounters(encounter_id),
    medication_name VARCHAR(200) NOT NULL,
    generic_name VARCHAR(200),
    ndc_code VARCHAR(20), -- National Drug Code
    rxnorm_code VARCHAR(20),
    dosage_form VARCHAR(100), -- tablet, capsule, liquid, etc.
    strength VARCHAR(100), -- 10mg, 500mg, etc.
    route VARCHAR(100), -- oral, intravenous, topical, etc.
    frequency VARCHAR(100), -- daily, twice daily, etc.
    quantity DECIMAL(10,2),
    quantity_unit VARCHAR(50),
    prescribed_date DATE,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active', -- active, discontinued, completed, etc.
    prescribed_by UUID REFERENCES providers(provider_id),
    pharmacy VARCHAR(200),
    instructions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- Vital signs table - Patient vital signs
CREATE TABLE vital_signs (
    vital_sign_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(patient_id),
    encounter_id UUID REFERENCES encounters(encounter_id),
    vital_sign_type VARCHAR(50) NOT NULL, -- blood_pressure, heart_rate, temperature, etc.
    value DECIMAL(10,2),
    unit VARCHAR(20),
    systolic DECIMAL(10,2), -- for blood pressure
    diastolic DECIMAL(10,2), -- for blood pressure
    measurement_date TIMESTAMP WITH TIME ZONE NOT NULL,
    measured_by UUID REFERENCES providers(provider_id),
    method VARCHAR(100), -- automated, manual, etc.
    position VARCHAR(50), -- sitting, standing, lying, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- Lab results table - Laboratory test results
CREATE TABLE lab_results (
    lab_result_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(patient_id),
    encounter_id UUID REFERENCES encounters(encounter_id),
    test_name VARCHAR(200) NOT NULL,
    test_code VARCHAR(50), -- LOINC code
    result_value VARCHAR(500),
    result_numeric DECIMAL(10,4),
    unit VARCHAR(50),
    reference_range_low DECIMAL(10,4),
    reference_range_high DECIMAL(10,4),
    reference_range_text VARCHAR(200),
    abnormal_flag VARCHAR(10), -- high, low, normal, critical
    result_status VARCHAR(50) DEFAULT 'final', -- preliminary, final, corrected, etc.
    specimen_type VARCHAR(100),
    collection_date TIMESTAMP WITH TIME ZONE,
    result_date TIMESTAMP WITH TIME ZONE NOT NULL,
    ordering_provider UUID REFERENCES providers(provider_id),
    performing_lab UUID REFERENCES organizations(organization_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- Procedures table - Medical procedures
CREATE TABLE procedures (
    procedure_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(patient_id),
    encounter_id UUID REFERENCES encounters(encounter_id),
    procedure_code VARCHAR(20), -- CPT code
    procedure_name VARCHAR(200) NOT NULL,
    procedure_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled
    scheduled_date TIMESTAMP WITH TIME ZONE,
    performed_date TIMESTAMP WITH TIME ZONE,
    performing_provider UUID REFERENCES providers(provider_id),
    facility UUID REFERENCES organizations(organization_id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- Allergies table - Patient allergies
CREATE TABLE allergies (
    allergy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(patient_id),
    allergen_name VARCHAR(200) NOT NULL,
    allergen_type VARCHAR(100), -- drug, food, environmental, etc.
    reaction VARCHAR(200),
    severity VARCHAR(20), -- mild, moderate, severe
    onset_date DATE,
    status VARCHAR(50) DEFAULT 'active', -- active, resolved, unknown
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- Immunizations table - Patient immunizations
CREATE TABLE immunizations (
    immunization_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(patient_id),
    encounter_id UUID REFERENCES encounters(encounter_id),
    vaccine_name VARCHAR(200) NOT NULL,
    vaccine_code VARCHAR(20), -- CVX code
    administration_date DATE NOT NULL,
    expiration_date DATE,
    lot_number VARCHAR(100),
    manufacturer VARCHAR(200),
    administered_by UUID REFERENCES providers(provider_id),
    site VARCHAR(100), -- left arm, right arm, etc.
    route VARCHAR(100), -- intramuscular, subcutaneous, etc.
    dose_quantity DECIMAL(10,2),
    dose_unit VARCHAR(50),
    status VARCHAR(50) DEFAULT 'completed', -- completed, cancelled, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- ======================================================
-- DOCUMENTATION TABLES
-- ======================================================

-- Clinical notes table - Clinical documentation
CREATE TABLE clinical_notes (
    note_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(patient_id),
    encounter_id UUID REFERENCES encounters(encounter_id),
    note_type VARCHAR(100), -- progress_note, discharge_summary, consultation, etc.
    note_title VARCHAR(200),
    note_content TEXT NOT NULL,
    author_id UUID REFERENCES providers(provider_id),
    authored_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) DEFAULT 'draft', -- draft, final, amended, etc.
    confidentiality_level VARCHAR(50) DEFAULT 'normal', -- normal, restricted, confidential
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- Documents table - General documents
CREATE TABLE documents (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(patient_id),
    encounter_id UUID REFERENCES encounters(encounter_id),
    document_type VARCHAR(100), -- consent_form, advance_directive, etc.
    document_title VARCHAR(200) NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    mime_type VARCHAR(100),
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES providers(provider_id),
    status VARCHAR(50) DEFAULT 'active', -- active, archived, deleted
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB
);

-- ======================================================
-- RELATIONSHIP TABLES
-- ======================================================

-- Patient-provider relationships
CREATE TABLE patient_provider_relationships (
    relationship_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(patient_id),
    provider_id UUID NOT NULL REFERENCES providers(provider_id),
    relationship_type VARCHAR(100), -- primary_care, specialist, consultant, etc.
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active', -- active, inactive, terminated
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB,
    UNIQUE(patient_id, provider_id, relationship_type)
);

-- Provider-organization relationships
CREATE TABLE provider_organization_relationships (
    relationship_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID NOT NULL REFERENCES providers(provider_id),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    relationship_type VARCHAR(100), -- employee, contractor, affiliate, etc.
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active', -- active, inactive, terminated
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service',
    metadata JSONB,
    UNIQUE(provider_id, organization_id, relationship_type)
);

-- ======================================================
-- AUDIT AND TRACKING TABLES
-- ======================================================

-- Data audit log
CREATE TABLE data_audit_log (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    operation VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by UUID REFERENCES providers(provider_id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    data_source VARCHAR(100) DEFAULT 'unified_service'
);

-- Data quality metrics
CREATE TABLE data_quality_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4),
    metric_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'unified_service'
);

-- ======================================================
-- INDEXES FOR PERFORMANCE
-- ======================================================

-- Patient indexes
CREATE INDEX idx_patients_mrn ON patients(mrn);
CREATE INDEX idx_patients_name ON patients(last_name, first_name);
CREATE INDEX idx_patients_dob ON patients(date_of_birth);
CREATE INDEX idx_patients_active ON patients(is_active);

-- Provider indexes
CREATE INDEX idx_providers_npi ON providers(npi);
CREATE INDEX idx_providers_name ON providers(last_name, first_name);
CREATE INDEX idx_providers_specialty ON providers(specialty);
CREATE INDEX idx_providers_active ON providers(is_active);

-- Organization indexes
CREATE INDEX idx_organizations_name ON organizations(name);
CREATE INDEX idx_organizations_type ON organizations(type);
CREATE INDEX idx_organizations_npi ON organizations(npi);

-- Encounter indexes
CREATE INDEX idx_encounters_patient ON encounters(patient_id);
CREATE INDEX idx_encounters_provider ON encounters(provider_id);
CREATE INDEX idx_encounters_date ON encounters(start_date);
CREATE INDEX idx_encounters_status ON encounters(status);

-- Clinical data indexes
CREATE INDEX idx_diagnoses_patient ON diagnoses(patient_id);
CREATE INDEX idx_diagnoses_code ON diagnoses(diagnosis_code);
CREATE INDEX idx_medications_patient ON medications(patient_id);
CREATE INDEX idx_medications_name ON medications(medication_name);
CREATE INDEX idx_vital_signs_patient ON vital_signs(patient_id);
CREATE INDEX idx_vital_signs_type ON vital_signs(vital_sign_type);
CREATE INDEX idx_lab_results_patient ON lab_results(patient_id);
CREATE INDEX idx_lab_results_test ON lab_results(test_name);
CREATE INDEX idx_procedures_patient ON procedures(patient_id);
CREATE INDEX idx_allergies_patient ON allergies(patient_id);
CREATE INDEX idx_immunizations_patient ON immunizations(patient_id);

-- Documentation indexes
CREATE INDEX idx_clinical_notes_patient ON clinical_notes(patient_id);
CREATE INDEX idx_clinical_notes_type ON clinical_notes(note_type);
CREATE INDEX idx_documents_patient ON documents(patient_id);
CREATE INDEX idx_documents_type ON documents(document_type);

-- Relationship indexes
CREATE INDEX idx_patient_provider_patient ON patient_provider_relationships(patient_id);
CREATE INDEX idx_patient_provider_provider ON patient_provider_relationships(provider_id);
CREATE INDEX idx_provider_org_provider ON provider_organization_relationships(provider_id);
CREATE INDEX idx_provider_org_organization ON provider_organization_relationships(organization_id);

-- Audit indexes
CREATE INDEX idx_audit_log_table ON data_audit_log(table_name);
CREATE INDEX idx_audit_log_record ON data_audit_log(record_id);
CREATE INDEX idx_audit_log_date ON data_audit_log(changed_at);

-- Full-text search indexes
CREATE INDEX idx_patients_search ON patients USING gin(to_tsvector('english', first_name || ' ' || last_name || ' ' || mrn));
CREATE INDEX idx_providers_search ON providers USING gin(to_tsvector('english', first_name || ' ' || last_name || ' ' || specialty));
CREATE INDEX idx_organizations_search ON organizations USING gin(to_tsvector('english', name || ' ' || type));

-- ======================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ======================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_providers_updated_at BEFORE UPDATE ON providers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_encounters_updated_at BEFORE UPDATE ON encounters FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_diagnoses_updated_at BEFORE UPDATE ON diagnoses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_medications_updated_at BEFORE UPDATE ON medications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_procedures_updated_at BEFORE UPDATE ON procedures FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_allergies_updated_at BEFORE UPDATE ON allergies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_clinical_notes_updated_at BEFORE UPDATE ON clinical_notes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_patient_provider_relationships_updated_at BEFORE UPDATE ON patient_provider_relationships FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_provider_organization_relationships_updated_at BEFORE UPDATE ON provider_organization_relationships FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ======================================================
-- VIEWS FOR COMMON QUERIES
-- ======================================================

-- Patient summary view
CREATE VIEW patient_summary AS
SELECT 
    p.patient_id,
    p.mrn,
    p.first_name,
    p.last_name,
    p.date_of_birth,
    p.gender,
    COUNT(DISTINCT e.encounter_id) as encounter_count,
    COUNT(DISTINCT d.diagnosis_id) as diagnosis_count,
    COUNT(DISTINCT m.medication_id) as medication_count,
    COUNT(DISTINCT a.allergy_id) as allergy_count,
    MAX(e.start_date) as last_encounter_date
FROM patients p
LEFT JOIN encounters e ON p.patient_id = e.patient_id
LEFT JOIN diagnoses d ON p.patient_id = d.patient_id
LEFT JOIN medications m ON p.patient_id = m.patient_id
LEFT JOIN allergies a ON p.patient_id = a.patient_id
WHERE p.is_active = true
GROUP BY p.patient_id, p.mrn, p.first_name, p.last_name, p.date_of_birth, p.gender;

-- Provider summary view
CREATE VIEW provider_summary AS
SELECT 
    pr.provider_id,
    pr.npi,
    pr.first_name,
    pr.last_name,
    pr.specialty,
    o.name as organization_name,
    COUNT(DISTINCT e.encounter_id) as encounter_count,
    COUNT(DISTINCT ppr.patient_id) as patient_count
FROM providers pr
LEFT JOIN encounters e ON pr.provider_id = e.provider_id
LEFT JOIN patient_provider_relationships ppr ON pr.provider_id = ppr.provider_id
LEFT JOIN organizations o ON pr.organization_id = o.organization_id
WHERE pr.is_active = true
GROUP BY pr.provider_id, pr.npi, pr.first_name, pr.last_name, pr.specialty, o.name;

-- ======================================================
-- COMMENTS
-- ======================================================

COMMENT ON TABLE patients IS 'Core patient information for the Abena IHR system';
COMMENT ON TABLE providers IS 'Healthcare providers including physicians, nurses, and other clinical staff';
COMMENT ON TABLE organizations IS 'Healthcare organizations such as hospitals, clinics, and laboratories';
COMMENT ON TABLE encounters IS 'Patient encounters and visits';
COMMENT ON TABLE diagnoses IS 'Patient diagnoses and conditions';
COMMENT ON TABLE medications IS 'Patient medications and prescriptions';
COMMENT ON TABLE vital_signs IS 'Patient vital signs measurements';
COMMENT ON TABLE lab_results IS 'Laboratory test results';
COMMENT ON TABLE procedures IS 'Medical procedures performed on patients';
COMMENT ON TABLE allergies IS 'Patient allergies and adverse reactions';
COMMENT ON TABLE immunizations IS 'Patient immunization records';
COMMENT ON TABLE clinical_notes IS 'Clinical documentation and notes';
COMMENT ON TABLE documents IS 'General documents and files';
COMMENT ON TABLE data_audit_log IS 'Audit trail for data changes';
COMMENT ON TABLE data_quality_metrics IS 'Data quality monitoring metrics';

-- ======================================================
-- GRANTS AND PERMISSIONS
-- ======================================================

-- Create roles for different access levels
CREATE ROLE abena_readonly;
CREATE ROLE abena_analyst;
CREATE ROLE abena_clinician;
CREATE ROLE abena_admin;

-- Grant appropriate permissions
GRANT CONNECT ON DATABASE abena_unified_db TO abena_readonly, abena_analyst, abena_clinician, abena_admin;
GRANT USAGE ON SCHEMA public TO abena_readonly, abena_analyst, abena_clinician, abena_admin;

-- Read-only access
GRANT SELECT ON ALL TABLES IN SCHEMA public TO abena_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO abena_readonly;

-- Analyst access (read + some write)
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO abena_analyst;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO abena_analyst;

-- Clinician access (read + clinical data write)
GRANT SELECT, INSERT, UPDATE ON patients, encounters, diagnoses, medications, vital_signs, lab_results, procedures, allergies, immunizations, clinical_notes TO abena_clinician;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO abena_clinician;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO abena_clinician;

-- Admin access (full access)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO abena_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO abena_admin; 