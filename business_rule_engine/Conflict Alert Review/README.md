# Abena IHR Conflict Alert/Review Module

A comprehensive healthcare conflict detection and alert management system designed for the Abena Integrated Health Records (IHR) platform. This module handles notifications and alerts for conflicts requiring manual review, ensuring patient safety and data integrity.

**🔐 Built with Abena SDK** - Uses Abena's integrated authentication, authorization, privacy, and data handling services.

## 🏥 Features

- **Multi-level Alert System**: Critical, Warning, and Info level alerts
- **Priority Management**: Low, Medium, High, and Critical priority levels
- **Abena SDK Integration**: Automatic authentication, authorization, and data handling
- **Real-time Notifications**: Subscribe to alerts with custom filters via Abena SDK
- **Comprehensive Workflow**: Assign, review, resolve, and escalate alerts
- **Audit Trail**: Complete history of all alert actions via Abena SDK
- **Statistics & Reporting**: Detailed analytics and performance metrics
- **RESTful API**: Full HTTP API with Abena SDK authentication
- **Privacy & Security**: Automatic encryption and privacy compliance via Abena SDK

## 🚀 Quick Start

### Prerequisites

- Node.js 18.0.0 or higher
- npm or yarn package manager
- Abena SDK services running (auth, data, privacy, blockchain)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd abena-ihr-conflict-alert
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your Abena SDK service URLs
   ```

4. **Configure Abena SDK services**
   ```env
   ABENA_AUTH_SERVICE_URL=http://localhost:3001
   ABENA_DATA_SERVICE_URL=http://localhost:8001
   ABENA_PRIVACY_SERVICE_URL=http://localhost:8002
   ABENA_BLOCKCHAIN_SERVICE_URL=http://localhost:8003
   ```

5. **Run the demo**
   ```bash
   npm run demo
   ```

6. **Start the API server**
   ```bash
   npm start
   ```

## 📚 API Documentation

### Base URL
```
http://localhost:3000
```

### Authentication

All API endpoints require authentication via Abena SDK. Include the Abena authentication token in your requests:

```http
Authorization: Bearer <abena-auth-token>
```

### Endpoints

#### Health Check
```http
GET /health
```

#### Create Alert
```http
POST /api/alerts
Authorization: Bearer <abena-auth-token>
Content-Type: application/json

{
  "patientId": "P12345",
  "conflictType": "medication_dosage",
  "description": "Critical medication dosage conflict detected",
  "priority": "critical",
  "severity": "critical",
  "affectsPatientSafety": true,
  "affectedData": ["medication_orders", "pharmacy_records"],
  "suggestedResolution": "Immediate review required"
}
```

#### Get Alerts
```http
GET /api/alerts?status=pending&priority=high
Authorization: Bearer <abena-auth-token>
```

#### Get Alert by ID
```http
GET /api/alerts/{alertId}
Authorization: Bearer <abena-auth-token>
```

#### Assign Alert
```http
PATCH /api/alerts/{alertId}/assign
Authorization: Bearer <abena-auth-token>
Content-Type: application/json

{
  "assigneeUserId": "DR_SMITH"
}
```

#### Review Alert
```http
PATCH /api/alerts/{alertId}/review
Authorization: Bearer <abena-auth-token>
Content-Type: application/json

{
  "resolution": "Dosage corrected in pharmacy system",
  "notes": "Verified with pharmacist and updated dosage"
}
```

#### Resolve Alert
```http
PATCH /api/alerts/{alertId}/resolve
Authorization: Bearer <abena-auth-token>
Content-Type: application/json

{
  "resolutionDetails": "Medication dosage conflict resolved"
}
```

#### Escalate Alert
```http
PATCH /api/alerts/{alertId}/escalate
Authorization: Bearer <abena-auth-token>
Content-Type: application/json

{
  "escalationReason": "Patient unavailable for verification"
}
```

#### Get Statistics
```http
GET /api/alerts/stats?patientId=P12345&startDate=2024-01-01&endDate=2024-12-31
Authorization: Bearer <abena-auth-token>
```

#### Cleanup Old Alerts
```http
DELETE /api/alerts/cleanup?daysOld=90
Authorization: Bearer <abena-auth-token>
```

## 💻 Usage Examples

### Basic Module Usage

```javascript
import ConflictAlertModule from './modules/ConflictAlertModule.js';

// Initialize the module with Abena SDK
const conflictAlerts = new ConflictAlertModule({
    authServiceUrl: 'http://localhost:3001',
    dataServiceUrl: 'http://localhost:8001',
    privacyServiceUrl: 'http://localhost:8002',
    blockchainServiceUrl: 'http://localhost:8003'
});

// Create an alert (auto-handles auth & permissions via Abena SDK)
const alert = await conflictAlerts.createAlert({
    patientId: 'P12345',
    conflictType: 'medication_dosage',
    description: 'Critical medication dosage conflict detected',
    priority: 'critical',
    severity: 'critical',
    affectsPatientSafety: true
}, 'DR001'); // User ID from Abena SDK auth

// Subscribe to critical alerts via Abena SDK
const subscriptionId = await conflictAlerts.subscribeToAlerts('DR001', { type: 'critical' });

// Assign alert to physician (auto-handles permissions)
await conflictAlerts.assignAlert(alert.id, 'DR_SMITH', 'DR001');

// Review and resolve (auto-handles audit logging)
await conflictAlerts.markAsReviewed(alert.id, 'DR_SMITH', 'Dosage corrected', 'Notes here');
await conflictAlerts.resolveAlert(alert.id, 'DR_SMITH', 'Conflict resolved');

// Get statistics (auto-handles data access permissions)
const stats = await conflictAlerts.getAlertStats({}, 'ADMIN001');
console.log(`Total alerts: ${stats.total}`);
```

### Healthcare Scenarios

#### 1. Medication Dosage Conflict
```javascript
const medicationAlert = await conflictAlerts.createAlert({
    patientId: 'P12345',
    conflictType: 'medication_dosage',
    description: 'Conflicting medication dosages between EHR and pharmacy system',
    affectedData: ['medication_orders', 'pharmacy_records', 'patient_vitals'],
    suggestedResolution: 'Review with prescribing physician and pharmacist',
    priority: 'critical',
    severity: 'critical',
    affectsPatientSafety: true,
    source: 'pharmacy_system',
    confidence: 0.95
}, 'DR001');
```

#### 2. Lab Result Discrepancy
```javascript
const labAlert = await conflictAlerts.createAlert({
    patientId: 'P12346',
    conflictType: 'lab_results',
    description: 'Discrepancy in lab results between different testing facilities',
    affectedData: ['lab_results', 'diagnostic_reports'],
    suggestedResolution: 'Review with lab supervisor and ordering physician',
    priority: 'high',
    severity: 'warning',
    requiresReview: true,
    source: 'lab_system',
    confidence: 0.88
}, 'LAB001');
```

#### 3. Patient Demographic Conflict
```javascript
const demographicAlert = await conflictAlerts.createAlert({
    patientId: 'P12347',
    conflictType: 'demographics',
    description: 'Inconsistent patient demographic information across systems',
    affectedData: ['patient_demographics', 'insurance_info'],
    suggestedResolution: 'Verify with patient and update all systems',
    priority: 'medium',
    severity: 'warning',
    source: 'registration_system',
    confidence: 0.75
}, 'ADMIN001');
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Server Configuration
PORT=3000
NODE_ENV=development

# Abena SDK Service URLs
ABENA_AUTH_SERVICE_URL=http://localhost:3001
ABENA_DATA_SERVICE_URL=http://localhost:8001
ABENA_PRIVACY_SERVICE_URL=http://localhost:8002
ABENA_BLOCKCHAIN_SERVICE_URL=http://localhost:8003

# Security
CORS_ORIGIN=http://localhost:3000

# Logging
LOG_LEVEL=info
LOG_FILE=logs/app.log

# Alert Configuration
DEFAULT_ALERT_RETENTION_DAYS=90
MAX_ALERTS_PER_USER=100
AUTO_CLEANUP_ENABLED=true
AUTO_CLEANUP_INTERVAL_HOURS=24

# Abena SDK Configuration
ABENA_API_KEY=your-abena-api-key-here
ABENA_ENVIRONMENT=development
```

### Alert Types

The module supports three alert types:

- **CRITICAL**: Patient safety issues, requires immediate attention
- **WARNING**: Data discrepancies, requires review
- **INFO**: Informational alerts, low priority

### Priority Levels

- **CRITICAL**: Highest priority, immediate action required
- **HIGH**: High priority, action required soon
- **MEDIUM**: Normal priority, standard review
- **LOW**: Low priority, informational

### Abena SDK Permissions

The module uses the following Abena SDK permissions:

- `create_alerts`: Create new conflict alerts
- `view_alerts`: View alerts and alert details
- `assign_alerts`: Assign alerts to users
- `review_alerts`: Review and mark alerts as reviewed
- `resolve_alerts`: Resolve alerts
- `escalate_alerts`: Escalate alerts
- `view_statistics`: View alert statistics
- `cleanup_alerts`: Clean up old alerts
- `subscribe_alerts`: Subscribe to alert notifications
- `view_patient_alerts`: View alerts for specific patients

## 📊 Monitoring & Analytics

### Alert Statistics

The module provides comprehensive statistics via Abena SDK:

```javascript
const stats = await conflictAlerts.getAlertStats({
    patientId: 'P12345',
    dateRange: { start: '2024-01-01', end: '2024-12-31' }
}, 'ADMIN001');

// Available metrics:
// - total: Total number of alerts
// - pending: Pending alerts
// - assigned: Assigned alerts
// - reviewed: Reviewed alerts
// - resolved: Resolved alerts
// - escalated: Escalated alerts
// - byType: Breakdown by alert type
// - byPriority: Breakdown by priority
// - averageResolutionTime: Average time to resolve
// - escalationRate: Percentage of escalated alerts
```

### Performance Metrics

- **Response Time**: API endpoint response times
- **Throughput**: Alerts processed per minute
- **Error Rate**: Failed operations percentage
- **User Activity**: Most active users and roles
- **Abena SDK Metrics**: Authentication, data access, and privacy compliance metrics

## 🔒 Security Features

- **Abena SDK Authentication**: Automatic user authentication and session management
- **Abena SDK Authorization**: Role-based access control with fine-grained permissions
- **Abena SDK Privacy**: Automatic data encryption and privacy compliance
- **Abena SDK Audit Logging**: Comprehensive audit trail for all actions
- **Input Validation**: All inputs are validated and sanitized
- **Error Handling**: Comprehensive error handling prevents data leaks
- **CORS Protection**: Configurable CORS settings
- **Helmet Security**: Security headers via Helmet middleware

## 🧪 Testing

### Run Tests
```bash
npm test
```

### Run Demo
```bash
npm run demo
```

### Manual Testing
```bash
# Start the server
npm start

# Test endpoints with curl (include Abena auth token)
curl -H "Authorization: Bearer <abena-auth-token>" http://localhost:3000/health
curl -X POST http://localhost:3000/api/alerts \
  -H "Authorization: Bearer <abena-auth-token>" \
  -H "Content-Type: application/json" \
  -d '{"patientId":"P12345","conflictType":"test","description":"Test alert"}'
```

## 📝 Development

### Project Structure
```
src/
├── modules/
│   └── ConflictAlertModule.js    # Main module class (Abena SDK integrated)
├── server.js                     # Express API server (Abena SDK auth)
├── demo.js                       # Demo script (Abena SDK integrated)
└── index.js                      # Entry point

tests/                            # Test files
docs/                             # Documentation
```

### Adding New Features

1. **Extend the Module Class**: Add new methods to `ConflictAlertModule.js` using Abena SDK
2. **Add API Endpoints**: Create new routes in `server.js` with Abena SDK auth
3. **Update Documentation**: Document new features in README
4. **Add Tests**: Create test cases for new functionality

### Code Style

- Use ES6+ features
- Follow JSDoc documentation standards
- Implement proper error handling
- Use Abena SDK for all auth, data, and privacy operations
- Write unit tests for new features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes using Abena SDK patterns
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the documentation
- Refer to Abena SDK documentation

## 🔄 Version History

- **v2.0.0**: Abena SDK integration
  - Integrated Abena SDK for authentication, authorization, and data handling
  - Removed custom auth and data management
  - Added automatic privacy and audit logging
  - Updated all endpoints to use Abena SDK middleware

- **v1.0.0**: Initial release with core functionality
  - Basic alert creation and management
  - REST API endpoints
  - Custom role-based access control
  - Statistics and reporting

---

**Built with ❤️ for Abena IHR System using Abena SDK** 