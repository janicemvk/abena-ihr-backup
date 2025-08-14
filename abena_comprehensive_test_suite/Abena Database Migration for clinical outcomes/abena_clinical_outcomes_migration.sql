-- Abena IHR - Database Migration for Clinical Outcomes Schema
-- Execute this script to create the clinical outcomes database structure

-- ============================================================================
-- Create Clinical Outcomes Schema
-- ============================================================================

-- Create schema for clinical outcomes if it doesn't exist
CREATE SCHEMA IF NOT EXISTS clinical_outcomes;

-- Set search path
SET search_path TO clinical_outcomes, public;

-- ============================================================================
-- Create Enums and Types
-- ============================================================================

-- Measurement timing enum
CREATE TYPE measurement_timing AS ENUM (
    'baseline',
    'week_2', 
    'week_4',
    'week_8',
    'week_12',
    'week_24',
    'week_52',
    'unscheduled'
);

-- Data quality enum
CREATE TYPE data_quality_level AS ENUM (
    'complete',
    'adequate', 
    'minimal',
    'insufficient'
);

-- Outcome type enum
CREATE TYPE outcome_type AS ENUM (
    'primary',
    'secondary',
    'patient_reported',
    'safety',
    'economic'
);

-- Assessment status enum
CREATE TYPE assessment_status AS ENUM (
    'scheduled',
    'completed',
    'overdue',
    'cancelled'
);

-- ============================================================================
-- Create Primary Outcomes Tables
-- ============================================================================

-- Pain assessments table
CREATE TABLE pain_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    measurement_timing measurement_timing NOT NULL,
    
    -- Pain intensity scores (0-10 scale)
    current_pain DECIMAL(3,1) NOT NULL CHECK (current_pain >= 0 AND current_pain <= 10),
    average_pain_24h DECIMAL(3,1) NOT NULL CHECK (average_pain_24h >= 0 AND average_pain_24h <= 10),
    worst_pain_24h DECIMAL(3,1) NOT NULL CHECK (worst_pain_24h >= 0 AND worst_pain_24h <= 10),
    least_pain_24h DECIMAL(3,1) NOT NULL CHECK (least_pain_24h >= 0 AND least_pain_24h <= 10),
    pain_interference DECIMAL(3,1) NOT NULL CHECK (pain_interference >= 0 AND pain_interference <= 10),
    
    -- Activity-specific pain (optional)
    pain_at_rest DECIMAL(3,1) CHECK (pain_at_rest >= 0 AND pain_at_rest <= 10),
    pain_with_movement DECIMAL(3,1) CHECK (pain_with_movement >= 0 AND pain_with_movement <= 10),
    pain_with_exercise DECIMAL(3,1) CHECK (pain_with_exercise >= 0 AND pain_with_exercise <= 10),
    
    -- Pain characteristics
    pain_locations TEXT[] DEFAULT '{}',
    pain_quality TEXT[] DEFAULT '{}',
    
    -- Assessment metadata
    assessment_method VARCHAR(50) DEFAULT 'self_report',
    assessor_type VARCHAR(50) DEFAULT 'patient',
    assessor_id VARCHAR(50),
    data_quality data_quality_level NOT NULL DEFAULT 'complete',
    notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    version INTEGER DEFAULT 1,
    
    -- Constraints
    CONSTRAINT valid_pain_progression CHECK (worst_pain_24h >= average_pain_24h AND average_pain_24h >= least_pain_24h),
    CONSTRAINT unique_patient_assessment UNIQUE (patient_id, measurement_timing, assessment_date)
);

-- WOMAC assessments table
CREATE TABLE womac_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    measurement_timing measurement_timing NOT NULL,
    
    -- Pain subscale (5 items, 0-4 scale each)
    pain_walking INTEGER NOT NULL CHECK (pain_walking >= 0 AND pain_walking <= 4),
    pain_stairs INTEGER NOT NULL CHECK (pain_stairs >= 0 AND pain_stairs <= 4),
    pain_night_bed INTEGER NOT NULL CHECK (pain_night_bed >= 0 AND pain_night_bed <= 4),
    pain_sitting INTEGER NOT NULL CHECK (pain_sitting >= 0 AND pain_sitting <= 4),
    pain_standing INTEGER NOT NULL CHECK (pain_standing >= 0 AND pain_standing <= 4),
    
    -- Stiffness subscale (2 items, 0-4 scale each)
    stiffness_waking INTEGER NOT NULL CHECK (stiffness_waking >= 0 AND stiffness_waking <= 4),
    stiffness_later_day INTEGER NOT NULL CHECK (stiffness_later_day >= 0 AND stiffness_later_day <= 4),
    
    -- Physical function subscale (17 items, 0-4 scale each)
    function_stairs_down INTEGER NOT NULL CHECK (function_stairs_down >= 0 AND function_stairs_down <= 4),
    function_stairs_up INTEGER NOT NULL CHECK (function_stairs_up >= 0 AND function_stairs_up <= 4),
    function_rising_sitting INTEGER NOT NULL CHECK (function_rising_sitting >= 0 AND function_rising_sitting <= 4),
    function_standing INTEGER NOT NULL CHECK (function_standing >= 0 AND function_standing <= 4),
    function_bending INTEGER NOT NULL CHECK (function_bending >= 0 AND function_bending <= 4),
    function_walking_flat INTEGER NOT NULL CHECK (function_walking_flat >= 0 AND function_walking_flat <= 4),
    function_getting_in_out_car INTEGER NOT NULL CHECK (function_getting_in_out_car >= 0 AND function_getting_in_out_car <= 4),
    function_shopping INTEGER NOT NULL CHECK (function_shopping >= 0 AND function_shopping <= 4),
    function_socks INTEGER NOT NULL CHECK (function_socks >= 0 AND function_socks <= 4),
    function_rising_bed INTEGER NOT NULL CHECK (function_rising_bed >= 0 AND function_rising_bed <= 4),
    function_socks_off INTEGER NOT NULL CHECK (function_socks_off >= 0 AND function_socks_off <= 4),
    function_lying_bed INTEGER NOT NULL CHECK (function_lying_bed >= 0 AND function_lying_bed <= 4),
    function_bath_shower INTEGER NOT NULL CHECK (function_bath_shower >= 0 AND function_bath_shower <= 4),
    function_sitting INTEGER NOT NULL CHECK (function_sitting >= 0 AND function_sitting <= 4),
    function_toilet INTEGER NOT NULL CHECK (function_toilet >= 0 AND function_toilet <= 4),
    function_heavy_domestic INTEGER NOT NULL CHECK (function_heavy_domestic >= 0 AND function_heavy_domestic <= 4),
    function_light_domestic INTEGER NOT NULL CHECK (function_light_domestic >= 0 AND function_light_domestic <= 4),
    
    -- Computed scores (calculated by triggers)
    pain_score INTEGER GENERATED ALWAYS AS (
        pain_walking + pain_stairs + pain_night_bed + pain_sitting + pain_standing
    ) STORED,
    stiffness_score INTEGER GENERATED ALWAYS AS (
        stiffness_waking + stiffness_later_day
    ) STORED,
    function_score INTEGER GENERATED ALWAYS AS (
        function_stairs_down + function_stairs_up + function_rising_sitting + function_standing + 
        function_bending + function_walking_flat + function_getting_in_out_car + function_shopping + 
        function_socks + function_rising_bed + function_socks_off + function_lying_bed + 
        function_bath_shower + function_sitting + function_toilet + function_heavy_domestic + function_light_domestic
    ) STORED,
    total_score INTEGER GENERATED ALWAYS AS (
        pain_walking + pain_stairs + pain_night_bed + pain_sitting + pain_standing +
        stiffness_waking + stiffness_later_day +
        function_stairs_down + function_stairs_up + function_rising_sitting + function_standing + 
        function_bending + function_walking_flat + function_getting_in_out_car + function_shopping + 
        function_socks + function_rising_bed + function_socks_off + function_lying_bed + 
        function_bath_shower + function_sitting + function_toilet + function_heavy_domestic + function_light_domestic
    ) STORED,
    normalized_score DECIMAL(5,2) GENERATED ALWAYS AS (
        ((pain_walking + pain_stairs + pain_night_bed + pain_sitting + pain_standing +
          stiffness_waking + stiffness_later_day +
          function_stairs_down + function_stairs_up + function_rising_sitting + function_standing + 
          function_bending + function_walking_flat + function_getting_in_out_car + function_shopping + 
          function_socks + function_rising_bed + function_socks_off + function_lying_bed + 
          function_bath_shower + function_sitting + function_toilet + function_heavy_domestic + function_light_domestic
        ) / 96.0) * 100.0
    ) STORED,
    
    -- Assessment metadata
    assessor_id VARCHAR(50),
    data_quality data_quality_level NOT NULL DEFAULT 'complete',
    notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    version INTEGER DEFAULT 1,
    
    -- Constraints
    CONSTRAINT unique_patient_womac_assessment UNIQUE (patient_id, measurement_timing, assessment_date)
);

-- ODI assessments table
CREATE TABLE odi_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    measurement_timing measurement_timing NOT NULL,
    
    -- ODI sections (0-5 scale each)
    pain_intensity INTEGER NOT NULL CHECK (pain_intensity >= 0 AND pain_intensity <= 5),
    personal_care INTEGER NOT NULL CHECK (personal_care >= 0 AND personal_care <= 5),
    lifting INTEGER NOT NULL CHECK (lifting >= 0 AND lifting <= 5),
    walking INTEGER NOT NULL CHECK (walking >= 0 AND walking <= 5),
    sitting INTEGER NOT NULL CHECK (sitting >= 0 AND sitting <= 5),
    standing INTEGER NOT NULL CHECK (standing >= 0 AND standing <= 5),
    sleeping INTEGER NOT NULL CHECK (sleeping >= 0 AND sleeping <= 5),
    sex_life INTEGER NOT NULL CHECK (sex_life >= 0 AND sex_life <= 5),
    social_life INTEGER NOT NULL CHECK (social_life >= 0 AND social_life <= 5),
    traveling INTEGER NOT NULL CHECK (traveling >= 0 AND traveling <= 5),
    
    -- Computed scores
    total_score INTEGER GENERATED ALWAYS AS (
        pain_intensity + personal_care + lifting + walking + sitting + 
        standing + sleeping + sex_life + social_life + traveling
    ) STORED,
    percentage_disability DECIMAL(5,2) GENERATED ALWAYS AS (
        ((pain_intensity + personal_care + lifting + walking + sitting + 
          standing + sleeping + sex_life + social_life + traveling) / 50.0) * 100.0
    ) STORED,
    
    -- Assessment metadata
    assessor_id VARCHAR(50),
    data_quality data_quality_level NOT NULL DEFAULT 'complete',
    notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    version INTEGER DEFAULT 1,
    
    -- Constraints
    CONSTRAINT unique_patient_odi_assessment UNIQUE (patient_id, measurement_timing, assessment_date)
);

-- ============================================================================
-- Create Secondary Outcomes Tables
-- ============================================================================

-- Medication usage assessments table
CREATE TABLE medication_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    measurement_timing measurement_timing NOT NULL,
    assessment_period_days INTEGER DEFAULT 30 CHECK (assessment_period_days > 0),
    
    -- Medication details (stored as JSONB for flexibility)
    current_medications JSONB NOT NULL DEFAULT '[]',
    opioid_usage JSONB DEFAULT '{}',
    nsaid_usage JSONB DEFAULT '{}',
    adjuvant_usage JSONB DEFAULT '{}',
    
    -- Usage metrics
    total_medication_count INTEGER DEFAULT 0 CHECK (total_medication_count >= 0),
    pain_medication_count INTEGER DEFAULT 0 CHECK (pain_medication_count >= 0),
    
    -- Adherence metrics
    adherence_percentage DECIMAL(5,2) DEFAULT 100.0 CHECK (adherence_percentage >= 0 AND adherence_percentage <= 100),
    missed_doses_count INTEGER DEFAULT 0 CHECK (missed_doses_count >= 0),
    
    -- Side effects and effectiveness
    side_effects TEXT[] DEFAULT '{}',
    side_effect_severity JSONB DEFAULT '{}',
    medication_effectiveness DECIMAL(3,1) DEFAULT 5.0 CHECK (medication_effectiveness >= 0 AND medication_effectiveness <= 10),
    satisfaction_with_medication DECIMAL(3,1) DEFAULT 5.0 CHECK (satisfaction_with_medication >= 0 AND satisfaction_with_medication <= 10),
    
    -- Assessment metadata
    assessor_id VARCHAR(50),
    data_quality data_quality_level NOT NULL DEFAULT 'complete',
    notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    version INTEGER DEFAULT 1,
    
    -- Constraints
    CONSTRAINT unique_patient_medication_assessment UNIQUE (patient_id, measurement_timing, assessment_date)
);

-- Healthcare utilization assessments table
CREATE TABLE healthcare_utilization (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    measurement_timing measurement_timing NOT NULL,
    assessment_period_days INTEGER DEFAULT 30 CHECK (assessment_period_days > 0),
    
    -- Healthcare visits
    primary_care_visits INTEGER DEFAULT 0 CHECK (primary_care_visits >= 0),
    specialist_visits INTEGER DEFAULT 0 CHECK (specialist_visits >= 0),
    pain_clinic_visits INTEGER DEFAULT 0 CHECK (pain_clinic_visits >= 0),
    physical_therapy_visits INTEGER DEFAULT 0 CHECK (physical_therapy_visits >= 0),
    
    -- Emergency utilization
    emergency_room_visits INTEGER DEFAULT 0 CHECK (emergency_room_visits >= 0),
    urgent_care_visits INTEGER DEFAULT 0 CHECK (urgent_care_visits >= 0),
    hospitalizations INTEGER DEFAULT 0 CHECK (hospitalizations >= 0),
    hospital_days INTEGER DEFAULT 0 CHECK (hospital_days >= 0),
    
    -- Procedures and tests
    imaging_studies INTEGER DEFAULT 0 CHECK (imaging_studies >= 0),
    laboratory_tests INTEGER DEFAULT 0 CHECK (laboratory_tests >= 0),
    procedures INTEGER DEFAULT 0 CHECK (procedures >= 0),
    
    -- Costs (optional)
    estimated_total_cost DECIMAL(10,2) CHECK (estimated_total_cost >= 0),
    out_of_pocket_cost DECIMAL(10,2) CHECK (out_of_pocket_cost >= 0),
    
    -- Utilization reasons
    pain_related_visits INTEGER DEFAULT 0 CHECK (pain_related_visits >= 0),
    treatment_related_visits INTEGER DEFAULT 0 CHECK (treatment_related_visits >= 0),
    
    -- Computed total visits
    total_visits INTEGER GENERATED ALWAYS AS (
        primary_care_visits + specialist_visits + pain_clinic_visits + 
        physical_therapy_visits + emergency_room_visits + urgent_care_visits
    ) STORED,
    
    -- Assessment metadata
    assessor_id VARCHAR(50),
    data_quality data_quality_level NOT NULL DEFAULT 'complete',
    notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    version INTEGER DEFAULT 1,
    
    -- Constraints
    CONSTRAINT unique_patient_utilization_assessment UNIQUE (patient_id, measurement_timing, assessment_date),
    CONSTRAINT logical_pain_visits CHECK (pain_related_visits <= (primary_care_visits + specialist_visits + pain_clinic_visits + emergency_room_visits + urgent_care_visits))
);

-- Quality of life assessments table
CREATE TABLE quality_of_life (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    measurement_timing measurement_timing NOT NULL,
    
    -- SF-12 Health Survey components
    general_health INTEGER NOT NULL CHECK (general_health >= 1 AND general_health <= 5),
    physical_functioning INTEGER NOT NULL CHECK (physical_functioning >= 1 AND physical_functioning <= 3),
    role_physical INTEGER NOT NULL CHECK (role_physical >= 1 AND role_physical <= 5),
    bodily_pain INTEGER NOT NULL CHECK (bodily_pain >= 1 AND bodily_pain <= 6),
    vitality INTEGER NOT NULL CHECK (vitality >= 1 AND vitality <= 6),
    social_functioning INTEGER NOT NULL CHECK (social_functioning >= 1 AND social_functioning <= 5),
    role_emotional INTEGER NOT NULL CHECK (role_emotional >= 1 AND role_emotional <= 5),
    mental_health INTEGER NOT NULL CHECK (mental_health >= 1 AND mental_health <= 6),
    
    -- Additional QoL measures
    sleep_quality DECIMAL(3,1) NOT NULL CHECK (sleep_quality >= 0 AND sleep_quality <= 10),
    work_productivity DECIMAL(3,1) DEFAULT 5.0 CHECK (work_productivity >= 0 AND work_productivity <= 10),
    relationship_satisfaction DECIMAL(3,1) DEFAULT 5.0 CHECK (relationship_satisfaction >= 0 AND relationship_satisfaction <= 10),
    life_satisfaction DECIMAL(3,1) NOT NULL CHECK (life_satisfaction >= 0 AND life_satisfaction <= 10),
    
    -- Physical activity
    days_per_week_exercise INTEGER DEFAULT 0 CHECK (days_per_week_exercise >= 0 AND days_per_week_exercise <= 7),
    minutes_per_day_exercise INTEGER DEFAULT 0 CHECK (minutes_per_day_exercise >= 0),
    
    -- Computed component scores (simplified calculation)
    physical_component_score DECIMAL(5,2) GENERATED ALWAYS AS (
        (general_health + physical_functioning + role_physical + bodily_pain) / 4.0
    ) STORED,
    mental_component_score DECIMAL(5,2) GENERATED ALWAYS AS (
        (vitality + social_functioning + role_emotional + mental_health) / 4.0
    ) STORED,
    
    -- Assessment metadata
    assessor_id VARCHAR(50),
    data_quality data_quality_level NOT NULL DEFAULT 'complete',
    notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    version INTEGER DEFAULT 1,
    
    -- Constraints
    CONSTRAINT unique_patient_qol_assessment UNIQUE (patient_id, measurement_timing, assessment_date)
);

-- ============================================================================
-- Create Patient-Reported Outcomes Tables
-- ============================================================================

-- Weekly symptom tracking table
CREATE TABLE weekly_symptom_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(50) NOT NULL,
    report_date TIMESTAMP WITH TIME ZONE NOT NULL,
    week_number INTEGER NOT NULL CHECK (week_number >= 1),
    
    -- Symptom tracking
    average_pain_week DECIMAL(3,1) NOT NULL CHECK (average_pain_week >= 0 AND average_pain_week <= 10),
    worst_pain_week DECIMAL(3,1) NOT NULL CHECK (worst_pain_week >= 0 AND worst_pain_week <= 10),
    pain_free_days INTEGER NOT NULL CHECK (pain_free_days >= 0 AND pain_free_days <= 7),
    
    -- Functional status
    activity_limitation_days INTEGER NOT NULL CHECK (activity_limitation_days >= 0 AND activity_limitation_days <= 7),
    missed_work_days INTEGER DEFAULT 0 CHECK (missed_work_days >= 0 AND missed_work_days <= 7),
    
    -- Symptom burden
    fatigue_level DECIMAL(3,1) DEFAULT 5.0 CHECK (fatigue_level >= 0 AND fatigue_level <= 10),
    mood_rating DECIMAL(3,1) DEFAULT 5.0 CHECK (mood_rating >= 0 AND mood_rating <= 10),
    anxiety_level DECIMAL(3,1) DEFAULT 5.0 CHECK (anxiety_level >= 0 AND anxiety_level <= 10),
    
    -- Treatment response
    treatment_helpfulness DECIMAL(3,1) DEFAULT 5.0 CHECK (treatment_helpfulness >= 0 AND treatment_helpfulness <= 10),
    side_effects_this_week TEXT[] DEFAULT '{}',
    
    -- Global impression (1=Very much improved, 4=No change, 7=Very much worse)
    global_improvement INTEGER NOT NULL CHECK (global_improvement >= 1 AND global_improvement <= 7),
    
    -- Assessment metadata
    data_source VARCHAR(50) DEFAULT 'patient_app',
    data_quality data_quality_level NOT NULL DEFAULT 'complete',
    notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    
    -- Constraints
    CONSTRAINT unique_patient_week UNIQUE (patient_id, week_number),
    CONSTRAINT logical_pain_week CHECK (worst_pain_week >= average_pain_week)
);

-- Treatment satisfaction assessments table
CREATE TABLE treatment_satisfaction (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(50) NOT NULL,
    assessment_date TIMESTAMP WITH TIME ZONE NOT NULL,
    measurement_timing measurement_timing NOT NULL,
    
    -- Overall satisfaction
    overall_satisfaction DECIMAL(3,1) NOT NULL CHECK (overall_satisfaction >= 0 AND overall_satisfaction <= 10),
    would_recommend BOOLEAN NOT NULL,
    would_continue BOOLEAN NOT NULL,
    
    -- Specific satisfaction domains
    pain_relief_satisfaction DECIMAL(3,1) NOT NULL CHECK (pain_relief_satisfaction >= 0 AND pain_relief_satisfaction <= 10),
    function_improvement_satisfaction DECIMAL(3,1) NOT NULL CHECK (function_improvement_satisfaction >= 0 AND function_improvement_satisfaction <= 10),
    side_effect_tolerance DECIMAL(3,1) NOT NULL CHECK (side_effect_tolerance >= 0 AND side_effect_tolerance <= 10),
    
    -- Treatment burden
    treatment_burden DECIMAL(3,1) DEFAULT 5.0 CHECK (treatment_burden >= 0 AND treatment_burden <= 10),
    convenience DECIMAL(3,1) DEFAULT 5.0 CHECK (convenience >= 0 AND convenience <= 10),
    
    -- Communication and care
    provider_communication DECIMAL(3,1) DEFAULT 8.0 CHECK (provider_communication >= 0 AND provider_communication <= 10),
    care_coordination DECIMAL(3,1) DEFAULT 8.0 CHECK (care_coordination >= 0 AND care_coordination <= 10),
    
    -- Expectations
    expectations_met DECIMAL(3,1) NOT NULL CHECK (expectations_met >= 0 AND expectations_met <= 10),
    
    -- Open feedback
    most_helpful_aspect TEXT,
    least_helpful_aspect TEXT,
    suggestions_for_improvement TEXT,
    
    -- Assessment metadata
    assessor_id VARCHAR(50),
    data_quality data_quality_level NOT NULL DEFAULT 'complete',
    notes TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    version INTEGER DEFAULT 1,
    
    -- Constraints
    CONSTRAINT unique_patient_satisfaction_assessment UNIQUE (patient_id, measurement_timing, assessment_date)
);

-- ============================================================================
-- Create Assessment Management Tables
-- ============================================================================

-- Assessment schedules table
CREATE TABLE assessment_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(50) NOT NULL UNIQUE,
    baseline_date TIMESTAMP WITH TIME ZONE NOT NULL,
    study_duration_weeks INTEGER DEFAULT 52 CHECK (study_duration_weeks > 0),
    
    -- Schedule details stored as JSONB for flexibility
    scheduled_assessments JSONB NOT NULL DEFAULT '[]',
    
    -- Compliance tracking
    total_scheduled INTEGER DEFAULT 0,
    total_completed INTEGER DEFAULT 0,
    compliance_rate DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN total_scheduled > 0 THEN (total_completed::DECIMAL / total_scheduled::DECIMAL) * 100.0
            ELSE 0.0
        END
    ) STORED,
    
    -- Status tracking
    active BOOLEAN DEFAULT TRUE,
    completion_status VARCHAR(20) DEFAULT 'active',
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    version INTEGER DEFAULT 1
);

-- Outcome change calculations table (for caching computed changes)
CREATE TABLE outcome_changes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(50) NOT NULL,
    baseline_date TIMESTAMP WITH TIME ZONE NOT NULL,
    comparison_date TIMESTAMP WITH TIME ZONE NOT NULL,
    follow_up_duration_days INTEGER NOT NULL,
    
    -- Pain score changes
    pain_baseline DECIMAL(3,1),
    pain_current DECIMAL(3,1),
    pain_change DECIMAL(4,1),
    pain_percent_change DECIMAL(6,2),
    pain_clinically_significant BOOLEAN,
    
    -- WOMAC changes
    womac_baseline DECIMAL(5,2),
    womac_current DECIMAL(5,2),
    womac_change DECIMAL(6,2),
    womac_percent_change DECIMAL(6,2),
    womac_clinically_significant BOOLEAN,
    
    -- ODI changes
    odi_baseline DECIMAL(5,2),
    odi_current DECIMAL(5,2),
    odi_change DECIMAL(6,2),
    odi_percent_change DECIMAL(6,2),
    odi_clinically_significant BOOLEAN,
    
    -- QOL changes
    qol_baseline DECIMAL(3,1),
    qol_current DECIMAL(3,1),
    qol_change DECIMAL(4,1),
    qol_percent_change DECIMAL(6,2),
    qol_clinically_significant BOOLEAN,
    
    -- Overall clinical response
    clinical_response_category VARCHAR(50),
    significant_improvements INTEGER DEFAULT 0,
    total_outcomes_assessed INTEGER DEFAULT 0,
    response_rate DECIMAL(5,2),
    
    -- Audit fields
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    calculation_version VARCHAR(10) DEFAULT '1.0',
    
    -- Constraints
    CONSTRAINT unique_patient_comparison UNIQUE (patient_id, baseline_date, comparison_date)
);

-- ============================================================================
-- Create Indexes for Performance
-- ============================================================================

-- Primary outcome indexes
CREATE INDEX idx_pain_assessments_patient_date ON pain_assessments(patient_id, assessment_date);
CREATE INDEX idx_pain_assessments_timing ON pain_assessments(measurement_timing);
CREATE INDEX idx_pain_assessments_quality ON pain_assessments(data_quality);

CREATE INDEX idx_womac_assessments_patient_date ON womac_assessments(patient_id, assessment_date);
CREATE INDEX idx_womac_assessments_timing ON womac_assessments(measurement_timing);
CREATE INDEX idx_womac_total_score ON womac_assessments(total_score);

CREATE INDEX idx_odi_assessments_patient_date ON odi_assessments(patient_id, assessment_date);
CREATE INDEX idx_odi_assessments_timing ON odi_assessments(measurement_timing);
CREATE INDEX idx_odi_percentage ON odi_assessments(percentage_disability);

-- Secondary outcome indexes
CREATE INDEX idx_medication_usage_patient_date ON medication_usage(patient_id, assessment_date);
CREATE INDEX idx_medication_adherence ON medication_usage(adherence_percentage);

CREATE INDEX idx_healthcare_utilization_patient_date ON healthcare_utilization(patient_id, assessment_date);
CREATE INDEX idx_healthcare_total_visits ON healthcare_utilization(total_visits);

CREATE INDEX idx_quality_of_life_patient_date ON quality_of_life(patient_id, assessment_date);
CREATE INDEX idx_qol_life_satisfaction ON quality_of_life(life_satisfaction);

-- Patient-reported outcome indexes
CREATE INDEX idx_weekly_symptoms_patient_week ON weekly_symptom_tracking(patient_id, week_number);
CREATE INDEX idx_weekly_symptoms_date ON weekly_symptom_tracking(report_date);

CREATE INDEX idx_treatment_satisfaction_patient_date ON treatment_satisfaction(patient_id, assessment_date);
CREATE INDEX idx_satisfaction_overall ON treatment_satisfaction(overall_satisfaction);

-- Management table indexes
CREATE INDEX idx_assessment_schedules_patient ON assessment_schedules(patient_id);
CREATE INDEX idx_assessment_schedules_baseline ON assessment_schedules(baseline_date);
CREATE INDEX idx_compliance_rate ON assessment_schedules(compliance_rate);

CREATE INDEX idx_outcome_changes_patient ON outcome_changes(patient_id);
CREATE INDEX idx_outcome_changes_dates ON outcome_changes(baseline_date, comparison_date);

-- ============================================================================
-- Create Views for Common Queries
-- ============================================================================

-- View for latest assessments per patient
CREATE VIEW latest_assessments AS
SELECT DISTINCT ON (p.patient_id)
    p.patient_id,
    p.assessment_date,
    p.measurement_timing,
    p.average_pain_24h as latest_pain_score,
    w.normalized_score as latest_womac_score,
    o.percentage_disability as latest_odi_score,
    q.life_satisfaction as latest_qol_score
FROM pain_assessments p
LEFT JOIN womac_assessments w ON p.patient_id = w.patient_id AND p.assessment_date = w.assessment_date
LEFT JOIN odi_assessments o ON p.patient_id = o.patient_id AND p.assessment_date = o.assessment_date  
LEFT JOIN quality_of_life q ON p.patient_id = q.patient_id AND p.assessment_date = q.assessment_date
ORDER BY p.patient_id, p.assessment_date DESC;

-- View for baseline assessments
CREATE VIEW baseline_assessments AS
SELECT 
    p.patient_id,
    p.assessment_date as baseline_date,
    p.average_pain_24h as baseline_pain_score,
    w.normalized_score as baseline_womac_score,
    o.percentage_disability as baseline_odi_score,
    q.life_satisfaction as baseline_qol_score
FROM pain_assessments p
LEFT JOIN womac_assessments w ON p.patient_id = w.patient_id AND p.assessment_date = w.assessment_date
LEFT JOIN odi_assessments o ON p.patient_id = o.patient_id AND p.assessment_date = o.assessment_date
LEFT JOIN quality_of_life q ON p.patient_id = q.patient_id AND p.assessment_date = q.assessment_date
WHERE p.measurement_timing = 'baseline';

-- View for data quality summary
CREATE VIEW data_quality_summary AS
SELECT 
    'pain_assessments' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE data_quality = 'complete') as complete_records,
    COUNT(*) FILTER (WHERE data_quality = 'adequate') as adequate_records,
    COUNT(*) FILTER (WHERE data_quality = 'minimal') as minimal_records,
    COUNT(*) FILTER (WHERE data_quality = 'insufficient') as insufficient_records,
    ROUND(COUNT(*) FILTER (WHERE data_quality IN ('complete', 'adequate'))::DECIMAL / COUNT(*) * 100, 2) as acceptable_quality_rate
FROM pain_assessments
UNION ALL
SELECT 
    'womac_assessments' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE data_quality = 'complete') as complete_records,
    COUNT(*) FILTER (WHERE data_quality = 'adequate') as adequate_records,
    COUNT(*) FILTER (WHERE data_quality = 'minimal') as minimal_records,
    COUNT(*) FILTER (WHERE data_quality = 'insufficient') as insufficient_records,
    ROUND(COUNT(*) FILTER (WHERE data_quality IN ('complete', 'adequate'))::DECIMAL / COUNT(*) * 100, 2) as acceptable_quality_rate
FROM womac_assessments;

-- ============================================================================
-- Create Triggers for Automatic Updates
-- ============================================================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$ language 'plpgsql';

-- Apply update triggers to all main tables
CREATE TRIGGER update_pain_assessments_updated_at BEFORE UPDATE ON pain_assessments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_womac_assessments_updated_at BEFORE UPDATE ON womac_assessments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_odi_assessments_updated_at BEFORE UPDATE ON odi_assessments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_medication_usage_updated_at BEFORE UPDATE ON medication_usage FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_healthcare_utilization_updated_at BEFORE UPDATE ON healthcare_utilization FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_quality_of_life_updated_at BEFORE UPDATE ON quality_of_life FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_weekly_symptom_tracking_updated_at BEFORE UPDATE ON weekly_symptom_tracking FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_treatment_satisfaction_updated_at BEFORE UPDATE ON treatment_satisfaction FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assessment_schedules_updated_at BEFORE UPDATE ON assessment_schedules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Insert Reference Data
-- ============================================================================

-- Insert sample data quality standards
INSERT INTO assessment_schedules (patient_id, baseline_date, study_duration_weeks, scheduled_assessments) VALUES
('DEMO_PATIENT_001', '2024-01-01 09:00:00+00', 52, '[
    {"timing": "baseline", "scheduled_date": "2024-01-01", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life"]},
    {"timing": "week_4", "scheduled_date": "2024-01-29", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage"]},
    {"timing": "week_12", "scheduled_date": "2024-03-25", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life", "treatment_satisfaction"]},
    {"timing": "week_24", "scheduled_date": "2024-06-17", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life", "treatment_satisfaction"]}
]');

-- ============================================================================
-- Grant Permissions (Adjust based on your user roles)
-- ============================================================================

-- Grant permissions to application user (replace 'abena_app_user' with actual username)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA clinical_outcomes TO abena_app_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA clinical_outcomes TO abena_app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA clinical_outcomes TO abena_app_user;

-- Grant read-only permissions to reporting user (replace 'abena_report_user' with actual username)
-- GRANT SELECT ON ALL TABLES IN SCHEMA clinical_outcomes TO abena_report_user;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify schema creation
SELECT schemaname, tablename, tableowner 
FROM pg_tables 
WHERE schemaname = 'clinical_outcomes' 
ORDER BY tablename;

-- Verify indexes
SELECT schemaname, tablename, indexname, indexdef 
FROM pg_indexes 
WHERE schemaname = 'clinical_outcomes' 
ORDER BY tablename, indexname;

-- Verify constraints
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type,
    cc.check_clause
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.check_constraints cc ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'clinical_outcomes'
ORDER BY tc.table_name, tc.constraint_type;

-- Test data insertion (run after schema creation)
/*
INSERT INTO clinical_outcomes.pain_assessments (
    patient_id, assessment_date, measurement_timing,
    current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference
) VALUES (
    'TEST_PATIENT_001', CURRENT_TIMESTAMP, 'baseline',
    7.5, 7.0, 9.0, 5.0, 8.0
);

SELECT * FROM clinical_outcomes.pain_assessments WHERE patient_id = 'TEST_PATIENT_001';
*/

-- ============================================================================
-- Migration Complete
-- ============================================================================

-- Reset search path
SET search_path TO public; 