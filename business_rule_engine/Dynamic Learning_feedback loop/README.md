# Abena IHR Dynamic Learning Platform v2.0.0

## 🧠 Intelligent Healthcare Research with Abena SDK

The Abena IHR Dynamic Learning Platform is a comprehensive healthcare research system that leverages the Abena SDK to provide advanced clinical decision support, pharmacogenomic analysis, and adaptive learning capabilities.

## ✨ Key Features

### 🔧 Abena SDK Integration
- **Centralized Authentication**: Secure user management through Abena Auth Service
- **Privacy Controls**: HIPAA-compliant data handling with Privacy Service
- **Blockchain Audit Trails**: Immutable audit logs for all clinical decisions
- **Real-time Learning**: Continuous model optimization with feedback loops

### 🎯 Core Capabilities
- **Learning Engine**: Machine learning insights with automatic validation
- **Clinical Context**: Comprehensive patient data integration with genomic analysis
- **eCdome Integration**: Advanced pharmacogenomic analysis and drug interaction detection
- **Risk Assessment**: Multi-factor risk analysis including genetic and environmental factors

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (for full deployment)
- Abena SDK API key

### Local Development Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Environment Configuration**
Copy `env.example` to `.env` and configure your settings:
```bash
cp env.example .env
# Edit .env with your Abena SDK credentials
```

3. **Run the Application**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment
```bash
docker-compose up -d
```

## 📚 API Endpoints

### Core Endpoints
- `POST /api/learning/generate-insights` - Generate ML insights
- `POST /api/clinical/context` - Get clinical context
- `POST /api/ecdome/analyze` - Perform pharmacogenomic analysis
- `GET /` - Enhanced dashboard with SDK status
- `GET /health` - Health check with SDK status

## 📖 Documentation

For comprehensive documentation, setup instructions, and advanced configuration, see:
**[📚 Complete Documentation](README_SDK.md)**

## 🔐 Security & Privacy

- **End-to-End Encryption**: All data encrypted in transit and at rest
- **Role-Based Access Control**: Granular permissions for different user types
- **Audit Logging**: Complete audit trail for compliance
- **Data Anonymization**: Automatic PII protection

## 🏗️ Architecture

The platform is built with a modern microservices architecture leveraging the Abena SDK:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Learning      │    │   Clinical      │
│   Dashboard     │◄──►│   Engine        │◄──►│   Context       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Abena SDK Layer                              │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│   Auth Service  │   Data Service  │ Privacy Service │Blockchain │
│   (Port 3001)   │   (Port 8001)   │   (Port 8002)   │(Port 8003)│
└─────────────────┴─────────────────┴─────────────────┴───────────┘
```

## 📞 Support

- **Technical Support**: support@abena-ihr.com
- **SDK Support**: sdk-support@abena.com
- **Documentation**: [Complete Guide](README_SDK.md)

## 📄 License

This project is licensed under the MIT License.

---

**🧠 Abena IHR Dynamic Learning Platform v2.0.0**  
*Intelligent Healthcare Research with Adaptive Analytics* 