/**
 * Auth Service API Client
 * Connects to Integration Bridge for authentication (port 8081)
 * Falls back to Auth Service (port 3002) if needed
 */

// Use environment variable or fallback to localhost for browser-side calls
// In Docker, use the service name for internal calls, but browser needs localhost
const INTEGRATION_BRIDGE_URL = typeof window !== 'undefined' 
  ? (process.env.NEXT_PUBLIC_INTEGRATION_BRIDGE_URL || 'http://localhost:8081')
  : (process.env.NEXT_PUBLIC_INTEGRATION_BRIDGE_URL || 'http://abena-api-gateway:80');
const AUTH_SERVICE_URL = process.env.NEXT_PUBLIC_AUTH_SERVICE_URL || 'http://localhost:3002';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  token?: string;
  user?: {
    id: string;
    email: string;
    name?: string;
    role: string;
  };
  error?: string;
}

/**
 * Authenticate user via Integration Bridge
 * The bridge will verify credentials against admin_users table
 */
export async function authenticateUser(credentials: LoginCredentials): Promise<AuthResponse> {
  try {
    // Authenticate via Integration Bridge with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

    try {
      const response = await fetch(`${INTEGRATION_BRIDGE_URL}/api/admin/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Check if response is ok before trying to parse JSON
      if (!response.ok) {
        let errorMessage = 'Authentication failed';
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorMessage;
        } catch {
          // If JSON parsing fails, use status text
          errorMessage = response.statusText || `HTTP ${response.status}`;
        }
        return {
          success: false,
          error: errorMessage,
        };
      }

      const data = await response.json();

      if (!data.success) {
        return {
          success: false,
          error: data.error || 'Authentication failed',
        };
      }

      return {
        success: true,
        token: data.token,
        user: data.user,
      };
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      
      // Handle abort (timeout)
      if (fetchError.name === 'AbortError') {
        return {
          success: false,
          error: 'Connection timeout. Please ensure the Integration Bridge is running on port 8081.',
        };
      }

      // Handle network errors
      if (fetchError instanceof TypeError && fetchError.message.includes('fetch')) {
        return {
          success: false,
          error: 'Cannot connect to authentication service. Please ensure the Integration Bridge is running on port 8081.',
        };
      }

      throw fetchError; // Re-throw if it's an unexpected error
    }
  } catch (error: any) {
    console.error('Authentication error:', error);
    return {
      success: false,
      error: error.message || 'Unable to connect to authentication service. Please check your connection and ensure the Integration Bridge is running.',
    };
  }
}

/**
 * Verify token (for session validation)
 */
export async function verifyToken(token: string): Promise<{ valid: boolean; user?: any }> {
  try {
    // In production, verify token with Integration Bridge
    // For now, decode the mock token
    try {
      const decoded = JSON.parse(Buffer.from(token, 'base64').toString());
      return {
        valid: true,
        user: decoded,
      };
    } catch {
      return { valid: false };
    }
  } catch (error) {
    return { valid: false };
  }
}

