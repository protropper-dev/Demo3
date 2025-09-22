import React, { createContext, useContext, useReducer, useCallback } from 'react';

const KnowledgeBaseContext = createContext();

const initialState = {
  documents: [],
  isUploading: false,
  isProcessing: false,
  uploadProgress: 0,
  processingProgress: 0,
  error: null,
  searchResults: [],
  isSearching: false
};

const knowledgeBaseReducer = (state, action) => {
  switch (action.type) {
    case 'SET_DOCUMENTS':
      return {
        ...state,
        documents: action.payload
      };
    case 'ADD_DOCUMENT':
      return {
        ...state,
        documents: [...state.documents, action.payload]
      };
    case 'REMOVE_DOCUMENT':
      return {
        ...state,
        documents: state.documents.filter(doc => doc.id !== action.payload)
      };
    case 'SET_UPLOADING':
      return {
        ...state,
        isUploading: action.payload
      };
    case 'SET_PROCESSING':
      return {
        ...state,
        isProcessing: action.payload
      };
    case 'SET_UPLOAD_PROGRESS':
      return {
        ...state,
        uploadProgress: action.payload
      };
    case 'SET_PROCESSING_PROGRESS':
      return {
        ...state,
        processingProgress: action.payload
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload
      };
    case 'SET_SEARCH_RESULTS':
      return {
        ...state,
        searchResults: action.payload
      };
    case 'SET_SEARCHING':
      return {
        ...state,
        isSearching: action.payload
      };
    default:
      return state;
  }
};

export const KnowledgeBaseProvider = ({ children }) => {
  const [state, dispatch] = useReducer(knowledgeBaseReducer, initialState);

  const uploadDocument = useCallback(async (file) => {
    dispatch({ type: 'SET_UPLOADING', payload: true });
    dispatch({ type: 'SET_UPLOAD_PROGRESS', payload: 0 });

    try {
      // Simulate upload progress
      for (let i = 0; i <= 100; i += 10) {
        dispatch({ type: 'SET_UPLOAD_PROGRESS', payload: i });
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      const document = {
        id: Date.now(),
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'uploaded',
        uploadDate: new Date().toISOString()
      };

      dispatch({ type: 'ADD_DOCUMENT', payload: document });
      return document;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    } finally {
      dispatch({ type: 'SET_UPLOADING', payload: false });
    }
  }, []);

  const processDocument = useCallback(async (documentId) => {
    dispatch({ type: 'SET_PROCESSING', payload: true });
    dispatch({ type: 'SET_PROCESSING_PROGRESS', payload: 0 });

    try {
      // Simulate processing steps
      const steps = [
        { progress: 20, status: 'Đang phân tích tài liệu...' },
        { progress: 40, status: 'Đang tách đoạn văn...' },
        { progress: 60, status: 'Đang tạo embeddings...' },
        { progress: 80, status: 'Đang lưu trữ...' },
        { progress: 100, status: 'Hoàn thành' }
      ];

      for (const step of steps) {
        dispatch({ type: 'SET_PROCESSING_PROGRESS', payload: step.progress });
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      // Update document status
      const updatedDocuments = state.documents.map(doc =>
        doc.id === documentId ? { ...doc, status: 'processed' } : doc
      );
      dispatch({ type: 'SET_DOCUMENTS', payload: updatedDocuments });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    } finally {
      dispatch({ type: 'SET_PROCESSING', payload: false });
    }
  }, [state.documents]);

  const removeDocument = useCallback((documentId) => {
    dispatch({ type: 'REMOVE_DOCUMENT', payload: documentId });
  }, []);

  const searchDocuments = useCallback(async (query) => {
    dispatch({ type: 'SET_SEARCHING', payload: true });

    try {
      // Simulate search
      await new Promise(resolve => setTimeout(resolve, 1000));

      const results = [
        {
          id: 1,
          text: `Kết quả tìm kiếm cho: "${query}"`,
          score: 0.95,
          source: 'document1.pdf',
          page: 1,
          chunk: 1
        },
        {
          id: 2,
          text: `Kết quả khác cho: "${query}"`,
          score: 0.87,
          source: 'document2.pdf',
          page: 3,
          chunk: 2
        }
      ];

      dispatch({ type: 'SET_SEARCH_RESULTS', payload: results });
      return results;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    } finally {
      dispatch({ type: 'SET_SEARCHING', payload: false });
    }
  }, []);

  const clearError = useCallback(() => {
    dispatch({ type: 'SET_ERROR', payload: null });
  }, []);

  const value = {
    ...state,
    uploadDocument,
    processDocument,
    removeDocument,
    searchDocuments,
    clearError
  };

  return (
    <KnowledgeBaseContext.Provider value={value}>
      {children}
    </KnowledgeBaseContext.Provider>
  );
};

export const useKnowledgeBase = () => {
  const context = useContext(KnowledgeBaseContext);
  if (!context) {
    throw new Error('useKnowledgeBase must be used within a KnowledgeBaseProvider');
  }
  return context;
};
