import React, { useState, useEffect } from 'react';
import { ChatProvider } from '../../context/ChatContext';
import { RAGProvider } from '../../context/RAGContext';
import { VinallamaProvider } from '../../context/VinallamaContext';
import { E5EmbeddingProvider } from '../../context/E5EmbeddingContext';
import { KnowledgeBaseProvider } from '../../context/KnowledgeBaseContext';
import { ThemeProvider } from '../../context/ThemeContext';
import chatHistoryService from '../../services/chatHistoryService';

import Sidebar from '../Sidebar/Sidebar';
import MainChatArea from '../MainChatArea/MainChatArea';
import ChatInput from '../ChatInput/ChatInput';
import KnowledgeBase from '../KnowledgeBase/KnowledgeBase';
import ModelStatus from '../ModelStatus/ModelStatus';
import ConnectionStatus from '../ConnectionStatus/ConnectionStatus';
import LoadingSpinner from '../LoadingSpinner/LoadingSpinner';

import './Chatbot.css';

const Chatbot = () => {
  const [showKnowledgeBase, setShowKnowledgeBase] = useState(false);
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [currentChatTitle, setCurrentChatTitle] = useState('Tin nhắn mới');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    // Initialize app and session
    const initializeApp = async () => {
      try {
        // Tạo session ID mới
        const newSessionId = chatHistoryService.generateSessionId();
        setSessionId(newSessionId);
        console.log('Chatbot initialized with session:', newSessionId);
      } catch (error) {
        console.error('Lỗi khởi tạo ứng dụng:', error);
      }
    };

    initializeApp();
  }, []);

  const handleNewChat = () => {
    setSelectedChat(null);
    setCurrentChatId(null);
    setMessages([]);
    setCurrentChatTitle('Tin nhắn mới');
    setShowKnowledgeBase(false);
  };

  const handleChatSelect = async (chat) => {
    if (!chat) {
      handleNewChat();
      return;
    }

    // Validate chat object
    if (!chat.id || typeof chat.id !== 'number') {
      console.error('Invalid chat object:', chat);
      alert('Lỗi: Chat ID không hợp lệ');
      return;
    }

    try {
      console.log('Selecting chat:', chat);
      
      setSelectedChat(chat.id);
      setCurrentChatId(chat.id);
      setCurrentChatTitle(chat.title);
      setShowKnowledgeBase(false);
      
      // Load messages từ chat history
      console.log('Loading messages for chat ID:', chat.id);
      const result = await chatHistoryService.getChatMessages(chat.id, { page: 1, perPage: 100 });
      
      // Format messages cho UI
      const formattedMessages = chatHistoryService.formatMessagesForUI(result.messages);
      setMessages(formattedMessages);
      
      console.log('Loaded', formattedMessages.length, 'messages for chat', chat.id);
      
    } catch (error) {
      console.error('Error loading chat messages:', error);
      console.error('Chat object was:', chat);
      alert('Lỗi khi tải tin nhắn: ' + error.message);
    }
  };

  const handleSendMessage = async (message) => {
    setIsSending(true);
    
    // Add user message to UI immediately
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    
    // Show loading state
    const loadingMessage = {
      id: Date.now() + 1,
      type: 'ai',
      content: 'Đang suy nghĩ...',
      timestamp: new Date(),
      isLoading: true
    };
    setMessages(prev => [...prev, loadingMessage]);
    
    try {
      // Sử dụng Chat History Service mới
      const result = await chatHistoryService.sendMessage({
        message: message,
        chatId: currentChatId,
        userId: 1, // Có thể lấy từ user context
        sessionId: sessionId,
        topK: 5,
        filterCategory: null
      });
      
      // Cập nhật chat ID nếu là chat mới
      if (!currentChatId) {
        setCurrentChatId(result.chatId);
        setSelectedChat(result.chatId);
        
        // Cập nhật title nếu cần
        const shortTitle = message.length > 50 ? message.substring(0, 50) + '...' : message;
        setCurrentChatTitle(shortTitle);
      }
      
      // Remove loading message and add real response
      setMessages(prev => {
        const withoutLoading = prev.filter(msg => !msg.isLoading);
        return [...withoutLoading, {
          id: result.messageId,
          type: 'ai',
          content: result.aiResponse,
          timestamp: new Date(result.timestamp),
          sources: result.sources || [],
          confidence: result.confidence,
          processingTime: result.processingTime,
          totalSources: result.totalSources
        }];
      });
      
      console.log('Message sent successfully:', result);
      
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Remove loading message and add error message
      setMessages(prev => {
        const withoutLoading = prev.filter(msg => !msg.isLoading);
        return [...withoutLoading, {
          id: Date.now() + 2,
          type: 'ai',
          content: `Xin lỗi, có lỗi xảy ra khi xử lý tin nhắn của bạn: ${error.message}`,
          timestamp: new Date(),
          isError: true
        }];
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleAttachFile = () => {
    console.log('Attach file clicked');
    // Implement file attachment logic
  };


  const handleToggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <ThemeProvider>
      <ChatProvider>
        <RAGProvider>
          <VinallamaProvider>
            <E5EmbeddingProvider>
              <KnowledgeBaseProvider>
                <div className="chatbot-container">
                  <Sidebar 
                    onNewChat={handleNewChat}
                    onChatSelect={handleChatSelect}
                    selectedChat={selectedChat}
                    isCollapsed={isSidebarCollapsed}
                    onToggleCollapse={handleToggleSidebar}
                    currentChatId={currentChatId}
                    sessionId={sessionId}
                  />
                  
                  <div className="main-content">
                    {showKnowledgeBase ? (
                      <KnowledgeBase />
                    ) : (
                      <>
                        <MainChatArea 
                          messages={messages}
                          currentChatTitle={currentChatTitle}
                        />
                        <ChatInput 
                          onSendMessage={handleSendMessage}
                          onAttachFile={handleAttachFile}
                          isSending={isSending}
                        />
                      </>
                    )}
                  </div>
                  
                  <div className="status-panel">
                    <ConnectionStatus />
                    <ModelStatus />
                  </div>
                </div>
              </KnowledgeBaseProvider>
            </E5EmbeddingProvider>
          </VinallamaProvider>
        </RAGProvider>
      </ChatProvider>
    </ThemeProvider>
  );
};

export default Chatbot;
