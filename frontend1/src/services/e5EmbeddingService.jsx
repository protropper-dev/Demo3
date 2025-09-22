class E5EmbeddingService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.endpoints = {
      embed: '/api/e5/embed',
      batchEmbed: '/api/e5/batch-embed',
      search: '/api/e5/search',
      status: '/api/e5/status',
      config: '/api/e5/config'
    };
  }

  async generateEmbedding(text) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.embed}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('E5 embedding generation error:', error);
      throw error;
    }
  }

  async generateEmbeddings(texts) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.batchEmbed}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ texts })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('E5 batch embedding generation error:', error);
      throw error;
    }
  }

  async searchSimilar(query, topK = 5, threshold = 0.7) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.search}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          topK,
          threshold
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('E5 similarity search error:', error);
      throw error;
    }
  }

  async addToIndex(embeddings, metadata = []) {
    try {
      const response = await fetch(`${this.baseURL}/api/e5/index`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          embeddings,
          metadata
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Add to index error:', error);
      throw error;
    }
  }

  async removeFromIndex(ids) {
    try {
      const response = await fetch(`${this.baseURL}/api/e5/index`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Remove from index error:', error);
      throw error;
    }
  }

  async getIndexStats() {
    try {
      const response = await fetch(`${this.baseURL}/api/e5/index/stats`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Get index stats error:', error);
      throw error;
    }
  }

  async getModelStatus() {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.status}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Get model status error:', error);
      throw error;
    }
  }

  async updateConfig(config) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.config}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Update config error:', error);
      throw error;
    }
  }

  async getConfig() {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.config}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Get config error:', error);
      throw error;
    }
  }

  async clearIndex() {
    try {
      const response = await fetch(`${this.baseURL}/api/e5/index/clear`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Clear index error:', error);
      throw error;
    }
  }

  async exportIndex() {
    try {
      const response = await fetch(`${this.baseURL}/api/e5/index/export`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Export index error:', error);
      throw error;
    }
  }

  async importIndex(indexData) {
    try {
      const response = await fetch(`${this.baseURL}/api/e5/index/import`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(indexData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Import index error:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/api/e5/health`, {
        method: 'GET'
      });

      return response.ok;
    } catch (error) {
      console.error('E5 embedding health check error:', error);
      return false;
    }
  }
}

export default new E5EmbeddingService();
