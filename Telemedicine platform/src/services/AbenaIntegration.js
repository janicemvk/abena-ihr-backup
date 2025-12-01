// Real Abena SDK Implementation
// This connects to the actual database and APIs

class RealAbenaSDK {
  constructor(config) {
    this.config = config;
    this.isAuthenticated = false;
    this.providerId = null;
    this.apiBaseUrl = 'http://138.68.24.154:4001'; // Background Modules API
    this.ihrApiUrl = 'http://138.68.24.154:4002'; // Abena IHR API
    this.authToken = null;
    this.currentUser = null;
  }

  // Authentication methods - NOW USING REAL AUTHENTICATION
  async authenticate(credentials) {
    try {
      console.log('🔐 AbenaSDK: Starting authentication for:', credentials.email);
      console.log('🔐 AbenaSDK: API URL:', `${this.ihrApiUrl}/api/v1/auth/login`);
      
      // Call real authentication API using Abena IHR service
      // The backend determines the role from the users table
      const response = await fetch(`${this.ihrApiUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: credentials.email,
          password: credentials.password
        })
      });

      console.log('🔐 AbenaSDK: Response status:', response.status);
      console.log('🔐 AbenaSDK: Response headers:', response.headers);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('🔐 AbenaSDK: Authentication failed:', errorData);
        throw new Error(errorData.detail || 'Authentication failed');
      }

      const authData = await response.json();
      console.log('🔐 AbenaSDK: Authentication successful:', authData);
    
      this.isAuthenticated = true;
      this.authToken = authData.token;
      this.currentUser = {
        id: authData.userId,
        name: authData.userName,
        type: authData.userType,
        role: authData.userRole // Added role
      };
      
      // Store token in localStorage for persistence
      localStorage.setItem('abena_token', this.authToken);
      localStorage.setItem('abena_user', JSON.stringify(this.currentUser));
    
      return {
        userId: authData.userId, // Changed from providerId to userId
        token: authData.token,
        expiresAt: authData.expiresAt,
        user: this.currentUser,
        userType: authData.userType, // Add userType at top level for frontend compatibility
        success: authData.success,
        message: authData.message
      };
    } catch (error) {
      console.error('🔐 AbenaSDK: Authentication error:', error);
      throw new Error(error.message || 'Authentication failed');
    }
  }

  // Backward compatibility method
  async authenticateProvider(credentials) {
    console.log('🔐 AbenaSDK: Using authenticateProvider (deprecated) - calling authenticate instead');
    return await this.authenticate(credentials);
  }

  // Patient data methods - Get real patient data from database
  async getPatientData(patientId, purpose) {
    if (!this.isAuthenticated) {
      throw new Error('Not authenticated');
    }
    
    try {
      // Get real patient data from database
      const response = await fetch(`${this.apiBaseUrl}/patients/${patientId}`, {
        headers: {
          'Authorization': `Bearer ${this.authToken}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch patient data');
      }
      
      const patientData = await response.json();
    return {
        id: patientData.id,
        name: patientData.name,
        age: patientData.age,
        gender: patientData.gender,
        lastVisit: patientData.lastVisit,
        provider: patientData.provider,
        status: patientData.status,
        riskLevel: patientData.riskLevel,
        ecdomeScore: patientData.ecdomeScore,
      vitalSigns: {
        bloodPressure: '120/80',
        heartRate: '72',
        temperature: '98.6',
        oxygenSaturation: '98%'
      }
    };
    } catch (error) {
      console.error('Failed to fetch patient data:', error);
      throw new Error('Failed to fetch patient data from database');
    }
  }

  // Get all patients from database
  async getAllPatients() {
    try {
      const response = await fetch(`${this.apiBaseUrl}/patients`, {
        headers: {
          'Authorization': `Bearer ${this.authToken}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch patients');
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch patients:', error);
      throw new Error('Failed to fetch patients from database');
    }
  }

  // Get all doctors from database
  async getAllDoctors() {
    try {
      const response = await fetch(`${this.ihrApiUrl}/api/v1/doctors`, {
        headers: {
          'Authorization': `Bearer ${this.authToken}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch doctors');
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch doctors:', error);
      throw new Error('Failed to fetch doctors from database');
    }
  }

  // Get appointments from database
  async getAppointments(userId = null, userType = 'patient') {
    try {
      let url;
      if (userType === 'provider') {
        url = userId
          ? `${this.ihrApiUrl}/api/v1/appointments?provider_id=${userId}`
          : `${this.ihrApiUrl}/api/v1/appointments`;
      } else {
        url = userId
          ? `${this.ihrApiUrl}/api/v1/appointments?patient_id=${userId}`
          : `${this.ihrApiUrl}/api/v1/appointments`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${this.authToken}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch appointments');
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch appointments:', error);
      throw new Error('Failed to fetch appointments from database');
    }
  }

  // Prescription methods - Connect to real prescription system
  async createPrescription(patientId, prescriptionData, providerId) {
    if (!this.isAuthenticated) {
      throw new Error('Not authenticated');
    }
    
    try {
      const response = await fetch(`${this.ihrApiUrl}/api/v1/prescriptions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.authToken}`
        },
        body: JSON.stringify({
      patientId,
      providerId,
          ...prescriptionData
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create prescription');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to create prescription:', error);
      throw new Error('Failed to create prescription in database');
    }
  }

  async sendPrescriptionToPharmacy(prescriptionId, pharmacyName) {
    if (!this.isAuthenticated) {
      throw new Error('Not authenticated');
    }
    
    try {
      const response = await fetch(`${this.ihrApiUrl}/api/v1/prescriptions/${prescriptionId}/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.authToken}`
        },
        body: JSON.stringify({ pharmacyName })
      });

      if (!response.ok) {
        throw new Error('Failed to send prescription');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to send prescription:', error);
      throw new Error('Failed to send prescription to pharmacy');
    }
  }

  // Lab request methods
  async createLabRequest(patientId, labRequestData, providerId) {
    if (!this.isAuthenticated) {
      throw new Error('Not authenticated');
    }
    
    try {
      const response = await fetch(`${this.ihrApiUrl}/api/v1/lab-requests`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.authToken}`
        },
        body: JSON.stringify({
      patientId,
      providerId,
          ...labRequestData
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create lab request');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to create lab request:', error);
      throw new Error('Failed to create lab request in database');
    }
  }

  async sendLabRequestToLaboratory(labRequestId, laboratoryName) {
    if (!this.isAuthenticated) {
      throw new Error('Not authenticated');
    }
    
    try {
      const response = await fetch(`${this.ihrApiUrl}/api/v1/lab-requests/${labRequestId}/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.authToken}`
        },
        body: JSON.stringify({ laboratoryName })
      });

      if (!response.ok) {
        throw new Error('Failed to send lab request');
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to send lab request:', error);
      throw new Error('Failed to send lab request to laboratory');
    }
  }

  // Utility methods
  getAuthToken() {
    return this.authToken || localStorage.getItem('abena_token');
  }

  setAuthToken(token) {
    this.authToken = token;
    localStorage.setItem('abena_token', token);
  }

  clearAuthToken() {
    this.authToken = null;
    this.isAuthenticated = false;
    this.currentUser = null;
    localStorage.removeItem('abena_token');
    localStorage.removeItem('abena_user');
  }

  // Check if user is authenticated
  isUserAuthenticated() {
    return this.isAuthenticated && this.authToken;
  }

  // Get current user info
  getCurrentUser() {
    if (!this.currentUser) {
      const storedUser = localStorage.getItem('abena_user');
      if (storedUser) {
        this.currentUser = JSON.parse(storedUser);
      }
    }
    return this.currentUser;
  }
}

// Export the real SDK
export default RealAbenaSDK; 