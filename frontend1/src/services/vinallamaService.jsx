class VinallamaService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.endpoints = {
      generate: '/api/vinallama/generate',
      status: '/api/vinallama/status',
      config: '/api/vinallama/config',
      models: '/api/vinallama/models'
    };
  }

  async generateResponse(prompt, context = '', options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.generate}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          context,
          ...options
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Vinallama generation error:', error);
      throw error;
    }
  }

  async generateStreamResponse(prompt, context = '', options = {}, onChunk) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.generate}/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          context,
          stream: true,
          ...options
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.content) {
                fullResponse += data.content;
                onChunk(data.content);
              }
              if (data.done) {
                return fullResponse;
              }
            } catch (e) {
              // Ignore parsing errors for incomplete chunks
            }
          }
        }
      }

      return fullResponse;
    } catch (error) {
      console.error('Vinallama stream generation error:', error);
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

  async loadModel(modelPath) {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.models}/load`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ modelPath })
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

  async unloadModel() {
    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.models}/unload`, {
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
      console.error('Unload model error:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/api/vinallama/health`, {
        method: 'GET'
      });

      return response.ok;
    } catch (error) {
      console.error('Vinallama health check error:', error);
      return false;
    }
  }
}

export default new VinallamaService();
