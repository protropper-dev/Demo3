import React from 'react';
import './MainChatArea.css';

const MainChatArea = ({ messages = [], currentChatTitle = "Cuộc trò chuyện 11" }) => {
  // Use real messages from props
  const displayMessages = messages;

  return (
    <div className="main-chat-area">
      {/* Header */}
      <div className="chat-header">
        <h1 className="chat-title">{currentChatTitle}</h1>
        <button className="settings-btn">⚙️</button>
      </div>

      {/* Messages */}
      <div className="messages-container">
        {displayMessages.map((message) => (
          <div key={message.id} className={`message-wrapper ${message.type}`}>
            <div className="message">
              <div className="message-avatar">
                {message.type === 'user' ? (
                  <span className="user-avatar">You</span>
                ) : (
                  <span className="ai-avatar">AI</span>
                )}
              </div>
              
              <div className="message-content">
                <div className={`message-text ${message.isLoading ? 'loading' : ''} ${message.isError ? 'error' : ''}`}>
                  {message.content}
                  {message.isLoading && <span className="loading-dots">...</span>}
                </div>
                
                {/* Show sources if available */}
                {message.sources && message.sources.length > 0 && (
                  <div className="message-sources">
                    <div className="sources-header">Nguồn tham khảo:</div>
                    <div className="sources-list">
                      {message.sources.slice(0, 3).map((source, index) => (
                        <div key={index} className="source-item">
                          <span className="source-title">{source.title || source.filename || `Nguồn ${index + 1}`}</span>
                          {source.score && (
                            <span className="source-score">({Math.round(source.score * 100)}%)</span>
                          )}
                        </div>
                      ))}
                      {message.sources.length > 3 && (
                        <div className="more-sources">+{message.sources.length - 3} nguồn khác</div>
                      )}
                    </div>
                  </div>
                )}
                
                <div className="message-actions">
                  <button className="action-btn copy-btn">Copy</button>
                  {message.type === 'user' ? (
                    <button className="action-btn edit-btn">Edit</button>
                  ) : (
                    <>
                      <button className="action-btn like-btn">👍</button>
                      <button className="action-btn dislike-btn">👎</button>
                      <button className="action-btn share-btn">🔗</button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MainChatArea;
