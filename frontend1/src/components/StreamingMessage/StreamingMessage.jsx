import React, { useState, useEffect, useRef } from 'react';
import useStreamingChat from '../../hooks/useStreamingChat.jsx';
import './StreamingMessage.css';

const StreamingMessage = ({ query, onComplete, onError }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messageRef = useRef(null);
  const { startStreamingChat, isStreaming, streamingError } = useStreamingChat();

  useEffect(() => {
    if (!query) return;

    const handleToken = (token) => {
      setDisplayedText(prev => prev + token);
      setIsTyping(true);
      
      // Auto scroll to bottom
      if (messageRef.current) {
        messageRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    };

    const handleComplete = () => {
      setIsTyping(false);
      onComplete && onComplete(displayedText);
    };

    const handleError = (error) => {
      setIsTyping(false);
      onError && onError(error);
    };

    // Start streaming
    startStreamingChat(query, handleToken, handleComplete, handleError);
  }, [query, startStreamingChat, onComplete, onError]);

  if (streamingError) {
    return (
      <div className="streaming-message error">
        <div className="message-content">
          <div className="error-text">
            ❌ Lỗi streaming: {streamingError}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="streaming-message" ref={messageRef}>
      <div className="message-content">
        <div className="streaming-text">
          {displayedText}
          {isTyping && (
            <span className="typing-cursor">|</span>
          )}
        </div>
        
        {isStreaming && (
          <div className="streaming-status">
            <div className="streaming-indicator">
              <div className="streaming-dot"></div>
              <div className="streaming-dot"></div>
              <div className="streaming-dot"></div>
            </div>
            <span className="streaming-label">Đang trả lời...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default StreamingMessage;
