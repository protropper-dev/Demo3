class VectorService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.endpoints = {
      search: '/api/vector/search',
      index: '/api/vector/index',
      similarity: '/api/vector/similarity',
      cluster: '/api/vector/cluster'
    };
  }

  async searchVectors(query, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.search}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          ...options
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Vector search error:', error);
      throw error;
    }
  }

  async calculateSimilarity(vector1, vector2) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.similarity}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          vector1,
          vector2
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Similarity calculation error:', error);
      throw error;
    }
  }

  async addVectors(vectors, metadata = []) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.index}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          vectors,
          metadata
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Add vectors error:', error);
      throw error;
    }
  }

  async removeVectors(ids) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.index}`, {
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
      console.error('Remove vectors error:', error);
      throw error;
    }
  }

  async updateVectors(vectors, metadata = []) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.index}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          vectors,
          metadata
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Update vectors error:', error);
      throw error;
    }
  }

  async getVectorById(id) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.index}/${id}`, {
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
      console.error('Get vector by ID error:', error);
      throw error;
    }
  }

  async getIndexStats() {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.index}/stats`, {
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

  async clusterVectors(options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.cluster}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(options)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Cluster vectors error:', error);
      throw error;
    }
  }

  async getClusters() {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.cluster}`, {
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
      console.error('Get clusters error:', error);
      throw error;
    }
  }

  async clearIndex() {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.index}/clear`, {
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
      const response = await fetch(`${this.baseURL}${this.endpoints.index}/export`, {
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
      const response = await fetch(`${this.baseURL}${this.endpoints.index}/import`, {
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
      const response = await fetch(`${this.baseURL}/api/vector/health`, {
        method: 'GET'
      });

      return response.ok;
    } catch (error) {
      console.error('Vector service health check error:', error);
      return false;
    }
  }
}

export default new VectorService();
