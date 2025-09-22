import { useState, useCallback, useEffect } from 'react';
import { useRAG as useRAGContext } from '../context/RAGContext';
import { useE5Embedding } from '../context/E5EmbeddingContext';
import { useVinallama } from '../context/VinallamaContext';

export const useRAG = () => {
  const ragContext = useRAGContext();
  const e5Embedding = useE5Embedding();
  const vinallama = useVinallama();

  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState('idle');

  const processQuery = useCallback(async (query) => {
    if (!ragContext.isRAGEnabled) {
      // If RAG is disabled, just use Vinallama directly
      return await vinallama.generateResponse(query);
    }

    setIsProcessing(true);
    setCurrentStep('searching');

    try {
      // Step 1: Search for relevant documents
      const searchResults = await ragContext.searchDocuments(query);
      setCurrentStep('embedding');

      // Step 2: Generate embeddings for query
      const queryEmbeddings = await e5Embedding.generateEmbeddings([query]);
      setCurrentStep('retrieving');

      // Step 3: Find similar chunks
      const similarChunks = await e5Embedding.searchSimilar(query, ragContext.config.maxResults);
      setCurrentStep('generating');

      // Step 4: Generate response with context
      const context = similarChunks.map(chunk => chunk.text).join('\n\n');
      const response = await vinallama.generateResponse(query, context);

      setCurrentStep('completed');
      return {
        response,
        sources: similarChunks.map(chunk => ({
          title: chunk.metadata?.source || 'Unknown',
          excerpt: chunk.text,
          score: chunk.similarity,
          type: 'text'
        }))
      };
    } catch (error) {
      setCurrentStep('error');
      throw error;
    } finally {
      setIsProcessing(false);
    }
  }, [ragContext, e5Embedding, vinallama]);

  const processDocument = useCallback(async (document) => {
    setIsProcessing(true);
    setCurrentStep('processing');

    try {
      // Step 1: Extract text from document
      setCurrentStep('extracting');
      const textChunks = await extractTextChunks(document);

      // Step 2: Generate embeddings
      setCurrentStep('embedding');
      const embeddings = await e5Embedding.generateEmbeddings(textChunks);

      // Step 3: Store in knowledge base
      setCurrentStep('storing');
      await storeEmbeddings(embeddings, document);

      setCurrentStep('completed');
      return embeddings;
    } catch (error) {
      setCurrentStep('error');
      throw error;
    } finally {
      setIsProcessing(false);
    }
  }, [e5Embedding]);

  const extractTextChunks = async (document) => {
    // Mock text extraction
    const chunks = [
      'Chunk 1: Nội dung đầu tiên của tài liệu...',
      'Chunk 2: Nội dung thứ hai của tài liệu...',
      'Chunk 3: Nội dung thứ ba của tài liệu...'
    ];
    return chunks;
  };

  const storeEmbeddings = async (embeddings, document) => {
    // Mock storage
    console.log('Storing embeddings:', embeddings.length, 'for document:', document.name);
  };

  const getProcessingStatus = useCallback(() => {
    return {
      isProcessing,
      currentStep,
      progress: {
        searching: currentStep === 'searching' ? 25 : 0,
        embedding: currentStep === 'embedding' ? 50 : 0,
        retrieving: currentStep === 'retrieving' ? 75 : 0,
        generating: currentStep === 'generating' ? 90 : 0,
        completed: currentStep === 'completed' ? 100 : 0
      }
    };
  }, [isProcessing, currentStep]);

  return {
    ...ragContext,
    processQuery,
    processDocument,
    getProcessingStatus,
    isProcessing,
    currentStep
  };
};
