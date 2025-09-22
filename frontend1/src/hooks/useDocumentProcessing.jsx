import { useState, useCallback, useEffect } from 'react';
import { useKnowledgeBase } from '../context/KnowledgeBaseContext';
import { useE5Embedding } from './useE5Embedding';

export const useDocumentProcessing = () => {
  const knowledgeBase = useKnowledgeBase();
  const e5Embedding = useE5Embedding();
  
  const [processingQueue, setProcessingQueue] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const processDocument = useCallback(async (file) => {
    const documentId = Date.now();
    
    // Add to processing queue
    const document = {
      id: documentId,
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'queued',
      timestamp: new Date().toISOString()
    };

    setProcessingQueue(prev => [...prev, document]);

    try {
      // Upload document
      await knowledgeBase.uploadDocument(file);
      
      // Process document
      await knowledgeBase.processDocument(documentId);
      
      // Generate embeddings
      const textChunks = await extractTextChunks(file);
      const embeddings = await e5Embedding.generateEmbeddings(textChunks);
      
      // Update document status
      setProcessingQueue(prev => 
        prev.map(doc => 
          doc.id === documentId 
            ? { ...doc, status: 'completed', embeddings }
            : doc
        )
      );

      return {
        document,
        embeddings,
        chunks: textChunks
      };
    } catch (error) {
      setProcessingQueue(prev => 
        prev.map(doc => 
          doc.id === documentId 
            ? { ...doc, status: 'error', error: error.message }
            : doc
        )
      );
      throw error;
    }
  }, [knowledgeBase, e5Embedding]);

  const extractTextChunks = async (file) => {
    // Mock text extraction based on file type
    const chunks = [];
    
    if (file.type === 'text/plain') {
      const text = await file.text();
      chunks.push(...splitTextIntoChunks(text));
    } else if (file.type === 'application/pdf') {
      // Mock PDF processing
      chunks.push(
        'PDF Chunk 1: Nội dung từ trang 1...',
        'PDF Chunk 2: Nội dung từ trang 2...',
        'PDF Chunk 3: Nội dung từ trang 3...'
      );
    } else if (file.type.includes('word')) {
      // Mock Word document processing
      chunks.push(
        'Word Chunk 1: Nội dung từ tài liệu Word...',
        'Word Chunk 2: Nội dung tiếp theo...'
      );
    }

    return chunks;
  };

  const splitTextIntoChunks = (text, chunkSize = 1000, overlap = 200) => {
    const chunks = [];
    let start = 0;
    
    while (start < text.length) {
      const end = Math.min(start + chunkSize, text.length);
      const chunk = text.slice(start, end);
      chunks.push(chunk);
      start = end - overlap;
    }
    
    return chunks;
  };

  const processMultipleDocuments = useCallback(async (files) => {
    setIsProcessing(true);
    const results = [];

    try {
      for (const file of files) {
        const result = await processDocument(file);
        results.push(result);
      }
      return results;
    } finally {
      setIsProcessing(false);
    }
  }, [processDocument]);

  const clearProcessingQueue = useCallback(() => {
    setProcessingQueue([]);
  }, []);

  const removeFromQueue = useCallback((documentId) => {
    setProcessingQueue(prev => prev.filter(doc => doc.id !== documentId));
  }, []);

  const getProcessingStats = useCallback(() => {
    const stats = {
      total: processingQueue.length,
      queued: processingQueue.filter(doc => doc.status === 'queued').length,
      processing: processingQueue.filter(doc => doc.status === 'processing').length,
      completed: processingQueue.filter(doc => doc.status === 'completed').length,
      error: processingQueue.filter(doc => doc.status === 'error').length
    };

    return stats;
  }, [processingQueue]);

  const retryProcessing = useCallback(async (documentId) => {
    const document = processingQueue.find(doc => doc.id === documentId);
    if (!document) return;

    try {
      await processDocument(document.file);
    } catch (error) {
      console.error('Retry processing failed:', error);
    }
  }, [processingQueue, processDocument]);

  return {
    processDocument,
    processMultipleDocuments,
    clearProcessingQueue,
    removeFromQueue,
    getProcessingStats,
    retryProcessing,
    processingQueue,
    isProcessing
  };
};
