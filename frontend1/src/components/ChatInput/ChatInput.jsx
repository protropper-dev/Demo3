import React, { useState, useRef } from 'react';
import './ChatInput.css';

const ChatInput = ({ onSendMessage, onAttachFile, disabled = false, isSending = false }) => {
  const [message, setMessage] = useState('');
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled && !isSending) {
      onSendMessage(message.trim());
      setMessage('');
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      if (e.shiftKey) {
        // Allow Shift+Enter for new line, do nothing
        return;
      } else {
        // Enter without Shift sends message
        e.preventDefault();
        handleSubmit(e);
      }
    }
  };

  const handleAttachClick = () => {
    if (!disabled && !isSending && onAttachFile) {
      onAttachFile();
    }
  };


  return (
    <div className="chat-input-container">
      <form onSubmit={handleSubmit} className="chat-input-form">
        <div className="input-actions">
          <button
            type="button"
            className="action-button attach-btn"
            onClick={handleAttachClick}
            disabled={disabled || isSending}
            title="Đính kèm tệp"
          >
            📎
          </button>
        </div>

        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isSending ? "Đang gửi..." : "Nhập tin nhắn... (Shift+Enter để xuống dòng)"}
            className="message-input"
            disabled={disabled || isSending}
            rows={1}
            style={{
              height: 'auto',
              minHeight: '44px',
              maxHeight: '120px'
            }}
            onInput={(e) => {
              e.target.style.height = 'auto';
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
            }}
          />
        </div>

        <button
          type="submit"
          className="send-button"
          disabled={disabled || isSending || !message.trim()}
          title={isSending ? "Đang gửi..." : "Gửi tin nhắn"}
        >
          {isSending ? "⏳" : "➤"}
        </button>
      </form>
    </div>
  );
};

export default ChatInput;
