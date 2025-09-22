class ModelManager {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.endpoints = {
      models: '/api/models',
      status: '/api/models/status',
      load: '/api/models/load',
      unload: '/api/models/unload',
      config: '/api/models/config'
    };
  }

  async getAvailableModels() {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.models}`, {
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
      console.error('Get available models error:', error);
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

  async loadModel(modelType, modelPath, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.load}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          modelType,
          modelPath,
          ...options
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Load model error:', error);
      throw error;
    }
  }

  async unloadModel(modelType) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.unload}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ modelType })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Unload model error:', error);
      throw error;
    }
  }

  async updateModelConfig(modelType, config) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.config}/${modelType}`, {
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
      console.error('Update model config error:', error);
      throw error;
    }
  }

  async getModelConfig(modelType) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.config}/${modelType}`, {
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
      console.error('Get model config error:', error);
      throw error;
    }
  }

  async getModelInfo(modelType) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.models}/${modelType}`, {
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
      console.error('Get model info error:', error);
      throw error;
    }
  }

  async getModelMetrics(modelType) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.models}/${modelType}/metrics`, {
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
      console.error('Get model metrics error:', error);
      throw error;
    }
  }

  async restartModel(modelType) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.models}/${modelType}/restart`, {
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
      console.error('Restart model error:', error);
      throw error;
    }
  }

  async getSystemResources() {
    try {
      const response = await fetch(`${this.baseURL}/api/system/resources`, {
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
      console.error('Get system resources error:', error);
      throw error;
    }
  }

  async getModelLogs(modelType, lines = 100) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.models}/${modelType}/logs?lines=${lines}`, {
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
      console.error('Get model logs error:', error);
      throw error;
    }
  }

  async downloadModel(modelType, modelPath) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.models}/download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ modelType, modelPath })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Download model error:', error);
      throw error;
    }
  }

  // Health check for all models
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/api/models/health`, {
        method: 'GET'
      });

      return response.ok;
    } catch (error) {
      console.error('Model manager health check error:', error);
      return false;
    }
  }

  // Get overall system status
  async getSystemStatus() {
    try {
      const response = await fetch(`${this.baseURL}/api/system/status`, {
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
      console.error('Get system status error:', error);
      throw error;
    }
  }
}

export default new ModelManager();
