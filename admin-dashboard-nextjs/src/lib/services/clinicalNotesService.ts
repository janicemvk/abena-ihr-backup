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

// Mock data for demo purposes
const MOCK_NOTES: ClinicalNote[] = [
  {
    note_id: '1',
    patient_id: 'P001',
    provider_id: 'DR001',
    note_type: 'Progress Note',
    title: 'Follow-up Visit - Chronic Pain Management',
    content: 'Patient reports 40% improvement in chronic pain symptoms since starting eCBome-guided therapy. Continuing current treatment protocol with minor adjustments.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    note_id: '2',
    patient_id: 'P002',
    provider_id: 'DR002',
    note_type: 'Consultation',
    title: 'Initial Consultation - Anxiety Disorder',
    content: 'New patient consultation for anxiety management. Discussed integrative approach combining quantum analysis with traditional methods.',
    created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    note_id: '3',
    patient_id: 'P003',
    provider_id: 'DR001',
    note_type: 'Treatment Plan',
    title: 'Personalized Treatment Plan - Inflammation',
    content: 'Based on quantum analysis results and eCBome biomarkers, developed personalized anti-inflammatory protocol.',
    created_at: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
  },
];

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
    try {
      const queryParams = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            queryParams.append(key, value.toString());
          }
        });
      }
      const queryString = queryParams.toString();
      return await apiRequest<ClinicalNoteResponse>(
        `/api/clinical-notes${queryString ? `?${queryString}` : ''}`
      );
    } catch (error) {
      console.warn('Using mock clinical notes data:', error);
      // Return mock data if API fails
      let filteredNotes = MOCK_NOTES;
      if (filters?.patient_id) {
        filteredNotes = filteredNotes.filter(n => n.patient_id === filters.patient_id);
      }
      if (filters?.provider_id) {
        filteredNotes = filteredNotes.filter(n => n.provider_id === filters.provider_id);
      }
      if (filters?.note_type) {
        filteredNotes = filteredNotes.filter(n => n.note_type === filters.note_type);
      }
      return {
        success: true,
        notes: filteredNotes,
        count: filteredNotes.length,
      };
    }
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


