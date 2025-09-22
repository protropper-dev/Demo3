import React from 'react';
import SourceCitations from '../SourceCitations/SourceCitations';
import './VinallamaMessage.css';

const VinallamaMessage = ({ message }) => {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="message bot-message">
      <div className="message-avatar">
        <div className="avatar">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
      </div>
      
      <div className="message-content">
        <div className="message-text">
          {message.text}
        </div>
        
        {message.sources && message.sources.length > 0 && (
          <SourceCitations sources={message.sources} />
        )}
        
        {message.metadata && (
          <div className="message-metadata">
            <div className="metadata-item">
              <span className="metadata-label">Method:</span>
              <span className="metadata-value">{message.metadata.method}</span>
            </div>
            {message.metadata.totalSources > 0 && (
              <div className="metadata-item">
                <span className="metadata-label">Sources:</span>
                <span className="metadata-value">{message.metadata.totalSources}</span>
              </div>
            )}
          </div>
        )}
        
        <div className="message-meta">
          <span className="message-time">
            {formatTime(message.timestamp)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default VinallamaMessage;