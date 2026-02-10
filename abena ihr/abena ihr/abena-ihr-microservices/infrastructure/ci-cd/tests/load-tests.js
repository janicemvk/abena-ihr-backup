import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const authTokenTrend = new Trend('auth_token_time');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must be below 500ms
    http_req_failed: ['rate<0.1'],    // Error rate must be below 10%
    errors: ['rate<0.1'],             // Custom error rate
  },
};

// Test data
const BASE_URL = __ENV.TEST_BASE_URL || 'https://api.abena-ihr.com';
const API_VERSION = 'v1';

// Test users for different roles
const testUsers = {
  patient: {
    email: 'patient.loadtest@abena-ihr.com',
    password: 'LoadTestPassword123!'
  },
  provider: {
    email: 'provider.loadtest@abena-ihr.com',
    password: 'LoadTestPassword123!'
  },
  admin: {
    email: 'admin.loadtest@abena-ihr.com',
    password: 'LoadTestPassword123!'
  }
};

// Global variables
let authTokens = {};

export function setup() {
  console.log('Setting up load test...');
  
  // Authenticate all test users
  for (const [role, user] of Object.entries(testUsers)) {
    const startTime = new Date();
    const authResponse = http.post(`${BASE_URL}/api/${API_VERSION}/auth/login`, {
      email: user.email,
      password: user.password
    }, {
      headers: { 'Content-Type': 'application/json' }
    });
    
    const endTime = new Date();
    authTokenTrend.add(endTime - startTime);
    
    if (authResponse.status === 200) {
      authTokens[role] = authResponse.json('access_token');
      console.log(`✅ Authenticated ${role} user`);
    } else {
      console.log(`❌ Failed to authenticate ${role} user: ${authResponse.status}`);
    }
  }
  
  return { authTokens };
}

export default function(data) {
  const { authTokens } = data;
  
  // Randomly select a user role for this iteration
  const roles = Object.keys(authTokens);
  const selectedRole = roles[Math.floor(Math.random() * roles.length)];
  const token = authTokens[selectedRole];
  
  if (!token) {
    errorRate.add(1);
    return;
  }
  
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
  
  // Test different endpoints based on user role
  const testResults = {};
  
  // Health check test
  testResults.health = check(http.get(`${BASE_URL}/api/${API_VERSION}/health`), {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 200ms': (r) => r.timings.duration < 200,
  });
  
  // Patient-specific tests
  if (selectedRole === 'patient') {
    testResults.patientProfile = check(http.get(`${BASE_URL}/api/${API_VERSION}/patient-engagement/patients/profile`, { headers }), {
      'patient profile status is 200': (r) => r.status === 200,
      'patient profile response time < 500ms': (r) => r.timings.duration < 500,
    });
    
    testResults.appointments = check(http.get(`${BASE_URL}/api/${API_VERSION}/patient-engagement/appointments`, { headers }), {
      'appointments status is 200': (r) => r.status === 200,
      'appointments response time < 500ms': (r) => r.timings.duration < 500,
    });
    
    // Test appointment booking
    const appointmentData = {
      provider_id: 'test-provider-123',
      appointment_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      appointment_type: 'consultation',
      reason: 'Load test appointment',
      preferred_time: '09:00'
    };
    
    testResults.appointmentBooking = check(http.post(`${BASE_URL}/api/${API_VERSION}/patient-engagement/appointments`, JSON.stringify(appointmentData), { headers }), {
      'appointment booking status is 201': (r) => r.status === 201,
      'appointment booking response time < 1000ms': (r) => r.timings.duration < 1000,
    });
  }
  
  // Provider-specific tests
  if (selectedRole === 'provider') {
    testResults.clinicalAnalysis = check(http.post(`${BASE_URL}/api/${API_VERSION}/clinical-decision-support/analyze`, JSON.stringify({
      patient_id: 'test-patient-123',
      symptoms: ['fever', 'cough'],
      vital_signs: {
        temperature: 38.5,
        blood_pressure: '120/80',
        heart_rate: 85
      }
    }), { headers }), {
      'clinical analysis status is 200': (r) => r.status === 200,
      'clinical analysis response time < 2000ms': (r) => r.timings.duration < 2000,
    });
    
    // Test HL7 data ingestion
    const hl7Message = `MSH|^~\\&|EPIC|EPICADT|ABENA_IHR|ABENA_IHR|${new Date().toISOString().replace(/[-:]/g, '').split('.')[0]}||ADT^A01|MSG${Math.random().toString(36).substr(2, 9)}|P|2.5
PID|||${Math.random().toString(36).substr(2, 9)}^^^MRN||DOE^JOHN^^^^||19900101|M|||123 MAIN ST^^ANYTOWN^CA^12345
PV1||I|2000^2012^01||||123456^SMITH^JANE^^^^^^^MD`;
    
    testResults.hl7Ingestion = check(http.post(`${BASE_URL}/api/${API_VERSION}/data-ingestion/hl7`, hl7Message, {
      headers: { 'Content-Type': 'text/plain', ...headers }
    }), {
      'HL7 ingestion status is 200': (r) => r.status === 200,
      'HL7 ingestion response time < 1000ms': (r) => r.timings.duration < 1000,
    });
  }
  
  // Admin-specific tests
  if (selectedRole === 'admin') {
    testResults.dataAnonymization = check(http.post(`${BASE_URL}/api/${API_VERSION}/privacy-security/anonymize`, JSON.stringify({
      patient_id: 'test-patient-123',
      first_name: 'John',
      last_name: 'Doe',
      ssn: '123-45-6789',
      date_of_birth: '1990-01-01'
    }), { headers }), {
      'data anonymization status is 200': (r) => r.status === 200,
      'data anonymization response time < 1000ms': (r) => r.timings.duration < 1000,
    });
  }
  
  // Blockchain tests (for all authenticated users)
  testResults.blockchainHealth = check(http.get(`${BASE_URL}/api/${API_VERSION}/blockchain/health`, { headers }), {
    'blockchain health status is 200': (r) => r.status === 200,
    'blockchain health response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  // Test health record creation on blockchain
  const healthRecord = {
    patient_id: 'test-patient-123',
    record_type: 'lab_result',
    data: {
      test_name: 'Complete Blood Count',
      results: {
        wbc: 7.5,
        rbc: 4.8,
        hemoglobin: 14.2,
        platelets: 250
      },
      reference_range: 'Normal',
      date: new Date().toISOString()
    }
  };
  
  testResults.blockchainRecord = check(http.post(`${BASE_URL}/api/${API_VERSION}/blockchain/health-records`, JSON.stringify(healthRecord), { headers }), {
    'blockchain record creation status is 201': (r) => r.status === 201,
    'blockchain record creation response time < 3000ms': (r) => r.timings.duration < 3000,
  });
  
  // Check for any test failures
  const allTests = Object.values(testResults);
  const failedTests = allTests.filter(test => !test);
  
  if (failedTests.length > 0) {
    errorRate.add(1);
  }
  
  // Random sleep between requests to simulate real user behavior
  sleep(Math.random() * 2 + 1); // 1-3 seconds
}

export function teardown(data) {
  console.log('Load test completed');
  console.log(`Final error rate: ${errorRate.value}`);
  console.log(`Average auth token time: ${authTokenTrend.value}`);
}

// Additional test scenarios
export function handleSummary(data) {
  return {
    'load-test-results.json': JSON.stringify({
      timestamp: new Date().toISOString(),
      metrics: {
        http_req_duration: {
          avg: data.metrics.http_req_duration.values.avg,
          p95: data.metrics.http_req_duration.values['p(95)'],
          p99: data.metrics.http_req_duration.values['p(99)']
        },
        http_req_rate: data.metrics.http_req_rate.values.rate,
        http_req_failed: data.metrics.http_req_failed.values.rate,
        errors: data.metrics.errors.values.rate,
        auth_token_time: {
          avg: data.metrics.auth_token_time.values.avg,
          p95: data.metrics.auth_token_time.values['p(95)']
        }
      },
      thresholds: {
        http_req_duration_p95: data.metrics.http_req_duration.values['p(95)'] < 500,
        http_req_failed_rate: data.metrics.http_req_failed.values.rate < 0.1,
        error_rate: data.metrics.errors.values.rate < 0.1
      }
    }, null, 2)
  };
} 