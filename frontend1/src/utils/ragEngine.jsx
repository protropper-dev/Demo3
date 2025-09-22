class RAGEngine {
  constructor() {
    this.config = {
      maxResults: 5,
      similarityThreshold: 0.7,
      chunkSize: 1000,
      overlapSize: 200,
      rerankResults: true
    };
  }

  // Main RAG pipeline
  async processQuery(query, context = {}) {
    try {
      // Step 1: Preprocess query
      const processedQuery = this.preprocessQuery(query);
      
      // Step 2: Retrieve relevant documents
      const retrievedDocs = await this.retrieveDocuments(processedQuery, context);
      
      // Step 3: Rerank results if enabled
      const rerankedDocs = this.config.rerankResults ? 
        this.rerankDocuments(retrievedDocs, processedQuery) : 
        retrievedDocs;
      
      // Step 4: Generate context
      const contextText = this.generateContext(rerankedDocs);
      
      // Step 5: Format response
      const response = {
        query: processedQuery,
        context: contextText,
        sources: rerankedDocs,
        metadata: {
          totalResults: retrievedDocs.length,
          filteredResults: rerankedDocs.length,
          processingTime: Date.now()
        }
      };
      
      return response;
    } catch (error) {
      console.error('RAG processing error:', error);
      throw error;
    }
  }

  // Preprocess query for better retrieval
  preprocessQuery(query) {
    return {
      original: query,
      normalized: this.normalizeText(query),
      keywords: this.extractKeywords(query),
      entities: this.extractEntities(query),
      intent: this.detectIntent(query)
    };
  }

  // Normalize text for better matching
  normalizeText(text) {
    return text
      .toLowerCase()
      .trim()
      .replace(/[^\w\s]/g, ' ')
      .replace(/\s+/g, ' ');
  }

  // Extract keywords from query
  extractKeywords(text) {
    const stopWords = new Set([
      'của', 'và', 'với', 'trong', 'cho', 'từ', 'đến', 'về', 'là', 'có', 'được', 'sẽ', 'đã', 'đang'
    ]);
    
    return text
      .toLowerCase()
      .split(/\s+/)
      .filter(word => word.length > 2 && !stopWords.has(word));
  }

  // Extract entities from query
  extractEntities(text) {
    // Simple entity extraction - can be enhanced with NER
    const entities = {
      dates: this.extractDates(text),
      numbers: this.extractNumbers(text),
      properNouns: this.extractProperNouns(text)
    };
    
    return entities;
  }

  // Detect query intent
  detectIntent(text) {
    const questionWords = ['gì', 'nào', 'sao', 'tại sao', 'như thế nào', 'khi nào', 'ở đâu'];
    const commandWords = ['tìm', 'hiển thị', 'cho tôi', 'giải thích', 'so sánh'];
    
    if (questionWords.some(word => text.includes(word))) {
      return 'question';
    } else if (commandWords.some(word => text.includes(word))) {
      return 'command';
    } else {
      return 'statement';
    }
  }

  // Retrieve relevant documents
  async retrieveDocuments(query, context) {
    // Mock retrieval - replace with actual vector search
    const mockDocs = [
      {
        id: 1,
        text: 'Tài liệu liên quan đến: ' + query.original,
        score: 0.95,
        source: 'document1.pdf',
        page: 1,
        chunk: 1
      },
      {
        id: 2,
        text: 'Thông tin khác về: ' + query.original,
        score: 0.87,
        source: 'document2.pdf',
        page: 3,
        chunk: 2
      }
    ];
    
    return mockDocs.filter(doc => doc.score >= this.config.similarityThreshold);
  }

  // Rerank documents based on relevance
  rerankDocuments(documents, query) {
    return documents
      .map(doc => ({
        ...doc,
        relevanceScore: this.calculateRelevance(doc, query)
      }))
      .sort((a, b) => b.relevanceScore - a.relevanceScore);
  }

  // Calculate relevance score
  calculateRelevance(document, query) {
    let score = document.score;
    
    // Boost score for keyword matches
    const keywordMatches = query.keywords.filter(keyword => 
      document.text.toLowerCase().includes(keyword)
    ).length;
    score += keywordMatches * 0.1;
    
    // Boost score for entity matches
    const entityMatches = this.countEntityMatches(document, query.entities);
    score += entityMatches * 0.05;
    
    return Math.min(score, 1.0);
  }

  // Count entity matches
  countEntityMatches(document, entities) {
    let matches = 0;
    
    // Check date matches
    entities.dates.forEach(date => {
      if (document.text.includes(date)) matches++;
    });
    
    // Check number matches
    entities.numbers.forEach(number => {
      if (document.text.includes(number)) matches++;
    });
    
    // Check proper noun matches
    entities.properNouns.forEach(noun => {
      if (document.text.toLowerCase().includes(noun.toLowerCase())) matches++;
    });
    
    return matches;
  }

  // Generate context from retrieved documents
  generateContext(documents) {
    return documents
      .slice(0, this.config.maxResults)
      .map(doc => doc.text)
      .join('\n\n');
  }

  // Extract dates from text
  extractDates(text) {
    const dateRegex = /\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b/g;
    return text.match(dateRegex) || [];
  }

  // Extract numbers from text
  extractNumbers(text) {
    const numberRegex = /\b\d+\b/g;
    return text.match(numberRegex) || [];
  }

  // Extract proper nouns from text
  extractProperNouns(text) {
    // Simple proper noun extraction - can be enhanced with NLP
    const words = text.split(/\s+/);
    return words.filter(word => 
      word.length > 2 && 
      word[0] === word[0].toUpperCase() &&
      /^[A-Za-zÀ-ỹ]+$/.test(word)
    );
  }

  // Update configuration
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
  }

  // Get current configuration
  getConfig() {
    return { ...this.config };
  }

  // Validate configuration
  validateConfig(config) {
    const errors = [];
    
    if (config.maxResults && (config.maxResults < 1 || config.maxResults > 20)) {
      errors.push('maxResults must be between 1 and 20');
    }
    
    if (config.similarityThreshold && (config.similarityThreshold < 0 || config.similarityThreshold > 1)) {
      errors.push('similarityThreshold must be between 0 and 1');
    }
    
    if (config.chunkSize && (config.chunkSize < 100 || config.chunkSize > 5000)) {
      errors.push('chunkSize must be between 100 and 5000');
    }
    
    return errors;
  }
}

export default new RAGEngine();
