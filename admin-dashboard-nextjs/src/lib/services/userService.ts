/**
 * User Service API Client
 * Connects to Integration Bridge for admin user management (port 8081)
 */

import { getBridgeToken } from '../utils/authToken'

const INTEGRATION_BRIDGE_URL = process.env.NEXT_PUBLIC_INTEGRATION_BRIDGE_URL || 'http://localhost:8081';

export interface AdminUser {
  user_id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role: string; // admin, super_admin, billing_admin, coding_admin, etc.
  status: string; // active, inactive, suspended
  telephone?: string;
  pager?: string;
  office_number?: string;
  created_at: string;
  updated_at?: string;
  last_login?: string;
}

export interface UserResponse {
  success: boolean;
  user?: AdminUser;
  users?: AdminUser[];
  count?: number;
  error?: string;
  message?: string;
}

const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  // Get token from NextAuth session
  const token = await getBridgeToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  } else {
    console.warn('No bridge token found. User may need to log in again.');
  }

  const response = await fetch(`${INTEGRATION_BRIDGE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || error.message || `HTTP ${response.status}`);
  }

  return response.json();
};

export const userService = {
  /**
   * Get all admin users
   */
  getAll: async (filters?: {
    search?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<UserResponse> => {
    const queryParams = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const queryString = queryParams.toString();
    return apiRequest<UserResponse>(
      `/api/admin/users${queryString ? `?${queryString}` : ''}`
    );
  },

  /**
   * Get user by ID
   */
  getById: async (userId: string): Promise<UserResponse> => {
    return apiRequest<UserResponse>(`/api/admin/users/${userId}`);
  },

  /**
   * Create admin user
   */
  create: async (data: {
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    role?: string;
    status?: string;
    telephone?: string;
    pager?: string;
    office_number?: string;
  }): Promise<UserResponse> => {
    return apiRequest<UserResponse>('/api/admin/users', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update admin user
   */
  update: async (
    userId: string,
    data: Partial<Omit<AdminUser, 'user_id' | 'created_at' | 'password_hash'>> & {
      password?: string;
    }
  ): Promise<UserResponse> => {
    return apiRequest<UserResponse>(`/api/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete admin user (soft delete - sets status to inactive)
   */
  delete: async (userId: string): Promise<UserResponse> => {
    return apiRequest<UserResponse>(`/api/admin/users/${userId}`, {
      method: 'DELETE',
    });
  },

  /**
   * Reset user password
   */
  resetPassword: async (userId: string, newPassword: string): Promise<UserResponse> => {
    return apiRequest<UserResponse>(`/api/admin/users/${userId}/reset-password`, {
      method: 'POST',
      body: JSON.stringify({ new_password: newPassword }),
    });
  },

  /**
   * Health check
   */
  health: async (): Promise<{ status: string; service: string }> => {
    return apiRequest('/health');
  },
};

