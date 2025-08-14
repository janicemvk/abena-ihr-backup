--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.9

-- Started on 2025-07-04 07:27:56

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
-- TOC entry 3 (class 3079 OID 25866)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 5110 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- TOC entry 2 (class 3079 OID 25855)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 5111 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 277 (class 1255 OID 26060)
-- Name: calculate_voting_power(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.calculate_voting_power() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    total_stake DECIMAL(36, 18);
BEGIN
    SELECT SUM(stake_amount + total_delegated_stake) INTO total_stake FROM validator_nodes WHERE status = 'active';
    
    IF total_stake > 0 THEN
        NEW.voting_power = (NEW.stake_amount + NEW.total_delegated_stake) / total_stake;
    ELSE
        NEW.voting_power = 0;
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.calculate_voting_power() OWNER TO postgres;

--
-- TOC entry 283 (class 1255 OID 26112)
-- Name: notify_critical_triage(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.notify_critical_triage() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- If this is a critical classification, create an alert
    IF NEW.classification_level = 'CRITICAL' THEN
        INSERT INTO system_alerts (
            alert_type, severity, message, metadata, created_at
        ) VALUES (
            'CRITICAL_TRIAGE',
            'HIGH',
            'Critical medical data detected requiring immediate attention',
            jsonb_build_object(
                'triage_id', NEW.triage_id,
                'patient_id', NEW.patient_id,
                'priority_score', NEW.priority_score,
                'data_type', NEW.data_type
            ),
            CURRENT_TIMESTAMP
        );
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.notify_critical_triage() OWNER TO postgres;

--
-- TOC entry 278 (class 1255 OID 26110)
-- Name: update_triage_timestamp(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_triage_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_triage_timestamp() OWNER TO postgres;

--
-- TOC entry 276 (class 1255 OID 26056)
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
-- TOC entry 221 (class 1259 OID 26013)
-- Name: blockchain_blocks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.blockchain_blocks (
    block_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    block_number bigint NOT NULL,
    block_hash character varying(64) NOT NULL,
    parent_hash character varying(64) NOT NULL,
    merkle_root character varying(64) NOT NULL,
    state_root character varying(64) NOT NULL,
    receipts_root character varying(64) NOT NULL,
    miner_address character varying(42) NOT NULL,
    difficulty numeric(78,0) DEFAULT 0,
    total_difficulty numeric(78,0) DEFAULT 0,
    gas_limit bigint NOT NULL,
    gas_used bigint NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    extra_data text,
    transaction_count integer DEFAULT 0,
    uncle_count integer DEFAULT 0,
    size_bytes integer,
    block_reward numeric(36,18) DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.blockchain_blocks OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 25903)
-- Name: blockchain_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.blockchain_transactions (
    transaction_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    block_hash character varying(64) NOT NULL,
    block_number bigint NOT NULL,
    transaction_hash character varying(64) NOT NULL,
    transaction_index integer NOT NULL,
    from_address character varying(42) NOT NULL,
    to_address character varying(42),
    value numeric(36,18) DEFAULT 0,
    gas_used bigint NOT NULL,
    gas_price bigint NOT NULL,
    transaction_fee numeric(36,18) NOT NULL,
    nonce bigint NOT NULL,
    transaction_type character varying(20) NOT NULL,
    status character varying(10) NOT NULL,
    input_data text,
    output_data text,
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    confirmation_count integer DEFAULT 0,
    medical_record_id uuid,
    patient_id uuid,
    provider_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT blockchain_transactions_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'confirmed'::character varying, 'failed'::character varying])::text[]))),
    CONSTRAINT blockchain_transactions_transaction_type_check CHECK (((transaction_type)::text = ANY ((ARRAY['transfer'::character varying, 'contract_call'::character varying, 'contract_deploy'::character varying, 'medical_record'::character varying, 'consent'::character varying, 'insurance_claim'::character varying])::text[])))
);


ALTER TABLE public.blockchain_transactions OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 26051)
-- Name: blockchain_performance; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.blockchain_performance AS
 SELECT date("timestamp") AS date,
    count(*) AS daily_transactions,
    avg(gas_used) AS avg_gas_used,
    avg(transaction_fee) AS avg_transaction_fee,
    count(*) FILTER (WHERE ((status)::text = 'confirmed'::text)) AS confirmed_transactions,
    count(*) FILTER (WHERE ((status)::text = 'failed'::text)) AS failed_transactions
   FROM public.blockchain_transactions
  GROUP BY (date("timestamp"))
  ORDER BY (date("timestamp")) DESC;


ALTER VIEW public.blockchain_performance OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 25951)
-- Name: consensus_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.consensus_records (
    consensus_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    block_number bigint NOT NULL,
    block_hash character varying(64) NOT NULL,
    previous_block_hash character varying(64) NOT NULL,
    merkle_root character varying(64) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    consensus_algorithm character varying(20) NOT NULL,
    consensus_round integer NOT NULL,
    proposer_address character varying(42) NOT NULL,
    total_validators integer NOT NULL,
    participating_validators integer NOT NULL,
    required_confirmations integer NOT NULL,
    actual_confirmations integer NOT NULL,
    consensus_reached boolean NOT NULL,
    finality_status character varying(15) NOT NULL,
    votes_for integer DEFAULT 0,
    votes_against integer DEFAULT 0,
    votes_abstain integer DEFAULT 0,
    voting_power_for numeric(36,18) DEFAULT 0,
    voting_power_against numeric(36,18) DEFAULT 0,
    consensus_time_ms integer,
    network_latency_ms integer,
    gas_used bigint DEFAULT 0,
    medical_network_id uuid,
    compliance_verified boolean DEFAULT false,
    audit_signature character varying(132),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT consensus_records_consensus_algorithm_check CHECK (((consensus_algorithm)::text = ANY ((ARRAY['proof_of_stake'::character varying, 'proof_of_authority'::character varying, 'delegated_pos'::character varying, 'hybrid'::character varying])::text[]))),
    CONSTRAINT consensus_records_finality_status_check CHECK (((finality_status)::text = ANY ((ARRAY['pending'::character varying, 'probable'::character varying, 'justified'::character varying, 'finalized'::character varying])::text[])))
);


ALTER TABLE public.consensus_records OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 26062)
-- Name: data_triage_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_triage_records (
    triage_id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id character varying(50) NOT NULL,
    provider_id character varying(50),
    data_type character varying(100) NOT NULL,
    source_system character varying(100),
    classification_level character varying(20) NOT NULL,
    priority_score numeric(3,1) NOT NULL,
    security_level character varying(20) DEFAULT 'LEVEL_1'::character varying NOT NULL,
    encryption_required boolean DEFAULT false NOT NULL,
    compliance_flags jsonb DEFAULT '{}'::jsonb NOT NULL,
    risk_assessment numeric(3,2) NOT NULL,
    processing_requirements jsonb DEFAULT '{}'::jsonb NOT NULL,
    analysis_timestamp timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    algorithm_version character varying(20) DEFAULT '1.0.0'::character varying NOT NULL,
    transaction_hash character varying(66),
    blockchain_stored boolean DEFAULT false NOT NULL,
    approval_status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    approver_id character varying(50),
    approval_notes text,
    processed_at timestamp with time zone,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT data_triage_records_approval_status_check CHECK (((approval_status)::text = ANY ((ARRAY['pending'::character varying, 'approved'::character varying, 'rejected'::character varying, 'auto_approved'::character varying])::text[]))),
    CONSTRAINT data_triage_records_classification_level_check CHECK (((classification_level)::text = ANY ((ARRAY['CRITICAL'::character varying, 'HIGH'::character varying, 'MEDIUM'::character varying, 'LOW'::character varying])::text[]))),
    CONSTRAINT data_triage_records_priority_score_check CHECK (((priority_score >= (0)::numeric) AND (priority_score <= (10)::numeric))),
    CONSTRAINT data_triage_records_risk_assessment_check CHECK (((risk_assessment >= (0)::numeric) AND (risk_assessment <= (1)::numeric)))
);


ALTER TABLE public.data_triage_records OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 26035)
-- Name: medical_record_blockchain_mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medical_record_blockchain_mappings (
    mapping_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    medical_record_id uuid NOT NULL,
    patient_id uuid NOT NULL,
    blockchain_address character varying(42) NOT NULL,
    transaction_hash character varying(64) NOT NULL,
    ipfs_hash character varying(46),
    encryption_key_hash character varying(64),
    access_control_hash character varying(64),
    record_type character varying(50) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    last_accessed timestamp with time zone,
    access_count integer DEFAULT 0
);


ALTER TABLE public.medical_record_blockchain_mappings OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 25973)
-- Name: validator_nodes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.validator_nodes (
    validator_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    node_address character varying(42) NOT NULL,
    public_key character varying(132) NOT NULL,
    node_name character varying(100) NOT NULL,
    node_type character varying(20) NOT NULL,
    organization_name character varying(200) NOT NULL,
    organization_id uuid,
    stake_amount numeric(36,18) DEFAULT 0 NOT NULL,
    locked_stake numeric(36,18) DEFAULT 0 NOT NULL,
    delegation_count integer DEFAULT 0,
    total_delegated_stake numeric(36,18) DEFAULT 0,
    voting_power numeric(10,6) DEFAULT 0 NOT NULL,
    uptime_percentage numeric(5,2) DEFAULT 100.00,
    blocks_proposed integer DEFAULT 0,
    blocks_validated integer DEFAULT 0,
    successful_validations integer DEFAULT 0,
    failed_validations integer DEFAULT 0,
    last_active_block bigint,
    last_active_timestamp timestamp with time zone,
    status character varying(15) DEFAULT 'active'::character varying NOT NULL,
    license_number character varying(100),
    license_expiry timestamp with time zone,
    compliance_score numeric(3,2) DEFAULT 1.00,
    hipaa_certified boolean DEFAULT false,
    last_audit_date timestamp with time zone,
    network_endpoint character varying(255),
    p2p_port integer DEFAULT 30303,
    rpc_port integer DEFAULT 8545,
    api_version character varying(20) DEFAULT '1.0'::character varying,
    client_version character varying(50),
    country character varying(3),
    region character varying(100),
    contact_email character varying(255),
    contact_phone character varying(20),
    total_rewards_earned numeric(36,18) DEFAULT 0,
    total_penalties numeric(36,18) DEFAULT 0,
    last_reward_block bigint,
    last_penalty_block bigint,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT validator_nodes_compliance_score_check CHECK (((compliance_score >= (0)::numeric) AND (compliance_score <= (1)::numeric))),
    CONSTRAINT validator_nodes_node_type_check CHECK (((node_type)::text = ANY ((ARRAY['hospital'::character varying, 'clinic'::character varying, 'pharmacy'::character varying, 'insurance'::character varying, 'regulator'::character varying, 'research'::character varying])::text[]))),
    CONSTRAINT validator_nodes_status_check CHECK (((status)::text = ANY ((ARRAY['active'::character varying, 'inactive'::character varying, 'suspended'::character varying, 'slashed'::character varying, 'jailed'::character varying])::text[])))
);


ALTER TABLE public.validator_nodes OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 26046)
-- Name: network_health_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.network_health_summary AS
 SELECT count(*) AS total_validators,
    count(*) FILTER (WHERE ((status)::text = 'active'::text)) AS active_validators,
    count(*) FILTER (WHERE ((status)::text = 'inactive'::text)) AS inactive_validators,
    avg(uptime_percentage) AS avg_uptime,
    sum(stake_amount) AS total_staked,
    avg(compliance_score) AS avg_compliance_score,
    count(*) FILTER (WHERE (hipaa_certified = true)) AS hipaa_certified_count
   FROM public.validator_nodes;


ALTER VIEW public.network_health_summary OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 25929)
-- Name: smart_contract_states; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.smart_contract_states (
    state_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    contract_address character varying(42) NOT NULL,
    contract_name character varying(100) NOT NULL,
    contract_type character varying(50) NOT NULL,
    version character varying(20) NOT NULL,
    state_root_hash character varying(64) NOT NULL,
    storage_layout jsonb NOT NULL,
    current_state jsonb NOT NULL,
    previous_state_hash character varying(64),
    last_updated_block bigint NOT NULL,
    last_updated_transaction character varying(64) NOT NULL,
    deployment_block bigint NOT NULL,
    deployment_transaction character varying(64) NOT NULL,
    owner_address character varying(42) NOT NULL,
    is_active boolean DEFAULT true,
    gas_limit bigint DEFAULT 3000000,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    medical_organization_id uuid,
    compliance_status character varying(20) DEFAULT 'compliant'::character varying,
    hipaa_compliant boolean DEFAULT true,
    audit_trail jsonb DEFAULT '[]'::jsonb,
    CONSTRAINT smart_contract_states_compliance_status_check CHECK (((compliance_status)::text = ANY ((ARRAY['compliant'::character varying, 'non_compliant'::character varying, 'under_review'::character varying])::text[]))),
    CONSTRAINT smart_contract_states_contract_type_check CHECK (((contract_type)::text = ANY ((ARRAY['medical_records'::character varying, 'patient_consent'::character varying, 'insurance_claims'::character varying, 'drug_supply_chain'::character varying, 'clinical_trials'::character varying, 'provider_credentials'::character varying])::text[])))
);


ALTER TABLE public.smart_contract_states OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 26114)
-- Name: system_alerts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_alerts (
    alert_id uuid DEFAULT gen_random_uuid() NOT NULL,
    alert_type character varying(50) NOT NULL,
    severity character varying(20) NOT NULL,
    message text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb,
    acknowledged boolean DEFAULT false,
    acknowledged_by character varying(50),
    acknowledged_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT system_alerts_severity_check CHECK (((severity)::text = ANY ((ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'CRITICAL'::character varying])::text[])))
);


ALTER TABLE public.system_alerts OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 26095)
-- Name: triage_analytics_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.triage_analytics_summary AS
 SELECT count(*) AS total_records,
    count(
        CASE
            WHEN ((classification_level)::text = 'CRITICAL'::text) THEN 1
            ELSE NULL::integer
        END) AS critical_count,
    count(
        CASE
            WHEN ((classification_level)::text = 'HIGH'::text) THEN 1
            ELSE NULL::integer
        END) AS high_count,
    count(
        CASE
            WHEN ((classification_level)::text = 'MEDIUM'::text) THEN 1
            ELSE NULL::integer
        END) AS medium_count,
    count(
        CASE
            WHEN ((classification_level)::text = 'LOW'::text) THEN 1
            ELSE NULL::integer
        END) AS low_count,
    avg(priority_score) AS avg_priority_score,
    avg(risk_assessment) AS avg_risk_score,
    count(
        CASE
            WHEN ((approval_status)::text = 'pending'::text) THEN 1
            ELSE NULL::integer
        END) AS pending_approval,
    count(
        CASE
            WHEN ((approval_status)::text = 'approved'::text) THEN 1
            ELSE NULL::integer
        END) AS approved_count,
    count(
        CASE
            WHEN ((approval_status)::text = 'auto_approved'::text) THEN 1
            ELSE NULL::integer
        END) AS auto_approved_count,
    count(
        CASE
            WHEN ((approval_status)::text = 'rejected'::text) THEN 1
            ELSE NULL::integer
        END) AS rejected_count,
    count(
        CASE
            WHEN (encryption_required = true) THEN 1
            ELSE NULL::integer
        END) AS encryption_required_count,
    count(
        CASE
            WHEN (blockchain_stored = true) THEN 1
            ELSE NULL::integer
        END) AS blockchain_stored_count,
    count(
        CASE
            WHEN (analysis_timestamp >= (now() - '24:00:00'::interval)) THEN 1
            ELSE NULL::integer
        END) AS recent_24h,
    count(
        CASE
            WHEN ((analysis_timestamp >= (now() - '24:00:00'::interval)) AND ((classification_level)::text = 'CRITICAL'::text)) THEN 1
            ELSE NULL::integer
        END) AS recent_critical_24h
   FROM public.data_triage_records;


ALTER VIEW public.triage_analytics_summary OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 26105)
-- Name: triage_daily_trends; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.triage_daily_trends AS
 SELECT date_trunc('day'::text, analysis_timestamp) AS day,
    count(*) AS total_records,
    count(
        CASE
            WHEN ((classification_level)::text = 'CRITICAL'::text) THEN 1
            ELSE NULL::integer
        END) AS critical_count,
    count(
        CASE
            WHEN ((classification_level)::text = 'HIGH'::text) THEN 1
            ELSE NULL::integer
        END) AS high_count,
    avg(priority_score) AS avg_priority,
    avg(risk_assessment) AS avg_risk,
    count(
        CASE
            WHEN ((approval_status)::text = 'auto_approved'::text) THEN 1
            ELSE NULL::integer
        END) AS auto_approved_count
   FROM public.data_triage_records
  WHERE (analysis_timestamp >= (now() - '30 days'::interval))
  GROUP BY (date_trunc('day'::text, analysis_timestamp))
  ORDER BY (date_trunc('day'::text, analysis_timestamp)) DESC;


ALTER VIEW public.triage_daily_trends OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 26100)
-- Name: triage_provider_performance; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.triage_provider_performance AS
 SELECT provider_id,
    count(*) AS total_triaged,
    avg(priority_score) AS avg_priority,
    avg(risk_assessment) AS avg_risk,
    count(
        CASE
            WHEN ((classification_level)::text = 'CRITICAL'::text) THEN 1
            ELSE NULL::integer
        END) AS critical_cases,
    count(
        CASE
            WHEN ((approval_status)::text = 'approved'::text) THEN 1
            ELSE NULL::integer
        END) AS approved_cases,
    count(
        CASE
            WHEN (encryption_required = true) THEN 1
            ELSE NULL::integer
        END) AS encrypted_cases,
    avg((EXTRACT(epoch FROM (processed_at - analysis_timestamp)) / (3600)::numeric)) AS avg_processing_hours
   FROM public.data_triage_records
  WHERE (provider_id IS NOT NULL)
  GROUP BY provider_id;


ALTER VIEW public.triage_provider_performance OWNER TO postgres;

--
-- TOC entry 5101 (class 0 OID 26013)
-- Dependencies: 221
-- Data for Name: blockchain_blocks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.blockchain_blocks (block_id, block_number, block_hash, parent_hash, merkle_root, state_root, receipts_root, miner_address, difficulty, total_difficulty, gas_limit, gas_used, "timestamp", extra_data, transaction_count, uncle_count, size_bytes, block_reward, created_at) FROM stdin;
\.


--
-- TOC entry 5097 (class 0 OID 25903)
-- Dependencies: 217
-- Data for Name: blockchain_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.blockchain_transactions (transaction_id, block_hash, block_number, transaction_hash, transaction_index, from_address, to_address, value, gas_used, gas_price, transaction_fee, nonce, transaction_type, status, input_data, output_data, "timestamp", confirmation_count, medical_record_id, patient_id, provider_id, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5099 (class 0 OID 25951)
-- Dependencies: 219
-- Data for Name: consensus_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.consensus_records (consensus_id, block_number, block_hash, previous_block_hash, merkle_root, "timestamp", consensus_algorithm, consensus_round, proposer_address, total_validators, participating_validators, required_confirmations, actual_confirmations, consensus_reached, finality_status, votes_for, votes_against, votes_abstain, voting_power_for, voting_power_against, consensus_time_ms, network_latency_ms, gas_used, medical_network_id, compliance_verified, audit_signature, created_at) FROM stdin;
\.


--
-- TOC entry 5103 (class 0 OID 26062)
-- Dependencies: 225
-- Data for Name: data_triage_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_triage_records (triage_id, patient_id, provider_id, data_type, source_system, classification_level, priority_score, security_level, encryption_required, compliance_flags, risk_assessment, processing_requirements, analysis_timestamp, algorithm_version, transaction_hash, blockchain_stored, approval_status, approver_id, approval_notes, processed_at, metadata, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5102 (class 0 OID 26035)
-- Dependencies: 222
-- Data for Name: medical_record_blockchain_mappings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.medical_record_blockchain_mappings (mapping_id, medical_record_id, patient_id, blockchain_address, transaction_hash, ipfs_hash, encryption_key_hash, access_control_hash, record_type, created_at, last_accessed, access_count) FROM stdin;
\.


--
-- TOC entry 5098 (class 0 OID 25929)
-- Dependencies: 218
-- Data for Name: smart_contract_states; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.smart_contract_states (state_id, contract_address, contract_name, contract_type, version, state_root_hash, storage_layout, current_state, previous_state_hash, last_updated_block, last_updated_transaction, deployment_block, deployment_transaction, owner_address, is_active, gas_limit, created_at, updated_at, medical_organization_id, compliance_status, hipaa_compliant, audit_trail) FROM stdin;
\.


--
-- TOC entry 5104 (class 0 OID 26114)
-- Dependencies: 229
-- Data for Name: system_alerts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_alerts (alert_id, alert_type, severity, message, metadata, acknowledged, acknowledged_by, acknowledged_at, created_at) FROM stdin;
\.


--
-- TOC entry 5100 (class 0 OID 25973)
-- Dependencies: 220
-- Data for Name: validator_nodes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.validator_nodes (validator_id, node_address, public_key, node_name, node_type, organization_name, organization_id, stake_amount, locked_stake, delegation_count, total_delegated_stake, voting_power, uptime_percentage, blocks_proposed, blocks_validated, successful_validations, failed_validations, last_active_block, last_active_timestamp, status, license_number, license_expiry, compliance_score, hipaa_certified, last_audit_date, network_endpoint, p2p_port, rpc_port, api_version, client_version, country, region, contact_email, contact_phone, total_rewards_earned, total_penalties, last_reward_block, last_penalty_block, created_at, updated_at) FROM stdin;
be7c6009-80e8-49d4-82a4-cc3d4e64c9ff	0x742d35Cc6B3C3Bdf5C2d0c5C2C8B8B8B8B8B8B8B	0x04d35Cc6B3C3Bdf5C2d0c5C2C8B8B8B8B8B8B8B742d35Cc6B3C3Bdf5C2d0c5C2C8B8B8B8B8B8B8B742d35Cc6B3C3Bdf5C2d0c5C2C8B8B8B8B8B8B8B	Abena-Hospital-Node-1	hospital	Abena Medical Center	\N	100000.000000000000000000	0.000000000000000000	0	0.000000000000000000	0.000000	100.00	0	0	0	0	\N	\N	active	\N	\N	0.98	t	\N	\N	30303	8545	1.0	\N	\N	\N	\N	\N	0.000000000000000000	0.000000000000000000	\N	\N	2025-06-10 12:34:46.76298-07	2025-06-10 12:34:46.76298-07
11785d5d-1165-4293-85f7-eba70fcbbc83	0x853e46Ed7F5B4C8e6F5D5E5E5D5D5D5D5D5D5D5D	0x04853e46Ed7F5B4C8e6F5D5E5E5D5D5D5D5D5D5D853e46Ed7F5B4C8e6F5D5E5E5D5D5D5D5D5D5D853e46Ed7F5B4C8e6F5D5E5E5D5D5D5D5D5D5D	CityClinic-Node-1	clinic	City Health Clinic	\N	50000.000000000000000000	0.000000000000000000	0	0.000000000000000000	0.500000	100.00	0	0	0	0	\N	\N	active	\N	\N	0.95	t	\N	\N	30303	8545	1.0	\N	\N	\N	\N	\N	0.000000000000000000	0.000000000000000000	\N	\N	2025-06-10 12:34:46.76298-07	2025-06-10 12:34:46.76298-07
a432406d-2b69-4cef-9373-1840405feede	0x964f57Ee8G6C5D9f7G6E6F6F6E6E6E6E6E6E6E6E	0x04964f57Ee8G6C5D9f7G6E6F6F6E6E6E6E6E6E6E964f57Ee8G6C5D9f7G6E6F6F6E6E6E6E6E6E6E964f57Ee8G6C5D9f7G6E6F6F6E6E6E6E6E6E6E	PharmaCare-Node-1	pharmacy	PharmaCare Networks	\N	25000.000000000000000000	0.000000000000000000	0	0.000000000000000000	0.166667	100.00	0	0	0	0	\N	\N	active	\N	\N	0.92	t	\N	\N	30303	8545	1.0	\N	\N	\N	\N	\N	0.000000000000000000	0.000000000000000000	\N	\N	2025-06-10 12:34:46.76298-07	2025-06-10 12:34:46.76298-07
\.


--
-- TOC entry 4911 (class 2606 OID 26030)
-- Name: blockchain_blocks blockchain_blocks_block_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.blockchain_blocks
    ADD CONSTRAINT blockchain_blocks_block_hash_key UNIQUE (block_hash);


--
-- TOC entry 4913 (class 2606 OID 26028)
-- Name: blockchain_blocks blockchain_blocks_block_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.blockchain_blocks
    ADD CONSTRAINT blockchain_blocks_block_number_key UNIQUE (block_number);


--
-- TOC entry 4915 (class 2606 OID 26026)
-- Name: blockchain_blocks blockchain_blocks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.blockchain_blocks
    ADD CONSTRAINT blockchain_blocks_pkey PRIMARY KEY (block_id);


--
-- TOC entry 4872 (class 2606 OID 25917)
-- Name: blockchain_transactions blockchain_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.blockchain_transactions
    ADD CONSTRAINT blockchain_transactions_pkey PRIMARY KEY (transaction_id);


--
-- TOC entry 4874 (class 2606 OID 25919)
-- Name: blockchain_transactions blockchain_transactions_transaction_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.blockchain_transactions
    ADD CONSTRAINT blockchain_transactions_transaction_hash_key UNIQUE (transaction_hash);


--
-- TOC entry 4892 (class 2606 OID 25966)
-- Name: consensus_records consensus_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consensus_records
    ADD CONSTRAINT consensus_records_pkey PRIMARY KEY (consensus_id);


--
-- TOC entry 4926 (class 2606 OID 26084)
-- Name: data_triage_records data_triage_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_triage_records
    ADD CONSTRAINT data_triage_records_pkey PRIMARY KEY (triage_id);


--
-- TOC entry 4924 (class 2606 OID 26042)
-- Name: medical_record_blockchain_mappings medical_record_blockchain_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medical_record_blockchain_mappings
    ADD CONSTRAINT medical_record_blockchain_mappings_pkey PRIMARY KEY (mapping_id);


--
-- TOC entry 4890 (class 2606 OID 25945)
-- Name: smart_contract_states smart_contract_states_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.smart_contract_states
    ADD CONSTRAINT smart_contract_states_pkey PRIMARY KEY (state_id);


--
-- TOC entry 4942 (class 2606 OID 26125)
-- Name: system_alerts system_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_alerts
    ADD CONSTRAINT system_alerts_pkey PRIMARY KEY (alert_id);


--
-- TOC entry 4907 (class 2606 OID 26005)
-- Name: validator_nodes validator_nodes_node_address_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.validator_nodes
    ADD CONSTRAINT validator_nodes_node_address_key UNIQUE (node_address);


--
-- TOC entry 4909 (class 2606 OID 26003)
-- Name: validator_nodes validator_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.validator_nodes
    ADD CONSTRAINT validator_nodes_pkey PRIMARY KEY (validator_id);


--
-- TOC entry 4916 (class 1259 OID 26032)
-- Name: idx_block_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_block_hash ON public.blockchain_blocks USING btree (block_hash);


--
-- TOC entry 4917 (class 1259 OID 26034)
-- Name: idx_block_miner; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_block_miner ON public.blockchain_blocks USING btree (miner_address);


--
-- TOC entry 4918 (class 1259 OID 26031)
-- Name: idx_block_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_block_number ON public.blockchain_blocks USING btree (block_number);


--
-- TOC entry 4919 (class 1259 OID 26033)
-- Name: idx_block_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_block_timestamp ON public.blockchain_blocks USING btree ("timestamp");


--
-- TOC entry 4875 (class 1259 OID 25921)
-- Name: idx_blockchain_block_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_blockchain_block_hash ON public.blockchain_transactions USING btree (block_hash);


--
-- TOC entry 4876 (class 1259 OID 25922)
-- Name: idx_blockchain_block_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_blockchain_block_number ON public.blockchain_transactions USING btree (block_number);


--
-- TOC entry 4877 (class 1259 OID 25923)
-- Name: idx_blockchain_from_address; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_blockchain_from_address ON public.blockchain_transactions USING btree (from_address);


--
-- TOC entry 4878 (class 1259 OID 25926)
-- Name: idx_blockchain_medical_record; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_blockchain_medical_record ON public.blockchain_transactions USING btree (medical_record_id);


--
-- TOC entry 4879 (class 1259 OID 25927)
-- Name: idx_blockchain_patient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_blockchain_patient ON public.blockchain_transactions USING btree (patient_id);


--
-- TOC entry 4880 (class 1259 OID 25928)
-- Name: idx_blockchain_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_blockchain_status ON public.blockchain_transactions USING btree (status);


--
-- TOC entry 4881 (class 1259 OID 25925)
-- Name: idx_blockchain_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_blockchain_timestamp ON public.blockchain_transactions USING btree ("timestamp");


--
-- TOC entry 4882 (class 1259 OID 25924)
-- Name: idx_blockchain_to_address; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_blockchain_to_address ON public.blockchain_transactions USING btree (to_address);


--
-- TOC entry 4883 (class 1259 OID 25920)
-- Name: idx_blockchain_tx_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_blockchain_tx_hash ON public.blockchain_transactions USING btree (transaction_hash);


--
-- TOC entry 4893 (class 1259 OID 25968)
-- Name: idx_consensus_block_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_consensus_block_hash ON public.consensus_records USING btree (block_hash);


--
-- TOC entry 4894 (class 1259 OID 25967)
-- Name: idx_consensus_block_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_consensus_block_number ON public.consensus_records USING btree (block_number);


--
-- TOC entry 4895 (class 1259 OID 25972)
-- Name: idx_consensus_medical_network; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_consensus_medical_network ON public.consensus_records USING btree (medical_network_id);


--
-- TOC entry 4896 (class 1259 OID 25970)
-- Name: idx_consensus_proposer; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_consensus_proposer ON public.consensus_records USING btree (proposer_address);


--
-- TOC entry 4897 (class 1259 OID 25971)
-- Name: idx_consensus_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_consensus_status ON public.consensus_records USING btree (finality_status);


--
-- TOC entry 4898 (class 1259 OID 25969)
-- Name: idx_consensus_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_consensus_timestamp ON public.consensus_records USING btree ("timestamp");


--
-- TOC entry 4884 (class 1259 OID 25948)
-- Name: idx_contract_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contract_active ON public.smart_contract_states USING btree (is_active);


--
-- TOC entry 4885 (class 1259 OID 25946)
-- Name: idx_contract_address; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contract_address ON public.smart_contract_states USING btree (contract_address);


--
-- TOC entry 4886 (class 1259 OID 25949)
-- Name: idx_contract_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contract_org ON public.smart_contract_states USING btree (medical_organization_id);


--
-- TOC entry 4887 (class 1259 OID 25947)
-- Name: idx_contract_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contract_type ON public.smart_contract_states USING btree (contract_type);


--
-- TOC entry 4888 (class 1259 OID 25950)
-- Name: idx_contract_updated_block; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contract_updated_block ON public.smart_contract_states USING btree (last_updated_block);


--
-- TOC entry 4920 (class 1259 OID 26045)
-- Name: idx_medical_mapping_blockchain; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_medical_mapping_blockchain ON public.medical_record_blockchain_mappings USING btree (blockchain_address);


--
-- TOC entry 4921 (class 1259 OID 26044)
-- Name: idx_medical_mapping_patient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_medical_mapping_patient ON public.medical_record_blockchain_mappings USING btree (patient_id);


--
-- TOC entry 4922 (class 1259 OID 26043)
-- Name: idx_medical_mapping_record; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_medical_mapping_record ON public.medical_record_blockchain_mappings USING btree (medical_record_id);


--
-- TOC entry 4937 (class 1259 OID 26128)
-- Name: idx_system_alerts_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_system_alerts_created ON public.system_alerts USING btree (created_at DESC);


--
-- TOC entry 4938 (class 1259 OID 26127)
-- Name: idx_system_alerts_severity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_system_alerts_severity ON public.system_alerts USING btree (severity);


--
-- TOC entry 4939 (class 1259 OID 26126)
-- Name: idx_system_alerts_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_system_alerts_type ON public.system_alerts USING btree (alert_type);


--
-- TOC entry 4940 (class 1259 OID 26129)
-- Name: idx_system_alerts_unacknowledged; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_system_alerts_unacknowledged ON public.system_alerts USING btree (acknowledged) WHERE (acknowledged = false);


--
-- TOC entry 4927 (class 1259 OID 26089)
-- Name: idx_triage_approval_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_triage_approval_status ON public.data_triage_records USING btree (approval_status);


--
-- TOC entry 4928 (class 1259 OID 26086)
-- Name: idx_triage_classification; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_triage_classification ON public.data_triage_records USING btree (classification_level);


--
-- TOC entry 4929 (class 1259 OID 26092)
-- Name: idx_triage_classification_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_triage_classification_priority ON public.data_triage_records USING btree (classification_level, priority_score DESC);


--
-- TOC entry 4930 (class 1259 OID 26091)
-- Name: idx_triage_data_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_triage_data_type ON public.data_triage_records USING btree (data_type);


--
-- TOC entry 4931 (class 1259 OID 26085)
-- Name: idx_triage_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_triage_patient_id ON public.data_triage_records USING btree (patient_id);


--
-- TOC entry 4932 (class 1259 OID 26093)
-- Name: idx_triage_patient_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_triage_patient_timestamp ON public.data_triage_records USING btree (patient_id, analysis_timestamp DESC);


--
-- TOC entry 4933 (class 1259 OID 26094)
-- Name: idx_triage_pending_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_triage_pending_priority ON public.data_triage_records USING btree (approval_status, priority_score DESC) WHERE ((approval_status)::text = 'pending'::text);


--
-- TOC entry 4934 (class 1259 OID 26087)
-- Name: idx_triage_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_triage_priority ON public.data_triage_records USING btree (priority_score DESC);


--
-- TOC entry 4935 (class 1259 OID 26090)
-- Name: idx_triage_provider; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_triage_provider ON public.data_triage_records USING btree (provider_id);


--
-- TOC entry 4936 (class 1259 OID 26088)
-- Name: idx_triage_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_triage_timestamp ON public.data_triage_records USING btree (analysis_timestamp DESC);


--
-- TOC entry 4899 (class 1259 OID 26006)
-- Name: idx_validator_address; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_validator_address ON public.validator_nodes USING btree (node_address);


--
-- TOC entry 4900 (class 1259 OID 26007)
-- Name: idx_validator_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_validator_org ON public.validator_nodes USING btree (organization_id);


--
-- TOC entry 4901 (class 1259 OID 26011)
-- Name: idx_validator_stake; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_validator_stake ON public.validator_nodes USING btree (stake_amount);


--
-- TOC entry 4902 (class 1259 OID 26009)
-- Name: idx_validator_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_validator_status ON public.validator_nodes USING btree (status);


--
-- TOC entry 4903 (class 1259 OID 26008)
-- Name: idx_validator_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_validator_type ON public.validator_nodes USING btree (node_type);


--
-- TOC entry 4904 (class 1259 OID 26012)
-- Name: idx_validator_uptime; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_validator_uptime ON public.validator_nodes USING btree (uptime_percentage);


--
-- TOC entry 4905 (class 1259 OID 26010)
-- Name: idx_validator_voting_power; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_validator_voting_power ON public.validator_nodes USING btree (voting_power);


--
-- TOC entry 4945 (class 2620 OID 26061)
-- Name: validator_nodes calculate_validator_voting_power; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER calculate_validator_voting_power BEFORE INSERT OR UPDATE ON public.validator_nodes FOR EACH ROW EXECUTE FUNCTION public.calculate_voting_power();


--
-- TOC entry 4947 (class 2620 OID 26113)
-- Name: data_triage_records triage_critical_notification; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER triage_critical_notification AFTER INSERT ON public.data_triage_records FOR EACH ROW WHEN (((new.classification_level)::text = 'CRITICAL'::text)) EXECUTE FUNCTION public.notify_critical_triage();


--
-- TOC entry 4948 (class 2620 OID 26111)
-- Name: data_triage_records triage_update_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER triage_update_timestamp BEFORE UPDATE ON public.data_triage_records FOR EACH ROW EXECUTE FUNCTION public.update_triage_timestamp();


--
-- TOC entry 4943 (class 2620 OID 26057)
-- Name: blockchain_transactions update_blockchain_transactions_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_blockchain_transactions_updated_at BEFORE UPDATE ON public.blockchain_transactions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4944 (class 2620 OID 26058)
-- Name: smart_contract_states update_smart_contract_states_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_smart_contract_states_updated_at BEFORE UPDATE ON public.smart_contract_states FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4946 (class 2620 OID 26059)
-- Name: validator_nodes update_validator_nodes_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_validator_nodes_updated_at BEFORE UPDATE ON public.validator_nodes FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


-- Completed on 2025-07-04 07:27:57

--
-- PostgreSQL database dump complete
--

