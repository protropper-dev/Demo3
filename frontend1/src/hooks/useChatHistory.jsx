import { useState, useCallback, useEffect } from 'react';
import { useLocalStorage } from './useLocalStorage';

export const useChatHistory = () => {
  const [chatHistory, setChatHistory] = useLocalStorage('chatbot-history', []);
  const [currentSession, setCurrentSession] = useState(null);
  const [sessions, setSessions] = useLocalStorage('chatbot-sessions', []);

  // Create new session
  const createNewSession = useCallback(() => {
    const newSession = {
      id: Date.now(),
      name: `Cuộc trò chuyện ${new Date().toLocaleDateString('vi-VN')}`,
      createdAt: new Date().toISOString(),
      messages: []
    };
    
    setCurrentSession(newSession);
    setSessions(prev => [newSession, ...prev]);
    setChatHistory([]);
    
    return newSession;
  }, [setSessions]);

  // Load session
  const loadSession = useCallback((sessionId) => {
    const session = sessions.find(s => s.id === sessionId);
    if (session) {
      setCurrentSession(session);
      setChatHistory(session.messages || []);
    }
  }, [sessions]);

  // Save current session
  const saveCurrentSession = useCallback(() => {
    if (currentSession) {
      const updatedSession = {
        ...currentSession,
        messages: chatHistory,
        updatedAt: new Date().toISOString()
      };
      
      setCurrentSession(updatedSession);
      setSessions(prev => 
        prev.map(s => s.id === updatedSession.id ? updatedSession : s)
      );
    }
  }, [currentSession, chatHistory, setSessions]);

  // Add message to current session
  const addMessage = useCallback((message) => {
    const newMessage = {
      ...message,
      id: message.id || Date.now(),
      timestamp: message.timestamp || new Date().toISOString()
    };
    
    setChatHistory(prev => [...prev, newMessage]);
  }, []);

  // Clear current session
  const clearCurrentSession = useCallback(() => {
    setChatHistory([]);
    if (currentSession) {
      setCurrentSession(prev => ({
        ...prev,
        messages: []
      }));
    }
  }, [currentSession]);

  // Delete session
  const deleteSession = useCallback((sessionId) => {
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    
    if (currentSession && currentSession.id === sessionId) {
      setCurrentSession(null);
      setChatHistory([]);
    }
  }, [currentSession, setSessions]);

  // Rename session
  const renameSession = useCallback((sessionId, newName) => {
    setSessions(prev => 
      prev.map(s => 
        s.id === sessionId ? { ...s, name: newName } : s
      )
    );
    
    if (currentSession && currentSession.id === sessionId) {
      setCurrentSession(prev => ({ ...prev, name: newName }));
    }
  }, [currentSession, setSessions]);

  // Export session
  const exportSession = useCallback((sessionId) => {
    const session = sessions.find(s => s.id === sessionId);
    if (!session) return;

    const dataStr = JSON.stringify(session, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `chat-session-${session.name.replace(/[^a-z0-9]/gi, '_')}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, [sessions]);

  // Import session
  const importSession = useCallback((file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const session = JSON.parse(e.target.result);
          const importedSession = {
            ...session,
            id: Date.now(),
            importedAt: new Date().toISOString()
          };
          
          setSessions(prev => [importedSession, ...prev]);
          resolve(importedSession);
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }, [setSessions]);

  // Get session stats
  const getSessionStats = useCallback((sessionId) => {
    const session = sessions.find(s => s.id === sessionId);
    if (!session) return null;

    const messages = session.messages || [];
    const userMessages = messages.filter(m => m.type === 'user');
    const botMessages = messages.filter(m => m.type === 'bot');

    return {
      totalMessages: messages.length,
      userMessages: userMessages.length,
      botMessages: botMessages.length,
      duration: session.updatedAt ? 
        new Date(session.updatedAt) - new Date(session.createdAt) : 0,
      createdAt: session.createdAt,
      updatedAt: session.updatedAt
    };
  }, [sessions]);

  // Auto-save current session
  useEffect(() => {
    if (currentSession && chatHistory.length > 0) {
      const timeoutId = setTimeout(() => {
        saveCurrentSession();
      }, 1000); // Auto-save after 1 second of inactivity

      return () => clearTimeout(timeoutId);
    }
  }, [chatHistory, saveCurrentSession, currentSession]);

  // Initialize with latest session if no current session
  useEffect(() => {
    if (!currentSession && sessions.length > 0) {
      loadSession(sessions[0].id);
    }
  }, [currentSession, sessions, loadSession]);

  return {
    chatHistory,
    currentSession,
    sessions,
    createNewSession,
    loadSession,
    saveCurrentSession,
    addMessage,
    clearCurrentSession,
    deleteSession,
    renameSession,
    exportSession,
    importSession,
    getSessionStats
  };
};
