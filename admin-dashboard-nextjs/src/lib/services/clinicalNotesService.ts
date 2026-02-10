/**
 * Clinical Notes Service API Client
 * Connects to Clinical Notes Service backend (port 3008)
 */

const CLINICAL_NOTES_SERVICE_URL = process.env.NEXT_PUBLIC_CLINICAL_NOTES_SERVICE_URL || 'http://localhost:3008';

export interface ClinicalNote {
  note_id: string;
  patient_id: string;
  provider_id?: string;
  title: string;
  content: string;
  note_type: string;
  tags: string[] | string;
  is_important: boolean;
  created_at: string;
  updated_at?: string;
  created_by?: string;
}

export interface ClinicalNoteResponse {
  success: boolean;
  clinical_note?: ClinicalNote;
  clinical_notes?: ClinicalNote[];
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

  const response = await fetch(`${CLINICAL_NOTES_SERVICE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || error.message || `HTTP ${response.status}`);
  }

  return response.json();
};

export const clinicalNotesService = {
  /**
   * Get all clinical notes
   */
  getAll: async (filters?: {
    patient_id?: string;
    provider_id?: string;
    note_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<ClinicalNoteResponse> => {
    const queryParams = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const queryString = queryParams.toString();
    return apiRequest<ClinicalNoteResponse>(
      `/api/clinical-notes${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get clinical note by ID
   */
  getById: async (noteId: string): Promise<ClinicalNoteResponse> => {
    return apiRequest<ClinicalNoteResponse>(`/api/clinical-notes/${noteId}`);
  },

  /**
   * Get patient clinical notes
   */
  getByPatient: async (
    patientId: string,
    options?: {
      note_type?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<ClinicalNoteResponse> => {
    const queryParams = new URLSearchParams();
    if (options) {
      Object.entries(options).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const queryString = queryParams.toString();
    return apiRequest<ClinicalNoteResponse>(
      `/api/patients/${patientId}/clinical-notes${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Create clinical note
   */
  create: async (data: {
    patient_id: string;
    provider_id?: string;
    title: string;
    content: string;
    note_type?: string;
    tags?: string[];
    is_important?: boolean;
  }): Promise<ClinicalNoteResponse> => {
    return apiRequest<ClinicalNoteResponse>('/api/clinical-notes', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update clinical note
   */
  update: async (
    noteId: string,
    data: Partial<Omit<ClinicalNote, 'note_id' | 'created_at' | 'created_by'>>
  ): Promise<ClinicalNoteResponse> => {
    return apiRequest<ClinicalNoteResponse>(`/api/clinical-notes/${noteId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete clinical note
   */
  delete: async (noteId: string): Promise<ClinicalNoteResponse> => {
    return apiRequest<ClinicalNoteResponse>(`/api/clinical-notes/${noteId}`, {
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


