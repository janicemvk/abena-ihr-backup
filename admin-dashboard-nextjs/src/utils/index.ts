import { format, parseISO } from 'date-fns'
import { config } from '@/config'

// Date formatting
export const formatDate = (date: string | Date): string => {
  const parsedDate = typeof date === 'string' ? parseISO(date) : date
  return format(parsedDate, config.ui.dateFormat)
}

export const formatTime = (time: string | Date): string => {
  const parsedTime = typeof time === 'string' ? parseISO(time) : time
  return format(parsedTime, config.ui.timeFormat)
}

// Currency formatting
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: config.features.billing.currency,
  }).format(amount)
}

// Status badge styling
export const getStatusColor = (status: string): { bg: string; text: string } => {
  switch (status.toLowerCase()) {
    case 'active':
    case 'confirmed':
    case 'approved':
    case 'paid':
      return { bg: 'bg-green-100', text: 'text-green-800' }
    case 'pending':
      return { bg: 'bg-yellow-100', text: 'text-yellow-800' }
    case 'inactive':
    case 'cancelled':
      return { bg: 'bg-gray-100', text: 'text-gray-800' }
    default:
      return { bg: 'bg-gray-100', text: 'text-gray-800' }
  }
}

// Error handling
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public data?: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

// Validation
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export const isValidPhone = (phone: string): boolean => {
  const phoneRegex = /^\+?[\d\s-()]{10,}$/
  return phoneRegex.test(phone)
}

// Data transformation
export const groupBy = <T>(array: T[], key: keyof T): { [key: string]: T[] } => {
  return array.reduce((result, item) => {
    const groupKey = String(item[key])
    return {
      ...result,
      [groupKey]: [...(result[groupKey] || []), item],
    }
  }, {} as { [key: string]: T[] })
}

// Local storage
export const storage = {
  get: (key: string): any => {
    if (typeof window === 'undefined') return null
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : null
    } catch (error) {
      console.error('Error reading from localStorage', error)
      return null
    }
  },
  set: (key: string, value: any): void => {
    if (typeof window === 'undefined') return
    try {
      window.localStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error('Error writing to localStorage', error)
    }
  },
  remove: (key: string): void => {
    if (typeof window === 'undefined') return
    try {
      window.localStorage.removeItem(key)
    } catch (error) {
      console.error('Error removing from localStorage', error)
    }
  },
} 