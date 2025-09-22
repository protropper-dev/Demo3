import React from 'react';
import { useChat } from '../../context/ChatContext';
import { useVinallama } from '../../context/VinallamaContext';
import { useE5Embedding } from '../../context/E5EmbeddingContext';
import './ChatHeader.css';

const ChatHeader = ({ onToggleKnowledgeBase, showKnowledgeBase }) => {
  const { messages } = useChat();
  const { modelStatus: vinallamaStatus } = useVinallama();
  const { modelStatus: e5Status } = useE5Embedding();

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready': return '#4CAF50';
      case 'loading': return '#FF9800';
      case 'error': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  return (
    <header className="chat-header">
      <div className="header-left">
        <div className="logo-section">
          <img 
            src="/assets/images/vinallama-logo.png" 
            alt="Vinallama" 
            className="logo"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
          <h1>Vinallama RAG Chatbot</h1>
        </div>
      </div>

      <div className="header-center">
        <div className="model-status-indicators">
          <div className="status-indicator">
            <span 
              className="status-dot" 
              style={{ backgroundColor: getStatusColor(vinallamaStatus) }}
            ></span>
            <span className="status-text">Vinallama</span>
          </div>
          <div className="status-indicator">
            <span 
              className="status-dot" 
              style={{ backgroundColor: getStatusColor(e5Status) }}
            ></span>
            <span className="status-text">E5 Embedding</span>
          </div>
        </div>
      </div>

      <div className="header-right">
        <div className="message-count">
          <span className="count-badge">{messages.length}</span>
          <span className="count-label">tin nhắn</span>
        </div>
        
        <button 
          className={`knowledge-base-toggle ${showKnowledgeBase ? 'active' : ''}`}
          onClick={onToggleKnowledgeBase}
          title={showKnowledgeBase ? 'Đóng Knowledge Base' : 'Mở Knowledge Base'}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </button>
      </div>
    </header>
  );
};

export default ChatHeader;
