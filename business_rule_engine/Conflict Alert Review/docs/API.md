# Abena IHR Conflict Alert Module - API Documentation

## Overview

The Conflict Alert Module provides a RESTful API for managing healthcare conflict alerts. All endpoints return JSON responses and use standard HTTP status codes.

## Base URL

```
http://localhost:3000
```

## Authentication

Currently, the API does not require authentication. In production, implement proper authentication middleware.

## Response Format

All API responses follow this format:

```json
{
  "success": true|false,
  "data": {...},
  "message": "Optional message",
  "error": "Error type (if applicable)"
}
```

## Endpoints

### Health Check

**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "Abena IHR Conflict Alert Module"
}
```

### Create Alert

**POST** `/api/alerts`

Create a new conflict alert.

**Request Body:**
```json
{
  "patientId": "P12345",
  "conflictType": "medication_dosage",
  "description": "Critical medication dosage conflict detected",
  "priority": "critical",
  "severity": "critical",
  "affectsPatientSafety": true,
  "userId": "DR001",
  "affectedData": ["medication_orders", "pharmacy_records"],
  "suggestedResolution": "Immediate review required",
  "source": "pharmacy_system",
  "confidence": 0.95,
  "tags": ["medication", "safety"]
}
```

**Required Fields:**
- `patientId`: Patient identifier
- `conflictType`: Type of conflict

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "ALERT_1705312200000_abc123",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "type": "critical",
    "priority": "critical",
    "patientId": "P12345",
    "conflictType": "medication_dosage",
    "description": "Critical medication dosage conflict detected",
    "status": "pending",
    "assignedTo": null,
    "createdBy": "DR001",
    "escalationLevel": 0,
    "reviewHistory": [],
    "metadata": {
      "source": "pharmacy_system",
      "confidence": 0.95,
      "tags": ["medication", "safety"]
    }
  },
  "message": "Alert created successfully"
}
```

### Get Alerts

**GET** `/api/alerts`

Retrieve alerts with optional filtering and pagination.

**Query Parameters:**
- `userId`: Filter by assigned user
- `role`: User role for permission filtering
- `status`: Filter by alert status (pending, assigned, reviewed, resolved, escalated)
- `priority`: Filter by priority (low, medium, high, critical)
- `type`: Filter by alert type (critical, warning, info)
- `patientId`: Filter by patient ID
- `limit`: Number of alerts per page (default: 50)
- `offset`: Number of alerts to skip (default: 0)

**Example:**
```
GET /api/alerts?userId=DR001&role=physician&status=pending&priority=high&limit=10&offset=0
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "ALERT_1705312200000_abc123",
      "timestamp": "2024-01-15T10:30:00.000Z",
      "type": "critical",
      "priority": "high",
      "patientId": "P12345",
      "conflictType": "medication_dosage",
      "description": "Critical medication dosage conflict detected",
      "status": "pending",
      "assignedTo": "DR001"
    }
  ],
  "pagination": {
    "total": 25,
    "limit": 10,
    "offset": 0,
    "hasMore": true
  }
}
```

### Get Alert by ID

**GET** `/api/alerts/{alertId}`

Retrieve a specific alert by its ID.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "ALERT_1705312200000_abc123",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "type": "critical",
    "priority": "critical",
    "patientId": "P12345",
    "conflictType": "medication_dosage",
    "description": "Critical medication dosage conflict detected",
    "affectedData": ["medication_orders", "pharmacy_records"],
    "suggestedResolution": "Immediate review required",
    "status": "assigned",
    "assignedTo": "DR_SMITH",
    "assignedAt": "2024-01-15T10:35:00.000Z",
    "assignedBy": "SYSTEM",
    "createdBy": "DR001",
    "escalationLevel": 0,
    "reviewHistory": [
      {
        "action": "assigned",
        "userId": "SYSTEM",
        "timestamp": "2024-01-15T10:35:00.000Z",
        "details": "Assigned to DR_SMITH"
      }
    ],
    "metadata": {
      "source": "pharmacy_system",
      "confidence": 0.95,
      "tags": ["medication", "safety"]
    }
  }
}
```

### Assign Alert

**PATCH** `/api/alerts/{alertId}/assign`

Assign an alert to a specific user.

**Request Body:**
```json
{
  "userId": "DR_SMITH",
  "assignerId": "SYSTEM"
}
```

**Required Fields:**
- `userId`: ID of the user to assign the alert to

**Response:**
```json
{
  "success": true,
  "message": "Alert assigned successfully"
}
```

### Review Alert

**PATCH** `/api/alerts/{alertId}/review`

Mark an alert as reviewed.

**Request Body:**
```json
{
  "userId": "DR_SMITH",
  "resolution": "Dosage corrected in pharmacy system",
  "notes": "Verified with pharmacist and updated dosage to 10mg daily"
}
```

**Required Fields:**
- `userId`: ID of the user reviewing the alert
- `resolution`: Resolution description

**Response:**
```json
{
  "success": true,
  "message": "Alert marked as reviewed successfully"
}
```

### Resolve Alert

**PATCH** `/api/alerts/{alertId}/resolve`

Mark an alert as resolved.

**Request Body:**
```json
{
  "userId": "DR_SMITH",
  "resolutionDetails": "Medication dosage conflict resolved by updating pharmacy system with correct dosage"
}
```

**Required Fields:**
- `userId`: ID of the user resolving the alert
- `resolutionDetails`: Detailed description of the resolution

**Response:**
```json
{
  "success": true,
  "message": "Alert resolved successfully"
}
```

### Escalate Alert

**PATCH** `/api/alerts/{alertId}/escalate`

Escalate an alert to a higher level.

**Request Body:**
```json
{
  "userId": "ADMIN001",
  "escalationReason": "Patient unavailable for verification, requires supervisor review"
}
```

**Required Fields:**
- `userId`: ID of the user escalating the alert
- `escalationReason`: Reason for escalation

**Response:**
```json
{
  "success": true,
  "message": "Alert escalated successfully"
}
```

### Get Statistics

**GET** `/api/alerts/stats`

Get alert statistics with optional filtering.

**Query Parameters:**
- `patientId`: Filter by patient ID
- `startDate`: Start date for date range filter (ISO format)
- `endDate`: End date for date range filter (ISO format)

**Example:**
```
GET /api/alerts/stats?patientId=P12345&startDate=2024-01-01&endDate=2024-12-31
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 150,
    "pending": 25,
    "assigned": 15,
    "inReview": 5,
    "reviewed": 30,
    "resolved": 70,
    "escalated": 5,
    "byType": {
      "critical": 20,
      "warning": 80,
      "info": 50
    },
    "byPriority": {
      "low": 30,
      "medium": 60,
      "high": 40,
      "critical": 20
    },
    "averageResolutionTime": 3600000,
    "escalationRate": 3.33
  }
}
```

### Cleanup Old Alerts

**DELETE** `/api/alerts/cleanup`

Remove old alerts from the system.

**Query Parameters:**
- `daysOld`: Age in days for alerts to be considered old (default: 90)

**Example:**
```
DELETE /api/alerts/cleanup?daysOld=90
```

**Response:**
```json
{
  "success": true,
  "data": {
    "removedCount": 15
  },
  "message": "Cleared 15 old alerts"
}
```

### Subscribe to Alerts

**POST** `/api/alerts/subscribe`

Create a subscription for alert notifications.

**Request Body:**
```json
{
  "callback": "https://your-webhook-url.com/alerts",
  "filters": {
    "type": "critical",
    "priority": "high"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "subscriptionId": "sub_abc123def456"
  },
  "message": "Subscription created successfully"
}
```

### Unsubscribe from Alerts

**DELETE** `/api/alerts/subscribe/{subscriptionId}`

Remove a subscription.

**Response:**
```json
{
  "success": true,
  "message": "Unsubscribed successfully"
}
```

## Error Responses

### Validation Error (400)
```json
{
  "success": false,
  "error": "Validation error",
  "message": "Patient ID and conflict type are required"
}
```

### Not Found (404)
```json
{
  "success": false,
  "error": "Not found",
  "message": "Alert not found"
}
```

### Server Error (500)
```json
{
  "success": false,
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting

Currently, no rate limiting is implemented. In production, implement appropriate rate limiting based on your requirements.

## Pagination

When retrieving multiple alerts, use the `limit` and `offset` query parameters for pagination:

```
GET /api/alerts?limit=20&offset=40
```

The response includes pagination metadata:

```json
{
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 40,
    "hasMore": true
  }
}
```

## Webhook Notifications

For real-time notifications, implement webhook endpoints that receive POST requests when alerts are created, updated, or resolved.

The webhook payload will include the alert data and the action performed:

```json
{
  "alert": {
    "id": "ALERT_1705312200000_abc123",
    "patientId": "P12345",
    "conflictType": "medication_dosage",
    "description": "Critical medication dosage conflict detected",
    "priority": "critical",
    "status": "pending"
  },
  "action": "created",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Examples

### Complete Workflow Example

1. **Create Alert**
```bash
curl -X POST http://localhost:3000/api/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "patientId": "P12345",
    "conflictType": "medication_dosage",
    "description": "Critical medication dosage conflict",
    "priority": "critical",
    "severity": "critical",
    "affectsPatientSafety": true,
    "userId": "DR001"
  }'
```

2. **Assign Alert**
```bash
curl -X PATCH http://localhost:3000/api/alerts/ALERT_1705312200000_abc123/assign \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "DR_SMITH",
    "assignerId": "SYSTEM"
  }'
```

3. **Review Alert**
```bash
curl -X PATCH http://localhost:3000/api/alerts/ALERT_1705312200000_abc123/review \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "DR_SMITH",
    "resolution": "Dosage corrected",
    "notes": "Verified with pharmacist"
  }'
```

4. **Resolve Alert**
```bash
curl -X PATCH http://localhost:3000/api/alerts/ALERT_1705312200000_abc123/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "DR_SMITH",
    "resolutionDetails": "Conflict resolved by updating pharmacy system"
  }'
```

### Get Statistics Example

```bash
curl "http://localhost:3000/api/alerts/stats?startDate=2024-01-01&endDate=2024-12-31"
```

### Get User Alerts Example

```bash
curl "http://localhost:3000/api/alerts?userId=DR_SMITH&role=physician&status=pending&priority=high"
``` 