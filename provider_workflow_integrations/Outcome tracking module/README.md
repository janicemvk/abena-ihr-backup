# Outcome Tracking Module

A comprehensive Python-based outcome tracking system for healthcare applications, designed to monitor patient outcomes and treatment episodes.

## Features

- **Patient Outcome Tracking**: Record and monitor various outcome types (pain scores, functional assessments, etc.)
- **Treatment Episode Management**: Track treatment episodes with Abena recommendations
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **RESTful API**: FastAPI-based API for easy integration
- **Data Validation**: Pydantic models for robust data validation
- **Migration Support**: Alembic for database schema management

## Database Schema

### Core Tables

1. **patient_outcomes**: Stores individual outcome measurements
   - `outcome_id` (UUID): Primary key
   - `patient_id` (UUID): Patient identifier
   - `measurement_date` (DATE): Date of measurement
   - `outcome_type` (VARCHAR): Type of outcome (pain_score, functional_assessment, etc.)
   - `outcome_value` (DECIMAL): Numeric outcome value
   - `measurement_method` (VARCHAR): Method used for measurement
   - `created_at` (TIMESTAMP): Record creation timestamp

2. **treatment_episodes**: Tracks treatment episodes
   - `episode_id` (UUID): Primary key
   - `patient_id` (UUID): Patient identifier
   - `start_date` (DATE): Episode start date
   - `treatment_plan` (JSONB): Abena recommendations and treatment plan
   - `provider_id` (UUID): Healthcare provider identifier
   - `status` (VARCHAR): Episode status (active, completed, discontinued)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env` file
4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

## Usage

### Starting the API Server
```bash
uvicorn app.main:app --reload
```

### Using the Outcome Tracking Service
```python
from app.services.outcome_service import OutcomeService
from app.models.outcome import OutcomeCreate

# Create outcome service instance
outcome_service = OutcomeService()

# Record a new outcome
outcome_data = OutcomeCreate(
    patient_id="123e4567-e89b-12d3-a456-426614174000",
    measurement_date="2024-01-15",
    outcome_type="pain_score",
    outcome_value=7.5,
    measurement_method="visual_analog_scale"
)

result = outcome_service.create_outcome(outcome_data)
```

## Project Structure

```
outcome_tracking_module/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   └── api/                   # API routes
├── alembic/                   # Database migrations
├── tests/                     # Test files
├── requirements.txt
└── README.md
```

## API Endpoints

- `POST /outcomes/` - Create new outcome record
- `GET /outcomes/{outcome_id}` - Get specific outcome
- `GET /outcomes/patient/{patient_id}` - Get all outcomes for a patient
- `PUT /outcomes/{outcome_id}` - Update outcome record
- `DELETE /outcomes/{outcome_id}` - Delete outcome record
- `POST /episodes/` - Create new treatment episode
- `GET /episodes/{episode_id}` - Get specific episode
- `GET /episodes/patient/{patient_id}` - Get all episodes for a patient
- `PUT /episodes/{episode_id}` - Update episode
- `DELETE /episodes/{episode_id}` - Delete episode

## Testing

Run tests with:
```bash
pytest
```

## License

MIT License 