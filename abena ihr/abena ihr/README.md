# Abena IHR - Intelligent Health Records

Comprehensive healthcare intelligence platform with predictive analytics and real-time biomarker integration.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment: Copy `.env.example` to `.env`
3. Run database migrations: `python database/scripts/migrate.py`
4. Start application: `uvicorn src.api.main:app --reload`

## Features

- Clinical outcome tracking
- Predictive analytics
- Real-time biomarker monitoring
- Provider workflow integration
- Continuous learning system

## 🏥 Project Overview

The Abena IHR Clinical Outcomes Management System provides a robust framework for managing clinical outcomes in healthcare settings. It enables healthcare professionals to define outcome measures, collect patient data through structured forms, validate data quality, and generate comprehensive reports for clinical decision-making.

## ✨ Features

### Core Functionality
- **Outcome Framework Management**: Define and manage clinical outcomes with measurement criteria
- **Data Collection**: Collect clinical measurements through structured forms
- **Quality Assurance**: Validate data quality and maintain audit trails
- **Evaluation Engine**: Evaluate measurements against outcome definitions
- **Reporting & Analytics**: Generate comprehensive reports and analytics
- **Export Capabilities**: Export data in multiple formats (JSON, CSV)

### Technical Features
- **RESTful API**: FastAPI-based API with comprehensive documentation
- **Database Integration**: PostgreSQL with advanced schema design
- **Data Validation**: Robust validation and error handling
- **Audit Trail**: Complete audit trail for data quality changes
- **Flexible Data Storage**: Support for various data types and measurement scales

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd abena_ihr
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Run the migration
   psql -U your_user -d your_database -f database/migrations/001_clinical_outcomes.sql
   ```

6. **Start the application**
   ```bash
   python -m src.api.main
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the application is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Key Endpoints

#### Outcome Management
- `GET /api/v1/outcomes` - List all outcomes
- `POST /api/v1/outcomes` - Create new outcome
- `GET /api/v1/outcomes/{name}` - Get specific outcome

#### Data Collection
- `GET /api/v1/measurements` - List measurements
- `POST /api/v1/measurements` - Create measurement
- `GET /api/v1/forms` - List data collection forms
- `POST /api/v1/forms` - Create new form

#### Evaluation & Quality
- `POST /api/v1/evaluate` - Evaluate outcome values
- `PUT /api/v1/measurements/{id}/quality` - Update data quality

#### Reporting
- `GET /api/v1/reports/quality` - Data quality report
- `GET /api/v1/reports/measurements` - Measurement summary
- `GET /api/v1/export/measurements` - Export data

## 🏗️ Project Structure

```
abena_ihr/
├── src/
│   ├── api/
│   │   ├── main.py                 # FastAPI application
│   │   └── routers/
│   │       └── outcomes.py         # API endpoints
│   └── clinical_outcomes/
│       ├── __init__.py
│       ├── outcome_framework.py    # Outcome management
│       └── data_collection.py      # Data collection logic
├── database/
│   └── migrations/
│       └── 001_clinical_outcomes.sql
├── config/                         # Configuration files
├── tests/                          # Test suite
├── docs/
│   └── clinical_forms/             # Clinical forms documentation
├── requirements.txt                # Python dependencies
├── docker-compose.yml              # Docker configuration
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🐳 Docker Deployment

### Using Docker Compose

1. **Build and start services**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - API: http://localhost:8000
   - Database: localhost:5432

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

### Manual Docker Build

```bash
# Build the image
docker build -t abena-ihr .

# Run the container
docker run -p 8000:8000 abena-ihr
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_outcomes.py
```

### Test Structure
```
tests/
├── test_outcomes.py           # Outcome framework tests
├── test_data_collection.py    # Data collection tests
├── test_api.py               # API endpoint tests
└── conftest.py               # Test configuration
```

## 📊 Database Schema

The system uses PostgreSQL with the following key tables:

- **outcome_definitions**: Clinical outcome definitions
- **clinical_measurements**: Individual measurements
- **data_collection_forms**: Form definitions
- **outcome_evaluations**: Evaluation results
- **data_quality_audits**: Quality audit trail
- **outcome_frameworks**: Complete framework definitions

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://postgrel:2114***Million@localhost:5432/abena_ihr

# API Configuration
ENVIRONMENT=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=0M9-XM3g22BhPCsG205HhOKQ1W6KJdfoOy-9DjKSCx8
CORS_ORIGINS=http://localhost:3000,https://abena-ihr.com

# Logging
LOG_LEVEL=INFO
```   

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Use type hints throughout the codebase
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- **Email**: dev@abena-ihr.com
- **Documentation**: http://localhost:8000/docs (when running)
- **Issues**: Create an issue in the repository

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
  - Outcome framework management
  - Data collection system
  - RESTful API
  - Database schema
  - Basic reporting

## 🚧 Roadmap

### Upcoming Features
- [ ] Advanced analytics dashboard
- [ ] Real-time data validation
- [ ] Integration with EHR systems
- [ ] Mobile data collection app
- [ ] Advanced reporting templates
- [ ] Multi-tenant support
- [ ] API rate limiting
- [ ] Advanced security features

### Planned Improvements
- [ ] Performance optimization
- [ ] Enhanced error handling
- [ ] More export formats
- [ ] Batch data import
- [ ] Automated testing pipeline
- [ ] CI/CD integration

---

**Built with ❤️ for better healthcare outcomes** 