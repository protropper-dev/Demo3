import React from 'react';
import './Message.css';

const Message = ({ message }) => {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="message user-message">
      <div className="message-content">
        <div className="message-text">
          {message.text}
        </div>
        <div className="message-meta">
          <span className="message-time">
            {formatTime(message.timestamp)}
          </span>
          <span className="message-status">
            {message.status === 'sent' && '✓'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default Message;