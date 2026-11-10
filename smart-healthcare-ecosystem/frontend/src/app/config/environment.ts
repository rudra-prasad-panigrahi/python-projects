export const environment = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  enableDevelopmentDemo: import.meta.env.VITE_ENABLE_DEMO_AUTH === 'true' || import.meta.env.DEV,
  isDevelopment: import.meta.env.DEV,
} as const;
