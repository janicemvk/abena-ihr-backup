import AbenaSDK from '../index';

// Mock axios for testing
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    post: jest.fn(),
    get: jest.fn(),
    interceptors: {
      request: {
        use: jest.fn()
      }
    }
  }))
}));

describe('AbenaSDK', () => {
  let sdk: AbenaSDK;
  const mockConfig = {
    authServiceUrl: 'https://auth.test.com',
    dataServiceUrl: 'https://data.test.com',
    privacyServiceUrl: 'https://privacy.test.com',
    blockchainServiceUrl: 'https://blockchain.test.com',
    timeout: 10000
  };

  beforeEach(() => {
    sdk = new AbenaSDK(mockConfig);
  });

  describe('Initialization', () => {
    it('should create SDK instance with correct configuration', () => {
      expect(sdk).toBeInstanceOf(AbenaSDK);
    });

    it('should set default timeout if not provided', () => {
      const sdkWithoutTimeout = new AbenaSDK({
        authServiceUrl: 'https://auth.test.com',
        dataServiceUrl: 'https://data.test.com',
        privacyServiceUrl: 'https://privacy.test.com',
        blockchainServiceUrl: 'https://blockchain.test.com'
      });
      expect(sdkWithoutTimeout).toBeInstanceOf(AbenaSDK);
    });
  });

  describe('Authentication', () => {
    it('should handle login request', async () => {
      const mockResponse = {
        data: {
          user: {
            id: 'user-123',
            email: 'test@example.com',
            role: 'doctor',
            firstName: 'John',
            lastName: 'Doe'
          },
          token: 'jwt-token-123'
        }
      };

      // Mock the auth client post method
      const mockAuthClient = {
        post: jest.fn().mockResolvedValue(mockResponse)
      };
      (sdk as any).authClient = mockAuthClient;

      const result = await sdk.login('test@example.com', 'password');

      expect(result).toEqual(mockResponse.data);
      expect(mockAuthClient.post).toHaveBeenCalledWith('/auth/login', {
        email: 'test@example.com',
        password: 'password'
      });
    });

    it('should handle login with MFA token', async () => {
      const mockResponse = {
        data: {
          user: { id: 'user-123', email: 'test@example.com', role: 'doctor', firstName: 'John', lastName: 'Doe' },
          token: 'jwt-token-123'
        }
      };

      const mockAuthClient = {
        post: jest.fn().mockResolvedValue(mockResponse)
      };
      (sdk as any).authClient = mockAuthClient;

      await sdk.login('test@example.com', 'password', 'mfa-token');

      expect(mockAuthClient.post).toHaveBeenCalledWith('/auth/login', {
        email: 'test@example.com',
        password: 'password',
        mfaToken: 'mfa-token'
      });
    });
  });

  describe('Data Access', () => {
    it('should get patient data with access validation', async () => {
      const mockAccessResponse = {
        data: {
          granted: true,
          riskScore: 0.1,
          conditions: [],
          reason: 'Access granted'
        }
      };

      const mockPatientResponse = {
        data: {
          patientId: 'patient-123',
          demographics: { name: 'John Doe' },
          healthRecords: [],
          consents: [],
          accessLog: []
        }
      };

      const mockAuthClient = {
        post: jest.fn().mockResolvedValue(mockAccessResponse)
      };
      const mockDataClient = {
        get: jest.fn().mockResolvedValue(mockPatientResponse)
      };
      const mockBlockchainClient = {
        post: jest.fn().mockResolvedValue({ data: { blockchain_tx_id: 'tx-123' } })
      };

      (sdk as any).authClient = mockAuthClient;
      (sdk as any).dataClient = mockDataClient;
      (sdk as any).blockchainClient = mockBlockchainClient;

      const result = await sdk.getPatientData('patient-123', 'clinical_care');

      expect(result).toEqual(mockPatientResponse.data);
      expect(mockAuthClient.post).toHaveBeenCalledWith('/auth/validate-access', {
        patientId: 'patient-123',
        action: 'read',
        service: 'data_access'
      });
    });

    it('should throw error when access is denied', async () => {
      const mockAccessResponse = {
        data: {
          granted: false,
          riskScore: 0.9,
          conditions: ['high_risk'],
          reason: 'Access denied due to high risk'
        }
      };

      const mockAuthClient = {
        post: jest.fn().mockResolvedValue(mockAccessResponse)
      };
      (sdk as any).authClient = mockAuthClient;

      await expect(sdk.getPatientData('patient-123', 'clinical_care'))
        .rejects
        .toThrow('Access denied: Access denied due to high risk');
    });
  });

  describe('Privacy & Security', () => {
    it('should encrypt sensitive data', async () => {
      const mockResponse = {
        data: {
          encrypted_data: 'encrypted-string-123'
        }
      };

      const mockPrivacyClient = {
        post: jest.fn().mockResolvedValue(mockResponse)
      };
      (sdk as any).privacyClient = mockPrivacyClient;

      const result = await sdk.encryptSensitiveData(
        { ssn: '123-45-6789' },
        'demographics',
        'patient-123'
      );

      expect(result).toBe('encrypted-string-123');
      expect(mockPrivacyClient.post).toHaveBeenCalledWith('/encrypt', {
        data: { ssn: '123-45-6789' },
        data_type: 'demographics',
        patient_id: 'patient-123',
        purpose: 'data_protection'
      });
    });

    it('should check patient consent', async () => {
      const mockResponse = {
        data: {
          hasConsent: true
        }
      };

      const mockPrivacyClient = {
        get: jest.fn().mockResolvedValue(mockResponse)
      };
      (sdk as any).privacyClient = mockPrivacyClient;

      const result = await sdk.checkPatientConsent(
        'patient-123',
        'provider-456',
        'clinical_care'
      );

      expect(result).toBe(true);
      expect(mockPrivacyClient.get).toHaveBeenCalledWith('/check-consent', {
        params: {
          patientId: 'patient-123',
          providerId: 'provider-456',
          purpose: 'clinical_care'
        }
      });
    });
  });

  describe('Blockchain', () => {
    it('should log blockchain access', async () => {
      const mockResponse = {
        data: {
          blockchain_tx_id: 'tx-123456'
        }
      };

      const mockBlockchainClient = {
        post: jest.fn().mockResolvedValue(mockResponse)
      };
      (sdk as any).blockchainClient = mockBlockchainClient;

      const result = await sdk.logBlockchainAccess(
        'patient-123',
        'READ',
        'clinical_care',
        { riskScore: 0.1 }
      );

      expect(result).toBe('tx-123456');
      expect(mockBlockchainClient.post).toHaveBeenCalledWith('/records/patient-123/access', {
        purpose: 'clinical_care',
        action: 'READ',
        metadata: { riskScore: 0.1 }
      });
    });

    it('should handle blockchain logging failure gracefully', async () => {
      const mockBlockchainClient = {
        post: jest.fn().mockRejectedValue(new Error('Blockchain service down'))
      };
      (sdk as any).blockchainClient = mockBlockchainClient;

      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      const result = await sdk.logBlockchainAccess(
        'patient-123',
        'READ',
        'clinical_care'
      );

      expect(result).toBe('');
      expect(consoleSpy).toHaveBeenCalledWith('Blockchain logging failed:', expect.any(Error));

      consoleSpy.mockRestore();
    });
  });

  describe('Utilities', () => {
    it('should check service health', async () => {
      const mockAuthClient = { get: jest.fn().mockResolvedValue({}) };
      const mockDataClient = { get: jest.fn().mockResolvedValue({}) };
      const mockPrivacyClient = { get: jest.fn().mockResolvedValue({}) };
      const mockBlockchainClient = { get: jest.fn().mockRejectedValue(new Error('Service down')) };

      (sdk as any).authClient = mockAuthClient;
      (sdk as any).dataClient = mockDataClient;
      (sdk as any).privacyClient = mockPrivacyClient;
      (sdk as any).blockchainClient = mockBlockchainClient;

      const result = await sdk.healthCheck();

      expect(result).toEqual({
        auth: true,
        data: true,
        privacy: true,
        blockchain: false
      });
    });

    it('should manage auth token', () => {
      sdk.setAuthToken('new-token-123');
      expect((sdk as any).currentToken).toBe('new-token-123');

      sdk.clearAuthToken();
      expect((sdk as any).currentToken).toBeNull();
    });
  });
}); 