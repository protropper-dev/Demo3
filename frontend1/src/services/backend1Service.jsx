// Backend1 API Service
// Service để gọi API backend1 từ frontend1

import { API_CONFIG, API_ENDPOINTS } from '../utils/constants.jsx';

class Backend1Service {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
  }

  // Utility method để tạo URL đầy đủ
  getFullURL(endpoint) {
    return `${this.baseURL}${endpoint}`;
  }

  // Utility method để tạo fetch request với error handling và retry logic
  async makeRequest(url, options = {}, retries = 3) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      console.log(`Making request to: ${url} (attempt ${4-retries})`);
      
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
          ...options.headers,
        },
        cache: 'no-store'
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log(`Response from ${url}:`, data);
      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      
      console.error(`Error making request to ${url} (attempt ${4-retries}):`, error);
      
      // Retry logic cho network errors
      if (retries > 0 && (
        error.name === 'AbortError' ||
        error.name === 'TypeError' && error.message.includes('fetch') ||
        error.message.includes('ERR_EMPTY_RESPONSE')
      )) {
        console.log(`Retrying request to ${url} in 1 second... (${retries} attempts left)`);
        await new Promise(resolve => setTimeout(resolve, 1000));
        return this.makeRequest(url, options, retries - 1);
      }
      
      if (error.name === 'AbortError') {
        throw new Error('Request timeout. Vui lòng thử lại.');
      }
      
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Network error - cannot connect to server');
      }
      
      if (error.message.includes('ERR_EMPTY_RESPONSE')) {
        throw new Error('Server connection lost - please check if backend is running');
      }
      
      throw error;
    }
  }

  // Health Check Methods
  async healthCheck() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.HEALTH_BASIC));
  }

  async detailedHealthCheck() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.HEALTH_DETAILED));
  }

  async readinessCheck() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.HEALTH_READY));
  }

  async livenessCheck() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.HEALTH_LIVE));
  }

  // Chatbot Methods (Basic RAG)
  async chat(message, chatHistory = null, filterCategory = null) {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_CHAT), {
      method: 'POST',
      body: JSON.stringify({
        message,
        chat_history: chatHistory,
        filter_category: filterCategory
      })
    });
  }

  async query(question, topK = null, filterCategory = null) {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_QUERY), {
      method: 'POST',
      body: JSON.stringify({
        question,
        top_k: topK,
        filter_category: filterCategory
      })
    });
  }

  async getChatbotStats() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_STATS));
  }

  async buildKnowledgeBase(forceRebuild = false) {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_BUILD_KB), {
      method: 'POST',
      body: JSON.stringify({
        force_rebuild: forceRebuild
      })
    });
  }

  async resetKnowledgeBase() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_RESET_KB), {
      method: 'POST'
    });
  }

  async getCategories() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_CATEGORIES));
  }

  async getChatbotHealth() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_HEALTH));
  }

  // Enhanced Chatbot Methods
  async enhancedChat(query, maxTokens = 512, temperature = 0.7, topK = 50, topP = 0.95) {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_ENHANCED_CHAT), {
      method: 'POST',
      body: JSON.stringify({
        query,
        max_tokens: maxTokens,
        temperature,
        top_k: topK,
        top_p: topP
      })
    });
  }

  // Enhanced Chat with Streaming
  async enhancedChatStream(query, maxTokens = 512, temperature = 0.7, topK = 50, topP = 0.95) {
    const response = await fetch(this.getFullURL(API_ENDPOINTS.CHATBOT_ENHANCED_STREAM), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        max_tokens: maxTokens,
        temperature,
        top_k: topK,
        top_p: topP
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.body.getReader();
  }

  async getEnhancedStatus() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_ENHANCED_STATUS));
  }

  async getDeviceInfo() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_ENHANCED_DEVICE));
  }

  async initializeEnhanced() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_ENHANCED_INIT), {
      method: 'POST'
    });
  }

  async getEnhancedStats() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_ENHANCED_STATS));
  }

  async getEnhancedHealth() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.CHATBOT_ENHANCED_HEALTH));
  }

  // Items Methods (Demo)
  async getItems(skip = 0, limit = 100) {
    return this.makeRequest(this.getFullURL(`${API_ENDPOINTS.ITEMS_LIST}?skip=${skip}&limit=${limit}`));
  }

  async getItem(itemId) {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.ITEMS_GET.replace('{item_id}', itemId)));
  }

  async createItem(itemData) {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.ITEMS_CREATE), {
      method: 'POST',
      body: JSON.stringify(itemData)
    });
  }

  async updateItem(itemId, itemData) {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.ITEMS_UPDATE.replace('{item_id}', itemId)), {
      method: 'PUT',
      body: JSON.stringify(itemData)
    });
  }

  async deleteItem(itemId) {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.ITEMS_DELETE.replace('{item_id}', itemId)), {
      method: 'DELETE'
    });
  }

  // Root Methods
  async getRoot() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.ROOT));
  }

  async getRootHealth() {
    return this.makeRequest(this.getFullURL(API_ENDPOINTS.ROOT_HEALTH));
  }

  // Utility Methods
  async checkConnection() {
    try {
      await this.healthCheck();
      return { connected: true, message: 'Kết nối thành công' };
    } catch (error) {
      return { connected: false, message: `Lỗi kết nối: ${error.message}` };
    }
  }

  async getSystemInfo() {
    try {
      const [health, enhancedStatus] = await Promise.all([
        this.detailedHealthCheck(),
        this.getEnhancedStatus()
      ]);
      
      return {
        health,
        enhancedStatus,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Lỗi lấy thông tin hệ thống: ${error.message}`);
    }
  }
}

// Export singleton instance
export default new Backend1Service();
