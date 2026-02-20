-- Migration: 001_clinical_outcomes.sql
-- Description: Initial database schema for Abena IHR Clinical Outcomes Management System
-- Created: 2024-01-01
-- Author: Abena IHR Development Team

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types/enums
CREATE TYPE outcome_type AS ENUM (
    'clinical_outcome',
    'functional_outcome',
    'patient_reported_outcome',
    'safety_outcome',
    'economic_outcome'
);

CREATE TYPE measurement_type AS ENUM (
    'continuous',
    'categorical',
    'ordinal',
    'binary',
    'time_to_event'
);

CREATE TYPE data_quality_status AS ENUM (
    'excellent',
    'good',
    'fair',
    'poor',
    'unacceptable'
);

CREATE TYPE evaluation_status AS ENUM (
    'pending',
    'in_progress',
    'completed',
    'failed',
    'cancelled'
);

CREATE TYPE audit_action AS ENUM (
    'create',
    'update',
    'delete',
    'export',
    'import'
);

-- Create outcomes table
CREATE TABLE outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    outcome_type outcome_type NOT NULL,
    measurement_type measurement_type NOT NULL,
    unit VARCHAR(50),
    min_value DECIMAL(10,2),
    max_value DECIMAL(10,2),
    reference_range_low DECIMAL(10,2),
    reference_range_high DECIMAL(10,2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Create outcome measurements table
CREATE TABLE outcome_measurements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    outcome_id UUID NOT NULL REFERENCES outcomes(id) ON DELETE CASCADE,
    patient_id VARCHAR(100) NOT NULL,
    measurement_value DECIMAL(10,2),
    measurement_text TEXT,
    measurement_date TIMESTAMP WITH TIME ZONE NOT NULL,
    data_source VARCHAR(100),
    data_quality_score DECIMAL(3,2),
    is_validated BOOLEAN DEFAULT false,
    validated_by UUID,
    validated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Create clinical forms table
CREATE TABLE clinical_forms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_name VARCHAR(255) NOT NULL,
    form_version VARCHAR(20) NOT NULL,
    description TEXT,
    form_schema JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Create form responses table
CREATE TABLE form_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_id UUID NOT NULL REFERENCES clinical_forms(id) ON DELETE CASCADE,
    patient_id VARCHAR(100) NOT NULL,
    response_data JSONB NOT NULL,
    completion_date TIMESTAMP WITH TIME ZONE,
    is_complete BOOLEAN DEFAULT false,
    data_quality_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Create outcome evaluations table
CREATE TABLE outcome_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    outcome_id UUID NOT NULL REFERENCES outcomes(id) ON DELETE CASCADE,
    patient_id VARCHAR(100) NOT NULL,
    evaluation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    evaluation_status evaluation_status DEFAULT 'pending',
    evaluation_result JSONB,
    evaluator_id UUID,
    evaluation_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Create data quality audits table
CREATE TABLE data_quality_audits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID,
    audit_action audit_action NOT NULL,
    audit_details JSONB,
    data_quality_score DECIMAL(3,2),
    audit_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    audited_by UUID
);

-- Create outcome frameworks table
CREATE TABLE outcome_frameworks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    framework_name VARCHAR(255) NOT NULL,
    framework_version VARCHAR(20) NOT NULL,
    description TEXT,
    framework_schema JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

-- Create framework outcomes mapping table
CREATE TABLE framework_outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    framework_id UUID NOT NULL REFERENCES outcome_frameworks(id) ON DELETE CASCADE,
    outcome_id UUID NOT NULL REFERENCES outcomes(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT false,
    weight DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(framework_id, outcome_id)
);

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create providers table
CREATE TABLE IF NOT EXISTS providers (
    provider_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create appointments table
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES patients(patient_id),
    provider_id VARCHAR(50) REFERENCES providers(provider_id),
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    appointment_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add provider availability table for scheduling support
CREATE TABLE IF NOT EXISTS provider_availability (
    availability_id SERIAL PRIMARY KEY,
    provider_id VARCHAR(50) REFERENCES providers(provider_id),
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6), -- 0=Sunday, 1=Monday, etc.
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create provider time slots table for specific dates
CREATE TABLE IF NOT EXISTS provider_time_slots (
    slot_id SERIAL PRIMARY KEY,
    provider_id VARCHAR(50) REFERENCES providers(provider_id),
    slot_date DATE NOT NULL,
    slot_time TIME NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    is_available BOOLEAN DEFAULT true,
    is_booked BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create clinical outcomes table
CREATE TABLE IF NOT EXISTS clinical_outcomes (
    outcome_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) REFERENCES patients(patient_id),
    outcome_type VARCHAR(100) NOT NULL,
    outcome_value TEXT,
    outcome_date DATE,
    provider_id VARCHAR(50) REFERENCES providers(provider_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_outcome_measurements_patient_id ON outcome_measurements(patient_id);
CREATE INDEX idx_outcome_measurements_outcome_id ON outcome_measurements(outcome_id);
CREATE INDEX idx_outcome_measurements_date ON outcome_measurements(measurement_date);
CREATE INDEX idx_form_responses_patient_id ON form_responses(patient_id);
CREATE INDEX idx_form_responses_form_id ON form_responses(form_id);
CREATE INDEX idx_outcome_evaluations_patient_id ON outcome_evaluations(patient_id);
CREATE INDEX idx_outcome_evaluations_outcome_id ON outcome_evaluations(outcome_id);
CREATE INDEX idx_data_quality_audits_table_record ON data_quality_audits(table_name, record_id);
CREATE INDEX idx_data_quality_audits_date ON data_quality_audits(audit_date);
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_appointments_provider_id ON appointments(provider_id);
CREATE INDEX idx_appointments_date_time ON appointments(appointment_date, appointment_time);
CREATE INDEX idx_provider_availability_provider_id ON provider_availability(provider_id);
CREATE INDEX idx_provider_availability_day ON provider_availability(day_of_week);
CREATE INDEX idx_provider_time_slots_provider_id ON provider_time_slots(provider_id);
CREATE INDEX idx_provider_time_slots_date ON provider_time_slots(slot_date);
CREATE INDEX idx_provider_time_slots_available ON provider_time_slots(is_available, is_booked);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_outcomes_updated_at BEFORE UPDATE ON outcomes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_outcome_measurements_updated_at BEFORE UPDATE ON outcome_measurements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clinical_forms_updated_at BEFORE UPDATE ON clinical_forms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_form_responses_updated_at BEFORE UPDATE ON form_responses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_outcome_evaluations_updated_at BEFORE UPDATE ON outcome_evaluations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_outcome_frameworks_updated_at BEFORE UPDATE ON outcome_frameworks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE VIEW outcome_summary AS
SELECT 
    o.id,
    o.name,
    o.outcome_type,
    o.measurement_type,
    COUNT(om.id) as measurement_count,
    AVG(om.data_quality_score) as avg_data_quality,
    MIN(om.measurement_date) as first_measurement,
    MAX(om.measurement_date) as last_measurement
FROM outcomes o
LEFT JOIN outcome_measurements om ON o.id = om.outcome_id
WHERE o.is_active = true
GROUP BY o.id, o.name, o.outcome_type, o.measurement_type;

CREATE VIEW patient_outcome_overview AS
SELECT 
    om.patient_id,
    o.name as outcome_name,
    o.outcome_type,
    COUNT(om.id) as measurement_count,
    AVG(om.data_quality_score) as avg_data_quality,
    MIN(om.measurement_date) as first_measurement,
    MAX(om.measurement_date) as last_measurement
FROM outcome_measurements om
JOIN outcomes o ON om.outcome_id = o.id
WHERE o.is_active = true
GROUP BY om.patient_id, o.name, o.outcome_type;

-- Insert sample data
INSERT INTO outcomes (name, description, outcome_type, measurement_type, unit, min_value, max_value) VALUES
('Blood Pressure Systolic', 'Systolic blood pressure measurement', 'clinical_outcome', 'continuous', 'mmHg', 70, 200),
('Blood Pressure Diastolic', 'Diastolic blood pressure measurement', 'clinical_outcome', 'continuous', 'mmHg', 40, 120),
('Heart Rate', 'Resting heart rate', 'clinical_outcome', 'continuous', 'bpm', 40, 200),
('Body Mass Index', 'BMI calculation', 'clinical_outcome', 'continuous', 'kg/m²', 15, 50),
('Pain Score', 'Patient reported pain level', 'patient_reported_outcome', 'ordinal', 'scale 0-10', 0, 10),
('Functional Independence', 'Patient functional status', 'functional_outcome', 'ordinal', 'scale 0-100', 0, 100),
('Hospital Readmission', '30-day readmission status', 'safety_outcome', 'binary', 'yes/no', 0, 1),
('Length of Stay', 'Hospital length of stay', 'economic_outcome', 'continuous', 'days', 1, 365);

INSERT INTO clinical_forms (form_name, form_version, description, form_schema) VALUES
('Patient Assessment Form', '1.0', 'Comprehensive patient assessment form', '{"fields": [{"name": "patient_id", "type": "text", "required": true}, {"name": "assessment_date", "type": "date", "required": true}, {"name": "vital_signs", "type": "object", "fields": [{"name": "blood_pressure_systolic", "type": "number"}, {"name": "blood_pressure_diastolic", "type": "number"}, {"name": "heart_rate", "type": "number"}]}]}'),
('Outcome Evaluation Form', '1.0', 'Standard outcome evaluation form', '{"fields": [{"name": "patient_id", "type": "text", "required": true}, {"name": "evaluation_date", "type": "date", "required": true}, {"name": "outcomes", "type": "array", "items": {"type": "object", "fields": [{"name": "outcome_id", "type": "text"}, {"name": "value", "type": "number"}, {"name": "notes", "type": "text"}]}}]}');

INSERT INTO outcome_frameworks (framework_name, framework_version, description, framework_schema) VALUES
('Cardiovascular Outcomes Framework', '1.0', 'Comprehensive cardiovascular outcomes assessment framework', '{"description": "Framework for assessing cardiovascular outcomes", "outcomes": ["blood_pressure_systolic", "blood_pressure_diastolic", "heart_rate"], "scoring": {"method": "weighted_average", "weights": {"blood_pressure_systolic": 0.4, "blood_pressure_diastolic": 0.4, "heart_rate": 0.2}}}'),
('Patient Safety Framework', '1.0', 'Patient safety outcomes framework', '{"description": "Framework for assessing patient safety outcomes", "outcomes": ["hospital_readmission", "length_of_stay"], "scoring": {"method": "composite", "calculation": "readmission_rate * 0.7 + length_of_stay_score * 0.3}}}');

-- Insert sample data for testing
INSERT INTO patients (patient_id, first_name, last_name, email, phone, date_of_birth, gender) VALUES
('P001', 'John', 'Smith', 'john.smith@email.com', '555-0101', '1985-03-15', 'M'),
('P002', 'Sarah', 'Johnson', 'sarah.johnson@email.com', '555-0102', '1990-07-22', 'F'),
('P003', 'Mike', 'Wilson', 'mike.wilson@email.com', '555-0103', '1978-11-08', 'M');

-- Insert sample providers
INSERT INTO providers (provider_id, first_name, last_name, specialization, email, phone) VALUES
('DOC001', 'Dr. Emily', 'Davis', 'Cardiology', 'emily.davis@abena.com', '555-0201'),
('DOC002', 'Dr. Robert', 'Chen', 'Neurology', 'robert.chen@abena.com', '555-0202'),
('DOC003', 'Dr. Maria', 'Garcia', 'Pediatrics', 'maria.garcia@abena.com', '555-0203');

-- Add sample provider availability (Monday to Friday, 9 AM to 5 PM)
INSERT INTO provider_availability (provider_id, day_of_week, start_time, end_time) VALUES
-- Dr. Emily Davis - Monday to Friday, 9 AM to 5 PM
('DOC001', 1, '09:00:00', '17:00:00'), -- Monday
('DOC001', 2, '09:00:00', '17:00:00'), -- Tuesday
('DOC001', 3, '09:00:00', '17:00:00'), -- Wednesday
('DOC001', 4, '09:00:00', '17:00:00'), -- Thursday
('DOC001', 5, '09:00:00', '17:00:00'), -- Friday

-- Dr. Robert Chen - Monday to Friday, 10 AM to 6 PM
('DOC002', 1, '10:00:00', '18:00:00'), -- Monday
('DOC002', 2, '10:00:00', '18:00:00'), -- Tuesday
('DOC002', 3, '10:00:00', '18:00:00'), -- Wednesday
('DOC002', 4, '10:00:00', '18:00:00'), -- Thursday
('DOC002', 5, '10:00:00', '18:00:00'), -- Friday

-- Dr. Maria Garcia - Monday to Friday, 8 AM to 4 PM
('DOC003', 1, '08:00:00', '16:00:00'), -- Monday
('DOC003', 2, '08:00:00', '16:00:00'), -- Tuesday
('DOC003', 3, '08:00:00', '16:00:00'), -- Wednesday
('DOC003', 4, '08:00:00', '16:00:00'), -- Thursday
('DOC003', 5, '08:00:00', '16:00:00'); -- Friday

-- Insert sample appointments
INSERT INTO appointments (patient_id, provider_id, appointment_date, appointment_time, appointment_type, status, notes) VALUES
('P001', 'DOC001', '2024-07-20', '10:00:00', 'Follow-up', 'confirmed', 'Regular checkup'),
('P002', 'DOC002', '2024-07-20', '14:30:00', 'Consultation', 'pending', 'New patient consultation'),
('P003', 'DOC003', '2024-07-21', '09:00:00', 'Emergency', 'confirmed', 'Urgent care needed');

INSERT INTO clinical_outcomes (patient_id, outcome_type, outcome_value, outcome_date, provider_id) VALUES
('P001', 'Blood Pressure', '120/80 mmHg', '2024-01-15', 'D001'),
('P002', 'Neurological Assessment', 'Normal reflexes and coordination', '2024-01-15', 'D002'),
('P003', 'Pediatric Assessment', 'Healthy development, no concerns', '2024-01-16', 'D003'),
('P004', 'Cardiac Function', 'Ejection fraction 65%', '2024-01-16', 'D001'),
('P005', 'Orthopedic Assessment', 'Mild arthritis in right knee', '2024-01-17', 'D004')
ON CONFLICT DO NOTHING;

-- Grant permissions (adjust as needed for your environment)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO abena_ihr_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO abena_ihr_user; 