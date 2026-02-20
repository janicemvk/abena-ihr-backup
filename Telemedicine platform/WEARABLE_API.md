# Wearable Device API Integration

## Overview

The telemedicine platform now supports comprehensive wearable device integration through the Abena SDK. Wearables can submit health data directly to the system, which is automatically processed, encrypted, and made available to healthcare providers.

## API Endpoints

### Base URL
```
https://api.telemedicine-platform.com/v1/wearables
```

### Authentication
All API requests require authentication using the Abena SDK:
```javascript
const abena = new AbenaSDK({
  authServiceUrl: 'http://localhost:3001',
  dataServiceUrl: 'http://localhost:8001',
  privacyServiceUrl: 'http://localhost:8002',
  blockchainServiceUrl: 'http://localhost:8003'
});
```

## Data Submission Endpoints

### 1. Submit Wearable Data
**POST** `/submit-data`

Submit raw data from wearable devices.

```javascript
// Example: Submit heart rate data
const response = await abena.submitWearableData(patientId, {
  heartRate: 72,
  timestamp: '2024-01-15T10:30:00Z',
  deviceId: 'apple_watch_123',
  accuracy: 0.95
}, 'smartwatch');
```

**Request Body:**
```json
{
  "patientId": "patient_123",
  "data": {
    "heartRate": 72,
    "bloodPressure": {
      "systolic": 120,
      "diastolic": 80
    },
    "temperature": 98.6,
    "oxygenSaturation": 98
  },
  "deviceType": "smartwatch",
  "timestamp": "2024-01-15T10:30:00Z",
  "deviceId": "apple_watch_123",
  "accuracy": 0.95
}
```

**Response:**
```json
{
  "success": true,
  "dataId": "data_456",
  "processed": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Submit Vital Signs
**POST** `/vital-signs`

Submit specific vital signs data.

```javascript
const response = await abena.submitVitalSigns(patientId, {
  heartRate: 72,
  bloodPressure: { systolic: 120, diastolic: 80 },
  temperature: 98.6,
  oxygenSaturation: 98,
  respiratoryRate: 16
});
```

### 3. Submit Activity Data
**POST** `/activity`

Submit activity tracking data.

```javascript
const response = await abena.submitActivityData(patientId, {
  steps: 8542,
  calories: 420,
  distance: 3.2,
  activeMinutes: 45,
  exerciseMinutes: 30,
  floors: 12
});
```

### 4. Submit Sleep Data
**POST** `/sleep`

Submit sleep tracking data.

```javascript
const response = await abena.submitSleepData(patientId, {
  totalHours: 7.5,
  deepSleep: 2.1,
  lightSleep: 4.2,
  remSleep: 1.2,
  sleepScore: 85,
  sleepEfficiency: 0.92
});
```

### 5. Submit Heart Rate Data
**POST** `/heart-rate`

Submit continuous heart rate monitoring data.

```javascript
const response = await abena.submitHeartRateData(patientId, {
  current: 72,
  average: 68,
  min: 55,
  max: 120,
  resting: 58,
  variability: 45
});
```

## Device Management

### 1. Register Device
**POST** `/devices/register`

Register a new wearable device.

```javascript
const response = await abena.registerWearableDevice(patientId, {
  name: 'Apple Watch Series 7',
  type: 'smartwatch',
  model: 'Series 7',
  serialNumber: 'AW123456789',
  manufacturer: 'Apple',
  firmware: '8.1.1'
});
```

### 2. Get Registered Devices
**GET** `/devices`

Get all registered devices for a patient.

```javascript
const devices = await abena.getRegisteredDevices(patientId);
```

### 3. Update Device Status
**PUT** `/devices/{deviceId}/status`

Update device connection status.

```javascript
const response = await abena.updateDeviceStatus(patientId, deviceId, 'active');
```

## Data Retrieval

### 1. Get Wearable Data
**GET** `/data`

Retrieve processed wearable data.

```javascript
const data = await abena.getWearableData(patientId, 'smartwatch', '7d');
```

### 2. Get Vital Signs History
**GET** `/vital-signs/history`

Get historical vital signs data.

```javascript
const vitals = await abena.getVitalSignsHistory(patientId, '30d');
```

### 3. Get Activity Summary
**GET** `/activity/summary`

Get activity summary and trends.

```javascript
const activity = await abena.getActivitySummary(patientId, '7d');
```

### 4. Get Sleep Analysis
**GET** `/sleep/analysis`

Get sleep analysis and patterns.

```javascript
const sleep = await abena.getSleepAnalysis(patientId, '30d');
```

### 5. Get Heart Rate Trends
**GET** `/heart-rate/trends`

Get heart rate trends and patterns.

```javascript
const trends = await abena.getHeartRateTrends(patientId, '7d');
```

## Alert System

### 1. Set Wearable Alerts
**POST** `/alerts`

Configure alerts for specific health metrics.

```javascript
const alerts = await abena.setWearableAlerts(patientId, {
  heartRate: {
    min: 50,
    max: 100,
    enabled: true
  },
  bloodPressure: {
    systolic: { min: 90, max: 140 },
    diastolic: { min: 60, max: 90 },
    enabled: true
  },
  activity: {
    minSteps: 5000,
    enabled: true
  }
});
```

### 2. Get Wearable Alerts
**GET** `/alerts`

Get configured alerts for a patient.

```javascript
const alerts = await abena.getWearableAlerts(patientId);
```

## Analytics & Reporting

### 1. Generate Health Report
**POST** `/reports/health`

Generate comprehensive health reports.

```javascript
const report = await abena.generateHealthReport(patientId, 'comprehensive', '30d');
```

### 2. Get Health Trends
**GET** `/trends`

Get health trends and patterns.

```javascript
const trends = await abena.getHealthTrends(patientId, 'heart_rate', '7d');
```

## Data Processing

### 1. Process Wearable Data
**POST** `/process`

Process raw wearable data.

```javascript
const processed = await abena.processWearableData(patientId, rawData, 'heart_rate');
```

## Supported Device Types

### Smartwatches
- Apple Watch
- Samsung Galaxy Watch
- Fitbit Versa
- Garmin Vivoactive

### Fitness Trackers
- Fitbit Charge
- Garmin Vivosmart
- Xiaomi Mi Band
- Huawei Band

### Smart Rings
- Oura Ring
- Motiv Ring
- NFC Ring

### Medical Devices
- Blood Pressure Monitors
- Glucose Monitors
- Pulse Oximeters
- Thermometers

## Data Types

### Vital Signs
- Heart Rate (bpm)
- Blood Pressure (mmHg)
- Temperature (°F/°C)
- Oxygen Saturation (%)
- Respiratory Rate (breaths/min)

### Activity Metrics
- Steps (count)
- Calories (kcal)
- Distance (miles/km)
- Active Minutes
- Exercise Minutes
- Floors Climbed

### Sleep Metrics
- Total Sleep Hours
- Deep Sleep
- Light Sleep
- REM Sleep
- Sleep Score
- Sleep Efficiency

### Heart Rate Metrics
- Current Heart Rate
- Average Heart Rate
- Resting Heart Rate
- Heart Rate Variability
- Min/Max Heart Rate

## Security & Privacy

### Data Encryption
All wearable data is automatically encrypted using the Abena SDK:
- **In Transit**: TLS 1.3 encryption
- **At Rest**: AES-256 encryption
- **Processing**: End-to-end encryption

### Privacy Controls
- Patient consent management
- Data access controls
- HIPAA compliance
- GDPR compliance

### Audit Logging
All data submissions are logged for compliance:
```javascript
await abena.logActivity({
  action: 'wearable_data_submitted',
  patientId: 'patient_123',
  deviceType: 'smartwatch',
  dataType: 'heart_rate',
  timestamp: '2024-01-15T10:30:00Z'
});
```

## Blockchain Integration

### Recording Transactions
All wearable data submissions are recorded on the blockchain:
```javascript
await abena.recordToBlockchain({
  patientId: 'patient_123',
  dataType: 'heart_rate',
  value: 72,
  timestamp: '2024-01-15T10:30:00Z'
}, 'wearable_data_submission');
```

### Audit Trail
Complete audit trail available for all data submissions:
```javascript
const history = await abena.getBlockchainHistory(patientId);
```

## Error Handling

### API Error Responses
```json
{
  "error": "Invalid device type",
  "code": "INVALID_DEVICE_TYPE",
  "timestamp": "2024-01-15T10:30:00Z",
  "details": "Device type 'invalid_type' is not supported"
}
```

### Error Reporting
```javascript
await abena.handleError(error, 'wearable_data_submission');
```

## Rate Limits

- **Data Submissions**: 100 requests per minute per device
- **Data Retrieval**: 1000 requests per hour per patient
- **Device Management**: 10 requests per minute per patient

## Webhook Support

### Configure Webhooks
```javascript
// Configure webhook for real-time alerts
await abena.setWearableAlerts(patientId, {
  webhook: {
    url: 'https://your-app.com/webhooks/health-alerts',
    events: ['heart_rate_alert', 'blood_pressure_alert']
  }
});
```

## SDK Integration Examples

### React Native App
```javascript
import AbenaSDK from '@abena/sdk';

const abena = new AbenaSDK({
  authServiceUrl: 'https://auth.abena.com',
  dataServiceUrl: 'https://data.abena.com',
  privacyServiceUrl: 'https://privacy.abena.com',
  blockchainServiceUrl: 'https://blockchain.abena.com'
});

// Submit heart rate data
const submitHeartRate = async (heartRate) => {
  try {
    await abena.submitHeartRateData(patientId, {
      current: heartRate,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error submitting heart rate:', error);
  }
};
```

### iOS Swift
```swift
import AbenaSDK

let abena = AbenaSDK(
    authServiceUrl: "https://auth.abena.com",
    dataServiceUrl: "https://data.abena.com",
    privacyServiceUrl: "https://privacy.abena.com",
    blockchainServiceUrl: "https://blockchain.abena.com"
)

// Submit heart rate data
func submitHeartRate(_ heartRate: Int) {
    abena.submitHeartRateData(
        patientId: "patient_123",
        data: ["current": heartRate, "timestamp": Date().iso8601]
    ) { result in
        switch result {
        case .success(let response):
            print("Heart rate submitted successfully")
        case .failure(let error):
            print("Error submitting heart rate: \(error)")
        }
    }
}
```

### Android Kotlin
```kotlin
import com.abena.sdk.AbenaSDK

val abena = AbenaSDK(
    authServiceUrl = "https://auth.abena.com",
    dataServiceUrl = "https://data.abena.com",
    privacyServiceUrl = "https://privacy.abena.com",
    blockchainServiceUrl = "https://blockchain.abena.com"
)

// Submit heart rate data
fun submitHeartRate(heartRate: Int) {
    abena.submitHeartRateData(
        patientId = "patient_123",
        data = mapOf(
            "current" to heartRate,
            "timestamp" to ISO8601DateFormatter().string(Date())
        )
    ) { result ->
        when (result) {
            is Result.Success -> println("Heart rate submitted successfully")
            is Result.Failure -> println("Error submitting heart rate: ${result.error}")
        }
    }
}
```

## Testing

### Test Environment
```javascript
const abena = new AbenaSDK({
  authServiceUrl: 'https://test-auth.abena.com',
  dataServiceUrl: 'https://test-data.abena.com',
  privacyServiceUrl: 'https://test-privacy.abena.com',
  blockchainServiceUrl: 'https://test-blockchain.abena.com'
});
```

### Mock Data
```javascript
// Submit test data
await abena.submitWearableData('test_patient_123', {
  heartRate: 72,
  steps: 8542,
  sleepHours: 7.5
}, 'test_device');
```

## Support

For technical support and API documentation:
- **Email**: api-support@abena.com
- **Documentation**: https://docs.abena.com/wearable-api
- **SDK Downloads**: https://github.com/abena/wearable-sdk 