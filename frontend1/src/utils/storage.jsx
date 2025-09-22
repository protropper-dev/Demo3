// Local storage utilities

// Storage keys
const STORAGE_KEYS = {
  CHAT_HISTORY: 'chatbot-history',
  CHAT_SESSIONS: 'chatbot-sessions',
  THEME: 'chatbot-theme',
  SETTINGS: 'chatbot-settings',
  USER_PREFERENCES: 'chatbot-preferences',
  DOCUMENTS: 'chatbot-documents',
  EMBEDDINGS: 'chatbot-embeddings',
  SEARCH_HISTORY: 'chatbot-search-history'
};

// Generic storage functions
const storage = {
  // Get item from localStorage
  get: (key, defaultValue = null) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error(`Error getting item from localStorage: ${key}`, error);
      return defaultValue;
    }
  },

  // Set item in localStorage
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error(`Error setting item in localStorage: ${key}`, error);
      return false;
    }
  },

  // Remove item from localStorage
  remove: (key) => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error(`Error removing item from localStorage: ${key}`, error);
      return false;
    }
  },

  // Clear all localStorage
  clear: () => {
    try {
      localStorage.clear();
      return true;
    } catch (error) {
      console.error('Error clearing localStorage', error);
      return false;
    }
  },

  // Check if key exists
  has: (key) => {
    return localStorage.getItem(key) !== null;
  },

  // Get all keys
  keys: () => {
    return Object.keys(localStorage);
  },

  // Get storage size
  size: () => {
    let total = 0;
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        total += localStorage[key].length + key.length;
      }
    }
    return total;
  }
};

// Session storage functions
const sessionStorage = {
  // Get item from sessionStorage
  get: (key, defaultValue = null) => {
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error(`Error getting item from sessionStorage: ${key}`, error);
      return defaultValue;
    }
  },

  // Set item in sessionStorage
  set: (key, value) => {
    try {
      window.sessionStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error(`Error setting item in sessionStorage: ${key}`, error);
      return false;
    }
  },

  // Remove item from sessionStorage
  remove: (key) => {
    try {
      window.sessionStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error(`Error removing item from sessionStorage: ${key}`, error);
      return false;
    }
  },

  // Clear all sessionStorage
  clear: () => {
    try {
      window.sessionStorage.clear();
      return true;
    } catch (error) {
      console.error('Error clearing sessionStorage', error);
      return false;
    }
  }
};

// Chat history storage
export const chatHistoryStorage = {
  // Get chat history
  get: () => {
    return storage.get(STORAGE_KEYS.CHAT_HISTORY, []);
  },

  // Set chat history
  set: (history) => {
    return storage.set(STORAGE_KEYS.CHAT_HISTORY, history);
  },

  // Add message to history
  addMessage: (message) => {
    const history = chatHistoryStorage.get();
    history.push({
      ...message,
      id: message.id || Date.now(),
      timestamp: message.timestamp || new Date().toISOString()
    });
    return chatHistoryStorage.set(history);
  },

  // Clear chat history
  clear: () => {
    return storage.remove(STORAGE_KEYS.CHAT_HISTORY);
  }
};

// Chat sessions storage
export const chatSessionsStorage = {
  // Get chat sessions
  get: () => {
    return storage.get(STORAGE_KEYS.CHAT_SESSIONS, []);
  },

  // Set chat sessions
  set: (sessions) => {
    return storage.set(STORAGE_KEYS.CHAT_SESSIONS, sessions);
  },

  // Add session
  addSession: (session) => {
    const sessions = chatSessionsStorage.get();
    sessions.unshift({
      ...session,
      id: session.id || Date.now(),
      createdAt: session.createdAt || new Date().toISOString()
    });
    return chatSessionsStorage.set(sessions);
  },

  // Update session
  updateSession: (sessionId, updates) => {
    const sessions = chatSessionsStorage.get();
    const index = sessions.findIndex(s => s.id === sessionId);
    if (index !== -1) {
      sessions[index] = { ...sessions[index], ...updates };
      return chatSessionsStorage.set(sessions);
    }
    return false;
  },

  // Remove session
  removeSession: (sessionId) => {
    const sessions = chatSessionsStorage.get();
    const filtered = sessions.filter(s => s.id !== sessionId);
    return chatSessionsStorage.set(filtered);
  },

  // Clear all sessions
  clear: () => {
    return storage.remove(STORAGE_KEYS.CHAT_SESSIONS);
  }
};

// Theme storage
export const themeStorage = {
  // Get theme
  get: () => {
    return storage.get(STORAGE_KEYS.THEME, 'light');
  },

  // Set theme
  set: (theme) => {
    return storage.set(STORAGE_KEYS.THEME, theme);
  },

  // Toggle theme
  toggle: () => {
    const currentTheme = themeStorage.get();
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    return themeStorage.set(newTheme);
  }
};

// Settings storage
export const settingsStorage = {
  // Get settings
  get: () => {
    return storage.get(STORAGE_KEYS.SETTINGS, {});
  },

  // Set settings
  set: (settings) => {
    return storage.set(STORAGE_KEYS.SETTINGS, settings);
  },

  // Update setting
  updateSetting: (key, value) => {
    const settings = settingsStorage.get();
    settings[key] = value;
    return settingsStorage.set(settings);
  },

  // Get setting
  getSetting: (key, defaultValue = null) => {
    const settings = settingsStorage.get();
    return settings[key] !== undefined ? settings[key] : defaultValue;
  },

  // Clear settings
  clear: () => {
    return storage.remove(STORAGE_KEYS.SETTINGS);
  }
};

// User preferences storage
export const preferencesStorage = {
  // Get preferences
  get: () => {
    return storage.get(STORAGE_KEYS.USER_PREFERENCES, {});
  },

  // Set preferences
  set: (preferences) => {
    return storage.set(STORAGE_KEYS.USER_PREFERENCES, preferences);
  },

  // Update preference
  updatePreference: (key, value) => {
    const preferences = preferencesStorage.get();
    preferences[key] = value;
    return preferencesStorage.set(preferences);
  },

  // Get preference
  getPreference: (key, defaultValue = null) => {
    const preferences = preferencesStorage.get();
    return preferences[key] !== undefined ? preferences[key] : defaultValue;
  },

  // Clear preferences
  clear: () => {
    return storage.remove(STORAGE_KEYS.USER_PREFERENCES);
  }
};

// Documents storage
export const documentsStorage = {
  // Get documents
  get: () => {
    return storage.get(STORAGE_KEYS.DOCUMENTS, []);
  },

  // Set documents
  set: (documents) => {
    return storage.set(STORAGE_KEYS.DOCUMENTS, documents);
  },

  // Add document
  addDocument: (document) => {
    const documents = documentsStorage.get();
    documents.push({
      ...document,
      id: document.id || Date.now(),
      uploadDate: document.uploadDate || new Date().toISOString()
    });
    return documentsStorage.set(documents);
  },

  // Update document
  updateDocument: (documentId, updates) => {
    const documents = documentsStorage.get();
    const index = documents.findIndex(d => d.id === documentId);
    if (index !== -1) {
      documents[index] = { ...documents[index], ...updates };
      return documentsStorage.set(documents);
    }
    return false;
  },

  // Remove document
  removeDocument: (documentId) => {
    const documents = documentsStorage.get();
    const filtered = documents.filter(d => d.id !== documentId);
    return documentsStorage.set(filtered);
  },

  // Clear documents
  clear: () => {
    return storage.remove(STORAGE_KEYS.DOCUMENTS);
  }
};

// Embeddings storage
export const embeddingsStorage = {
  // Get embeddings
  get: () => {
    return storage.get(STORAGE_KEYS.EMBEDDINGS, []);
  },

  // Set embeddings
  set: (embeddings) => {
    return storage.set(STORAGE_KEYS.EMBEDDINGS, embeddings);
  },

  // Add embedding
  addEmbedding: (embedding) => {
    const embeddings = embeddingsStorage.get();
    embeddings.push({
      ...embedding,
      id: embedding.id || Date.now(),
      timestamp: embedding.timestamp || new Date().toISOString()
    });
    return embeddingsStorage.set(embeddings);
  },

  // Update embedding
  updateEmbedding: (embeddingId, updates) => {
    const embeddings = embeddingsStorage.get();
    const index = embeddings.findIndex(e => e.id === embeddingId);
    if (index !== -1) {
      embeddings[index] = { ...embeddings[index], ...updates };
      return embeddingsStorage.set(embeddings);
    }
    return false;
  },

  // Remove embedding
  removeEmbedding: (embeddingId) => {
    const embeddings = embeddingsStorage.get();
    const filtered = embeddings.filter(e => e.id !== embeddingId);
    return embeddingsStorage.set(filtered);
  },

  // Clear embeddings
  clear: () => {
    return storage.remove(STORAGE_KEYS.EMBEDDINGS);
  }
};

// Search history storage
export const searchHistoryStorage = {
  // Get search history
  get: () => {
    return storage.get(STORAGE_KEYS.SEARCH_HISTORY, []);
  },

  // Set search history
  set: (history) => {
    return storage.set(STORAGE_KEYS.SEARCH_HISTORY, history);
  },

  // Add search query
  addQuery: (query) => {
    const history = searchHistoryStorage.get();
    const newEntry = {
      id: Date.now(),
      query,
      timestamp: new Date().toISOString()
    };
    history.unshift(newEntry);
    // Keep only last 100 searches
    const limited = history.slice(0, 100);
    return searchHistoryStorage.set(limited);
  },

  // Clear search history
  clear: () => {
    return storage.remove(STORAGE_KEYS.SEARCH_HISTORY);
  }
};

// Export all storage functions
export {
  storage,
  sessionStorage,
  STORAGE_KEYS
};
