# Abena IHR Unified Data Service

## Overview

The Unified Data Service serves as the foundational data layer for the Abena IHR (Integrated Health Record) system. It provides a centralized, master database that acts as the single source of truth for all healthcare data across multiple microservices and applications.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Abena IHR Unified Data Service              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   PostgreSQL    │    │      Redis      │                    │
│  │   Master DB     │    │     Cache       │                    │
│  │                 │    │                 │                    │
│  │ • Patients      │    │ • Sessions      │                    │
│  │ • Providers     │    │ • Cache         │                    │
│  │ • Encounters    │    │ • Queues        │                    │
│  │ • Clinical Data │    │                 │                    │
│  │ • Documents     │    │                 │                    │
│  │ • Audit Logs    │    │                 │                    │
│  └─────────────────┘    └─────────────────┘                    │
│           │                       │                            │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   Migration     │    │   Monitoring    │                    │
│  │   Service       │    │   Service       │                    │
│  └─────────────────┘    └─────────────────┘                    │
│           │                       │                            │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   Backup        │    │   Data Quality  │                    │
│  │   Service       │    │   Metrics       │                    │
│  └─────────────────┘    └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

### 🗄️ **Master Database**
- **Single Source of Truth**: Centralized data repository for all healthcare information
- **Comprehensive Schema**: Complete data model covering patients, providers, clinical data, and more
- **Data Integrity**: Foreign key constraints, triggers, and validation rules
- **Audit Trail**: Complete audit logging for all data changes

### 🔄 **Data Management**
- **Migration System**: Automated database schema migrations
- **Backup Service**: Automated daily backups with retention policies
- **Data Quality**: Monitoring and metrics for data quality assessment
- **Performance Optimization**: Comprehensive indexing strategy

### 🚀 **Scalability & Performance**
- **High Availability**: Health checks and monitoring
- **Caching Layer**: Redis integration for performance optimization
- **Connection Pooling**: Optimized database connections
- **Query Optimization**: Strategic indexing and views

### 🔒 **Security & Compliance**
- **Role-Based Access**: Granular permissions for different user types
- **Data Encryption**: Support for encrypted data storage
- **Audit Compliance**: Complete audit trail for regulatory compliance
- **HIPAA Ready**: Designed with healthcare privacy requirements in mind

## Database Schema

### Core Entities

#### 1. **Patients**
- Medical Record Numbers (MRN)
- Demographics and contact information
- Insurance and emergency contact details
- Metadata and audit information

#### 2. **Providers**
- National Provider Identifiers (NPI)
- Professional credentials and specialties
- Contact information and affiliations
- License and certification details

#### 3. **Organizations**
- Healthcare facilities and organizations
- Tax IDs and NPIs
- Address and contact information
- Organization types and classifications

### Clinical Data

#### 4. **Encounters**
- Patient visits and appointments
- Provider and organization associations
- Encounter types and status tracking
- Reason codes and priority levels

#### 5. **Diagnoses**
- ICD-10 diagnosis codes
- Diagnosis types and severity
- Onset and resolution dates
- Status tracking (active, resolved, chronic)

#### 6. **Medications**
- Prescription medications
- NDC and RxNorm codes
- Dosage, frequency, and instructions
- Prescribing provider information

#### 7. **Vital Signs**
- Blood pressure, heart rate, temperature
- Measurement methods and positions
- Timestamps and provider attribution
- Unit standardization

#### 8. **Lab Results**
- Laboratory test results
- LOINC codes and reference ranges
- Abnormal flags and result status
- Specimen and collection information

#### 9. **Procedures**
- Medical procedures and interventions
- CPT codes and procedure types
- Scheduling and performance tracking
- Facility and provider attribution

#### 10. **Allergies & Immunizations**
- Patient allergies and reactions
- Immunization records and schedules
- Vaccine codes and administration details
- Severity and status tracking

### Documentation

#### 11. **Clinical Notes**
- Progress notes and documentation
- Note types and confidentiality levels
- Author attribution and timestamps
- Status tracking (draft, final, amended)

#### 12. **Documents**
- General documents and files
- File metadata and storage paths
- Upload tracking and status
- MIME types and file sizes

### Relationships & Audit

#### 13. **Patient-Provider Relationships**
- Care team associations
- Relationship types and durations
- Status tracking and history

#### 14. **Provider-Organization Relationships**
- Employment and affiliation tracking
- Role types and responsibilities
- Temporal relationship management

#### 15. **Audit & Quality**
- Complete audit trail
- Data quality metrics
- Change tracking and attribution
- Performance monitoring

## Quick Start

### Prerequisites
- Docker and Docker Compose
- PostgreSQL 15+ (for local development)
- Redis 7+ (for caching)

### 1. Clone and Setup

```bash
# Navigate to the unified-data-service directory
cd foundational-services/unified-data-service

# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
```

### 2. Environment Configuration

```bash
# Database Configuration
POSTGRES_PASSWORD=your_secure_password
POSTGRES_USER=abena_admin
POSTGRES_DB=abena_unified_db

# Redis Configuration
REDIS_PASSWORD=your_redis_password

# Network Configuration
NETWORK_SUBNET=172.20.0.0/16
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f unified-postgres
```

### 4. Verify Setup

```bash
# Connect to database
docker exec -it abena-unified-postgres psql -U abena_admin -d abena_unified_db

# Check tables
\dt

# Check sample data
SELECT COUNT(*) FROM patients;
SELECT COUNT(*) FROM providers;
SELECT COUNT(*) FROM organizations;
```

## Database Operations

### Schema Management

#### Apply Migrations
```bash
# Run migrations manually
docker-compose exec db-migrate psql -h unified-postgres -U abena_admin -d abena_unified_db -f /migrations/001_initial_schema.sql
```

#### Create New Migration
```bash
# Create new migration file
touch migrations/002_new_feature.sql

# Add migration content
cat > migrations/002_new_feature.sql << 'EOF'
-- Migration: 002_new_feature.sql
-- Description: Add new feature to schema
-- Version: 1.0.1

-- Add new table
CREATE TABLE new_feature (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes
CREATE INDEX idx_new_feature_name ON new_feature(name);
EOF
```

### Backup and Recovery

#### Manual Backup
```bash
# Create backup
docker-compose exec db-backup pg_dump -h unified-postgres -U abena_admin -d abena_unified_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### Restore from Backup
```bash
# Restore database
docker-compose exec -T unified-postgres psql -U abena_admin -d abena_unified_db < backup_20240101_120000.sql
```

### Data Quality Monitoring

#### Check Data Quality Metrics
```sql
-- View data quality metrics
SELECT 
    table_name,
    metric_name,
    metric_value,
    metric_date
FROM data_quality_metrics
ORDER BY metric_date DESC, table_name;
```

#### Monitor Database Health
```bash
# Check database status
docker-compose exec db-monitor cat /monitoring/status.txt

# View recent audit logs
docker-compose exec unified-postgres psql -U abena_admin -d abena_unified_db -c "
SELECT 
    table_name,
    operation,
    changed_at,
    changed_by
FROM data_audit_log
ORDER BY changed_at DESC
LIMIT 10;
"
```

## API Integration

### Connection Details

```python
# Python connection example
import psycopg2
import redis

# PostgreSQL connection
db_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'abena_unified_db',
    'user': 'abena_admin',
    'password': 'your_secure_password'
}

# Redis connection
redis_config = {
    'host': 'localhost',
    'port': 6379,
    'password': 'your_redis_password',
    'decode_responses': True
}

# Connect to database
conn = psycopg2.connect(**db_config)
redis_client = redis.Redis(**redis_config)
```

### Common Queries

#### Patient Information
```sql
-- Get patient summary
SELECT 
    p.patient_id,
    p.mrn,
    p.first_name,
    p.last_name,
    p.date_of_birth,
    COUNT(e.encounter_id) as encounter_count,
    COUNT(m.medication_id) as medication_count
FROM patients p
LEFT JOIN encounters e ON p.patient_id = e.patient_id
LEFT JOIN medications m ON p.patient_id = m.patient_id
WHERE p.is_active = true
GROUP BY p.patient_id, p.mrn, p.first_name, p.last_name, p.date_of_birth;
```

#### Provider Information
```sql
-- Get provider summary
SELECT 
    pr.provider_id,
    pr.npi,
    pr.first_name,
    pr.last_name,
    pr.specialty,
    o.name as organization_name,
    COUNT(DISTINCT e.encounter_id) as encounter_count
FROM providers pr
LEFT JOIN encounters e ON pr.provider_id = e.provider_id
LEFT JOIN organizations o ON pr.organization_id = o.organization_id
WHERE pr.is_active = true
GROUP BY pr.provider_id, pr.npi, pr.first_name, pr.last_name, pr.specialty, o.name;
```

#### Clinical Data
```sql
-- Get recent vital signs
SELECT 
    p.mrn,
    p.first_name,
    p.last_name,
    vs.vital_sign_type,
    vs.value,
    vs.unit,
    vs.measurement_date
FROM vital_signs vs
JOIN patients p ON vs.patient_id = p.patient_id
WHERE vs.measurement_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY vs.measurement_date DESC;
```

## Security & Access Control

### User Roles

#### 1. **abena_readonly**
- Read-only access to all tables
- No modification privileges
- Suitable for reporting and analytics

#### 2. **abena_analyst**
- Read access to all tables
- Limited write access for data analysis
- Cannot modify clinical data

#### 3. **abena_clinician**
- Read access to all tables
- Write access to clinical data tables
- Cannot modify administrative data

#### 4. **abena_admin**
- Full access to all tables and operations
- Database administration privileges
- Schema modification capabilities

### Granting Access

```sql
-- Grant access to new user
CREATE USER new_clinician WITH PASSWORD 'secure_password';
GRANT abena_clinician TO new_clinician;

-- Grant specific table access
GRANT SELECT, INSERT, UPDATE ON patients, encounters, diagnoses TO new_clinician;
```

## Monitoring & Maintenance

### Health Checks

```bash
# Check database health
docker-compose exec unified-postgres pg_isready -U abena_admin -d abena_unified_db

# Check Redis health
docker-compose exec unified-redis redis-cli ping

# Check service status
docker-compose ps
```

### Performance Monitoring

```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY tablename, attname;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### Maintenance Tasks

```bash
# Vacuum database
docker-compose exec unified-postgres psql -U abena_admin -d abena_unified_db -c "VACUUM ANALYZE;"

# Update statistics
docker-compose exec unified-postgres psql -U abena_admin -d abena_unified_db -c "ANALYZE;"

# Check for long-running queries
docker-compose exec unified-postgres psql -U abena_admin -d abena_unified_db -c "
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
"
```

## Troubleshooting

### Common Issues

#### 1. **Database Connection Failed**
```bash
# Check if database is running
docker-compose ps unified-postgres

# Check database logs
docker-compose logs unified-postgres

# Verify environment variables
docker-compose exec unified-postgres env | grep POSTGRES
```

#### 2. **Migration Failed**
```bash
# Check migration logs
docker-compose logs db-migrate

# Manually run migration
docker-compose exec db-migrate psql -h unified-postgres -U abena_admin -d abena_unified_db -f /migrations/001_initial_schema.sql
```

#### 3. **Performance Issues**
```sql
-- Check for slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check table bloat
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY tablename, attname;
```

### Debug Mode

```bash
# Enable debug logging
export POSTGRES_LOG_LEVEL=DEBUG
export REDIS_LOG_LEVEL=DEBUG

# Restart services with debug
docker-compose down
docker-compose up -d

# View debug logs
docker-compose logs -f
```

## Development

### Local Development Setup

```bash
# Clone repository
git clone <repository-url>
cd abena-ihr-microservices/foundational-services/unified-data-service

# Create development environment
cp .env.example .env.dev

# Start development services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Run tests
docker-compose exec unified-postgres psql -U abena_admin -d abena_unified_db -f /tests/test_schema.sql
```

### Testing

```bash
# Run schema tests
docker-compose exec unified-postgres psql -U abena_admin -d abena_unified_db -c "
-- Test patient creation
INSERT INTO patients (mrn, first_name, last_name, date_of_birth, gender) 
VALUES ('TEST001', 'Test', 'Patient', '1990-01-01', 'male');

-- Verify insertion
SELECT * FROM patients WHERE mrn = 'TEST001';

-- Clean up
DELETE FROM patients WHERE mrn = 'TEST001';
"
```

## Production Deployment

### Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  unified-postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    ports:
      - "127.0.0.1:5432:5432"  # Bind to localhost only
    networks:
      - abena-network
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  unified-redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"  # Bind to localhost only
    networks:
      - abena-network
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  abena-network:
    driver: bridge
    ipam:
      config:
        - subnet: ${NETWORK_SUBNET}
```

### Security Hardening

```bash
# Set secure passwords
export POSTGRES_PASSWORD=$(openssl rand -base64 32)
export REDIS_PASSWORD=$(openssl rand -base64 32)

# Configure firewall
sudo ufw allow 5432/tcp
sudo ufw allow 6379/tcp

# Enable SSL
docker-compose exec unified-postgres psql -U abena_admin -d abena_unified_db -c "
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/etc/ssl/certs/server.crt';
ALTER SYSTEM SET ssl_key_file = '/etc/ssl/private/server.key';
SELECT pg_reload_conf();
"
```

## Contributing

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-database-table
   ```

2. **Create Migration**
   ```bash
   # Create migration file
   touch migrations/003_new_table.sql
   ```

3. **Test Changes**
   ```bash
   # Apply migration
   docker-compose exec db-migrate psql -h unified-postgres -U abena_admin -d abena_unified_db -f /migrations/003_new_table.sql
   
   # Run tests
   docker-compose exec unified-postgres psql -U abena_admin -d abena_unified_db -f /tests/test_new_table.sql
   ```

4. **Submit Pull Request**
   ```bash
   git add .
   git commit -m "Add new database table with migration"
   git push origin feature/new-database-table
   ```

### Code Standards

- **SQL Formatting**: Use consistent indentation and naming conventions
- **Comments**: Include comprehensive comments for complex queries
- **Testing**: Write tests for all schema changes
- **Documentation**: Update README for new features

## Support

### Getting Help

- **Documentation**: Review this README and inline comments
- **Logs**: Check service logs for error details
- **Issues**: Create GitHub issues for bugs or feature requests
- **Community**: Join the development team discussions

### Contact Information

- **Technical Support**: development@abenahealth.org
- **Database Administration**: dba@abenahealth.org
- **Security Issues**: security@abenahealth.org

---

The Unified Data Service provides the foundational data layer for the Abena IHR system, ensuring data integrity, security, and performance across all healthcare applications. 