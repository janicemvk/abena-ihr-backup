-- Create schema for clinical outcomes
CREATE SCHEMA IF NOT EXISTS clinical_outcomes;

-- Create enums
CREATE TYPE clinical_outcomes.measurement_timing AS ENUM (
    'baseline',
    'week_2',
    'week_4',
    'week_8',
    'week_12',
    'week_24',
    'week_52'
);

CREATE TYPE clinical_outcomes.data_quality_level AS ENUM (
    'complete',
    'adequate',
    'minimal',
    'insufficient'
);

CREATE TYPE clinical_outcomes.outcome_type AS ENUM (
    'primary',
    'secondary',
    'patient_reported'
);

CREATE TYPE clinical_outcomes.assessment_status AS ENUM (
    'scheduled',
    'completed',
    'missed',
    'cancelled'
);

-- Create primary outcomes tables
CREATE TABLE clinical_outcomes.pain_assessments (
    assessment_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    pain_score_24h NUMERIC(3,1) CHECK (pain_score_24h >= 0 AND pain_score_24h <= 10),
    pain_score_7d NUMERIC(3,1) CHECK (pain_score_7d >= 0 AND pain_score_7d <= 10),
    pain_location TEXT[],
    pain_characteristics TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

CREATE TABLE clinical_outcomes.womac_assessments (
    assessment_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    pain_score NUMERIC(3,1) CHECK (pain_score >= 0 AND pain_score <= 20),
    stiffness_score NUMERIC(3,1) CHECK (stiffness_score >= 0 AND stiffness_score <= 8),
    physical_function_score NUMERIC(3,1) CHECK (physical_function_score >= 0 AND physical_function_score <= 68),
    total_score NUMERIC(3,1) CHECK (total_score >= 0 AND total_score <= 96),
    normalized_score NUMERIC(3,1) CHECK (normalized_score >= 0 AND normalized_score <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

CREATE TABLE clinical_outcomes.odi_assessments (
    assessment_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    pain_intensity_score NUMERIC(3,1) CHECK (pain_intensity_score >= 0 AND pain_intensity_score <= 5),
    personal_care_score NUMERIC(3,1) CHECK (personal_care_score >= 0 AND personal_care_score <= 5),
    lifting_score NUMERIC(3,1) CHECK (lifting_score >= 0 AND lifting_score <= 5),
    walking_score NUMERIC(3,1) CHECK (walking_score >= 0 AND walking_score <= 5),
    sitting_score NUMERIC(3,1) CHECK (sitting_score >= 0 AND sitting_score <= 5),
    standing_score NUMERIC(3,1) CHECK (standing_score >= 0 AND standing_score <= 5),
    sleeping_score NUMERIC(3,1) CHECK (sleeping_score >= 0 AND sleeping_score <= 5),
    sex_life_score NUMERIC(3,1) CHECK (sex_life_score >= 0 AND sex_life_score <= 5),
    social_life_score NUMERIC(3,1) CHECK (social_life_score >= 0 AND social_life_score <= 5),
    traveling_score NUMERIC(3,1) CHECK (traveling_score >= 0 AND traveling_score <= 5),
    total_score NUMERIC(3,1) CHECK (total_score >= 0 AND total_score <= 50),
    percentage_disability NUMERIC(3,1) CHECK (percentage_disability >= 0 AND percentage_disability <= 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

-- Create secondary outcomes tables
CREATE TABLE clinical_outcomes.medication_usage (
    record_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    medication_name VARCHAR(100) NOT NULL,
    dosage VARCHAR(50),
    frequency VARCHAR(50),
    start_date DATE,
    end_date DATE,
    reason_for_use TEXT,
    side_effects TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

CREATE TABLE clinical_outcomes.healthcare_utilization (
    record_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    visit_date TIMESTAMP NOT NULL,
    visit_type VARCHAR(50) NOT NULL,
    provider_type VARCHAR(50),
    visit_reason TEXT,
    procedures_performed TEXT[],
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

CREATE TABLE clinical_outcomes.quality_of_life (
    assessment_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    physical_health_score NUMERIC(3,1) CHECK (physical_health_score >= 0 AND physical_health_score <= 100),
    mental_health_score NUMERIC(3,1) CHECK (mental_health_score >= 0 AND mental_health_score <= 100),
    social_functioning_score NUMERIC(3,1) CHECK (social_functioning_score >= 0 AND social_functioning_score <= 100),
    life_satisfaction NUMERIC(3,1) CHECK (life_satisfaction >= 0 AND life_satisfaction <= 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

-- Create patient-reported outcomes tables
CREATE TABLE clinical_outcomes.weekly_symptom_tracking (
    record_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    report_date TIMESTAMP NOT NULL,
    pain_level NUMERIC(3,1) CHECK (pain_level >= 0 AND pain_level <= 10),
    stiffness_level NUMERIC(3,1) CHECK (stiffness_level >= 0 AND stiffness_level <= 10),
    sleep_quality NUMERIC(3,1) CHECK (sleep_quality >= 0 AND sleep_quality <= 10),
    activity_level NUMERIC(3,1) CHECK (activity_level >= 0 AND activity_level <= 10),
    mood_level NUMERIC(3,1) CHECK (mood_level >= 0 AND mood_level <= 10),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

CREATE TABLE clinical_outcomes.treatment_satisfaction (
    assessment_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    overall_satisfaction NUMERIC(3,1) CHECK (overall_satisfaction >= 0 AND overall_satisfaction <= 10),
    pain_improvement NUMERIC(3,1) CHECK (pain_improvement >= 0 AND pain_improvement <= 10),
    function_improvement NUMERIC(3,1) CHECK (function_improvement >= 0 AND function_improvement <= 10),
    treatment_side_effects NUMERIC(3,1) CHECK (treatment_side_effects >= 0 AND treatment_side_effects <= 10),
    would_recommend BOOLEAN,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

-- Create assessment management tables
CREATE TABLE clinical_outcomes.assessment_schedules (
    schedule_id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    baseline_date TIMESTAMP NOT NULL,
    study_duration_weeks INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

CREATE TABLE clinical_outcomes.scheduled_assessments (
    assessment_id SERIAL PRIMARY KEY,
    schedule_id INTEGER REFERENCES clinical_outcomes.assessment_schedules(schedule_id),
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    scheduled_date TIMESTAMP NOT NULL,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    status clinical_outcomes.assessment_status DEFAULT 'scheduled',
    completed_date TIMESTAMP,
    data_quality clinical_outcomes.data_quality_level,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

-- Create indexes for performance
CREATE INDEX idx_pain_assessments_patient_date ON clinical_outcomes.pain_assessments(patient_id, assessment_date);
CREATE INDEX idx_womac_assessments_patient_date ON clinical_outcomes.womac_assessments(patient_id, assessment_date);
CREATE INDEX idx_odi_assessments_patient_date ON clinical_outcomes.odi_assessments(patient_id, assessment_date);
CREATE INDEX idx_medication_usage_patient_date ON clinical_outcomes.medication_usage(patient_id, assessment_date);
CREATE INDEX idx_healthcare_utilization_patient_date ON clinical_outcomes.healthcare_utilization(patient_id, visit_date);
CREATE INDEX idx_quality_of_life_patient_date ON clinical_outcomes.quality_of_life(patient_id, assessment_date);
CREATE INDEX idx_weekly_symptoms_patient_date ON clinical_outcomes.weekly_symptom_tracking(patient_id, report_date);
CREATE INDEX idx_treatment_satisfaction_patient_date ON clinical_outcomes.treatment_satisfaction(patient_id, assessment_date);
CREATE INDEX idx_scheduled_assessments_schedule ON clinical_outcomes.scheduled_assessments(schedule_id);
CREATE INDEX idx_scheduled_assessments_date ON clinical_outcomes.scheduled_assessments(scheduled_date);

-- Create views for common queries
CREATE VIEW clinical_outcomes.patient_outcome_summary AS
SELECT 
    p.patient_id,
    p.assessment_date,
    p.measurement_timing,
    p.pain_score_24h,
    w.total_score as womac_total,
    w.normalized_score as womac_normalized,
    o.total_score as odi_total,
    o.percentage_disability as odi_percentage,
    q.physical_health_score,
    q.mental_health_score,
    q.life_satisfaction,
    t.overall_satisfaction
FROM clinical_outcomes.pain_assessments p
LEFT JOIN clinical_outcomes.womac_assessments w 
    ON p.patient_id = w.patient_id AND p.assessment_date = w.assessment_date
LEFT JOIN clinical_outcomes.odi_assessments o 
    ON p.patient_id = o.patient_id AND p.assessment_date = o.assessment_date
LEFT JOIN clinical_outcomes.quality_of_life q 
    ON p.patient_id = q.patient_id AND p.assessment_date = q.assessment_date
LEFT JOIN clinical_outcomes.treatment_satisfaction t 
    ON p.patient_id = t.patient_id AND p.assessment_date = t.assessment_date;

-- Create triggers for automatic updates
CREATE OR REPLACE FUNCTION clinical_outcomes.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update timestamp trigger to all tables
CREATE TRIGGER update_pain_assessments_timestamp
    BEFORE UPDATE ON clinical_outcomes.pain_assessments
    FOR EACH ROW
    EXECUTE FUNCTION clinical_outcomes.update_timestamp();

CREATE TRIGGER update_womac_assessments_timestamp
    BEFORE UPDATE ON clinical_outcomes.womac_assessments
    FOR EACH ROW
    EXECUTE FUNCTION clinical_outcomes.update_timestamp();

CREATE TRIGGER update_odi_assessments_timestamp
    BEFORE UPDATE ON clinical_outcomes.odi_assessments
    FOR EACH ROW
    EXECUTE FUNCTION clinical_outcomes.update_timestamp();

CREATE TRIGGER update_medication_usage_timestamp
    BEFORE UPDATE ON clinical_outcomes.medication_usage
    FOR EACH ROW
    EXECUTE FUNCTION clinical_outcomes.update_timestamp();

CREATE TRIGGER update_healthcare_utilization_timestamp
    BEFORE UPDATE ON clinical_outcomes.healthcare_utilization
    FOR EACH ROW
    EXECUTE FUNCTION clinical_outcomes.update_timestamp();

CREATE TRIGGER update_quality_of_life_timestamp
    BEFORE UPDATE ON clinical_outcomes.quality_of_life
    FOR EACH ROW
    EXECUTE FUNCTION clinical_outcomes.update_timestamp();

CREATE TRIGGER update_weekly_symptoms_timestamp
    BEFORE UPDATE ON clinical_outcomes.weekly_symptom_tracking
    FOR EACH ROW
    EXECUTE FUNCTION clinical_outcomes.update_timestamp();

CREATE TRIGGER update_treatment_satisfaction_timestamp
    BEFORE UPDATE ON clinical_outcomes.treatment_satisfaction
    FOR EACH ROW
    EXECUTE FUNCTION clinical_outcomes.update_timestamp();

CREATE TRIGGER update_assessment_schedules_timestamp
    BEFORE UPDATE ON clinical_outcomes.assessment_schedules
    FOR EACH ROW
    EXECUTE FUNCTION clinical_outcomes.update_timestamp();

CREATE TRIGGER update_scheduled_assessments_timestamp
    BEFORE UPDATE ON clinical_outcomes.scheduled_assessments
    FOR EACH ROW
    EXECUTE FUNCTION clinical_outcomes.update_timestamp();

-- Grant permissions
GRANT USAGE ON SCHEMA clinical_outcomes TO application_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA clinical_outcomes TO application_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA clinical_outcomes TO application_user;

GRANT USAGE ON SCHEMA clinical_outcomes TO reporting_user;
GRANT SELECT ON ALL TABLES IN SCHEMA clinical_outcomes TO reporting_user;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA clinical_outcomes TO reporting_user;

-- Verify schema creation
DO $$
BEGIN
    -- Check if schema exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'clinical_outcomes') THEN
        RAISE EXCEPTION 'Schema clinical_outcomes was not created';
    END IF;
    
    -- Check if tables exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'clinical_outcomes' AND table_name = 'pain_assessments') THEN
        RAISE EXCEPTION 'Table pain_assessments was not created';
    END IF;
    
    -- Check if indexes exist
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'clinical_outcomes' AND tablename = 'pain_assessments' AND indexname = 'idx_pain_assessments_patient_date') THEN
        RAISE EXCEPTION 'Index idx_pain_assessments_patient_date was not created';
    END IF;
    
    -- Check if triggers exist
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_pain_assessments_timestamp') THEN
        RAISE EXCEPTION 'Trigger update_pain_assessments_timestamp was not created';
    END IF;
    
    RAISE NOTICE 'All schema objects created successfully';
END $$; 