import React, { useRef, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import Message from '../Message/Message';
import VinallamaMessage from '../VinallamaMessage/VinallamaMessage';
import LoadingSpinner from '../LoadingSpinner/LoadingSpinner';
import './ChatMessages.css';

const ChatMessages = () => {
  const { messages, isLoading } = useChat();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="chat-messages">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <h3>Chào mừng đến với Vinallama RAG Chatbot!</h3>
            <p>Hãy bắt đầu cuộc trò chuyện bằng cách gửi tin nhắn đầu tiên của bạn.</p>
            <div className="suggestions">
              <div className="suggestion-item">
                <span>💡</span>
                <span>Hỏi về tài liệu đã upload</span>
              </div>
              <div className="suggestion-item">
                <span>🔍</span>
                <span>Tìm kiếm thông tin cụ thể</span>
              </div>
              <div className="suggestion-item">
                <span>📚</span>
                <span>Khám phá knowledge base</span>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={message.id || index} className="message-wrapper">
              {message.type === 'user' ? (
                <Message message={message} />
              ) : (
                <VinallamaMessage message={message} />
              )}
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="loading-message">
            <LoadingSpinner size="small" />
            <span>Vinallama đang suy nghĩ...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatMessages;
