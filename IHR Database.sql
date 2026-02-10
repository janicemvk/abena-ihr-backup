--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.9

-- Started on 2025-07-04 07:43:43

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
-- TOC entry 5 (class 2615 OID 16400)
-- Name: ihr; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA ihr;


ALTER SCHEMA ihr OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 225 (class 1259 OID 16454)
-- Name: activity_data; Type: TABLE; Schema: ihr; Owner: postgres
--

CREATE TABLE ihr.activity_data (
    id integer NOT NULL,
    patient_id integer,
    device_id integer,
    date date,
    steps_count integer,
    distance_traveled numeric(8,2),
    calories_burned integer,
    active_minutes integer,
    sedentary_minutes integer
);


ALTER TABLE ihr.activity_data OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16453)
-- Name: activity_data_id_seq; Type: SEQUENCE; Schema: ihr; Owner: postgres
--

CREATE SEQUENCE ihr.activity_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ihr.activity_data_id_seq OWNER TO postgres;

--
-- TOC entry 5354 (class 0 OID 0)
-- Dependencies: 224
-- Name: activity_data_id_seq; Type: SEQUENCE OWNED BY; Schema: ihr; Owner: postgres
--

ALTER SEQUENCE ihr.activity_data_id_seq OWNED BY ihr.activity_data.id;


--
-- TOC entry 237 (class 1259 OID 16561)
-- Name: cannabinoid_effects; Type: TABLE; Schema: ihr; Owner: postgres
--

CREATE TABLE ihr.cannabinoid_effects (
    id integer NOT NULL,
    patient_id integer,
    usage_log_id integer,
    effect_type character varying(50),
    effect_intensity integer,
    onset_time interval,
    duration interval,
    notes text,
    CONSTRAINT cannabinoid_effects_effect_intensity_check CHECK (((effect_intensity >= 1) AND (effect_intensity <= 10)))
);


ALTER TABLE ihr.cannabinoid_effects OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 16560)
-- Name: cannabinoid_effects_id_seq; Type: SEQUENCE; Schema: ihr; Owner: postgres
--

CREATE SEQUENCE ihr.cannabinoid_effects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ihr.cannabinoid_effects_id_seq OWNER TO postgres;

--
-- TOC entry 5357 (class 0 OID 0)
-- Dependencies: 236
-- Name: cannabinoid_effects_id_seq; Type: SEQUENCE OWNED BY; Schema: ihr; Owner: postgres
--

ALTER SEQUENCE ihr.cannabinoid_effects_id_seq OWNED BY ihr.cannabinoid_effects.id;


--
-- TOC entry 231 (class 1259 OID 16516)
-- Name: cannabinoid_medications; Type: TABLE; Schema: ihr; Owner: postgres
--

CREATE TABLE ihr.cannabinoid_medications (
    id integer NOT NULL,
    name character varying(100),
    type character varying(50),
    description text,
    recommended_dosage character varying(100),
    potential_interactions text
);


ALTER TABLE ihr.cannabinoid_medications OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 16515)
-- Name: cannabinoid_medications_id_seq; Type: SEQUENCE; Schema: ihr; Owner: postgres
--

CREATE SEQUENCE ihr.cannabinoid_medications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ihr.cannabinoid_medications_id_seq OWNER TO postgres;

--
-- TOC entry 5360 (class 0 OID 0)
-- Dependencies: 230
-- Name: cannabinoid_medications_id_seq; Type: SEQUENCE OWNED BY; Schema: ihr; Owner: postgres
--

ALTER SEQUENCE ihr.cannabinoid_medications_id_seq OWNED BY ihr.cannabinoid_medications.id;


--
-- TOC entry 239 (class 1259 OID 16581)
-- Name: cannabinoid_side_effects; Type: TABLE; Schema: ihr; Owner: postgres
--

CREATE TABLE ihr.cannabinoid_side_effects (
    id integer NOT NULL,
    patient_id integer,
    usage_log_id integer,
    side_effect_type character varying(50),
    severity integer,
    onset_time interval,
    duration interval,
    notes text,
    CONSTRAINT cannabinoid_side_effects_severity_check CHECK (((severity >= 1) AND (severity <= 10)))
);


ALTER TABLE ihr.cannabinoid_side_effects OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 16580)
-- Name: cannabinoid_side_effects_id_seq; Type: SEQUENCE; Schema: ihr; Owner: postgres
--

CREATE SEQUENCE ihr.cannabinoid_side_effects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ihr.cannabinoid_side_effects_id_seq OWNER TO postgres;

--
-- TOC entry 5363 (class 0 OID 0)
-- Dependencies: 238
-- Name: cannabinoid_side_effects_id_seq; Type: SEQUENCE OWNED BY; Schema: ihr; Owner: postgres
--

ALTER SEQUENCE ihr.cannabinoid_side_effects_id_seq OWNED BY ihr.cannabinoid_side_effects.id;


--
-- TOC entry 235 (class 1259 OID 16542)
-- Name: cannabinoid_usage_logs; Type: TABLE; Schema: ihr; Owner: postgres
--

CREATE TABLE ihr.cannabinoid_usage_logs (
    id integer NOT NULL,
    patient_id integer,
    prescription_id integer,
    usage_datetime timestamp without time zone,
    dosage_taken character varying(50),
    notes text
);


ALTER TABLE ihr.cannabinoid_usage_logs OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 16541)
-- Name: cannabinoid_usage_logs_id_seq; Type: SEQUENCE; Schema: ihr; Owner: postgres
--

CREATE SEQUENCE ihr.cannabinoid_usage_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ihr.cannabinoid_usage_logs_id_seq OWNER TO postgres;

--
-- TOC entry 5366 (class 0 OID 0)
-- Dependencies: 234
-- Name: cannabinoid_usage_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: ihr; Owner: postgres
--

ALTER SEQUENCE ihr.cannabinoid_usage_logs_id_seq OWNED BY ihr.cannabinoid_usage_logs.id;


--
-- TOC entry 229 (class 1259 OID 16488)
-- Name: device_notifications; Type: TABLE; Schema: ihr; Owner: postgres
--

CREATE TABLE ihr.device_notifications (
    id integer NOT NULL,
    device_id integer,
    "timestamp" timestamp without time zone,
    notification_type character varying(50),
    notification_message text,
    is_acknowledged boolean
);


ALTER TABLE ihr.device_notifications OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16487)
-- Name: device_notifications_id_seq; Type: SEQUENCE; Schema: ihr; Owner: postgres
--

CREATE SEQUENCE ihr.device_notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ihr.device_notifications_id_seq OWNER TO postgres;

--
-- TOC entry 5369 (class 0 OID 0)
-- Dependencies: 228
-- Name: device_notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: ihr; Owner: postgres
--

ALTER SEQUENCE ihr.device_notifications_id_seq OWNED BY ihr.device_notifications.id;


--
-- TOC entry 221 (class 1259 OID 16425)
-- Name: devices; Type: TABLE; Schema: ihr; Owner: postgres
--

CREATE TABLE ihr.devices (
    id integer NOT NULL,
    patient_id integer,
    device_type character varying(50),
    device_model character varying(100),
    serial_number character varying(100),
    last_sync_time timestamp without time zone
);


ALTER TABLE ihr.devices OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16424)
-- Name: devices_id_seq; Type: SEQUENCE; Schema: ihr; Owner: postgres
--

CREATE SEQUENCE ihr.devices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ihr.devices_id_seq OWNER TO postgres;

--
-- TOC entry 5372 (class 0 OID 0)
-- Dependencies: 220
-- Name: devices_id_seq; Type: SEQUENCE OWNED BY; Schema: ihr; Owner: postgres
--

ALTER SEQUENCE ihr.devices_id_seq OWNED BY ihr.devices.id;


--
-- TOC entry 219 (class 1259 OID 16410)
-- Name: medications; Type: TABLE; Schema: ihr; Owner: postgres
--

CREATE TABLE ihr.medications (
    id integer NOT NULL,
    patient_id integer,
    medication_name character varying(100),
    dosage character varying(50),
    frequency character varying(50),
    start_date date,
    end_date date,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE ihr.medications OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16409)
-- Name: medications_id_seq; Type: SEQUENCE; Schema: ihr; Owner: postgres
--

CREATE SEQUENCE ihr.medications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ihr.medications_id_seq OWNER TO postgres;

--
-- TOC entry 5375 (class 0 OID 0)
-- Dependencies: 218
-- Name: medications_id_seq; Type: SEQUENCE OWNED BY; Schema: ihr; Owner: postgres
--

ALTER SEQUENCE ihr.medications_id_seq OWNED BY ihr.medications.id;


--
-- TOC entry 233 (class 1259 OID 16525)
-- Name: patient_cannabinoid_prescriptions; Type: TABLE; Schema: ihr; Owner: postgres
--

CREATE TABLE ihr.patient_cannabinoid_prescriptions (
    id integer NOT NULL,
    patient_id integer,
    medication_id integer,
    prescribing_doctor character varying(100),
    prescription_date date,
    start_date date,
    end_date date,
    dosage character varying(100),
    frequency character varying(50),
    administration_method character varying(50)
);


ALTER TABLE ihr.patient_cannabinoid_prescriptions OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 16524)
-- Name: patient_cannabinoid_prescriptions_id_seq; Type: SEQUENCE; Schema: ihr; Owner: postgres
--

CREATE SEQUENCE ihr.patient_cannabinoid_prescriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ihr.patient_cannabinoid_prescriptions_id_seq OWNER TO postgres;

--
-- TOC entry 5377 (class 0 OID 0)
-- Dependencies: 232
-- Name: patient_cannabinoid_prescriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: ihr; Owner: postgres
--

ALTER SEQUENCE ihr.patient_cannabinoid_prescriptions_id_seq OWNED BY ihr.patient_cannabinoid_prescriptions.id;


--
-- TOC entry 217 (class 1259 OID 16402)
-- Name: patients; Type: TABLE; Schema: ihr; Owner: postgres
--

CREATE TABLE ihr.patients (
    id integer NOT NULL,
    first_name character varying(50),
    last_name character varying(50),
    date_of_birth date,
    gender character varying(10),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE ihr.patients OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 16401)
-- Name: patients_id_seq; Type: SEQUENCE; Schema: ihr; Owner: postgres
--

CREATE SEQUENCE ihr.patients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ihr.patients_id_seq OWNER TO postgres;

--
-- TOC entry 5380 (class 0 OID 0)
-- Dependencies: 216
-- Name: patients_id_seq; Type: SEQUENCE OWNED BY; Schema: ihr; Owner: postgres
--

ALTER SEQUENCE ihr.patients_id_seq OWNED BY ihr.patients.id;


--
-- TOC entry 227 (class 1259 OID 16471)
-- Name: sleep_data; Type: TABLE; Schema: ihr; Owner: postgres
--

CREATE TABLE ihr.sleep_data (
    id integer NOT NULL,
    patient_id integer,
    device_id integer,
    sleep_start timestamp without time zone,
    sleep_end timestamp without time zone,
    total_sleep_time integer,
    deep_sleep_time integer,
    rem_sleep_time integer,
    light_sleep_time integer,
    awake_time integer
);


ALTER TABLE ihr.sleep_data OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16470)
-- Name: sleep_data_id_seq; Type: SEQUENCE; Schema: ihr; Owner: postgres
--

CREATE SEQUENCE ihr.sleep_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ihr.sleep_data_id_seq OWNER TO postgres;

--
-- TOC entry 5382 (class 0 OID 0)
-- Dependencies: 226
-- Name: sleep_data_id_seq; Type: SEQUENCE OWNED BY; Schema: ihr; Owner: postgres
--

ALTER SEQUENCE ihr.sleep_data_id_seq OWNED BY ihr.sleep_data.id;


--
-- TOC entry 223 (class 1259 OID 16437)
-- Name: vital_signs; Type: TABLE; Schema: ihr; Owner: postgres
--

CREATE TABLE ihr.vital_signs (
    id integer NOT NULL,
    patient_id integer,
    device_id integer,
    "timestamp" timestamp without time zone,
    heart_rate integer,
    blood_pressure_systolic integer,
    blood_pressure_diastolic integer,
    body_temperature numeric(5,2),
    respiratory_rate integer,
    oxygen_saturation integer,
    CONSTRAINT check_blood_pressure CHECK (((blood_pressure_systolic >= 0) AND (blood_pressure_systolic <= 300) AND (blood_pressure_diastolic >= 0) AND (blood_pressure_diastolic <= 300))),
    CONSTRAINT check_body_temperature CHECK (((body_temperature >= (25)::numeric) AND (body_temperature <= (45)::numeric))),
    CONSTRAINT check_heart_rate CHECK (((heart_rate >= 0) AND (heart_rate <= 300))),
    CONSTRAINT check_oxygen_saturation CHECK (((oxygen_saturation >= 0) AND (oxygen_saturation <= 100))),
    CONSTRAINT check_respiratory_rate CHECK (((respiratory_rate >= 0) AND (respiratory_rate <= 100)))
);


ALTER TABLE ihr.vital_signs OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16436)
-- Name: vital_signs_id_seq; Type: SEQUENCE; Schema: ihr; Owner: postgres
--

CREATE SEQUENCE ihr.vital_signs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE ihr.vital_signs_id_seq OWNER TO postgres;

--
-- TOC entry 5385 (class 0 OID 0)
-- Dependencies: 222
-- Name: vital_signs_id_seq; Type: SEQUENCE OWNED BY; Schema: ihr; Owner: postgres
--

ALTER SEQUENCE ihr.vital_signs_id_seq OWNED BY ihr.vital_signs.id;


--
-- TOC entry 296 (class 1259 OID 17015)
-- Name: Telemedicine_doctoravailability; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public."Telemedicine_doctoravailability" (
    id bigint NOT NULL,
    day_of_week integer NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    is_available boolean NOT NULL,
    doctor_id bigint NOT NULL
);


ALTER TABLE public."Telemedicine_doctoravailability" OWNER TO ihr_user;

--
-- TOC entry 295 (class 1259 OID 17014)
-- Name: Telemedicine_doctoravailability_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public."Telemedicine_doctoravailability" ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public."Telemedicine_doctoravailability_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 292 (class 1259 OID 16999)
-- Name: Telemedicine_doctorprofile; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public."Telemedicine_doctorprofile" (
    id bigint NOT NULL,
    profile_photo character varying(100) NOT NULL,
    specialty character varying(100) NOT NULL,
    license_number character varying(50) NOT NULL,
    license_document character varying(100) NOT NULL,
    education text NOT NULL,
    board_certifications text NOT NULL,
    years_of_experience integer NOT NULL,
    bio text NOT NULL,
    consultation_fee numeric(10,2) NOT NULL,
    is_verified boolean NOT NULL,
    verification_date timestamp with time zone,
    user_id integer NOT NULL
);


ALTER TABLE public."Telemedicine_doctorprofile" OWNER TO ihr_user;

--
-- TOC entry 291 (class 1259 OID 16998)
-- Name: Telemedicine_doctorprofile_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public."Telemedicine_doctorprofile" ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public."Telemedicine_doctorprofile_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 294 (class 1259 OID 17009)
-- Name: Telemedicine_doctortimeoff; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public."Telemedicine_doctortimeoff" (
    id bigint NOT NULL,
    start_datetime timestamp with time zone NOT NULL,
    end_datetime timestamp with time zone NOT NULL,
    reason character varying(200) NOT NULL,
    doctor_id bigint NOT NULL
);


ALTER TABLE public."Telemedicine_doctortimeoff" OWNER TO ihr_user;

--
-- TOC entry 293 (class 1259 OID 17008)
-- Name: Telemedicine_doctortimeoff_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public."Telemedicine_doctortimeoff" ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public."Telemedicine_doctortimeoff_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 288 (class 1259 OID 16937)
-- Name: Telemedicine_medicaldocument; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public."Telemedicine_medicaldocument" (
    id bigint NOT NULL,
    document_type character varying(20) NOT NULL,
    file character varying(100) NOT NULL,
    uploaded_at timestamp with time zone NOT NULL,
    description text NOT NULL,
    uploaded_by_id integer NOT NULL,
    appointment_id bigint NOT NULL
);


ALTER TABLE public."Telemedicine_medicaldocument" OWNER TO ihr_user;

--
-- TOC entry 287 (class 1259 OID 16936)
-- Name: Telemedicine_medicaldocument_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public."Telemedicine_medicaldocument" ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public."Telemedicine_medicaldocument_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 284 (class 1259 OID 16923)
-- Name: Telemedicine_patientvitals; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public."Telemedicine_patientvitals" (
    id bigint NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    heart_rate integer,
    blood_pressure_systolic integer,
    blood_pressure_diastolic integer,
    temperature numeric(4,1),
    oxygen_saturation integer,
    notes text NOT NULL,
    patient_id integer NOT NULL
);


ALTER TABLE public."Telemedicine_patientvitals" OWNER TO ihr_user;

--
-- TOC entry 283 (class 1259 OID 16922)
-- Name: Telemedicine_patientvitals_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public."Telemedicine_patientvitals" ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public."Telemedicine_patientvitals_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 286 (class 1259 OID 16931)
-- Name: Telemedicine_telemedicineappointment; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public."Telemedicine_telemedicineappointment" (
    id bigint NOT NULL,
    scheduled_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone NOT NULL,
    status character varying(20) NOT NULL,
    meeting_link character varying(200) NOT NULL,
    payment_status boolean NOT NULL,
    payment_amount numeric(10,2) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    patient_id integer NOT NULL,
    provider_id integer NOT NULL,
    doctor_notes text NOT NULL,
    patient_notes text NOT NULL,
    reason_for_visit text NOT NULL
);


ALTER TABLE public."Telemedicine_telemedicineappointment" OWNER TO ihr_user;

--
-- TOC entry 285 (class 1259 OID 16930)
-- Name: Telemedicine_telemedicineappointment_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public."Telemedicine_telemedicineappointment" ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public."Telemedicine_telemedicineappointment_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 290 (class 1259 OID 16945)
-- Name: Telemedicine_virtualwaitingroom; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public."Telemedicine_virtualwaitingroom" (
    id bigint NOT NULL,
    joined_at timestamp with time zone NOT NULL,
    status character varying(20) NOT NULL,
    appointment_id bigint NOT NULL,
    patient_id integer NOT NULL
);


ALTER TABLE public."Telemedicine_virtualwaitingroom" OWNER TO ihr_user;

--
-- TOC entry 289 (class 1259 OID 16944)
-- Name: Telemedicine_virtualwaitingroom_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public."Telemedicine_virtualwaitingroom" ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public."Telemedicine_virtualwaitingroom_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 247 (class 1259 OID 16634)
-- Name: auth_group; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO ihr_user;

--
-- TOC entry 246 (class 1259 OID 16633)
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 249 (class 1259 OID 16642)
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO ihr_user;

--
-- TOC entry 248 (class 1259 OID 16641)
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 245 (class 1259 OID 16628)
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO ihr_user;

--
-- TOC entry 244 (class 1259 OID 16627)
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 251 (class 1259 OID 16648)
-- Name: auth_user; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO ihr_user;

--
-- TOC entry 253 (class 1259 OID 16656)
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.auth_user_groups (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO ihr_user;

--
-- TOC entry 252 (class 1259 OID 16655)
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.auth_user_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 250 (class 1259 OID 16647)
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.auth_user ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 255 (class 1259 OID 16662)
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.auth_user_user_permissions (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO ihr_user;

--
-- TOC entry 254 (class 1259 OID 16661)
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.auth_user_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 259 (class 1259 OID 16749)
-- Name: core_patient; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.core_patient (
    id bigint NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    date_of_birth date NOT NULL,
    gender character varying(10) NOT NULL,
    created_at timestamp with time zone NOT NULL
);


ALTER TABLE public.core_patient OWNER TO ihr_user;

--
-- TOC entry 258 (class 1259 OID 16748)
-- Name: core_patient_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.core_patient ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.core_patient_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 257 (class 1259 OID 16720)
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO ihr_user;

--
-- TOC entry 256 (class 1259 OID 16719)
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 243 (class 1259 OID 16620)
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO ihr_user;

--
-- TOC entry 242 (class 1259 OID 16619)
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 241 (class 1259 OID 16612)
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO ihr_user;

--
-- TOC entry 240 (class 1259 OID 16611)
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 260 (class 1259 OID 16754)
-- Name: django_session; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO ihr_user;

--
-- TOC entry 262 (class 1259 OID 16764)
-- Name: ihr_cannabinoid_medicine_cannabinoidmedication; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.ihr_cannabinoid_medicine_cannabinoidmedication (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    type character varying(50) NOT NULL,
    description text NOT NULL,
    recommended_dosage character varying(100) NOT NULL,
    potential_interactions text NOT NULL
);


ALTER TABLE public.ihr_cannabinoid_medicine_cannabinoidmedication OWNER TO ihr_user;

--
-- TOC entry 261 (class 1259 OID 16763)
-- Name: ihr_cannabinoid_medicine_cannabinoidmedication_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.ihr_cannabinoid_medicine_cannabinoidmedication ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.ihr_cannabinoid_medicine_cannabinoidmedication_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 266 (class 1259 OID 16778)
-- Name: ihr_cannabinoid_medicine_cannabinoidusagelog; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.ihr_cannabinoid_medicine_cannabinoidusagelog (
    id bigint NOT NULL,
    usage_datetime timestamp with time zone NOT NULL,
    dosage_taken character varying(50) NOT NULL,
    notes text NOT NULL,
    patient_id bigint NOT NULL,
    prescription_id bigint NOT NULL
);


ALTER TABLE public.ihr_cannabinoid_medicine_cannabinoidusagelog OWNER TO ihr_user;

--
-- TOC entry 265 (class 1259 OID 16777)
-- Name: ihr_cannabinoid_medicine_cannabinoidusagelog_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.ihr_cannabinoid_medicine_cannabinoidusagelog ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.ihr_cannabinoid_medicine_cannabinoidusagelog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 264 (class 1259 OID 16772)
-- Name: ihr_cannabinoid_medicine_patientcannabinoidprescription; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.ihr_cannabinoid_medicine_patientcannabinoidprescription (
    id bigint NOT NULL,
    prescribing_doctor character varying(100) NOT NULL,
    prescription_date date NOT NULL,
    start_date date NOT NULL,
    end_date date,
    dosage character varying(100) NOT NULL,
    frequency character varying(50) NOT NULL,
    administration_method character varying(50) NOT NULL,
    medication_id bigint NOT NULL,
    patient_id bigint NOT NULL
);


ALTER TABLE public.ihr_cannabinoid_medicine_patientcannabinoidprescription OWNER TO ihr_user;

--
-- TOC entry 263 (class 1259 OID 16771)
-- Name: ihr_cannabinoid_medicine_patientcannabinoidprescription_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.ihr_cannabinoid_medicine_patientcannabinoidprescription ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.ihr_cannabinoid_medicine_patientcannabinoidprescription_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 270 (class 1259 OID 16818)
-- Name: ihr_iot_wearables_activitydata; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.ihr_iot_wearables_activitydata (
    id bigint NOT NULL,
    date date NOT NULL,
    steps integer NOT NULL,
    calories_burned double precision NOT NULL,
    active_minutes integer NOT NULL,
    patient_id bigint NOT NULL,
    device_id bigint NOT NULL
);


ALTER TABLE public.ihr_iot_wearables_activitydata OWNER TO ihr_user;

--
-- TOC entry 269 (class 1259 OID 16817)
-- Name: ihr_iot_wearables_activitydata_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.ihr_iot_wearables_activitydata ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.ihr_iot_wearables_activitydata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 268 (class 1259 OID 16810)
-- Name: ihr_iot_wearables_device; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.ihr_iot_wearables_device (
    id bigint NOT NULL,
    device_type character varying(100) NOT NULL,
    device_id character varying(100) NOT NULL,
    last_sync timestamp with time zone NOT NULL,
    patient_id bigint NOT NULL
);


ALTER TABLE public.ihr_iot_wearables_device OWNER TO ihr_user;

--
-- TOC entry 267 (class 1259 OID 16809)
-- Name: ihr_iot_wearables_device_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.ihr_iot_wearables_device ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.ihr_iot_wearables_device_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 278 (class 1259 OID 16888)
-- Name: ihr_iot_wearables_iotwearabledata; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.ihr_iot_wearables_iotwearabledata (
    id bigint NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    patient_id bigint NOT NULL
);


ALTER TABLE public.ihr_iot_wearables_iotwearabledata OWNER TO ihr_user;

--
-- TOC entry 277 (class 1259 OID 16887)
-- Name: ihr_iot_wearables_iotwearabledata_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.ihr_iot_wearables_iotwearabledata ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.ihr_iot_wearables_iotwearabledata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 272 (class 1259 OID 16824)
-- Name: ihr_iot_wearables_vitalsigns; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.ihr_iot_wearables_vitalsigns (
    id bigint NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    heart_rate integer,
    blood_pressure_systolic integer,
    blood_pressure_diastolic integer,
    temperature double precision,
    oxygen_saturation integer,
    device_id bigint NOT NULL,
    patient_id bigint NOT NULL
);


ALTER TABLE public.ihr_iot_wearables_vitalsigns OWNER TO ihr_user;

--
-- TOC entry 271 (class 1259 OID 16823)
-- Name: ihr_iot_wearables_vitalsigns_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.ihr_iot_wearables_vitalsigns ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.ihr_iot_wearables_vitalsigns_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 274 (class 1259 OID 16861)
-- Name: mental_health_moodlog; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.mental_health_moodlog (
    id bigint NOT NULL,
    date date NOT NULL,
    mood integer NOT NULL,
    notes text NOT NULL,
    patient_id bigint NOT NULL
);


ALTER TABLE public.mental_health_moodlog OWNER TO ihr_user;

--
-- TOC entry 273 (class 1259 OID 16860)
-- Name: mental_health_moodlog_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.mental_health_moodlog ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.mental_health_moodlog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 276 (class 1259 OID 16875)
-- Name: nutrition_nutritionlog; Type: TABLE; Schema: public; Owner: ihr_user
--

CREATE TABLE public.nutrition_nutritionlog (
    id bigint NOT NULL,
    date date NOT NULL,
    calories integer NOT NULL,
    protein double precision NOT NULL,
    carbs double precision NOT NULL,
    fats double precision NOT NULL,
    patient_id bigint NOT NULL
);


ALTER TABLE public.nutrition_nutritionlog OWNER TO ihr_user;

--
-- TOC entry 275 (class 1259 OID 16874)
-- Name: nutrition_nutritionlog_id_seq; Type: SEQUENCE; Schema: public; Owner: ihr_user
--

ALTER TABLE public.nutrition_nutritionlog ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.nutrition_nutritionlog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 280 (class 1259 OID 16901)
-- Name: patients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.patients (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    dob date NOT NULL,
    gender character varying(10),
    contact character varying(100)
);


ALTER TABLE public.patients OWNER TO postgres;

--
-- TOC entry 279 (class 1259 OID 16900)
-- Name: patients_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.patients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.patients_id_seq OWNER TO postgres;

--
-- TOC entry 5388 (class 0 OID 0)
-- Dependencies: 279
-- Name: patients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.patients_id_seq OWNED BY public.patients.id;


--
-- TOC entry 282 (class 1259 OID 16911)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    first_name character varying(100),
    last_name character varying(100),
    phone character varying(20),
    date_of_birth date
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 281 (class 1259 OID 16910)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 5390 (class 0 OID 0)
-- Dependencies: 281
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4897 (class 2604 OID 16457)
-- Name: activity_data id; Type: DEFAULT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.activity_data ALTER COLUMN id SET DEFAULT nextval('ihr.activity_data_id_seq'::regclass);


--
-- TOC entry 4903 (class 2604 OID 16564)
-- Name: cannabinoid_effects id; Type: DEFAULT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_effects ALTER COLUMN id SET DEFAULT nextval('ihr.cannabinoid_effects_id_seq'::regclass);


--
-- TOC entry 4900 (class 2604 OID 16519)
-- Name: cannabinoid_medications id; Type: DEFAULT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_medications ALTER COLUMN id SET DEFAULT nextval('ihr.cannabinoid_medications_id_seq'::regclass);


--
-- TOC entry 4904 (class 2604 OID 16584)
-- Name: cannabinoid_side_effects id; Type: DEFAULT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_side_effects ALTER COLUMN id SET DEFAULT nextval('ihr.cannabinoid_side_effects_id_seq'::regclass);


--
-- TOC entry 4902 (class 2604 OID 16545)
-- Name: cannabinoid_usage_logs id; Type: DEFAULT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_usage_logs ALTER COLUMN id SET DEFAULT nextval('ihr.cannabinoid_usage_logs_id_seq'::regclass);


--
-- TOC entry 4899 (class 2604 OID 16491)
-- Name: device_notifications id; Type: DEFAULT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.device_notifications ALTER COLUMN id SET DEFAULT nextval('ihr.device_notifications_id_seq'::regclass);


--
-- TOC entry 4895 (class 2604 OID 16428)
-- Name: devices id; Type: DEFAULT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.devices ALTER COLUMN id SET DEFAULT nextval('ihr.devices_id_seq'::regclass);


--
-- TOC entry 4893 (class 2604 OID 16413)
-- Name: medications id; Type: DEFAULT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.medications ALTER COLUMN id SET DEFAULT nextval('ihr.medications_id_seq'::regclass);


--
-- TOC entry 4901 (class 2604 OID 16528)
-- Name: patient_cannabinoid_prescriptions id; Type: DEFAULT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.patient_cannabinoid_prescriptions ALTER COLUMN id SET DEFAULT nextval('ihr.patient_cannabinoid_prescriptions_id_seq'::regclass);


--
-- TOC entry 4891 (class 2604 OID 16405)
-- Name: patients id; Type: DEFAULT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.patients ALTER COLUMN id SET DEFAULT nextval('ihr.patients_id_seq'::regclass);


--
-- TOC entry 4898 (class 2604 OID 16474)
-- Name: sleep_data id; Type: DEFAULT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.sleep_data ALTER COLUMN id SET DEFAULT nextval('ihr.sleep_data_id_seq'::regclass);


--
-- TOC entry 4896 (class 2604 OID 16440)
-- Name: vital_signs id; Type: DEFAULT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.vital_signs ALTER COLUMN id SET DEFAULT nextval('ihr.vital_signs_id_seq'::regclass);


--
-- TOC entry 4905 (class 2604 OID 16904)
-- Name: patients id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patients ALTER COLUMN id SET DEFAULT nextval('public.patients_id_seq'::regclass);


--
-- TOC entry 4906 (class 2604 OID 16914)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 5274 (class 0 OID 16454)
-- Dependencies: 225
-- Data for Name: activity_data; Type: TABLE DATA; Schema: ihr; Owner: postgres
--

COPY ihr.activity_data (id, patient_id, device_id, date, steps_count, distance_traveled, calories_burned, active_minutes, sedentary_minutes) FROM stdin;
\.


--
-- TOC entry 5286 (class 0 OID 16561)
-- Dependencies: 237
-- Data for Name: cannabinoid_effects; Type: TABLE DATA; Schema: ihr; Owner: postgres
--

COPY ihr.cannabinoid_effects (id, patient_id, usage_log_id, effect_type, effect_intensity, onset_time, duration, notes) FROM stdin;
\.


--
-- TOC entry 5280 (class 0 OID 16516)
-- Dependencies: 231
-- Data for Name: cannabinoid_medications; Type: TABLE DATA; Schema: ihr; Owner: postgres
--

COPY ihr.cannabinoid_medications (id, name, type, description, recommended_dosage, potential_interactions) FROM stdin;
\.


--
-- TOC entry 5288 (class 0 OID 16581)
-- Dependencies: 239
-- Data for Name: cannabinoid_side_effects; Type: TABLE DATA; Schema: ihr; Owner: postgres
--

COPY ihr.cannabinoid_side_effects (id, patient_id, usage_log_id, side_effect_type, severity, onset_time, duration, notes) FROM stdin;
\.


--
-- TOC entry 5284 (class 0 OID 16542)
-- Dependencies: 235
-- Data for Name: cannabinoid_usage_logs; Type: TABLE DATA; Schema: ihr; Owner: postgres
--

COPY ihr.cannabinoid_usage_logs (id, patient_id, prescription_id, usage_datetime, dosage_taken, notes) FROM stdin;
\.


--
-- TOC entry 5278 (class 0 OID 16488)
-- Dependencies: 229
-- Data for Name: device_notifications; Type: TABLE DATA; Schema: ihr; Owner: postgres
--

COPY ihr.device_notifications (id, device_id, "timestamp", notification_type, notification_message, is_acknowledged) FROM stdin;
\.


--
-- TOC entry 5270 (class 0 OID 16425)
-- Dependencies: 221
-- Data for Name: devices; Type: TABLE DATA; Schema: ihr; Owner: postgres
--

COPY ihr.devices (id, patient_id, device_type, device_model, serial_number, last_sync_time) FROM stdin;
\.


--
-- TOC entry 5268 (class 0 OID 16410)
-- Dependencies: 219
-- Data for Name: medications; Type: TABLE DATA; Schema: ihr; Owner: postgres
--

COPY ihr.medications (id, patient_id, medication_name, dosage, frequency, start_date, end_date, created_at) FROM stdin;
\.


--
-- TOC entry 5282 (class 0 OID 16525)
-- Dependencies: 233
-- Data for Name: patient_cannabinoid_prescriptions; Type: TABLE DATA; Schema: ihr; Owner: postgres
--

COPY ihr.patient_cannabinoid_prescriptions (id, patient_id, medication_id, prescribing_doctor, prescription_date, start_date, end_date, dosage, frequency, administration_method) FROM stdin;
\.


--
-- TOC entry 5266 (class 0 OID 16402)
-- Dependencies: 217
-- Data for Name: patients; Type: TABLE DATA; Schema: ihr; Owner: postgres
--

COPY ihr.patients (id, first_name, last_name, date_of_birth, gender, created_at) FROM stdin;
\.


--
-- TOC entry 5276 (class 0 OID 16471)
-- Dependencies: 227
-- Data for Name: sleep_data; Type: TABLE DATA; Schema: ihr; Owner: postgres
--

COPY ihr.sleep_data (id, patient_id, device_id, sleep_start, sleep_end, total_sleep_time, deep_sleep_time, rem_sleep_time, light_sleep_time, awake_time) FROM stdin;
\.


--
-- TOC entry 5272 (class 0 OID 16437)
-- Dependencies: 223
-- Data for Name: vital_signs; Type: TABLE DATA; Schema: ihr; Owner: postgres
--

COPY ihr.vital_signs (id, patient_id, device_id, "timestamp", heart_rate, blood_pressure_systolic, blood_pressure_diastolic, body_temperature, respiratory_rate, oxygen_saturation) FROM stdin;
\.


--
-- TOC entry 5345 (class 0 OID 17015)
-- Dependencies: 296
-- Data for Name: Telemedicine_doctoravailability; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public."Telemedicine_doctoravailability" (id, day_of_week, start_time, end_time, is_available, doctor_id) FROM stdin;
\.


--
-- TOC entry 5341 (class 0 OID 16999)
-- Dependencies: 292
-- Data for Name: Telemedicine_doctorprofile; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public."Telemedicine_doctorprofile" (id, profile_photo, specialty, license_number, license_document, education, board_certifications, years_of_experience, bio, consultation_fee, is_verified, verification_date, user_id) FROM stdin;
\.


--
-- TOC entry 5343 (class 0 OID 17009)
-- Dependencies: 294
-- Data for Name: Telemedicine_doctortimeoff; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public."Telemedicine_doctortimeoff" (id, start_datetime, end_datetime, reason, doctor_id) FROM stdin;
\.


--
-- TOC entry 5337 (class 0 OID 16937)
-- Dependencies: 288
-- Data for Name: Telemedicine_medicaldocument; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public."Telemedicine_medicaldocument" (id, document_type, file, uploaded_at, description, uploaded_by_id, appointment_id) FROM stdin;
\.


--
-- TOC entry 5333 (class 0 OID 16923)
-- Dependencies: 284
-- Data for Name: Telemedicine_patientvitals; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public."Telemedicine_patientvitals" (id, "timestamp", heart_rate, blood_pressure_systolic, blood_pressure_diastolic, temperature, oxygen_saturation, notes, patient_id) FROM stdin;
\.


--
-- TOC entry 5335 (class 0 OID 16931)
-- Dependencies: 286
-- Data for Name: Telemedicine_telemedicineappointment; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public."Telemedicine_telemedicineappointment" (id, scheduled_time, end_time, status, meeting_link, payment_status, payment_amount, created_at, updated_at, patient_id, provider_id, doctor_notes, patient_notes, reason_for_visit) FROM stdin;
1	2025-02-07 04:00:00-08	2025-02-07 10:00:00-08	scheduled		t	-0.01	2025-02-04 10:30:23.949814-08	2025-02-04 10:30:23.949814-08	2	5			
\.


--
-- TOC entry 5339 (class 0 OID 16945)
-- Dependencies: 290
-- Data for Name: Telemedicine_virtualwaitingroom; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public."Telemedicine_virtualwaitingroom" (id, joined_at, status, appointment_id, patient_id) FROM stdin;
\.


--
-- TOC entry 5296 (class 0 OID 16634)
-- Dependencies: 247
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- TOC entry 5298 (class 0 OID 16642)
-- Dependencies: 249
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- TOC entry 5294 (class 0 OID 16628)
-- Dependencies: 245
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
25	Can add patient	7	add_patient
26	Can change patient	7	change_patient
27	Can delete patient	7	delete_patient
28	Can view patient	7	view_patient
29	Can add activity data	8	add_activitydata
30	Can change activity data	8	change_activitydata
31	Can delete activity data	8	delete_activitydata
32	Can view activity data	8	view_activitydata
33	Can add device	9	add_device
34	Can change device	9	change_device
35	Can delete device	9	delete_device
36	Can view device	9	view_device
37	Can add vital signs	10	add_vitalsigns
38	Can change vital signs	10	change_vitalsigns
39	Can delete vital signs	10	delete_vitalsigns
40	Can view vital signs	10	view_vitalsigns
41	Can add patient cannabinoid prescription	11	add_patientcannabinoidprescription
42	Can change patient cannabinoid prescription	11	change_patientcannabinoidprescription
43	Can delete patient cannabinoid prescription	11	delete_patientcannabinoidprescription
44	Can view patient cannabinoid prescription	11	view_patientcannabinoidprescription
45	Can add cannabinoid usage log	12	add_cannabinoidusagelog
46	Can change cannabinoid usage log	12	change_cannabinoidusagelog
47	Can delete cannabinoid usage log	12	delete_cannabinoidusagelog
48	Can view cannabinoid usage log	12	view_cannabinoidusagelog
49	Can add cannabinoid medication	13	add_cannabinoidmedication
50	Can change cannabinoid medication	13	change_cannabinoidmedication
51	Can delete cannabinoid medication	13	delete_cannabinoidmedication
52	Can view cannabinoid medication	13	view_cannabinoidmedication
53	Can add nutrition log	14	add_nutritionlog
54	Can change nutrition log	14	change_nutritionlog
55	Can delete nutrition log	14	delete_nutritionlog
56	Can view nutrition log	14	view_nutritionlog
57	Can add mood log	15	add_moodlog
58	Can change mood log	15	change_moodlog
59	Can delete mood log	15	delete_moodlog
60	Can view mood log	15	view_moodlog
61	Can add io t wearable data	16	add_iotwearabledata
62	Can change io t wearable data	16	change_iotwearabledata
63	Can delete io t wearable data	16	delete_iotwearabledata
64	Can view io t wearable data	16	view_iotwearabledata
65	Can add telemedicine appointment	17	add_telemedicineappointment
66	Can change telemedicine appointment	17	change_telemedicineappointment
67	Can delete telemedicine appointment	17	delete_telemedicineappointment
68	Can view telemedicine appointment	17	view_telemedicineappointment
69	Can add virtual waiting room	18	add_virtualwaitingroom
70	Can change virtual waiting room	18	change_virtualwaitingroom
71	Can delete virtual waiting room	18	delete_virtualwaitingroom
72	Can view virtual waiting room	18	view_virtualwaitingroom
73	Can add medical document	19	add_medicaldocument
74	Can change medical document	19	change_medicaldocument
75	Can delete medical document	19	delete_medicaldocument
76	Can view medical document	19	view_medicaldocument
77	Can add patient vitals	20	add_patientvitals
78	Can change patient vitals	20	change_patientvitals
79	Can delete patient vitals	20	delete_patientvitals
80	Can view patient vitals	20	view_patientvitals
81	Can add doctor profile	23	add_doctorprofile
82	Can change doctor profile	23	change_doctorprofile
83	Can delete doctor profile	23	delete_doctorprofile
84	Can view doctor profile	23	view_doctorprofile
85	Can add doctor time off	21	add_doctortimeoff
86	Can change doctor time off	21	change_doctortimeoff
87	Can delete doctor time off	21	delete_doctortimeoff
88	Can view doctor time off	21	view_doctortimeoff
89	Can add doctor availability	22	add_doctoravailability
90	Can change doctor availability	22	change_doctoravailability
91	Can delete doctor availability	22	delete_doctoravailability
92	Can view doctor availability	22	view_doctoravailability
\.


--
-- TOC entry 5300 (class 0 OID 16648)
-- Dependencies: 251
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
2	pbkdf2_sha256$720000$pMAdAmMCn79FlUTmlYzDnj$yhuC/OoC/rq2CLRfx1iICIQ/MDmHv78dXJRhfbtZI6w=	2024-08-28 16:19:00.507111-07	t	Janice			jmknox@gmail.com	t	t	2024-08-28 16:17:51.151843-07
1	pbkdf2_sha256$720000$EXR9gYo1UJV7L3iguFPfci$VDWRxgye3p7XPqSM+UfJ3XPr67JKfLkzht3e4ygao3M=	2024-08-28 16:42:23.398986-07	t	janmarie			drjanice@pivitalholdings.com	t	t	2024-08-26 23:11:38.450865-07
4	pbkdf2_sha256$720000$sliwS65gZf0lTqzZm52DSf$DLsKFWggeFWLEGJk9Td2OFdoZ8ujF4vXtR32pNIBBj4=	\N	f	DavidGK	David G	Knox	doctorsknox@gmail.com	t	t	2025-02-04 10:08:28-08
5	pbkdf2_sha256$720000$Ea9s6UOT2KUlG75Rw2QCJ0$ZY64JyMjNlJ1szq8wdZC2sBfpqgojVDoMMetyd4GdKc=	\N	f	racheldoc	Rachel	Knox	doctorsknox@gmail.com	t	t	2025-02-04 10:08:54-08
3	pbkdf2_sha256$720000$LW9GWZ9fCRMf02Mgktvji5$JeGMQxMl5CG4ofaydL93CEbJiPYAoFRI42AfUVHJIC0=	2025-02-04 11:21:25.41554-08	t	janicemvk1			drjanice@pivitalhealth.com	t	t	2025-02-04 10:00:48.34294-08
6	pbkdf2_sha256$720000$TPHCJ7j0a4VmDDtrw6AwrZ$QUGL27BRF1V2W1hk9HeoYq+OYpzb62QT1MpXH698KKg=	2025-02-04 11:28:41.8457-08	t	janicemvk2			doctorsknox@gmail.com	t	t	2025-02-04 11:10:15.216756-08
\.


--
-- TOC entry 5302 (class 0 OID 16656)
-- Dependencies: 253
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- TOC entry 5304 (class 0 OID 16662)
-- Dependencies: 255
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
1	4	1
2	4	2
3	4	3
4	4	4
5	4	5
6	4	6
7	4	7
8	4	8
9	4	9
10	4	10
11	4	11
12	4	12
13	4	13
14	4	14
15	4	15
16	4	16
17	4	17
18	4	18
19	4	19
20	4	20
21	4	21
22	4	22
23	4	23
24	4	24
25	4	25
26	4	26
27	4	27
28	4	28
29	4	29
30	4	30
31	4	31
32	4	32
33	4	33
34	4	34
35	4	35
36	4	36
37	4	37
38	4	38
39	4	39
40	4	40
41	4	41
42	4	42
43	4	43
44	4	44
45	4	45
46	4	46
47	4	47
48	4	48
49	4	49
50	4	50
51	4	51
52	4	52
53	4	53
54	4	54
55	4	55
56	4	56
57	4	57
58	4	58
59	4	59
60	4	60
61	4	61
62	4	62
63	4	63
64	4	64
65	4	65
66	4	66
67	4	67
68	4	68
69	4	69
70	4	70
71	4	71
72	4	72
73	4	73
74	4	74
75	4	75
76	4	76
77	4	77
78	4	78
79	4	79
80	4	80
81	5	1
82	5	2
83	5	3
84	5	4
85	5	5
86	5	6
87	5	7
88	5	8
89	5	9
90	5	10
91	5	11
92	5	12
93	5	13
94	5	14
95	5	15
96	5	16
97	5	17
98	5	18
99	5	19
100	5	20
101	5	21
102	5	22
103	5	23
104	5	24
105	5	25
106	5	26
107	5	27
108	5	28
109	5	29
110	5	30
111	5	31
112	5	32
113	5	33
114	5	34
115	5	35
116	5	36
117	5	37
118	5	38
119	5	39
120	5	40
121	5	41
122	5	42
123	5	43
124	5	44
125	5	45
126	5	46
127	5	47
128	5	48
129	5	49
130	5	50
131	5	51
132	5	52
133	5	53
134	5	54
135	5	55
136	5	56
137	5	57
138	5	58
139	5	59
140	5	60
141	5	61
142	5	62
143	5	63
144	5	64
145	5	65
146	5	66
147	5	67
148	5	68
149	5	69
150	5	70
151	5	71
152	5	72
153	5	73
154	5	74
155	5	75
156	5	76
157	5	77
158	5	78
159	5	79
160	5	80
161	5	81
162	5	82
163	5	83
164	5	84
165	5	85
166	5	86
167	5	87
168	5	88
169	5	89
170	5	90
171	5	91
172	5	92
\.


--
-- TOC entry 5308 (class 0 OID 16749)
-- Dependencies: 259
-- Data for Name: core_patient; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.core_patient (id, first_name, last_name, date_of_birth, gender, created_at) FROM stdin;
1	Happy	Day	2000-01-03	F	2024-08-28 10:41:56.549104-07
\.


--
-- TOC entry 5306 (class 0 OID 16720)
-- Dependencies: 257
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2024-08-28 10:41:56.558752-07	1	Happy Day	1	[{"added": {}}]	7	1
2	2024-08-28 10:44:38.441161-07	1	Happy Day - 2024-08-28	1	[{"added": {}}]	14	1
3	2024-08-28 10:45:15.810541-07	1	Happy Day - 2024-08-28 - Mood: Good	1	[{"added": {}}]	15	1
4	2024-08-28 10:46:41.07539-07	1	Smartwatch - xx	1	[{"added": {}}]	9	1
5	2024-08-28 10:49:21.252953-07	1	CBD	1	[{"added": {}}]	13	1
6	2024-08-28 10:51:16.1851-07	1	Happy Day - CBD - 2024-08-28	1	[{"added": {}}]	11	1
7	2024-08-28 10:52:17.900839-07	1	Happy Day	2	[]	7	1
8	2024-08-28 10:52:22.151789-07	1	Happy Day	2	[]	7	1
9	2024-08-28 10:52:39.880152-07	1	CBD	2	[]	13	1
10	2024-08-28 10:52:57.447748-07	1	Smartwatch - xx	2	[]	9	1
11	2024-08-28 10:53:26.059386-07	1	Happy Day - 2024-08-28	2	[]	14	1
12	2024-08-28 10:54:05.10804-07	1	Happy Day - 2024-08-28 - Mood: Very Bad	2	[{"changed": {"fields": ["Mood"]}}]	15	1
13	2024-08-28 10:54:12.20467-07	1	Happy Day - 2024-08-28 - Mood: Very Bad	2	[]	15	1
14	2024-08-28 10:59:00.233285-07	1	Happy Day - 2024-08-28	2	[{"changed": {"fields": ["Protein", "Carbs", "Fats"]}}]	14	1
15	2024-08-28 10:59:17.912075-07	1	Happy Day - 2024-08-28	2	[]	14	1
16	2024-08-28 10:59:46.504026-07	1	Happy Day - 2024-08-28	2	[{"changed": {"fields": ["Protein"]}}]	14	1
17	2024-08-28 11:00:20.942315-07	1	Happy Day - 2024-08-28	2	[{"changed": {"fields": ["Calories", "Protein", "Carbs", "Fats"]}}]	14	1
18	2024-08-28 11:01:29.024595-07	1	Happy Day - 2024-08-28	2	[{"changed": {"fields": ["Calories"]}}]	14	1
19	2024-08-28 11:02:12.925518-07	1	Happy Day - 2024-08-28	2	[{"changed": {"fields": ["Calories", "Protein", "Carbs", "Fats"]}}]	14	1
20	2024-08-28 11:19:07.538572-07	1	NutritionLog object (1)	2	[{"changed": {"fields": ["Carbs", "Protein", "Fats"]}}]	14	1
21	2024-08-28 16:11:53.164543-07	1	Happy Day	2	[{"changed": {"fields": ["Gender"]}}]	7	1
22	2025-02-04 10:08:28.581832-08	4	DavidGK	1	[{"added": {}}]	4	3
23	2025-02-04 10:08:54.834885-08	5	racheldoc	1	[{"added": {}}]	4	3
24	2025-02-04 10:11:17.544594-08	4	DavidGK	2	[{"changed": {"fields": ["password"]}}]	4	3
25	2025-02-04 10:12:33.114337-08	4	DavidGK	2	[{"changed": {"fields": ["First name", "Last name", "Email address", "Staff status", "User permissions"]}}]	4	3
26	2025-02-04 10:13:20.941491-08	5	racheldoc	2	[{"changed": {"fields": ["First name", "Last name", "Email address", "User permissions"]}}]	4	3
27	2025-02-04 10:14:09.504634-08	5	racheldoc	2	[{"changed": {"fields": ["password"]}}]	4	3
28	2025-02-04 10:14:35.183058-08	5	racheldoc	2	[{"changed": {"fields": ["Staff status"]}}]	4	3
29	2025-02-04 10:30:23.958453-08	1	Appointment: Janice with Dr. racheldoc	1	[{"added": {}}]	17	3
30	2025-02-04 10:43:21.5975-08	5	racheldoc	2	[{"changed": {"fields": ["User permissions"]}}]	4	3
\.


--
-- TOC entry 5292 (class 0 OID 16620)
-- Dependencies: 243
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	core	patient
8	ihr_iot_wearables	activitydata
9	ihr_iot_wearables	device
10	ihr_iot_wearables	vitalsigns
11	ihr_cannabinoid_medicine	patientcannabinoidprescription
12	ihr_cannabinoid_medicine	cannabinoidusagelog
13	ihr_cannabinoid_medicine	cannabinoidmedication
14	nutrition	nutritionlog
15	mental_health	moodlog
16	ihr_iot_wearables	iotwearabledata
17	Telemedicine	telemedicineappointment
18	Telemedicine	virtualwaitingroom
19	Telemedicine	medicaldocument
20	Telemedicine	patientvitals
21	Telemedicine	doctortimeoff
22	Telemedicine	doctoravailability
23	Telemedicine	doctorprofile
\.


--
-- TOC entry 5290 (class 0 OID 16612)
-- Dependencies: 241
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2024-08-26 23:09:00.511242-07
2	auth	0001_initial	2024-08-26 23:09:00.601416-07
3	admin	0001_initial	2024-08-26 23:09:00.62369-07
4	admin	0002_logentry_remove_auto_add	2024-08-26 23:09:00.627782-07
5	admin	0003_logentry_add_action_flag_choices	2024-08-26 23:09:00.631535-07
6	contenttypes	0002_remove_content_type_name	2024-08-26 23:09:00.652694-07
7	auth	0002_alter_permission_name_max_length	2024-08-26 23:09:00.656145-07
8	auth	0003_alter_user_email_max_length	2024-08-26 23:09:00.660247-07
9	auth	0004_alter_user_username_opts	2024-08-26 23:09:00.663567-07
10	auth	0005_alter_user_last_login_null	2024-08-26 23:09:00.667069-07
11	auth	0006_require_contenttypes_0002	2024-08-26 23:09:00.668392-07
12	auth	0007_alter_validators_add_error_messages	2024-08-26 23:09:00.67211-07
13	auth	0008_alter_user_username_max_length	2024-08-26 23:09:00.682687-07
14	auth	0009_alter_user_last_name_max_length	2024-08-26 23:09:00.687554-07
15	auth	0010_alter_group_name_max_length	2024-08-26 23:09:00.692554-07
16	auth	0011_update_proxy_permissions	2024-08-26 23:09:00.695554-07
17	auth	0012_alter_user_first_name_max_length	2024-08-26 23:09:00.699509-07
18	core	0001_initial	2024-08-26 23:09:00.706119-07
19	sessions	0001_initial	2024-08-26 23:09:00.720843-07
20	ihr_cannabinoid_medicine	0001_initial	2024-08-27 13:06:58.025254-07
21	ihr_iot_wearables	0001_initial	2024-08-27 13:06:58.086253-07
22	mental_health	0001_initial	2024-08-27 13:06:58.102178-07
23	nutrition	0001_initial	2024-08-27 13:06:58.116484-07
24	nutrition	0002_alter_nutritionlog_calories_alter_nutritionlog_carbs_and_more	2024-08-28 11:18:16.94958-07
25	core	0002_alter_patient_gender	2024-08-28 16:08:47.608747-07
26	ihr_iot_wearables	0002_iotwearabledata	2024-08-28 16:41:17.977914-07
27	Telemedicine	0001_initial	2025-02-04 10:25:00.376412-08
28	Telemedicine	0002_telemedicineappointment_doctor_notes_and_more	2025-02-04 10:39:29.607228-08
29	Telemedicine	0003_auto_20250204_1118	2025-02-04 11:19:01.878335-08
\.


--
-- TOC entry 5309 (class 0 OID 16754)
-- Dependencies: 260
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
k3d7jaqhte4s6qgmq66a7itzlkrh005t	.eJxVjDsOwyAQBe9CHSFYlo9TpvcZECwQnERYMnYV5e6xJRdJ-2bmvZkP21r91vPip8SuTLLL7xYDPXM7QHqEdp85zW1dpsgPhZ-083FO-XU73b-DGnrdaxdyIS0hIxhr0SXt0BJB0TQYgylahKgGYVSOUoGC4qIgsQPCoKxkny_WlTdu:1sjSIx:x9BKXF0z3ixQmzqVr30gFBZSw18qQn1BmIB0NQs9UZM	2024-09-11 16:42:23.399854-07
vk0kb2frrw505cnpkagnlo1a6dlz3bwo	.eJxVjDsOwjAQBe_iGln2hnVkSnrOYO3PJIASKZ8q4u4QKQW0b2be5gqtS1fW2abSq7u45E6_G5M8bdiBPmi4j17GYZl69rviDzr726j2uh7u30FHc_etDU2NAeqZs1IgbkJbhVMiEATMWBUMm4yJNEpsIhiJBcstIgcg9_4AE3o4rQ:1tfObB:PvP_TGqYkS5LECrfr5_0hdKJDTp979siKEHdpD7EY48	2025-02-18 11:28:41.8467-08
\.


--
-- TOC entry 5311 (class 0 OID 16764)
-- Dependencies: 262
-- Data for Name: ihr_cannabinoid_medicine_cannabinoidmedication; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.ihr_cannabinoid_medicine_cannabinoidmedication (id, name, type, description, recommended_dosage, potential_interactions) FROM stdin;
1	CBD	Cannabinoid	cannabidiol capsules	250 mg 3X/day	liver enzymes cyp450 metabolizing other drugs
\.


--
-- TOC entry 5315 (class 0 OID 16778)
-- Dependencies: 266
-- Data for Name: ihr_cannabinoid_medicine_cannabinoidusagelog; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.ihr_cannabinoid_medicine_cannabinoidusagelog (id, usage_datetime, dosage_taken, notes, patient_id, prescription_id) FROM stdin;
\.


--
-- TOC entry 5313 (class 0 OID 16772)
-- Dependencies: 264
-- Data for Name: ihr_cannabinoid_medicine_patientcannabinoidprescription; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.ihr_cannabinoid_medicine_patientcannabinoidprescription (id, prescribing_doctor, prescription_date, start_date, end_date, dosage, frequency, administration_method, medication_id, patient_id) FROM stdin;
1	Dr. Rightallthe time	2024-08-28	2024-08-28	2024-09-30	250 mg	Every 8 hours	oral	1	1
\.


--
-- TOC entry 5319 (class 0 OID 16818)
-- Dependencies: 270
-- Data for Name: ihr_iot_wearables_activitydata; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.ihr_iot_wearables_activitydata (id, date, steps, calories_burned, active_minutes, patient_id, device_id) FROM stdin;
\.


--
-- TOC entry 5317 (class 0 OID 16810)
-- Dependencies: 268
-- Data for Name: ihr_iot_wearables_device; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.ihr_iot_wearables_device (id, device_type, device_id, last_sync, patient_id) FROM stdin;
1	Smartwatch	xx	2024-08-28 10:52:57.446741-07	1
\.


--
-- TOC entry 5327 (class 0 OID 16888)
-- Dependencies: 278
-- Data for Name: ihr_iot_wearables_iotwearabledata; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.ihr_iot_wearables_iotwearabledata (id, "timestamp", patient_id) FROM stdin;
\.


--
-- TOC entry 5321 (class 0 OID 16824)
-- Dependencies: 272
-- Data for Name: ihr_iot_wearables_vitalsigns; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.ihr_iot_wearables_vitalsigns (id, "timestamp", heart_rate, blood_pressure_systolic, blood_pressure_diastolic, temperature, oxygen_saturation, device_id, patient_id) FROM stdin;
\.


--
-- TOC entry 5323 (class 0 OID 16861)
-- Dependencies: 274
-- Data for Name: mental_health_moodlog; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.mental_health_moodlog (id, date, mood, notes, patient_id) FROM stdin;
1	2024-08-28	1		1
\.


--
-- TOC entry 5325 (class 0 OID 16875)
-- Dependencies: 276
-- Data for Name: nutrition_nutritionlog; Type: TABLE DATA; Schema: public; Owner: ihr_user
--

COPY public.nutrition_nutritionlog (id, date, calories, protein, carbs, fats, patient_id) FROM stdin;
1	2024-08-28	139	6	9	4	1
\.


--
-- TOC entry 5329 (class 0 OID 16901)
-- Dependencies: 280
-- Data for Name: patients; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.patients (id, name, dob, gender, contact) FROM stdin;
1	John Doe	1990-01-01	male	john@example.com
\.


--
-- TOC entry 5331 (class 0 OID 16911)
-- Dependencies: 282
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, password, created_at, first_name, last_name, phone, date_of_birth) FROM stdin;
\.


--
-- TOC entry 5391 (class 0 OID 0)
-- Dependencies: 224
-- Name: activity_data_id_seq; Type: SEQUENCE SET; Schema: ihr; Owner: postgres
--

SELECT pg_catalog.setval('ihr.activity_data_id_seq', 1, false);


--
-- TOC entry 5392 (class 0 OID 0)
-- Dependencies: 236
-- Name: cannabinoid_effects_id_seq; Type: SEQUENCE SET; Schema: ihr; Owner: postgres
--

SELECT pg_catalog.setval('ihr.cannabinoid_effects_id_seq', 1, false);


--
-- TOC entry 5393 (class 0 OID 0)
-- Dependencies: 230
-- Name: cannabinoid_medications_id_seq; Type: SEQUENCE SET; Schema: ihr; Owner: postgres
--

SELECT pg_catalog.setval('ihr.cannabinoid_medications_id_seq', 1, false);


--
-- TOC entry 5394 (class 0 OID 0)
-- Dependencies: 238
-- Name: cannabinoid_side_effects_id_seq; Type: SEQUENCE SET; Schema: ihr; Owner: postgres
--

SELECT pg_catalog.setval('ihr.cannabinoid_side_effects_id_seq', 1, false);


--
-- TOC entry 5395 (class 0 OID 0)
-- Dependencies: 234
-- Name: cannabinoid_usage_logs_id_seq; Type: SEQUENCE SET; Schema: ihr; Owner: postgres
--

SELECT pg_catalog.setval('ihr.cannabinoid_usage_logs_id_seq', 1, false);


--
-- TOC entry 5396 (class 0 OID 0)
-- Dependencies: 228
-- Name: device_notifications_id_seq; Type: SEQUENCE SET; Schema: ihr; Owner: postgres
--

SELECT pg_catalog.setval('ihr.device_notifications_id_seq', 1, false);


--
-- TOC entry 5397 (class 0 OID 0)
-- Dependencies: 220
-- Name: devices_id_seq; Type: SEQUENCE SET; Schema: ihr; Owner: postgres
--

SELECT pg_catalog.setval('ihr.devices_id_seq', 1, false);


--
-- TOC entry 5398 (class 0 OID 0)
-- Dependencies: 218
-- Name: medications_id_seq; Type: SEQUENCE SET; Schema: ihr; Owner: postgres
--

SELECT pg_catalog.setval('ihr.medications_id_seq', 1, false);


--
-- TOC entry 5399 (class 0 OID 0)
-- Dependencies: 232
-- Name: patient_cannabinoid_prescriptions_id_seq; Type: SEQUENCE SET; Schema: ihr; Owner: postgres
--

SELECT pg_catalog.setval('ihr.patient_cannabinoid_prescriptions_id_seq', 1, false);


--
-- TOC entry 5400 (class 0 OID 0)
-- Dependencies: 216
-- Name: patients_id_seq; Type: SEQUENCE SET; Schema: ihr; Owner: postgres
--

SELECT pg_catalog.setval('ihr.patients_id_seq', 1, false);


--
-- TOC entry 5401 (class 0 OID 0)
-- Dependencies: 226
-- Name: sleep_data_id_seq; Type: SEQUENCE SET; Schema: ihr; Owner: postgres
--

SELECT pg_catalog.setval('ihr.sleep_data_id_seq', 1, false);


--
-- TOC entry 5402 (class 0 OID 0)
-- Dependencies: 222
-- Name: vital_signs_id_seq; Type: SEQUENCE SET; Schema: ihr; Owner: postgres
--

SELECT pg_catalog.setval('ihr.vital_signs_id_seq', 1, false);


--
-- TOC entry 5403 (class 0 OID 0)
-- Dependencies: 295
-- Name: Telemedicine_doctoravailability_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public."Telemedicine_doctoravailability_id_seq"', 1, false);


--
-- TOC entry 5404 (class 0 OID 0)
-- Dependencies: 291
-- Name: Telemedicine_doctorprofile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public."Telemedicine_doctorprofile_id_seq"', 1, false);


--
-- TOC entry 5405 (class 0 OID 0)
-- Dependencies: 293
-- Name: Telemedicine_doctortimeoff_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public."Telemedicine_doctortimeoff_id_seq"', 1, false);


--
-- TOC entry 5406 (class 0 OID 0)
-- Dependencies: 287
-- Name: Telemedicine_medicaldocument_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public."Telemedicine_medicaldocument_id_seq"', 1, false);


--
-- TOC entry 5407 (class 0 OID 0)
-- Dependencies: 283
-- Name: Telemedicine_patientvitals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public."Telemedicine_patientvitals_id_seq"', 1, false);


--
-- TOC entry 5408 (class 0 OID 0)
-- Dependencies: 285
-- Name: Telemedicine_telemedicineappointment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public."Telemedicine_telemedicineappointment_id_seq"', 1, true);


--
-- TOC entry 5409 (class 0 OID 0)
-- Dependencies: 289
-- Name: Telemedicine_virtualwaitingroom_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public."Telemedicine_virtualwaitingroom_id_seq"', 1, false);


--
-- TOC entry 5410 (class 0 OID 0)
-- Dependencies: 246
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- TOC entry 5411 (class 0 OID 0)
-- Dependencies: 248
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- TOC entry 5412 (class 0 OID 0)
-- Dependencies: 244
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 92, true);


--
-- TOC entry 5413 (class 0 OID 0)
-- Dependencies: 252
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);


--
-- TOC entry 5414 (class 0 OID 0)
-- Dependencies: 250
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.auth_user_id_seq', 6, true);


--
-- TOC entry 5415 (class 0 OID 0)
-- Dependencies: 254
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 172, true);


--
-- TOC entry 5416 (class 0 OID 0)
-- Dependencies: 258
-- Name: core_patient_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.core_patient_id_seq', 1, true);


--
-- TOC entry 5417 (class 0 OID 0)
-- Dependencies: 256
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 30, true);


--
-- TOC entry 5418 (class 0 OID 0)
-- Dependencies: 242
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 23, true);


--
-- TOC entry 5419 (class 0 OID 0)
-- Dependencies: 240
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 29, true);


--
-- TOC entry 5420 (class 0 OID 0)
-- Dependencies: 261
-- Name: ihr_cannabinoid_medicine_cannabinoidmedication_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.ihr_cannabinoid_medicine_cannabinoidmedication_id_seq', 1, true);


--
-- TOC entry 5421 (class 0 OID 0)
-- Dependencies: 265
-- Name: ihr_cannabinoid_medicine_cannabinoidusagelog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.ihr_cannabinoid_medicine_cannabinoidusagelog_id_seq', 1, false);


--
-- TOC entry 5422 (class 0 OID 0)
-- Dependencies: 263
-- Name: ihr_cannabinoid_medicine_patientcannabinoidprescription_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.ihr_cannabinoid_medicine_patientcannabinoidprescription_id_seq', 1, true);


--
-- TOC entry 5423 (class 0 OID 0)
-- Dependencies: 269
-- Name: ihr_iot_wearables_activitydata_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.ihr_iot_wearables_activitydata_id_seq', 1, false);


--
-- TOC entry 5424 (class 0 OID 0)
-- Dependencies: 267
-- Name: ihr_iot_wearables_device_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.ihr_iot_wearables_device_id_seq', 1, true);


--
-- TOC entry 5425 (class 0 OID 0)
-- Dependencies: 277
-- Name: ihr_iot_wearables_iotwearabledata_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.ihr_iot_wearables_iotwearabledata_id_seq', 1, false);


--
-- TOC entry 5426 (class 0 OID 0)
-- Dependencies: 271
-- Name: ihr_iot_wearables_vitalsigns_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.ihr_iot_wearables_vitalsigns_id_seq', 1, false);


--
-- TOC entry 5427 (class 0 OID 0)
-- Dependencies: 273
-- Name: mental_health_moodlog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.mental_health_moodlog_id_seq', 1, true);


--
-- TOC entry 5428 (class 0 OID 0)
-- Dependencies: 275
-- Name: nutrition_nutritionlog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ihr_user
--

SELECT pg_catalog.setval('public.nutrition_nutritionlog_id_seq', 1, true);


--
-- TOC entry 5429 (class 0 OID 0)
-- Dependencies: 279
-- Name: patients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.patients_id_seq', 1, true);


--
-- TOC entry 5430 (class 0 OID 0)
-- Dependencies: 281
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- TOC entry 4928 (class 2606 OID 16459)
-- Name: activity_data activity_data_pkey; Type: CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.activity_data
    ADD CONSTRAINT activity_data_pkey PRIMARY KEY (id);


--
-- TOC entry 4951 (class 2606 OID 16569)
-- Name: cannabinoid_effects cannabinoid_effects_pkey; Type: CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_effects
    ADD CONSTRAINT cannabinoid_effects_pkey PRIMARY KEY (id);


--
-- TOC entry 4940 (class 2606 OID 16523)
-- Name: cannabinoid_medications cannabinoid_medications_pkey; Type: CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_medications
    ADD CONSTRAINT cannabinoid_medications_pkey PRIMARY KEY (id);


--
-- TOC entry 4955 (class 2606 OID 16589)
-- Name: cannabinoid_side_effects cannabinoid_side_effects_pkey; Type: CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_side_effects
    ADD CONSTRAINT cannabinoid_side_effects_pkey PRIMARY KEY (id);


--
-- TOC entry 4946 (class 2606 OID 16549)
-- Name: cannabinoid_usage_logs cannabinoid_usage_logs_pkey; Type: CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_usage_logs
    ADD CONSTRAINT cannabinoid_usage_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 4938 (class 2606 OID 16495)
-- Name: device_notifications device_notifications_pkey; Type: CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.device_notifications
    ADD CONSTRAINT device_notifications_pkey PRIMARY KEY (id);


--
-- TOC entry 4921 (class 2606 OID 16430)
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (id);


--
-- TOC entry 4919 (class 2606 OID 16416)
-- Name: medications medications_pkey; Type: CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.medications
    ADD CONSTRAINT medications_pkey PRIMARY KEY (id);


--
-- TOC entry 4944 (class 2606 OID 16530)
-- Name: patient_cannabinoid_prescriptions patient_cannabinoid_prescriptions_pkey; Type: CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.patient_cannabinoid_prescriptions
    ADD CONSTRAINT patient_cannabinoid_prescriptions_pkey PRIMARY KEY (id);


--
-- TOC entry 4917 (class 2606 OID 16408)
-- Name: patients patients_pkey; Type: CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.patients
    ADD CONSTRAINT patients_pkey PRIMARY KEY (id);


--
-- TOC entry 4936 (class 2606 OID 16476)
-- Name: sleep_data sleep_data_pkey; Type: CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.sleep_data
    ADD CONSTRAINT sleep_data_pkey PRIMARY KEY (id);


--
-- TOC entry 4926 (class 2606 OID 16442)
-- Name: vital_signs vital_signs_pkey; Type: CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.vital_signs
    ADD CONSTRAINT vital_signs_pkey PRIMARY KEY (id);


--
-- TOC entry 5070 (class 2606 OID 17032)
-- Name: Telemedicine_doctoravailability Telemedicine_doctoravail_doctor_id_day_of_week_db2da508_uniq; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_doctoravailability"
    ADD CONSTRAINT "Telemedicine_doctoravail_doctor_id_day_of_week_db2da508_uniq" UNIQUE (doctor_id, day_of_week);


--
-- TOC entry 5073 (class 2606 OID 17019)
-- Name: Telemedicine_doctoravailability Telemedicine_doctoravailability_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_doctoravailability"
    ADD CONSTRAINT "Telemedicine_doctoravailability_pkey" PRIMARY KEY (id);


--
-- TOC entry 5063 (class 2606 OID 17005)
-- Name: Telemedicine_doctorprofile Telemedicine_doctorprofile_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_doctorprofile"
    ADD CONSTRAINT "Telemedicine_doctorprofile_pkey" PRIMARY KEY (id);


--
-- TOC entry 5065 (class 2606 OID 17007)
-- Name: Telemedicine_doctorprofile Telemedicine_doctorprofile_user_id_key; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_doctorprofile"
    ADD CONSTRAINT "Telemedicine_doctorprofile_user_id_key" UNIQUE (user_id);


--
-- TOC entry 5068 (class 2606 OID 17013)
-- Name: Telemedicine_doctortimeoff Telemedicine_doctortimeoff_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_doctortimeoff"
    ADD CONSTRAINT "Telemedicine_doctortimeoff_pkey" PRIMARY KEY (id);


--
-- TOC entry 5055 (class 2606 OID 16943)
-- Name: Telemedicine_medicaldocument Telemedicine_medicaldocument_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_medicaldocument"
    ADD CONSTRAINT "Telemedicine_medicaldocument_pkey" PRIMARY KEY (id);


--
-- TOC entry 5048 (class 2606 OID 16929)
-- Name: Telemedicine_patientvitals Telemedicine_patientvitals_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_patientvitals"
    ADD CONSTRAINT "Telemedicine_patientvitals_pkey" PRIMARY KEY (id);


--
-- TOC entry 5051 (class 2606 OID 16935)
-- Name: Telemedicine_telemedicineappointment Telemedicine_telemedicineappointment_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_telemedicineappointment"
    ADD CONSTRAINT "Telemedicine_telemedicineappointment_pkey" PRIMARY KEY (id);


--
-- TOC entry 5058 (class 2606 OID 16951)
-- Name: Telemedicine_virtualwaitingroom Telemedicine_virtualwaitingroom_appointment_id_key; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_virtualwaitingroom"
    ADD CONSTRAINT "Telemedicine_virtualwaitingroom_appointment_id_key" UNIQUE (appointment_id);


--
-- TOC entry 5061 (class 2606 OID 16949)
-- Name: Telemedicine_virtualwaitingroom Telemedicine_virtualwaitingroom_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_virtualwaitingroom"
    ADD CONSTRAINT "Telemedicine_virtualwaitingroom_pkey" PRIMARY KEY (id);


--
-- TOC entry 4971 (class 2606 OID 16746)
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- TOC entry 4976 (class 2606 OID 16677)
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- TOC entry 4979 (class 2606 OID 16646)
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 4973 (class 2606 OID 16638)
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- TOC entry 4966 (class 2606 OID 16668)
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- TOC entry 4968 (class 2606 OID 16632)
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- TOC entry 4987 (class 2606 OID 16660)
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- TOC entry 4990 (class 2606 OID 16692)
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- TOC entry 4981 (class 2606 OID 16652)
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- TOC entry 4993 (class 2606 OID 16666)
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 4996 (class 2606 OID 16706)
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- TOC entry 4984 (class 2606 OID 16741)
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- TOC entry 5002 (class 2606 OID 16753)
-- Name: core_patient core_patient_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.core_patient
    ADD CONSTRAINT core_patient_pkey PRIMARY KEY (id);


--
-- TOC entry 4999 (class 2606 OID 16727)
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- TOC entry 4961 (class 2606 OID 16626)
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- TOC entry 4963 (class 2606 OID 16624)
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- TOC entry 4959 (class 2606 OID 16618)
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- TOC entry 5005 (class 2606 OID 16760)
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- TOC entry 5008 (class 2606 OID 16770)
-- Name: ihr_cannabinoid_medicine_cannabinoidmedication ihr_cannabinoid_medicine_cannabinoidmedication_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_cannabinoid_medicine_cannabinoidmedication
    ADD CONSTRAINT ihr_cannabinoid_medicine_cannabinoidmedication_pkey PRIMARY KEY (id);


--
-- TOC entry 5016 (class 2606 OID 16784)
-- Name: ihr_cannabinoid_medicine_cannabinoidusagelog ihr_cannabinoid_medicine_cannabinoidusagelog_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_cannabinoid_medicine_cannabinoidusagelog
    ADD CONSTRAINT ihr_cannabinoid_medicine_cannabinoidusagelog_pkey PRIMARY KEY (id);


--
-- TOC entry 5012 (class 2606 OID 16776)
-- Name: ihr_cannabinoid_medicine_patientcannabinoidprescription ihr_cannabinoid_medicine_patientcannabinoidprescription_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_cannabinoid_medicine_patientcannabinoidprescription
    ADD CONSTRAINT ihr_cannabinoid_medicine_patientcannabinoidprescription_pkey PRIMARY KEY (id);


--
-- TOC entry 5026 (class 2606 OID 16822)
-- Name: ihr_iot_wearables_activitydata ihr_iot_wearables_activitydata_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_iot_wearables_activitydata
    ADD CONSTRAINT ihr_iot_wearables_activitydata_pkey PRIMARY KEY (id);


--
-- TOC entry 5019 (class 2606 OID 16816)
-- Name: ihr_iot_wearables_device ihr_iot_wearables_device_device_id_key; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_iot_wearables_device
    ADD CONSTRAINT ihr_iot_wearables_device_device_id_key UNIQUE (device_id);


--
-- TOC entry 5022 (class 2606 OID 16814)
-- Name: ihr_iot_wearables_device ihr_iot_wearables_device_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_iot_wearables_device
    ADD CONSTRAINT ihr_iot_wearables_device_pkey PRIMARY KEY (id);


--
-- TOC entry 5039 (class 2606 OID 16892)
-- Name: ihr_iot_wearables_iotwearabledata ihr_iot_wearables_iotwearabledata_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_iot_wearables_iotwearabledata
    ADD CONSTRAINT ihr_iot_wearables_iotwearabledata_pkey PRIMARY KEY (id);


--
-- TOC entry 5030 (class 2606 OID 16828)
-- Name: ihr_iot_wearables_vitalsigns ihr_iot_wearables_vitalsigns_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_iot_wearables_vitalsigns
    ADD CONSTRAINT ihr_iot_wearables_vitalsigns_pkey PRIMARY KEY (id);


--
-- TOC entry 5033 (class 2606 OID 16867)
-- Name: mental_health_moodlog mental_health_moodlog_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.mental_health_moodlog
    ADD CONSTRAINT mental_health_moodlog_pkey PRIMARY KEY (id);


--
-- TOC entry 5036 (class 2606 OID 16879)
-- Name: nutrition_nutritionlog nutrition_nutritionlog_pkey; Type: CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.nutrition_nutritionlog
    ADD CONSTRAINT nutrition_nutritionlog_pkey PRIMARY KEY (id);


--
-- TOC entry 5041 (class 2606 OID 16906)
-- Name: patients patients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_pkey PRIMARY KEY (id);


--
-- TOC entry 5043 (class 2606 OID 16921)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 5045 (class 2606 OID 16919)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4929 (class 1259 OID 16506)
-- Name: idx_activity_data_date; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_activity_data_date ON ihr.activity_data USING btree (date);


--
-- TOC entry 4930 (class 1259 OID 16505)
-- Name: idx_activity_data_device_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_activity_data_device_id ON ihr.activity_data USING btree (device_id);


--
-- TOC entry 4931 (class 1259 OID 16504)
-- Name: idx_activity_data_patient_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_activity_data_patient_id ON ihr.activity_data USING btree (patient_id);


--
-- TOC entry 4952 (class 1259 OID 16605)
-- Name: idx_cannabinoid_effects_patient_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_cannabinoid_effects_patient_id ON ihr.cannabinoid_effects USING btree (patient_id);


--
-- TOC entry 4953 (class 1259 OID 16606)
-- Name: idx_cannabinoid_effects_usage_log_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_cannabinoid_effects_usage_log_id ON ihr.cannabinoid_effects USING btree (usage_log_id);


--
-- TOC entry 4956 (class 1259 OID 16607)
-- Name: idx_cannabinoid_side_effects_patient_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_cannabinoid_side_effects_patient_id ON ihr.cannabinoid_side_effects USING btree (patient_id);


--
-- TOC entry 4957 (class 1259 OID 16608)
-- Name: idx_cannabinoid_side_effects_usage_log_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_cannabinoid_side_effects_usage_log_id ON ihr.cannabinoid_side_effects USING btree (usage_log_id);


--
-- TOC entry 4947 (class 1259 OID 16602)
-- Name: idx_cannabinoid_usage_logs_patient_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_cannabinoid_usage_logs_patient_id ON ihr.cannabinoid_usage_logs USING btree (patient_id);


--
-- TOC entry 4948 (class 1259 OID 16603)
-- Name: idx_cannabinoid_usage_logs_prescription_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_cannabinoid_usage_logs_prescription_id ON ihr.cannabinoid_usage_logs USING btree (prescription_id);


--
-- TOC entry 4949 (class 1259 OID 16604)
-- Name: idx_cannabinoid_usage_logs_usage_datetime; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_cannabinoid_usage_logs_usage_datetime ON ihr.cannabinoid_usage_logs USING btree (usage_datetime);


--
-- TOC entry 4941 (class 1259 OID 16601)
-- Name: idx_patient_cannabinoid_prescriptions_medication_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_patient_cannabinoid_prescriptions_medication_id ON ihr.patient_cannabinoid_prescriptions USING btree (medication_id);


--
-- TOC entry 4942 (class 1259 OID 16600)
-- Name: idx_patient_cannabinoid_prescriptions_patient_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_patient_cannabinoid_prescriptions_patient_id ON ihr.patient_cannabinoid_prescriptions USING btree (patient_id);


--
-- TOC entry 4932 (class 1259 OID 16508)
-- Name: idx_sleep_data_device_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_sleep_data_device_id ON ihr.sleep_data USING btree (device_id);


--
-- TOC entry 4933 (class 1259 OID 16507)
-- Name: idx_sleep_data_patient_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_sleep_data_patient_id ON ihr.sleep_data USING btree (patient_id);


--
-- TOC entry 4934 (class 1259 OID 16509)
-- Name: idx_sleep_data_sleep_start; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_sleep_data_sleep_start ON ihr.sleep_data USING btree (sleep_start);


--
-- TOC entry 4922 (class 1259 OID 16502)
-- Name: idx_vital_signs_device_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_vital_signs_device_id ON ihr.vital_signs USING btree (device_id);


--
-- TOC entry 4923 (class 1259 OID 16501)
-- Name: idx_vital_signs_patient_id; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_vital_signs_patient_id ON ihr.vital_signs USING btree (patient_id);


--
-- TOC entry 4924 (class 1259 OID 16503)
-- Name: idx_vital_signs_timestamp; Type: INDEX; Schema: ihr; Owner: postgres
--

CREATE INDEX idx_vital_signs_timestamp ON ihr.vital_signs USING btree ("timestamp");


--
-- TOC entry 5071 (class 1259 OID 17038)
-- Name: Telemedicine_doctoravailability_doctor_id_b75a7849; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX "Telemedicine_doctoravailability_doctor_id_b75a7849" ON public."Telemedicine_doctoravailability" USING btree (doctor_id);


--
-- TOC entry 5066 (class 1259 OID 17030)
-- Name: Telemedicine_doctortimeoff_doctor_id_e6ff4de7; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX "Telemedicine_doctortimeoff_doctor_id_e6ff4de7" ON public."Telemedicine_doctortimeoff" USING btree (doctor_id);


--
-- TOC entry 5053 (class 1259 OID 16981)
-- Name: Telemedicine_medicaldocument_appointment_id_0bba97e2; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX "Telemedicine_medicaldocument_appointment_id_0bba97e2" ON public."Telemedicine_medicaldocument" USING btree (appointment_id);


--
-- TOC entry 5056 (class 1259 OID 16980)
-- Name: Telemedicine_medicaldocument_uploaded_by_id_09d2ca4c; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX "Telemedicine_medicaldocument_uploaded_by_id_09d2ca4c" ON public."Telemedicine_medicaldocument" USING btree (uploaded_by_id);


--
-- TOC entry 5046 (class 1259 OID 16957)
-- Name: Telemedicine_patientvitals_patient_id_ac1b27d2; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX "Telemedicine_patientvitals_patient_id_ac1b27d2" ON public."Telemedicine_patientvitals" USING btree (patient_id);


--
-- TOC entry 5049 (class 1259 OID 16968)
-- Name: Telemedicine_telemedicineappointment_patient_id_cfbb4a92; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX "Telemedicine_telemedicineappointment_patient_id_cfbb4a92" ON public."Telemedicine_telemedicineappointment" USING btree (patient_id);


--
-- TOC entry 5052 (class 1259 OID 16969)
-- Name: Telemedicine_telemedicineappointment_provider_id_fe6190f7; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX "Telemedicine_telemedicineappointment_provider_id_fe6190f7" ON public."Telemedicine_telemedicineappointment" USING btree (provider_id);


--
-- TOC entry 5059 (class 1259 OID 16992)
-- Name: Telemedicine_virtualwaitingroom_patient_id_f9b2d660; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX "Telemedicine_virtualwaitingroom_patient_id_f9b2d660" ON public."Telemedicine_virtualwaitingroom" USING btree (patient_id);


--
-- TOC entry 4969 (class 1259 OID 16747)
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- TOC entry 4974 (class 1259 OID 16688)
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- TOC entry 4977 (class 1259 OID 16689)
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- TOC entry 4964 (class 1259 OID 16674)
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- TOC entry 4985 (class 1259 OID 16704)
-- Name: auth_user_groups_group_id_97559544; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);


--
-- TOC entry 4988 (class 1259 OID 16703)
-- Name: auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);


--
-- TOC entry 4991 (class 1259 OID 16718)
-- Name: auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);


--
-- TOC entry 4994 (class 1259 OID 16717)
-- Name: auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);


--
-- TOC entry 4982 (class 1259 OID 16742)
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX auth_user_username_6821ab7c_like ON public.auth_user USING btree (username varchar_pattern_ops);


--
-- TOC entry 4997 (class 1259 OID 16738)
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- TOC entry 5000 (class 1259 OID 16739)
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- TOC entry 5003 (class 1259 OID 16762)
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- TOC entry 5006 (class 1259 OID 16761)
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- TOC entry 5013 (class 1259 OID 16807)
-- Name: ihr_cannabinoid_medicine_c_patient_id_3c9b0878; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX ihr_cannabinoid_medicine_c_patient_id_3c9b0878 ON public.ihr_cannabinoid_medicine_cannabinoidusagelog USING btree (patient_id);


--
-- TOC entry 5014 (class 1259 OID 16808)
-- Name: ihr_cannabinoid_medicine_c_prescription_id_1b521312; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX ihr_cannabinoid_medicine_c_prescription_id_1b521312 ON public.ihr_cannabinoid_medicine_cannabinoidusagelog USING btree (prescription_id);


--
-- TOC entry 5009 (class 1259 OID 16795)
-- Name: ihr_cannabinoid_medicine_p_medication_id_8ca6df71; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX ihr_cannabinoid_medicine_p_medication_id_8ca6df71 ON public.ihr_cannabinoid_medicine_patientcannabinoidprescription USING btree (medication_id);


--
-- TOC entry 5010 (class 1259 OID 16796)
-- Name: ihr_cannabinoid_medicine_p_patient_id_732e4447; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX ihr_cannabinoid_medicine_p_patient_id_732e4447 ON public.ihr_cannabinoid_medicine_patientcannabinoidprescription USING btree (patient_id);


--
-- TOC entry 5023 (class 1259 OID 16847)
-- Name: ihr_iot_wearables_activitydata_device_id_36354f3b; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX ihr_iot_wearables_activitydata_device_id_36354f3b ON public.ihr_iot_wearables_activitydata USING btree (device_id);


--
-- TOC entry 5024 (class 1259 OID 16846)
-- Name: ihr_iot_wearables_activitydata_patient_id_c304b163; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX ihr_iot_wearables_activitydata_patient_id_c304b163 ON public.ihr_iot_wearables_activitydata USING btree (patient_id);


--
-- TOC entry 5017 (class 1259 OID 16834)
-- Name: ihr_iot_wearables_device_device_id_3ea37f83_like; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX ihr_iot_wearables_device_device_id_3ea37f83_like ON public.ihr_iot_wearables_device USING btree (device_id varchar_pattern_ops);


--
-- TOC entry 5020 (class 1259 OID 16835)
-- Name: ihr_iot_wearables_device_patient_id_8d9a3745; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX ihr_iot_wearables_device_patient_id_8d9a3745 ON public.ihr_iot_wearables_device USING btree (patient_id);


--
-- TOC entry 5037 (class 1259 OID 16898)
-- Name: ihr_iot_wearables_iotwearabledata_patient_id_17e9dffe; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX ihr_iot_wearables_iotwearabledata_patient_id_17e9dffe ON public.ihr_iot_wearables_iotwearabledata USING btree (patient_id);


--
-- TOC entry 5027 (class 1259 OID 16858)
-- Name: ihr_iot_wearables_vitalsigns_device_id_1bbcae8c; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX ihr_iot_wearables_vitalsigns_device_id_1bbcae8c ON public.ihr_iot_wearables_vitalsigns USING btree (device_id);


--
-- TOC entry 5028 (class 1259 OID 16859)
-- Name: ihr_iot_wearables_vitalsigns_patient_id_2f7931a9; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX ihr_iot_wearables_vitalsigns_patient_id_2f7931a9 ON public.ihr_iot_wearables_vitalsigns USING btree (patient_id);


--
-- TOC entry 5031 (class 1259 OID 16873)
-- Name: mental_health_moodlog_patient_id_dad90c43; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX mental_health_moodlog_patient_id_dad90c43 ON public.mental_health_moodlog USING btree (patient_id);


--
-- TOC entry 5034 (class 1259 OID 16885)
-- Name: nutrition_nutritionlog_patient_id_7727de11; Type: INDEX; Schema: public; Owner: ihr_user
--

CREATE INDEX nutrition_nutritionlog_patient_id_7727de11 ON public.nutrition_nutritionlog USING btree (patient_id);


--
-- TOC entry 5078 (class 2606 OID 16465)
-- Name: activity_data activity_data_device_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.activity_data
    ADD CONSTRAINT activity_data_device_id_fkey FOREIGN KEY (device_id) REFERENCES ihr.devices(id);


--
-- TOC entry 5079 (class 2606 OID 16460)
-- Name: activity_data activity_data_patient_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.activity_data
    ADD CONSTRAINT activity_data_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES ihr.patients(id);


--
-- TOC entry 5087 (class 2606 OID 16570)
-- Name: cannabinoid_effects cannabinoid_effects_patient_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_effects
    ADD CONSTRAINT cannabinoid_effects_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES ihr.patients(id);


--
-- TOC entry 5088 (class 2606 OID 16575)
-- Name: cannabinoid_effects cannabinoid_effects_usage_log_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_effects
    ADD CONSTRAINT cannabinoid_effects_usage_log_id_fkey FOREIGN KEY (usage_log_id) REFERENCES ihr.cannabinoid_usage_logs(id);


--
-- TOC entry 5089 (class 2606 OID 16590)
-- Name: cannabinoid_side_effects cannabinoid_side_effects_patient_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_side_effects
    ADD CONSTRAINT cannabinoid_side_effects_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES ihr.patients(id);


--
-- TOC entry 5090 (class 2606 OID 16595)
-- Name: cannabinoid_side_effects cannabinoid_side_effects_usage_log_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_side_effects
    ADD CONSTRAINT cannabinoid_side_effects_usage_log_id_fkey FOREIGN KEY (usage_log_id) REFERENCES ihr.cannabinoid_usage_logs(id);


--
-- TOC entry 5085 (class 2606 OID 16550)
-- Name: cannabinoid_usage_logs cannabinoid_usage_logs_patient_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_usage_logs
    ADD CONSTRAINT cannabinoid_usage_logs_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES ihr.patients(id);


--
-- TOC entry 5086 (class 2606 OID 16555)
-- Name: cannabinoid_usage_logs cannabinoid_usage_logs_prescription_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.cannabinoid_usage_logs
    ADD CONSTRAINT cannabinoid_usage_logs_prescription_id_fkey FOREIGN KEY (prescription_id) REFERENCES ihr.patient_cannabinoid_prescriptions(id);


--
-- TOC entry 5082 (class 2606 OID 16496)
-- Name: device_notifications device_notifications_device_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.device_notifications
    ADD CONSTRAINT device_notifications_device_id_fkey FOREIGN KEY (device_id) REFERENCES ihr.devices(id);


--
-- TOC entry 5075 (class 2606 OID 16431)
-- Name: devices devices_patient_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.devices
    ADD CONSTRAINT devices_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES ihr.patients(id);


--
-- TOC entry 5074 (class 2606 OID 16417)
-- Name: medications medications_patient_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.medications
    ADD CONSTRAINT medications_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES ihr.patients(id);


--
-- TOC entry 5083 (class 2606 OID 16536)
-- Name: patient_cannabinoid_prescriptions patient_cannabinoid_prescriptions_medication_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.patient_cannabinoid_prescriptions
    ADD CONSTRAINT patient_cannabinoid_prescriptions_medication_id_fkey FOREIGN KEY (medication_id) REFERENCES ihr.cannabinoid_medications(id);


--
-- TOC entry 5084 (class 2606 OID 16531)
-- Name: patient_cannabinoid_prescriptions patient_cannabinoid_prescriptions_patient_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.patient_cannabinoid_prescriptions
    ADD CONSTRAINT patient_cannabinoid_prescriptions_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES ihr.patients(id);


--
-- TOC entry 5080 (class 2606 OID 16482)
-- Name: sleep_data sleep_data_device_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.sleep_data
    ADD CONSTRAINT sleep_data_device_id_fkey FOREIGN KEY (device_id) REFERENCES ihr.devices(id);


--
-- TOC entry 5081 (class 2606 OID 16477)
-- Name: sleep_data sleep_data_patient_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.sleep_data
    ADD CONSTRAINT sleep_data_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES ihr.patients(id);


--
-- TOC entry 5076 (class 2606 OID 16448)
-- Name: vital_signs vital_signs_device_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.vital_signs
    ADD CONSTRAINT vital_signs_device_id_fkey FOREIGN KEY (device_id) REFERENCES ihr.devices(id);


--
-- TOC entry 5077 (class 2606 OID 16443)
-- Name: vital_signs vital_signs_patient_id_fkey; Type: FK CONSTRAINT; Schema: ihr; Owner: postgres
--

ALTER TABLE ONLY ihr.vital_signs
    ADD CONSTRAINT vital_signs_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES ihr.patients(id);


--
-- TOC entry 5121 (class 2606 OID 17033)
-- Name: Telemedicine_doctoravailability Telemedicine_doctora_doctor_id_b75a7849_fk_Telemedic; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_doctoravailability"
    ADD CONSTRAINT "Telemedicine_doctora_doctor_id_b75a7849_fk_Telemedic" FOREIGN KEY (doctor_id) REFERENCES public."Telemedicine_doctorprofile"(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5119 (class 2606 OID 17020)
-- Name: Telemedicine_doctorprofile Telemedicine_doctorprofile_user_id_85fed446_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_doctorprofile"
    ADD CONSTRAINT "Telemedicine_doctorprofile_user_id_85fed446_fk_auth_user_id" FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5120 (class 2606 OID 17025)
-- Name: Telemedicine_doctortimeoff Telemedicine_doctort_doctor_id_e6ff4de7_fk_Telemedic; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_doctortimeoff"
    ADD CONSTRAINT "Telemedicine_doctort_doctor_id_e6ff4de7_fk_Telemedic" FOREIGN KEY (doctor_id) REFERENCES public."Telemedicine_doctorprofile"(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5115 (class 2606 OID 16975)
-- Name: Telemedicine_medicaldocument Telemedicine_medical_appointment_id_0bba97e2_fk_Telemedic; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_medicaldocument"
    ADD CONSTRAINT "Telemedicine_medical_appointment_id_0bba97e2_fk_Telemedic" FOREIGN KEY (appointment_id) REFERENCES public."Telemedicine_telemedicineappointment"(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5116 (class 2606 OID 16970)
-- Name: Telemedicine_medicaldocument Telemedicine_medical_uploaded_by_id_09d2ca4c_fk_auth_user; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_medicaldocument"
    ADD CONSTRAINT "Telemedicine_medical_uploaded_by_id_09d2ca4c_fk_auth_user" FOREIGN KEY (uploaded_by_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5112 (class 2606 OID 16952)
-- Name: Telemedicine_patientvitals Telemedicine_patientvitals_patient_id_ac1b27d2_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_patientvitals"
    ADD CONSTRAINT "Telemedicine_patientvitals_patient_id_ac1b27d2_fk_auth_user_id" FOREIGN KEY (patient_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5113 (class 2606 OID 16958)
-- Name: Telemedicine_telemedicineappointment Telemedicine_telemed_patient_id_cfbb4a92_fk_auth_user; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_telemedicineappointment"
    ADD CONSTRAINT "Telemedicine_telemed_patient_id_cfbb4a92_fk_auth_user" FOREIGN KEY (patient_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5114 (class 2606 OID 16963)
-- Name: Telemedicine_telemedicineappointment Telemedicine_telemed_provider_id_fe6190f7_fk_auth_user; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_telemedicineappointment"
    ADD CONSTRAINT "Telemedicine_telemed_provider_id_fe6190f7_fk_auth_user" FOREIGN KEY (provider_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5117 (class 2606 OID 16982)
-- Name: Telemedicine_virtualwaitingroom Telemedicine_virtual_appointment_id_fde0ceeb_fk_Telemedic; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_virtualwaitingroom"
    ADD CONSTRAINT "Telemedicine_virtual_appointment_id_fde0ceeb_fk_Telemedic" FOREIGN KEY (appointment_id) REFERENCES public."Telemedicine_telemedicineappointment"(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5118 (class 2606 OID 16987)
-- Name: Telemedicine_virtualwaitingroom Telemedicine_virtual_patient_id_f9b2d660_fk_auth_user; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public."Telemedicine_virtualwaitingroom"
    ADD CONSTRAINT "Telemedicine_virtual_patient_id_f9b2d660_fk_auth_user" FOREIGN KEY (patient_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5092 (class 2606 OID 16683)
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5093 (class 2606 OID 16678)
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5091 (class 2606 OID 16669)
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5094 (class 2606 OID 16698)
-- Name: auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5095 (class 2606 OID 16693)
-- Name: auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5096 (class 2606 OID 16712)
-- Name: auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5097 (class 2606 OID 16707)
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5098 (class 2606 OID 16728)
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5099 (class 2606 OID 16733)
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5100 (class 2606 OID 16785)
-- Name: ihr_cannabinoid_medicine_patientcannabinoidprescription ihr_cannabinoid_medi_medication_id_8ca6df71_fk_ihr_canna; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_cannabinoid_medicine_patientcannabinoidprescription
    ADD CONSTRAINT ihr_cannabinoid_medi_medication_id_8ca6df71_fk_ihr_canna FOREIGN KEY (medication_id) REFERENCES public.ihr_cannabinoid_medicine_cannabinoidmedication(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5102 (class 2606 OID 16797)
-- Name: ihr_cannabinoid_medicine_cannabinoidusagelog ihr_cannabinoid_medi_patient_id_3c9b0878_fk_core_pati; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_cannabinoid_medicine_cannabinoidusagelog
    ADD CONSTRAINT ihr_cannabinoid_medi_patient_id_3c9b0878_fk_core_pati FOREIGN KEY (patient_id) REFERENCES public.core_patient(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5101 (class 2606 OID 16790)
-- Name: ihr_cannabinoid_medicine_patientcannabinoidprescription ihr_cannabinoid_medi_patient_id_732e4447_fk_core_pati; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_cannabinoid_medicine_patientcannabinoidprescription
    ADD CONSTRAINT ihr_cannabinoid_medi_patient_id_732e4447_fk_core_pati FOREIGN KEY (patient_id) REFERENCES public.core_patient(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5103 (class 2606 OID 16802)
-- Name: ihr_cannabinoid_medicine_cannabinoidusagelog ihr_cannabinoid_medi_prescription_id_1b521312_fk_ihr_canna; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_cannabinoid_medicine_cannabinoidusagelog
    ADD CONSTRAINT ihr_cannabinoid_medi_prescription_id_1b521312_fk_ihr_canna FOREIGN KEY (prescription_id) REFERENCES public.ihr_cannabinoid_medicine_patientcannabinoidprescription(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5105 (class 2606 OID 16841)
-- Name: ihr_iot_wearables_activitydata ihr_iot_wearables_ac_device_id_36354f3b_fk_ihr_iot_w; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_iot_wearables_activitydata
    ADD CONSTRAINT ihr_iot_wearables_ac_device_id_36354f3b_fk_ihr_iot_w FOREIGN KEY (device_id) REFERENCES public.ihr_iot_wearables_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5106 (class 2606 OID 16836)
-- Name: ihr_iot_wearables_activitydata ihr_iot_wearables_ac_patient_id_c304b163_fk_core_pati; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_iot_wearables_activitydata
    ADD CONSTRAINT ihr_iot_wearables_ac_patient_id_c304b163_fk_core_pati FOREIGN KEY (patient_id) REFERENCES public.core_patient(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5104 (class 2606 OID 16829)
-- Name: ihr_iot_wearables_device ihr_iot_wearables_device_patient_id_8d9a3745_fk_core_patient_id; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_iot_wearables_device
    ADD CONSTRAINT ihr_iot_wearables_device_patient_id_8d9a3745_fk_core_patient_id FOREIGN KEY (patient_id) REFERENCES public.core_patient(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5111 (class 2606 OID 16893)
-- Name: ihr_iot_wearables_iotwearabledata ihr_iot_wearables_io_patient_id_17e9dffe_fk_core_pati; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_iot_wearables_iotwearabledata
    ADD CONSTRAINT ihr_iot_wearables_io_patient_id_17e9dffe_fk_core_pati FOREIGN KEY (patient_id) REFERENCES public.core_patient(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5107 (class 2606 OID 16848)
-- Name: ihr_iot_wearables_vitalsigns ihr_iot_wearables_vi_device_id_1bbcae8c_fk_ihr_iot_w; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_iot_wearables_vitalsigns
    ADD CONSTRAINT ihr_iot_wearables_vi_device_id_1bbcae8c_fk_ihr_iot_w FOREIGN KEY (device_id) REFERENCES public.ihr_iot_wearables_device(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5108 (class 2606 OID 16853)
-- Name: ihr_iot_wearables_vitalsigns ihr_iot_wearables_vi_patient_id_2f7931a9_fk_core_pati; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.ihr_iot_wearables_vitalsigns
    ADD CONSTRAINT ihr_iot_wearables_vi_patient_id_2f7931a9_fk_core_pati FOREIGN KEY (patient_id) REFERENCES public.core_patient(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5109 (class 2606 OID 16868)
-- Name: mental_health_moodlog mental_health_moodlog_patient_id_dad90c43_fk_core_patient_id; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.mental_health_moodlog
    ADD CONSTRAINT mental_health_moodlog_patient_id_dad90c43_fk_core_patient_id FOREIGN KEY (patient_id) REFERENCES public.core_patient(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5110 (class 2606 OID 16880)
-- Name: nutrition_nutritionlog nutrition_nutritionlog_patient_id_7727de11_fk_core_patient_id; Type: FK CONSTRAINT; Schema: public; Owner: ihr_user
--

ALTER TABLE ONLY public.nutrition_nutritionlog
    ADD CONSTRAINT nutrition_nutritionlog_patient_id_7727de11_fk_core_patient_id FOREIGN KEY (patient_id) REFERENCES public.core_patient(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 5351 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA ihr; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA ihr TO ihr_user;


--
-- TOC entry 5352 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO ihr_user;


--
-- TOC entry 5353 (class 0 OID 0)
-- Dependencies: 225
-- Name: TABLE activity_data; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON TABLE ihr.activity_data TO ihr_user;


--
-- TOC entry 5355 (class 0 OID 0)
-- Dependencies: 224
-- Name: SEQUENCE activity_data_id_seq; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON SEQUENCE ihr.activity_data_id_seq TO ihr_user;


--
-- TOC entry 5356 (class 0 OID 0)
-- Dependencies: 237
-- Name: TABLE cannabinoid_effects; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON TABLE ihr.cannabinoid_effects TO ihr_user;


--
-- TOC entry 5358 (class 0 OID 0)
-- Dependencies: 236
-- Name: SEQUENCE cannabinoid_effects_id_seq; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON SEQUENCE ihr.cannabinoid_effects_id_seq TO ihr_user;


--
-- TOC entry 5359 (class 0 OID 0)
-- Dependencies: 231
-- Name: TABLE cannabinoid_medications; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON TABLE ihr.cannabinoid_medications TO ihr_user;


--
-- TOC entry 5361 (class 0 OID 0)
-- Dependencies: 230
-- Name: SEQUENCE cannabinoid_medications_id_seq; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON SEQUENCE ihr.cannabinoid_medications_id_seq TO ihr_user;


--
-- TOC entry 5362 (class 0 OID 0)
-- Dependencies: 239
-- Name: TABLE cannabinoid_side_effects; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON TABLE ihr.cannabinoid_side_effects TO ihr_user;


--
-- TOC entry 5364 (class 0 OID 0)
-- Dependencies: 238
-- Name: SEQUENCE cannabinoid_side_effects_id_seq; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON SEQUENCE ihr.cannabinoid_side_effects_id_seq TO ihr_user;


--
-- TOC entry 5365 (class 0 OID 0)
-- Dependencies: 235
-- Name: TABLE cannabinoid_usage_logs; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON TABLE ihr.cannabinoid_usage_logs TO ihr_user;


--
-- TOC entry 5367 (class 0 OID 0)
-- Dependencies: 234
-- Name: SEQUENCE cannabinoid_usage_logs_id_seq; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON SEQUENCE ihr.cannabinoid_usage_logs_id_seq TO ihr_user;


--
-- TOC entry 5368 (class 0 OID 0)
-- Dependencies: 229
-- Name: TABLE device_notifications; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON TABLE ihr.device_notifications TO ihr_user;


--
-- TOC entry 5370 (class 0 OID 0)
-- Dependencies: 228
-- Name: SEQUENCE device_notifications_id_seq; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON SEQUENCE ihr.device_notifications_id_seq TO ihr_user;


--
-- TOC entry 5371 (class 0 OID 0)
-- Dependencies: 221
-- Name: TABLE devices; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON TABLE ihr.devices TO ihr_user;


--
-- TOC entry 5373 (class 0 OID 0)
-- Dependencies: 220
-- Name: SEQUENCE devices_id_seq; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON SEQUENCE ihr.devices_id_seq TO ihr_user;


--
-- TOC entry 5374 (class 0 OID 0)
-- Dependencies: 219
-- Name: TABLE medications; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON TABLE ihr.medications TO ihr_user;


--
-- TOC entry 5376 (class 0 OID 0)
-- Dependencies: 233
-- Name: TABLE patient_cannabinoid_prescriptions; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON TABLE ihr.patient_cannabinoid_prescriptions TO ihr_user;


--
-- TOC entry 5378 (class 0 OID 0)
-- Dependencies: 232
-- Name: SEQUENCE patient_cannabinoid_prescriptions_id_seq; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON SEQUENCE ihr.patient_cannabinoid_prescriptions_id_seq TO ihr_user;


--
-- TOC entry 5379 (class 0 OID 0)
-- Dependencies: 217
-- Name: TABLE patients; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON TABLE ihr.patients TO ihr_user;


--
-- TOC entry 5381 (class 0 OID 0)
-- Dependencies: 227
-- Name: TABLE sleep_data; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON TABLE ihr.sleep_data TO ihr_user;


--
-- TOC entry 5383 (class 0 OID 0)
-- Dependencies: 226
-- Name: SEQUENCE sleep_data_id_seq; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON SEQUENCE ihr.sleep_data_id_seq TO ihr_user;


--
-- TOC entry 5384 (class 0 OID 0)
-- Dependencies: 223
-- Name: TABLE vital_signs; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON TABLE ihr.vital_signs TO ihr_user;


--
-- TOC entry 5386 (class 0 OID 0)
-- Dependencies: 222
-- Name: SEQUENCE vital_signs_id_seq; Type: ACL; Schema: ihr; Owner: postgres
--

GRANT ALL ON SEQUENCE ihr.vital_signs_id_seq TO ihr_user;


--
-- TOC entry 5387 (class 0 OID 0)
-- Dependencies: 280
-- Name: TABLE patients; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.patients TO ihr_user;


--
-- TOC entry 5389 (class 0 OID 0)
-- Dependencies: 282
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.users TO ihr_user;


--
-- TOC entry 2239 (class 826 OID 16423)
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: ihr; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA ihr GRANT ALL ON SEQUENCES TO ihr_user;


--
-- TOC entry 2238 (class 826 OID 16422)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: ihr; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA ihr GRANT ALL ON TABLES TO ihr_user;


--
-- TOC entry 2240 (class 826 OID 16610)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO ihr_user;


-- Completed on 2025-07-04 07:43:44

--
-- PostgreSQL database dump complete
--

