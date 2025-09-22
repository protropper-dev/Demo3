// Environment Configuration for Frontend1
// This file contains environment-specific settings

export const ENV_CONFIG = {
  // API Configuration
  API_URL: 'http://localhost:8000',
  API_TIMEOUT: 30000,
  API_RETRY_ATTEMPTS: 3,
  API_RETRY_DELAY: 1000,
  
  // Development
  DEV_MODE: true,
  DEBUG_MODE: false,
  
  // Backend Configuration
  BACKEND_URL: 'http://localhost:8000',
  BACKEND_API_VERSION: 'v1',
  
  // Feature Flags
  FEATURES: {
    ENABLE_STREAMING: true,
    ENABLE_FILE_UPLOAD: true,
    ENABLE_VECTOR_SEARCH: true,
    ENABLE_MODEL_STATUS: true,
    ENABLE_CONNECTION_STATUS: true
  }
};

// Helper function to get API URL
export const getApiUrl = (endpoint = '') => {
  return `${ENV_CONFIG.API_URL}${endpoint}`;
};

// Helper function to check if feature is enabled
export const isFeatureEnabled = (feature) => {
  return ENV_CONFIG.FEATURES[feature] || false;
};

export default ENV_CONFIG;
