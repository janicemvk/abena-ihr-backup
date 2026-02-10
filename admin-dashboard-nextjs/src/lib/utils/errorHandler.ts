/**
 * Error Handling Utility
 * Provides user-friendly error messages and error handling helpers
 */

export interface ApiError {
  message: string
  status?: number
  details?: string
}

/**
 * Extract user-friendly error message from various error types
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    // Check for common error patterns
    const message = error.message.toLowerCase()
    
    // Network errors
    if (message.includes('fetch') || message.includes('network')) {
      return 'Unable to connect to the server. Please check your internet connection and try again.'
    }
    
    // Authentication errors
    if (message.includes('401') || message.includes('unauthorized') || message.includes('authentication')) {
      return 'Your session has expired. Please log in again.'
    }
    
    // Permission errors
    if (message.includes('403') || message.includes('forbidden') || message.includes('permission')) {
      return 'You do not have permission to perform this action.'
    }
    
    // Not found errors
    if (message.includes('404') || message.includes('not found')) {
      return 'The requested resource was not found.'
    }
    
    // Server errors
    if (message.includes('500') || message.includes('internal server error')) {
      return 'A server error occurred. Please try again later or contact support.'
    }
    
    // Service unavailable
    if (message.includes('503') || message.includes('service unavailable')) {
      return 'The service is temporarily unavailable. Please try again in a few moments.'
    }
    
    // Timeout errors
    if (message.includes('timeout')) {
      return 'The request took too long. Please try again.'
    }
    
    // Return the original message if it's user-friendly
    if (error.message.length < 100 && !error.message.includes('http')) {
      return error.message
    }
    
    // Default for unknown errors
    return 'An unexpected error occurred. Please try again.'
  }
  
  if (typeof error === 'string') {
    return error
  }
  
  return 'An unexpected error occurred. Please try again.'
}

/**
 * Handle API errors with user-friendly messages
 */
export function handleApiError(error: unknown, defaultMessage = 'An error occurred'): string {
  const message = getErrorMessage(error)
  console.error('API Error:', error)
  return message || defaultMessage
}

/**
 * Show error notification (can be extended to use a toast library)
 */
export function showError(message: string): void {
  // For now, use alert. In production, replace with a toast notification library
  alert(message)
}

/**
 * Show success notification
 */
export function showSuccess(message: string): void {
  // For now, use alert. In production, replace with a toast notification library
  alert(message)
}

/**
 * Wrap async operations with error handling
 */
export async function withErrorHandling<T>(
  operation: () => Promise<T>,
  errorMessage = 'An error occurred'
): Promise<T | null> {
  try {
    return await operation()
  } catch (error) {
    const message = handleApiError(error, errorMessage)
    showError(message)
    return null
  }
}

