export const config = {
  app: {
    name: 'Abena IHR',
    description: 'Integrated Healthcare Records System',
    version: '1.0.0',
  },
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api',
  },
  auth: {
    // Add authentication configuration here
    tokenKey: 'abena_ihr_token',
    refreshTokenKey: 'abena_ihr_refresh_token',
  },
  features: {
    appointments: {
      maxDaysInAdvance: 90,
      defaultDuration: 30, // minutes
    },
    billing: {
      currency: 'USD',
      dateFormat: 'YYYY-MM-DD',
    },
    analytics: {
      defaultDateRange: 30, // days
    },
  },
  ui: {
    theme: {
      colors: {
        primary: 'indigo',
        secondary: 'gray',
        accent: 'blue',
      },
      sidebar: {
        width: '16rem',
      },
    },
    dateFormat: 'MMMM D, YYYY',
    timeFormat: 'h:mm A',
  },
} 