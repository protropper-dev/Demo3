import { useState, useCallback, useEffect } from 'react';
import { useVinallama as useVinallamaContext } from '../context/VinallamaContext';

export const useVinallama = () => {
  const vinallamaContext = useVinallamaContext();
  const [conversationHistory, setConversationHistory] = useState([]);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize Vinallama model
  useEffect(() => {
    const initializeModel = async () => {
      try {
        await vinallamaContext.checkModelStatus();
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize Vinallama:', error);
      }
    };

    initializeModel();
  }, [vinallamaContext]);

  const generateResponse = useCallback(async (prompt, context = '') => {
    if (!isInitialized) {
      throw new Error('Vinallama model not initialized');
    }

    try {
      // Add user message to conversation history
      const userMessage = {
        role: 'user',
        content: prompt,
        timestamp: new Date().toISOString()
      };
      setConversationHistory(prev => [...prev, userMessage]);

      // Generate response
      const response = await vinallamaContext.generateResponse(prompt, context);
      
      // Add assistant response to conversation history
      const assistantMessage = {
        role: 'assistant',
        content: response,
        timestamp: new Date().toISOString(),
        context: context
      };
      setConversationHistory(prev => [...prev, assistantMessage]);

      return response;
    } catch (error) {
      console.error('Error generating response:', error);
      throw error;
    }
  }, [vinallamaContext, isInitialized]);

  const clearHistory = useCallback(() => {
    setConversationHistory([]);
  }, []);

  const getConversationContext = useCallback(() => {
    // Return last few messages for context
    return conversationHistory.slice(-6); // Last 3 exchanges
  }, [conversationHistory]);

  const updateModelConfig = useCallback((config) => {
    vinallamaContext.updateConfig(config);
  }, [vinallamaContext]);

  const getModelInfo = useCallback(() => {
    return {
      status: vinallamaContext.modelStatus,
      isGenerating: vinallamaContext.isGenerating,
      progress: vinallamaContext.progress,
      config: vinallamaContext.config,
      isInitialized
    };
  }, [vinallamaContext, isInitialized]);

  const exportConversation = useCallback(() => {
    const dataStr = JSON.stringify(conversationHistory, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `vinallama-conversation-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, [conversationHistory]);

  return {
    ...vinallamaContext,
    generateResponse,
    clearHistory,
    getConversationContext,
    updateModelConfig,
    getModelInfo,
    exportConversation,
    conversationHistory,
    isInitialized
  };
};
