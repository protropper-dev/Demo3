class DocumentService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.endpoints = {
      upload: '/api/documents/upload',
      process: '/api/documents/process',
      list: '/api/documents',
      delete: '/api/documents',
      extract: '/api/documents/extract',
      chunk: '/api/documents/chunk'
    };
  }

  async uploadDocument(file, options = {}) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('options', JSON.stringify(options));

      const response = await fetch(`${this.baseURL}${this.endpoints.upload}`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Document upload error:', error);
      throw error;
    }
  }

  async processDocument(documentId, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.process}/${documentId}`, {
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
      console.error('Document processing error:', error);
      throw error;
    }
  }

  async getDocuments(options = {}) {
    try {
      const queryParams = new URLSearchParams(options);
      const response = await fetch(`${this.baseURL}${this.endpoints.list}?${queryParams}`, {
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

  async getDocument(documentId) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.list}/${documentId}`, {
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
      console.error('Get document error:', error);
      throw error;
    }
  }

  async deleteDocument(documentId) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.delete}/${documentId}`, {
        method: 'DELETE',
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
      console.error('Delete document error:', error);
      throw error;
    }
  }

  async extractText(documentId, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.extract}/${documentId}`, {
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
      console.error('Extract text error:', error);
      throw error;
    }
  }

  async chunkDocument(documentId, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.chunk}/${documentId}`, {
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
      console.error('Chunk document error:', error);
      throw error;
    }
  }

  async getDocumentChunks(documentId) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.chunk}/${documentId}`, {
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
      console.error('Get document chunks error:', error);
      throw error;
    }
  }

  async updateDocumentMetadata(documentId, metadata) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.list}/${documentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ metadata })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Update document metadata error:', error);
      throw error;
    }
  }

  async getDocumentStatus(documentId) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.list}/${documentId}/status`, {
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
      console.error('Get document status error:', error);
      throw error;
    }
  }

  async downloadDocument(documentId) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.list}/${documentId}/download`, {
        method: 'GET'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      return blob;
    } catch (error) {
      console.error('Download document error:', error);
      throw error;
    }
  }

  async getDocumentStats() {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.list}/stats`, {
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
      console.error('Get document stats error:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/api/documents/health`, {
        method: 'GET'
      });

      return response.ok;
    } catch (error) {
      console.error('Document service health check error:', error);
      return false;
    }
  }
}

export default new DocumentService();
