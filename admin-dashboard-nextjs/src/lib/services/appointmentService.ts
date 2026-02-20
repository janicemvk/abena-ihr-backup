/**
 * Appointment Service API Client
 * Connects to Appointment Service backend (port 3009)
 */

const APPOINTMENT_SERVICE_URL = process.env.NEXT_PUBLIC_APPOINTMENT_SERVICE_URL || 'http://localhost:3009';

export interface Appointment {
  appointment_id: string;
  patient_id: string;
  provider_id?: string;
  appointment_date: string;
  appointment_time: string;
  duration: number;
  appointment_type: string;
  location: string;
  status: string;
  notes?: string;
  reminder: boolean;
  created_at: string;
  updated_at?: string;
}

export interface AppointmentResponse {
  success: boolean;
  appointment?: Appointment;
  appointments?: Appointment[];
  count?: number;
  error?: string;
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

  const response = await fetch(`${APPOINTMENT_SERVICE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || error.message || `HTTP ${response.status}`);
  }

  return response.json();
};

export const appointmentService = {
  /**
   * Get all appointments
   */
  getAll: async (filters?: {
    patient_id?: string;
    provider_id?: string;
    status?: string;
    appointment_date?: string;
    limit?: number;
    offset?: number;
  }): Promise<AppointmentResponse> => {
    const queryParams = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const queryString = queryParams.toString();
    return apiRequest<AppointmentResponse>(
      `/api/appointments${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get appointment by ID
   */
  getById: async (appointmentId: string): Promise<AppointmentResponse> => {
    return apiRequest<AppointmentResponse>(`/api/appointments/${appointmentId}`);
  },

  /**
   * Get patient appointments
   */
  getByPatient: async (
    patientId: string,
    options?: {
      status?: string;
      upcoming_only?: boolean;
      limit?: number;
      offset?: number;
    }
  ): Promise<AppointmentResponse> => {
    const queryParams = new URLSearchParams();
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const queryString = queryParams.toString();
    return apiRequest<AppointmentResponse>(
      `/api/patients/${patientId}/appointments${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Create appointment
   */
  create: async (data: {
    patient_id: string;
    provider_id?: string;
    appointment_date: string;
    appointment_time: string;
    duration?: number;
    appointment_type?: string;
    location?: string;
    status?: string;
    notes?: string;
    reminder?: boolean;
  }): Promise<AppointmentResponse> => {
    return apiRequest<AppointmentResponse>('/api/appointments', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update appointment
   */
  update: async (
    appointmentId: string,
    data: Partial<Omit<Appointment, 'appointment_id' | 'created_at'>>
  ): Promise<AppointmentResponse> => {
    return apiRequest<AppointmentResponse>(`/api/appointments/${appointmentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete appointment
   */
  delete: async (appointmentId: string): Promise<AppointmentResponse> => {
    return apiRequest<AppointmentResponse>(`/api/appointments/${appointmentId}`, {
      method: 'DELETE',
    });
  },

  /**
   * Check available time slots for a provider
   */
  checkAvailability: async (
    providerId: string,
    appointmentDate: string,
    duration?: number
  ): Promise<{
    success: boolean;
    provider_id: string;
    appointment_date: string;
    available_slots: string[];
    occupied_appointments: Array<{
      time: string;
      duration: number;
      status: string;
    }>;
  }> => {
    const queryParams = new URLSearchParams({
      provider_id: providerId,
      appointment_date: appointmentDate,
    });
    if (duration) {
      queryParams.append('duration', duration.toString());
    }
    return apiRequest(`/api/appointments/availability?${queryParams.toString()}`);
  },

  /**
   * Health check
   */
  health: async (): Promise<{ status: string; service: string; database: string }> => {
    return apiRequest('/health');
  },
};


