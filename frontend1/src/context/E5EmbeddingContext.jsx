import React, { createContext, useContext, useReducer, useCallback } from 'react';

const E5EmbeddingContext = createContext();

const initialState = {
  modelStatus: 'ready', // ready, loading, error
  isProcessing: false,
  progress: {
    percentage: 0,
    status: 'Ready',
    currentStep: 'idle',
    processedChunks: 0,
    totalChunks: 0
  },
  config: {
    modelPath: '/models/e5-large-v2',
    batchSize: 32,
    maxLength: 512,
    normalize: true
  },
  embeddings: [],
  error: null
};

const e5EmbeddingReducer = (state, action) => {
  switch (action.type) {
    case 'SET_MODEL_STATUS':
      return {
        ...state,
        modelStatus: action.payload
      };
    case 'SET_PROCESSING':
      return {
        ...state,
        isProcessing: action.payload
      };
    case 'UPDATE_PROGRESS':
      return {
        ...state,
        progress: { ...state.progress, ...action.payload }
      };
    case 'SET_EMBEDDINGS':
      return {
        ...state,
        embeddings: action.payload
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload
      };
    case 'UPDATE_CONFIG':
      return {
        ...state,
        config: { ...state.config, ...action.payload }
      };
    case 'RESET_PROGRESS':
      return {
        ...state,
        progress: initialState.progress
      };
    default:
      return state;
  }
};

export const E5EmbeddingProvider = ({ children }) => {
  const [state, dispatch] = useReducer(e5EmbeddingReducer, initialState);

  const generateEmbeddings = useCallback(async (texts) => {
    dispatch({ type: 'SET_PROCESSING', payload: true });
    dispatch({ type: 'SET_MODEL_STATUS', payload: 'loading' });
    dispatch({ type: 'RESET_PROGRESS' });

    try {
      const totalChunks = texts.length;
      const embeddings = [];

      for (let i = 0; i < texts.length; i++) {
        const progress = {
          percentage: Math.round(((i + 1) / totalChunks) * 100),
          status: `Đang xử lý chunk ${i + 1}/${totalChunks}`,
          currentStep: 'embedding',
          processedChunks: i + 1,
          totalChunks
        };

        dispatch({ type: 'UPDATE_PROGRESS', payload: progress });

        // Simulate embedding generation
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Generate mock embedding vector
        const embedding = Array.from({ length: 1024 }, () => Math.random() - 0.5);
        embeddings.push({
          id: i,
          text: texts[i],
          embedding,
          metadata: {
            timestamp: new Date().toISOString(),
            model: 'e5-large-v2'
          }
        });
      }

      dispatch({ type: 'SET_EMBEDDINGS', payload: embeddings });
      dispatch({ type: 'SET_MODEL_STATUS', payload: 'ready' });
      
      return embeddings;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      dispatch({ type: 'SET_MODEL_STATUS', payload: 'error' });
      throw error;
    } finally {
      dispatch({ type: 'SET_PROCESSING', payload: false });
    }
  }, []);

  const searchSimilar = useCallback(async (query, topK = 5) => {
    dispatch({ type: 'SET_PROCESSING', payload: true });
    
    try {
      // Generate embedding for query
      const queryEmbedding = Array.from({ length: 1024 }, () => Math.random() - 0.5);
      
      // Calculate similarities
      const similarities = state.embeddings.map((item, index) => {
        // Mock similarity calculation
        const similarity = Math.random();
        return {
          ...item,
          similarity,
          rank: index
        };
      });

      // Sort by similarity and return top K
      const results = similarities
        .sort((a, b) => b.similarity - a.similarity)
        .slice(0, topK);

      return results;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    } finally {
      dispatch({ type: 'SET_PROCESSING', payload: false });
    }
  }, [state.embeddings]);

  const updateConfig = useCallback((newConfig) => {
    dispatch({ type: 'UPDATE_CONFIG', payload: newConfig });
  }, []);

  const checkModelStatus = useCallback(async () => {
    dispatch({ type: 'SET_MODEL_STATUS', payload: 'loading' });
    
    try {
      // Simulate model status check
      await new Promise(resolve => setTimeout(resolve, 1000));
      dispatch({ type: 'SET_MODEL_STATUS', payload: 'ready' });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      dispatch({ type: 'SET_MODEL_STATUS', payload: 'error' });
    }
  }, []);

  const value = {
    ...state,
    generateEmbeddings,
    searchSimilar,
    updateConfig,
    checkModelStatus
  };

  return (
    <E5EmbeddingContext.Provider value={value}>
      {children}
    </E5EmbeddingContext.Provider>
  );
};

export const useE5Embedding = () => {
  const context = useContext(E5EmbeddingContext);
  if (!context) {
    throw new Error('useE5Embedding must be used within an E5EmbeddingProvider');
  }
  return context;
};
