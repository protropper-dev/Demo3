import { useState, useCallback } from 'react';
import Backend1Service from '../services/backend1Service.jsx';

const useStreamingChat = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingError, setStreamingError] = useState(null);

  const startStreamingChat = useCallback(async (query, onToken, onComplete, onError) => {
    setIsStreaming(true);
    setStreamingError(null);

    try {
      const reader = await Backend1Service.enhancedChatStream(query);
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          onComplete && onComplete();
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep the incomplete line in buffer

        for (const line of lines) {
          if (line.trim() === '') continue;
          
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              switch (data.type) {
                case 'start':
                  console.log('Stream started:', data.message);
                  break;
                case 'token':
                  onToken && onToken(data.content);
                  break;
                case 'end':
                  console.log('Stream ended, response length:', data.response_length);
                  break;
                case 'error':
                  throw new Error(data.message);
                default:
                  console.log('Unknown stream event:', data);
              }
            } catch (parseError) {
              console.error('Error parsing stream data:', parseError);
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      setStreamingError(error.message);
      onError && onError(error);
    } finally {
      setIsStreaming(false);
    }
  }, []);

  const stopStreaming = useCallback(() => {
    setIsStreaming(false);
    setStreamingError(null);
  }, []);

  return {
    isStreaming,
    streamingError,
    startStreamingChat,
    stopStreaming
  };
};

export default useStreamingChat;
