# Abena Clinical Outcomes Database - Quick Reference Guide

This guide provides quick access to common queries and operations for the Abena Clinical Outcomes Database.

## 🚀 Quick Start

### Connect to Database
```bash
# Using psql
psql -h localhost -U postgres -d abena_clinical

# Set search path
SET search_path TO clinical_outcomes, public;
```

### Basic Verification
```sql
-- Check if schema exists
SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'clinical_outcomes');

-- List all tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'clinical_outcomes' ORDER BY table_name;

-- Count records in each table
SELECT 'pain_assessments' as table_name, COUNT(*) as count FROM pain_assessments
UNION ALL
SELECT 'womac_assessments', COUNT(*) FROM womac_assessments
UNION ALL
SELECT 'odi_assessments', COUNT(*) FROM odi_assessments
UNION ALL
SELECT 'medication_usage', COUNT(*) FROM medication_usage;
```

## 📊 Patient Data Queries

### Get Patient Overview
```sql
-- Latest assessment for each patient
SELECT * FROM latest_assessments;

-- Baseline data for all patients
SELECT * FROM baseline_assessments;

-- Patient progress summary
SELECT 
    p.patient_id,
    baseline.average_pain_24h as baseline_pain,
    current.average_pain_24h as current_pain,
    (baseline.average_pain_24h - current.average_pain_24h) as pain_improvement,
    baseline.assessment_date as baseline_date,
    current.assessment_date as current_date
FROM pain_assessments baseline
JOIN pain_assessments current ON baseline.patient_id = current.patient_id
WHERE baseline.measurement_timing = 'baseline'
    AND current.measurement_timing = 'week_12';
```

### Patient-Specific Data
```sql
-- All assessments for a specific patient
SELECT 
    assessment_date,
    measurement_timing,
    average_pain_24h,
    pain_interference
FROM pain_assessments 
WHERE patient_id = 'PATIENT_001'
ORDER BY assessment_date;

-- Patient's WOMAC progression
SELECT 
    assessment_date,
    measurement_timing,
    pain_score,
    stiffness_score,
    function_score,
    total_score,
    normalized_score
FROM womac_assessments 
WHERE patient_id = 'PATIENT_001'
ORDER BY assessment_date;
```

## 📈 Outcome Analysis

### Pain Assessment Analysis
```sql
-- Pain score distribution
SELECT 
    CASE 
        WHEN average_pain_24h < 3 THEN 'Mild (0-3)'
        WHEN average_pain_24h < 7 THEN 'Moderate (3-7)'
        ELSE 'Severe (7-10)'
    END as pain_level,
    COUNT(*) as patient_count,
    ROUND(AVG(average_pain_24h), 2) as avg_pain_score
FROM pain_assessments 
WHERE measurement_timing = 'baseline'
GROUP BY 
    CASE 
        WHEN average_pain_24h < 3 THEN 'Mild (0-3)'
        WHEN average_pain_24h < 7 THEN 'Moderate (3-7)'
        ELSE 'Severe (7-10)'
    END;

-- Pain improvement rates
SELECT 
    measurement_timing,
    COUNT(*) as patients_assessed,
    ROUND(AVG(average_pain_24h), 2) as avg_pain_score,
    ROUND(STDDEV(average_pain_24h), 2) as std_dev
FROM pain_assessments 
GROUP BY measurement_timing
ORDER BY 
    CASE measurement_timing
        WHEN 'baseline' THEN 1
        WHEN 'week_2' THEN 2
        WHEN 'week_4' THEN 3
        WHEN 'week_8' THEN 4
        WHEN 'week_12' THEN 5
        WHEN 'week_24' THEN 6
        WHEN 'week_52' THEN 7
        ELSE 8
    END;
```

### WOMAC Analysis
```sql
-- WOMAC subscale analysis
SELECT 
    measurement_timing,
    ROUND(AVG(pain_score), 2) as avg_pain_score,
    ROUND(AVG(stiffness_score), 2) as avg_stiffness_score,
    ROUND(AVG(function_score), 2) as avg_function_score,
    ROUND(AVG(normalized_score), 2) as avg_normalized_score
FROM womac_assessments 
GROUP BY measurement_timing
ORDER BY 
    CASE measurement_timing
        WHEN 'baseline' THEN 1
        WHEN 'week_4' THEN 2
        WHEN 'week_12' THEN 3
        WHEN 'week_24' THEN 4
        ELSE 5
    END;

-- Patients with significant WOMAC improvement (>20%)
SELECT 
    p.patient_id,
    baseline.normalized_score as baseline_womac,
    current.normalized_score as current_womac,
    (baseline.normalized_score - current.normalized_score) as improvement,
    ROUND(((baseline.normalized_score - current.normalized_score) / baseline.normalized_score * 100), 2) as percent_improvement
FROM womac_assessments baseline
JOIN womac_assessments current ON baseline.patient_id = current.patient_id
WHERE baseline.measurement_timing = 'baseline'
    AND current.measurement_timing = 'week_12'
    AND ((baseline.normalized_score - current.normalized_score) / baseline.normalized_score * 100) > 20;
```

## 💊 Medication Analysis

### Medication Usage Patterns
```sql
-- Medication adherence analysis
SELECT 
    CASE 
        WHEN adherence_percentage >= 95 THEN 'Excellent (≥95%)'
        WHEN adherence_percentage >= 80 THEN 'Good (80-94%)'
        WHEN adherence_percentage >= 60 THEN 'Fair (60-79%)'
        ELSE 'Poor (<60%)'
    END as adherence_level,
    COUNT(*) as patient_count,
    ROUND(AVG(adherence_percentage), 2) as avg_adherence
FROM medication_usage 
WHERE measurement_timing = 'baseline'
GROUP BY 
    CASE 
        WHEN adherence_percentage >= 95 THEN 'Excellent (≥95%)'
        WHEN adherence_percentage >= 80 THEN 'Good (80-94%)'
        WHEN adherence_percentage >= 60 THEN 'Fair (60-79%)'
        ELSE 'Poor (<60%)'
    END;

-- Side effects analysis
SELECT 
    unnest(side_effects) as side_effect,
    COUNT(*) as occurrence_count
FROM medication_usage 
WHERE side_effects != '{}'
GROUP BY unnest(side_effects)
ORDER BY occurrence_count DESC;
```

## 🏥 Healthcare Utilization

### Visit Patterns
```sql
-- Healthcare visit summary
SELECT 
    measurement_timing,
    COUNT(*) as patients,
    ROUND(AVG(total_visits), 2) as avg_total_visits,
    ROUND(AVG(pain_related_visits), 2) as avg_pain_visits,
    ROUND(SUM(estimated_total_cost), 2) as total_cost
FROM healthcare_utilization 
GROUP BY measurement_timing
ORDER BY 
    CASE measurement_timing
        WHEN 'baseline' THEN 1
        WHEN 'week_4' THEN 2
        WHEN 'week_12' THEN 3
        ELSE 4
    END;

-- High utilizers (top 20%)
SELECT 
    patient_id,
    total_visits,
    pain_related_visits,
    estimated_total_cost
FROM healthcare_utilization 
WHERE measurement_timing = 'baseline'
ORDER BY total_visits DESC
LIMIT (SELECT CEIL(COUNT(*) * 0.2) FROM healthcare_utilization WHERE measurement_timing = 'baseline');
```

## 📊 Quality of Life Analysis

### QoL Trends
```sql
-- Quality of life progression
SELECT 
    measurement_timing,
    ROUND(AVG(physical_component_score), 2) as avg_physical_score,
    ROUND(AVG(mental_component_score), 2) as avg_mental_score,
    ROUND(AVG(life_satisfaction), 2) as avg_life_satisfaction,
    ROUND(AVG(sleep_quality), 2) as avg_sleep_quality
FROM quality_of_life 
GROUP BY measurement_timing
ORDER BY 
    CASE measurement_timing
        WHEN 'baseline' THEN 1
        WHEN 'week_12' THEN 2
        WHEN 'week_24' THEN 3
        ELSE 4
    END;

-- Exercise patterns
SELECT 
    CASE 
        WHEN days_per_week_exercise = 0 THEN 'No exercise'
        WHEN days_per_week_exercise <= 2 THEN 'Low (1-2 days)'
        WHEN days_per_week_exercise <= 4 THEN 'Moderate (3-4 days)'
        ELSE 'High (5+ days)'
    END as exercise_level,
    COUNT(*) as patient_count,
    ROUND(AVG(life_satisfaction), 2) as avg_life_satisfaction
FROM quality_of_life 
WHERE measurement_timing = 'baseline'
GROUP BY 
    CASE 
        WHEN days_per_week_exercise = 0 THEN 'No exercise'
        WHEN days_per_week_exercise <= 2 THEN 'Low (1-2 days)'
        WHEN days_per_week_exercise <= 4 THEN 'Moderate (3-4 days)'
        ELSE 'High (5+ days)'
    END;
```

## 📈 Treatment Response Analysis

### Clinical Response Categories
```sql
-- Response rate analysis
SELECT 
    clinical_response_category,
    COUNT(*) as patient_count,
    ROUND(AVG(response_rate), 2) as avg_response_rate,
    ROUND(AVG(significant_improvements), 2) as avg_significant_improvements
FROM outcome_changes 
GROUP BY clinical_response_category
ORDER BY patient_count DESC;

-- Patients with excellent response
SELECT 
    patient_id,
    pain_percent_change,
    womac_percent_change,
    qol_percent_change,
    clinical_response_category
FROM outcome_changes 
WHERE clinical_response_category = 'excellent_response'
ORDER BY pain_percent_change;
```

## 🔍 Data Quality Monitoring

### Data Quality Summary
```sql
-- Overall data quality
SELECT * FROM data_quality_summary;

-- Missing assessments
SELECT 
    s.patient_id,
    s.baseline_date,
    s.total_scheduled,
    s.total_completed,
    s.compliance_rate
FROM assessment_schedules s
WHERE s.compliance_rate < 100
ORDER BY s.compliance_rate;

-- Data completeness by assessment type
SELECT 
    'pain_assessments' as assessment_type,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE data_quality = 'complete') as complete_records,
    ROUND(COUNT(*) FILTER (WHERE data_quality = 'complete')::DECIMAL / COUNT(*) * 100, 2) as completeness_rate
FROM pain_assessments
UNION ALL
SELECT 
    'womac_assessments',
    COUNT(*),
    COUNT(*) FILTER (WHERE data_quality = 'complete'),
    ROUND(COUNT(*) FILTER (WHERE data_quality = 'complete')::DECIMAL / COUNT(*) * 100, 2)
FROM womac_assessments;
```

## 📋 Weekly Symptom Tracking

### Symptom Trends
```sql
-- Weekly pain progression
SELECT 
    week_number,
    COUNT(*) as patients_reporting,
    ROUND(AVG(average_pain_week), 2) as avg_pain,
    ROUND(AVG(worst_pain_week), 2) as avg_worst_pain,
    ROUND(AVG(pain_free_days), 2) as avg_pain_free_days
FROM weekly_symptom_tracking 
GROUP BY week_number
ORDER BY week_number;

-- Treatment effectiveness over time
SELECT 
    week_number,
    ROUND(AVG(treatment_helpfulness), 2) as avg_helpfulness,
    ROUND(AVG(global_improvement), 2) as avg_global_improvement,
    COUNT(*) FILTER (WHERE global_improvement <= 3) as improved_patients
FROM weekly_symptom_tracking 
GROUP BY week_number
ORDER BY week_number;
```

## 🎯 Treatment Satisfaction

### Satisfaction Analysis
```sql
-- Overall satisfaction scores
SELECT 
    measurement_timing,
    COUNT(*) as patients,
    ROUND(AVG(overall_satisfaction), 2) as avg_satisfaction,
    COUNT(*) FILTER (WHERE would_recommend = true) as would_recommend_count,
    ROUND(COUNT(*) FILTER (WHERE would_recommend = true)::DECIMAL / COUNT(*) * 100, 2) as recommend_rate
FROM treatment_satisfaction 
GROUP BY measurement_timing
ORDER BY 
    CASE measurement_timing
        WHEN 'week_12' THEN 1
        WHEN 'week_24' THEN 2
        ELSE 3
    END;

-- Satisfaction by domain
SELECT 
    ROUND(AVG(pain_relief_satisfaction), 2) as avg_pain_relief_satisfaction,
    ROUND(AVG(function_improvement_satisfaction), 2) as avg_function_satisfaction,
    ROUND(AVG(side_effect_tolerance), 2) as avg_side_effect_tolerance,
    ROUND(AVG(provider_communication), 2) as avg_communication
FROM treatment_satisfaction;
```

## 🔧 Maintenance Queries

### Database Maintenance
```sql
-- Analyze table statistics
ANALYZE clinical_outcomes.pain_assessments;
ANALYZE clinical_outcomes.womac_assessments;
ANALYZE clinical_outcomes.medication_usage;

-- Check for orphaned records
SELECT COUNT(*) as orphaned_pain_assessments
FROM pain_assessments p
LEFT JOIN assessment_schedules s ON p.patient_id = s.patient_id
WHERE s.patient_id IS NULL;

-- Find duplicate assessments
SELECT 
    patient_id,
    measurement_timing,
    assessment_date,
    COUNT(*) as duplicate_count
FROM pain_assessments 
GROUP BY patient_id, measurement_timing, assessment_date
HAVING COUNT(*) > 1;
```

### Performance Monitoring
```sql
-- Index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes 
WHERE schemaname = 'clinical_outcomes'
ORDER BY idx_scan DESC;

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'clinical_outcomes'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 📝 Common Data Insertion Patterns

### Adding New Patient Assessment
```sql
-- Insert baseline pain assessment
INSERT INTO pain_assessments (
    patient_id, assessment_date, measurement_timing,
    current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference,
    assessor_id, created_by
) VALUES (
    'NEW_PATIENT_001', CURRENT_TIMESTAMP, 'baseline',
    7.0, 6.5, 8.5, 4.5, 7.0,
    'DR_SMITH', 'SYSTEM'
);

-- Insert corresponding WOMAC assessment
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
    'NEW_PATIENT_001', CURRENT_TIMESTAMP, 'baseline',
    3, 3, 2, 2, 3,
    3, 2,
    3, 3, 2, 3, 3, 2, 3, 2, 3, 2, 2, 2, 2, 2, 3, 2,
    'DR_SMITH', 'SYSTEM'
);
```

### Updating Assessment Data
```sql
-- Update pain assessment
UPDATE pain_assessments 
SET 
    current_pain = 6.0,
    average_pain_24h = 5.5,
    worst_pain_24h = 7.5,
    least_pain_24h = 4.0,
    pain_interference = 6.0,
    updated_at = CURRENT_TIMESTAMP
WHERE patient_id = 'PATIENT_001' 
    AND measurement_timing = 'week_4'
    AND assessment_date = '2024-02-12 09:00:00+00';
```

## 🚨 Troubleshooting

### Common Issues
```sql
-- Check for constraint violations
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'clinical_outcomes'
    AND tc.constraint_type = 'CHECK';

-- Find invalid data
SELECT 
    patient_id,
    assessment_date,
    current_pain,
    average_pain_24h,
    worst_pain_24h
FROM pain_assessments 
WHERE current_pain > 10 
    OR average_pain_24h > 10 
    OR worst_pain_24h > 10;

-- Check for missing required fields
SELECT 
    patient_id,
    assessment_date,
    measurement_timing
FROM pain_assessments 
WHERE current_pain IS NULL 
    OR average_pain_24h IS NULL 
    OR worst_pain_24h IS NULL;
```

---

**Note**: This quick reference guide provides common queries for the Abena Clinical Outcomes Database. For more detailed information, refer to the main README.md file and the database schema documentation. 