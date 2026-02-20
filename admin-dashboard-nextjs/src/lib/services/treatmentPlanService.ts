/**
 * Treatment Plan Service API Client
 * Connects to Treatment Plan Service backend (port 3007)
 */

const TREATMENT_PLAN_SERVICE_URL = process.env.NEXT_PUBLIC_TREATMENT_PLAN_SERVICE_URL || 'http://localhost:3007';

export interface TreatmentPlan {
  plan_id: string;
  patient_id: string;
  provider_id?: string;
  title: string;
  description?: string;
  start_date: string;
  end_date?: string;
  status: string;
  goals: string[] | string;
  medications: string[] | string;
  interventions: string[] | string;
  monitoring: string[] | string;
  notes?: string;
  created_at: string;
  updated_at?: string;
  created_by?: string;
}

export interface TreatmentPlanResponse {
  success: boolean;
  treatment_plan?: TreatmentPlan;
  treatment_plans?: TreatmentPlan[];
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

  const response = await fetch(`${TREATMENT_PLAN_SERVICE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || error.message || `HTTP ${response.status}`);
  }

  return response.json();
};

export const treatmentPlanService = {
  /**
   * Get all treatment plans
   */
  getAll: async (filters?: {
    patient_id?: string;
    provider_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<TreatmentPlanResponse> => {
    const queryParams = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const queryString = queryParams.toString();
    return apiRequest<TreatmentPlanResponse>(
      `/api/treatment-plans${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get treatment plan by ID
   */
  getById: async (planId: string): Promise<TreatmentPlanResponse> => {
    return apiRequest<TreatmentPlanResponse>(`/api/treatment-plans/${planId}`);
  },

  /**
   * Get patient treatment plans
   */
  getByPatient: async (
    patientId: string,
    options?: {
      status?: string;
      active_only?: boolean;
      limit?: number;
      offset?: number;
    }
  ): Promise<TreatmentPlanResponse> => {
    const queryParams = new URLSearchParams();
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const queryString = queryParams.toString();
    return apiRequest<TreatmentPlanResponse>(
      `/api/patients/${patientId}/treatment-plans${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Create treatment plan
   */
  create: async (data: {
    patient_id: string;
    provider_id?: string;
    title: string;
    description?: string;
    start_date: string;
    end_date?: string;
    status?: string;
    goals?: string[];
    medications?: string[];
    interventions?: string[];
    monitoring?: string[];
    notes?: string;
  }): Promise<TreatmentPlanResponse> => {
    return apiRequest<TreatmentPlanResponse>('/api/treatment-plans', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update treatment plan
   */
  update: async (
    planId: string,
    data: Partial<Omit<TreatmentPlan, 'plan_id' | 'created_at' | 'created_by'>>
  ): Promise<TreatmentPlanResponse> => {
    return apiRequest<TreatmentPlanResponse>(`/api/treatment-plans/${planId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete treatment plan
   */
  delete: async (planId: string): Promise<TreatmentPlanResponse> => {
    return apiRequest<TreatmentPlanResponse>(`/api/treatment-plans/${planId}`, {
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


