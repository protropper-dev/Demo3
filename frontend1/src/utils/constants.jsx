// Application constants
import { ENV_CONFIG } from '../config/environment.jsx';

// API Configuration
export const API_CONFIG = {
  BASE_URL: ENV_CONFIG.API_URL,
  TIMEOUT: ENV_CONFIG.API_TIMEOUT,
  RETRY_ATTEMPTS: ENV_CONFIG.API_RETRY_ATTEMPTS,
  RETRY_DELAY: ENV_CONFIG.API_RETRY_DELAY
};

// Model Configuration
export const MODEL_CONFIG = {
  VINALLAMA: {
    DEFAULT_PATH: '/models/vinallama',
    MAX_TOKENS: 2048,
    TEMPERATURE: 0.7,
    TOP_P: 0.9,
    TOP_K: 40,
    REPETITION_PENALTY: 1.1
  },
  E5_EMBEDDING: {
    DEFAULT_PATH: '/models/e5-large-v2',
    BATCH_SIZE: 32,
    MAX_LENGTH: 512,
    NORMALIZE: true,
    DEVICE: 'cpu'
  }
};

// RAG Configuration
export const RAG_CONFIG = {
  MAX_RESULTS: 5,
  SIMILARITY_THRESHOLD: 0.7,
  CHUNK_SIZE: 1000,
  OVERLAP_SIZE: 200,
  RERANK_RESULTS: true
};

// File Upload Configuration
export const FILE_CONFIG = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: [
    'text/plain',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
    'text/markdown'
  ],
  ALLOWED_EXTENSIONS: ['.txt', '.pdf', '.docx', '.doc', '.md']
};

// UI Configuration
export const UI_CONFIG = {
  THEMES: {
    LIGHT: 'light',
    DARK: 'dark'
  },
  LANGUAGES: {
    VIETNAMESE: 'vi',
    ENGLISH: 'en'
  },
  FONT_SIZES: {
    SMALL: 'small',
    MEDIUM: 'medium',
    LARGE: 'large'
  }
};

// Chat Configuration
export const CHAT_CONFIG = {
  MAX_MESSAGE_LENGTH: 2000,
  MAX_MESSAGES_PER_SESSION: 1000,
  AUTO_SAVE_INTERVAL: 5000, // 5 seconds
  TYPING_INDICATOR_DELAY: 1000 // 1 second
};

// Vector Search Configuration
export const VECTOR_CONFIG = {
  DEFAULT_TOP_K: 5,
  DEFAULT_THRESHOLD: 0.7,
  MAX_EMBEDDING_DIMENSION: 1024,
  CACHE_SIZE: 1000
};

// Document Processing Configuration
export const DOCUMENT_CONFIG = {
  CHUNK_SIZE: 1000,
  OVERLAP_SIZE: 200,
  MAX_CHUNKS_PER_DOCUMENT: 1000,
  PROCESSING_TIMEOUT: 300000 // 5 minutes
};

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Lỗi kết nối mạng. Vui lòng kiểm tra kết nối internet.',
  SERVER_ERROR: 'Lỗi máy chủ. Vui lòng thử lại sau.',
  MODEL_NOT_LOADED: 'Model chưa được tải. Vui lòng đợi hoặc thử lại.',
  FILE_TOO_LARGE: 'File quá lớn. Vui lòng chọn file nhỏ hơn 10MB.',
  UNSUPPORTED_FILE_TYPE: 'Loại file không được hỗ trợ.',
  INVALID_INPUT: 'Dữ liệu đầu vào không hợp lệ.',
  PROCESSING_ERROR: 'Lỗi xử lý. Vui lòng thử lại.',
  UNAUTHORIZED: 'Không có quyền truy cập.',
  NOT_FOUND: 'Không tìm thấy dữ liệu.',
  TIMEOUT: 'Hết thời gian chờ. Vui lòng thử lại.'
};

// Success Messages
export const SUCCESS_MESSAGES = {
  FILE_UPLOADED: 'File đã được tải lên thành công.',
  DOCUMENT_PROCESSED: 'Tài liệu đã được xử lý thành công.',
  MODEL_LOADED: 'Model đã được tải thành công.',
  SETTINGS_SAVED: 'Cài đặt đã được lưu thành công.',
  MESSAGE_SENT: 'Tin nhắn đã được gửi thành công.',
  SEARCH_COMPLETED: 'Tìm kiếm hoàn thành.',
  EXPORT_SUCCESS: 'Xuất dữ liệu thành công.',
  IMPORT_SUCCESS: 'Nhập dữ liệu thành công.'
};

// Status Types
export const STATUS_TYPES = {
  IDLE: 'idle',
  LOADING: 'loading',
  PROCESSING: 'processing',
  READY: 'ready',
  ERROR: 'error',
  SUCCESS: 'success'
};

// Message Types
export const MESSAGE_TYPES = {
  USER: 'user',
  BOT: 'bot',
  SYSTEM: 'system',
  ERROR: 'error'
};

// Document Status
export const DOCUMENT_STATUS = {
  UPLOADED: 'uploaded',
  PROCESSING: 'processing',
  PROCESSED: 'processed',
  ERROR: 'error',
  DELETED: 'deleted'
};

// Model Status
export const MODEL_STATUS = {
  UNLOADED: 'unloaded',
  LOADING: 'loading',
  READY: 'ready',
  ERROR: 'error',
  UNLOADING: 'unloading'
};

// Storage Keys
export const STORAGE_KEYS = {
  CHAT_HISTORY: 'chatbot-history',
  CHAT_SESSIONS: 'chatbot-sessions',
  THEME: 'chatbot-theme',
  SETTINGS: 'chatbot-settings',
  USER_PREFERENCES: 'chatbot-preferences'
};

// API Endpoints - Updated for Backend1
export const API_ENDPOINTS = {
  // Backend1 API v1 endpoints
  API_V1: '/api/v1',
  
  // Health endpoints
  HEALTH_BASIC: '/api/v1/health/',
  HEALTH_DETAILED: '/api/v1/health/detailed',
  HEALTH_READY: '/api/v1/health/ready',
  HEALTH_LIVE: '/api/v1/health/live',
  
  // Chatbot endpoints (Basic RAG)
  CHATBOT_CHAT: '/api/v1/chatbot/chat',
  CHATBOT_QUERY: '/api/v1/chatbot/query',
  CHATBOT_STATS: '/api/v1/chatbot/stats',
  CHATBOT_BUILD_KB: '/api/v1/chatbot/build-knowledge-base',
  CHATBOT_RESET_KB: '/api/v1/chatbot/reset-knowledge-base',
  CHATBOT_CATEGORIES: '/api/v1/chatbot/categories',
  CHATBOT_HEALTH: '/api/v1/chatbot/health',
  
  // Enhanced Chatbot endpoints
  CHATBOT_ENHANCED_CHAT: '/api/v1/chatbot/enhanced',
  CHATBOT_ENHANCED_STREAM: '/api/v1/chatbot/enhanced/stream',
  CHATBOT_ENHANCED_STATUS: '/api/v1/chatbot/status/enhanced',
  CHATBOT_ENHANCED_DEVICE: '/api/v1/chatbot/device/enhanced',
  CHATBOT_ENHANCED_INIT: '/api/v1/chatbot/initialize/enhanced',
  CHATBOT_ENHANCED_STATS: '/api/v1/chatbot/stats/enhanced',
  CHATBOT_ENHANCED_HEALTH: '/api/v1/chatbot/health/enhanced',
  
  // Items endpoints (Demo)
  ITEMS_LIST: '/api/v1/items/',
  ITEMS_GET: '/api/v1/items/{item_id}',
  ITEMS_CREATE: '/api/v1/items/',
  ITEMS_UPDATE: '/api/v1/items/{item_id}',
  ITEMS_DELETE: '/api/v1/items/{item_id}',
  
  // Root endpoints
  ROOT: '/',
  ROOT_HEALTH: '/health'
};

// Animation Durations
export const ANIMATION_DURATIONS = {
  FAST: 200,
  NORMAL: 300,
  SLOW: 500,
  VERY_SLOW: 1000
};

// Breakpoints
export const BREAKPOINTS = {
  MOBILE: 480,
  TABLET: 768,
  DESKTOP: 1024,
  LARGE_DESKTOP: 1200
};

// Colors
export const COLORS = {
  PRIMARY: '#4CAF50',
  SECONDARY: '#2196F3',
  ACCENT: '#FF9800',
  SUCCESS: '#4CAF50',
  WARNING: '#FF9800',
  ERROR: '#F44336',
  INFO: '#2196F3',
  LIGHT: '#F5F5F5',
  DARK: '#333333',
  WHITE: '#FFFFFF',
  BLACK: '#000000',
  GRAY: '#9E9E9E',
  LIGHT_GRAY: '#E0E0E0',
  DARK_GRAY: '#616161'
};

// Z-Index Values
export const Z_INDEX = {
  DROPDOWN: 1000,
  STICKY: 1020,
  FIXED: 1030,
  MODAL_BACKDROP: 1040,
  MODAL: 1050,
  POPOVER: 1060,
  TOOLTIP: 1070,
  TOAST: 1080
};
