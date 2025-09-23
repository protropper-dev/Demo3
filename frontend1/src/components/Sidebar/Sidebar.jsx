import React, { useState, useEffect } from 'react';
import chatHistoryService from '../../services/chatHistoryService';
import filesService from '../../services/filesService';
import './Sidebar.css';

const Sidebar = ({ onNewChat, onChatSelect, selectedChat, isCollapsed, onToggleCollapse }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showMoreChats, setShowMoreChats] = useState(false);
  const [showFilesDropdown, setShowFilesDropdown] = useState(false);
  const [recentFiles, setRecentFiles] = useState([]);
  const [allFilesData, setAllFilesData] = useState(null);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [loadingChats, setLoadingChats] = useState(false);
  const [editingChatId, setEditingChatId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  // Utility function để kiểm tra backend status
  const checkBackendHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        },
        cache: 'no-store'
      });
      return response.ok;
    } catch (error) {
      console.error('Backend health check failed:', error);
      return false;
    }
  };

  // Fetch all files data from new Files API
  useEffect(() => {
    const fetchAllFiles = async () => {
      setLoadingFiles(true);
      
      // Kiểm tra backend health trước
      const isHealthy = await checkBackendHealth();
      if (!isHealthy) {
        console.log('Backend not healthy, skipping file fetch');
        setLoadingFiles(false);
        return;
      }
      
      try {
        const data = await filesService.getAllFiles();
        
        // Lưu dữ liệu tất cả files
        setAllFilesData(data);
        
        // Lưu recent uploads (10 files gần nhất)
        setRecentFiles(data.recent_uploads || []);
        
        console.log('Successfully fetched all files:', {
          recentUploads: data.recent_uploads?.length || 0,
          totalFiles: data.total_files || 0,
          categories: Object.keys(data.categories || {})
        });
        
      } catch (error) {
        console.error('Error fetching files:', error);
        setRecentFiles([]);
        setAllFilesData(null);
      } finally {
        setLoadingFiles(false);
      }
    };

    // Delay một chút để đảm bảo backend đã sẵn sàng
    const timer = setTimeout(fetchAllFiles, 1000);
    return () => clearTimeout(timer);
  }, []);

  // Fetch chat history using new service
  useEffect(() => {
    const fetchChatHistory = async () => {
      setLoadingChats(true);
      
      // Kiểm tra backend health trước
      const isHealthy = await checkBackendHealth();
      if (!isHealthy) {
        console.log('Backend not healthy, skipping chat history fetch');
        setLoadingChats(false);
        return;
      }
      
      try {
        const result = await chatHistoryService.getChatHistory({
          page: 1,
          perPage: 20,
          userId: null // Có thể thêm user management sau
        });
        
        const formattedChats = chatHistoryService.formatChatsForUI(result.chats);
        setChatHistory(formattedChats);
        console.log('Successfully fetched chat history:', formattedChats.length, 'chats');
        console.log('Sample chat object:', formattedChats[0]); // Debug first chat
        
      } catch (error) {
        console.error('Error fetching chat history:', error);
        setChatHistory([]);
      } finally {
        setLoadingChats(false);
      }
    };

    // Delay một chút để đảm bảo backend đã sẵn sàng
    const timer = setTimeout(fetchChatHistory, 1500);
    return () => clearTimeout(timer);
  }, []);

  const getFileIcon = (filename) => {
    const extension = filename.split('.').pop().toLowerCase();
    switch (extension) {
      case 'pdf':
        return '📕';
      case 'doc':
      case 'docx':
        return '📄';
      case 'txt':
        return '📝';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return '🖼️';
      case 'py':
      case 'js':
      case 'jsx':
      case 'ts':
      case 'tsx':
      case 'java':
      case 'cpp':
      case 'c':
        return '💻';
      case 'zip':
      case 'rar':
      case '7z':
        return '📦';
      default:
        return '📄';
    }
  };

  // Format time for display
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'vài giây trước';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} phút trước`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} giờ trước`;
    return `${Math.floor(diff / 86400000)} ngày trước`;
  };

  // Handle edit chat title
  const handleEditChat = (chatId, currentTitle) => {
    setEditingChatId(chatId);
    setEditTitle(currentTitle);
  };

  const handleSaveEdit = async (chatId) => {
    try {
      await chatHistoryService.updateChat(chatId, { title: editTitle });
      
      // Update local state
      setChatHistory(prev => prev.map(chat => 
        chat.id === chatId ? { ...chat, title: editTitle } : chat
      ));
      setEditingChatId(null);
      setEditTitle('');
      
    } catch (error) {
      console.error('Error updating chat title:', error);
      alert('Lỗi khi cập nhật tiêu đề: ' + error.message);
    }
  };

  const handleCancelEdit = () => {
    setEditingChatId(null);
    setEditTitle('');
  };

  // Handle delete chat
  const handleDeleteChat = async (chatId) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa cuộc trò chuyện này?')) {
      try {
        await chatHistoryService.deleteChat(chatId);
        
        // Remove from local state
        setChatHistory(prev => prev.filter(chat => chat.id !== chatId));
        
        // If this was the selected chat, clear selection
        if (selectedChat === chatId) {
          onChatSelect(null);
        }
        
      } catch (error) {
        console.error('Error deleting chat:', error);
        alert('Lỗi khi xóa cuộc trò chuyện: ' + error.message);
      }
    }
  };

  const filteredChats = chatHistory.filter(chat =>
    chat.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const displayedChats = showMoreChats ? filteredChats : filteredChats.slice(0, 4);
  const displayedRecentFiles = recentFiles.slice(0, 10); // Hiển thị tối đa 10 files gần đây

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      {/* Header */}
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-icon">AI</span>
          {!isCollapsed && <span className="logo-text">ChatGPT</span>}
        </div>
        
        {!isCollapsed && (
          <>
            <button className="new-chat-btn" onClick={onNewChat}>
              <span className="plus-icon">+</span>
              Tin mới
            </button>
            
            <div className="search-container">
              <span className="search-icon">🔍</span>
              <input
                type="text"
                placeholder="Tìm kiếm cuộc trò chuyện..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
          </>
        )}
        
        {isCollapsed && (
          <button className="new-chat-btn collapsed" onClick={onNewChat} title="Tin mới">
            <span className="plus-icon">+</span>
          </button>
        )}
      </div>


      {/* Chat History */}
      {!isCollapsed && (
        <div className="chat-history-section">
          <h3 className="section-title">Lịch sử trò chuyện</h3>
          <div className="chat-list">
            {loadingChats ? (
              <div className="loading-chats">
                <span className="loading-text">Đang tải...</span>
              </div>
            ) : displayedChats.length > 0 ? (
              displayedChats.map((chat) => (
                <div
                  key={chat.id}
                  className={`chat-item ${selectedChat === chat.id ? 'selected' : ''}`}
                  onClick={() => onChatSelect(chat)}
                >
                  <div className="chat-icon">C</div>
                  <div className="chat-content">
                    {editingChatId === chat.id ? (
                      <div className="edit-input-container">
                        <input
                          type="text"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          className="edit-input"
                          onClick={(e) => e.stopPropagation()}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              handleSaveEdit(chat.id);
                            } else if (e.key === 'Escape') {
                              handleCancelEdit();
                            }
                          }}
                          autoFocus
                        />
                        <div className="edit-actions">
                          <button 
                            className="save-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSaveEdit(chat.id);
                            }}
                          >
                            ✓
                          </button>
                          <button 
                            className="cancel-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCancelEdit();
                            }}
                          >
                            ✗
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="chat-title">{chat.title}</div>
                        <div className="chat-time">{formatTime(chat.updated_at)}</div>
                      </>
                    )}
                  </div>
                  {editingChatId !== chat.id && (
                    <div className="chat-actions">
                      <button 
                        className="edit-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEditChat(chat.id, chat.title);
                        }}
                        title="Chỉnh sửa"
                      >
                        ✏️
                      </button>
                      <button 
                        className="delete-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteChat(chat.id);
                        }}
                        title="Xóa"
                      >
                        🗑️
                      </button>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="no-chats">
                <span className="no-chats-text">Chưa có cuộc trò chuyện nào</span>
              </div>
            )}
          </div>
          
          {filteredChats.length > 4 && (
            <button 
              className="see-more-btn"
              onClick={() => setShowMoreChats(!showMoreChats)}
            >
              {showMoreChats ? 'Thu gọn' : 'Xem thêm'}
            </button>
          )}
        </div>
      )}

      {/* Files Section */}
      {!isCollapsed && (
        <div className="files-section">
          <h3 className="section-title">
            <span className="folder-icon">📁</span>
            Tệp tin
          </h3>
          
          {/* Recent Files */}
          <div className="files-list">
            {loadingFiles ? (
              <div className="loading-files">
                <span className="loading-text">Đang tải...</span>
              </div>
            ) : displayedRecentFiles.length > 0 ? (
              displayedRecentFiles.map((file, index) => (
                <div key={index} className="file-item">
                  <span className="file-icon">{filesService.getFileIcon(file.filename)}</span>
                  <div className="file-info">
                    <span className="file-name" title={file.filename}>
                      {file.filename.length > 20 ? file.filename.substring(0, 20) + '...' : file.filename}
                    </span>
                    <span className="file-meta">
                      {filesService.formatFileSize(file.size)} • {filesService.formatTime(file.uploaded_at)}
                    </span>
                  </div>
                  <div className="file-status">
                    {file.is_embedded ? (
                      <span className="status-embedded" title="Đã embedding">✅</span>
                    ) : (
                      <span className="status-pending" title="Chưa embedding">⏳</span>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="no-files">
                <span className="no-files-text">Chưa có tệp nào</span>
              </div>
            )}
          </div>
          
          {/* View All Files Button */}
          {allFilesData && allFilesData.total_files > 0 && (
            <div className="files-actions">
              <button 
                className="view-all-files-btn"
                onClick={() => setShowFilesDropdown(!showFilesDropdown)}
              >
                <span className="btn-icon">📋</span>
                Xem thêm ({allFilesData.total_files} files)
                <span className={`dropdown-arrow ${showFilesDropdown ? 'open' : ''}`}>▼</span>
              </button>
              
            </div>
          )}
        </div>
      )}

      {/* Toggle Button */}
      <button className="toggle-btn" onClick={onToggleCollapse}>
        {isCollapsed ? '▶' : '◀'}
      </button>

      {/* Files Popup Modal */}
      {showFilesDropdown && (
        <div className="files-popup-overlay" onClick={() => setShowFilesDropdown(false)}>
          <div className="files-popup-modal" onClick={(e) => e.stopPropagation()}>
            <div className="popup-header">
              <h3>Tất cả tệp tin</h3>
              <button 
                className="close-popup"
                onClick={() => setShowFilesDropdown(false)}
              >
                ✕
              </button>
            </div>
            
            <div className="popup-content">
              {Object.entries(allFilesData.all_files || {}).map(([category, files]) => (
                <div key={category} className="popup-category-section">
                  <div className="popup-category-header">
                    <span className="category-icon">
                      {category === 'Luật' ? '⚖️' : 
                       category === 'Tài liệu Tiếng Anh' ? '🇬🇧' :
                       category === 'Tài liệu Tiếng Việt' ? '🇻🇳' :
                       category === 'Files Upload' ? '📤' : '📁'}
                    </span>
                    <span className="category-name">{category}</span>
                    <span className="category-count">({files.length} files)</span>
                  </div>
                  
                  <div className="popup-category-files">
                    {files.map((file, index) => (
                      <div key={index} className="popup-file-item">
                        <span className="file-icon">{filesService.getFileIcon(file.filename)}</span>
                        <div className="file-info">
                          <span className="file-name" title={file.filename}>
                            {file.filename}
                          </span>
                          <span className="file-meta">
                            {filesService.formatFileSize(file.size)} • 
                            {filesService.formatTime(file.modified || file.uploaded_at)}
                            {file.is_embedded && <span className="embedded-badge">✅</span>}
                          </span>
                        </div>
                        <div className="file-status">
                          {file.is_embedded ? (
                            <span className="status-embedded" title="Đã embedding">✅</span>
                          ) : (
                            <span className="status-pending" title="Chưa embedding">⏳</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="popup-footer">
              <div className="total-stats">
                Tổng cộng: {allFilesData.total_files} files
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
