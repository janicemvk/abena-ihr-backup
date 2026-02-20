-- Abena Clinical Outcomes - Sample Data Insertion Script
-- This script inserts realistic sample data for testing and demonstration

-- Set search path
SET search_path TO clinical_outcomes, public;

-- ============================================================================
-- Sample Patient Data Insertion
-- ============================================================================

-- Insert sample assessment schedules
INSERT INTO assessment_schedules (patient_id, baseline_date, study_duration_weeks, scheduled_assessments, total_scheduled, total_completed) VALUES
('PATIENT_001', '2024-01-15 09:00:00+00', 52, '[
    {"timing": "baseline", "scheduled_date": "2024-01-15", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life"]},
    {"timing": "week_4", "scheduled_date": "2024-02-12", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage"]},
    {"timing": "week_12", "scheduled_date": "2024-04-08", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life", "treatment_satisfaction"]}
]', 3, 3),
('PATIENT_002', '2024-01-20 10:30:00+00', 52, '[
    {"timing": "baseline", "scheduled_date": "2024-01-20", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life"]},
    {"timing": "week_4", "scheduled_date": "2024-02-17", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage"]},
    {"timing": "week_12", "scheduled_date": "2024-04-13", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life", "treatment_satisfaction"]}
]', 3, 2),
('PATIENT_003', '2024-02-01 14:15:00+00', 52, '[
    {"timing": "baseline", "scheduled_date": "2024-02-01", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage", "quality_of_life"]},
    {"timing": "week_4", "scheduled_date": "2024-02-29", "required_assessments": ["pain_assessment", "womac_assessment", "medication_usage"]}
]', 2, 2);

-- ============================================================================
-- Pain Assessments Sample Data
-- ============================================================================

-- Patient 001 - Baseline
INSERT INTO pain_assessments (
    patient_id, assessment_date, measurement_timing,
    current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference,
    pain_at_rest, pain_with_movement, pain_with_exercise,
    pain_locations, pain_quality, assessor_id, created_by
) VALUES (
    'PATIENT_001', '2024-01-15 09:00:00+00', 'baseline',
    8.0, 7.5, 9.5, 5.0, 8.5,
    6.0, 9.0, 9.5,
    ARRAY['right_knee', 'left_knee'], ARRAY['aching', 'stiffness'],
    'DR_SMITH', 'SYSTEM'
);

-- Patient 001 - Week 4
INSERT INTO pain_assessments (
    patient_id, assessment_date, measurement_timing,
    current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference,
    pain_at_rest, pain_with_movement, pain_with_exercise,
    pain_locations, pain_quality, assessor_id, created_by
) VALUES (
    'PATIENT_001', '2024-02-12 09:00:00+00', 'week_4',
    6.5, 6.0, 8.0, 4.0, 6.5,
    4.5, 7.5, 8.0,
    ARRAY['right_knee', 'left_knee'], ARRAY['aching'],
    'DR_SMITH', 'SYSTEM'
);

-- Patient 001 - Week 12
INSERT INTO pain_assessments (
    patient_id, assessment_date, measurement_timing,
    current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference,
    pain_at_rest, pain_with_movement, pain_with_exercise,
    pain_locations, pain_quality, assessor_id, created_by
) VALUES (
    'PATIENT_001', '2024-04-08 09:00:00+00', 'week_12',
    5.0, 4.5, 6.5, 3.0, 5.0,
    3.0, 6.0, 6.5,
    ARRAY['right_knee'], ARRAY['mild_aching'],
    'DR_SMITH', 'SYSTEM'
);

-- Patient 002 - Baseline
INSERT INTO pain_assessments (
    patient_id, assessment_date, measurement_timing,
    current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference,
    pain_at_rest, pain_with_movement, pain_with_exercise,
    pain_locations, pain_quality, assessor_id, created_by
) VALUES (
    'PATIENT_002', '2024-01-20 10:30:00+00', 'baseline',
    9.0, 8.5, 10.0, 6.0, 9.0,
    7.0, 9.5, 10.0,
    ARRAY['lower_back', 'right_hip'], ARRAY['sharp', 'radiating'],
    'DR_JOHNSON', 'SYSTEM'
);

-- Patient 002 - Week 4
INSERT INTO pain_assessments (
    patient_id, assessment_date, measurement_timing,
    current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference,
    pain_at_rest, pain_with_movement, pain_with_exercise,
    pain_locations, pain_quality, assessor_id, created_by
) VALUES (
    'PATIENT_002', '2024-02-17 10:30:00+00', 'week_4',
    7.5, 7.0, 8.5, 5.5, 7.5,
    5.5, 8.0, 8.5,
    ARRAY['lower_back', 'right_hip'], ARRAY['dull', 'aching'],
    'DR_JOHNSON', 'SYSTEM'
);

-- Patient 003 - Baseline
INSERT INTO pain_assessments (
    patient_id, assessment_date, measurement_timing,
    current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference,
    pain_at_rest, pain_with_movement, pain_with_exercise,
    pain_locations, pain_quality, assessor_id, created_by
) VALUES (
    'PATIENT_003', '2024-02-01 14:15:00+00', 'baseline',
    6.5, 6.0, 8.0, 4.5, 6.5,
    4.0, 7.0, 8.0,
    ARRAY['left_shoulder', 'neck'], ARRAY['stiffness', 'aching'],
    'DR_WILLIAMS', 'SYSTEM'
);

-- Patient 003 - Week 4
INSERT INTO pain_assessments (
    patient_id, assessment_date, measurement_timing,
    current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference,
    pain_at_rest, pain_with_movement, pain_with_exercise,
    pain_locations, pain_quality, assessor_id, created_by
) VALUES (
    'PATIENT_003', '2024-02-29 14:15:00+00', 'week_4',
    5.0, 4.5, 6.0, 3.5, 5.0,
    2.5, 5.5, 6.0,
    ARRAY['left_shoulder'], ARRAY['mild_stiffness'],
    'DR_WILLIAMS', 'SYSTEM'
);

-- ============================================================================
-- WOMAC Assessments Sample Data
-- ============================================================================

-- Patient 001 - Baseline WOMAC
INSERT INTO womac_assessments (
    patient_id, assessment_date, measurement_timing,
    -- Pain subscale
    pain_walking, pain_stairs, pain_night_bed, pain_sitting, pain_standing,
    -- Stiffness subscale
    stiffness_waking, stiffness_later_day,
    -- Physical function subscale
    function_stairs_down, function_stairs_up, function_rising_sitting, function_standing,
    function_bending, function_walking_flat, function_getting_in_out_car, function_shopping,
    function_socks, function_rising_bed, function_socks_off, function_lying_bed,
    function_bath_shower, function_sitting, function_toilet, function_heavy_domestic, function_light_domestic,
    assessor_id, created_by
) VALUES (
    'PATIENT_001', '2024-01-15 09:00:00+00', 'baseline',
    -- Pain scores (0-4 scale)
    3, 3, 2, 2, 3,
    -- Stiffness scores
    3, 2,
    -- Function scores
    3, 3, 2, 3, 3, 2, 3, 2, 3, 2, 2, 2, 2, 2, 3, 2,
    'DR_SMITH', 'SYSTEM'
);

-- Patient 001 - Week 4 WOMAC
INSERT INTO womac_assessments (
    patient_id, assessment_date, measurement_timing,
    pain_walking, pain_stairs, pain_night_bed, pain_sitting, pain_standing,
    stiffness_waking, stiffness_later_day,
    function_stairs_down, function_stairs_up, function_rising_sitting, function_standing,
    function_bending, function_walking_flat, function_getting_in_out_car, function_shopping,
    function_socks, function_rising_bed, function_socks_off, function_lying_bed,
    function_bath_shower, function_sitting, function_toilet, function_heavy_domestic, function_light_domestic,
    assessor_id, created_by
) VALUES (
    'PATIENT_001', '2024-02-12 09:00:00+00', 'week_4',
    2, 2, 1, 1, 2,
    2, 1,
    2, 2, 1, 2, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1,
    'DR_SMITH', 'SYSTEM'
);

-- Patient 001 - Week 12 WOMAC
INSERT INTO womac_assessments (
    patient_id, assessment_date, measurement_timing,
    pain_walking, pain_stairs, pain_night_bed, pain_sitting, pain_standing,
    stiffness_waking, stiffness_later_day,
    function_stairs_down, function_stairs_up, function_rising_sitting, function_standing,
    function_bending, function_walking_flat, function_getting_in_out_car, function_shopping,
    function_socks, function_rising_bed, function_socks_off, function_lying_bed,
    function_bath_shower, function_sitting, function_toilet, function_heavy_domestic, function_light_domestic,
    assessor_id, created_by
) VALUES (
    'PATIENT_001', '2024-04-08 09:00:00+00', 'week_12',
    1, 1, 0, 0, 1,
    1, 0,
    1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0,
    'DR_SMITH', 'SYSTEM'
);

-- Patient 002 - Baseline WOMAC
INSERT INTO womac_assessments (
    patient_id, assessment_date, measurement_timing,
    pain_walking, pain_stairs, pain_night_bed, pain_sitting, pain_standing,
    stiffness_waking, stiffness_later_day,
    function_stairs_down, function_stairs_up, function_rising_sitting, function_standing,
    function_bending, function_walking_flat, function_getting_in_out_car, function_shopping,
    function_socks, function_rising_bed, function_socks_off, function_lying_bed,
    function_bath_shower, function_sitting, function_toilet, function_heavy_domestic, function_light_domestic,
    assessor_id, created_by
) VALUES (
    'PATIENT_002', '2024-01-20 10:30:00+00', 'baseline',
    4, 4, 3, 3, 4,
    4, 3,
    4, 4, 3, 4, 4, 3, 4, 3, 4, 3, 3, 3, 3, 3, 4, 3,
    'DR_JOHNSON', 'SYSTEM'
);

-- Patient 002 - Week 4 WOMAC
INSERT INTO womac_assessments (
    patient_id, assessment_date, measurement_timing,
    pain_walking, pain_stairs, pain_night_bed, pain_sitting, pain_standing,
    stiffness_waking, stiffness_later_day,
    function_stairs_down, function_stairs_up, function_rising_sitting, function_standing,
    function_bending, function_walking_flat, function_getting_in_out_car, function_shopping,
    function_socks, function_rising_bed, function_socks_off, function_lying_bed,
    function_bath_shower, function_sitting, function_toilet, function_heavy_domestic, function_light_domestic,
    assessor_id, created_by
) VALUES (
    'PATIENT_002', '2024-02-17 10:30:00+00', 'week_4',
    3, 3, 2, 2, 3,
    3, 2,
    3, 3, 2, 3, 3, 2, 3, 2, 3, 2, 2, 2, 2, 2, 3, 2,
    'DR_JOHNSON', 'SYSTEM'
);

-- ============================================================================
-- ODI Assessments Sample Data
-- ============================================================================

-- Patient 002 - Baseline ODI (back pain patient)
INSERT INTO odi_assessments (
    patient_id, assessment_date, measurement_timing,
    pain_intensity, personal_care, lifting, walking, sitting, standing, sleeping, sex_life, social_life, traveling,
    assessor_id, created_by
) VALUES (
    'PATIENT_002', '2024-01-20 10:30:00+00', 'baseline',
    4, 3, 4, 3, 4, 4, 3, 2, 3, 4,
    'DR_JOHNSON', 'SYSTEM'
);

-- Patient 002 - Week 4 ODI
INSERT INTO odi_assessments (
    patient_id, assessment_date, measurement_timing,
    pain_intensity, personal_care, lifting, walking, sitting, standing, sleeping, sex_life, social_life, traveling,
    assessor_id, created_by
) VALUES (
    'PATIENT_002', '2024-02-17 10:30:00+00', 'week_4',
    3, 2, 3, 2, 3, 3, 2, 1, 2, 3,
    'DR_JOHNSON', 'SYSTEM'
);

-- ============================================================================
-- Medication Usage Sample Data
-- ============================================================================

-- Patient 001 - Baseline medication
INSERT INTO medication_usage (
    patient_id, assessment_date, measurement_timing,
    current_medications, opioid_usage, nsaid_usage, adjuvant_usage,
    total_medication_count, pain_medication_count,
    adherence_percentage, missed_doses_count,
    side_effects, medication_effectiveness, satisfaction_with_medication,
    assessor_id, created_by
) VALUES (
    'PATIENT_001', '2024-01-15 09:00:00+00', 'baseline',
    '[{"name": "Ibuprofen", "dose": "400mg", "frequency": "TID", "start_date": "2024-01-10"}]',
    '{}',
    '{"ibuprofen": {"dose": "400mg", "frequency": "TID", "days_per_week": 7}}',
    '{"glucosamine": {"dose": "1500mg", "frequency": "QD", "days_per_week": 7}}',
    2, 1,
    95.0, 2,
    ARRAY['stomach_upset'], 6.5, 7.0,
    'DR_SMITH', 'SYSTEM'
);

-- Patient 001 - Week 4 medication
INSERT INTO medication_usage (
    patient_id, assessment_date, measurement_timing,
    current_medications, opioid_usage, nsaid_usage, adjuvant_usage,
    total_medication_count, pain_medication_count,
    adherence_percentage, missed_doses_count,
    side_effects, medication_effectiveness, satisfaction_with_medication,
    assessor_id, created_by
) VALUES (
    'PATIENT_001', '2024-02-12 09:00:00+00', 'week_4',
    '[{"name": "Ibuprofen", "dose": "400mg", "frequency": "BID", "start_date": "2024-01-10"}]',
    '{}',
    '{"ibuprofen": {"dose": "400mg", "frequency": "BID", "days_per_week": 7}}',
    '{"glucosamine": {"dose": "1500mg", "frequency": "QD", "days_per_week": 7}}',
    2, 1,
    98.0, 1,
    ARRAY['mild_stomach_upset'], 7.5, 8.0,
    'DR_SMITH', 'SYSTEM'
);

-- Patient 002 - Baseline medication
INSERT INTO medication_usage (
    patient_id, assessment_date, measurement_timing,
    current_medications, opioid_usage, nsaid_usage, adjuvant_usage,
    total_medication_count, pain_medication_count,
    adherence_percentage, missed_doses_count,
    side_effects, medication_effectiveness, satisfaction_with_medication,
    assessor_id, created_by
) VALUES (
    'PATIENT_002', '2024-01-20 10:30:00+00', 'baseline',
    '[{"name": "Tramadol", "dose": "50mg", "frequency": "QID", "start_date": "2024-01-15"}, {"name": "Naproxen", "dose": "500mg", "frequency": "BID", "start_date": "2024-01-15"}]',
    '{"tramadol": {"dose": "50mg", "frequency": "QID", "days_per_week": 7}}',
    '{"naproxen": {"dose": "500mg", "frequency": "BID", "days_per_week": 7}}',
    '{}',
    2, 2,
    90.0, 5,
    ARRAY['drowsiness', 'constipation'], 7.0, 6.5,
    'DR_JOHNSON', 'SYSTEM'
);

-- ============================================================================
-- Healthcare Utilization Sample Data
-- ============================================================================

-- Patient 001 - Baseline utilization
INSERT INTO healthcare_utilization (
    patient_id, assessment_date, measurement_timing,
    primary_care_visits, specialist_visits, pain_clinic_visits, physical_therapy_visits,
    emergency_room_visits, urgent_care_visits, hospitalizations, hospital_days,
    imaging_studies, laboratory_tests, procedures,
    estimated_total_cost, out_of_pocket_cost,
    pain_related_visits, treatment_related_visits,
    assessor_id, created_by
) VALUES (
    'PATIENT_001', '2024-01-15 09:00:00+00', 'baseline',
    2, 1, 1, 0,
    0, 0, 0, 0,
    1, 2, 0,
    1250.00, 150.00,
    3, 1,
    'DR_SMITH', 'SYSTEM'
);

-- Patient 002 - Baseline utilization
INSERT INTO healthcare_utilization (
    patient_id, assessment_date, measurement_timing,
    primary_care_visits, specialist_visits, pain_clinic_visits, physical_therapy_visits,
    emergency_room_visits, urgent_care_visits, hospitalizations, hospital_days,
    imaging_studies, laboratory_tests, procedures,
    estimated_total_cost, out_of_pocket_cost,
    pain_related_visits, treatment_related_visits,
    assessor_id, created_by
) VALUES (
    'PATIENT_002', '2024-01-20 10:30:00+00', 'baseline',
    3, 2, 1, 2,
    1, 0, 0, 0,
    2, 3, 0,
    2100.00, 300.00,
    5, 2,
    'DR_JOHNSON', 'SYSTEM'
);

-- ============================================================================
-- Quality of Life Sample Data
-- ============================================================================

-- Patient 001 - Baseline QoL
INSERT INTO quality_of_life (
    patient_id, assessment_date, measurement_timing,
    general_health, physical_functioning, role_physical, bodily_pain,
    vitality, social_functioning, role_emotional, mental_health,
    sleep_quality, work_productivity, relationship_satisfaction, life_satisfaction,
    days_per_week_exercise, minutes_per_day_exercise,
    assessor_id, created_by
) VALUES (
    'PATIENT_001', '2024-01-15 09:00:00+00', 'baseline',
    3, 2, 3, 2,
    3, 3, 3, 3,
    5.0, 6.0, 7.0, 6.0,
    2, 20,
    'DR_SMITH', 'SYSTEM'
);

-- Patient 001 - Week 12 QoL
INSERT INTO quality_of_life (
    patient_id, assessment_date, measurement_timing,
    general_health, physical_functioning, role_physical, bodily_pain,
    vitality, social_functioning, role_emotional, mental_health,
    sleep_quality, work_productivity, relationship_satisfaction, life_satisfaction,
    days_per_week_exercise, minutes_per_day_exercise,
    assessor_id, created_by
) VALUES (
    'PATIENT_001', '2024-04-08 09:00:00+00', 'week_12',
    4, 3, 4, 4,
    4, 4, 4, 4,
    7.5, 8.0, 8.5, 8.0,
    4, 30,
    'DR_SMITH', 'SYSTEM'
);

-- Patient 002 - Baseline QoL
INSERT INTO quality_of_life (
    patient_id, assessment_date, measurement_timing,
    general_health, physical_functioning, role_physical, bodily_pain,
    vitality, social_functioning, role_emotional, mental_health,
    sleep_quality, work_productivity, relationship_satisfaction, life_satisfaction,
    days_per_week_exercise, minutes_per_day_exercise,
    assessor_id, created_by
) VALUES (
    'PATIENT_002', '2024-01-20 10:30:00+00', 'baseline',
    2, 1, 2, 1,
    2, 2, 2, 2,
    3.0, 4.0, 5.0, 4.0,
    0, 0,
    'DR_JOHNSON', 'SYSTEM'
);

-- ============================================================================
-- Weekly Symptom Tracking Sample Data
-- ============================================================================

-- Patient 001 - Week 1
INSERT INTO weekly_symptom_tracking (
    patient_id, report_date, week_number,
    average_pain_week, worst_pain_week, pain_free_days,
    activity_limitation_days, missed_work_days,
    fatigue_level, mood_rating, anxiety_level,
    treatment_helpfulness, side_effects_this_week, global_improvement
) VALUES (
    'PATIENT_001', '2024-01-22 18:00:00+00', 1,
    7.5, 9.0, 0,
    5, 2,
    6.0, 5.0, 4.0,
    6.0, ARRAY['stomach_upset'], 4
);

-- Patient 001 - Week 2
INSERT INTO weekly_symptom_tracking (
    patient_id, report_date, week_number,
    average_pain_week, worst_pain_week, pain_free_days,
    activity_limitation_days, missed_work_days,
    fatigue_level, mood_rating, anxiety_level,
    treatment_helpfulness, side_effects_this_week, global_improvement
) VALUES (
    'PATIENT_001', '2024-01-29 18:00:00+00', 2,
    7.0, 8.5, 1,
    4, 1,
    5.5, 5.5, 3.5,
    6.5, ARRAY['mild_stomach_upset'], 3
);

-- Patient 001 - Week 3
INSERT INTO weekly_symptom_tracking (
    patient_id, report_date, week_number,
    average_pain_week, worst_pain_week, pain_free_days,
    activity_limitation_days, missed_work_days,
    fatigue_level, mood_rating, anxiety_level,
    treatment_helpfulness, side_effects_this_week, global_improvement
) VALUES (
    'PATIENT_001', '2024-02-05 18:00:00+00', 3,
    6.5, 8.0, 1,
    3, 1,
    5.0, 6.0, 3.0,
    7.0, ARRAY['mild_stomach_upset'], 3
);

-- Patient 001 - Week 4
INSERT INTO weekly_symptom_tracking (
    patient_id, report_date, week_number,
    average_pain_week, worst_pain_week, pain_free_days,
    activity_limitation_days, missed_work_days,
    fatigue_level, mood_rating, anxiety_level,
    treatment_helpfulness, side_effects_this_week, global_improvement
) VALUES (
    'PATIENT_001', '2024-02-12 18:00:00+00', 4,
    6.0, 7.5, 2,
    2, 0,
    4.5, 6.5, 2.5,
    7.5, ARRAY['mild_stomach_upset'], 2
);

-- ============================================================================
-- Treatment Satisfaction Sample Data
-- ============================================================================

-- Patient 001 - Week 12 satisfaction
INSERT INTO treatment_satisfaction (
    patient_id, assessment_date, measurement_timing,
    overall_satisfaction, would_recommend, would_continue,
    pain_relief_satisfaction, function_improvement_satisfaction, side_effect_tolerance,
    treatment_burden, convenience,
    provider_communication, care_coordination,
    expectations_met,
    most_helpful_aspect, least_helpful_aspect, suggestions_for_improvement,
    assessor_id, created_by
) VALUES (
    'PATIENT_001', '2024-04-08 09:00:00+00', 'week_12',
    8.5, TRUE, TRUE,
    8.0, 8.5, 7.5,
    6.0, 8.0,
    9.0, 8.5,
    8.0,
    'Reduced pain and improved mobility',
    'Medication side effects',
    'Consider alternative pain medications with fewer side effects',
    'DR_SMITH', 'SYSTEM'
);

-- ============================================================================
-- Outcome Changes Sample Data
-- ============================================================================

-- Patient 001 - Baseline to Week 12 changes
INSERT INTO outcome_changes (
    patient_id, baseline_date, comparison_date, follow_up_duration_days,
    pain_baseline, pain_current, pain_change, pain_percent_change, pain_clinically_significant,
    womac_baseline, womac_current, womac_change, womac_percent_change, womac_clinically_significant,
    qol_baseline, qol_current, qol_change, qol_percent_change, qol_clinically_significant,
    clinical_response_category, significant_improvements, total_outcomes_assessed, response_rate
) VALUES (
    'PATIENT_001', '2024-01-15 09:00:00+00', '2024-04-08 09:00:00+00', 84,
    7.5, 4.5, -3.0, -40.0, TRUE,
    75.0, 25.0, -50.0, -66.7, TRUE,
    6.0, 8.0, 2.0, 33.3, TRUE,
    'excellent_response', 3, 3, 100.0
);

-- Patient 002 - Baseline to Week 4 changes
INSERT INTO outcome_changes (
    patient_id, baseline_date, comparison_date, follow_up_duration_days,
    pain_baseline, pain_current, pain_change, pain_percent_change, pain_clinically_significant,
    womac_baseline, womac_current, womac_change, womac_percent_change, womac_clinically_significant,
    qol_baseline, qol_current, qol_change, qol_percent_change, qol_clinically_significant,
    clinical_response_category, significant_improvements, total_outcomes_assessed, response_rate
) VALUES (
    'PATIENT_002', '2024-01-20 10:30:00+00', '2024-02-17 10:30:00+00', 28,
    8.5, 7.0, -1.5, -17.6, FALSE,
    87.5, 62.5, -25.0, -28.6, TRUE,
    4.0, 4.0, 0.0, 0.0, FALSE,
    'moderate_response', 1, 3, 33.3
);

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Verify data insertion
SELECT 'Pain Assessments' as table_name, COUNT(*) as record_count FROM pain_assessments
UNION ALL
SELECT 'WOMAC Assessments', COUNT(*) FROM womac_assessments
UNION ALL
SELECT 'ODI Assessments', COUNT(*) FROM odi_assessments
UNION ALL
SELECT 'Medication Usage', COUNT(*) FROM medication_usage
UNION ALL
SELECT 'Healthcare Utilization', COUNT(*) FROM healthcare_utilization
UNION ALL
SELECT 'Quality of Life', COUNT(*) FROM quality_of_life
UNION ALL
SELECT 'Weekly Symptom Tracking', COUNT(*) FROM weekly_symptom_tracking
UNION ALL
SELECT 'Treatment Satisfaction', COUNT(*) FROM treatment_satisfaction
UNION ALL
SELECT 'Assessment Schedules', COUNT(*) FROM assessment_schedules
UNION ALL
SELECT 'Outcome Changes', COUNT(*) FROM outcome_changes;

-- Test computed fields
SELECT 
    patient_id,
    measurement_timing,
    total_score,
    normalized_score,
    pain_score,
    stiffness_score,
    function_score
FROM womac_assessments 
WHERE patient_id = 'PATIENT_001'
ORDER BY assessment_date;

-- Test views
SELECT * FROM latest_assessments;
SELECT * FROM baseline_assessments;
SELECT * FROM data_quality_summary;

-- Reset search path
SET search_path TO public; 