-- Abena IHR Data Ingestion Service Database Schema
-- Run this script to set up the PostgreSQL database

-- Create database (run as superuser)
-- CREATE DATABASE abena_ihr_data;

-- Connect to the database and create tables

-- Raw health data storage (all incoming data)
CREATE TABLE raw_health_data (
    id SERIAL PRIMARY KEY,
    message_id UUID UNIQUE NOT NULL,
    data_type VARCHAR(50) NOT NULL CHECK (data_type IN ('vitals', 'lab_result', 'medication', 'hl7_message', 'fhir_resource', 'imaging', 'clinical_notes')),
    raw_data JSONB NOT NULL,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    processing_status VARCHAR(20) DEFAULT 'received' CHECK (processing_status IN ('received', 'processing', 'processed', 'failed', 'rejected')),
    source_system VARCHAR(100),
    patient_id VARCHAR(100),
    provider_id VARCHAR(100),
    ingested_by INTEGER,
    checksum VARCHAR(64), -- SHA-256 hash for duplicate detection
    error_details TEXT,
    validation_errors JSONB,
    retry_count INTEGER DEFAULT 0,
    last_retry_at TIMESTAMP WITH TIME ZONE
);

-- Processed health data (normalized and validated)
CREATE TABLE processed_health_data (
    id SERIAL PRIMARY KEY,
    message_id UUID REFERENCES raw_health_data(message_id),
    patient_id VARCHAR(100) NOT NULL,
    provider_id VARCHAR(100),
    data_type VARCHAR(50) NOT NULL,
    structured_data JSONB NOT NULL,
    extracted_values JSONB, -- Key-value pairs for easy querying
    processing_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    quality_score DECIMAL(3,2), -- Data quality score (0.00 to 1.00)
    confidence_level DECIMAL(3,2), -- Confidence in data accuracy
    tags TEXT[], -- Searchable tags
    metadata JSONB -- Additional metadata
);

-- Vital signs (structured storage)
CREATE TABLE vital_signs (
    id SERIAL PRIMARY KEY,
    message_id UUID REFERENCES raw_health_data(message_id),
    patient_id VARCHAR(100) NOT NULL,
    provider_id VARCHAR(100),
    measurement_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    heart_rate INTEGER CHECK (heart_rate >= 0 AND heart_rate <= 300),
    blood_pressure_systolic INTEGER CHECK (blood_pressure_systolic >= 0 AND blood_pressure_systolic <= 300),
    blood_pressure_diastolic INTEGER CHECK (blood_pressure_diastolic >= 0 AND blood_pressure_diastolic <= 200),
    temperature DECIMAL(4,1) CHECK (temperature >= 80.0 AND temperature <= 110.0), -- Fahrenheit
    oxygen_saturation DECIMAL(4,1) CHECK (oxygen_saturation >= 0.0 AND oxygen_saturation <= 100.0),
    respiratory_rate INTEGER CHECK (respiratory_rate >= 0 AND respiratory_rate <= 60),
    weight DECIMAL(5,2) CHECK (weight >= 0.0 AND weight <= 1000.0), -- lbs
    height DECIMAL(4,1) CHECK (height >= 0.0 AND height <= 120.0), -- inches
    bmi DECIMAL(4,1) GENERATED ALWAYS AS (
        CASE 
            WHEN weight IS NOT NULL AND height IS NOT NULL AND height > 0 
            THEN ROUND((weight / (height * height)) * 703, 1)
            ELSE NULL 
        END
    ) STORED,
    source_system VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Laboratory results
CREATE TABLE lab_results (
    id SERIAL PRIMARY KEY,
    message_id UUID REFERENCES raw_health_data(message_id),
    patient_id VARCHAR(100) NOT NULL,
    provider_id VARCHAR(100),
    test_name VARCHAR(200) NOT NULL,
    test_code VARCHAR(50), -- LOINC code
    result_value TEXT NOT NULL,
    numeric_value DECIMAL(15,6), -- Extracted numeric value if applicable
    reference_range VARCHAR(100),
    units VARCHAR(50),
    status VARCHAR(20) DEFAULT 'final' CHECK (status IN ('preliminary', 'final', 'corrected', 'cancelled')),
    abnormal_flag VARCHAR(10), -- N, H, L, HH, LL, etc.
    lab_id VARCHAR(100),
    specimen_type VARCHAR(100),
    collection_timestamp TIMESTAMP WITH TIME ZONE,
    result_timestamp TIMESTAMP WITH TIME ZONE,
    source_system VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Medications
CREATE TABLE medications (
    id SERIAL PRIMARY KEY,
    message_id UUID REFERENCES raw_health_data(message_id),
    patient_id VARCHAR(100) NOT NULL,
    provider_id VARCHAR(100),
    prescriber_id VARCHAR(100),
    medication_name VARCHAR(200) NOT NULL,
    generic_name VARCHAR(200),
    dosage VARCHAR(100),
    dosage_form VARCHAR(50), -- tablet, capsule, liquid, etc.
    strength VARCHAR(50),
    frequency VARCHAR(100),
    route VARCHAR(50), -- oral, IV, topical, etc.
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    ndc_code VARCHAR(20), -- National Drug Code
    pharmacy_id VARCHAR(100),
    prescription_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'discontinued', 'completed', 'on_hold')),
    source_system VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- HL7 Messages (parsed)
CREATE TABLE hl7_messages (
    id SERIAL PRIMARY KEY,
    message_id UUID REFERENCES raw_health_data(message_id),
    message_type VARCHAR(10) NOT NULL, -- ADT, ORU, ORM, etc.
    message_control_id VARCHAR(50) NOT NULL,
    sending_application VARCHAR(100),
    receiving_application VARCHAR(100),
    message_timestamp TIMESTAMP WITH TIME ZONE,
    patient_id VARCHAR(100),
    parsed_segments JSONB, -- Parsed HL7 segments
    source_system VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- FHIR Resources (parsed)
CREATE TABLE fhir_resources (
    id SERIAL PRIMARY KEY,
    message_id UUID REFERENCES raw_health_data(message_id),
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100) NOT NULL,
    patient_reference VARCHAR(100),
    fhir_version VARCHAR(10) DEFAULT 'R4',
    raw_resource JSONB NOT NULL,
    parsed_data JSONB, -- Extracted and normalized data
    source_system VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Imaging studies
CREATE TABLE imaging_studies (
    id SERIAL PRIMARY KEY,
    message_id UUID REFERENCES raw_health_data(message_id),
    patient_id VARCHAR(100) NOT NULL,
    provider_id VARCHAR(100),
    study_id VARCHAR(100) UNIQUE NOT NULL,
    study_type VARCHAR(100) NOT NULL, -- X-ray, CT, MRI, etc.
    body_part VARCHAR(100),
    modality VARCHAR(20), -- CR, CT, MR, US, etc.
    study_date TIMESTAMP WITH TIME ZONE,
    report_status VARCHAR(20) DEFAULT 'pending' CHECK (report_status IN ('pending', 'preliminary', 'final', 'amended')),
    radiologist_id VARCHAR(100),
    report_text TEXT,
    findings TEXT,
    impression TEXT,
    source_system VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Clinical notes
CREATE TABLE clinical_notes (
    id SERIAL PRIMARY KEY,
    message_id UUID REFERENCES raw_health_data(message_id),
    patient_id VARCHAR(100) NOT NULL,
    provider_id VARCHAR(100),
    note_type VARCHAR(50) NOT NULL, -- progress_note, discharge_summary, consultation, etc.
    note_title VARCHAR(200),
    note_text TEXT NOT NULL,
    note_date TIMESTAMP WITH TIME ZONE,
    author_id VARCHAR(100),
    encounter_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'final', 'amended', 'deleted')),
    source_system VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data quality metrics
CREATE TABLE data_quality_metrics (
    id SERIAL PRIMARY KEY,
    data_type VARCHAR(50) NOT NULL,
    metric_date DATE NOT NULL,
    total_records INTEGER DEFAULT 0,
    valid_records INTEGER DEFAULT 0,
    invalid_records INTEGER DEFAULT 0,
    duplicate_records INTEGER DEFAULT 0,
    missing_required_fields INTEGER DEFAULT 0,
    quality_score DECIMAL(3,2),
    average_processing_time_ms INTEGER,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(data_type, metric_date)
);

-- Processing errors log
CREATE TABLE processing_errors (
    id SERIAL PRIMARY KEY,
    message_id UUID REFERENCES raw_health_data(message_id),
    error_type VARCHAR(50) NOT NULL, -- validation, parsing, storage, etc.
    error_message TEXT NOT NULL,
    error_details JSONB,
    retry_count INTEGER DEFAULT 0,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data lineage tracking
CREATE TABLE data_lineage (
    id SERIAL PRIMARY KEY,
    source_message_id UUID REFERENCES raw_health_data(message_id),
    target_message_id UUID REFERENCES raw_health_data(message_id),
    transformation_type VARCHAR(50) NOT NULL, -- parse, validate, enrich, etc.
    transformation_details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_raw_health_data_patient_id ON raw_health_data(patient_id);
CREATE INDEX idx_raw_health_data_data_type ON raw_health_data(data_type);
CREATE INDEX idx_raw_health_data_received_at ON raw_health_data(received_at);
CREATE INDEX idx_raw_health_data_processing_status ON raw_health_data(processing_status);
CREATE INDEX idx_raw_health_data_checksum ON raw_health_data(checksum);

CREATE INDEX idx_vital_signs_patient_id ON vital_signs(patient_id);
CREATE INDEX idx_vital_signs_measurement_timestamp ON vital_signs(measurement_timestamp);

CREATE INDEX idx_lab_results_patient_id ON lab_results(patient_id);
CREATE INDEX idx_lab_results_test_name ON lab_results(test_name);
CREATE INDEX idx_lab_results_result_timestamp ON lab_results(result_timestamp);

CREATE INDEX idx_medications_patient_id ON medications(patient_id);
CREATE INDEX idx_medications_medication_name ON medications(medication_name);
CREATE INDEX idx_medications_status ON medications(status);

CREATE INDEX idx_hl7_messages_patient_id ON hl7_messages(patient_id);
CREATE INDEX idx_hl7_messages_message_type ON hl7_messages(message_type);

CREATE INDEX idx_fhir_resources_patient_reference ON fhir_resources(patient_reference);
CREATE INDEX idx_fhir_resources_resource_type ON fhir_resources(resource_type);

CREATE INDEX idx_imaging_studies_patient_id ON imaging_studies(patient_id);
CREATE INDEX idx_imaging_studies_study_type ON imaging_studies(study_type);

CREATE INDEX idx_clinical_notes_patient_id ON clinical_notes(patient_id);
CREATE INDEX idx_clinical_notes_note_type ON clinical_notes(note_type);

-- Create views for common queries
CREATE VIEW daily_ingestion_summary AS
SELECT 
    DATE(received_at) as ingestion_date,
    data_type,
    COUNT(*) as total_messages,
    COUNT(CASE WHEN processing_status = 'processed' THEN 1 END) as processed_messages,
    COUNT(CASE WHEN processing_status = 'failed' THEN 1 END) as failed_messages,
    AVG(EXTRACT(EPOCH FROM (processed_at - received_at)) * 1000) as avg_processing_time_ms
FROM raw_health_data
WHERE received_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(received_at), data_type
ORDER BY ingestion_date DESC, data_type;

CREATE VIEW patient_data_summary AS
SELECT 
    patient_id,
    COUNT(DISTINCT CASE WHEN data_type = 'vitals' THEN message_id END) as vital_signs_count,
    COUNT(DISTINCT CASE WHEN data_type = 'lab_result' THEN message_id END) as lab_results_count,
    COUNT(DISTINCT CASE WHEN data_type = 'medication' THEN message_id END) as medications_count,
    COUNT(DISTINCT CASE WHEN data_type = 'imaging' THEN message_id END) as imaging_count,
    COUNT(DISTINCT CASE WHEN data_type = 'clinical_notes' THEN message_id END) as notes_count,
    MIN(received_at) as first_data_received,
    MAX(received_at) as last_data_received
FROM raw_health_data
GROUP BY patient_id;

-- Create functions for data maintenance
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at columns
CREATE TRIGGER update_vital_signs_updated_at BEFORE UPDATE ON vital_signs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lab_results_updated_at BEFORE UPDATE ON lab_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medications_updated_at BEFORE UPDATE ON medications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fhir_resources_updated_at BEFORE UPDATE ON fhir_resources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_imaging_studies_updated_at BEFORE UPDATE ON imaging_studies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clinical_notes_updated_at BEFORE UPDATE ON clinical_notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO abena_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO abena_user; 