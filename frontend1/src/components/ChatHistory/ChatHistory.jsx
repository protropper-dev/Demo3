// ChatHistory Component - Hiển thị lịch sử trò chuyện
import React, { useState, useEffect } from 'react';
import chatHistoryService from '../../services/chatHistoryService';
import LoadingSpinner from '../LoadingSpinner/LoadingSpinner';
import './ChatHistory.css';

const ChatHistory = ({ 
  userId = null, 
  onChatSelect = null, 
  selectedChatId = null,
  onClose = null 
}) => {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalChats, setTotalChats] = useState(0);
  const [filter, setFilter] = useState({
    categoryFilter: null,
    perPage: 10
  });

  // Load chat history
  const loadChatHistory = async (pageNum = 1, resetList = false) => {
    try {
      setLoading(true);
      setError(null);

      const result = await chatHistoryService.getChatHistory({
        page: pageNum,
        perPage: filter.perPage,
        userId: userId,
        categoryFilter: filter.categoryFilter
      });

      const formattedChats = chatHistoryService.formatChatsForUI(result.chats);

      if (resetList || pageNum === 1) {
        setChats(formattedChats);
      } else {
        setChats(prev => [...prev, ...formattedChats]);
      }

      setPage(pageNum);
      setTotalChats(result.total);
      setTotalPages(Math.ceil(result.total / filter.perPage));

    } catch (err) {
      console.error('Error loading chat history:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Load on mount and filter changes
  useEffect(() => {
    loadChatHistory(1, true);
  }, [userId, filter.categoryFilter, filter.perPage]);

  // Handle chat selection
  const handleChatClick = (chat) => {
    if (onChatSelect) {
      onChatSelect(chat);
    }
  };

  // Handle load more
  const handleLoadMore = () => {
    if (page < totalPages && !loading) {
      loadChatHistory(page + 1, false);
    }
  };

  // Handle filter change
  const handleFilterChange = (newFilter) => {
    setFilter(prev => ({ ...prev, ...newFilter }));
  };

  // Handle delete chat
  const handleDeleteChat = async (chatId, event) => {
    event.stopPropagation(); // Prevent chat selection
    
    if (!window.confirm('Bạn có chắc muốn xóa cuộc trò chuyện này?')) {
      return;
    }

    try {
      await chatHistoryService.deleteChat(chatId);
      
      // Remove from UI
      setChats(prev => prev.filter(chat => chat.id !== chatId));
      setTotalChats(prev => prev - 1);
      
      // Notify parent if this was selected chat
      if (selectedChatId === chatId && onChatSelect) {
        onChatSelect(null);
      }

    } catch (err) {
      console.error('Error deleting chat:', err);
      alert('Lỗi khi xóa cuộc trò chuyện: ' + err.message);
    }
  };

  // Format date for display
  const formatDate = (date) => {
    if (!date) return 'N/A';
    
    const now = new Date();
    const diffHours = (now - date) / (1000 * 60 * 60);
    
    if (diffHours < 1) {
      return 'Vừa xong';
    } else if (diffHours < 24) {
      return `${Math.floor(diffHours)} giờ trước`;
    } else if (diffHours < 24 * 7) {
      return `${Math.floor(diffHours / 24)} ngày trước`;
    } else {
      return date.toLocaleDateString('vi-VN');
    }
  };

  return (
    <div className="chat-history">
      {/* Header */}
      <div className="chat-history-header">
        <h3>Lịch sử trò chuyện</h3>
        {onClose && (
          <button className="close-button" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="chat-history-filters">
        <select 
          value={filter.categoryFilter || ''} 
          onChange={(e) => handleFilterChange({ categoryFilter: e.target.value || null })}
          className="filter-select"
        >
          <option value="">Tất cả danh mục</option>
          <option value="luat">Luật pháp</option>
          <option value="english">Tiếng Anh</option>
          <option value="vietnamese">Tiếng Việt</option>
        </select>

        <select 
          value={filter.perPage} 
          onChange={(e) => handleFilterChange({ perPage: parseInt(e.target.value) })}
          className="filter-select"
        >
          <option value={5}>5 chat</option>
          <option value={10}>10 chat</option>
          <option value={20}>20 chat</option>
        </select>
      </div>

      {/* Stats */}
      <div className="chat-history-stats">
        <span className="stats-item">
          <i className="fas fa-comments"></i>
          {totalChats} cuộc trò chuyện
        </span>
      </div>

      {/* Error */}
      {error && (
        <div className="chat-history-error">
          <i className="fas fa-exclamation-triangle"></i>
          <span>Lỗi: {error}</span>
          <button onClick={() => loadChatHistory(1, true)} className="retry-button">
            Thử lại
          </button>
        </div>
      )}

      {/* Chat List */}
      <div className="chat-history-list">
        {chats.map(chat => (
          <div 
            key={chat.id}
            className={`chat-history-item ${selectedChatId === chat.id ? 'selected' : ''}`}
            onClick={() => handleChatClick(chat)}
          >
            {/* Chat Header */}
            <div className="chat-item-header">
              <div className="chat-title" title={chat.title}>
                {chat.title}
              </div>
              <div className="chat-actions">
                <button 
                  className="delete-chat-btn"
                  onClick={(e) => handleDeleteChat(chat.id, e)}
                  title="Xóa cuộc trò chuyện"
                >
                  <i className="fas fa-trash"></i>
                </button>
              </div>
            </div>

            {/* Chat Stats */}
            <div className="chat-item-stats">
              <div className="stat-item">
                <i className="fas fa-comments"></i>
                <span>{chat.messageCount} tin nhắn</span>
              </div>
              
              <div className="stat-item">
                <i className="fas fa-book"></i>
                <span>{chat.sourcesUsed} nguồn</span>
              </div>
              
              {chat.avgConfidence > 0 && (
                <div className="stat-item">
                  <i className="fas fa-chart-line"></i>
                  <span>{(chat.avgConfidence * 100).toFixed(0)}% tin cậy</span>
                </div>
              )}
            </div>

            {/* Chat Meta */}
            <div className="chat-item-meta">
              <div className="chat-time">
                <i className="fas fa-clock"></i>
                {formatDate(chat.lastMessage || chat.updatedAt)}
              </div>
              
              {chat.categoryFilter && (
                <div className="chat-category">
                  <i className="fas fa-tag"></i>
                  {chat.categoryFilter}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading more */}
        {loading && (
          <div className="loading-more">
            <LoadingSpinner size="small" />
            <span>Đang tải...</span>
          </div>
        )}

        {/* Load More Button */}
        {!loading && page < totalPages && (
          <button 
            className="load-more-button"
            onClick={handleLoadMore}
          >
            <i className="fas fa-chevron-down"></i>
            Tải thêm ({totalChats - chats.length} còn lại)
          </button>
        )}

        {/* Empty State */}
        {!loading && chats.length === 0 && !error && (
          <div className="empty-state">
            <i className="fas fa-comments"></i>
            <p>Chưa có cuộc trò chuyện nào</p>
            <small>Bắt đầu chat để tạo lịch sử</small>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="chat-history-footer">
        <small>
          Hiển thị {chats.length} / {totalChats} cuộc trò chuyện
        </small>
      </div>
    </div>
  );
};

export default ChatHistory;
