/**
 * Patient Service API Client
 * Connects to Patient Service backend (port 3003)
 */

const PATIENT_SERVICE_URL = process.env.NEXT_PUBLIC_PATIENT_SERVICE_URL || 'http://localhost:3003';

export interface Patient {
  patient_id: string;
  mrn: string;
  first_name: string;
  last_name: string;
  date_of_birth?: string;
  gender?: string;
  email?: string;
  phone?: string;
  created_at: string;
  updated_at?: string;
}

export interface PatientResponse {
  success: boolean;
  patient?: Patient;
  patients?: Patient[];
  count?: number;
  error?: string;
  message?: string;
}

const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token') || localStorage.getItem('jwt_token');
  }
  return null;
};

const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${PATIENT_SERVICE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || error.message || `HTTP ${response.status}`);
  }

  return response.json();
};

export const patientService = {
  /**
   * Get all patients
   */
  getAll: async (filters?: {
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<PatientResponse> => {
    const queryParams = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const queryString = queryParams.toString();
    return apiRequest<PatientResponse>(
      `/api/patients${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get patient by ID
   */
  getById: async (patientId: string): Promise<PatientResponse> => {
    return apiRequest<PatientResponse>(`/api/patients/${patientId}`);
  },

  /**
   * Create patient
   */
  create: async (data: {
    mrn: string;
    first_name: string;
    last_name: string;
    date_of_birth?: string;
    gender?: string;
    email?: string;
    phone?: string;
  }): Promise<PatientResponse> => {
    return apiRequest<PatientResponse>('/api/patients', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update patient
   */
  update: async (
    patientId: string,
    data: Partial<Omit<Patient, 'patient_id' | 'created_at'>>
  ): Promise<PatientResponse> => {
    return apiRequest<PatientResponse>(`/api/patients/${patientId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete patient
   */
  delete: async (patientId: string): Promise<PatientResponse> => {
    return apiRequest<PatientResponse>(`/api/patients/${patientId}`, {
      method: 'DELETE',
    });
  },

  /**
   * Health check
   */
  health: async (): Promise<{ status: string; service: string; database: string }> => {
    return apiRequest('/health');
  },
};

