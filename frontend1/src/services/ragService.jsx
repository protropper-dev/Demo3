class RAGService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.endpoints = {
      search: '/api/rag/search',
      process: '/api/rag/process',
      documents: '/api/rag/documents',
      config: '/api/rag/config'
    };
  }

  async searchDocuments(query, options = {}) {
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
      console.error('RAG search error:', error);
      throw error;
    }
  }

  async processDocument(document) {
    try {
      const formData = new FormData();
      formData.append('file', document);
      formData.append('metadata', JSON.stringify({
        name: document.name,
        size: document.size,
        type: document.type
      }));

      const response = await fetch(`${this.baseURL}${this.endpoints.process}`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Document processing error:', error);
      throw error;
    }
  }

  async getDocuments() {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.documents}`, {
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
      console.error('Get documents error:', error);
      throw error;
    }
  }

  async deleteDocument(documentId) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.documents}/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return true;
    } catch (error) {
      console.error('Delete document error:', error);
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

  // Health check
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/api/rag/health`, {
        method: 'GET'
      });

      return response.ok;
    } catch (error) {
      console.error('RAG health check error:', error);
      return false;
    }
  }
}

export default new RAGService();
