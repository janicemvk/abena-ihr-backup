--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.9

-- Started on 2025-07-04 07:41:56

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
-- TOC entry 2 (class 3079 OID 25750)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 5020 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 238 (class 1255 OID 26242)
-- Name: check_permission_expiration(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_permission_expiration() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Auto-expire permissions that have passed their expiration date
    IF NEW.expiration_date IS NOT NULL AND NEW.expiration_date < CURRENT_TIMESTAMP AND NEW.permission_status = 'active' THEN
        NEW.permission_status = 'expired';
    END IF;
    
    -- Auto-renew if eligible
    IF NEW.auto_renewal = true AND NEW.expiration_date IS NOT NULL AND NEW.expiration_date < CURRENT_TIMESTAMP AND NEW.permission_status = 'active' THEN
        NEW.expiration_date = CURRENT_TIMESTAMP + INTERVAL '1 month' * NEW.renewal_period_months;
        NEW.permission_status = 'active';
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_permission_expiration() OWNER TO postgres;

--
-- TOC entry 237 (class 1255 OID 26240)
-- Name: update_data_sharing_timestamp(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_data_sharing_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_data_sharing_timestamp() OWNER TO postgres;

--
-- TOC entry 236 (class 1255 OID 25761)
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
-- TOC entry 217 (class 1259 OID 25283)
-- Name: access_logs; Type: TABLE; Schema: public; Owner: abena_user
--

CREATE TABLE public.access_logs (
    log_id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id uuid,
    user_id character varying(100) NOT NULL,
    access_type character varying(50) NOT NULL,
    accessed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    ip_address inet,
    user_agent text
);


ALTER TABLE public.access_logs OWNER TO abena_user;

--
-- TOC entry 223 (class 1259 OID 26177)
-- Name: data_sharing_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_sharing_permissions (
    permission_id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id uuid NOT NULL,
    permission_type character varying(50) NOT NULL,
    permission_scope character varying(30) NOT NULL,
    includes_demographics boolean DEFAULT false,
    includes_medical_history boolean DEFAULT false,
    includes_lab_results boolean DEFAULT false,
    includes_medications boolean DEFAULT false,
    includes_allergies boolean DEFAULT false,
    includes_vital_signs boolean DEFAULT false,
    includes_imaging boolean DEFAULT false,
    includes_genetic_data boolean DEFAULT false,
    includes_mental_health boolean DEFAULT false,
    includes_substance_abuse boolean DEFAULT false,
    recipient_type character varying(30) NOT NULL,
    recipient_id uuid,
    recipient_name character varying(200),
    recipient_organization character varying(200),
    permission_status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    consent_method character varying(30) NOT NULL,
    granted_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    effective_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expiration_date timestamp with time zone,
    auto_renewal boolean DEFAULT false,
    renewal_period_months integer,
    purpose_limitation text,
    access_frequency_limit character varying(20),
    max_access_count integer,
    current_access_count integer DEFAULT 0,
    geographic_restrictions text[],
    time_restrictions jsonb,
    ip_restrictions text[],
    consent_document_id uuid,
    consent_version character varying(20),
    witness_name character varying(100),
    witness_relationship character varying(50),
    legal_guardian_id uuid,
    can_be_revoked boolean DEFAULT true,
    revocation_notice_days integer DEFAULT 30,
    revoked_date timestamp with time zone,
    revoked_by uuid,
    revocation_reason text,
    hipaa_compliant boolean DEFAULT true,
    gdpr_compliant boolean DEFAULT true,
    state_law_compliant boolean DEFAULT true,
    requires_audit_trail boolean DEFAULT true,
    data_minimization boolean DEFAULT true,
    purpose_limitation_enforced boolean DEFAULT true,
    retention_period_days integer,
    emergency_override_allowed boolean DEFAULT false,
    override_conditions text,
    break_glass_access boolean DEFAULT false,
    notify_patient_on_access boolean DEFAULT true,
    notification_method character varying(30),
    notification_frequency character varying(20),
    api_access_allowed boolean DEFAULT false,
    bulk_export_allowed boolean DEFAULT false,
    real_time_access boolean DEFAULT false,
    notes text,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    CONSTRAINT data_sharing_permissions_consent_method_check CHECK (((consent_method)::text = ANY ((ARRAY['written_consent'::character varying, 'electronic_consent'::character varying, 'verbal_consent'::character varying, 'implied_consent'::character varying, 'emergency_override'::character varying, 'legal_guardian'::character varying, 'court_order'::character varying])::text[]))),
    CONSTRAINT data_sharing_permissions_notification_frequency_check CHECK (((notification_frequency)::text = ANY ((ARRAY['immediate'::character varying, 'daily'::character varying, 'weekly'::character varying, 'monthly'::character varying, 'none'::character varying])::text[]))),
    CONSTRAINT data_sharing_permissions_notification_method_check CHECK (((notification_method)::text = ANY ((ARRAY['email'::character varying, 'sms'::character varying, 'phone'::character varying, 'mail'::character varying, 'patient_portal'::character varying, 'none'::character varying])::text[]))),
    CONSTRAINT data_sharing_permissions_permission_scope_check CHECK (((permission_scope)::text = ANY ((ARRAY['full_access'::character varying, 'limited_access'::character varying, 'specific_data'::character varying, 'emergency_only'::character varying, 'no_access'::character varying])::text[]))),
    CONSTRAINT data_sharing_permissions_permission_status_check CHECK (((permission_status)::text = ANY ((ARRAY['pending'::character varying, 'active'::character varying, 'suspended'::character varying, 'revoked'::character varying, 'expired'::character varying])::text[]))),
    CONSTRAINT data_sharing_permissions_permission_type_check CHECK (((permission_type)::text = ANY ((ARRAY['research_sharing'::character varying, 'care_coordination'::character varying, 'public_health'::character varying, 'insurance_claims'::character varying, 'family_access'::character varying, 'emergency_access'::character varying, 'provider_network'::character varying, 'analytics'::character varying, 'quality_improvement'::character varying, 'billing'::character varying, 'legal_compliance'::character varying, 'marketing'::character varying])::text[]))),
    CONSTRAINT data_sharing_permissions_recipient_type_check CHECK (((recipient_type)::text = ANY ((ARRAY['healthcare_provider'::character varying, 'research_institution'::character varying, 'insurance_company'::character varying, 'family_member'::character varying, 'emergency_contact'::character varying, 'government_agency'::character varying, 'pharmacy'::character varying, 'laboratory'::character varying, 'specialist'::character varying, 'care_team'::character varying])::text[]))),
    CONSTRAINT valid_access_count CHECK (((current_access_count <= max_access_count) OR (max_access_count IS NULL))),
    CONSTRAINT valid_expiration CHECK (((expiration_date IS NULL) OR (expiration_date > effective_date))),
    CONSTRAINT valid_renewal CHECK (((NOT auto_renewal) OR (renewal_period_months IS NOT NULL)))
);


ALTER TABLE public.data_sharing_permissions OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 26244)
-- Name: active_data_sharing_summary; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.active_data_sharing_summary AS
 SELECT permission_type,
    recipient_type,
    count(*) AS total_permissions,
    count(
        CASE
            WHEN (expiration_date IS NULL) THEN 1
            ELSE NULL::integer
        END) AS permanent_permissions,
    count(
        CASE
            WHEN (expiration_date > CURRENT_TIMESTAMP) THEN 1
            ELSE NULL::integer
        END) AS temporary_permissions,
    avg(current_access_count) AS avg_access_count,
    count(
        CASE
            WHEN (emergency_override_allowed = true) THEN 1
            ELSE NULL::integer
        END) AS emergency_override_count
   FROM public.data_sharing_permissions
  WHERE ((permission_status)::text = 'active'::text)
  GROUP BY permission_type, recipient_type
  ORDER BY (count(*)) DESC;


ALTER VIEW public.active_data_sharing_summary OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 25775)
-- Name: emergency_contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.emergency_contacts (
    contact_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    contact_name character varying(255) NOT NULL,
    relationship character varying(100) NOT NULL,
    phone character varying(20) NOT NULL,
    email character varying(255),
    address jsonb,
    is_primary boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.emergency_contacts OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 26249)
-- Name: expiring_permissions; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.expiring_permissions AS
 SELECT permission_id,
    patient_id,
    permission_type,
    recipient_name,
    recipient_organization,
    expiration_date,
    EXTRACT(days FROM (expiration_date - CURRENT_TIMESTAMP)) AS days_until_expiration,
    auto_renewal,
    notification_method
   FROM public.data_sharing_permissions
  WHERE (((permission_status)::text = 'active'::text) AND (expiration_date IS NOT NULL) AND (expiration_date <= (CURRENT_TIMESTAMP + '30 days'::interval)))
  ORDER BY expiration_date;


ALTER VIEW public.expiring_permissions OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 25791)
-- Name: insurance_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.insurance_plans (
    insurance_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    insurance_company character varying(255) NOT NULL,
    policy_number character varying(100) NOT NULL,
    group_number character varying(100),
    subscriber_name character varying(255),
    subscriber_relationship character varying(50),
    subscriber_dob date,
    plan_type character varying(100),
    effective_date date,
    termination_date date,
    copay_amount numeric(10,2),
    deductible_amount numeric(10,2),
    is_primary boolean DEFAULT false,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.insurance_plans OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 25270)
-- Name: patient_consents; Type: TABLE; Schema: public; Owner: abena_user
--

CREATE TABLE public.patient_consents (
    consent_id uuid DEFAULT gen_random_uuid() NOT NULL,
    patient_id uuid,
    consent_type character varying(50) NOT NULL,
    granted boolean DEFAULT false,
    granted_at timestamp without time zone,
    expires_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.patient_consents OWNER TO abena_user;

--
-- TOC entry 221 (class 1259 OID 25808)
-- Name: patient_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.patient_documents (
    document_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    document_name character varying(255) NOT NULL,
    document_type character varying(100) NOT NULL,
    file_path character varying(500),
    file_size integer,
    mime_type character varying(100),
    uploaded_by uuid,
    upload_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    is_confidential boolean DEFAULT false,
    expiration_date date,
    tags text[],
    metadata jsonb
);


ALTER TABLE public.patient_documents OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 25823)
-- Name: patient_preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.patient_preferences (
    preference_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    patient_id uuid NOT NULL,
    preference_category character varying(100) NOT NULL,
    preference_key character varying(100) NOT NULL,
    preference_value jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.patient_preferences OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 25762)
-- Name: patients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.patients (
    patient_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    medical_record_number character varying(50) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    middle_name character varying(100),
    date_of_birth date NOT NULL,
    gender character varying(20),
    ssn character varying(11),
    phone character varying(20),
    email character varying(255),
    address jsonb,
    marital_status character varying(20),
    emergency_contact jsonb,
    preferred_language character varying(50),
    ethnicity character varying(100),
    race character varying(100),
    religion character varying(100),
    occupation character varying(100),
    employer character varying(255),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.patients OWNER TO postgres;

--
-- TOC entry 5007 (class 0 OID 25283)
-- Dependencies: 217
-- Data for Name: access_logs; Type: TABLE DATA; Schema: public; Owner: abena_user
--

COPY public.access_logs (log_id, patient_id, user_id, access_type, accessed_at, ip_address, user_agent) FROM stdin;
\.


--
-- TOC entry 5013 (class 0 OID 26177)
-- Dependencies: 223
-- Data for Name: data_sharing_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_sharing_permissions (permission_id, patient_id, permission_type, permission_scope, includes_demographics, includes_medical_history, includes_lab_results, includes_medications, includes_allergies, includes_vital_signs, includes_imaging, includes_genetic_data, includes_mental_health, includes_substance_abuse, recipient_type, recipient_id, recipient_name, recipient_organization, permission_status, consent_method, granted_date, effective_date, expiration_date, auto_renewal, renewal_period_months, purpose_limitation, access_frequency_limit, max_access_count, current_access_count, geographic_restrictions, time_restrictions, ip_restrictions, consent_document_id, consent_version, witness_name, witness_relationship, legal_guardian_id, can_be_revoked, revocation_notice_days, revoked_date, revoked_by, revocation_reason, hipaa_compliant, gdpr_compliant, state_law_compliant, requires_audit_trail, data_minimization, purpose_limitation_enforced, retention_period_days, emergency_override_allowed, override_conditions, break_glass_access, notify_patient_on_access, notification_method, notification_frequency, api_access_allowed, bulk_export_allowed, real_time_access, notes, metadata, created_at, updated_at, created_by, updated_by) FROM stdin;
0d2f29b1-8efa-40ba-8ab9-edb39e433a8f	550e8400-e29b-41d4-a716-446655440001	research_sharing	limited_access	f	t	t	t	f	f	f	f	f	f	research_institution	\N	Dr. Sarah Johnson	Medical Research Institute	pending	electronic_consent	2025-06-10 13:24:19.334562-07	2025-06-10 13:24:19.334562-07	2026-06-10 13:24:19.334562-07	t	12	Cardiovascular disease research and treatment improvement	\N	\N	0	\N	\N	\N	\N	\N	\N	\N	\N	t	30	\N	\N	\N	t	t	t	t	t	t	\N	f	\N	f	t	\N	\N	f	f	f	\N	{}	2025-06-10 13:24:19.334562-07	2025-06-10 13:24:19.334562-07	\N	\N
a0ab5f07-53ff-4067-acdd-39fab8e2e87d	550e8400-e29b-41d4-a716-446655440002	care_coordination	full_access	t	t	t	t	f	f	f	f	f	f	healthcare_provider	\N	Dr. Michael Chen	City Medical Center	pending	written_consent	2025-06-10 13:24:19.334562-07	2025-06-10 13:24:19.334562-07	2027-06-10 13:24:19.334562-07	f	\N	Comprehensive care coordination and treatment planning	\N	\N	0	\N	\N	\N	\N	\N	\N	\N	\N	t	30	\N	\N	\N	t	t	t	t	t	t	\N	f	\N	f	t	\N	\N	f	f	f	\N	{}	2025-06-10 13:24:19.334562-07	2025-06-10 13:24:19.334562-07	\N	\N
c9adeefe-a0ec-48c2-82c8-d77d4bf03eec	550e8400-e29b-41d4-a716-446655440003	insurance_claims	specific_data	t	f	t	f	f	f	f	f	f	f	insurance_company	\N	Claims Department	HealthFirst Insurance	pending	electronic_consent	2025-06-10 13:24:19.334562-07	2025-06-10 13:24:19.334562-07	2025-12-10 13:24:19.334562-08	t	6	Insurance claim processing and verification only	\N	\N	0	\N	\N	\N	\N	\N	\N	\N	\N	t	30	\N	\N	\N	t	f	t	t	t	t	\N	f	\N	f	t	\N	\N	f	f	f	\N	{}	2025-06-10 13:24:19.334562-07	2025-06-10 13:24:19.334562-07	\N	\N
74875c56-59c8-4299-a8dc-fb8b38a5e3d1	550e8400-e29b-41d4-a716-446655440004	family_access	limited_access	t	t	f	t	f	f	f	f	f	f	family_member	\N	Emma Johnson	Spouse	pending	written_consent	2025-06-10 13:24:19.334562-07	2025-06-10 13:24:19.334562-07	\N	f	\N	Emergency medical decision making and care support	\N	\N	0	\N	\N	\N	\N	\N	\N	\N	\N	t	30	\N	\N	\N	t	t	t	t	t	t	\N	f	\N	f	t	\N	\N	f	f	f	\N	{}	2025-06-10 13:24:19.334562-07	2025-06-10 13:24:19.334562-07	\N	\N
a70a719e-3acc-4f42-86ba-050b61c269fa	550e8400-e29b-41d4-a716-446655440005	emergency_access	emergency_only	t	t	t	t	f	f	f	f	f	f	emergency_contact	\N	Robert Smith	Emergency Contact	pending	implied_consent	2025-06-10 13:24:19.334562-07	2025-06-10 13:24:19.334562-07	\N	f	\N	Emergency medical situations only	\N	\N	0	\N	\N	\N	\N	\N	\N	\N	\N	t	30	\N	\N	\N	t	t	t	t	t	t	\N	f	\N	f	t	\N	\N	f	f	f	\N	{}	2025-06-10 13:24:19.334562-07	2025-06-10 13:24:19.334562-07	\N	\N
\.


--
-- TOC entry 5009 (class 0 OID 25775)
-- Dependencies: 219
-- Data for Name: emergency_contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.emergency_contacts (contact_id, patient_id, contact_name, relationship, phone, email, address, is_primary, created_at, updated_at) FROM stdin;
bda59d70-557f-47b9-9c26-3d8f5bdf868e	444ed30b-defc-47c9-93ca-5b522828d7ec	Jane Doe	Spouse	555-111-2222	jane.doe@email.com	\N	t	2025-06-07 16:34:05.993636-07	2025-06-07 16:34:05.993636-07
\.


--
-- TOC entry 5010 (class 0 OID 25791)
-- Dependencies: 220
-- Data for Name: insurance_plans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.insurance_plans (insurance_id, patient_id, insurance_company, policy_number, group_number, subscriber_name, subscriber_relationship, subscriber_dob, plan_type, effective_date, termination_date, copay_amount, deductible_amount, is_primary, is_active, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5006 (class 0 OID 25270)
-- Dependencies: 216
-- Data for Name: patient_consents; Type: TABLE DATA; Schema: public; Owner: abena_user
--

COPY public.patient_consents (consent_id, patient_id, consent_type, granted, granted_at, expires_at, created_at) FROM stdin;
\.


--
-- TOC entry 5011 (class 0 OID 25808)
-- Dependencies: 221
-- Data for Name: patient_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.patient_documents (document_id, patient_id, document_name, document_type, file_path, file_size, mime_type, uploaded_by, upload_date, is_confidential, expiration_date, tags, metadata) FROM stdin;
\.


--
-- TOC entry 5012 (class 0 OID 25823)
-- Dependencies: 222
-- Data for Name: patient_preferences; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.patient_preferences (preference_id, patient_id, preference_category, preference_key, preference_value, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5008 (class 0 OID 25762)
-- Dependencies: 218
-- Data for Name: patients; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.patients (patient_id, medical_record_number, first_name, last_name, middle_name, date_of_birth, gender, ssn, phone, email, address, marital_status, emergency_contact, preferred_language, ethnicity, race, religion, occupation, employer, is_active, created_at, updated_at) FROM stdin;
444ed30b-defc-47c9-93ca-5b522828d7ec	MRN001	John	Doe	Michael	1985-03-15	Male	\N	555-987-6543	john.doe@email.com	\N	Married	\N	English	\N	\N	\N	\N	\N	t	2025-06-07 16:34:05.951832-07	2025-06-07 16:34:05.976715-07
357af4b8-8032-4dbd-b50b-d2650f2b70e2	MRN002-CLINICAL	Alice	Johnson	Marie	1990-05-20	Female	\N	555-456-7890	alice.johnson@email.com	\N	Single	\N	English	\N	\N	\N	\N	\N	t	2025-06-07 16:40:27.842165-07	2025-06-07 16:40:27.842165-07
151733f9-6109-4053-bfc8-af0237c3eded	MRN003-FULL-TEST	Emily	Davis	Rose	1985-08-15	Female	\N	555-123-9876	emily.davis@email.com	\N	Married	\N	English	\N	\N	\N	\N	\N	t	2025-06-07 16:48:08.731074-07	2025-06-07 16:48:08.731074-07
\.


--
-- TOC entry 4809 (class 2606 OID 25291)
-- Name: access_logs access_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.access_logs
    ADD CONSTRAINT access_logs_pkey PRIMARY KEY (log_id);


--
-- TOC entry 4837 (class 2606 OID 26226)
-- Name: data_sharing_permissions data_sharing_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_sharing_permissions
    ADD CONSTRAINT data_sharing_permissions_pkey PRIMARY KEY (permission_id);


--
-- TOC entry 4821 (class 2606 OID 25785)
-- Name: emergency_contacts emergency_contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emergency_contacts
    ADD CONSTRAINT emergency_contacts_pkey PRIMARY KEY (contact_id);


--
-- TOC entry 4826 (class 2606 OID 25802)
-- Name: insurance_plans insurance_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_plans
    ADD CONSTRAINT insurance_plans_pkey PRIMARY KEY (insurance_id);


--
-- TOC entry 4807 (class 2606 OID 25277)
-- Name: patient_consents patient_consents_pkey; Type: CONSTRAINT; Schema: public; Owner: abena_user
--

ALTER TABLE ONLY public.patient_consents
    ADD CONSTRAINT patient_consents_pkey PRIMARY KEY (consent_id);


--
-- TOC entry 4830 (class 2606 OID 25817)
-- Name: patient_documents patient_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient_documents
    ADD CONSTRAINT patient_documents_pkey PRIMARY KEY (document_id);


--
-- TOC entry 4833 (class 2606 OID 25834)
-- Name: patient_preferences patient_preferences_patient_id_preference_category_preferen_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient_preferences
    ADD CONSTRAINT patient_preferences_patient_id_preference_category_preferen_key UNIQUE (patient_id, preference_category, preference_key);


--
-- TOC entry 4835 (class 2606 OID 25832)
-- Name: patient_preferences patient_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient_preferences
    ADD CONSTRAINT patient_preferences_pkey PRIMARY KEY (preference_id);


--
-- TOC entry 4817 (class 2606 OID 25774)
-- Name: patients patients_medical_record_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_medical_record_number_key UNIQUE (medical_record_number);


--
-- TOC entry 4819 (class 2606 OID 25772)
-- Name: patients patients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_pkey PRIMARY KEY (patient_id);


--
-- TOC entry 4810 (class 1259 OID 25374)
-- Name: idx_access_logs_accessed_at; Type: INDEX; Schema: public; Owner: abena_user
--

CREATE INDEX idx_access_logs_accessed_at ON public.access_logs USING btree (accessed_at);


--
-- TOC entry 4811 (class 1259 OID 25373)
-- Name: idx_access_logs_patient_id; Type: INDEX; Schema: public; Owner: abena_user
--

CREATE INDEX idx_access_logs_patient_id ON public.access_logs USING btree (patient_id);


--
-- TOC entry 4838 (class 1259 OID 26239)
-- Name: idx_data_sharing_active_permissions; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_active_permissions ON public.data_sharing_permissions USING btree (permission_status, effective_date, expiration_date) WHERE ((permission_status)::text = 'active'::text);


--
-- TOC entry 4839 (class 1259 OID 26235)
-- Name: idx_data_sharing_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_created_at ON public.data_sharing_permissions USING btree (created_at DESC);


--
-- TOC entry 4840 (class 1259 OID 26232)
-- Name: idx_data_sharing_effective_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_effective_date ON public.data_sharing_permissions USING btree (effective_date);


--
-- TOC entry 4841 (class 1259 OID 26233)
-- Name: idx_data_sharing_expiration_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_expiration_date ON public.data_sharing_permissions USING btree (expiration_date);


--
-- TOC entry 4842 (class 1259 OID 26234)
-- Name: idx_data_sharing_granted_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_granted_date ON public.data_sharing_permissions USING btree (granted_date DESC);


--
-- TOC entry 4843 (class 1259 OID 26227)
-- Name: idx_data_sharing_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_patient_id ON public.data_sharing_permissions USING btree (patient_id);


--
-- TOC entry 4844 (class 1259 OID 26236)
-- Name: idx_data_sharing_patient_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_patient_status ON public.data_sharing_permissions USING btree (patient_id, permission_status);


--
-- TOC entry 4845 (class 1259 OID 26237)
-- Name: idx_data_sharing_patient_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_patient_type ON public.data_sharing_permissions USING btree (patient_id, permission_type);


--
-- TOC entry 4846 (class 1259 OID 26229)
-- Name: idx_data_sharing_permission_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_permission_status ON public.data_sharing_permissions USING btree (permission_status);


--
-- TOC entry 4847 (class 1259 OID 26228)
-- Name: idx_data_sharing_permission_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_permission_type ON public.data_sharing_permissions USING btree (permission_type);


--
-- TOC entry 4848 (class 1259 OID 26231)
-- Name: idx_data_sharing_recipient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_recipient_id ON public.data_sharing_permissions USING btree (recipient_id);


--
-- TOC entry 4849 (class 1259 OID 26238)
-- Name: idx_data_sharing_recipient_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_recipient_status ON public.data_sharing_permissions USING btree (recipient_id, permission_status);


--
-- TOC entry 4850 (class 1259 OID 26230)
-- Name: idx_data_sharing_recipient_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_data_sharing_recipient_type ON public.data_sharing_permissions USING btree (recipient_type);


--
-- TOC entry 4822 (class 1259 OID 25844)
-- Name: idx_emergency_contacts_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_emergency_contacts_patient_id ON public.emergency_contacts USING btree (patient_id);


--
-- TOC entry 4823 (class 1259 OID 25846)
-- Name: idx_insurance_plans_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_insurance_plans_active ON public.insurance_plans USING btree (is_active);


--
-- TOC entry 4824 (class 1259 OID 25845)
-- Name: idx_insurance_plans_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_insurance_plans_patient_id ON public.insurance_plans USING btree (patient_id);


--
-- TOC entry 4827 (class 1259 OID 25847)
-- Name: idx_patient_documents_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_patient_documents_patient_id ON public.patient_documents USING btree (patient_id);


--
-- TOC entry 4828 (class 1259 OID 25848)
-- Name: idx_patient_documents_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_patient_documents_type ON public.patient_documents USING btree (document_type);


--
-- TOC entry 4831 (class 1259 OID 25849)
-- Name: idx_patient_preferences_patient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_patient_preferences_patient_id ON public.patient_preferences USING btree (patient_id);


--
-- TOC entry 4812 (class 1259 OID 25843)
-- Name: idx_patients_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_patients_active ON public.patients USING btree (is_active);


--
-- TOC entry 4813 (class 1259 OID 25842)
-- Name: idx_patients_dob; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_patients_dob ON public.patients USING btree (date_of_birth);


--
-- TOC entry 4814 (class 1259 OID 25840)
-- Name: idx_patients_mrn; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_patients_mrn ON public.patients USING btree (medical_record_number);


--
-- TOC entry 4815 (class 1259 OID 25841)
-- Name: idx_patients_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_patients_name ON public.patients USING btree (last_name, first_name);


--
-- TOC entry 4859 (class 2620 OID 26243)
-- Name: data_sharing_permissions check_data_sharing_expiration; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER check_data_sharing_expiration BEFORE INSERT OR UPDATE ON public.data_sharing_permissions FOR EACH ROW EXECUTE FUNCTION public.check_permission_expiration();


--
-- TOC entry 4860 (class 2620 OID 26241)
-- Name: data_sharing_permissions data_sharing_update_timestamp; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER data_sharing_update_timestamp BEFORE UPDATE ON public.data_sharing_permissions FOR EACH ROW EXECUTE FUNCTION public.update_data_sharing_timestamp();


--
-- TOC entry 4856 (class 2620 OID 25851)
-- Name: emergency_contacts update_emergency_contacts_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_emergency_contacts_updated_at BEFORE UPDATE ON public.emergency_contacts FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4857 (class 2620 OID 25852)
-- Name: insurance_plans update_insurance_plans_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_insurance_plans_updated_at BEFORE UPDATE ON public.insurance_plans FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4858 (class 2620 OID 25853)
-- Name: patient_preferences update_patient_preferences_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_patient_preferences_updated_at BEFORE UPDATE ON public.patient_preferences FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4855 (class 2620 OID 25850)
-- Name: patients update_patients_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON public.patients FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4851 (class 2606 OID 25786)
-- Name: emergency_contacts emergency_contacts_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emergency_contacts
    ADD CONSTRAINT emergency_contacts_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(patient_id) ON DELETE CASCADE;


--
-- TOC entry 4852 (class 2606 OID 25803)
-- Name: insurance_plans insurance_plans_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_plans
    ADD CONSTRAINT insurance_plans_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(patient_id) ON DELETE CASCADE;


--
-- TOC entry 4853 (class 2606 OID 25818)
-- Name: patient_documents patient_documents_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient_documents
    ADD CONSTRAINT patient_documents_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(patient_id) ON DELETE CASCADE;


--
-- TOC entry 4854 (class 2606 OID 25835)
-- Name: patient_preferences patient_preferences_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient_preferences
    ADD CONSTRAINT patient_preferences_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(patient_id) ON DELETE CASCADE;


--
-- TOC entry 5019 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO abena_user;


--
-- TOC entry 2088 (class 826 OID 25255)
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: abena_user
--

ALTER DEFAULT PRIVILEGES FOR ROLE abena_user IN SCHEMA public GRANT ALL ON SEQUENCES TO abena_user;


--
-- TOC entry 2087 (class 826 OID 25254)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: abena_user
--

ALTER DEFAULT PRIVILEGES FOR ROLE abena_user IN SCHEMA public GRANT ALL ON TABLES TO abena_user;


-- Completed on 2025-07-04 07:41:56

--
-- PostgreSQL database dump complete
--

