import React, { createContext, useContext, useReducer, useCallback } from 'react';

const RAGContext = createContext();

const initialState = {
  isRAGEnabled: true,
  documents: [],
  searchResults: [],
  isLoading: false,
  error: null,
  config: {
    maxResults: 5,
    similarityThreshold: 0.7,
    chunkSize: 1000,
    overlapSize: 200
  }
};

const ragReducer = (state, action) => {
  switch (action.type) {
    case 'TOGGLE_RAG':
      return {
        ...state,
        isRAGEnabled: !state.isRAGEnabled
      };
    case 'SET_DOCUMENTS':
      return {
        ...state,
        documents: action.payload
      };
    case 'SET_SEARCH_RESULTS':
      return {
        ...state,
        searchResults: action.payload
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
    case 'UPDATE_CONFIG':
      return {
        ...state,
        config: { ...state.config, ...action.payload }
      };
    default:
      return state;
  }
};

export const RAGProvider = ({ children }) => {
  const [state, dispatch] = useReducer(ragReducer, initialState);

  const toggleRAG = useCallback(() => {
    dispatch({ type: 'TOGGLE_RAG' });
  }, []);

  const searchDocuments = useCallback(async (query) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      // Simulate vector search
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const results = [
        {
          id: 1,
          text: 'Kết quả tìm kiếm 1 cho: ' + query,
          score: 0.95,
          source: 'document1.pdf',
          page: 1
        },
        {
          id: 2,
          text: 'Kết quả tìm kiếm 2 cho: ' + query,
          score: 0.87,
          source: 'document2.pdf',
          page: 3
        }
      ];
      
      dispatch({ type: 'SET_SEARCH_RESULTS', payload: results });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  const addDocument = useCallback((document) => {
    dispatch({ type: 'SET_DOCUMENTS', payload: [...state.documents, document] });
  }, [state.documents]);

  const removeDocument = useCallback((documentId) => {
    const updatedDocuments = state.documents.filter(doc => doc.id !== documentId);
    dispatch({ type: 'SET_DOCUMENTS', payload: updatedDocuments });
  }, [state.documents]);

  const updateConfig = useCallback((newConfig) => {
    dispatch({ type: 'UPDATE_CONFIG', payload: newConfig });
  }, []);

  const value = {
    ...state,
    toggleRAG,
    searchDocuments,
    addDocument,
    removeDocument,
    updateConfig
  };

  return (
    <RAGContext.Provider value={value}>
      {children}
    </RAGContext.Provider>
  );
};

export const useRAG = () => {
  const context = useContext(RAGContext);
  if (!context) {
    throw new Error('useRAG must be used within a RAGProvider');
  }
  return context;
};
