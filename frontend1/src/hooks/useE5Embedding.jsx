import { useState, useCallback, useEffect } from 'react';
import { useE5Embedding as useE5EmbeddingContext } from '../context/E5EmbeddingContext';

export const useE5Embedding = () => {
  const e5EmbeddingContext = useE5EmbeddingContext();
  const [embeddingCache, setEmbeddingCache] = useState(new Map());
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize E5 model
  useEffect(() => {
    const initializeModel = async () => {
      try {
        await e5EmbeddingContext.checkModelStatus();
        setIsInitialized(true);
      } catch (error) {
        console.error('Failed to initialize E5 Embedding:', error);
      }
    };

    initializeModel();
  }, [e5EmbeddingContext]);

  const generateEmbedding = useCallback(async (text) => {
    if (!isInitialized) {
      throw new Error('E5 Embedding model not initialized');
    }

    // Check cache first
    const cacheKey = text.toLowerCase().trim();
    if (embeddingCache.has(cacheKey)) {
      return embeddingCache.get(cacheKey);
    }

    try {
      const embeddings = await e5EmbeddingContext.generateEmbeddings([text]);
      const embedding = embeddings[0];
      
      // Cache the result
      setEmbeddingCache(prev => new Map(prev).set(cacheKey, embedding));
      
      return embedding;
    } catch (error) {
      console.error('Error generating embedding:', error);
      throw error;
    }
  }, [e5EmbeddingContext, isInitialized, embeddingCache]);

  const generateEmbeddings = useCallback(async (texts) => {
    if (!isInitialized) {
      throw new Error('E5 Embedding model not initialized');
    }

    try {
      return await e5EmbeddingContext.generateEmbeddings(texts);
    } catch (error) {
      console.error('Error generating embeddings:', error);
      throw error;
    }
  }, [e5EmbeddingContext, isInitialized]);

  const searchSimilar = useCallback(async (query, topK = 5) => {
    if (!isInitialized) {
      throw new Error('E5 Embedding model not initialized');
    }

    try {
      return await e5EmbeddingContext.searchSimilar(query, topK);
    } catch (error) {
      console.error('Error searching similar:', error);
      throw error;
    }
  }, [e5EmbeddingContext, isInitialized]);

  const calculateSimilarity = useCallback((embedding1, embedding2) => {
    if (embedding1.length !== embedding2.length) {
      throw new Error('Embeddings must have the same dimension');
    }

    // Calculate cosine similarity
    let dotProduct = 0;
    let norm1 = 0;
    let norm2 = 0;

    for (let i = 0; i < embedding1.length; i++) {
      dotProduct += embedding1[i] * embedding2[i];
      norm1 += embedding1[i] * embedding1[i];
      norm2 += embedding2[i] * embedding2[i];
    }

    norm1 = Math.sqrt(norm1);
    norm2 = Math.sqrt(norm2);

    if (norm1 === 0 || norm2 === 0) {
      return 0;
    }

    return dotProduct / (norm1 * norm2);
  }, []);

  const clearCache = useCallback(() => {
    setEmbeddingCache(new Map());
  }, []);

  const getCacheStats = useCallback(() => {
    return {
      size: embeddingCache.size,
      keys: Array.from(embeddingCache.keys())
    };
  }, [embeddingCache]);

  const updateModelConfig = useCallback((config) => {
    e5EmbeddingContext.updateConfig(config);
  }, [e5EmbeddingContext]);

  const getModelInfo = useCallback(() => {
    return {
      status: e5EmbeddingContext.modelStatus,
      isProcessing: e5EmbeddingContext.isProcessing,
      progress: e5EmbeddingContext.progress,
      config: e5EmbeddingContext.config,
      isInitialized,
      cacheStats: getCacheStats()
    };
  }, [e5EmbeddingContext, isInitialized, getCacheStats]);

  return {
    ...e5EmbeddingContext,
    generateEmbedding,
    generateEmbeddings,
    searchSimilar,
    calculateSimilarity,
    clearCache,
    getCacheStats,
    updateModelConfig,
    getModelInfo,
    isInitialized
  };
};
