import React, { createContext, useContext, useReducer, useCallback } from 'react';

const VinallamaContext = createContext();

const initialState = {
  modelStatus: 'ready', // ready, loading, error
  isGenerating: false,
  progress: {
    percentage: 0,
    status: 'Ready',
    currentStep: 'idle'
  },
  config: {
    modelPath: '/models/vinallama',
    maxTokens: 2048,
    temperature: 0.7,
    topP: 0.9,
    topK: 40
  },
  error: null
};

const vinallamaReducer = (state, action) => {
  switch (action.type) {
    case 'SET_MODEL_STATUS':
      return {
        ...state,
        modelStatus: action.payload
      };
    case 'SET_GENERATING':
      return {
        ...state,
        isGenerating: action.payload
      };
    case 'UPDATE_PROGRESS':
      return {
        ...state,
        progress: { ...state.progress, ...action.payload }
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

export const VinallamaProvider = ({ children }) => {
  const [state, dispatch] = useReducer(vinallamaReducer, initialState);

  const generateResponse = useCallback(async (prompt, context = '') => {
    dispatch({ type: 'SET_GENERATING', payload: true });
    dispatch({ type: 'SET_MODEL_STATUS', payload: 'loading' });
    dispatch({ type: 'RESET_PROGRESS' });

    try {
      // Simulate generation process
      const steps = [
        { percentage: 20, status: 'Đang xử lý prompt...', currentStep: 'processing' },
        { percentage: 50, status: 'Đang tạo phản hồi...', currentStep: 'generating' },
        { percentage: 80, status: 'Đang hoàn thiện...', currentStep: 'finalizing' },
        { percentage: 100, status: 'Hoàn thành', currentStep: 'completed' }
      ];

      for (const step of steps) {
        dispatch({ type: 'UPDATE_PROGRESS', payload: step });
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      // Simulate response generation
      const response = `Đây là phản hồi từ Vinallama cho prompt: "${prompt}"`;
      
      dispatch({ type: 'SET_MODEL_STATUS', payload: 'ready' });
      return response;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      dispatch({ type: 'SET_MODEL_STATUS', payload: 'error' });
      throw error;
    } finally {
      dispatch({ type: 'SET_GENERATING', payload: false });
    }
  }, []);

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
    generateResponse,
    updateConfig,
    checkModelStatus
  };

  return (
    <VinallamaContext.Provider value={value}>
      {children}
    </VinallamaContext.Provider>
  );
};

export const useVinallama = () => {
  const context = useContext(VinallamaContext);
  if (!context) {
    throw new Error('useVinallama must be used within a VinallamaProvider');
  }
  return context;
};
