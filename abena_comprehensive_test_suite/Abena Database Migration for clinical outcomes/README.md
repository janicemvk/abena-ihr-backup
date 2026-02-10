# Abena Clinical Outcomes Database Migration

A comprehensive PostgreSQL database schema for managing clinical outcomes data in the Abena IHR (Integrated Health Records) system. This migration creates a robust structure for tracking patient outcomes, assessments, and clinical data across multiple domains.

## 🏥 Project Overview

The Abena Clinical Outcomes Database is designed to support clinical research and patient care by providing:

- **Primary Outcomes Tracking**: Pain assessments, WOMAC (Western Ontario and McMaster Universities Osteoarthritis Index), and ODI (Oswestry Disability Index)
- **Secondary Outcomes**: Medication usage, healthcare utilization, and quality of life measures
- **Patient-Reported Outcomes**: Weekly symptom tracking and treatment satisfaction
- **Assessment Management**: Scheduling, compliance tracking, and outcome change calculations

## 📋 Database Schema Structure

### Core Tables

#### Primary Outcomes
- `pain_assessments` - Comprehensive pain evaluation with multiple scales
- `womac_assessments` - Osteoarthritis-specific functional assessment
- `odi_assessments` - Low back pain disability assessment

#### Secondary Outcomes
- `medication_usage` - Medication tracking with adherence metrics
- `healthcare_utilization` - Healthcare visit and cost tracking
- `quality_of_life` - SF-12 health survey and additional QoL measures

#### Patient-Reported Outcomes
- `weekly_symptom_tracking` - Weekly patient symptom reports
- `treatment_satisfaction` - Patient satisfaction and feedback

#### Management Tables
- `assessment_schedules` - Study scheduling and compliance tracking
- `outcome_changes` - Cached outcome change calculations

### Key Features

- **Data Quality Tracking**: Built-in data quality levels (complete, adequate, minimal, insufficient)
- **Audit Trail**: Comprehensive audit fields (created_at, updated_at, created_by, version)
- **Computed Fields**: Automatic calculation of scores and percentages
- **Constraints**: Data validation and business rule enforcement
- **Indexes**: Optimized for common query patterns
- **Views**: Pre-built views for common reporting needs

## 🚀 Installation and Setup

### Prerequisites

- PostgreSQL 12 or higher
- Superuser privileges for initial setup
- `uuid-ossp` extension (usually available by default)

### Quick Start

1. **Clone or download the migration files**
   ```bash
   # Navigate to your project directory
   cd abena-clinical-outcomes-migration
   ```

2. **Run the migration**
   ```bash
   # Connect to your PostgreSQL database
   psql -h localhost -U your_username -d your_database -f abena_clinical_outcomes_migration.sql
   ```

3. **Verify the installation**
   ```sql
   -- Check that the schema was created
   SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'clinical_outcomes';
   
   -- Verify the demo data
   SELECT * FROM clinical_outcomes.assessment_schedules;
   ```

### Database Connection

The migration script will:
- Create the `clinical_outcomes` schema
- Set up all tables, indexes, views, and triggers
- Insert sample reference data
- Configure appropriate permissions (commented out - adjust as needed)

## 📊 Data Model Highlights

### Pain Assessments
```sql
-- Example pain assessment insertion
INSERT INTO clinical_outcomes.pain_assessments (
    patient_id, assessment_date, measurement_timing,
    current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference
) VALUES (
    'PATIENT_001', CURRENT_TIMESTAMP, 'baseline',
    7.5, 7.0, 9.0, 5.0, 8.0
);
```

### WOMAC Assessments
The WOMAC table includes 24 items across three subscales:
- **Pain**: 5 items (0-4 scale each)
- **Stiffness**: 2 items (0-4 scale each)  
- **Physical Function**: 17 items (0-4 scale each)

Scores are automatically computed and normalized to 0-100 scale.

### Medication Usage
Flexible JSONB storage for medication details:
```sql
-- Example medication usage
INSERT INTO clinical_outcomes.medication_usage (
    patient_id, assessment_date, measurement_timing,
    current_medications, adherence_percentage
) VALUES (
    'PATIENT_001', CURRENT_TIMESTAMP, 'baseline',
    '[{"name": "Ibuprofen", "dose": "400mg", "frequency": "TID"}]',
    95.5
);
```

## 🔍 Common Queries

### Latest Assessments Per Patient
```sql
SELECT * FROM clinical_outcomes.latest_assessments;
```

### Baseline Data
```sql
SELECT * FROM clinical_outcomes.baseline_assessments;
```

### Data Quality Summary
```sql
SELECT * FROM clinical_outcomes.data_quality_summary;
```

### Patient Progress Tracking
```sql
-- Compare baseline to current assessments
SELECT 
    p.patient_id,
    baseline.average_pain_24h as baseline_pain,
    current.average_pain_24h as current_pain,
    (baseline.average_pain_24h - current.average_pain_24h) as pain_improvement
FROM clinical_outcomes.pain_assessments baseline
JOIN clinical_outcomes.pain_assessments current 
    ON baseline.patient_id = current.patient_id
WHERE baseline.measurement_timing = 'baseline'
    AND current.measurement_timing = 'week_12';
```

## 🛠️ Customization

### Adding New Assessment Types

1. Create new enum values in `measurement_timing` if needed
2. Add new tables following the established pattern
3. Include audit fields and data quality tracking
4. Add appropriate indexes and constraints

### Modifying Scoring Algorithms

The computed fields use PostgreSQL's `GENERATED ALWAYS AS` feature. To modify:
1. Drop the existing computed column
2. Recreate with the new calculation
3. Update any dependent views or functions

### User Permissions

Uncomment and modify the permission grants at the end of the migration script:
```sql
-- Replace with your actual usernames
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA clinical_outcomes TO your_app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA clinical_outcomes TO your_report_user;
```

## 📈 Performance Considerations

### Indexes
The migration creates indexes for:
- Patient ID + date combinations
- Measurement timing
- Score ranges
- Data quality levels

### Partitioning
For large datasets, consider partitioning by:
- Patient ID ranges
- Assessment date ranges
- Measurement timing

### Maintenance
Regular maintenance tasks:
```sql
-- Analyze table statistics
ANALYZE clinical_outcomes.pain_assessments;

-- Vacuum to reclaim space
VACUUM ANALYZE clinical_outcomes.pain_assessments;
```

## 🔒 Security and Compliance

### Data Protection
- All tables include audit fields for tracking changes
- UUID primary keys prevent sequential ID enumeration
- Data quality tracking ensures data integrity

### HIPAA Considerations
- Patient IDs should be de-identified in production
- Implement row-level security (RLS) policies
- Encrypt sensitive data at rest and in transit

### Backup Strategy
```bash
# Create regular backups
pg_dump -h localhost -U username -d database -n clinical_outcomes > backup_$(date +%Y%m%d).sql
```

## 🧪 Testing

### Sample Data Insertion
The migration includes commented test data. To run:
```sql
-- Uncomment the test data section in the migration file
INSERT INTO clinical_outcomes.pain_assessments (
    patient_id, assessment_date, measurement_timing,
    current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference
) VALUES (
    'TEST_PATIENT_001', CURRENT_TIMESTAMP, 'baseline',
    7.5, 7.0, 9.0, 5.0, 8.0
);
```

### Validation Queries
```sql
-- Verify constraints are working
INSERT INTO clinical_outcomes.pain_assessments (
    patient_id, assessment_date, measurement_timing,
    current_pain, average_pain_24h, worst_pain_24h, least_pain_24h, pain_interference
) VALUES (
    'TEST_PATIENT_002', CURRENT_TIMESTAMP, 'baseline',
    11.0, 7.0, 9.0, 5.0, 8.0  -- This should fail (pain > 10)
);
```

## 📚 Documentation

### Schema Documentation
Generate schema documentation:
```sql
-- List all tables and their columns
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'clinical_outcomes'
ORDER BY table_name, ordinal_position;
```

### Data Dictionary
The migration includes comprehensive comments for all fields. Key concepts:

- **Measurement Timing**: Standardized assessment timepoints
- **Data Quality Levels**: Quality assessment for each record
- **Computed Scores**: Automatically calculated outcome measures
- **Audit Fields**: Change tracking and version control

## 🤝 Contributing

When contributing to this database migration:

1. Follow the existing naming conventions
2. Include comprehensive comments
3. Add appropriate constraints and indexes
4. Test with sample data
5. Update this README if adding new features

## 📞 Support

For questions or issues with the Abena Clinical Outcomes Database Migration:

- Review the verification queries in the migration script
- Check PostgreSQL logs for error messages
- Ensure all prerequisites are met
- Test with a small dataset first

## 📄 License

This database migration is part of the Abena IHR system. Please ensure compliance with your organization's data governance policies and applicable regulations.

---

**Version**: 1.0  
**Last Updated**: 2024  
**Compatibility**: PostgreSQL 12+  
**Author**: Abena IHR Development Team 