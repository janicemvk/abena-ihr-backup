--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.9

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: clinical_outcomes; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA clinical_outcomes;


ALTER SCHEMA clinical_outcomes OWNER TO postgres;

--
-- Name: assessment_status; Type: TYPE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TYPE clinical_outcomes.assessment_status AS ENUM (
    'scheduled',
    'completed',
    'overdue',
    'cancelled'
);


ALTER TYPE clinical_outcomes.assessment_status OWNER TO postgres;

--
-- Name: data_quality_level; Type: TYPE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TYPE clinical_outcomes.data_quality_level AS ENUM (
    'complete',
    'adequate',
    'minimal',
    'insufficient'
);


ALTER TYPE clinical_outcomes.data_quality_level OWNER TO postgres;

--
-- Name: measurement_timing; Type: TYPE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TYPE clinical_outcomes.measurement_timing AS ENUM (
    'baseline',
    'week_2',
    'week_4',
    'week_8',
    'week_12',
    'week_24',
    'week_52',
    'unscheduled'
);


ALTER TYPE clinical_outcomes.measurement_timing OWNER TO postgres;

--
-- Name: outcome_type; Type: TYPE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TYPE clinical_outcomes.outcome_type AS ENUM (
    'primary',
    'secondary',
    'patient_reported',
    'safety',
    'economic'
);


ALTER TYPE clinical_outcomes.outcome_type OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: assessment_schedules; Type: TABLE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TABLE clinical_outcomes.assessment_schedules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id character varying(50) NOT NULL,
    baseline_date timestamp with time zone NOT NULL,
    study_duration_weeks integer DEFAULT 52,
    scheduled_assessments jsonb DEFAULT '[]'::jsonb NOT NULL,
    total_scheduled integer DEFAULT 0,
    total_completed integer DEFAULT 0,
    compliance_rate numeric(5,2) GENERATED ALWAYS AS (
CASE
    WHEN (total_scheduled > 0) THEN (((total_completed)::numeric / (total_scheduled)::numeric) * 100.0)
    ELSE 0.0
END) STORED,
    active boolean DEFAULT true,
    completion_status character varying(20) DEFAULT 'active'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(50),
    version integer DEFAULT 1,
    CONSTRAINT assessment_schedules_study_duration_weeks_check CHECK ((study_duration_weeks > 0))
);


ALTER TABLE clinical_outcomes.assessment_schedules OWNER TO postgres;

--
-- Name: odi_assessments; Type: TABLE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TABLE clinical_outcomes.odi_assessments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id character varying(50) NOT NULL,
    assessment_date timestamp with time zone NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    pain_intensity integer NOT NULL,
    personal_care integer NOT NULL,
    lifting integer NOT NULL,
    walking integer NOT NULL,
    sitting integer NOT NULL,
    standing integer NOT NULL,
    sleeping integer NOT NULL,
    sex_life integer NOT NULL,
    social_life integer NOT NULL,
    traveling integer NOT NULL,
    total_score integer GENERATED ALWAYS AS ((((((((((pain_intensity + personal_care) + lifting) + walking) + sitting) + standing) + sleeping) + sex_life) + social_life) + traveling)) STORED,
    percentage_disability numeric(5,2) GENERATED ALWAYS AS (((((((((((((pain_intensity + personal_care) + lifting) + walking) + sitting) + standing) + sleeping) + sex_life) + social_life) + traveling))::numeric / 50.0) * 100.0)) STORED,
    assessor_id character varying(50),
    data_quality clinical_outcomes.data_quality_level DEFAULT 'complete'::clinical_outcomes.data_quality_level NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(50),
    version integer DEFAULT 1,
    CONSTRAINT odi_assessments_lifting_check CHECK (((lifting >= 0) AND (lifting <= 5))),
    CONSTRAINT odi_assessments_pain_intensity_check CHECK (((pain_intensity >= 0) AND (pain_intensity <= 5))),
    CONSTRAINT odi_assessments_personal_care_check CHECK (((personal_care >= 0) AND (personal_care <= 5))),
    CONSTRAINT odi_assessments_sex_life_check CHECK (((sex_life >= 0) AND (sex_life <= 5))),
    CONSTRAINT odi_assessments_sitting_check CHECK (((sitting >= 0) AND (sitting <= 5))),
    CONSTRAINT odi_assessments_sleeping_check CHECK (((sleeping >= 0) AND (sleeping <= 5))),
    CONSTRAINT odi_assessments_social_life_check CHECK (((social_life >= 0) AND (social_life <= 5))),
    CONSTRAINT odi_assessments_standing_check CHECK (((standing >= 0) AND (standing <= 5))),
    CONSTRAINT odi_assessments_traveling_check CHECK (((traveling >= 0) AND (traveling <= 5))),
    CONSTRAINT odi_assessments_walking_check CHECK (((walking >= 0) AND (walking <= 5)))
);


ALTER TABLE clinical_outcomes.odi_assessments OWNER TO postgres;

--
-- Name: pain_assessments; Type: TABLE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TABLE clinical_outcomes.pain_assessments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id character varying(50) NOT NULL,
    assessment_date timestamp with time zone NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    current_pain numeric(3,1) NOT NULL,
    average_pain_24h numeric(3,1) NOT NULL,
    worst_pain_24h numeric(3,1) NOT NULL,
    least_pain_24h numeric(3,1) NOT NULL,
    pain_interference numeric(3,1) NOT NULL,
    pain_at_rest numeric(3,1),
    pain_with_movement numeric(3,1),
    pain_with_exercise numeric(3,1),
    pain_locations text[] DEFAULT '{}'::text[],
    pain_quality text[] DEFAULT '{}'::text[],
    assessment_method character varying(50) DEFAULT 'self_report'::character varying,
    assessor_type character varying(50) DEFAULT 'patient'::character varying,
    assessor_id character varying(50),
    data_quality clinical_outcomes.data_quality_level DEFAULT 'complete'::clinical_outcomes.data_quality_level NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(50),
    version integer DEFAULT 1,
    CONSTRAINT pain_assessments_average_pain_24h_check CHECK (((average_pain_24h >= (0)::numeric) AND (average_pain_24h <= (10)::numeric))),
    CONSTRAINT pain_assessments_current_pain_check CHECK (((current_pain >= (0)::numeric) AND (current_pain <= (10)::numeric))),
    CONSTRAINT pain_assessments_least_pain_24h_check CHECK (((least_pain_24h >= (0)::numeric) AND (least_pain_24h <= (10)::numeric))),
    CONSTRAINT pain_assessments_pain_at_rest_check CHECK (((pain_at_rest >= (0)::numeric) AND (pain_at_rest <= (10)::numeric))),
    CONSTRAINT pain_assessments_pain_interference_check CHECK (((pain_interference >= (0)::numeric) AND (pain_interference <= (10)::numeric))),
    CONSTRAINT pain_assessments_pain_with_exercise_check CHECK (((pain_with_exercise >= (0)::numeric) AND (pain_with_exercise <= (10)::numeric))),
    CONSTRAINT pain_assessments_pain_with_movement_check CHECK (((pain_with_movement >= (0)::numeric) AND (pain_with_movement <= (10)::numeric))),
    CONSTRAINT pain_assessments_worst_pain_24h_check CHECK (((worst_pain_24h >= (0)::numeric) AND (worst_pain_24h <= (10)::numeric))),
    CONSTRAINT valid_pain_progression CHECK (((worst_pain_24h >= average_pain_24h) AND (average_pain_24h >= least_pain_24h)))
);


ALTER TABLE clinical_outcomes.pain_assessments OWNER TO postgres;

--
-- Name: quality_of_life; Type: TABLE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TABLE clinical_outcomes.quality_of_life (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id character varying(50) NOT NULL,
    assessment_date timestamp with time zone NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    general_health integer NOT NULL,
    physical_functioning integer NOT NULL,
    role_physical integer NOT NULL,
    bodily_pain integer NOT NULL,
    vitality integer NOT NULL,
    social_functioning integer NOT NULL,
    role_emotional integer NOT NULL,
    mental_health integer NOT NULL,
    sleep_quality numeric(3,1) NOT NULL,
    work_productivity numeric(3,1) DEFAULT 5.0,
    relationship_satisfaction numeric(3,1) DEFAULT 5.0,
    life_satisfaction numeric(3,1) NOT NULL,
    days_per_week_exercise integer DEFAULT 0,
    minutes_per_day_exercise integer DEFAULT 0,
    physical_component_score numeric(5,2) GENERATED ALWAYS AS ((((((general_health + physical_functioning) + role_physical) + bodily_pain))::numeric / 4.0)) STORED,
    mental_component_score numeric(5,2) GENERATED ALWAYS AS ((((((vitality + social_functioning) + role_emotional) + mental_health))::numeric / 4.0)) STORED,
    assessor_id character varying(50),
    data_quality clinical_outcomes.data_quality_level DEFAULT 'complete'::clinical_outcomes.data_quality_level NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(50),
    version integer DEFAULT 1,
    CONSTRAINT quality_of_life_bodily_pain_check CHECK (((bodily_pain >= 1) AND (bodily_pain <= 6))),
    CONSTRAINT quality_of_life_days_per_week_exercise_check CHECK (((days_per_week_exercise >= 0) AND (days_per_week_exercise <= 7))),
    CONSTRAINT quality_of_life_general_health_check CHECK (((general_health >= 1) AND (general_health <= 5))),
    CONSTRAINT quality_of_life_life_satisfaction_check CHECK (((life_satisfaction >= (0)::numeric) AND (life_satisfaction <= (10)::numeric))),
    CONSTRAINT quality_of_life_mental_health_check CHECK (((mental_health >= 1) AND (mental_health <= 6))),
    CONSTRAINT quality_of_life_minutes_per_day_exercise_check CHECK ((minutes_per_day_exercise >= 0)),
    CONSTRAINT quality_of_life_physical_functioning_check CHECK (((physical_functioning >= 1) AND (physical_functioning <= 3))),
    CONSTRAINT quality_of_life_relationship_satisfaction_check CHECK (((relationship_satisfaction >= (0)::numeric) AND (relationship_satisfaction <= (10)::numeric))),
    CONSTRAINT quality_of_life_role_emotional_check CHECK (((role_emotional >= 1) AND (role_emotional <= 5))),
    CONSTRAINT quality_of_life_role_physical_check CHECK (((role_physical >= 1) AND (role_physical <= 5))),
    CONSTRAINT quality_of_life_sleep_quality_check CHECK (((sleep_quality >= (0)::numeric) AND (sleep_quality <= (10)::numeric))),
    CONSTRAINT quality_of_life_social_functioning_check CHECK (((social_functioning >= 1) AND (social_functioning <= 5))),
    CONSTRAINT quality_of_life_vitality_check CHECK (((vitality >= 1) AND (vitality <= 6))),
    CONSTRAINT quality_of_life_work_productivity_check CHECK (((work_productivity >= (0)::numeric) AND (work_productivity <= (10)::numeric)))
);


ALTER TABLE clinical_outcomes.quality_of_life OWNER TO postgres;

--
-- Name: womac_assessments; Type: TABLE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TABLE clinical_outcomes.womac_assessments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id character varying(50) NOT NULL,
    assessment_date timestamp with time zone NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    pain_walking integer NOT NULL,
    pain_stairs integer NOT NULL,
    pain_night_bed integer NOT NULL,
    pain_sitting integer NOT NULL,
    pain_standing integer NOT NULL,
    stiffness_waking integer NOT NULL,
    stiffness_later_day integer NOT NULL,
    function_stairs_down integer NOT NULL,
    function_stairs_up integer NOT NULL,
    function_rising_sitting integer NOT NULL,
    function_standing integer NOT NULL,
    function_bending integer NOT NULL,
    function_walking_flat integer NOT NULL,
    function_getting_in_out_car integer NOT NULL,
    function_shopping integer NOT NULL,
    function_socks integer NOT NULL,
    function_rising_bed integer NOT NULL,
    function_socks_off integer NOT NULL,
    function_lying_bed integer NOT NULL,
    function_bath_shower integer NOT NULL,
    function_sitting integer NOT NULL,
    function_toilet integer NOT NULL,
    function_heavy_domestic integer NOT NULL,
    function_light_domestic integer NOT NULL,
    pain_score integer GENERATED ALWAYS AS (((((pain_walking + pain_stairs) + pain_night_bed) + pain_sitting) + pain_standing)) STORED,
    stiffness_score integer GENERATED ALWAYS AS ((stiffness_waking + stiffness_later_day)) STORED,
    function_score integer GENERATED ALWAYS AS (((((((((((((((((function_stairs_down + function_stairs_up) + function_rising_sitting) + function_standing) + function_bending) + function_walking_flat) + function_getting_in_out_car) + function_shopping) + function_socks) + function_rising_bed) + function_socks_off) + function_lying_bed) + function_bath_shower) + function_sitting) + function_toilet) + function_heavy_domestic) + function_light_domestic)) STORED,
    total_score integer GENERATED ALWAYS AS ((((((((((((((((((((((((pain_walking + pain_stairs) + pain_night_bed) + pain_sitting) + pain_standing) + stiffness_waking) + stiffness_later_day) + function_stairs_down) + function_stairs_up) + function_rising_sitting) + function_standing) + function_bending) + function_walking_flat) + function_getting_in_out_car) + function_shopping) + function_socks) + function_rising_bed) + function_socks_off) + function_lying_bed) + function_bath_shower) + function_sitting) + function_toilet) + function_heavy_domestic) + function_light_domestic)) STORED,
    normalized_score numeric(5,2) GENERATED ALWAYS AS (((((((((((((((((((((((((((pain_walking + pain_stairs) + pain_night_bed) + pain_sitting) + pain_standing) + stiffness_waking) + stiffness_later_day) + function_stairs_down) + function_stairs_up) + function_rising_sitting) + function_standing) + function_bending) + function_walking_flat) + function_getting_in_out_car) + function_shopping) + function_socks) + function_rising_bed) + function_socks_off) + function_lying_bed) + function_bath_shower) + function_sitting) + function_toilet) + function_heavy_domestic) + function_light_domestic))::numeric / 96.0) * 100.0)) STORED,
    assessor_id character varying(50),
    data_quality clinical_outcomes.data_quality_level DEFAULT 'complete'::clinical_outcomes.data_quality_level NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(50),
    version integer DEFAULT 1,
    CONSTRAINT womac_assessments_function_bath_shower_check CHECK (((function_bath_shower >= 0) AND (function_bath_shower <= 4))),
    CONSTRAINT womac_assessments_function_bending_check CHECK (((function_bending >= 0) AND (function_bending <= 4))),
    CONSTRAINT womac_assessments_function_getting_in_out_car_check CHECK (((function_getting_in_out_car >= 0) AND (function_getting_in_out_car <= 4))),
    CONSTRAINT womac_assessments_function_heavy_domestic_check CHECK (((function_heavy_domestic >= 0) AND (function_heavy_domestic <= 4))),
    CONSTRAINT womac_assessments_function_light_domestic_check CHECK (((function_light_domestic >= 0) AND (function_light_domestic <= 4))),
    CONSTRAINT womac_assessments_function_lying_bed_check CHECK (((function_lying_bed >= 0) AND (function_lying_bed <= 4))),
    CONSTRAINT womac_assessments_function_rising_bed_check CHECK (((function_rising_bed >= 0) AND (function_rising_bed <= 4))),
    CONSTRAINT womac_assessments_function_rising_sitting_check CHECK (((function_rising_sitting >= 0) AND (function_rising_sitting <= 4))),
    CONSTRAINT womac_assessments_function_shopping_check CHECK (((function_shopping >= 0) AND (function_shopping <= 4))),
    CONSTRAINT womac_assessments_function_sitting_check CHECK (((function_sitting >= 0) AND (function_sitting <= 4))),
    CONSTRAINT womac_assessments_function_socks_check CHECK (((function_socks >= 0) AND (function_socks <= 4))),
    CONSTRAINT womac_assessments_function_socks_off_check CHECK (((function_socks_off >= 0) AND (function_socks_off <= 4))),
    CONSTRAINT womac_assessments_function_stairs_down_check CHECK (((function_stairs_down >= 0) AND (function_stairs_down <= 4))),
    CONSTRAINT womac_assessments_function_stairs_up_check CHECK (((function_stairs_up >= 0) AND (function_stairs_up <= 4))),
    CONSTRAINT womac_assessments_function_standing_check CHECK (((function_standing >= 0) AND (function_standing <= 4))),
    CONSTRAINT womac_assessments_function_toilet_check CHECK (((function_toilet >= 0) AND (function_toilet <= 4))),
    CONSTRAINT womac_assessments_function_walking_flat_check CHECK (((function_walking_flat >= 0) AND (function_walking_flat <= 4))),
    CONSTRAINT womac_assessments_pain_night_bed_check CHECK (((pain_night_bed >= 0) AND (pain_night_bed <= 4))),
    CONSTRAINT womac_assessments_pain_sitting_check CHECK (((pain_sitting >= 0) AND (pain_sitting <= 4))),
    CONSTRAINT womac_assessments_pain_stairs_check CHECK (((pain_stairs >= 0) AND (pain_stairs <= 4))),
    CONSTRAINT womac_assessments_pain_standing_check CHECK (((pain_standing >= 0) AND (pain_standing <= 4))),
    CONSTRAINT womac_assessments_pain_walking_check CHECK (((pain_walking >= 0) AND (pain_walking <= 4))),
    CONSTRAINT womac_assessments_stiffness_later_day_check CHECK (((stiffness_later_day >= 0) AND (stiffness_later_day <= 4))),
    CONSTRAINT womac_assessments_stiffness_waking_check CHECK (((stiffness_waking >= 0) AND (stiffness_waking <= 4)))
);


ALTER TABLE clinical_outcomes.womac_assessments OWNER TO postgres;

--
-- Name: baseline_assessments; Type: VIEW; Schema: clinical_outcomes; Owner: postgres
--

CREATE VIEW clinical_outcomes.baseline_assessments AS
 SELECT p.patient_id,
    p.assessment_date AS baseline_date,
    p.average_pain_24h AS baseline_pain_score,
    w.normalized_score AS baseline_womac_score,
    o.percentage_disability AS baseline_odi_score,
    q.life_satisfaction AS baseline_qol_score
   FROM (((clinical_outcomes.pain_assessments p
     LEFT JOIN clinical_outcomes.womac_assessments w ON ((((p.patient_id)::text = (w.patient_id)::text) AND (p.assessment_date = w.assessment_date))))
     LEFT JOIN clinical_outcomes.odi_assessments o ON ((((p.patient_id)::text = (o.patient_id)::text) AND (p.assessment_date = o.assessment_date))))
     LEFT JOIN clinical_outcomes.quality_of_life q ON ((((p.patient_id)::text = (q.patient_id)::text) AND (p.assessment_date = q.assessment_date))))
  WHERE (p.measurement_timing = 'baseline'::clinical_outcomes.measurement_timing);


ALTER VIEW clinical_outcomes.baseline_assessments OWNER TO postgres;

--
-- Name: data_quality_summary; Type: VIEW; Schema: clinical_outcomes; Owner: postgres
--

CREATE VIEW clinical_outcomes.data_quality_summary AS
 SELECT 'pain_assessments'::text AS table_name,
    count(*) AS total_records,
    count(*) FILTER (WHERE (pain_assessments.data_quality = 'complete'::clinical_outcomes.data_quality_level)) AS complete_records,
    count(*) FILTER (WHERE (pain_assessments.data_quality = 'adequate'::clinical_outcomes.data_quality_level)) AS adequate_records,
    count(*) FILTER (WHERE (pain_assessments.data_quality = 'minimal'::clinical_outcomes.data_quality_level)) AS minimal_records,
    count(*) FILTER (WHERE (pain_assessments.data_quality = 'insufficient'::clinical_outcomes.data_quality_level)) AS insufficient_records,
    round((((count(*) FILTER (WHERE (pain_assessments.data_quality = ANY (ARRAY['complete'::clinical_outcomes.data_quality_level, 'adequate'::clinical_outcomes.data_quality_level]))))::numeric / (count(*))::numeric) * (100)::numeric), 2) AS acceptable_quality_rate
   FROM clinical_outcomes.pain_assessments
UNION ALL
 SELECT 'womac_assessments'::text AS table_name,
    count(*) AS total_records,
    count(*) FILTER (WHERE (womac_assessments.data_quality = 'complete'::clinical_outcomes.data_quality_level)) AS complete_records,
    count(*) FILTER (WHERE (womac_assessments.data_quality = 'adequate'::clinical_outcomes.data_quality_level)) AS adequate_records,
    count(*) FILTER (WHERE (womac_assessments.data_quality = 'minimal'::clinical_outcomes.data_quality_level)) AS minimal_records,
    count(*) FILTER (WHERE (womac_assessments.data_quality = 'insufficient'::clinical_outcomes.data_quality_level)) AS insufficient_records,
    round((((count(*) FILTER (WHERE (womac_assessments.data_quality = ANY (ARRAY['complete'::clinical_outcomes.data_quality_level, 'adequate'::clinical_outcomes.data_quality_level]))))::numeric / (count(*))::numeric) * (100)::numeric), 2) AS acceptable_quality_rate
   FROM clinical_outcomes.womac_assessments;


ALTER VIEW clinical_outcomes.data_quality_summary OWNER TO postgres;

--
-- Name: healthcare_utilization; Type: TABLE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TABLE clinical_outcomes.healthcare_utilization (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id character varying(50) NOT NULL,
    assessment_date timestamp with time zone NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    assessment_period_days integer DEFAULT 30,
    primary_care_visits integer DEFAULT 0,
    specialist_visits integer DEFAULT 0,
    pain_clinic_visits integer DEFAULT 0,
    physical_therapy_visits integer DEFAULT 0,
    emergency_room_visits integer DEFAULT 0,
    urgent_care_visits integer DEFAULT 0,
    hospitalizations integer DEFAULT 0,
    hospital_days integer DEFAULT 0,
    imaging_studies integer DEFAULT 0,
    laboratory_tests integer DEFAULT 0,
    procedures integer DEFAULT 0,
    estimated_total_cost numeric(10,2),
    out_of_pocket_cost numeric(10,2),
    pain_related_visits integer DEFAULT 0,
    treatment_related_visits integer DEFAULT 0,
    total_visits integer GENERATED ALWAYS AS ((((((primary_care_visits + specialist_visits) + pain_clinic_visits) + physical_therapy_visits) + emergency_room_visits) + urgent_care_visits)) STORED,
    assessor_id character varying(50),
    data_quality clinical_outcomes.data_quality_level DEFAULT 'complete'::clinical_outcomes.data_quality_level NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(50),
    version integer DEFAULT 1,
    CONSTRAINT healthcare_utilization_assessment_period_days_check CHECK ((assessment_period_days > 0)),
    CONSTRAINT healthcare_utilization_emergency_room_visits_check CHECK ((emergency_room_visits >= 0)),
    CONSTRAINT healthcare_utilization_estimated_total_cost_check CHECK ((estimated_total_cost >= (0)::numeric)),
    CONSTRAINT healthcare_utilization_hospital_days_check CHECK ((hospital_days >= 0)),
    CONSTRAINT healthcare_utilization_hospitalizations_check CHECK ((hospitalizations >= 0)),
    CONSTRAINT healthcare_utilization_imaging_studies_check CHECK ((imaging_studies >= 0)),
    CONSTRAINT healthcare_utilization_laboratory_tests_check CHECK ((laboratory_tests >= 0)),
    CONSTRAINT healthcare_utilization_out_of_pocket_cost_check CHECK ((out_of_pocket_cost >= (0)::numeric)),
    CONSTRAINT healthcare_utilization_pain_clinic_visits_check CHECK ((pain_clinic_visits >= 0)),
    CONSTRAINT healthcare_utilization_pain_related_visits_check CHECK ((pain_related_visits >= 0)),
    CONSTRAINT healthcare_utilization_physical_therapy_visits_check CHECK ((physical_therapy_visits >= 0)),
    CONSTRAINT healthcare_utilization_primary_care_visits_check CHECK ((primary_care_visits >= 0)),
    CONSTRAINT healthcare_utilization_procedures_check CHECK ((procedures >= 0)),
    CONSTRAINT healthcare_utilization_specialist_visits_check CHECK ((specialist_visits >= 0)),
    CONSTRAINT healthcare_utilization_treatment_related_visits_check CHECK ((treatment_related_visits >= 0)),
    CONSTRAINT healthcare_utilization_urgent_care_visits_check CHECK ((urgent_care_visits >= 0)),
    CONSTRAINT logical_pain_visits CHECK ((pain_related_visits <= ((((primary_care_visits + specialist_visits) + pain_clinic_visits) + emergency_room_visits) + urgent_care_visits)))
);


ALTER TABLE clinical_outcomes.healthcare_utilization OWNER TO postgres;

--
-- Name: latest_assessments; Type: VIEW; Schema: clinical_outcomes; Owner: postgres
--

CREATE VIEW clinical_outcomes.latest_assessments AS
 SELECT DISTINCT ON (p.patient_id) p.patient_id,
    p.assessment_date,
    p.measurement_timing,
    p.average_pain_24h AS latest_pain_score,
    w.normalized_score AS latest_womac_score,
    o.percentage_disability AS latest_odi_score,
    q.life_satisfaction AS latest_qol_score
   FROM (((clinical_outcomes.pain_assessments p
     LEFT JOIN clinical_outcomes.womac_assessments w ON ((((p.patient_id)::text = (w.patient_id)::text) AND (p.assessment_date = w.assessment_date))))
     LEFT JOIN clinical_outcomes.odi_assessments o ON ((((p.patient_id)::text = (o.patient_id)::text) AND (p.assessment_date = o.assessment_date))))
     LEFT JOIN clinical_outcomes.quality_of_life q ON ((((p.patient_id)::text = (q.patient_id)::text) AND (p.assessment_date = q.assessment_date))))
  ORDER BY p.patient_id, p.assessment_date DESC;


ALTER VIEW clinical_outcomes.latest_assessments OWNER TO postgres;

--
-- Name: medication_usage; Type: TABLE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TABLE clinical_outcomes.medication_usage (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id character varying(50) NOT NULL,
    assessment_date timestamp with time zone NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    assessment_period_days integer DEFAULT 30,
    current_medications jsonb DEFAULT '[]'::jsonb NOT NULL,
    opioid_usage jsonb DEFAULT '{}'::jsonb,
    nsaid_usage jsonb DEFAULT '{}'::jsonb,
    adjuvant_usage jsonb DEFAULT '{}'::jsonb,
    total_medication_count integer DEFAULT 0,
    pain_medication_count integer DEFAULT 0,
    adherence_percentage numeric(5,2) DEFAULT 100.0,
    missed_doses_count integer DEFAULT 0,
    side_effects text[] DEFAULT '{}'::text[],
    side_effect_severity jsonb DEFAULT '{}'::jsonb,
    medication_effectiveness numeric(3,1) DEFAULT 5.0,
    satisfaction_with_medication numeric(3,1) DEFAULT 5.0,
    assessor_id character varying(50),
    data_quality clinical_outcomes.data_quality_level DEFAULT 'complete'::clinical_outcomes.data_quality_level NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(50),
    version integer DEFAULT 1,
    CONSTRAINT medication_usage_adherence_percentage_check CHECK (((adherence_percentage >= (0)::numeric) AND (adherence_percentage <= (100)::numeric))),
    CONSTRAINT medication_usage_assessment_period_days_check CHECK ((assessment_period_days > 0)),
    CONSTRAINT medication_usage_medication_effectiveness_check CHECK (((medication_effectiveness >= (0)::numeric) AND (medication_effectiveness <= (10)::numeric))),
    CONSTRAINT medication_usage_missed_doses_count_check CHECK ((missed_doses_count >= 0)),
    CONSTRAINT medication_usage_pain_medication_count_check CHECK ((pain_medication_count >= 0)),
    CONSTRAINT medication_usage_satisfaction_with_medication_check CHECK (((satisfaction_with_medication >= (0)::numeric) AND (satisfaction_with_medication <= (10)::numeric))),
    CONSTRAINT medication_usage_total_medication_count_check CHECK ((total_medication_count >= 0))
);


ALTER TABLE clinical_outcomes.medication_usage OWNER TO postgres;

--
-- Name: outcome_changes; Type: TABLE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TABLE clinical_outcomes.outcome_changes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id character varying(50) NOT NULL,
    baseline_date timestamp with time zone NOT NULL,
    comparison_date timestamp with time zone NOT NULL,
    follow_up_duration_days integer NOT NULL,
    pain_baseline numeric(3,1),
    pain_current numeric(3,1),
    pain_change numeric(4,1),
    pain_percent_change numeric(6,2),
    pain_clinically_significant boolean,
    womac_baseline numeric(5,2),
    womac_current numeric(5,2),
    womac_change numeric(6,2),
    womac_percent_change numeric(6,2),
    womac_clinically_significant boolean,
    odi_baseline numeric(5,2),
    odi_current numeric(5,2),
    odi_change numeric(6,2),
    odi_percent_change numeric(6,2),
    odi_clinically_significant boolean,
    qol_baseline numeric(3,1),
    qol_current numeric(3,1),
    qol_change numeric(4,1),
    qol_percent_change numeric(6,2),
    qol_clinically_significant boolean,
    clinical_response_category character varying(50),
    significant_improvements integer DEFAULT 0,
    total_outcomes_assessed integer DEFAULT 0,
    response_rate numeric(5,2),
    calculated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    calculation_version character varying(10) DEFAULT '1.0'::character varying
);


ALTER TABLE clinical_outcomes.outcome_changes OWNER TO postgres;

--
-- Name: treatment_satisfaction; Type: TABLE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TABLE clinical_outcomes.treatment_satisfaction (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id character varying(50) NOT NULL,
    assessment_date timestamp with time zone NOT NULL,
    measurement_timing clinical_outcomes.measurement_timing NOT NULL,
    overall_satisfaction numeric(3,1) NOT NULL,
    would_recommend boolean NOT NULL,
    would_continue boolean NOT NULL,
    pain_relief_satisfaction numeric(3,1) NOT NULL,
    function_improvement_satisfaction numeric(3,1) NOT NULL,
    side_effect_tolerance numeric(3,1) NOT NULL,
    treatment_burden numeric(3,1) DEFAULT 5.0,
    convenience numeric(3,1) DEFAULT 5.0,
    provider_communication numeric(3,1) DEFAULT 8.0,
    care_coordination numeric(3,1) DEFAULT 8.0,
    expectations_met numeric(3,1) NOT NULL,
    most_helpful_aspect text,
    least_helpful_aspect text,
    suggestions_for_improvement text,
    assessor_id character varying(50),
    data_quality clinical_outcomes.data_quality_level DEFAULT 'complete'::clinical_outcomes.data_quality_level NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(50),
    version integer DEFAULT 1,
    CONSTRAINT treatment_satisfaction_care_coordination_check CHECK (((care_coordination >= (0)::numeric) AND (care_coordination <= (10)::numeric))),
    CONSTRAINT treatment_satisfaction_convenience_check CHECK (((convenience >= (0)::numeric) AND (convenience <= (10)::numeric))),
    CONSTRAINT treatment_satisfaction_expectations_met_check CHECK (((expectations_met >= (0)::numeric) AND (expectations_met <= (10)::numeric))),
    CONSTRAINT treatment_satisfaction_function_improvement_satisfaction_check CHECK (((function_improvement_satisfaction >= (0)::numeric) AND (function_improvement_satisfaction <= (10)::numeric))),
    CONSTRAINT treatment_satisfaction_overall_satisfaction_check CHECK (((overall_satisfaction >= (0)::numeric) AND (overall_satisfaction <= (10)::numeric))),
    CONSTRAINT treatment_satisfaction_pain_relief_satisfaction_check CHECK (((pain_relief_satisfaction >= (0)::numeric) AND (pain_relief_satisfaction <= (10)::numeric))),
    CONSTRAINT treatment_satisfaction_provider_communication_check CHECK (((provider_communication >= (0)::numeric) AND (provider_communication <= (10)::numeric))),
    CONSTRAINT treatment_satisfaction_side_effect_tolerance_check CHECK (((side_effect_tolerance >= (0)::numeric) AND (side_effect_tolerance <= (10)::numeric))),
    CONSTRAINT treatment_satisfaction_treatment_burden_check CHECK (((treatment_burden >= (0)::numeric) AND (treatment_burden <= (10)::numeric)))
);


ALTER TABLE clinical_outcomes.treatment_satisfaction OWNER TO postgres;

--
-- Name: weekly_symptom_tracking; Type: TABLE; Schema: clinical_outcomes; Owner: postgres
--

CREATE TABLE clinical_outcomes.weekly_symptom_tracking (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id character varying(50) NOT NULL,
    report_date timestamp with time zone NOT NULL,
    week_number integer NOT NULL,
    average_pain_week numeric(3,1) NOT NULL,
    worst_pain_week numeric(3,1) NOT NULL,
    pain_free_days integer NOT NULL,
    activity_limitation_days integer NOT NULL,
    missed_work_days integer DEFAULT 0,
    fatigue_level numeric(3,1) DEFAULT 5.0,
    mood_rating numeric(3,1) DEFAULT 5.0,
    anxiety_level numeric(3,1) DEFAULT 5.0,
    treatment_helpfulness numeric(3,1) DEFAULT 5.0,
    side_effects_this_week text[] DEFAULT '{}'::text[],
    global_improvement integer NOT NULL,
    data_source character varying(50) DEFAULT 'patient_app'::character varying,
    data_quality clinical_outcomes.data_quality_level DEFAULT 'complete'::clinical_outcomes.data_quality_level NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    version integer DEFAULT 1,
    CONSTRAINT logical_pain_week CHECK ((worst_pain_week >= average_pain_week)),
    CONSTRAINT weekly_symptom_tracking_activity_limitation_days_check CHECK (((activity_limitation_days >= 0) AND (activity_limitation_days <= 7))),
    CONSTRAINT weekly_symptom_tracking_anxiety_level_check CHECK (((anxiety_level >= (0)::numeric) AND (anxiety_level <= (10)::numeric))),
    CONSTRAINT weekly_symptom_tracking_average_pain_week_check CHECK (((average_pain_week >= (0)::numeric) AND (average_pain_week <= (10)::numeric))),
    CONSTRAINT weekly_symptom_tracking_fatigue_level_check CHECK (((fatigue_level >= (0)::numeric) AND (fatigue_level <= (10)::numeric))),
    CONSTRAINT weekly_symptom_tracking_global_improvement_check CHECK (((global_improvement >= 1) AND (global_improvement <= 7))),
    CONSTRAINT weekly_symptom_tracking_missed_work_days_check CHECK (((missed_work_days >= 0) AND (missed_work_days <= 7))),
    CONSTRAINT weekly_symptom_tracking_mood_rating_check CHECK (((mood_rating >= (0)::numeric) AND (mood_rating <= (10)::numeric))),
    CONSTRAINT weekly_symptom_tracking_pain_free_days_check CHECK (((pain_free_days >= 0) AND (pain_free_days <= 7))),
    CONSTRAINT weekly_symptom_tracking_treatment_helpfulness_check CHECK (((treatment_helpfulness >= (0)::numeric) AND (treatment_helpfulness <= (10)::numeric))),
    CONSTRAINT weekly_symptom_tracking_week_number_check CHECK ((week_number >= 1)),
    CONSTRAINT weekly_symptom_tracking_worst_pain_week_check CHECK (((worst_pain_week >= (0)::numeric) AND (worst_pain_week <= (10)::numeric)))
);


ALTER TABLE clinical_outcomes.weekly_symptom_tracking OWNER TO postgres;

--
-- Data for Name: assessment_schedules; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.assessment_schedules (id, patient_id, baseline_date, study_duration_weeks, scheduled_assessments, total_scheduled, total_completed, active, completion_status, created_at, updated_at, created_by, version) FROM stdin;
47cadc6c-f230-405b-a0d7-da345cf86f4a	DEMO_PATIENT_001	2024-01-01 01:00:00-08	52	[{"timing": "baseline", "scheduled_date": "2024-01-01", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life"]}, {"timing": "week_4", "scheduled_date": "2024-01-29", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage"]}, {"timing": "week_12", "scheduled_date": "2024-03-25", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life", "treatment_satisfaction"]}, {"timing": "week_24", "scheduled_date": "2024-06-17", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life", "treatment_satisfaction"]}]	0	0	t	active	2025-06-19 18:43:16.881215-07	2025-06-19 18:43:16.881215-07	\N	1
\.


--
-- Data for Name: healthcare_utilization; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.healthcare_utilization (id, patient_id, assessment_date, measurement_timing, assessment_period_days, primary_care_visits, specialist_visits, pain_clinic_visits, physical_therapy_visits, emergency_room_visits, urgent_care_visits, hospitalizations, hospital_days, imaging_studies, laboratory_tests, procedures, estimated_total_cost, out_of_pocket_cost, pain_related_visits, treatment_related_visits, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
\.


--
-- Data for Name: medication_usage; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.medication_usage (id, patient_id, assessment_date, measurement_timing, assessment_period_days, current_medications, opioid_usage, nsaid_usage, adjuvant_usage, total_medication_count, pain_medication_count, adherence_percentage, missed_doses_count, side_effects, side_effect_severity, medication_effectiveness, satisfaction_with_medication, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
\.


--
-- Data for Name: odi_assessments; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.odi_assessments (id, patient_id, assessment_date, measurement_timing, pain_intensity, personal_care, lifting, walking, sitting, standing, sleeping, sex_life, social_life, traveling, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
\.


--
-- Data for Name: outcome_changes; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.outcome_changes (id, patient_id, baseline_date, comparison_date, follow_up_duration_days, pain_baseline, pain_current, pain_change, pain_percent_change, pain_clinically_significant, womac_baseline, womac_current, womac_change, womac_percent_change, womac_clinically_significant, odi_baseline, odi_current, odi_change, odi_percent_change, odi_clinically_significant, qol_baseline, qol_current, qol_change, qol_percent_change, qol_clinically_significant, clinical_response_category, significant_improvements, total_outcomes_assessed, response_rate, calculated_at, calculation_version) FROM stdin;
\.


--
-- Data for Name: pain_assessments; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.pain_assessments (id, patient_id, assessment_date, measurement_timing, current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference, pain_at_rest, pain_with_movement, pain_with_exercise, pain_locations, pain_quality, assessment_method, assessor_type, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
\.


--
-- Data for Name: quality_of_life; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.quality_of_life (id, patient_id, assessment_date, measurement_timing, general_health, physical_functioning, role_physical, bodily_pain, vitality, social_functioning, role_emotional, mental_health, sleep_quality, work_productivity, relationship_satisfaction, life_satisfaction, days_per_week_exercise, minutes_per_day_exercise, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
\.


--
-- Data for Name: treatment_satisfaction; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.treatment_satisfaction (id, patient_id, assessment_date, measurement_timing, overall_satisfaction, would_recommend, would_continue, pain_relief_satisfaction, function_improvement_satisfaction, side_effect_tolerance, treatment_burden, convenience, provider_communication, care_coordination, expectations_met, most_helpful_aspect, least_helpful_aspect, suggestions_for_improvement, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
\.


--
-- Data for Name: weekly_symptom_tracking; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.weekly_symptom_tracking (id, patient_id, report_date, week_number, average_pain_week, worst_pain_week, pain_free_days, activity_limitation_days, missed_work_days, fatigue_level, mood_rating, anxiety_level, treatment_helpfulness, side_effects_this_week, global_improvement, data_source, data_quality, notes, created_at, updated_at, version) FROM stdin;
\.


--
-- Data for Name: womac_assessments; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.womac_assessments (id, patient_id, assessment_date, measurement_timing, pain_walking, pain_stairs, pain_night_bed, pain_sitting, pain_standing, stiffness_waking, stiffness_later_day, function_stairs_down, function_stairs_up, function_rising_sitting, function_standing, function_bending, function_walking_flat, function_getting_in_out_car, function_shopping, function_socks, function_rising_bed, function_socks_off, function_lying_bed, function_bath_shower, function_sitting, function_toilet, function_heavy_domestic, function_light_domestic, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
\.


--
-- Name: assessment_schedules assessment_schedules_patient_id_key; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.assessment_schedules
    ADD CONSTRAINT assessment_schedules_patient_id_key UNIQUE (patient_id);


--
-- Name: assessment_schedules assessment_schedules_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.assessment_schedules
    ADD CONSTRAINT assessment_schedules_pkey PRIMARY KEY (id);


--
-- Name: healthcare_utilization healthcare_utilization_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.healthcare_utilization
    ADD CONSTRAINT healthcare_utilization_pkey PRIMARY KEY (id);


--
-- Name: medication_usage medication_usage_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.medication_usage
    ADD CONSTRAINT medication_usage_pkey PRIMARY KEY (id);


--
-- Name: odi_assessments odi_assessments_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.odi_assessments
    ADD CONSTRAINT odi_assessments_pkey PRIMARY KEY (id);


--
-- Name: outcome_changes outcome_changes_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.outcome_changes
    ADD CONSTRAINT outcome_changes_pkey PRIMARY KEY (id);


--
-- Name: pain_assessments pain_assessments_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.pain_assessments
    ADD CONSTRAINT pain_assessments_pkey PRIMARY KEY (id);


--
-- Name: quality_of_life quality_of_life_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.quality_of_life
    ADD CONSTRAINT quality_of_life_pkey PRIMARY KEY (id);


--
-- Name: treatment_satisfaction treatment_satisfaction_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.treatment_satisfaction
    ADD CONSTRAINT treatment_satisfaction_pkey PRIMARY KEY (id);


--
-- Name: pain_assessments unique_patient_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.pain_assessments
    ADD CONSTRAINT unique_patient_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- Name: outcome_changes unique_patient_comparison; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.outcome_changes
    ADD CONSTRAINT unique_patient_comparison UNIQUE (patient_id, baseline_date, comparison_date);


--
-- Name: medication_usage unique_patient_medication_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.medication_usage
    ADD CONSTRAINT unique_patient_medication_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- Name: odi_assessments unique_patient_odi_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.odi_assessments
    ADD CONSTRAINT unique_patient_odi_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- Name: quality_of_life unique_patient_qol_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.quality_of_life
    ADD CONSTRAINT unique_patient_qol_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- Name: treatment_satisfaction unique_patient_satisfaction_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.treatment_satisfaction
    ADD CONSTRAINT unique_patient_satisfaction_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- Name: healthcare_utilization unique_patient_utilization_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.healthcare_utilization
    ADD CONSTRAINT unique_patient_utilization_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- Name: weekly_symptom_tracking unique_patient_week; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.weekly_symptom_tracking
    ADD CONSTRAINT unique_patient_week UNIQUE (patient_id, week_number);


--
-- Name: womac_assessments unique_patient_womac_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.womac_assessments
    ADD CONSTRAINT unique_patient_womac_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- Name: weekly_symptom_tracking weekly_symptom_tracking_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.weekly_symptom_tracking
    ADD CONSTRAINT weekly_symptom_tracking_pkey PRIMARY KEY (id);


--
-- Name: womac_assessments womac_assessments_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.womac_assessments
    ADD CONSTRAINT womac_assessments_pkey PRIMARY KEY (id);


--
-- Name: idx_assessment_schedules_baseline; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_assessment_schedules_baseline ON clinical_outcomes.assessment_schedules USING btree (baseline_date);


--
-- Name: idx_assessment_schedules_patient; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_assessment_schedules_patient ON clinical_outcomes.assessment_schedules USING btree (patient_id);


--
-- Name: idx_compliance_rate; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_compliance_rate ON clinical_outcomes.assessment_schedules USING btree (compliance_rate);


--
-- Name: idx_healthcare_total_visits; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_healthcare_total_visits ON clinical_outcomes.healthcare_utilization USING btree (total_visits);


--
-- Name: idx_healthcare_utilization_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_healthcare_utilization_patient_date ON clinical_outcomes.healthcare_utilization USING btree (patient_id, assessment_date);


--
-- Name: idx_medication_adherence; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_medication_adherence ON clinical_outcomes.medication_usage USING btree (adherence_percentage);


--
-- Name: idx_medication_usage_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_medication_usage_patient_date ON clinical_outcomes.medication_usage USING btree (patient_id, assessment_date);


--
-- Name: idx_odi_assessments_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_odi_assessments_patient_date ON clinical_outcomes.odi_assessments USING btree (patient_id, assessment_date);


--
-- Name: idx_odi_assessments_timing; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_odi_assessments_timing ON clinical_outcomes.odi_assessments USING btree (measurement_timing);


--
-- Name: idx_odi_percentage; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_odi_percentage ON clinical_outcomes.odi_assessments USING btree (percentage_disability);


--
-- Name: idx_outcome_changes_dates; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_outcome_changes_dates ON clinical_outcomes.outcome_changes USING btree (baseline_date, comparison_date);


--
-- Name: idx_outcome_changes_patient; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_outcome_changes_patient ON clinical_outcomes.outcome_changes USING btree (patient_id);


--
-- Name: idx_pain_assessments_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_pain_assessments_patient_date ON clinical_outcomes.pain_assessments USING btree (patient_id, assessment_date);


--
-- Name: idx_pain_assessments_quality; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_pain_assessments_quality ON clinical_outcomes.pain_assessments USING btree (data_quality);


--
-- Name: idx_pain_assessments_timing; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_pain_assessments_timing ON clinical_outcomes.pain_assessments USING btree (measurement_timing);


--
-- Name: idx_qol_life_satisfaction; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_qol_life_satisfaction ON clinical_outcomes.quality_of_life USING btree (life_satisfaction);


--
-- Name: idx_quality_of_life_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_quality_of_life_patient_date ON clinical_outcomes.quality_of_life USING btree (patient_id, assessment_date);


--
-- Name: idx_satisfaction_overall; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_satisfaction_overall ON clinical_outcomes.treatment_satisfaction USING btree (overall_satisfaction);


--
-- Name: idx_treatment_satisfaction_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_treatment_satisfaction_patient_date ON clinical_outcomes.treatment_satisfaction USING btree (patient_id, assessment_date);


--
-- Name: idx_weekly_symptoms_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_weekly_symptoms_date ON clinical_outcomes.weekly_symptom_tracking USING btree (report_date);


--
-- Name: idx_weekly_symptoms_patient_week; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_weekly_symptoms_patient_week ON clinical_outcomes.weekly_symptom_tracking USING btree (patient_id, week_number);


--
-- Name: idx_womac_assessments_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_womac_assessments_patient_date ON clinical_outcomes.womac_assessments USING btree (patient_id, assessment_date);


--
-- Name: idx_womac_assessments_timing; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_womac_assessments_timing ON clinical_outcomes.womac_assessments USING btree (measurement_timing);


--
-- Name: idx_womac_total_score; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_womac_total_score ON clinical_outcomes.womac_assessments USING btree (total_score);


--
-- Name: assessment_schedules update_assessment_schedules_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_assessment_schedules_updated_at BEFORE UPDATE ON clinical_outcomes.assessment_schedules FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: healthcare_utilization update_healthcare_utilization_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_healthcare_utilization_updated_at BEFORE UPDATE ON clinical_outcomes.healthcare_utilization FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: medication_usage update_medication_usage_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_medication_usage_updated_at BEFORE UPDATE ON clinical_outcomes.medication_usage FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: odi_assessments update_odi_assessments_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_odi_assessments_updated_at BEFORE UPDATE ON clinical_outcomes.odi_assessments FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: pain_assessments update_pain_assessments_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_pain_assessments_updated_at BEFORE UPDATE ON clinical_outcomes.pain_assessments FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: quality_of_life update_quality_of_life_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_quality_of_life_updated_at BEFORE UPDATE ON clinical_outcomes.quality_of_life FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: treatment_satisfaction update_treatment_satisfaction_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_treatment_satisfaction_updated_at BEFORE UPDATE ON clinical_outcomes.treatment_satisfaction FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: weekly_symptom_tracking update_weekly_symptom_tracking_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_weekly_symptom_tracking_updated_at BEFORE UPDATE ON clinical_outcomes.weekly_symptom_tracking FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: womac_assessments update_womac_assessments_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_womac_assessments_updated_at BEFORE UPDATE ON clinical_outcomes.womac_assessments FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- PostgreSQL database dump complete
--

