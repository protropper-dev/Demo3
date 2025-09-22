// Chat History Service - Kết nối với RAG Unified Chat History API
import { ENV_CONFIG } from '../config/environment';

class ChatHistoryService {
  constructor() {
    this.baseURL = ENV_CONFIG.API_URL || 'http://localhost:8000';
    this.apiPath = '/api/v1/rag';
  }

  // ===== Chat Management =====

  /**
   * Gửi tin nhắn và lưu lịch sử
   * @param {Object} params - Tham số chat
   * @param {string} params.message - Tin nhắn người dùng
   * @param {number} params.chatId - ID chat hiện tại (optional)
   * @param {number} params.userId - ID người dùng (optional)
   * @param {string} params.sessionId - ID phiên (optional)
   * @param {number} params.topK - Số lượng sources (default: 5)
   * @param {string} params.filterCategory - Lọc category (default: null)
   * @param {Object} params.ragSettings - Cấu hình RAG (optional)
   * @returns {Promise<Object>} Response với message_id, chat_id, sources, etc.
   */
  async sendMessage({
    message,
    chatId = null,
    userId = null,
    sessionId = null,
    topK = 5,
    filterCategory = null,
    ragSettings = null
  }) {
    try {
      const payload = {
        message,
        top_k: topK,
        filter_category: filterCategory
      };

      // Thêm optional params
      if (chatId) payload.chat_id = chatId;
      if (userId) payload.user_id = userId;
      if (sessionId) payload.session_id = sessionId;
      if (ragSettings) payload.rag_settings = ragSettings;

      const response = await fetch(`${this.baseURL}${this.apiPath}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        messageId: data.message_id,
        chatId: data.chat_id,
        userMessage: data.user_message,
        aiResponse: data.ai_response,
        sources: data.sources || [],
        totalSources: data.total_sources || 0,
        confidence: data.confidence || 0,
        processingTime: data.processing_time_ms || 0,
        timestamp: data.timestamp
      };

    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  /**
   * Lấy lịch sử chat với thống kê
   * @param {Object} params - Tham số query
   * @param {number} params.page - Số trang (default: 1)
   * @param {number} params.perPage - Số item per trang (default: 10)
   * @param {number} params.userId - ID người dùng (optional)
   * @param {string} params.categoryFilter - Lọc theo category (optional)
   * @returns {Promise<Object>} Danh sách chats với stats
   */
  async getChatHistory({
    page = 1,
    perPage = 10,
    userId = null,
    categoryFilter = null
  } = {}) {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString()
      });

      if (userId) params.append('user_id', userId.toString());
      if (categoryFilter) params.append('category_filter', categoryFilter);

      const response = await fetch(`${this.baseURL}${this.apiPath}/chats?${params}`, {
        method: 'GET',
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        chats: data.chats || [],
        total: data.total || 0,
        page: data.page || 1,
        perPage: data.per_page || 10,
        filters: data.filters || {}
      };

    } catch (error) {
      console.error('Error getting chat history:', error);
      throw error;
    }
  }

  /**
   * Lấy tin nhắn trong chat
   * @param {number} chatId - ID chat
   * @param {Object} params - Tham số query
   * @param {number} params.page - Số trang (default: 1)
   * @param {number} params.perPage - Số item per trang (default: 50)
   * @returns {Promise<Object>} Danh sách messages với sources info
   */
  async getChatMessages(chatId, { page = 1, perPage = 50 } = {}) {
    try {
      // Validate chatId
      if (!chatId || typeof chatId !== 'number') {
        throw new Error(`Invalid chatId: ${chatId} (type: ${typeof chatId})`);
      }

      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString()
      });

      const url = `${this.baseURL}${this.apiPath}/chats/${chatId}/messages?${params}`;
      console.log('Fetching messages from:', url);

      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include'
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
      }

      const data = await response.json();
      
      return {
        messages: data.messages || [],
        total: data.total || 0,
        page: data.page || 1,
        perPage: data.per_page || 50
      };

    } catch (error) {
      console.error('Error getting chat messages:', error);
      throw error;
    }
  }

  /**
   * Lấy analytics cho chat
   * @param {number} chatId - ID chat
   * @returns {Promise<Object>} Analytics data
   */
  async getChatAnalytics(chatId) {
    try {
      const response = await fetch(`${this.baseURL}${this.apiPath}/chats/${chatId}/analytics`, {
        method: 'GET',
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        chatId: data.chat_id,
        chatInfo: data.chat_info || {},
        performanceMetrics: data.performance_metrics || {},
        sourcesAnalysis: data.sources_analysis || {},
        timeline: data.timeline || []
      };

    } catch (error) {
      console.error('Error getting chat analytics:', error);
      throw error;
    }
  }

  /**
   * Cập nhật chat
   * @param {number} chatId - ID chat
   * @param {Object} updates - Dữ liệu cập nhật
   * @param {string} updates.title - Tiêu đề mới (optional)
   * @param {boolean} updates.isActive - Trạng thái active (optional)
   * @returns {Promise<Object>} Thông tin chat đã cập nhật
   */
  async updateChat(chatId, { title = null, isActive = null } = {}) {
    try {
      const params = new URLSearchParams();
      if (title !== null) params.append('title', title);
      if (isActive !== null) params.append('is_active', isActive.toString());

      const response = await fetch(`${this.baseURL}${this.apiPath}/chats/${chatId}?${params}`, {
        method: 'PUT',
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Error updating chat:', error);
      throw error;
    }
  }

  /**
   * Xóa chat
   * @param {number} chatId - ID chat
   * @returns {Promise<Object>} Kết quả xóa
   */
  async deleteChat(chatId) {
    try {
      const response = await fetch(`${this.baseURL}${this.apiPath}/chats/${chatId}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Error deleting chat:', error);
      throw error;
    }
  }

  // ===== Utility Methods =====

  /**
   * Format tin nhắn cho UI
   * @param {Array} messages - Danh sách messages từ API
   * @returns {Array} Messages đã format cho UI
   */
  formatMessagesForUI(messages) {
    return messages.map(msg => ({
      id: msg.id,
      type: msg.role === 'user' ? 'user' : 'ai',
      content: msg.content,
      timestamp: new Date(msg.created_at),
      sources: msg.sources_info?.sources || [],
      confidence: msg.sources_info?.confidence || 0,
      processingTime: msg.processing_time || 0,
      messageType: msg.message_type || 'text'
    }));
  }

  /**
   * Format chat history cho sidebar
   * @param {Array} chats - Danh sách chats từ API
   * @returns {Array} Chats đã format cho UI
   */
  formatChatsForUI(chats) {
    return chats.map(chat => {
      // Safely calculate message count
      const userMessages = chat.stats?.message_stats?.user || 0;
      const assistantMessages = chat.stats?.message_stats?.assistant || 0;
      const messageCount = userMessages + assistantMessages;
      
      return {
        id: chat.id,
        title: chat.title,
        lastMessage: chat.stats?.last_message_at ? new Date(chat.stats.last_message_at) : null,
        messageCount: messageCount,
        sourcesUsed: chat.stats?.sources_used || 0,
        avgConfidence: chat.stats?.avg_confidence || 0,
        isActive: chat.is_active,
        createdAt: new Date(chat.created_at),
        updatedAt: new Date(chat.updated_at),
        categoryFilter: chat.category_filter
      };
    });
  }

  /**
   * Tạo session ID mới
   * @returns {string} Session ID
   */
  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // ===== Legacy API Support =====

  /**
   * Query đơn giản (không lưu lịch sử) - để tương thích
   * @param {string} question - Câu hỏi
   * @param {number} topK - Số lượng sources
   * @param {string} filterCategory - Lọc category
   * @returns {Promise<Object>} Response
   */
  async simpleQuery(question, topK = 5, filterCategory = null) {
    try {
      const response = await fetch(`${this.baseURL}${this.apiPath}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          question,
          top_k: topK,
          filter_category: filterCategory,
          include_sources: true
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Error in simple query:', error);
      throw error;
    }
  }
}

// Export singleton instance
const chatHistoryService = new ChatHistoryService();
export default chatHistoryService;
