import React, { useState } from 'react';
import { Shield, Zap, CheckCircle, Activity, Key, Lock, Brain, Database } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const AbenaDataIngestionLayer = () => {
  // Data Ingestion State Management
  const [ingestionStatus] = useState({
    apiGateway: { status: 'active', requests: 1247, errors: 3, latency: 45 },
    dataValidators: { status: 'active', processed: 2341, validated: 2298, rejected: 43 },
    formatConverters: { status: 'active', converted: 1876, formats: 12, efficiency: 98.7 },
    realtimeProcessors: { status: 'active', streams: 47, throughput: 15420, bufferUsage: 23 }
  });

  const [dataStreams] = useState([
    { id: 'patient-input', name: 'Patient Direct Input', type: 'user', status: 'active', rate: '150/min', format: 'JSON', priority: 'high' },
    { id: 'iot-wearables', name: 'IoT & Wearables', type: 'streaming', status: 'active', rate: '2.3k/min', format: 'MQTT', priority: 'medium' },
    { id: 'emr-systems', name: 'EMR Integration', type: 'batch', status: 'active', rate: '45/min', format: 'HL7/FHIR', priority: 'high' },
    { id: 'lab-results', name: 'Laboratory Results', type: 'batch', status: 'active', rate: '23/min', format: 'XML/JSON', priority: 'critical' },
    { id: 'imaging-data', name: 'Medical Imaging', type: 'file', status: 'active', rate: '8/min', format: 'DICOM', priority: 'high' },
    { id: 'environmental', name: 'Environmental Sensors', type: 'streaming', status: 'active', rate: '890/min', format: 'Custom', priority: 'low' }
  ]);

  // Real-time processing metrics
  const [processingMetrics] = useState([
    { time: '00:00', throughput: 12500, latency: 45, errors: 2 },
    { time: '00:05', throughput: 13200, latency: 42, errors: 1 },
    { time: '00:10', throughput: 14100, latency: 38, errors: 0 },
    { time: '00:15', throughput: 15420, latency: 35, errors: 1 },
    { time: '00:20', throughput: 14800, latency: 41, errors: 3 }
  ]);

  // Enhanced Authentication System
  const [authConfig] = useState({
    oauth2: {
      enabled: true,
      providers: ['Google Health', 'Apple HealthKit', 'Microsoft Health'],
      scopes: ['read:health', 'write:health', 'read:ecbome'],
      tokenExpiry: 3600,
      refreshEnabled: true
    },
    apiKeys: {
      enabled: true,
      rateLimits: { basic: '1000/hour', premium: '10000/hour', enterprise: 'unlimited' },
      keyRotation: 'automatic',
      encryption: 'AES-256'
    },
    mTLS: {
      enabled: true,
      certificateAuthority: 'Internal CA',
      clientCertValidation: true,
      revocationCheck: true
    }
  });

  // eCBome Correlation Engine State
  const [correlationEngine] = useState({
    realtimeCorrelations: [
      { biomarker: 'AEA', incomingData: 'Heart Rate', correlation: 0.87, confidence: 94, pattern: 'Stress Response' },
      { biomarker: '2-AG', incomingData: 'Sleep Quality', correlation: 0.92, confidence: 89, pattern: 'Circadian Rhythm' },
      { biomarker: 'Cortisol', incomingData: 'Mood Score', correlation: -0.84, confidence: 91, pattern: 'Stress-Mood Axis' },
      { biomarker: 'CB1 Expression', incomingData: 'Activity Level', correlation: 0.78, confidence: 85, pattern: 'Motor Function' },
      { biomarker: 'Inflammatory Markers', incomingData: 'Dietary Input', correlation: 0.73, confidence: 82, pattern: 'Gut-Brain Axis' }
    ],
    processingStats: {
      correlationsPerSecond: 247,
      patternRecognitions: 34,
      anomaliesDetected: 3,
      confidenceThreshold: 80
    }
  });

  const [correlationData] = useState([
    { time: '00:00', AEA_HeartRate: 0.87, AG2_Sleep: 0.92, Cortisol_Mood: 0.84 },
    { time: '00:05', AEA_HeartRate: 0.89, AG2_Sleep: 0.89, Cortisol_Mood: 0.86 },
    { time: '00:10', AEA_HeartRate: 0.85, AG2_Sleep: 0.94, Cortisol_Mood: 0.82 },
    { time: '00:15', AEA_HeartRate: 0.91, AG2_Sleep: 0.87, Cortisol_Mood: 0.88 },
    { time: '00:20', AEA_HeartRate: 0.88, AG2_Sleep: 0.93, Cortisol_Mood: 0.85 }
  ]);

  // Enhanced API Gateway Component with Authentication
  const APIGateway = () => {
    const [activeTokens] = useState([
      { id: '1', type: 'OAuth2', user: 'patient@example.com', scope: 'read:health', expires: '2h 15m', status: 'active' },
      { id: '2', type: 'API Key', application: 'IoT Gateway', tier: 'enterprise', lastUsed: '2m ago', status: 'active' },
      { id: '3', type: 'mTLS', client: 'EMR System', certificate: 'Valid', expires: '30 days', status: 'active' },
      { id: '4', type: 'OAuth2', user: 'provider@clinic.com', scope: 'write:health', expires: '45m', status: 'active' }
    ]);

    const [securityMetrics] = useState({
      authAttempts: 1247,
      successfulAuth: 1243,
      failedAuth: 4,
      blockedIPs: 2,
      revokedTokens: 0
    });

    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-blue-500">
        <h3 className="text-xl font-bold text-blue-900 mb-4 flex items-center">
          <Shield className="w-6 h-6 mr-2" />
          Enhanced API Gateway - Multi-Layer Security
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* OAuth2 Configuration */}
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-blue-800 mb-3 flex items-center">
              <Key className="w-5 h-5 mr-2" />
              OAuth2 Integration
            </h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Status:</span>
                <span className="text-green-600 font-medium">Active</span>
              </div>
              <div className="flex justify-between">
                <span>Providers:</span>
                <span className="text-blue-700">{authConfig.oauth2.providers.length}</span>
              </div>
              <div className="flex justify-between">
                <span>Token Expiry:</span>
                <span className="text-blue-700">{authConfig.oauth2.tokenExpiry}s</span>
              </div>
              <div className="flex justify-between">
                <span>Refresh:</span>
                <span className="text-green-600">Enabled</span>
              </div>
            </div>
            
            <div className="mt-3 p-2 bg-blue-100 rounded text-xs">
              <strong>Scopes:</strong><br/>
              {authConfig.oauth2.scopes.join(', ')}
            </div>
          </div>

          {/* API Key Management */}
          <div className="p-4 bg-green-50 rounded-lg">
            <h4 className="font-semibold text-green-800 mb-3 flex items-center">
              <Database className="w-5 h-5 mr-2" />
              API Key Management
            </h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Basic Tier:</span>
                <span className="text-green-700">{authConfig.apiKeys.rateLimits.basic}</span>
              </div>
              <div className="flex justify-between">
                <span>Premium Tier:</span>
                <span className="text-green-700">{authConfig.apiKeys.rateLimits.premium}</span>
              </div>
              <div className="flex justify-between">
                <span>Enterprise:</span>
                <span className="text-green-700">{authConfig.apiKeys.rateLimits.enterprise}</span>
              </div>
              <div className="flex justify-between">
                <span>Rotation:</span>
                <span className="text-green-600">Automatic</span>
              </div>
            </div>
            
            <div className="mt-3 p-2 bg-green-100 rounded text-xs">
              <strong>Encryption:</strong> {authConfig.apiKeys.encryption}
            </div>
          </div>

          {/* mTLS Configuration */}
          <div className="p-4 bg-purple-50 rounded-lg">
            <h4 className="font-semibold text-purple-800 mb-3 flex items-center">
              <Lock className="w-5 h-5 mr-2" />
              Mutual TLS (mTLS)
            </h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Certificate CA:</span>
                <span className="text-purple-700">Internal</span>
              </div>
              <div className="flex justify-between">
                <span>Client Validation:</span>
                <span className="text-green-600">Active</span>
              </div>
              <div className="flex justify-between">
                <span>Revocation Check:</span>
                <span className="text-green-600">Enabled</span>
              </div>
              <div className="flex justify-between">
                <span>Auto-Renewal:</span>
                <span className="text-green-600">30 days</span>
              </div>
            </div>
            
            <div className="mt-3 p-2 bg-purple-100 rounded text-xs">
              <strong>Security Level:</strong> Enterprise Grade
            </div>
          </div>
        </div>

        {/* Active Tokens */}
        <div className="mt-6">
          <h4 className="text-lg font-semibold text-gray-800 mb-4">Active Authentication Tokens</h4>
          <div className="space-y-2">
            {activeTokens.map((token) => (
              <div key={token.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full ${
                    token.status === 'active' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <div>
                    <span className="font-medium text-gray-800">{token.type}</span>
                    <div className="text-sm text-gray-600">
                      {token.user || token.application || token.client}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-700">
                    {token.expires || token.lastUsed}
                  </div>
                  <div className="text-xs text-gray-500">
                    {token.scope || token.tier || token.certificate}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Security Metrics */}
        <div className="mt-4 p-4 bg-green-50 rounded-lg">
          <h4 className="font-semibold text-green-800 mb-2">Gateway Security Metrics</h4>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-700">{securityMetrics.authAttempts}</div>
              <div className="text-sm text-blue-600">Auth Attempts</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-700">{securityMetrics.successfulAuth}</div>
              <div className="text-sm text-green-600">Successful</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-700">{securityMetrics.failedAuth}</div>
              <div className="text-sm text-red-600">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-700">{securityMetrics.blockedIPs}</div>
              <div className="text-sm text-orange-600">Blocked IPs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-700">{securityMetrics.revokedTokens}</div>
              <div className="text-sm text-purple-600">Revoked Tokens</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Data Validators Component
  const DataValidators = () => {
    const [validationResults] = useState([
      { rule: 'Schema Validation', passed: 2298, failed: 23, accuracy: 99.0 },
      { rule: 'Range Validation', passed: 2267, failed: 54, accuracy: 97.7 },
      { rule: 'Format Validation', passed: 2310, failed: 11, accuracy: 99.5 },
      { rule: 'HIPAA Compliance', passed: 2321, failed: 0, accuracy: 100 },
      { rule: 'Freshness Check', passed: 2289, failed: 32, accuracy: 98.6 }
    ]);

    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-green-500">
        <h3 className="text-xl font-bold text-green-900 mb-4 flex items-center">
          <CheckCircle className="w-6 h-6 mr-2" />
          Data Validators - Quality & Integrity
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-green-800 mb-3">Validation Rules</h4>
            <div className="space-y-3">
              {validationResults.map((result, index) => (
                <div key={index} className="p-3 bg-green-50 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-green-800">{result.rule}</span>
                    <span className="text-sm font-bold text-green-700">{result.accuracy}%</span>
                  </div>
                  <div className="w-full bg-green-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${result.accuracy}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-green-600 mt-1">
                    Passed: {result.passed} | Failed: {result.failed}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold text-green-800 mb-3">Validation Logic Example</h4>
            <div className="bg-green-50 p-4 rounded-lg">
              <pre className="text-xs text-green-800 overflow-x-auto">
{`// Enhanced eCBome Data Validation
const validateeCBomeData = (data) => {
  // Required fields check
  if (!data.patientId || !data.timestamp) {
    return { valid: false, error: 'Missing required fields' };
  }
  
  // eCBome biomarker validation
  if (data.AEA && (data.AEA < 0.1 || data.AEA > 0.5)) {
    return { valid: false, error: 'AEA levels out of range' };
  }
  
  // Real-time correlation check
  const correlation = correlationEngine.validate(data);
  if (correlation.confidence < 80) {
    return { valid: false, error: 'Low correlation confidence' };
  }
  
  return { valid: true, correlation };
};`}
              </pre>
            </div>
          </div>
        </div>

        <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
          <h4 className="font-semibold text-yellow-800 mb-2">Data Quality Metrics</h4>
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-700">{ingestionStatus.dataValidators.processed}</div>
              <div className="text-sm text-yellow-600">Records Processed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-700">{ingestionStatus.dataValidators.validated}</div>
              <div className="text-sm text-yellow-600">Validated</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-700">{ingestionStatus.dataValidators.rejected}</div>
              <div className="text-sm text-yellow-600">Rejected</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-700">98.2%</div>
              <div className="text-sm text-yellow-600">Quality Score</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Enhanced eCBome Correlation Engine Component
  const ECBomeCorrelationEngine = () => {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-purple-500">
        <h3 className="text-xl font-bold text-purple-900 mb-4 flex items-center">
          <Brain className="w-6 h-6 mr-2" />
          eCBome Correlation Engine - Real-time Intelligence
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-purple-800 mb-3">Real-time Correlations</h4>
            <div className="space-y-3">
              {correlationEngine.realtimeCorrelations.map((corr, index) => (
                <div key={index} className="p-3 bg-purple-50 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <span className="font-medium text-purple-800">{corr.biomarker}</span>
                      <div className="text-sm text-purple-600">↔ {corr.incomingData}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-purple-700">{corr.correlation}</div>
                      <div className="text-xs text-purple-600">{corr.confidence}% confidence</div>
                    </div>
                  </div>
                  <div className="w-full bg-purple-200 rounded-full h-2">
                    <div 
                      className="bg-purple-500 h-2 rounded-full"
                      style={{ width: `${Math.abs(corr.correlation) * 100}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-purple-700 mt-1">
                    Pattern: {corr.pattern}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold text-purple-800 mb-3">Correlation Algorithm</h4>
            <div className="space-y-3">
              <div className="p-3 bg-purple-50 rounded-lg">
                <h5 className="font-medium text-purple-800 mb-2">1. Data Stream Analysis</h5>
                <p className="text-sm text-purple-700">Real-time analysis of incoming data streams for eCBome biomarker patterns</p>
              </div>
              <div className="p-3 bg-purple-50 rounded-lg">
                <h5 className="font-medium text-purple-800 mb-2">2. Pattern Recognition</h5>
                <p className="text-sm text-purple-700">AI identifies correlations between lifestyle data and eCBome markers</p>
              </div>
              <div className="p-3 bg-purple-50 rounded-lg">
                <h5 className="font-medium text-purple-800 mb-2">3. Confidence Scoring</h5>
                <p className="text-sm text-purple-700">Statistical confidence levels ensure reliable correlations</p>
              </div>
              <div className="p-3 bg-purple-50 rounded-lg">
                <h5 className="font-medium text-purple-800 mb-2">4. Real-time Alerting</h5>
                <p className="text-sm text-purple-700">Immediate notifications when significant patterns are detected</p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 p-4 bg-indigo-50 rounded-lg">
          <h4 className="font-semibold text-indigo-800 mb-2">Engine Performance</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-700">{correlationEngine.processingStats.correlationsPerSecond}</div>
              <div className="text-sm text-indigo-600">Correlations/Sec</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-700">{correlationEngine.processingStats.patternRecognitions}</div>
              <div className="text-sm text-green-600">Patterns Found</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-700">{correlationEngine.processingStats.anomaliesDetected}</div>
              <div className="text-sm text-yellow-600">Anomalies</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-700">{correlationEngine.processingStats.confidenceThreshold}%</div>
              <div className="text-sm text-purple-600">Min Confidence</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Format Converters Component
  const FormatConverters = () => {
    const [supportedFormats] = useState([
      { format: 'HL7 FHIR', type: 'Clinical', status: 'active', conversions: 234, success: 99.1 },
      { format: 'DICOM', type: 'Imaging', status: 'active', conversions: 45, success: 100 },
      { format: 'JSON', type: 'IoT/API', status: 'active', conversions: 1247, success: 99.8 },
      { format: 'XML', type: 'Lab Results', status: 'active', conversions: 156, success: 98.7 },
      { format: 'CSV', type: 'Batch Data', status: 'active', conversions: 89, success: 97.8 },
      { format: 'MQTT', type: 'Streaming', status: 'active', conversions: 2341, success: 99.5 }
    ]);

    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-orange-500">
        <h3 className="text-xl font-bold text-orange-900 mb-4 flex items-center">
          <Zap className="w-6 h-6 mr-2" />
          Format Converters - Universal Data Standardization
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-orange-800 mb-3">Supported Formats</h4>
            <div className="space-y-2">
              {supportedFormats.map((format, index) => (
                <div key={index} className="p-3 bg-orange-50 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div>
                      <span className="font-medium text-orange-800">{format.format}</span>
                      <div className="text-sm text-orange-600">{format.type}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-orange-700">{format.success}%</div>
                      <div className="text-xs text-orange-600">{format.conversions} converted</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold text-orange-800 mb-3">Conversion Pipeline</h4>
            <div className="space-y-3">
              <div className="p-3 bg-orange-50 rounded-lg">
                <h5 className="font-medium text-orange-800 mb-2">1. Format Detection</h5>
                <p className="text-sm text-orange-700">Automatically identify incoming data format using content analysis and headers</p>
              </div>
              <div className="p-3 bg-orange-50 rounded-lg">
                <h5 className="font-medium text-orange-800 mb-2">2. Schema Mapping</h5>
                <p className="text-sm text-orange-700">Map source fields to Abena standardized schema with eCBome integration points</p>
              </div>
              <div className="p-3 bg-orange-50 rounded-lg">
                <h5 className="font-medium text-orange-800 mb-2">3. Data Transformation</h5>
                <p className="text-sm text-orange-700">Convert to unified JSON format with eCBome correlation markers</p>
              </div>
              <div className="p-3 bg-orange-50 rounded-lg">
                <h5 className="font-medium text-orange-800 mb-2">4. Quality Assurance</h5>
                <p className="text-sm text-orange-700">Validate converted data meets Abena standards and eCBome requirements</p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 p-4 bg-indigo-50 rounded-lg">
          <h4 className="font-semibold text-indigo-800 mb-2">Conversion Performance</h4>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-700">{ingestionStatus.formatConverters.converted}</div>
              <div className="text-sm text-indigo-600">Records Converted</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-700">{ingestionStatus.formatConverters.formats}</div>
              <div className="text-sm text-indigo-600">Formats Supported</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-700">{ingestionStatus.formatConverters.efficiency}%</div>
              <div className="text-sm text-indigo-600">Efficiency</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Real-time Processors Component
  const RealtimeProcessors = () => {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-red-500">
        <h3 className="text-xl font-bold text-red-900 mb-4 flex items-center">
          <Activity className="w-6 h-6 mr-2" />
          Real-time Processors - Streaming Data Engine
        </h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-red-800 mb-3">Active Data Streams</h4>
            <div className="space-y-2">
              {dataStreams.map((stream, index) => (
                <div key={index} className="p-3 bg-red-50 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="font-medium text-red-800">{stream.name}</span>
                      <div className="text-sm text-red-600">
                        {stream.format} | {stream.rate}
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-1 text-xs rounded ${
                        stream.status === 'active' ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
                      }`}>
                        {stream.status}
                      </span>
                      <div className={`text-xs mt-1 ${
                        stream.priority === 'critical' ? 'text-red-600' :
                        stream.priority === 'high' ? 'text-orange-600' :
                        stream.priority === 'medium' ? 'text-yellow-600' :
                        'text-gray-600'
                      }`}>
                        {stream.priority} priority
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold text-red-800 mb-3">Processing Architecture</h4>
            <div className="space-y-3">
              <div className="p-3 bg-red-50 rounded-lg">
                <h5 className="font-medium text-red-800 mb-2">Stream Ingestion</h5>
                <p className="text-sm text-red-700">Apache Kafka clusters handle high-throughput data streams with automatic partitioning</p>
              </div>
              <div className="p-3 bg-red-50 rounded-lg">
                <h5 className="font-medium text-red-800 mb-2">Real-time Processing</h5>
                <p className="text-sm text-red-700">Apache Flink processes streams with eCBome correlation analysis in sub-second latency</p>
              </div>
              <div className="p-3 bg-red-50 rounded-lg">
                <h5 className="font-medium text-red-800 mb-2">Buffer Management</h5>
                <p className="text-sm text-red-700">Redis-based buffering ensures no data loss during processing spikes</p>
              </div>
              <div className="p-3 bg-red-50 rounded-lg">
                <h5 className="font-medium text-red-800 mb-2">eCBome Integration</h5>
                <p className="text-sm text-red-700">Real-time biomarker correlation with all incoming health data streams</p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-2">Streaming Performance</h4>
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-red-700">{ingestionStatus.realtimeProcessors.streams}</div>
              <div className="text-sm text-red-600">Active Streams</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-700">{ingestionStatus.realtimeProcessors.throughput}</div>
              <div className="text-sm text-red-600">Records/Min</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-700">{ingestionStatus.realtimeProcessors.bufferUsage}%</div>
              <div className="text-sm text-red-600">Buffer Usage</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-700">99.95%</div>
              <div className="text-sm text-red-600">Availability</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8 bg-gradient-to-br from-gray-50 to-blue-50 p-6 rounded-xl">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-indigo-900 mb-2">
          🔄 Abena Data Ingestion Layer
        </h1>
        <p className="text-xl text-indigo-700">
          Enterprise-Grade Data Pipeline with Enhanced Security & eCBome Intelligence
        </p>
      </div>

      {/* Overall Status Dashboard */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Enhanced Ingestion Layer Status</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
            <Shield className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-blue-800">Multi-Auth</div>
            <div className="text-sm text-blue-600">API Gateway</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
            <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-green-800">98.2%</div>
            <div className="text-sm text-green-600">Data Quality</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg border-l-4 border-purple-500">
            <Brain className="w-8 h-8 text-purple-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-purple-800">247</div>
            <div className="text-sm text-purple-600">eCBome Correlations/Sec</div>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg border-l-4 border-orange-500">
            <Activity className="w-8 h-8 text-orange-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-orange-800">15.4k</div>
            <div className="text-sm text-orange-600">Records/Min</div>
          </div>
        </div>
      </div>

      {/* Real-time Performance Chart */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Real-time Processing Metrics</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={processingMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="throughput" stroke="#8884d8" strokeWidth={2} name="Throughput (records/min)" />
              <Line yAxisId="right" type="monotone" dataKey="latency" stroke="#82ca9d" strokeWidth={2} name="Latency (ms)" />
              <Line yAxisId="right" type="monotone" dataKey="errors" stroke="#ffc658" strokeWidth={2} name="Errors" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* eCBome Correlation Visualization */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Real-time eCBome Correlation Tracking</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={correlationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="AEA_HeartRate" stroke="#8884d8" strokeWidth={2} name="AEA ↔ Heart Rate" />
              <Line type="monotone" dataKey="AG2_Sleep" stroke="#82ca9d" strokeWidth={2} name="2-AG ↔ Sleep Quality" />
              <Line type="monotone" dataKey="Cortisol_Mood" stroke="#ffc658" strokeWidth={2} name="Cortisol ↔ Mood" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Core Components */}
      <div className="space-y-8">
        <APIGateway />
        <DataValidators />
        <ECBomeCorrelationEngine />
        <FormatConverters />
        <RealtimeProcessors />
      </div>

      {/* Enhanced Integration Summary */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-6 rounded-lg">
        <h2 className="text-2xl font-bold mb-4">🚀 Enhanced Data Ingestion Layer Capabilities</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h3 className="font-semibold mb-2">🔒 Enhanced Security & Authentication</h3>
            <ul className="text-sm space-y-1 opacity-90">
              <li>• Multi-layer authentication (OAuth2, API Keys, mTLS)</li>
              <li>• Patient-controlled data access permissions</li>
              <li>• Real-time token validation and refresh</li>
              <li>• HIPAA-compliant audit trails</li>
              <li>• Automatic threat detection and blocking</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">🧠 eCBome Intelligence Integration</h3>
            <ul className="text-sm space-y-1 opacity-90">
              <li>• Real-time correlation of all incoming data</li>
              <li>• AI pattern recognition with 80%+ confidence</li>
              <li>• 247 correlations processed per second</li>
              <li>• Biomarker-lifestyle correlation analysis</li>
              <li>• Continuous learning from patient outcomes</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">⚡ Enterprise Performance & Scale</h3>
            <ul className="text-sm space-y-1 opacity-90">
              <li>• 15,000+ records/minute throughput</li>
              <li>• Sub-second processing latency</li>
              <li>• 99.95% system availability</li>
              <li>• Auto-scaling based on load</li>
              <li>• Multi-region data replication</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AbenaDataIngestionLayer; 