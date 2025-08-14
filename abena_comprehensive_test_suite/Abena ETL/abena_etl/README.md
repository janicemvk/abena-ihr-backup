# Abena IHR ETL System

## Overview

The Abena IHR ETL system transforms healthcare data from various EMR systems into FHIR-compliant resources using Apache Spark, SQLAlchemy, and the fhir.resources library. It supports flexible mapping, unit conversion, and scalable batch processing.

---

## System Architecture

```
+-------------------+      +-------------------+      +-------------------+      +-------------------+
|  Source EMR Data  | ---> |  Mapping &        | ---> |  Transformation   | ---> |  FHIR Resource    |
|  (CSV, DB, etc.)  |      |  Unit Conversion  |      |  Engine (Spark)   |      |  Output (Parquet) |
+-------------------+      +-------------------+      +-------------------+      +-------------------+
                                |                        |                          |
                                v                        v                          v
                        MappingRepository        UnitConversionService        FHIRConverter
```

---

## Setup Instructions

1. **Clone the repository**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Copy and configure your environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your DB, Redis, and logging settings
   ```
4. **(Optional) Start supporting services with Docker Compose**
   ```bash
   docker-compose up -d
   ```
5. **Run the ETL pipeline**
   ```bash
   python abena_etl.py
   ```
6. **Run tests**
   ```bash
   pip install -r tests/requirements-test.txt
   pytest tests/
   ```

---

## Configuration (.env)

```
ABENA_DB_URL=postgresql://abena_user:abena_pass@localhost/abena_ihr
ABENA_REDIS_HOST=localhost
ABENA_REDIS_PORT=6379
ABENA_REDIS_DB=1
ABENA_LOG_LEVEL=INFO
ABENA_LOG_FILE=abena_etl.log
```

**Security Note:**
- Never commit your real `.env` file to version control.
- For production, use SSL/TLS for DB and Redis connections. See your provider's documentation for enabling SSL.

---

## Adding a New EMR Mapping

To add a new EMR system mapping, update the `setup_sample_mappings()` function in `abena_etl.py`:

```python
new_emr_mapping = {
    'patient_mappings': {
        'EMR_FIELD1': 'mrn',
        'EMR_FIELD2': 'first_name',
        # ...
    },
    'observation_mappings': {
        'EMR_OBS_FIELD1': 'patient_id',
        'EMR_OBS_FIELD2': 'type',
        # ...
    }
}
repo.create_mapping("NewEMR", "FHIR", new_emr_mapping, "1.0")
```

---

## Adding a New FHIR Resource Type

To support a new FHIR resource (e.g., Medication):
1. Extend `FHIRConverter` with a `create_medication_resource()` method.
2. Update the transformation logic to call this method for relevant data.
3. Add mappings and tests for the new resource.

---

## Troubleshooting

- **DB/Redis connection errors:**
  - Check your `.env` settings and ensure services are running.
  - For production, verify SSL/TLS is enabled.
- **Spark errors:**
  - Ensure Java and Spark are installed, or use the provided Docker Compose setup.
- **Test failures:**
  - Run `pytest -v` for verbose output. Check logs in `abena_etl.log`.
- **Performance:**
  - Tune Spark settings in `TransformationEngine` as needed for your data size.

---

## Contact
For support, please contact the Abena IHR development team.
