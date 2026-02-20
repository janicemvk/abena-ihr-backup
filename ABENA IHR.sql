--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.9

-- Started on 2025-07-04 07:36:58

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 228 (class 1259 OID 26922)
-- Name: alert_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alert_log (
    id integer NOT NULL,
    alert_type character varying(50) NOT NULL,
    severity character varying(20) NOT NULL,
    source character varying(100) NOT NULL,
    message text NOT NULL,
    "timestamp" timestamp without time zone,
    resolved boolean,
    resolved_at timestamp without time zone,
    resolution_notes text
);


ALTER TABLE public.alert_log OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 26921)
-- Name: alert_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.alert_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.alert_log_id_seq OWNER TO postgres;

--
-- TOC entry 4923 (class 0 OID 0)
-- Dependencies: 227
-- Name: alert_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.alert_log_id_seq OWNED BY public.alert_log.id;


--
-- TOC entry 220 (class 1259 OID 26256)
-- Name: data_mapping_configs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_mapping_configs (
    id integer NOT NULL,
    source_system character varying(100) NOT NULL,
    target_system character varying(100) NOT NULL,
    mapping_version character varying(20) NOT NULL,
    mapping_config text NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_active integer
);


ALTER TABLE public.data_mapping_configs OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 26255)
-- Name: data_mapping_configs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.data_mapping_configs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.data_mapping_configs_id_seq OWNER TO postgres;

--
-- TOC entry 4926 (class 0 OID 0)
-- Dependencies: 219
-- Name: data_mapping_configs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.data_mapping_configs_id_seq OWNED BY public.data_mapping_configs.id;


--
-- TOC entry 224 (class 1259 OID 26906)
-- Name: data_quality_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_quality_metrics (
    id integer NOT NULL,
    source_system character varying(100) NOT NULL,
    data_type character varying(50) NOT NULL,
    "timestamp" timestamp without time zone,
    total_records integer,
    valid_records integer,
    completeness_score double precision,
    accuracy_score double precision,
    consistency_score double precision,
    timeliness_score double precision,
    quality_issues json
);


ALTER TABLE public.data_quality_metrics OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 26905)
-- Name: data_quality_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.data_quality_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.data_quality_metrics_id_seq OWNER TO postgres;

--
-- TOC entry 4929 (class 0 OID 0)
-- Dependencies: 223
-- Name: data_quality_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.data_quality_metrics_id_seq OWNED BY public.data_quality_metrics.id;


--
-- TOC entry 222 (class 1259 OID 26897)
-- Name: integration_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.integration_metrics (
    id integer NOT NULL,
    source_system character varying(100) NOT NULL,
    endpoint character varying(200) NOT NULL,
    "timestamp" timestamp without time zone,
    response_time double precision,
    status_code integer,
    success boolean,
    error_message text,
    request_size integer,
    response_size integer,
    records_processed integer
);


ALTER TABLE public.integration_metrics OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 26896)
-- Name: integration_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.integration_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.integration_metrics_id_seq OWNER TO postgres;

--
-- TOC entry 4932 (class 0 OID 0)
-- Dependencies: 221
-- Name: integration_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.integration_metrics_id_seq OWNED BY public.integration_metrics.id;


--
-- TOC entry 215 (class 1259 OID 25204)
-- Name: patients; Type: TABLE; Schema: public; Owner: abena_user
--

CREATE TABLE public.patients (
    patient_id character varying(50) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    age integer NOT NULL,
    gender character varying(20) NOT NULL,
    medical_history text[] DEFAULT '{}'::text[],
    current_medications text[] DEFAULT '{}'::text[],
    pain_scores real[] DEFAULT '{}'::real[],
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT patients_age_check CHECK (((age >= 0) AND (age <= 120)))
);


ALTER TABLE public.patients OWNER TO abena_user;

--
-- TOC entry 218 (class 1259 OID 25232)
-- Name: predictions; Type: TABLE; Schema: public; Owner: abena_user
--

CREATE TABLE public.predictions (
    prediction_id integer NOT NULL,
    patient_id character varying(50),
    treatment_id character varying(50),
    success_probability real NOT NULL,
    risk_score real NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT predictions_risk_score_check CHECK (((risk_score >= (0)::double precision) AND (risk_score <= (1)::double precision))),
    CONSTRAINT predictions_success_probability_check CHECK (((success_probability >= (0)::double precision) AND (success_probability <= (1)::double precision)))
);


ALTER TABLE public.predictions OWNER TO abena_user;

--
-- TOC entry 217 (class 1259 OID 25231)
-- Name: predictions_prediction_id_seq; Type: SEQUENCE; Schema: public; Owner: abena_user
--

CREATE SEQUENCE public.predictions_prediction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.predictions_prediction_id_seq OWNER TO abena_user;

--
-- TOC entry 4934 (class 0 OID 0)
-- Dependencies: 217
-- Name: predictions_prediction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: abena_user
--

ALTER SEQUENCE public.predictions_prediction_id_seq OWNED BY public.predictions.prediction_id;


--
-- TOC entry 226 (class 1259 OID 26915)
-- Name: system_health; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_health (
    id integer NOT NULL,
    component character varying(100) NOT NULL,
    "timestamp" timestamp without time zone,
    cpu_usage double precision,
    memory_usage double precision,
    disk_usage double precision,
    network_io double precision,
    is_healthy boolean,
    health_score double precision
);


ALTER TABLE public.system_health OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 26914)
-- Name: system_health_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_health_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_health_id_seq OWNER TO postgres;

--
-- TOC entry 4936 (class 0 OID 0)
-- Dependencies: 225
-- Name: system_health_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_health_id_seq OWNED BY public.system_health.id;


--
-- TOC entry 216 (class 1259 OID 25216)
-- Name: treatment_plans; Type: TABLE; Schema: public; Owner: abena_user
--

CREATE TABLE public.treatment_plans (
    treatment_id character varying(50) NOT NULL,
    patient_id character varying(50),
    treatment_type character varying(50) NOT NULL,
    medications text[] DEFAULT '{}'::text[],
    duration_weeks integer NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT treatment_plans_duration_weeks_check CHECK ((duration_weeks > 0))
);


ALTER TABLE public.treatment_plans OWNER TO abena_user;

--
-- TOC entry 4735 (class 2604 OID 26925)
-- Name: alert_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alert_log ALTER COLUMN id SET DEFAULT nextval('public.alert_log_id_seq'::regclass);


--
-- TOC entry 4731 (class 2604 OID 26259)
-- Name: data_mapping_configs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_mapping_configs ALTER COLUMN id SET DEFAULT nextval('public.data_mapping_configs_id_seq'::regclass);


--
-- TOC entry 4733 (class 2604 OID 26909)
-- Name: data_quality_metrics id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_quality_metrics ALTER COLUMN id SET DEFAULT nextval('public.data_quality_metrics_id_seq'::regclass);


--
-- TOC entry 4732 (class 2604 OID 26900)
-- Name: integration_metrics id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.integration_metrics ALTER COLUMN id SET DEFAULT nextval('public.integration_metrics_id_seq'::regclass);


--
-- TOC entry 4729 (class 2604 OID 25235)
-- Name: predictions prediction_id; Type: DEFAULT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.predictions ALTER COLUMN prediction_id SET DEFAULT nextval('public.predictions_prediction_id_seq'::regclass);


--
-- TOC entry 4734 (class 2604 OID 26918)
-- Name: system_health id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_health ALTER COLUMN id SET DEFAULT nextval('public.system_health_id_seq'::regclass);


--
-- TOC entry 4915 (class 0 OID 26922)
-- Dependencies: 228
-- Data for Name: alert_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alert_log (id, alert_type, severity, source, message, "timestamp", resolved, resolved_at, resolution_notes) FROM stdin;
\.


--
-- TOC entry 4907 (class 0 OID 26256)
-- Dependencies: 220
-- Data for Name: data_mapping_configs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_mapping_configs (id, source_system, target_system, mapping_version, mapping_config, created_at, updated_at, is_active) FROM stdin;
1	CustomEMR	FHIR	1.0	{"patient_mappings": {"PATIENT_ID": "mrn", "GIVEN_NAME": "first_name", "FAMILY_NAME": "last_name", "SEX": "gender", "DOB": "birth_date", "EMAIL": "email", "PHONE": "phone"}, "observation_mappings": {"PATIENT_ID": "patient_id", "OBS_TYPE": "type", "OBS_VALUE": "value", "OBS_UNIT": "unit", "OBS_TIMESTAMP": "timestamp", "SOURCE_SYS": "source_system"}}	2025-06-16 18:44:16.177697	2025-06-16 18:44:16.177703	1
2	CustomEMR	FHIR	1.0	{"patient_mappings": {"PATIENT_ID": "mrn", "GIVEN_NAME": "first_name", "FAMILY_NAME": "last_name", "SEX": "gender", "DOB": "birth_date", "EMAIL": "email", "PHONE": "phone"}, "observation_mappings": {"PATIENT_ID": "patient_id", "OBS_TYPE": "type", "OBS_VALUE": "value", "OBS_UNIT": "unit", "OBS_TIMESTAMP": "timestamp", "SOURCE_SYS": "source_system"}}	2025-06-16 18:48:37.301967	2025-06-16 18:48:37.301973	1
\.


--
-- TOC entry 4911 (class 0 OID 26906)
-- Dependencies: 224
-- Data for Name: data_quality_metrics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_quality_metrics (id, source_system, data_type, "timestamp", total_records, valid_records, completeness_score, accuracy_score, consistency_score, timeliness_score, quality_issues) FROM stdin;
\.


--
-- TOC entry 4909 (class 0 OID 26897)
-- Dependencies: 222
-- Data for Name: integration_metrics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.integration_metrics (id, source_system, endpoint, "timestamp", response_time, status_code, success, error_message, request_size, response_size, records_processed) FROM stdin;
\.


--
-- TOC entry 4902 (class 0 OID 25204)
-- Dependencies: 215
-- Data for Name: patients; Type: TABLE DATA; Schema: public; Owner: abena_user
--

COPY public.patients (patient_id, first_name, last_name, age, gender, medical_history, current_medications, pain_scores, created_at) FROM stdin;
PATIENT_001	Jennifer	Jones	67	male	{fibromyalgia,hypertension,chronic_pain}	{ibuprofen,pregabalin,gabapentin,acetaminophen}	{7.8,3.7,6.8,5.8,5.4,5.1}	2025-06-04 11:29:26.047443
PATIENT_002	Patricia	Smith	41	female	{fibromyalgia}	{}	{5.5,8.5,4.7,6.9,8.7,7,8.3}	2025-06-04 11:29:26.047443
PATIENT_003	John	Brown	47	female	{fibromyalgia,diabetes}	{ibuprofen,pregabalin,gabapentin}	{7.7,4,8.6,8.4,5.4}	2025-06-04 11:29:26.047443
PATIENT_004	James	Jones	42	female	{chronic_pain,hypertension,diabetes}	{ibuprofen,acetaminophen,pregabalin}	{5.6,3.3,7.9,3.5}	2025-06-04 11:29:26.047443
PATIENT_005	Patricia	Johnson	48	female	{hypertension,chronic_pain}	{pregabalin}	{5.9,7,8.8,7.3}	2025-06-04 11:29:26.047443
PATIENT_006	Mary	Davis	32	female	{fibromyalgia,diabetes,hypertension}	{ibuprofen,gabapentin}	{4.5,3.8,6.9,7.6,6.4,7.8}	2025-06-04 11:29:26.047443
PATIENT_007	Jennifer	Jones	26	female	{chronic_pain,arthritis,fibromyalgia}	{}	{8.7,7.8,5.8,3.1,8.5,6.9}	2025-06-04 11:29:26.047443
PATIENT_008	Mary	Davis	53	female	{arthritis,hypertension,diabetes}	{gabapentin}	{5.8,6.6,4.8,4.7,4.3}	2025-06-04 11:29:26.047443
PATIENT_009	Linda	Jones	42	female	{fibromyalgia,hypertension,diabetes}	{acetaminophen,gabapentin,pregabalin}	{6.3,4.2,9,5.8,7.4,5.4}	2025-06-04 11:29:26.047443
PATIENT_010	Patricia	Jones	74	male	{fibromyalgia,arthritis,diabetes}	{acetaminophen,pregabalin,ibuprofen,gabapentin}	{3.3,8.7,8,3.7,3.5}	2025-06-04 11:29:26.047443
PATIENT_011	Michael	Williams	39	female	{arthritis}	{pregabalin,acetaminophen}	{5.9,4.8,3.8,3.2,8.7,6.4,7.9}	2025-06-04 11:29:26.047443
PATIENT_012	Jennifer	Garcia	41	female	{hypertension,diabetes}	{}	{8,5,8.2,7.8,5.1,3.6}	2025-06-04 11:29:26.047443
PATIENT_013	Robert	Williams	27	male	{diabetes,hypertension,chronic_pain}	{pregabalin,tramadol,acetaminophen,gabapentin}	{5.4,3.5,5.7,4.9,6.4,3.3}	2025-06-04 11:29:26.047443
PATIENT_014	James	Miller	41	female	{chronic_pain,hypertension}	{gabapentin,tramadol}	{4.5,5.6,8.3}	2025-06-04 11:29:26.047443
PATIENT_015	Jennifer	Jones	63	male	{diabetes,fibromyalgia}	{gabapentin,tramadol,acetaminophen}	{8.6,8.9,6.3,3.9,3.7,6.1}	2025-06-04 11:29:26.047443
PATIENT_016	Mary	Davis	37	female	{diabetes,chronic_pain}	{pregabalin,gabapentin}	{8,6.1,8.1,4.1,7.6,4.9,4.5,6.3}	2025-06-04 11:29:26.047443
PATIENT_017	Robert	Brown	72	female	{arthritis,hypertension,fibromyalgia}	{pregabalin,tramadol,ibuprofen,gabapentin}	{7.2,7.2,8.2,8.1,6.6}	2025-06-04 11:29:26.047443
PATIENT_018	John	Jones	74	female	{fibromyalgia,arthritis}	{acetaminophen}	{5.2,6.8,7.4,7.3,4.4,6.5,6.7}	2025-06-04 11:29:26.047443
PATIENT_019	Jennifer	Miller	66	female	{diabetes,hypertension}	{ibuprofen,gabapentin,tramadol,pregabalin}	{4.5,3.6,8.8,5.3,8.6}	2025-06-04 11:29:26.047443
PATIENT_020	Michael	Jones	28	female	{arthritis,chronic_pain}	{pregabalin,ibuprofen,gabapentin}	{6.9,9,6.5}	2025-06-04 11:29:26.047443
PATIENT_021	Mary	Garcia	72	male	{fibromyalgia,chronic_pain}	{gabapentin,acetaminophen,tramadol,pregabalin}	{4.3,3.1,8.7,7.2,6.7}	2025-06-04 11:29:26.047443
PATIENT_022	Michael	Garcia	29	female	{diabetes,hypertension,chronic_pain}	{tramadol,pregabalin,acetaminophen}	{7.1,5.1,5.7,4.7,5,5.7,9}	2025-06-04 11:29:26.047443
PATIENT_023	Robert	Johnson	51	female	{hypertension,fibromyalgia,arthritis}	{gabapentin,pregabalin,acetaminophen,ibuprofen}	{6.8,8.5,7.7,3.7,4.7,3.9,4.1}	2025-06-04 11:29:26.047443
PATIENT_024	Mary	Smith	27	female	{diabetes}	{ibuprofen,acetaminophen,gabapentin,tramadol}	{8.8,5.5,8.4,3,3.6,3.8}	2025-06-04 11:29:26.047443
PATIENT_025	Patricia	Williams	46	female	{arthritis,chronic_pain,hypertension}	{}	{4.6,3.6,6.4}	2025-06-04 11:29:26.047443
\.


--
-- TOC entry 4905 (class 0 OID 25232)
-- Dependencies: 218
-- Data for Name: predictions; Type: TABLE DATA; Schema: public; Owner: abena_user
--

COPY public.predictions (prediction_id, patient_id, treatment_id, success_probability, risk_score, created_at) FROM stdin;
1	PATIENT_001	TX_001_01	0.34736553	0.6526345	2025-06-04 11:29:26.047443
2	PATIENT_001	TX_001_02	0.3625632	0.6374368	2025-06-04 11:29:26.047443
3	PATIENT_001	TX_001_03	0.8593381	0.14066193	2025-06-04 11:29:26.047443
4	PATIENT_002	TX_002_01	0.83802116	0.16197884	2025-06-04 11:29:26.047443
5	PATIENT_003	TX_003_01	0.62665224	0.37334776	2025-06-04 11:29:26.047443
6	PATIENT_003	TX_003_02	0.8619754	0.13802461	2025-06-04 11:29:26.047443
7	PATIENT_003	TX_003_03	0.6209133	0.37908664	2025-06-04 11:29:26.047443
8	PATIENT_004	TX_004_01	0.6464135	0.3535865	2025-06-04 11:29:26.047443
9	PATIENT_004	TX_004_02	0.31691232	0.68308765	2025-06-04 11:29:26.047443
10	PATIENT_005	TX_005_01	0.30434635	0.6956537	2025-06-04 11:29:26.047443
11	PATIENT_005	TX_005_02	0.66190726	0.3380927	2025-06-04 11:29:26.047443
12	PATIENT_006	TX_006_01	0.66543436	0.33456564	2025-06-04 11:29:26.047443
13	PATIENT_007	TX_007_01	0.5243721	0.4756279	2025-06-04 11:29:26.047443
14	PATIENT_007	TX_007_02	0.49238026	0.50761974	2025-06-04 11:29:26.047443
15	PATIENT_007	TX_007_03	0.7182702	0.2817298	2025-06-04 11:29:26.047443
16	PATIENT_008	TX_008_01	0.77843684	0.22156315	2025-06-04 11:29:26.047443
17	PATIENT_008	TX_008_02	0.42812464	0.5718754	2025-06-04 11:29:26.047443
18	PATIENT_008	TX_008_03	0.7169115	0.28308848	2025-06-04 11:29:26.047443
19	PATIENT_009	TX_009_01	0.6266801	0.37331992	2025-06-04 11:29:26.047443
20	PATIENT_010	TX_010_01	0.6041402	0.39585978	2025-06-04 11:29:26.047443
21	PATIENT_011	TX_011_01	0.72207433	0.27792567	2025-06-04 11:29:26.047443
22	PATIENT_012	TX_012_01	0.65946174	0.34053826	2025-06-04 11:29:26.047443
23	PATIENT_012	TX_012_02	0.7268289	0.27317116	2025-06-04 11:29:26.047443
24	PATIENT_012	TX_012_03	0.71159446	0.28840554	2025-06-04 11:29:26.047443
25	PATIENT_013	TX_013_01	0.47212368	0.5278763	2025-06-04 11:29:26.047443
26	PATIENT_014	TX_014_01	0.74820656	0.25179347	2025-06-04 11:29:26.047443
27	PATIENT_014	TX_014_02	0.7712038	0.22879621	2025-06-04 11:29:26.047443
28	PATIENT_015	TX_015_01	0.86131465	0.13868535	2025-06-04 11:29:26.047443
29	PATIENT_015	TX_015_02	0.35621175	0.6437882	2025-06-04 11:29:26.047443
30	PATIENT_015	TX_015_03	0.5041776	0.49582243	2025-06-04 11:29:26.047443
31	PATIENT_016	TX_016_01	0.4078361	0.5921639	2025-06-04 11:29:26.047443
32	PATIENT_016	TX_016_02	0.7987482	0.2012518	2025-06-04 11:29:26.047443
33	PATIENT_016	TX_016_03	0.8324056	0.16759437	2025-06-04 11:29:26.047443
34	PATIENT_017	TX_017_01	0.5297708	0.4702292	2025-06-04 11:29:26.047443
35	PATIENT_018	TX_018_01	0.70972747	0.29027256	2025-06-04 11:29:26.047443
36	PATIENT_019	TX_019_01	0.43608966	0.5639103	2025-06-04 11:29:26.047443
37	PATIENT_020	TX_020_01	0.8167232	0.1832768	2025-06-04 11:29:26.047443
38	PATIENT_020	TX_020_02	0.4104623	0.58953774	2025-06-04 11:29:26.047443
39	PATIENT_020	TX_020_03	0.8267483	0.1732517	2025-06-04 11:29:26.047443
40	PATIENT_021	TX_021_01	0.7276081	0.27239192	2025-06-04 11:29:26.047443
41	PATIENT_022	TX_022_01	0.627179	0.372821	2025-06-04 11:29:26.047443
42	PATIENT_023	TX_023_01	0.6266699	0.37333012	2025-06-04 11:29:26.047443
43	PATIENT_023	TX_023_02	0.6483632	0.35163683	2025-06-04 11:29:26.047443
44	PATIENT_023	TX_023_03	0.56991875	0.43008125	2025-06-04 11:29:26.047443
45	PATIENT_024	TX_024_01	0.44577354	0.55422646	2025-06-04 11:29:26.047443
46	PATIENT_024	TX_024_02	0.496404	0.503596	2025-06-04 11:29:26.047443
47	PATIENT_025	TX_025_01	0.7123232	0.28767684	2025-06-04 11:29:26.047443
48	PATIENT_025	TX_025_02	0.8618241	0.13817587	2025-06-04 11:29:26.047443
49	PATIENT_025	TX_025_03	0.7530066	0.24699345	2025-06-04 11:29:26.047443
\.


--
-- TOC entry 4913 (class 0 OID 26915)
-- Dependencies: 226
-- Data for Name: system_health; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_health (id, component, "timestamp", cpu_usage, memory_usage, disk_usage, network_io, is_healthy, health_score) FROM stdin;
\.


--
-- TOC entry 4903 (class 0 OID 25216)
-- Dependencies: 216
-- Data for Name: treatment_plans; Type: TABLE DATA; Schema: public; Owner: abena_user
--

COPY public.treatment_plans (treatment_id, patient_id, treatment_type, medications, duration_weeks, notes, created_at) FROM stdin;
TX_001_01	PATIENT_001	behavioral	{gabapentin,acetaminophen}	16	Treatment plan for behavioral approach	2025-06-04 11:29:26.047443
TX_001_02	PATIENT_001	combined	{acetaminophen,ibuprofen}	14	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_001_03	PATIENT_001	combined	{ibuprofen,acetaminophen,pregabalin}	8	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_002_01	PATIENT_002	combined	{tramadol,ibuprofen,gabapentin}	17	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_003_01	PATIENT_003	interventional	{pregabalin,acetaminophen}	19	Treatment plan for interventional approach	2025-06-04 11:29:26.047443
TX_003_02	PATIENT_003	interventional	{pregabalin,tramadol}	20	Treatment plan for interventional approach	2025-06-04 11:29:26.047443
TX_003_03	PATIENT_003	behavioral	{acetaminophen,tramadol,gabapentin}	4	Treatment plan for behavioral approach	2025-06-04 11:29:26.047443
TX_004_01	PATIENT_004	behavioral	{tramadol,ibuprofen,acetaminophen}	11	Treatment plan for behavioral approach	2025-06-04 11:29:26.047443
TX_004_02	PATIENT_004	combined	{ibuprofen,gabapentin,acetaminophen}	6	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_005_01	PATIENT_005	interventional	{ibuprofen,acetaminophen}	14	Treatment plan for interventional approach	2025-06-04 11:29:26.047443
TX_005_02	PATIENT_005	interventional	{gabapentin,tramadol,ibuprofen}	7	Treatment plan for interventional approach	2025-06-04 11:29:26.047443
TX_006_01	PATIENT_006	pharmacological	{gabapentin}	10	Treatment plan for pharmacological approach	2025-06-04 11:29:26.047443
TX_007_01	PATIENT_007	combined	{ibuprofen,acetaminophen}	11	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_007_02	PATIENT_007	combined	{pregabalin}	20	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_007_03	PATIENT_007	pharmacological	{ibuprofen,acetaminophen}	16	Treatment plan for pharmacological approach	2025-06-04 11:29:26.047443
TX_008_01	PATIENT_008	combined	{tramadol,pregabalin}	18	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_008_02	PATIENT_008	combined	{tramadol,gabapentin}	18	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_008_03	PATIENT_008	interventional	{pregabalin,ibuprofen}	9	Treatment plan for interventional approach	2025-06-04 11:29:26.047443
TX_009_01	PATIENT_009	combined	{ibuprofen,acetaminophen,pregabalin}	6	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_010_01	PATIENT_010	combined	{acetaminophen,gabapentin}	11	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_011_01	PATIENT_011	behavioral	{ibuprofen}	14	Treatment plan for behavioral approach	2025-06-04 11:29:26.047443
TX_012_01	PATIENT_012	interventional	{pregabalin,tramadol}	8	Treatment plan for interventional approach	2025-06-04 11:29:26.047443
TX_012_02	PATIENT_012	pharmacological	{acetaminophen,gabapentin}	15	Treatment plan for pharmacological approach	2025-06-04 11:29:26.047443
TX_012_03	PATIENT_012	pharmacological	{pregabalin,tramadol}	9	Treatment plan for pharmacological approach	2025-06-04 11:29:26.047443
TX_013_01	PATIENT_013	pharmacological	{ibuprofen}	10	Treatment plan for pharmacological approach	2025-06-04 11:29:26.047443
TX_014_01	PATIENT_014	pharmacological	{tramadol}	11	Treatment plan for pharmacological approach	2025-06-04 11:29:26.047443
TX_014_02	PATIENT_014	combined	{tramadol,acetaminophen}	9	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_015_01	PATIENT_015	interventional	{gabapentin,tramadol,pregabalin}	18	Treatment plan for interventional approach	2025-06-04 11:29:26.047443
TX_015_02	PATIENT_015	interventional	{pregabalin,ibuprofen}	7	Treatment plan for interventional approach	2025-06-04 11:29:26.047443
TX_015_03	PATIENT_015	interventional	{pregabalin,tramadol,ibuprofen}	7	Treatment plan for interventional approach	2025-06-04 11:29:26.047443
TX_016_01	PATIENT_016	pharmacological	{acetaminophen}	18	Treatment plan for pharmacological approach	2025-06-04 11:29:26.047443
TX_016_02	PATIENT_016	combined	{pregabalin}	19	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_016_03	PATIENT_016	combined	{gabapentin}	17	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_017_01	PATIENT_017	interventional	{ibuprofen,pregabalin}	5	Treatment plan for interventional approach	2025-06-04 11:29:26.047443
TX_018_01	PATIENT_018	behavioral	{acetaminophen,ibuprofen}	18	Treatment plan for behavioral approach	2025-06-04 11:29:26.047443
TX_019_01	PATIENT_019	pharmacological	{tramadol,pregabalin,ibuprofen}	17	Treatment plan for pharmacological approach	2025-06-04 11:29:26.047443
TX_020_01	PATIENT_020	combined	{ibuprofen,tramadol,gabapentin}	16	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_020_02	PATIENT_020	interventional	{ibuprofen,pregabalin}	13	Treatment plan for interventional approach	2025-06-04 11:29:26.047443
TX_020_03	PATIENT_020	behavioral	{gabapentin,tramadol,acetaminophen}	10	Treatment plan for behavioral approach	2025-06-04 11:29:26.047443
TX_021_01	PATIENT_021	behavioral	{acetaminophen}	13	Treatment plan for behavioral approach	2025-06-04 11:29:26.047443
TX_022_01	PATIENT_022	pharmacological	{pregabalin,tramadol}	4	Treatment plan for pharmacological approach	2025-06-04 11:29:26.047443
TX_023_01	PATIENT_023	interventional	{ibuprofen,tramadol,pregabalin}	19	Treatment plan for interventional approach	2025-06-04 11:29:26.047443
TX_023_02	PATIENT_023	combined	{gabapentin,acetaminophen,ibuprofen}	18	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_023_03	PATIENT_023	behavioral	{gabapentin,acetaminophen,ibuprofen}	14	Treatment plan for behavioral approach	2025-06-04 11:29:26.047443
TX_024_01	PATIENT_024	pharmacological	{pregabalin,ibuprofen}	6	Treatment plan for pharmacological approach	2025-06-04 11:29:26.047443
TX_024_02	PATIENT_024	behavioral	{ibuprofen,pregabalin}	20	Treatment plan for behavioral approach	2025-06-04 11:29:26.047443
TX_025_01	PATIENT_025	combined	{tramadol}	8	Treatment plan for combined approach	2025-06-04 11:29:26.047443
TX_025_02	PATIENT_025	behavioral	{gabapentin}	17	Treatment plan for behavioral approach	2025-06-04 11:29:26.047443
TX_025_03	PATIENT_025	combined	{tramadol,acetaminophen}	14	Treatment plan for combined approach	2025-06-04 11:29:26.047443
\.


--
-- TOC entry 4938 (class 0 OID 0)
-- Dependencies: 227
-- Name: alert_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.alert_log_id_seq', 1, false);


--
-- TOC entry 4939 (class 0 OID 0)
-- Dependencies: 219
-- Name: data_mapping_configs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.data_mapping_configs_id_seq', 2, true);


--
-- TOC entry 4940 (class 0 OID 0)
-- Dependencies: 223
-- Name: data_quality_metrics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.data_quality_metrics_id_seq', 1, false);


--
-- TOC entry 4941 (class 0 OID 0)
-- Dependencies: 221
-- Name: integration_metrics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.integration_metrics_id_seq', 1, false);


--
-- TOC entry 4942 (class 0 OID 0)
-- Dependencies: 217
-- Name: predictions_prediction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: abena_user
--

SELECT pg_catalog.setval('public.predictions_prediction_id_seq', 49, true);


--
-- TOC entry 4943 (class 0 OID 0)
-- Dependencies: 225
-- Name: system_health_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_health_id_seq', 1, false);


--
-- TOC entry 4755 (class 2606 OID 26929)
-- Name: alert_log alert_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alert_log
    ADD CONSTRAINT alert_log_pkey PRIMARY KEY (id);


--
-- TOC entry 4747 (class 2606 OID 26263)
-- Name: data_mapping_configs data_mapping_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_mapping_configs
    ADD CONSTRAINT data_mapping_configs_pkey PRIMARY KEY (id);


--
-- TOC entry 4751 (class 2606 OID 26913)
-- Name: data_quality_metrics data_quality_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_quality_metrics
    ADD CONSTRAINT data_quality_metrics_pkey PRIMARY KEY (id);


--
-- TOC entry 4749 (class 2606 OID 26904)
-- Name: integration_metrics integration_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.integration_metrics
    ADD CONSTRAINT integration_metrics_pkey PRIMARY KEY (id);


--
-- TOC entry 4741 (class 2606 OID 25215)
-- Name: patients patients_pkey; Type: CONSTRAINT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_pkey PRIMARY KEY (patient_id);


--
-- TOC entry 4745 (class 2606 OID 25240)
-- Name: predictions predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.predictions
    ADD CONSTRAINT predictions_pkey PRIMARY KEY (prediction_id);


--
-- TOC entry 4753 (class 2606 OID 26920)
-- Name: system_health system_health_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_health
    ADD CONSTRAINT system_health_pkey PRIMARY KEY (id);


--
-- TOC entry 4743 (class 2606 OID 25225)
-- Name: treatment_plans treatment_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.treatment_plans
    ADD CONSTRAINT treatment_plans_pkey PRIMARY KEY (treatment_id);


--
-- TOC entry 4757 (class 2606 OID 25241)
-- Name: predictions predictions_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.predictions
    ADD CONSTRAINT predictions_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(patient_id);


--
-- TOC entry 4758 (class 2606 OID 25246)
-- Name: predictions predictions_treatment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.predictions
    ADD CONSTRAINT predictions_treatment_id_fkey FOREIGN KEY (treatment_id) REFERENCES public.treatment_plans(treatment_id);


--
-- TOC entry 4756 (class 2606 OID 25226)
-- Name: treatment_plans treatment_plans_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.treatment_plans
    ADD CONSTRAINT treatment_plans_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(patient_id);


--
-- TOC entry 4921 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO abena_user;


--
-- TOC entry 4922 (class 0 OID 0)
-- Dependencies: 228
-- Name: TABLE alert_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.alert_log TO abena_user;


--
-- TOC entry 4924 (class 0 OID 0)
-- Dependencies: 227
-- Name: SEQUENCE alert_log_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.alert_log_id_seq TO abena_user;


--
-- TOC entry 4925 (class 0 OID 0)
-- Dependencies: 220
-- Name: TABLE data_mapping_configs; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.data_mapping_configs TO abena_user;


--
-- TOC entry 4927 (class 0 OID 0)
-- Dependencies: 219
-- Name: SEQUENCE data_mapping_configs_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.data_mapping_configs_id_seq TO abena_user;


--
-- TOC entry 4928 (class 0 OID 0)
-- Dependencies: 224
-- Name: TABLE data_quality_metrics; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.data_quality_metrics TO abena_user;


--
-- TOC entry 4930 (class 0 OID 0)
-- Dependencies: 223
-- Name: SEQUENCE data_quality_metrics_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.data_quality_metrics_id_seq TO abena_user;


--
-- TOC entry 4931 (class 0 OID 0)
-- Dependencies: 222
-- Name: TABLE integration_metrics; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.integration_metrics TO abena_user;


--
-- TOC entry 4933 (class 0 OID 0)
-- Dependencies: 221
-- Name: SEQUENCE integration_metrics_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.integration_metrics_id_seq TO abena_user;


--
-- TOC entry 4935 (class 0 OID 0)
-- Dependencies: 226
-- Name: TABLE system_health; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.system_health TO abena_user;


--
-- TOC entry 4937 (class 0 OID 0)
-- Dependencies: 225
-- Name: SEQUENCE system_health_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.system_health_id_seq TO abena_user;


--
-- TOC entry 2072 (class 826 OID 25203)
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO abena_user;


--
-- TOC entry 2071 (class 826 OID 25202)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO abena_user;


-- Completed on 2025-07-04 07:36:58

--
-- PostgreSQL database dump complete
--

