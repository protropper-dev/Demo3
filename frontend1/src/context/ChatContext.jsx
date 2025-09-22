import React, { createContext, useContext, useReducer, useCallback } from 'react';
import Backend1Service from '../services/backend1Service.jsx';

const ChatContext = createContext();

const initialState = {
  messages: [],
  isLoading: false,
  error: null,
  typing: false
};

const chatReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload]
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload
      };
    case 'SET_TYPING':
      return {
        ...state,
        typing: action.payload
      };
    case 'CLEAR_MESSAGES':
      return {
        ...state,
        messages: []
      };
    default:
      return state;
  }
};

export const ChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  const sendMessage = useCallback(async (text, options = {}) => {
    const { useEnhanced = false, filterCategory = null } = options;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text,
      timestamp: new Date().toISOString(),
      status: 'sent'
    };

    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      let response;
      
      if (useEnhanced) {
        // Sử dụng Enhanced Chat API
        response = await Backend1Service.enhancedChat(text);
      } else {
        // Sử dụng Basic Chat API
        response = await Backend1Service.chat(text, null, filterCategory);
      }
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: useEnhanced ? response.response : response.response,
        timestamp: new Date().toISOString(),
        sources: response.sources || [],
        metadata: {
          query: response.query || text,
          totalSources: response.total_sources || 0,
          method: response.method || (useEnhanced ? 'enhanced' : 'basic')
        }
      };

      dispatch({ type: 'ADD_MESSAGE', payload: botMessage });
    } catch (error) {
      console.error('Lỗi gửi tin nhắn:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        text: `Lỗi: ${error.message}`,
        timestamp: new Date().toISOString(),
        error: true
      };
      
      dispatch({ type: 'ADD_MESSAGE', payload: errorMessage });
      dispatch({ type: 'SET_ERROR', payload: error.message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  const clearMessages = useCallback(() => {
    dispatch({ type: 'CLEAR_MESSAGES' });
  }, []);

  const value = {
    ...state,
    sendMessage,
    clearMessages
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
