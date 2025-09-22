import { useState, useCallback, useEffect } from 'react';
import { useE5Embedding } from './useE5Embedding';
import { useRAG } from './useRAG';

export const useVectorSearch = () => {
  const e5Embedding = useE5Embedding();
  const rag = useRAG();
  
  const [searchHistory, setSearchHistory] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);

  const performVectorSearch = useCallback(async (query, options = {}) => {
    const {
      topK = 5,
      similarityThreshold = 0.7,
      includeMetadata = true
    } = options;

    setIsSearching(true);

    try {
      // Add to search history
      const searchEntry = {
        id: Date.now(),
        query,
        timestamp: new Date().toISOString(),
        options
      };
      setSearchHistory(prev => [searchEntry, ...prev.slice(0, 49)]); // Keep last 50 searches

      // Perform vector search
      const results = await e5Embedding.searchSimilar(query, topK);
      
      // Filter by similarity threshold
      const filteredResults = results.filter(result => 
        result.similarity >= similarityThreshold
      );

      // Add metadata if requested
      const enrichedResults = includeMetadata ? 
        filteredResults.map(result => ({
          ...result,
          metadata: {
            ...result.metadata,
            searchTimestamp: new Date().toISOString(),
            query,
            similarityThreshold
          }
        })) : filteredResults;

      setSearchResults(enrichedResults);
      return enrichedResults;
    } catch (error) {
      console.error('Vector search error:', error);
      throw error;
    } finally {
      setIsSearching(false);
    }
  }, [e5Embedding]);

  const searchWithRAG = useCallback(async (query, options = {}) => {
    if (!rag.isRAGEnabled) {
      throw new Error('RAG is not enabled');
    }

    setIsSearching(true);

    try {
      // Use RAG pipeline for search
      const result = await rag.processQuery(query);
      
      const searchEntry = {
        id: Date.now(),
        query,
        timestamp: new Date().toISOString(),
        type: 'rag',
        options
      };
      setSearchHistory(prev => [searchEntry, ...prev.slice(0, 49)]);

      setSearchResults(result.sources || []);
      return result;
    } catch (error) {
      console.error('RAG search error:', error);
      throw error;
    } finally {
      setIsSearching(false);
    }
  }, [rag]);

  const clearSearchHistory = useCallback(() => {
    setSearchHistory([]);
  }, []);

  const clearSearchResults = useCallback(() => {
    setSearchResults([]);
  }, []);

  const getSearchStats = useCallback(() => {
    return {
      totalSearches: searchHistory.length,
      recentSearches: searchHistory.slice(0, 10),
      currentResults: searchResults.length,
      isSearching
    };
  }, [searchHistory, searchResults, isSearching]);

  const exportSearchHistory = useCallback(() => {
    const dataStr = JSON.stringify(searchHistory, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `vector-search-history-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, [searchHistory]);

  const getSimilarityDistribution = useCallback(() => {
    if (searchResults.length === 0) return null;

    const similarities = searchResults.map(result => result.similarity);
    const stats = {
      min: Math.min(...similarities),
      max: Math.max(...similarities),
      avg: similarities.reduce((a, b) => a + b, 0) / similarities.length,
      median: similarities.sort((a, b) => a - b)[Math.floor(similarities.length / 2)]
    };

    return stats;
  }, [searchResults]);

  return {
    performVectorSearch,
    searchWithRAG,
    clearSearchHistory,
    clearSearchResults,
    getSearchStats,
    exportSearchHistory,
    getSimilarityDistribution,
    searchHistory,
    searchResults,
    isSearching
  };
};
