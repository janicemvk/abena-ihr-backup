--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.9

-- Started on 2025-07-04 07:32:16

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
-- TOC entry 7 (class 2615 OID 27335)
-- Name: clinical_outcomes; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA clinical_outcomes;


ALTER SCHEMA clinical_outcomes OWNER TO postgres;

--
-- TOC entry 2 (class 3079 OID 25592)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 5415 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 931 (class 1247 OID 27376)
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
-- TOC entry 925 (class 1247 OID 27354)
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
-- TOC entry 922 (class 1247 OID 27337)
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
-- TOC entry 928 (class 1247 OID 27364)
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

--
-- TOC entry 255 (class 1255 OID 26165)
-- Name: update_outcomes_timestamp(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_outcomes_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_outcomes_timestamp() OWNER TO postgres;

--
-- TOC entry 254 (class 1255 OID 25603)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 239 (class 1259 OID 27655)
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
-- TOC entry 233 (class 1259 OID 27455)
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
-- TOC entry 231 (class 1259 OID 27385)
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
-- TOC entry 236 (class 1259 OID 27561)
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
-- TOC entry 232 (class 1259 OID 27412)
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
-- TOC entry 242 (class 1259 OID 27717)
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
-- TOC entry 243 (class 1259 OID 27722)
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
-- TOC entry 235 (class 1259 OID 27515)
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
-- TOC entry 241 (class 1259 OID 27712)
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
-- TOC entry 234 (class 1259 OID 27481)
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
-- TOC entry 240 (class 1259 OID 27676)
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
-- TOC entry 238 (class 1259 OID 27628)
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
-- TOC entry 237 (class 1259 OID 27595)
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
-- TOC entry 226 (class 1259 OID 25691)
-- Name: allergies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.allergies (
    allergy_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    allergen character varying(255) NOT NULL,
    allergy_type character varying(100),
    severity character varying(50),
    reaction text,
    onset_date date,
    status character varying(50) DEFAULT 'active'::character varying,
    notes text,
    recorded_by uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.allergies OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 25617)
-- Name: appointments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.appointments (
    appointment_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    provider_id uuid NOT NULL,
    appointment_date date NOT NULL,
    appointment_time time without time zone NOT NULL,
    duration_minutes integer DEFAULT 30,
    appointment_type character varying(100),
    status character varying(50) DEFAULT 'scheduled'::character varying,
    reason_for_visit text,
    notes text,
    room_number character varying(20),
    created_by uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.appointments OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 25297)
-- Name: clinical_observations; Type: TABLE; Schema: public; Owner: abena_user
--

CREATE TABLE public.clinical_observations (
    observation_id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id uuid NOT NULL,
    observation_type character varying(100) NOT NULL,
    value_numeric numeric(10,3),
    value_text text,
    unit character varying(20),
    recorded_at timestamp without time zone NOT NULL,
    recorded_by character varying(100),
    source_system character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.clinical_observations OWNER TO abena_user;

--
-- TOC entry 224 (class 1259 OID 25655)
-- Name: diagnoses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.diagnoses (
    diagnosis_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    provider_id uuid NOT NULL,
    record_id uuid,
    icd10_code character varying(10),
    diagnosis_description text NOT NULL,
    diagnosis_type character varying(50),
    onset_date date,
    resolution_date date,
    status character varying(50) DEFAULT 'active'::character varying,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.diagnoses OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 25306)
-- Name: lab_results; Type: TABLE; Schema: public; Owner: abena_user
--

CREATE TABLE public.lab_results (
    result_id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id uuid NOT NULL,
    test_name character varying(100) NOT NULL,
    test_code character varying(20),
    result_value numeric(10,3),
    result_text text,
    unit character varying(20),
    reference_range character varying(50),
    abnormal_flag character varying(10),
    test_date timestamp without time zone NOT NULL,
    lab_name character varying(100),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.lab_results OWNER TO abena_user;

--
-- TOC entry 223 (class 1259 OID 25634)
-- Name: medical_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medical_records (
    record_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    provider_id uuid NOT NULL,
    appointment_id uuid,
    visit_date timestamp with time zone NOT NULL,
    chief_complaint text,
    history_of_present_illness text,
    review_of_systems jsonb,
    physical_examination jsonb,
    assessment_and_plan text,
    follow_up_instructions text,
    is_signed boolean DEFAULT false,
    signed_at timestamp with time zone,
    signed_by uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.medical_records OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 25315)
-- Name: medications; Type: TABLE; Schema: public; Owner: abena_user
--

CREATE TABLE public.medications (
    medication_id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id uuid NOT NULL,
    medication_name character varying(200) NOT NULL,
    dosage character varying(100),
    frequency character varying(100),
    start_date date,
    end_date date,
    prescribing_physician character varying(100),
    status character varying(20) DEFAULT 'active'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.medications OWNER TO abena_user;

--
-- TOC entry 228 (class 1259 OID 26131)
-- Name: outcomes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.outcomes (
    outcome_id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id uuid NOT NULL,
    medical_record_id uuid,
    provider_id uuid,
    outcome_type character varying(50) NOT NULL,
    outcome_category character varying(30) NOT NULL,
    severity_level character varying(20),
    outcome_description text NOT NULL,
    outcome_measure character varying(100),
    baseline_value numeric(10,2),
    outcome_value numeric(10,2),
    improvement_percentage numeric(5,2),
    related_diagnosis character varying(200),
    related_procedure_id uuid,
    related_medication_id uuid,
    treatment_plan_id uuid,
    outcome_date timestamp with time zone NOT NULL,
    follow_up_period character varying(20),
    time_to_outcome_days integer,
    assessment_method character varying(100),
    assessment_tools text[],
    measured_by uuid,
    patient_satisfaction_score numeric(3,1),
    functional_improvement boolean,
    pain_score_change numeric(3,1),
    mobility_improvement boolean,
    outcome_status character varying(20) DEFAULT 'active'::character varying NOT NULL,
    is_expected_outcome boolean DEFAULT true,
    requires_intervention boolean DEFAULT false,
    intervention_provided text,
    follow_up_required boolean DEFAULT false,
    next_assessment_date timestamp with time zone,
    follow_up_notes text,
    data_source character varying(50) DEFAULT 'clinical_assessment'::character varying,
    confidence_level character varying(20),
    notes text,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    CONSTRAINT outcomes_confidence_level_check CHECK (((confidence_level)::text = ANY ((ARRAY['high'::character varying, 'medium'::character varying, 'low'::character varying])::text[]))),
    CONSTRAINT outcomes_outcome_category_check CHECK (((outcome_category)::text = ANY ((ARRAY['positive'::character varying, 'negative'::character varying, 'neutral'::character varying, 'mixed'::character varying])::text[]))),
    CONSTRAINT outcomes_outcome_status_check CHECK (((outcome_status)::text = ANY ((ARRAY['active'::character varying, 'resolved'::character varying, 'ongoing'::character varying, 'worsened'::character varying, 'stable'::character varying, 'unknown'::character varying])::text[]))),
    CONSTRAINT outcomes_outcome_type_check CHECK (((outcome_type)::text = ANY ((ARRAY['treatment_response'::character varying, 'clinical_improvement'::character varying, 'adverse_event'::character varying, 'mortality'::character varying, 'functional_status'::character varying, 'quality_of_life'::character varying, 'readmission'::character varying, 'discharge'::character varying, 'recovery'::character varying, 'complications'::character varying, 'medication_response'::character varying, 'surgical_outcome'::character varying])::text[]))),
    CONSTRAINT outcomes_patient_satisfaction_score_check CHECK (((patient_satisfaction_score >= (0)::numeric) AND (patient_satisfaction_score <= (10)::numeric))),
    CONSTRAINT outcomes_severity_level_check CHECK (((severity_level)::text = ANY ((ARRAY['mild'::character varying, 'moderate'::character varying, 'severe'::character varying, 'critical'::character varying, 'resolved'::character varying])::text[])))
);


ALTER TABLE public.outcomes OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 26172)
-- Name: outcome_trends; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.outcome_trends AS
 SELECT date_trunc('month'::text, outcome_date) AS month,
    outcome_type,
    outcome_category,
    count(*) AS outcome_count,
    avg(improvement_percentage) AS avg_improvement,
    count(
        CASE
            WHEN (requires_intervention = true) THEN 1
            ELSE NULL::integer
        END) AS interventions_required
   FROM public.outcomes
  WHERE (outcome_date >= (now() - '1 year'::interval))
  GROUP BY (date_trunc('month'::text, outcome_date)), outcome_type, outcome_category
  ORDER BY (date_trunc('month'::text, outcome_date)) DESC, (count(*)) DESC;


ALTER VIEW public.outcome_trends OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 26167)
-- Name: positive_outcomes_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.positive_outcomes_summary AS
 SELECT outcome_type,
    count(*) AS total_positive_outcomes,
    avg(improvement_percentage) AS avg_improvement,
    avg(patient_satisfaction_score) AS avg_satisfaction,
    count(
        CASE
            WHEN (functional_improvement = true) THEN 1
            ELSE NULL::integer
        END) AS functional_improvements
   FROM public.outcomes
  WHERE (((outcome_category)::text = 'positive'::text) AND ((outcome_status)::text = ANY ((ARRAY['resolved'::character varying, 'stable'::character varying])::text[])))
  GROUP BY outcome_type
  ORDER BY (count(*)) DESC;


ALTER VIEW public.positive_outcomes_summary OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 25702)
-- Name: procedures; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.procedures (
    procedure_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    provider_id uuid NOT NULL,
    record_id uuid,
    procedure_name character varying(255) NOT NULL,
    cpt_code character varying(20),
    procedure_date timestamp with time zone,
    location character varying(255),
    status character varying(50) DEFAULT 'completed'::character varying,
    notes text,
    complications text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.procedures OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 25604)
-- Name: providers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.providers (
    provider_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    npi_number character varying(20),
    license_number character varying(50),
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    title character varying(100),
    specialization character varying(255),
    department character varying(255),
    phone character varying(20),
    email character varying(255),
    is_active boolean DEFAULT true,
    hire_date date,
    license_expiry_date date,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.providers OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 25325)
-- Name: risk_scores; Type: TABLE; Schema: public; Owner: abena_user
--

CREATE TABLE public.risk_scores (
    score_id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id uuid NOT NULL,
    risk_type character varying(50) NOT NULL,
    score_value numeric(5,3) NOT NULL,
    risk_level character varying(20),
    calculated_at timestamp without time zone NOT NULL,
    model_version character varying(20),
    factors_considered jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.risk_scores OWNER TO abena_user;

--
-- TOC entry 225 (class 1259 OID 25676)
-- Name: vital_signs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vital_signs (
    vital_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    recorded_by uuid,
    record_id uuid,
    recorded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    height_cm numeric(5,2),
    weight_kg numeric(5,2),
    bmi numeric(4,1),
    temperature_c numeric(4,1),
    blood_pressure_systolic integer,
    blood_pressure_diastolic integer,
    heart_rate integer,
    respiratory_rate integer,
    oxygen_saturation integer,
    pain_scale integer,
    notes text,
    CONSTRAINT vital_signs_pain_scale_check CHECK (((pain_scale >= 0) AND (pain_scale <= 10)))
);


ALTER TABLE public.vital_signs OWNER TO postgres;

--
-- TOC entry 5407 (class 0 OID 27655)
-- Dependencies: 239
-- Data for Name: assessment_schedules; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.assessment_schedules (id, patient_id, baseline_date, study_duration_weeks, scheduled_assessments, total_scheduled, total_completed, active, completion_status, created_at, updated_at, created_by, version) FROM stdin;
d6527a67-9e4c-42a2-a6b4-b6e413c0cd41	DEMO_PATIENT_001	2024-01-01 01:00:00-08	52	[{"timing": "baseline", "scheduled_date": "2024-01-01", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life"]}, {"timing": "week_4", "scheduled_date": "2024-01-29", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage"]}, {"timing": "week_12", "scheduled_date": "2024-03-25", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life", "treatment_satisfaction"]}, {"timing": "week_24", "scheduled_date": "2024-06-17", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life", "treatment_satisfaction"]}]	0	0	t	active	2025-06-19 18:51:09.155745-07	2025-06-19 18:51:09.155745-07	\N	1
af37d4f7-c6e6-4588-affc-906d535d053e	PATIENT_001	2024-01-15 01:00:00-08	52	[{"timing": "baseline", "scheduled_date": "2024-01-15", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life"]}, {"timing": "week_4", "scheduled_date": "2024-02-12", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage"]}, {"timing": "week_12", "scheduled_date": "2024-04-08", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life", "treatment_satisfaction"]}]	3	3	t	active	2025-06-19 18:55:38.944902-07	2025-06-19 18:55:38.944902-07	\N	1
a91126ed-58fd-4955-92d8-731f860e8f7d	PATIENT_002	2024-01-20 02:30:00-08	52	[{"timing": "baseline", "scheduled_date": "2024-01-20", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life"]}, {"timing": "week_4", "scheduled_date": "2024-02-17", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage"]}, {"timing": "week_12", "scheduled_date": "2024-04-13", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life", "treatment_satisfaction"]}]	3	2	t	active	2025-06-19 18:55:38.944902-07	2025-06-19 18:55:38.944902-07	\N	1
5de42d8d-03f1-41fe-965c-684d524ab6f5	PATIENT_003	2024-02-01 06:15:00-08	52	[{"timing": "baseline", "scheduled_date": "2024-02-01", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life"]}, {"timing": "week_4", "scheduled_date": "2024-02-29", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage"]}]	2	2	t	active	2025-06-19 18:55:38.944902-07	2025-06-19 18:55:38.944902-07	\N	1
\.


--
-- TOC entry 5403 (class 0 OID 27515)
-- Dependencies: 235
-- Data for Name: healthcare_utilization; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.healthcare_utilization (id, patient_id, assessment_date, measurement_timing, assessment_period_days, primary_care_visits, specialist_visits, pain_clinic_visits, physical_therapy_visits, emergency_room_visits, urgent_care_visits, hospitalizations, hospital_days, imaging_studies, laboratory_tests, procedures, estimated_total_cost, out_of_pocket_cost, pain_related_visits, treatment_related_visits, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
cb3aa133-43f4-4e4b-812e-340b78a42462	PATIENT_001	2024-01-15 01:00:00-08	baseline	30	2	1	1	0	0	0	0	0	1	2	0	1250.00	150.00	3	1	DR_SMITH	complete	\N	2025-06-19 18:55:39.016158-07	2025-06-19 18:55:39.016158-07	SYSTEM	1
12661966-e5b9-4a68-86a9-a9d52902cf02	PATIENT_002	2024-01-20 02:30:00-08	baseline	30	3	2	1	2	1	0	0	0	2	3	0	2100.00	300.00	5	2	DR_JOHNSON	complete	\N	2025-06-19 18:55:39.019717-07	2025-06-19 18:55:39.019717-07	SYSTEM	1
\.


--
-- TOC entry 5402 (class 0 OID 27481)
-- Dependencies: 234
-- Data for Name: medication_usage; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.medication_usage (id, patient_id, assessment_date, measurement_timing, assessment_period_days, current_medications, opioid_usage, nsaid_usage, adjuvant_usage, total_medication_count, pain_medication_count, adherence_percentage, missed_doses_count, side_effects, side_effect_severity, medication_effectiveness, satisfaction_with_medication, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
9dafa7a0-2838-4d4f-b9d4-39a1e6b1ece5	PATIENT_001	2024-01-15 01:00:00-08	baseline	30	[{"dose": "400mg", "name": "Ibuprofen", "frequency": "TID", "start_date": "2024-01-10"}]	{}	{"ibuprofen": {"dose": "400mg", "frequency": "TID", "days_per_week": 7}}	{"glucosamine": {"dose": "1500mg", "frequency": "QD", "days_per_week": 7}}	2	1	95.00	2	{stomach_upset}	{}	6.5	7.0	DR_SMITH	complete	\N	2025-06-19 18:55:39.001645-07	2025-06-19 18:55:39.001645-07	SYSTEM	1
56f22545-df12-4456-956f-73d5d34ae501	PATIENT_001	2024-02-12 01:00:00-08	week_4	30	[{"dose": "400mg", "name": "Ibuprofen", "frequency": "BID", "start_date": "2024-01-10"}]	{}	{"ibuprofen": {"dose": "400mg", "frequency": "BID", "days_per_week": 7}}	{"glucosamine": {"dose": "1500mg", "frequency": "QD", "days_per_week": 7}}	2	1	98.00	1	{mild_stomach_upset}	{}	7.5	8.0	DR_SMITH	complete	\N	2025-06-19 18:55:39.004442-07	2025-06-19 18:55:39.004442-07	SYSTEM	1
c6879833-bb44-4a54-a974-20b417b870b8	PATIENT_002	2024-01-20 02:30:00-08	baseline	30	[{"dose": "50mg", "name": "Tramadol", "frequency": "QID", "start_date": "2024-01-15"}, {"dose": "500mg", "name": "Naproxen", "frequency": "BID", "start_date": "2024-01-15"}]	{"tramadol": {"dose": "50mg", "frequency": "QID", "days_per_week": 7}}	{"naproxen": {"dose": "500mg", "frequency": "BID", "days_per_week": 7}}	{}	2	2	90.00	5	{drowsiness,constipation}	{}	7.0	6.5	DR_JOHNSON	complete	\N	2025-06-19 18:55:39.015471-07	2025-06-19 18:55:39.015471-07	SYSTEM	1
\.


--
-- TOC entry 5401 (class 0 OID 27455)
-- Dependencies: 233
-- Data for Name: odi_assessments; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.odi_assessments (id, patient_id, assessment_date, measurement_timing, pain_intensity, personal_care, lifting, walking, sitting, standing, sleeping, sex_life, social_life, traveling, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
352a0d0b-3962-4a0b-b896-038b3d7fe9b8	PATIENT_002	2024-01-20 02:30:00-08	baseline	4	3	4	3	4	4	3	2	3	4	DR_JOHNSON	complete	\N	2025-06-19 18:55:38.994586-07	2025-06-19 18:55:38.994586-07	SYSTEM	1
a9e406a3-33ff-4910-87a2-5d5bf604340e	PATIENT_002	2024-02-17 02:30:00-08	week_4	3	2	3	2	3	3	2	1	2	3	DR_JOHNSON	complete	\N	2025-06-19 18:55:39.000387-07	2025-06-19 18:55:39.000387-07	SYSTEM	1
\.


--
-- TOC entry 5408 (class 0 OID 27676)
-- Dependencies: 240
-- Data for Name: outcome_changes; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.outcome_changes (id, patient_id, baseline_date, comparison_date, follow_up_duration_days, pain_baseline, pain_current, pain_change, pain_percent_change, pain_clinically_significant, womac_baseline, womac_current, womac_change, womac_percent_change, womac_clinically_significant, odi_baseline, odi_current, odi_change, odi_percent_change, odi_clinically_significant, qol_baseline, qol_current, qol_change, qol_percent_change, qol_clinically_significant, clinical_response_category, significant_improvements, total_outcomes_assessed, response_rate, calculated_at, calculation_version) FROM stdin;
941752bf-14b3-42f4-a17f-b682ac22e180	PATIENT_001	2024-01-15 01:00:00-08	2024-04-08 02:00:00-07	84	7.5	4.5	-3.0	-40.00	t	75.00	25.00	-50.00	-66.70	t	\N	\N	\N	\N	\N	6.0	8.0	2.0	33.30	t	excellent_response	3	3	100.00	2025-06-19 18:55:39.053746-07	1.0
1b1d3f82-1951-4b76-81f4-99a40e688ed2	PATIENT_002	2024-01-20 02:30:00-08	2024-02-17 02:30:00-08	28	8.5	7.0	-1.5	-17.60	f	87.50	62.50	-25.00	-28.60	t	\N	\N	\N	\N	\N	4.0	4.0	0.0	0.00	f	moderate_response	1	3	33.30	2025-06-19 18:55:39.06358-07	1.0
\.


--
-- TOC entry 5399 (class 0 OID 27385)
-- Dependencies: 231
-- Data for Name: pain_assessments; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.pain_assessments (id, patient_id, assessment_date, measurement_timing, current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference, pain_at_rest, pain_with_movement, pain_with_exercise, pain_locations, pain_quality, assessment_method, assessor_type, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
6e8405ec-8229-475a-bf69-2824efdd119f	PATIENT_001	2024-01-15 01:00:00-08	baseline	8.0	7.5	9.5	5.0	8.5	6.0	9.0	9.5	{right_knee,left_knee}	{aching,stiffness}	self_report	patient	DR_SMITH	complete	\N	2025-06-19 18:55:38.947413-07	2025-06-19 18:55:38.947413-07	SYSTEM	1
c6cca302-474b-429b-bf06-485af14899e7	PATIENT_001	2024-02-12 01:00:00-08	week_4	6.5	6.0	8.0	4.0	6.5	4.5	7.5	8.0	{right_knee,left_knee}	{aching}	self_report	patient	DR_SMITH	complete	\N	2025-06-19 18:55:38.950384-07	2025-06-19 18:55:38.950384-07	SYSTEM	1
d34ad869-434d-495a-8bf2-f6b20102dfb2	PATIENT_001	2024-04-08 02:00:00-07	week_12	5.0	4.5	6.5	3.0	5.0	3.0	6.0	6.5	{right_knee}	{mild_aching}	self_report	patient	DR_SMITH	complete	\N	2025-06-19 18:55:38.952504-07	2025-06-19 18:55:38.952504-07	SYSTEM	1
3b3bb0bc-9bdb-482a-870d-2069889c8ccd	PATIENT_002	2024-01-20 02:30:00-08	baseline	9.0	8.5	10.0	6.0	9.0	7.0	9.5	10.0	{lower_back,right_hip}	{sharp,radiating}	self_report	patient	DR_JOHNSON	complete	\N	2025-06-19 18:55:38.965421-07	2025-06-19 18:55:38.965421-07	SYSTEM	1
0e3f4437-bc54-43f2-a531-f49b51cd0084	PATIENT_002	2024-02-17 02:30:00-08	week_4	7.5	7.0	8.5	5.5	7.5	5.5	8.0	8.5	{lower_back,right_hip}	{dull,aching}	self_report	patient	DR_JOHNSON	complete	\N	2025-06-19 18:55:38.966173-07	2025-06-19 18:55:38.966173-07	SYSTEM	1
a17d91ee-4309-445d-a8f1-3703558d842f	PATIENT_003	2024-02-01 06:15:00-08	baseline	6.5	6.0	8.0	4.5	6.5	4.0	7.0	8.0	{left_shoulder,neck}	{stiffness,aching}	self_report	patient	DR_WILLIAMS	complete	\N	2025-06-19 18:55:38.967888-07	2025-06-19 18:55:38.967888-07	SYSTEM	1
33079538-c27e-4d09-b80b-34598f441ca7	PATIENT_003	2024-02-29 06:15:00-08	week_4	5.0	4.5	6.0	3.5	5.0	2.5	5.5	6.0	{left_shoulder}	{mild_stiffness}	self_report	patient	DR_WILLIAMS	complete	\N	2025-06-19 18:55:38.968632-07	2025-06-19 18:55:38.968632-07	SYSTEM	1
\.


--
-- TOC entry 5404 (class 0 OID 27561)
-- Dependencies: 236
-- Data for Name: quality_of_life; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.quality_of_life (id, patient_id, assessment_date, measurement_timing, general_health, physical_functioning, role_physical, bodily_pain, vitality, social_functioning, role_emotional, mental_health, sleep_quality, work_productivity, relationship_satisfaction, life_satisfaction, days_per_week_exercise, minutes_per_day_exercise, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
38f88b78-092a-45e0-8ce7-492e186fcf01	PATIENT_001	2024-01-15 01:00:00-08	baseline	3	2	3	2	3	3	3	3	5.0	6.0	7.0	6.0	2	20	DR_SMITH	complete	\N	2025-06-19 18:55:39.020377-07	2025-06-19 18:55:39.020377-07	SYSTEM	1
9bcfbbf3-a7a4-4e4b-bf9b-679e98832f4e	PATIENT_001	2024-04-08 02:00:00-07	week_12	4	3	4	4	4	4	4	4	7.5	8.0	8.5	8.0	4	30	DR_SMITH	complete	\N	2025-06-19 18:55:39.031528-07	2025-06-19 18:55:39.031528-07	SYSTEM	1
120a30b6-fb30-417a-9bcb-5c6b65bf0fdf	PATIENT_002	2024-01-20 02:30:00-08	baseline	2	1	2	1	2	2	2	2	3.0	4.0	5.0	4.0	0	0	DR_JOHNSON	complete	\N	2025-06-19 18:55:39.03225-07	2025-06-19 18:55:39.03225-07	SYSTEM	1
\.


--
-- TOC entry 5406 (class 0 OID 27628)
-- Dependencies: 238
-- Data for Name: treatment_satisfaction; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.treatment_satisfaction (id, patient_id, assessment_date, measurement_timing, overall_satisfaction, would_recommend, would_continue, pain_relief_satisfaction, function_improvement_satisfaction, side_effect_tolerance, treatment_burden, convenience, provider_communication, care_coordination, expectations_met, most_helpful_aspect, least_helpful_aspect, suggestions_for_improvement, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
dee49331-ac39-46a6-88a0-2f8d170c9ebb	PATIENT_001	2024-04-08 02:00:00-07	week_12	8.5	t	t	8.0	8.5	7.5	6.0	8.0	9.0	8.5	8.0	Reduced pain and improved mobility	Medication side effects	Consider alternative pain medications with fewer side effects	DR_SMITH	complete	\N	2025-06-19 18:55:39.050992-07	2025-06-19 18:55:39.050992-07	SYSTEM	1
\.


--
-- TOC entry 5405 (class 0 OID 27595)
-- Dependencies: 237
-- Data for Name: weekly_symptom_tracking; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.weekly_symptom_tracking (id, patient_id, report_date, week_number, average_pain_week, worst_pain_week, pain_free_days, activity_limitation_days, missed_work_days, fatigue_level, mood_rating, anxiety_level, treatment_helpfulness, side_effects_this_week, global_improvement, data_source, data_quality, notes, created_at, updated_at, version) FROM stdin;
043a8321-3514-4450-a182-f8312bc2fe46	PATIENT_001	2024-01-22 10:00:00-08	1	7.5	9.0	0	5	2	6.0	5.0	4.0	6.0	{stomach_upset}	4	patient_app	complete	\N	2025-06-19 18:55:39.034338-07	2025-06-19 18:55:39.034338-07	1
6e5ad5d5-39b8-495a-81b1-87bec14729c5	PATIENT_001	2024-01-29 10:00:00-08	2	7.0	8.5	1	4	1	5.5	5.5	3.5	6.5	{mild_stomach_upset}	3	patient_app	complete	\N	2025-06-19 18:55:39.037669-07	2025-06-19 18:55:39.037669-07	1
17e0a158-4d40-4dbb-86c6-fcc6bc049ec1	PATIENT_001	2024-02-05 10:00:00-08	3	6.5	8.0	1	3	1	5.0	6.0	3.0	7.0	{mild_stomach_upset}	3	patient_app	complete	\N	2025-06-19 18:55:39.048429-07	2025-06-19 18:55:39.048429-07	1
58eb2718-e245-42fa-96ca-c1341727c27f	PATIENT_001	2024-02-12 10:00:00-08	4	6.0	7.5	2	2	0	4.5	6.5	2.5	7.5	{mild_stomach_upset}	2	patient_app	complete	\N	2025-06-19 18:55:39.049335-07	2025-06-19 18:55:39.049335-07	1
\.


--
-- TOC entry 5400 (class 0 OID 27412)
-- Dependencies: 232
-- Data for Name: womac_assessments; Type: TABLE DATA; Schema: clinical_outcomes; Owner: postgres
--

COPY clinical_outcomes.womac_assessments (id, patient_id, assessment_date, measurement_timing, pain_walking, pain_stairs, pain_night_bed, pain_sitting, pain_standing, stiffness_waking, stiffness_later_day, function_stairs_down, function_stairs_up, function_rising_sitting, function_standing, function_bending, function_walking_flat, function_getting_in_out_car, function_shopping, function_socks, function_rising_bed, function_socks_off, function_lying_bed, function_bath_shower, function_sitting, function_toilet, function_heavy_domestic, function_light_domestic, assessor_id, data_quality, notes, created_at, updated_at, created_by, version) FROM stdin;
\.


--
-- TOC entry 5396 (class 0 OID 25691)
-- Dependencies: 226
-- Data for Name: allergies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.allergies (allergy_id, patient_id, allergen, allergy_type, severity, reaction, onset_date, status, notes, recorded_by, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5392 (class 0 OID 25617)
-- Dependencies: 222
-- Data for Name: appointments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.appointments (appointment_id, patient_id, provider_id, appointment_date, appointment_time, duration_minutes, appointment_type, status, reason_for_visit, notes, room_number, created_by, created_at, updated_at) FROM stdin;
e5502377-83b4-4e47-b672-fa087ffa508f	151733f9-6109-4053-bfc8-af0237c3eded	4e00566c-f82c-4ab1-a263-e63cd04cdc05	2024-06-10	14:30:00	45	follow-up	scheduled	Annual physical examination	Patient scheduled for comprehensive physical	Room 205	\N	2025-06-07 16:48:08.745827-07	2025-06-07 16:48:08.745827-07
\.


--
-- TOC entry 5387 (class 0 OID 25297)
-- Dependencies: 217
-- Data for Name: clinical_observations; Type: TABLE DATA; Schema: public; Owner: abena_user
--

COPY public.clinical_observations (observation_id, patient_id, observation_type, value_numeric, value_text, unit, recorded_at, recorded_by, source_system, created_at) FROM stdin;
\.


--
-- TOC entry 5394 (class 0 OID 25655)
-- Dependencies: 224
-- Data for Name: diagnoses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.diagnoses (diagnosis_id, patient_id, provider_id, record_id, icd10_code, diagnosis_description, diagnosis_type, onset_date, resolution_date, status, notes, created_at, updated_at) FROM stdin;
23748df4-0ba0-449e-8175-cb14076dde78	151733f9-6109-4053-bfc8-af0237c3eded	4e00566c-f82c-4ab1-a263-e63cd04cdc05	992faf9a-facd-459e-8fd5-b1ff13f782d0	Z00.00	Encounter for general adult medical examination without abnormal findings	primary	2024-06-10	\N	active	Annual physical examination completed without abnormal findings	2025-06-07 16:48:08.777559-07	2025-06-07 16:48:08.777559-07
\.


--
-- TOC entry 5388 (class 0 OID 25306)
-- Dependencies: 218
-- Data for Name: lab_results; Type: TABLE DATA; Schema: public; Owner: abena_user
--

COPY public.lab_results (result_id, patient_id, test_name, test_code, result_value, result_text, unit, reference_range, abnormal_flag, test_date, lab_name, created_at) FROM stdin;
\.


--
-- TOC entry 5393 (class 0 OID 25634)
-- Dependencies: 223
-- Data for Name: medical_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.medical_records (record_id, patient_id, provider_id, appointment_id, visit_date, chief_complaint, history_of_present_illness, review_of_systems, physical_examination, assessment_and_plan, follow_up_instructions, is_signed, signed_at, signed_by, created_at, updated_at) FROM stdin;
992faf9a-facd-459e-8fd5-b1ff13f782d0	151733f9-6109-4053-bfc8-af0237c3eded	4e00566c-f82c-4ab1-a263-e63cd04cdc05	e5502377-83b4-4e47-b672-fa087ffa508f	2024-06-10 07:30:00-07	Annual physical examination	Patient presents for routine annual physical. Reports feeling well overall with no acute complaints.	{"respiratory": "No shortness of breath or cough", "cardiovascular": "No chest pain or palpitations", "constitutional": "No fever, chills, or weight loss"}	{"vitals": "See vital signs", "general": "Well-appearing, alert and oriented", "respiratory": "Clear to auscultation bilaterally", "cardiovascular": "Regular rate and rhythm, no murmurs"}	Healthy adult. Continue current lifestyle. Return for annual visit in 12 months.	Schedule mammogram and colonoscopy per guidelines. Return in 1 year or as needed.	f	\N	\N	2025-06-07 16:48:08.755614-07	2025-06-07 16:48:08.755614-07
\.


--
-- TOC entry 5389 (class 0 OID 25315)
-- Dependencies: 219
-- Data for Name: medications; Type: TABLE DATA; Schema: public; Owner: abena_user
--

COPY public.medications (medication_id, patient_id, medication_name, dosage, frequency, start_date, end_date, prescribing_physician, status, created_at) FROM stdin;
\.


--
-- TOC entry 5398 (class 0 OID 26131)
-- Dependencies: 228
-- Data for Name: outcomes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.outcomes (outcome_id, patient_id, medical_record_id, provider_id, outcome_type, outcome_category, severity_level, outcome_description, outcome_measure, baseline_value, outcome_value, improvement_percentage, related_diagnosis, related_procedure_id, related_medication_id, treatment_plan_id, outcome_date, follow_up_period, time_to_outcome_days, assessment_method, assessment_tools, measured_by, patient_satisfaction_score, functional_improvement, pain_score_change, mobility_improvement, outcome_status, is_expected_outcome, requires_intervention, intervention_provided, follow_up_required, next_assessment_date, follow_up_notes, data_source, confidence_level, notes, metadata, created_at, updated_at, created_by, updated_by) FROM stdin;
30e1fa56-097d-4bbf-9059-fef3c45d4e58	550e8400-e29b-41d4-a716-446655440001	\N	\N	treatment_response	positive	resolved	Complete recovery from pneumonia with full lung function restoration	Oxygen Saturation	85.00	98.00	15.30	Community-acquired pneumonia	\N	\N	\N	2025-06-05 13:22:05.755006-07	30_days	\N	Chest X-ray and pulmonary function tests	\N	\N	9.2	t	\N	\N	resolved	t	f	\N	f	\N	\N	clinical_assessment	\N	\N	{}	2025-06-10 13:22:05.755006-07	2025-06-10 13:22:05.755006-07	\N	\N
1ea30a46-46d6-4d33-ba89-98e425457205	550e8400-e29b-41d4-a716-446655440002	\N	\N	surgical_outcome	positive	mild	Successful appendectomy with minimal complications	Recovery Time	7.00	3.00	57.10	Acute appendicitis	\N	\N	\N	2025-05-31 13:22:05.755006-07	6_months	\N	Clinical examination and imaging	\N	\N	8.8	t	\N	\N	resolved	t	f	\N	f	\N	\N	clinical_assessment	\N	\N	{}	2025-06-10 13:22:05.755006-07	2025-06-10 13:22:05.755006-07	\N	\N
5ffb4b7b-60c2-4b72-b756-ea1a236dbd84	550e8400-e29b-41d4-a716-446655440003	\N	\N	medication_response	positive	moderate	Significant blood pressure reduction with ACE inhibitor	Systolic BP	160.00	125.00	21.90	Hypertension	\N	\N	\N	2025-05-26 13:22:05.755006-07	3_months	\N	Blood pressure monitoring	\N	\N	8.5	t	\N	\N	stable	t	f	\N	f	\N	\N	clinical_assessment	\N	\N	{}	2025-06-10 13:22:05.755006-07	2025-06-10 13:22:05.755006-07	\N	\N
927fc72b-445d-4d5f-ac7c-be4b5eb061af	550e8400-e29b-41d4-a716-446655440004	\N	\N	quality_of_life	positive	mild	Improved mobility and reduced pain after physical therapy	Pain Scale	8.00	3.00	62.50	Chronic lower back pain	\N	\N	\N	2025-05-21 13:22:05.755006-07	6_months	\N	SF-36 questionnaire and pain assessment	\N	\N	9.0	t	\N	\N	ongoing	t	f	\N	f	\N	\N	clinical_assessment	\N	\N	{}	2025-06-10 13:22:05.755006-07	2025-06-10 13:22:05.755006-07	\N	\N
866a7b77-d5a3-449b-b161-11de5da53081	550e8400-e29b-41d4-a716-446655440005	\N	\N	adverse_event	negative	moderate	Allergic reaction to prescribed antibiotic	Reaction Severity	0.00	6.00	-100.00	Urinary tract infection	\N	\N	\N	2025-06-07 13:22:05.755006-07	1_month	\N	Clinical observation and allergy testing	\N	\N	6.5	f	\N	\N	resolved	f	f	\N	f	\N	\N	clinical_assessment	\N	\N	{}	2025-06-10 13:22:05.755006-07	2025-06-10 13:22:05.755006-07	\N	\N
\.


--
-- TOC entry 5397 (class 0 OID 25702)
-- Dependencies: 227
-- Data for Name: procedures; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.procedures (procedure_id, patient_id, provider_id, record_id, procedure_name, cpt_code, procedure_date, location, status, notes, complications, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5391 (class 0 OID 25604)
-- Dependencies: 221
-- Data for Name: providers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.providers (provider_id, npi_number, license_number, first_name, last_name, title, specialization, department, phone, email, is_active, hire_date, license_expiry_date, created_at, updated_at) FROM stdin;
4e00566c-f82c-4ab1-a263-e63cd04cdc05	1234567890	MD12345	Dr. Sarah	Wilson	MD	Internal Medicine	Internal Medicine	555-DOC-TOR	dr.wilson@abena.com	t	2020-01-15	2025-12-31	2025-06-07 16:48:08.670604-07	2025-06-07 16:48:08.670604-07
\.


--
-- TOC entry 5390 (class 0 OID 25325)
-- Dependencies: 220
-- Data for Name: risk_scores; Type: TABLE DATA; Schema: public; Owner: abena_user
--

COPY public.risk_scores (score_id, patient_id, risk_type, score_value, risk_level, calculated_at, model_version, factors_considered, created_at) FROM stdin;
\.


--
-- TOC entry 5395 (class 0 OID 25676)
-- Dependencies: 225
-- Data for Name: vital_signs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vital_signs (vital_id, patient_id, recorded_by, record_id, recorded_at, height_cm, weight_kg, bmi, temperature_c, blood_pressure_systolic, blood_pressure_diastolic, heart_rate, respiratory_rate, oxygen_saturation, pain_scale, notes) FROM stdin;
75688026-32d0-45a2-b5c3-d568b2244c2d	357af4b8-8032-4dbd-b50b-d2650f2b70e2	\N	\N	2025-06-07 16:44:39.541708-07	165.00	63.50	23.3	37.0	120	80	72	16	99	0	All vital signs within normal limits
2329710d-b4cf-4326-9a73-36c8ce7e7c27	151733f9-6109-4053-bfc8-af0237c3eded	4e00566c-f82c-4ab1-a263-e63cd04cdc05	992faf9a-facd-459e-8fd5-b1ff13f782d0	2025-06-07 16:48:08.764208-07	168.00	65.50	23.2	36.8	118	75	68	14	98	0	All vital signs within normal limits
\.


--
-- TOC entry 5202 (class 2606 OID 27675)
-- Name: assessment_schedules assessment_schedules_patient_id_key; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.assessment_schedules
    ADD CONSTRAINT assessment_schedules_patient_id_key UNIQUE (patient_id);


--
-- TOC entry 5204 (class 2606 OID 27673)
-- Name: assessment_schedules assessment_schedules_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.assessment_schedules
    ADD CONSTRAINT assessment_schedules_pkey PRIMARY KEY (id);


--
-- TOC entry 5178 (class 2606 OID 27558)
-- Name: healthcare_utilization healthcare_utilization_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.healthcare_utilization
    ADD CONSTRAINT healthcare_utilization_pkey PRIMARY KEY (id);


--
-- TOC entry 5174 (class 2606 OID 27512)
-- Name: medication_usage medication_usage_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.medication_usage
    ADD CONSTRAINT medication_usage_pkey PRIMARY KEY (id);


--
-- TOC entry 5168 (class 2606 OID 27478)
-- Name: odi_assessments odi_assessments_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.odi_assessments
    ADD CONSTRAINT odi_assessments_pkey PRIMARY KEY (id);


--
-- TOC entry 5211 (class 2606 OID 27685)
-- Name: outcome_changes outcome_changes_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.outcome_changes
    ADD CONSTRAINT outcome_changes_pkey PRIMARY KEY (id);


--
-- TOC entry 5154 (class 2606 OID 27409)
-- Name: pain_assessments pain_assessments_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.pain_assessments
    ADD CONSTRAINT pain_assessments_pkey PRIMARY KEY (id);


--
-- TOC entry 5186 (class 2606 OID 27592)
-- Name: quality_of_life quality_of_life_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.quality_of_life
    ADD CONSTRAINT quality_of_life_pkey PRIMARY KEY (id);


--
-- TOC entry 5198 (class 2606 OID 27652)
-- Name: treatment_satisfaction treatment_satisfaction_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.treatment_satisfaction
    ADD CONSTRAINT treatment_satisfaction_pkey PRIMARY KEY (id);


--
-- TOC entry 5156 (class 2606 OID 27411)
-- Name: pain_assessments unique_patient_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.pain_assessments
    ADD CONSTRAINT unique_patient_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- TOC entry 5213 (class 2606 OID 27687)
-- Name: outcome_changes unique_patient_comparison; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.outcome_changes
    ADD CONSTRAINT unique_patient_comparison UNIQUE (patient_id, baseline_date, comparison_date);


--
-- TOC entry 5176 (class 2606 OID 27514)
-- Name: medication_usage unique_patient_medication_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.medication_usage
    ADD CONSTRAINT unique_patient_medication_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- TOC entry 5170 (class 2606 OID 27480)
-- Name: odi_assessments unique_patient_odi_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.odi_assessments
    ADD CONSTRAINT unique_patient_odi_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- TOC entry 5188 (class 2606 OID 27594)
-- Name: quality_of_life unique_patient_qol_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.quality_of_life
    ADD CONSTRAINT unique_patient_qol_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- TOC entry 5200 (class 2606 OID 27654)
-- Name: treatment_satisfaction unique_patient_satisfaction_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.treatment_satisfaction
    ADD CONSTRAINT unique_patient_satisfaction_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- TOC entry 5182 (class 2606 OID 27560)
-- Name: healthcare_utilization unique_patient_utilization_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.healthcare_utilization
    ADD CONSTRAINT unique_patient_utilization_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- TOC entry 5192 (class 2606 OID 27627)
-- Name: weekly_symptom_tracking unique_patient_week; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.weekly_symptom_tracking
    ADD CONSTRAINT unique_patient_week UNIQUE (patient_id, week_number);


--
-- TOC entry 5161 (class 2606 OID 27454)
-- Name: womac_assessments unique_patient_womac_assessment; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.womac_assessments
    ADD CONSTRAINT unique_patient_womac_assessment UNIQUE (patient_id, measurement_timing, assessment_date);


--
-- TOC entry 5194 (class 2606 OID 27625)
-- Name: weekly_symptom_tracking weekly_symptom_tracking_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.weekly_symptom_tracking
    ADD CONSTRAINT weekly_symptom_tracking_pkey PRIMARY KEY (id);


--
-- TOC entry 5163 (class 2606 OID 27452)
-- Name: womac_assessments womac_assessments_pkey; Type: CONSTRAINT; Schema: clinical_outcomes; Owner: postgres
--

ALTER TABLE ONLY clinical_outcomes.womac_assessments
    ADD CONSTRAINT womac_assessments_pkey PRIMARY KEY (id);


--
-- TOC entry 5129 (class 2606 OID 25701)
-- Name: allergies allergies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allergies
    ADD CONSTRAINT allergies_pkey PRIMARY KEY (allergy_id);


--
-- TOC entry 5110 (class 2606 OID 25628)
-- Name: appointments appointments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (appointment_id);


--
-- TOC entry 5087 (class 2606 OID 25305)
-- Name: clinical_observations clinical_observations_pkey; Type: CONSTRAINT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.clinical_observations
    ADD CONSTRAINT clinical_observations_pkey PRIMARY KEY (observation_id);


--
-- TOC entry 5121 (class 2606 OID 25665)
-- Name: diagnoses diagnoses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.diagnoses
    ADD CONSTRAINT diagnoses_pkey PRIMARY KEY (diagnosis_id);


--
-- TOC entry 5094 (class 2606 OID 25314)
-- Name: lab_results lab_results_pkey; Type: CONSTRAINT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.lab_results
    ADD CONSTRAINT lab_results_pkey PRIMARY KEY (result_id);


--
-- TOC entry 5119 (class 2606 OID 25644)
-- Name: medical_records medical_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medical_records
    ADD CONSTRAINT medical_records_pkey PRIMARY KEY (record_id);


--
-- TOC entry 5098 (class 2606 OID 25324)
-- Name: medications medications_pkey; Type: CONSTRAINT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.medications
    ADD CONSTRAINT medications_pkey PRIMARY KEY (medication_id);


--
-- TOC entry 5149 (class 2606 OID 26152)
-- Name: outcomes outcomes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.outcomes
    ADD CONSTRAINT outcomes_pkey PRIMARY KEY (outcome_id);


--
-- TOC entry 5135 (class 2606 OID 25712)
-- Name: procedures procedures_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT procedures_pkey PRIMARY KEY (procedure_id);


--
-- TOC entry 5106 (class 2606 OID 25616)
-- Name: providers providers_npi_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.providers
    ADD CONSTRAINT providers_npi_number_key UNIQUE (npi_number);


--
-- TOC entry 5108 (class 2606 OID 25614)
-- Name: providers providers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.providers
    ADD CONSTRAINT providers_pkey PRIMARY KEY (provider_id);


--
-- TOC entry 5102 (class 2606 OID 25333)
-- Name: risk_scores risk_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.risk_scores
    ADD CONSTRAINT risk_scores_pkey PRIMARY KEY (score_id);


--
-- TOC entry 5127 (class 2606 OID 25685)
-- Name: vital_signs vital_signs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vital_signs
    ADD CONSTRAINT vital_signs_pkey PRIMARY KEY (vital_id);


--
-- TOC entry 5205 (class 1259 OID 27708)
-- Name: idx_assessment_schedules_baseline; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_assessment_schedules_baseline ON clinical_outcomes.assessment_schedules USING btree (baseline_date);


--
-- TOC entry 5206 (class 1259 OID 27707)
-- Name: idx_assessment_schedules_patient; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_assessment_schedules_patient ON clinical_outcomes.assessment_schedules USING btree (patient_id);


--
-- TOC entry 5207 (class 1259 OID 27709)
-- Name: idx_compliance_rate; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_compliance_rate ON clinical_outcomes.assessment_schedules USING btree (compliance_rate);


--
-- TOC entry 5179 (class 1259 OID 27700)
-- Name: idx_healthcare_total_visits; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_healthcare_total_visits ON clinical_outcomes.healthcare_utilization USING btree (total_visits);


--
-- TOC entry 5180 (class 1259 OID 27699)
-- Name: idx_healthcare_utilization_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_healthcare_utilization_patient_date ON clinical_outcomes.healthcare_utilization USING btree (patient_id, assessment_date);


--
-- TOC entry 5171 (class 1259 OID 27698)
-- Name: idx_medication_adherence; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_medication_adherence ON clinical_outcomes.medication_usage USING btree (adherence_percentage);


--
-- TOC entry 5172 (class 1259 OID 27697)
-- Name: idx_medication_usage_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_medication_usage_patient_date ON clinical_outcomes.medication_usage USING btree (patient_id, assessment_date);


--
-- TOC entry 5164 (class 1259 OID 27694)
-- Name: idx_odi_assessments_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_odi_assessments_patient_date ON clinical_outcomes.odi_assessments USING btree (patient_id, assessment_date);


--
-- TOC entry 5165 (class 1259 OID 27695)
-- Name: idx_odi_assessments_timing; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_odi_assessments_timing ON clinical_outcomes.odi_assessments USING btree (measurement_timing);


--
-- TOC entry 5166 (class 1259 OID 27696)
-- Name: idx_odi_percentage; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_odi_percentage ON clinical_outcomes.odi_assessments USING btree (percentage_disability);


--
-- TOC entry 5208 (class 1259 OID 27711)
-- Name: idx_outcome_changes_dates; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_outcome_changes_dates ON clinical_outcomes.outcome_changes USING btree (baseline_date, comparison_date);


--
-- TOC entry 5209 (class 1259 OID 27710)
-- Name: idx_outcome_changes_patient; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_outcome_changes_patient ON clinical_outcomes.outcome_changes USING btree (patient_id);


--
-- TOC entry 5150 (class 1259 OID 27688)
-- Name: idx_pain_assessments_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_pain_assessments_patient_date ON clinical_outcomes.pain_assessments USING btree (patient_id, assessment_date);


--
-- TOC entry 5151 (class 1259 OID 27690)
-- Name: idx_pain_assessments_quality; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_pain_assessments_quality ON clinical_outcomes.pain_assessments USING btree (data_quality);


--
-- TOC entry 5152 (class 1259 OID 27689)
-- Name: idx_pain_assessments_timing; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_pain_assessments_timing ON clinical_outcomes.pain_assessments USING btree (measurement_timing);


--
-- TOC entry 5183 (class 1259 OID 27702)
-- Name: idx_qol_life_satisfaction; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_qol_life_satisfaction ON clinical_outcomes.quality_of_life USING btree (life_satisfaction);


--
-- TOC entry 5184 (class 1259 OID 27701)
-- Name: idx_quality_of_life_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_quality_of_life_patient_date ON clinical_outcomes.quality_of_life USING btree (patient_id, assessment_date);


--
-- TOC entry 5195 (class 1259 OID 27706)
-- Name: idx_satisfaction_overall; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_satisfaction_overall ON clinical_outcomes.treatment_satisfaction USING btree (overall_satisfaction);


--
-- TOC entry 5196 (class 1259 OID 27705)
-- Name: idx_treatment_satisfaction_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_treatment_satisfaction_patient_date ON clinical_outcomes.treatment_satisfaction USING btree (patient_id, assessment_date);


--
-- TOC entry 5189 (class 1259 OID 27704)
-- Name: idx_weekly_symptoms_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_weekly_symptoms_date ON clinical_outcomes.weekly_symptom_tracking USING btree (report_date);


--
-- TOC entry 5190 (class 1259 OID 27703)
-- Name: idx_weekly_symptoms_patient_week; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_weekly_symptoms_patient_week ON clinical_outcomes.weekly_symptom_tracking USING btree (patient_id, week_number);


--
-- TOC entry 5157 (class 1259 OID 27691)
-- Name: idx_womac_assessments_patient_date; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_womac_assessments_patient_date ON clinical_outcomes.womac_assessments USING btree (patient_id, assessment_date);


--
-- TOC entry 5158 (class 1259 OID 27692)
-- Name: idx_womac_assessments_timing; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_womac_assessments_timing ON clinical_outcomes.womac_assessments USING btree (measurement_timing);


--
-- TOC entry 5159 (class 1259 OID 27693)
-- Name: idx_womac_total_score; Type: INDEX; Schema: clinical_outcomes; Owner: postgres
--

CREATE INDEX idx_womac_total_score ON clinical_outcomes.womac_assessments USING btree (total_score);


--
-- TOC entry 5130 (class 1259 OID 25738)
-- Name: idx_allergies_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_allergies_patient_id ON public.allergies USING btree (patient_id);


--
-- TOC entry 5131 (class 1259 OID 25739)
-- Name: idx_allergies_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_allergies_status ON public.allergies USING btree (status);


--
-- TOC entry 5111 (class 1259 OID 25727)
-- Name: idx_appointments_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_appointments_date ON public.appointments USING btree (appointment_date);


--
-- TOC entry 5112 (class 1259 OID 25725)
-- Name: idx_appointments_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_appointments_patient_id ON public.appointments USING btree (patient_id);


--
-- TOC entry 5113 (class 1259 OID 25726)
-- Name: idx_appointments_provider_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_appointments_provider_id ON public.appointments USING btree (provider_id);


--
-- TOC entry 5114 (class 1259 OID 25728)
-- Name: idx_appointments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_appointments_status ON public.appointments USING btree (status);


--
-- TOC entry 5122 (class 1259 OID 25733)
-- Name: idx_diagnoses_icd10; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_diagnoses_icd10 ON public.diagnoses USING btree (icd10_code);


--
-- TOC entry 5123 (class 1259 OID 25732)
-- Name: idx_diagnoses_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_diagnoses_patient_id ON public.diagnoses USING btree (patient_id);


--
-- TOC entry 5091 (class 1259 OID 25378)
-- Name: idx_lab_results_patient_id; Type: INDEX; Schema: public; Owner: abena_user
--

CREATE INDEX idx_lab_results_patient_id ON public.lab_results USING btree (patient_id);


--
-- TOC entry 5092 (class 1259 OID 25379)
-- Name: idx_lab_results_test_date; Type: INDEX; Schema: public; Owner: abena_user
--

CREATE INDEX idx_lab_results_test_date ON public.lab_results USING btree (test_date);


--
-- TOC entry 5115 (class 1259 OID 25729)
-- Name: idx_medical_records_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_medical_records_patient_id ON public.medical_records USING btree (patient_id);


--
-- TOC entry 5116 (class 1259 OID 25730)
-- Name: idx_medical_records_provider_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_medical_records_provider_id ON public.medical_records USING btree (provider_id);


--
-- TOC entry 5117 (class 1259 OID 25731)
-- Name: idx_medical_records_visit_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_medical_records_visit_date ON public.medical_records USING btree (visit_date);


--
-- TOC entry 5095 (class 1259 OID 25734)
-- Name: idx_medications_patient_id; Type: INDEX; Schema: public; Owner: abena_user
--

CREATE INDEX idx_medications_patient_id ON public.medications USING btree (patient_id);


--
-- TOC entry 5096 (class 1259 OID 25735)
-- Name: idx_medications_status; Type: INDEX; Schema: public; Owner: abena_user
--

CREATE INDEX idx_medications_status ON public.medications USING btree (status);


--
-- TOC entry 5088 (class 1259 OID 25375)
-- Name: idx_observations_patient_id; Type: INDEX; Schema: public; Owner: abena_user
--

CREATE INDEX idx_observations_patient_id ON public.clinical_observations USING btree (patient_id);


--
-- TOC entry 5089 (class 1259 OID 25377)
-- Name: idx_observations_recorded_at; Type: INDEX; Schema: public; Owner: abena_user
--

CREATE INDEX idx_observations_recorded_at ON public.clinical_observations USING btree (recorded_at);


--
-- TOC entry 5090 (class 1259 OID 25376)
-- Name: idx_observations_type; Type: INDEX; Schema: public; Owner: abena_user
--

CREATE INDEX idx_observations_type ON public.clinical_observations USING btree (observation_type);


--
-- TOC entry 5136 (class 1259 OID 26164)
-- Name: idx_outcomes_category_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outcomes_category_date ON public.outcomes USING btree (outcome_category, outcome_date DESC);


--
-- TOC entry 5137 (class 1259 OID 26161)
-- Name: idx_outcomes_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outcomes_created_at ON public.outcomes USING btree (created_at DESC);


--
-- TOC entry 5138 (class 1259 OID 26160)
-- Name: idx_outcomes_medical_record; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outcomes_medical_record ON public.outcomes USING btree (medical_record_id);


--
-- TOC entry 5139 (class 1259 OID 26156)
-- Name: idx_outcomes_outcome_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outcomes_outcome_category ON public.outcomes USING btree (outcome_category);


--
-- TOC entry 5140 (class 1259 OID 26154)
-- Name: idx_outcomes_outcome_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outcomes_outcome_date ON public.outcomes USING btree (outcome_date DESC);


--
-- TOC entry 5141 (class 1259 OID 26158)
-- Name: idx_outcomes_outcome_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outcomes_outcome_status ON public.outcomes USING btree (outcome_status);


--
-- TOC entry 5142 (class 1259 OID 26155)
-- Name: idx_outcomes_outcome_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outcomes_outcome_type ON public.outcomes USING btree (outcome_type);


--
-- TOC entry 5143 (class 1259 OID 26162)
-- Name: idx_outcomes_patient_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outcomes_patient_date ON public.outcomes USING btree (patient_id, outcome_date DESC);


--
-- TOC entry 5144 (class 1259 OID 26153)
-- Name: idx_outcomes_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outcomes_patient_id ON public.outcomes USING btree (patient_id);


--
-- TOC entry 5145 (class 1259 OID 26159)
-- Name: idx_outcomes_provider_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outcomes_provider_id ON public.outcomes USING btree (provider_id);


--
-- TOC entry 5146 (class 1259 OID 26157)
-- Name: idx_outcomes_severity_level; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outcomes_severity_level ON public.outcomes USING btree (severity_level);


--
-- TOC entry 5147 (class 1259 OID 26163)
-- Name: idx_outcomes_type_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outcomes_type_status ON public.outcomes USING btree (outcome_type, outcome_status);


--
-- TOC entry 5132 (class 1259 OID 25740)
-- Name: idx_procedures_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_procedures_patient_id ON public.procedures USING btree (patient_id);


--
-- TOC entry 5133 (class 1259 OID 25741)
-- Name: idx_procedures_provider_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_procedures_provider_id ON public.procedures USING btree (provider_id);


--
-- TOC entry 5103 (class 1259 OID 25724)
-- Name: idx_providers_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_providers_active ON public.providers USING btree (is_active);


--
-- TOC entry 5104 (class 1259 OID 25723)
-- Name: idx_providers_npi; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_providers_npi ON public.providers USING btree (npi_number);


--
-- TOC entry 5099 (class 1259 OID 25381)
-- Name: idx_risk_scores_calculated_at; Type: INDEX; Schema: public; Owner: abena_user
--

CREATE INDEX idx_risk_scores_calculated_at ON public.risk_scores USING btree (calculated_at);


--
-- TOC entry 5100 (class 1259 OID 25380)
-- Name: idx_risk_scores_patient_id; Type: INDEX; Schema: public; Owner: abena_user
--

CREATE INDEX idx_risk_scores_patient_id ON public.risk_scores USING btree (patient_id);


--
-- TOC entry 5124 (class 1259 OID 25736)
-- Name: idx_vital_signs_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vital_signs_patient_id ON public.vital_signs USING btree (patient_id);


--
-- TOC entry 5125 (class 1259 OID 25737)
-- Name: idx_vital_signs_recorded_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vital_signs_recorded_at ON public.vital_signs USING btree (recorded_at);


--
-- TOC entry 5238 (class 2620 OID 27735)
-- Name: assessment_schedules update_assessment_schedules_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_assessment_schedules_updated_at BEFORE UPDATE ON clinical_outcomes.assessment_schedules FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5234 (class 2620 OID 27731)
-- Name: healthcare_utilization update_healthcare_utilization_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_healthcare_utilization_updated_at BEFORE UPDATE ON clinical_outcomes.healthcare_utilization FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5233 (class 2620 OID 27730)
-- Name: medication_usage update_medication_usage_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_medication_usage_updated_at BEFORE UPDATE ON clinical_outcomes.medication_usage FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5232 (class 2620 OID 27729)
-- Name: odi_assessments update_odi_assessments_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_odi_assessments_updated_at BEFORE UPDATE ON clinical_outcomes.odi_assessments FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5230 (class 2620 OID 27727)
-- Name: pain_assessments update_pain_assessments_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_pain_assessments_updated_at BEFORE UPDATE ON clinical_outcomes.pain_assessments FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5235 (class 2620 OID 27732)
-- Name: quality_of_life update_quality_of_life_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_quality_of_life_updated_at BEFORE UPDATE ON clinical_outcomes.quality_of_life FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5237 (class 2620 OID 27734)
-- Name: treatment_satisfaction update_treatment_satisfaction_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_treatment_satisfaction_updated_at BEFORE UPDATE ON clinical_outcomes.treatment_satisfaction FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5236 (class 2620 OID 27733)
-- Name: weekly_symptom_tracking update_weekly_symptom_tracking_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_weekly_symptom_tracking_updated_at BEFORE UPDATE ON clinical_outcomes.weekly_symptom_tracking FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5231 (class 2620 OID 27728)
-- Name: womac_assessments update_womac_assessments_updated_at; Type: TRIGGER; Schema: clinical_outcomes; Owner: postgres
--

CREATE TRIGGER update_womac_assessments_updated_at BEFORE UPDATE ON clinical_outcomes.womac_assessments FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5229 (class 2620 OID 26166)
-- Name: outcomes outcomes_update_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER outcomes_update_timestamp BEFORE UPDATE ON public.outcomes FOR EACH ROW EXECUTE FUNCTION public.update_outcomes_timestamp();


--
-- TOC entry 5227 (class 2620 OID 25747)
-- Name: allergies update_allergies_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_allergies_updated_at BEFORE UPDATE ON public.allergies FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5224 (class 2620 OID 25743)
-- Name: appointments update_appointments_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON public.appointments FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5226 (class 2620 OID 25745)
-- Name: diagnoses update_diagnoses_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_diagnoses_updated_at BEFORE UPDATE ON public.diagnoses FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5225 (class 2620 OID 25744)
-- Name: medical_records update_medical_records_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_medical_records_updated_at BEFORE UPDATE ON public.medical_records FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5222 (class 2620 OID 25746)
-- Name: medications update_medications_updated_at; Type: TRIGGER; Schema: public; Owner: abena_user
--

CREATE TRIGGER update_medications_updated_at BEFORE UPDATE ON public.medications FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5228 (class 2620 OID 25748)
-- Name: procedures update_procedures_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_procedures_updated_at BEFORE UPDATE ON public.procedures FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5223 (class 2620 OID 25742)
-- Name: providers update_providers_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_providers_updated_at BEFORE UPDATE ON public.providers FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5214 (class 2606 OID 25629)
-- Name: appointments appointments_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.providers(provider_id);


--
-- TOC entry 5217 (class 2606 OID 25666)
-- Name: diagnoses diagnoses_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.diagnoses
    ADD CONSTRAINT diagnoses_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.providers(provider_id);


--
-- TOC entry 5218 (class 2606 OID 25671)
-- Name: diagnoses diagnoses_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.diagnoses
    ADD CONSTRAINT diagnoses_record_id_fkey FOREIGN KEY (record_id) REFERENCES public.medical_records(record_id);


--
-- TOC entry 5215 (class 2606 OID 25650)
-- Name: medical_records medical_records_appointment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medical_records
    ADD CONSTRAINT medical_records_appointment_id_fkey FOREIGN KEY (appointment_id) REFERENCES public.appointments(appointment_id);


--
-- TOC entry 5216 (class 2606 OID 25645)
-- Name: medical_records medical_records_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medical_records
    ADD CONSTRAINT medical_records_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.providers(provider_id);


--
-- TOC entry 5220 (class 2606 OID 25713)
-- Name: procedures procedures_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT procedures_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.providers(provider_id);


--
-- TOC entry 5221 (class 2606 OID 25718)
-- Name: procedures procedures_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT procedures_record_id_fkey FOREIGN KEY (record_id) REFERENCES public.medical_records(record_id);


--
-- TOC entry 5219 (class 2606 OID 25686)
-- Name: vital_signs vital_signs_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vital_signs
    ADD CONSTRAINT vital_signs_record_id_fkey FOREIGN KEY (record_id) REFERENCES public.medical_records(record_id);


--
-- TOC entry 5414 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO abena_user;


--
-- TOC entry 2168 (class 826 OID 25257)
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: abena_user
--

ALTER DEFAULT PRIVILEGES FOR ROLE abena_user IN SCHEMA public GRANT ALL ON SEQUENCES TO abena_user;


--
-- TOC entry 2167 (class 826 OID 25256)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: abena_user
--

ALTER DEFAULT PRIVILEGES FOR ROLE abena_user IN SCHEMA public GRANT ALL ON TABLES TO abena_user;


-- Completed on 2025-07-04 07:32:17

--
-- PostgreSQL database dump complete
--

