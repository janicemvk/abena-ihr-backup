-- Abena IHR Unified Data Service - Database Initialization
-- ========================================================
-- 
-- This script initializes the unified database with:
-- - Database extensions
-- - Initial configuration
-- - Sample data for testing
--
-- Run this script after the master schema is applied

-- ======================================================
-- DATABASE CONFIGURATION
-- ======================================================

-- Set timezone
SET timezone = 'UTC';

-- Enable required extensions (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ======================================================
-- SAMPLE ORGANIZATIONS
-- ======================================================

INSERT INTO organizations (organization_id, name, type, tax_id, npi, address_line1, city, state, zip_code, phone, email, website) VALUES
(
    uuid_generate_v4(),
    'Abena General Hospital',
    'hospital',
    '12-3456789',
    '1234567890',
    '1234 Healthcare Blvd',
    'Springfield',
    'IL',
    '62701',
    '(217) 555-0123',
    'info@abenahealth.org',
    'https://www.abenahealth.org'
),
(
    uuid_generate_v4(),
    'Abena Medical Center',
    'clinic',
    '98-7654321',
    '0987654321',
    '5678 Medical Drive',
    'Springfield',
    'IL',
    '62702',
    '(217) 555-0456',
    'contact@abenamedical.com',
    'https://www.abenamedical.com'
),
(
    uuid_generate_v4(),
    'Abena Laboratory Services',
    'laboratory',
    '45-6789012',
    '4567890123',
    '9012 Lab Street',
    'Springfield',
    'IL',
    '62703',
    '(217) 555-0789',
    'lab@abenalabs.com',
    'https://www.abenalabs.com'
),
(
    uuid_generate_v4(),
    'Abena Pharmacy',
    'pharmacy',
    '34-5678901',
    '3456789012',
    '3456 Pharmacy Ave',
    'Springfield',
    'IL',
    '62704',
    '(217) 555-0321',
    'pharmacy@abenapharm.com',
    'https://www.abenapharm.com'
);

-- ======================================================
-- SAMPLE PROVIDERS
-- ======================================================

INSERT INTO providers (provider_id, npi, first_name, last_name, title, specialty, license_number, license_state, email, phone, organization_id) VALUES
(
    uuid_generate_v4(),
    '1234567890',
    'Dr. Sarah',
    'Johnson',
    'MD',
    'Internal Medicine',
    'MD123456',
    'IL',
    'sarah.johnson@abenahealth.org',
    '(217) 555-0101',
    (SELECT organization_id FROM organizations WHERE name = 'Abena General Hospital' LIMIT 1)
),
(
    uuid_generate_v4(),
    '2345678901',
    'Dr. Michael',
    'Chen',
    'MD',
    'Cardiology',
    'MD234567',
    'IL',
    'michael.chen@abenahealth.org',
    '(217) 555-0102',
    (SELECT organization_id FROM organizations WHERE name = 'Abena General Hospital' LIMIT 1)
),
(
    uuid_generate_v4(),
    '3456789012',
    'Dr. Emily',
    'Rodriguez',
    'MD',
    'Pediatrics',
    'MD345678',
    'IL',
    'emily.rodriguez@abenamedical.com',
    '(217) 555-0103',
    (SELECT organization_id FROM organizations WHERE name = 'Abena Medical Center' LIMIT 1)
),
(
    uuid_generate_v4(),
    '4567890123',
    'Dr. James',
    'Wilson',
    'MD',
    'Emergency Medicine',
    'MD456789',
    'IL',
    'james.wilson@abenahealth.org',
    '(217) 555-0104',
    (SELECT organization_id FROM organizations WHERE name = 'Abena General Hospital' LIMIT 1)
),
(
    uuid_generate_v4(),
    '5678901234',
    'Dr. Lisa',
    'Thompson',
    'MD',
    'Family Medicine',
    'MD567890',
    'IL',
    'lisa.thompson@abenamedical.com',
    '(217) 555-0105',
    (SELECT organization_id FROM organizations WHERE name = 'Abena Medical Center' LIMIT 1)
);

-- ======================================================
-- SAMPLE PATIENTS
-- ======================================================

INSERT INTO patients (patient_id, mrn, first_name, last_name, date_of_birth, gender, ethnicity, race, marital_status, primary_language, emergency_contact_name, emergency_contact_phone, emergency_contact_relationship, insurance_provider, insurance_policy_number) VALUES
(
    uuid_generate_v4(),
    'MRN001',
    'John',
    'Smith',
    '1985-03-15',
    'male',
    'Hispanic',
    'White',
    'married',
    'English',
    'Mary Smith',
    '(217) 555-1001',
    'spouse',
    'Blue Cross Blue Shield',
    'BCBS123456789'
),
(
    uuid_generate_v4(),
    'MRN002',
    'Jane',
    'Doe',
    '1992-07-22',
    'female',
    'Non-Hispanic',
    'Asian',
    'single',
    'English',
    'Robert Doe',
    '(217) 555-1002',
    'father',
    'Aetna',
    'AETNA987654321'
),
(
    uuid_generate_v4(),
    'MRN003',
    'Robert',
    'Johnson',
    '1978-11-08',
    'male',
    'Non-Hispanic',
    'Black',
    'divorced',
    'English',
    'Jennifer Johnson',
    '(217) 555-1003',
    'sister',
    'Cigna',
    'CIGNA456789123'
),
(
    uuid_generate_v4(),
    'MRN004',
    'Maria',
    'Garcia',
    '1990-04-30',
    'female',
    'Hispanic',
    'Hispanic',
    'married',
    'Spanish',
    'Carlos Garcia',
    '(217) 555-1004',
    'spouse',
    'UnitedHealth',
    'UNH789123456'
),
(
    uuid_generate_v4(),
    'MRN005',
    'David',
    'Brown',
    '1965-12-14',
    'male',
    'Non-Hispanic',
    'White',
    'married',
    'English',
    'Patricia Brown',
    '(217) 555-1005',
    'spouse',
    'Medicare',
    'MEDICARE123456'
);

-- ======================================================
-- SAMPLE ENCOUNTERS
-- ======================================================

INSERT INTO encounters (encounter_id, patient_id, provider_id, organization_id, encounter_type, encounter_class, status, start_date, end_date, reason_code, reason_text, priority) VALUES
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1),
    (SELECT provider_id FROM providers WHERE last_name = 'Johnson' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena General Hospital' LIMIT 1),
    'outpatient',
    'ambulatory',
    'finished',
    '2024-01-15 09:00:00+00',
    '2024-01-15 10:30:00+00',
    'Z00.00',
    'Annual physical examination',
    'routine'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN002' LIMIT 1),
    (SELECT provider_id FROM providers WHERE last_name = 'Rodriguez' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena Medical Center' LIMIT 1),
    'outpatient',
    'ambulatory',
    'finished',
    '2024-01-16 14:00:00+00',
    '2024-01-16 15:15:00+00',
    'R50.9',
    'Fever and cough',
    'urgent'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN003' LIMIT 1),
    (SELECT provider_id FROM providers WHERE last_name = 'Chen' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena General Hospital' LIMIT 1),
    'outpatient',
    'ambulatory',
    'finished',
    '2024-01-17 11:00:00+00',
    '2024-01-17 12:45:00+00',
    'I10',
    'Hypertension follow-up',
    'routine'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN004' LIMIT 1),
    (SELECT provider_id FROM providers WHERE last_name = 'Thompson' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena Medical Center' LIMIT 1),
    'outpatient',
    'ambulatory',
    'finished',
    '2024-01-18 16:00:00+00',
    '2024-01-18 17:00:00+00',
    'E11.9',
    'Diabetes management',
    'routine'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN005' LIMIT 1),
    (SELECT provider_id FROM providers WHERE last_name = 'Wilson' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena General Hospital' LIMIT 1),
    'emergency',
    'emergency',
    'finished',
    '2024-01-19 08:30:00+00',
    '2024-01-19 11:00:00+00',
    'R07.9',
    'Chest pain',
    'emergent'
);

-- ======================================================
-- SAMPLE DIAGNOSES
-- ======================================================

INSERT INTO diagnoses (diagnosis_id, patient_id, encounter_id, diagnosis_code, diagnosis_text, diagnosis_type, status, onset_date, severity) VALUES
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1) LIMIT 1),
    'Z00.00',
    'Encounter for general adult medical examination without abnormal findings',
    'primary',
    'active',
    '2024-01-15',
    'mild'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN002' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN002' LIMIT 1) LIMIT 1),
    'J06.9',
    'Acute upper respiratory infection, unspecified',
    'primary',
    'active',
    '2024-01-16',
    'moderate'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN003' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN003' LIMIT 1) LIMIT 1),
    'I10',
    'Essential (primary) hypertension',
    'primary',
    'chronic',
    '2020-03-15',
    'moderate'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN004' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN004' LIMIT 1) LIMIT 1),
    'E11.9',
    'Type 2 diabetes mellitus without complications',
    'primary',
    'chronic',
    '2018-06-10',
    'moderate'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN005' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN005' LIMIT 1) LIMIT 1),
    'I20.9',
    'Angina pectoris, unspecified',
    'primary',
    'active',
    '2024-01-19',
    'severe'
);

-- ======================================================
-- SAMPLE MEDICATIONS
-- ======================================================

INSERT INTO medications (medication_id, patient_id, encounter_id, medication_name, generic_name, ndc_code, dosage_form, strength, route, frequency, quantity, quantity_unit, prescribed_date, start_date, status, prescribed_by) VALUES
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN003' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN003' LIMIT 1) LIMIT 1),
    'Lisinopril',
    'Lisinopril',
    '00071-1010-01',
    'tablet',
    '10mg',
    'oral',
    'daily',
    30,
    'tablets',
    '2024-01-17',
    '2024-01-17',
    'active',
    (SELECT provider_id FROM providers WHERE last_name = 'Chen' LIMIT 1)
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN004' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN004' LIMIT 1) LIMIT 1),
    'Metformin',
    'Metformin',
    '00071-1020-01',
    'tablet',
    '500mg',
    'oral',
    'twice daily',
    60,
    'tablets',
    '2024-01-18',
    '2024-01-18',
    'active',
    (SELECT provider_id FROM providers WHERE last_name = 'Thompson' LIMIT 1)
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN002' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN002' LIMIT 1) LIMIT 1),
    'Amoxicillin',
    'Amoxicillin',
    '00071-1030-01',
    'capsule',
    '500mg',
    'oral',
    'three times daily',
    21,
    'capsules',
    '2024-01-16',
    '2024-01-16',
    'active',
    (SELECT provider_id FROM providers WHERE last_name = 'Rodriguez' LIMIT 1)
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN005' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN005' LIMIT 1) LIMIT 1),
    'Nitroglycerin',
    'Nitroglycerin',
    '00071-1040-01',
    'tablet',
    '0.4mg',
    'sublingual',
    'as needed',
    30,
    'tablets',
    '2024-01-19',
    '2024-01-19',
    'active',
    (SELECT provider_id FROM providers WHERE last_name = 'Wilson' LIMIT 1)
);

-- ======================================================
-- SAMPLE VITAL SIGNS
-- ======================================================

INSERT INTO vital_signs (vital_sign_id, patient_id, encounter_id, vital_sign_type, value, unit, systolic, diastolic, measurement_date, measured_by, method, position) VALUES
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1) LIMIT 1),
    'blood_pressure',
    NULL,
    'mmHg',
    120,
    80,
    '2024-01-15 09:15:00+00',
    (SELECT provider_id FROM providers WHERE last_name = 'Johnson' LIMIT 1),
    'automated',
    'sitting'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1) LIMIT 1),
    'heart_rate',
    72,
    'bpm',
    NULL,
    NULL,
    '2024-01-15 09:16:00+00',
    (SELECT provider_id FROM providers WHERE last_name = 'Johnson' LIMIT 1),
    'automated',
    'sitting'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1) LIMIT 1),
    'temperature',
    98.6,
    'F',
    NULL,
    NULL,
    '2024-01-15 09:17:00+00',
    (SELECT provider_id FROM providers WHERE last_name = 'Johnson' LIMIT 1),
    'automated',
    'sitting'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN003' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN003' LIMIT 1) LIMIT 1),
    'blood_pressure',
    NULL,
    'mmHg',
    145,
    95,
    '2024-01-17 11:15:00+00',
    (SELECT provider_id FROM providers WHERE last_name = 'Chen' LIMIT 1),
    'automated',
    'sitting'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN005' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN005' LIMIT 1) LIMIT 1),
    'blood_pressure',
    NULL,
    'mmHg',
    160,
    100,
    '2024-01-19 08:45:00+00',
    (SELECT provider_id FROM providers WHERE last_name = 'Wilson' LIMIT 1),
    'automated',
    'sitting'
);

-- ======================================================
-- SAMPLE LAB RESULTS
-- ======================================================

INSERT INTO lab_results (lab_result_id, patient_id, encounter_id, test_name, test_code, result_value, result_numeric, unit, reference_range_low, reference_range_high, reference_range_text, abnormal_flag, result_status, specimen_type, collection_date, result_date, ordering_provider, performing_lab) VALUES
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1) LIMIT 1),
    'Complete Blood Count',
    '58410-2',
    'Normal',
    12.5,
    '10^9/L',
    4.5,
    11.0,
    '4.5-11.0 x10^9/L',
    'high',
    'final',
    'blood',
    '2024-01-15 09:30:00+00',
    '2024-01-15 14:00:00+00',
    (SELECT provider_id FROM providers WHERE last_name = 'Johnson' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena Laboratory Services' LIMIT 1)
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN004' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN004' LIMIT 1) LIMIT 1),
    'Hemoglobin A1c',
    '4548-4',
    'Elevated',
    8.2,
    '%',
    4.0,
    5.6,
    '4.0-5.6%',
    'high',
    'final',
    'blood',
    '2024-01-18 16:30:00+00',
    '2024-01-18 18:00:00+00',
    (SELECT provider_id FROM providers WHERE last_name = 'Thompson' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena Laboratory Services' LIMIT 1)
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN003' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN003' LIMIT 1) LIMIT 1),
    'Basic Metabolic Panel',
    '24323-8',
    'Normal',
    1.1,
    'mg/dL',
    0.6,
    1.2,
    '0.6-1.2 mg/dL',
    'normal',
    'final',
    'blood',
    '2024-01-17 11:30:00+00',
    '2024-01-17 13:00:00+00',
    (SELECT provider_id FROM providers WHERE last_name = 'Chen' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena Laboratory Services' LIMIT 1)
);

-- ======================================================
-- SAMPLE ALLERGIES
-- ======================================================

INSERT INTO allergies (allergy_id, patient_id, allergen_name, allergen_type, reaction, severity, onset_date, status) VALUES
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN002' LIMIT 1),
    'Penicillin',
    'drug',
    'Rash and hives',
    'moderate',
    '2015-03-10',
    'active'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN004' LIMIT 1),
    'Peanuts',
    'food',
    'Anaphylaxis',
    'severe',
    '1995-08-15',
    'active'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN005' LIMIT 1),
    'Sulfa drugs',
    'drug',
    'Nausea and vomiting',
    'mild',
    '2010-11-20',
    'active'
);

-- ======================================================
-- SAMPLE CLINICAL NOTES
-- ======================================================

INSERT INTO clinical_notes (note_id, patient_id, encounter_id, note_type, note_title, note_content, author_id, authored_date, status, confidentiality_level) VALUES
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1) LIMIT 1),
    'progress_note',
    'Annual Physical Examination',
    'Patient presents for annual physical examination. Vital signs are within normal limits. Physical examination reveals no significant abnormalities. Patient reports feeling well with no new complaints. All systems reviewed and found to be normal. Patient is advised to continue current lifestyle and return in one year for follow-up.',
    (SELECT provider_id FROM providers WHERE last_name = 'Johnson' LIMIT 1),
    '2024-01-15 10:00:00+00',
    'final',
    'normal'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN002' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN002' LIMIT 1) LIMIT 1),
    'progress_note',
    'Upper Respiratory Infection',
    'Patient presents with fever (101.2F), cough, and sore throat for 3 days. Physical examination reveals mild pharyngeal erythema and clear lungs. Diagnosis: Acute upper respiratory infection. Prescribed amoxicillin 500mg TID for 7 days. Patient advised to rest and increase fluid intake.',
    (SELECT provider_id FROM providers WHERE last_name = 'Rodriguez' LIMIT 1),
    '2024-01-16 14:30:00+00',
    'final',
    'normal'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN003' LIMIT 1),
    (SELECT encounter_id FROM encounters WHERE patient_id = (SELECT patient_id FROM patients WHERE mrn = 'MRN003' LIMIT 1) LIMIT 1),
    'progress_note',
    'Hypertension Follow-up',
    'Patient returns for hypertension follow-up. Blood pressure remains elevated at 145/95 mmHg despite current medication. Patient reports good medication adherence. Increased lisinopril to 10mg daily. Advised to monitor blood pressure at home and return in 2 weeks for recheck.',
    (SELECT provider_id FROM providers WHERE last_name = 'Chen' LIMIT 1),
    '2024-01-17 12:00:00+00',
    'final',
    'normal'
);

-- ======================================================
-- SAMPLE PATIENT-PROVIDER RELATIONSHIPS
-- ======================================================

INSERT INTO patient_provider_relationships (relationship_id, patient_id, provider_id, relationship_type, start_date, status) VALUES
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN001' LIMIT 1),
    (SELECT provider_id FROM providers WHERE last_name = 'Johnson' LIMIT 1),
    'primary_care',
    '2020-01-15',
    'active'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN002' LIMIT 1),
    (SELECT provider_id FROM providers WHERE last_name = 'Rodriguez' LIMIT 1),
    'primary_care',
    '2018-06-10',
    'active'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN003' LIMIT 1),
    (SELECT provider_id FROM providers WHERE last_name = 'Chen' LIMIT 1),
    'specialist',
    '2020-03-15',
    'active'
),
(
    uuid_generate_v4(),
    (SELECT patient_id FROM patients WHERE mrn = 'MRN004' LIMIT 1),
    (SELECT provider_id FROM providers WHERE last_name = 'Thompson' LIMIT 1),
    'primary_care',
    '2018-06-10',
    'active'
);

-- ======================================================
-- SAMPLE PROVIDER-ORGANIZATION RELATIONSHIPS
-- ======================================================

INSERT INTO provider_organization_relationships (relationship_id, provider_id, organization_id, relationship_type, start_date, status) VALUES
(
    uuid_generate_v4(),
    (SELECT provider_id FROM providers WHERE last_name = 'Johnson' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena General Hospital' LIMIT 1),
    'employee',
    '2015-01-01',
    'active'
),
(
    uuid_generate_v4(),
    (SELECT provider_id FROM providers WHERE last_name = 'Chen' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena General Hospital' LIMIT 1),
    'employee',
    '2017-03-01',
    'active'
),
(
    uuid_generate_v4(),
    (SELECT provider_id FROM providers WHERE last_name = 'Rodriguez' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena Medical Center' LIMIT 1),
    'employee',
    '2019-08-15',
    'active'
),
(
    uuid_generate_v4(),
    (SELECT provider_id FROM providers WHERE last_name = 'Wilson' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena General Hospital' LIMIT 1),
    'employee',
    '2016-11-01',
    'active'
),
(
    uuid_generate_v4(),
    (SELECT provider_id FROM providers WHERE last_name = 'Thompson' LIMIT 1),
    (SELECT organization_id FROM organizations WHERE name = 'Abena Medical Center' LIMIT 1),
    'employee',
    '2020-01-01',
    'active'
);

-- ======================================================
-- INITIALIZATION COMPLETE
-- ======================================================

-- Log successful initialization
INSERT INTO data_quality_metrics (metric_id, table_name, metric_name, metric_value, metric_date) VALUES
(
    uuid_generate_v4(),
    'patients',
    'record_count',
    5,
    CURRENT_DATE
),
(
    uuid_generate_v4(),
    'providers',
    'record_count',
    5,
    CURRENT_DATE
),
(
    uuid_generate_v4(),
    'organizations',
    'record_count',
    4,
    CURRENT_DATE
),
(
    uuid_generate_v4(),
    'encounters',
    'record_count',
    5,
    CURRENT_DATE
);

-- Print initialization summary
DO $$
BEGIN
    RAISE NOTICE 'Abena IHR Unified Data Service initialization completed successfully!';
    RAISE NOTICE 'Sample data created:';
    RAISE NOTICE '- % organizations', (SELECT COUNT(*) FROM organizations);
    RAISE NOTICE '- % providers', (SELECT COUNT(*) FROM providers);
    RAISE NOTICE '- % patients', (SELECT COUNT(*) FROM patients);
    RAISE NOTICE '- % encounters', (SELECT COUNT(*) FROM encounters);
    RAISE NOTICE '- % diagnoses', (SELECT COUNT(*) FROM diagnoses);
    RAISE NOTICE '- % medications', (SELECT COUNT(*) FROM medications);
    RAISE NOTICE '- % vital signs', (SELECT COUNT(*) FROM vital_signs);
    RAISE NOTICE '- % lab results', (SELECT COUNT(*) FROM lab_results);
    RAISE NOTICE '- % allergies', (SELECT COUNT(*) FROM allergies);
    RAISE NOTICE '- % clinical notes', (SELECT COUNT(*) FROM clinical_notes);
END $$; 