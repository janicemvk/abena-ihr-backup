-- Add sample documents data
INSERT INTO patient_documents (
    patient_id,
    document_name,
    document_type,
    file_path,
    file_size,
    mime_type,
    upload_date,
    is_confidential,
    tags
) VALUES
-- John Doe's documents
(
    '444ed30b-defc-47c9-93ca-5b522828d7ec', -- John Doe's patient_id
    'Lab Results - Blood Test.pdf',
    'lab_results',
    'uploads/documents/lab_results_blood_test.pdf',
    245760,
    'application/pdf',
    '2024-01-15 10:30:00',
    false,
    ARRAY['lab', 'blood test', 'results']
),
(
    '444ed30b-defc-47c9-93ca-5b522828d7ec', -- John Doe's patient_id
    'Prescription - Antibiotics.pdf',
    'prescription',
    'uploads/documents/prescription_antibiotics.pdf',
    189440,
    'application/pdf',
    '2024-01-14 14:15:00',
    false,
    ARRAY['prescription', 'antibiotics', 'medication']
),
(
    '444ed30b-defc-47c9-93ca-5b522828d7ec', -- John Doe's patient_id
    'Medical Records Summary.pdf',
    'medical_records',
    'uploads/documents/medical_records_summary.pdf',
    512000,
    'application/pdf',
    '2024-01-13 09:45:00',
    true,
    ARRAY['medical records', 'summary', 'confidential']
),
-- Alice Johnson's documents
(
    '357af4b8-8032-4dbd-b50b-d2650f2b70e2', -- Alice Johnson's patient_id
    'Visit Summary - Cardiology.pdf',
    'visit_summary',
    'uploads/documents/visit_summary_cardiology.pdf',
    320000,
    'application/pdf',
    '2024-01-12 11:20:00',
    false,
    ARRAY['visit summary', 'cardiology', 'consultation']
),
(
    '357af4b8-8032-4dbd-b50b-d2650f2b70e2', -- Alice Johnson's patient_id
    'Lab Results - Cholesterol.pdf',
    'lab_results',
    'uploads/documents/lab_results_cholesterol.pdf',
    198400,
    'application/pdf',
    '2024-01-11 13:30:00',
    false,
    ARRAY['lab', 'cholesterol', 'results']
),
-- Emily Davis's documents
(
    '151733f9-6109-4053-bfc8-af0237c3eded', -- Emily Davis's patient_id
    'Treatment Plan - Diabetes.pdf',
    'treatment_plan',
    'uploads/documents/treatment_plan_diabetes.pdf',
    456000,
    'application/pdf',
    '2024-01-10 08:45:00',
    false,
    ARRAY['treatment plan', 'diabetes', 'management']
),
(
    '151733f9-6109-4053-bfc8-af0237c3eded', -- Emily Davis's patient_id
    'Consent Form - Surgery.pdf',
    'consent_form',
    'uploads/documents/consent_form_surgery.pdf',
    156000,
    'application/pdf',
    '2024-01-09 15:20:00',
    true,
    ARRAY['consent form', 'surgery', 'legal']
);
