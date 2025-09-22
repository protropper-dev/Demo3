import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import { useRAG } from '../../context/RAGContext';
import './MessageInput.css';

const MessageInput = () => {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const textareaRef = useRef(null);
  
  const { sendMessage, isLoading } = useChat();
  const { isRAGEnabled, toggleRAG } = useRAG();

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [message]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!message.trim() || isLoading) return;

    const messageText = message.trim();
    setMessage('');
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    try {
      await sendMessage(messageText);
    } catch (error) {
      console.error('Lỗi gửi tin nhắn:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleTyping = (e) => {
    setMessage(e.target.value);
    setIsTyping(true);
    
    // Clear typing indicator after 1 second of no typing
    clearTimeout(window.typingTimeout);
    window.typingTimeout = setTimeout(() => {
      setIsTyping(false);
    }, 1000);
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    // Handle file upload logic here
    console.log('Files to upload:', files);
  };

  const handleVoiceInput = () => {
    // Voice input logic here
    console.log('Voice input activated');
  };

  return (
    <div className="message-input-container">
      <form onSubmit={handleSubmit} className="message-input-form">
        <div className="input-wrapper">
          {/* RAG Toggle */}
          <div className="rag-toggle-section">
            <label className="rag-toggle">
              <input
                type="checkbox"
                checked={isRAGEnabled}
                onChange={toggleRAG}
              />
              <span className="toggle-slider"></span>
              <span className="toggle-label">RAG</span>
            </label>
          </div>

          {/* File Upload Button */}
          <div className="file-upload-section">
            <label className="file-upload-button">
              <input
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.md"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
              </svg>
            </label>
          </div>

          {/* Voice Input Button */}
          <div className="voice-input-section">
            <button
              type="button"
              className="voice-input-button"
              onClick={handleVoiceInput}
              title="Nhập bằng giọng nói"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12,14C13.66,14 15,12.66 15,11V5C15,3.34 13.66,2 12,2C10.34,2 9,3.34 9,5V11C9,12.66 10.34,14 12,14M19.73,11C19.73,15.42 16.16,19.11 12,19.11C7.84,19.11 4.27,15.42 4.27,11H2.73C2.73,16.18 6.55,20.5 12,20.5C17.45,20.5 21.27,16.18 21.27,11H19.73Z"/>
              </svg>
            </button>
          </div>

          {/* Text Input */}
          <div className="text-input-section">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleTyping}
              onKeyPress={handleKeyPress}
              placeholder="Nhập tin nhắn của bạn... (Enter để gửi, Shift+Enter để xuống dòng)"
              className="message-textarea"
              rows="1"
              disabled={isLoading}
            />
          </div>

          {/* Send Button */}
          <div className="send-button-section">
            <button
              type="submit"
              className={`send-button ${!message.trim() || isLoading ? 'disabled' : ''}`}
              disabled={!message.trim() || isLoading}
            >
              {isLoading ? (
                <div className="loading-spinner-small"></div>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z"/>
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Typing Indicator */}
        {isTyping && (
          <div className="typing-indicator">
            <span>Đang nhập...</span>
          </div>
        )}

        {/* Status Bar */}
        <div className="input-status-bar">
          <div className="status-left">
            <span className="rag-status">
              {isRAGEnabled ? '🔍 RAG Enabled' : '💬 Chat Only'}
            </span>
          </div>
          <div className="status-right">
            <span className="character-count">
              {message.length}/2000
            </span>
          </div>
        </div>
      </form>
    </div>
  );
};

export default MessageInput;
