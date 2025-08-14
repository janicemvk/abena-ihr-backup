import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics for SDK testing
const sdkErrorRate = new Rate('sdk_errors');
const sdkLatency = new Rate('sdk_latency');

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<300'],  // 95% of requests must be below 300ms
    http_req_failed: ['rate<0.05'],    // Error rate must be below 5%
    sdk_errors: ['rate<0.02'],         // SDK errors must be below 2%
    sdk_latency: ['p(95)<200'],        // SDK latency must be below 200ms
  },
};

const BASE_URL = 'https://ihr.abena-health.com';
const SDK_BASE_URL = `${BASE_URL}/sdk`;

export function setup() {
  // Login and get auth token
  const loginRes = http.post(`${BASE_URL}/api/auth/login`, {
    email: 'test@example.com',
    password: 'password123'
  });
  
  return { 
    authToken: loginRes.json('token'),
    sdkToken: loginRes.json('sdk_token') 
  };
}

export default function(data) {
  const params = {
    headers: {
      'Authorization': `Bearer ${data.authToken}`,
      'Content-Type': 'application/json',
      'X-Service-Client': 'universal'
    },
  };

  const sdkParams = {
    headers: {
      'Authorization': `Bearer ${data.sdkToken}`,
      'Content-Type': 'application/json',
      'X-Service-Client': 'abena-shared-sdk'
    },
  };

  // Test SDK Health Check
  const healthRes = http.get(`${SDK_BASE_URL}/health`, sdkParams);
  check(healthRes, {
    'SDK health check status is 200': (r) => r.status === 200,
    'SDK health check response time < 100ms': (r) => r.timings.duration < 100,
  });

  // Test SDK Metrics
  const metricsRes = http.get(`${SDK_BASE_URL}/metrics`, sdkParams);
  check(metricsRes, {
    'SDK metrics status is 200': (r) => r.status === 200,
    'SDK metrics response time < 200ms': (r) => r.timings.duration < 200,
  });

  // Test Universal Service Client - FHIR Integration
  const fhirRes = http.get(`${BASE_URL}/api/services/fhir/Patient?search=test`, params);
  check(fhirRes, {
    'FHIR service status is 200': (r) => r.status === 200,
    'FHIR service response time < 500ms': (r) => r.timings.duration < 500,
  });

  // Test Universal Service Client - HL7 Integration
  const hl7Res = http.post(`${BASE_URL}/api/services/hl7/message`, 
    JSON.stringify({
      messageType: 'ADT^A01',
      patientId: 'TEST123',
      data: { /* HL7 message data */ }
    }), 
    params
  );
  check(hl7Res, {
    'HL7 service status is 200': (r) => r.status === 200,
    'HL7 service response time < 1000ms': (r) => r.timings.duration < 1000,
  });

  // Test Universal Service Client - Epic Integration
  const epicRes = http.get(`${BASE_URL}/api/services/epic/patient/TEST123`, params);
  check(epicRes, {
    'Epic service status is 200': (r) => r.status === 200,
    'Epic service response time < 800ms': (r) => r.timings.duration < 800,
  });

  // Test Universal Service Client - Cerner Integration
  const cernerRes = http.get(`${BASE_URL}/api/services/cerner/patient/TEST123`, params);
  check(cernerRes, {
    'Cerner service status is 200': (r) => r.status === 200,
    'Cerner service response time < 800ms': (r) => r.timings.duration < 800,
  });

  // Test Universal Service Client - Payment Integration
  const paymentRes = http.post(`${BASE_URL}/api/services/payment/charge`, 
    JSON.stringify({
      amount: 1000,
      currency: 'USD',
      description: 'Test payment'
    }), 
    params
  );
  check(paymentRes, {
    'Payment service status is 200': (r) => r.status === 200,
    'Payment service response time < 1000ms': (r) => r.timings.duration < 1000,
  });

  // Test Universal Service Client - SMS Integration
  const smsRes = http.post(`${BASE_URL}/api/services/sms/send`, 
    JSON.stringify({
      to: '+1234567890',
      message: 'Test SMS message'
    }), 
    params
  );
  check(smsRes, {
    'SMS service status is 200': (r) => r.status === 200,
    'SMS service response time < 500ms': (r) => r.timings.duration < 500,
  });

  // Test Universal Service Client - Email Integration
  const emailRes = http.post(`${BASE_URL}/api/services/email/send`, 
    JSON.stringify({
      to: 'test@example.com',
      subject: 'Test Email',
      body: 'Test email body'
    }), 
    params
  );
  check(emailRes, {
    'Email service status is 200': (r) => r.status === 200,
    'Email service response time < 500ms': (r) => r.timings.duration < 500,
  });

  // Test Universal Service Client - Storage Integration
  const storageRes = http.post(`${BASE_URL}/api/services/storage/upload`, 
    JSON.stringify({
      filename: 'test-document.pdf',
      contentType: 'application/pdf',
      data: 'base64-encoded-data'
    }), 
    params
  );
  check(storageRes, {
    'Storage service status is 200': (r) => r.status === 200,
    'Storage service response time < 2000ms': (r) => r.timings.duration < 2000,
  });

  // Test SDK Circuit Breaker
  const circuitBreakerRes = http.get(`${SDK_BASE_URL}/circuit-breaker/status`, sdkParams);
  check(circuitBreakerRes, {
    'Circuit breaker status is 200': (r) => r.status === 200,
    'Circuit breaker response time < 100ms': (r) => r.timings.duration < 100,
  });

  // Test SDK Cache Status
  const cacheRes = http.get(`${SDK_BASE_URL}/cache/status`, sdkParams);
  check(cacheRes, {
    'Cache status is 200': (r) => r.status === 200,
    'Cache status response time < 100ms': (r) => r.timings.duration < 100,
  });

  // Test SDK Service Discovery
  const discoveryRes = http.get(`${SDK_BASE_URL}/discovery/services`, sdkParams);
  check(discoveryRes, {
    'Service discovery status is 200': (r) => r.status === 200,
    'Service discovery response time < 200ms': (r) => r.timings.duration < 200,
  });

  // Record custom metrics
  const responses = [healthRes, metricsRes, fhirRes, hl7Res, epicRes, cernerRes, 
                    paymentRes, smsRes, emailRes, storageRes, circuitBreakerRes, 
                    cacheRes, discoveryRes];
  
  responses.forEach(res => {
    sdkErrorRate.add(res.status >= 400);
    sdkLatency.add(res.timings.duration < 200);
  });

  sleep(1);
}

export function teardown(data) {
  // Cleanup any test data or resources
  console.log('SDK load test completed');
} 