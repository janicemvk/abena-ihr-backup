-- Add sample lab results data
INSERT INTO lab_results (
    patient_id,
    test_name,
    test_code,
    result_value,
    result_text,
    unit,
    reference_range,
    abnormal_flag,
    test_date,
    lab_name,
    created_at
) VALUES
-- John Doe's lab results
(
    '444ed30b-defc-47c9-93ca-5b522828d7ec', -- John Doe's patient_id
    'Complete Blood Count (CBC)',
    'CBC001',
    12.5,
    'Normal',
    'g/dL',
    '11.0-15.0',
    'N',
    '2024-01-15 10:30:00',
    'LabCorp',
    '2024-01-15 10:30:00'
),
(
    '444ed30b-defc-47c9-93ca-5b522828d7ec', -- John Doe's patient_id
    'Lipid Panel',
    'LIPID001',
    180,
    'Normal',
    'mg/dL',
    '<200',
    'N',
    '2024-01-10 14:15:00',
    'Quest Diagnostics',
    '2024-01-10 14:15:00'
),
(
    '444ed30b-defc-47c9-93ca-5b522828d7ec', -- John Doe's patient_id
    'Thyroid Function Test',
    'THYROID001',
    2.5,
    'Normal',
    'mIU/L',
    '0.4-4.0',
    'N',
    '2024-01-05 09:45:00',
    'LabCorp',
    '2024-01-05 09:45:00'
),
-- Alice Johnson's lab results
(
    '357af4b8-8032-4dbd-b50b-d2650f2b70e2', -- Alice Johnson's patient_id
    'Complete Blood Count (CBC)',
    'CBC002',
    11.8,
    'Normal',
    'g/dL',
    '11.0-15.0',
    'N',
    '2024-01-12 11:20:00',
    'Quest Diagnostics',
    '2024-01-12 11:20:00'
),
(
    '357af4b8-8032-4dbd-b50b-d2650f2b70e2', -- Alice Johnson's patient_id
    'Comprehensive Metabolic Panel',
    'CMP001',
    95,
    'Normal',
    'mg/dL',
    '70-100',
    'N',
    '2024-01-08 13:30:00',
    'LabCorp',
    '2024-01-08 13:30:00'
),
-- Emily Davis's lab results
(
    '151733f9-6109-4053-bfc8-af0237c3eded', -- Emily Davis's patient_id
    'Hemoglobin A1c',
    'HBA1C001',
    6.2,
    'Elevated',
    '%',
    '<5.7',
    'H',
    '2024-01-20 08:45:00',
    'Quest Diagnostics',
    '2024-01-20 08:45:00'
),
(
    '151733f9-6109-4053-bfc8-af0237c3eded', -- Emily Davis's patient_id
    'Vitamin D, 25-Hydroxy',
    'VITD001',
    18,
    'Low',
    'ng/mL',
    '30-100',
    'L',
    '2024-01-18 10:15:00',
    'LabCorp',
    '2024-01-18 10:15:00'
);
