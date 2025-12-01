import axios from 'axios';
import { API_CONFIG } from '../config/api.config';

const API_CONFIG_AI = {
  baseURL: process.env.REACT_APP_AI_API_URL || 'http://138.68.24.154:4002/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.REACT_APP_AI_API_KEY}`
  }
};

const aiService = {
  async analyzeMetrics(metrics) {
    try {
      const response = await axios.post(`${API_CONFIG_AI.baseURL}/outcomes`, {
        metrics,
        context: 'endocannabinoid_system'
      });
      return response.data;
    } catch (error) {
      console.error('Error analyzing metrics:', error);
      return null;
    }
  },

  async searchLiterature(query) {
    try {
      const response = await axios.post(`${API_CONFIG_AI.baseURL}/outcomes`, {
        query,
        filters: {
          dateRange: 'last_5_years',
          relevance: 'high',
          sourceTypes: ['peer_reviewed', 'clinical_trials']
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error searching literature:', error);
      return [];
    }
  },

  async generateExplanation(metric, value) {
    try {
      const response = await axios.post(`${API_CONFIG_AI.baseURL}/outcomes`, {
        metric,
        value,
        context: 'endocannabinoid_system'
      });
      return response.data;
    } catch (error) {
      console.error('Error generating explanation:', error);
      return null;
    }
  },

  async predictTrends(historicalData) {
    try {
      const response = await axios.post(`${API_CONFIG_AI.baseURL}/predictions`, {
        historicalData,
        predictionPeriod: '30_days'
      });
      return response.data;
    } catch (error) {
      console.error('Error predicting trends:', error);
      return null;
    }
  }
};

export const claudeAIService = {
  async getExplanation(prompt) {
    try {
      const response = await axios.post(
        API_CONFIG.CLAUDE_AI.BASE_URL,
        {
          model: 'claude-2',
          max_tokens: 512,
          messages: [{ role: 'user', content: prompt }]
        },
        {
          headers: {
            'x-api-key': API_CONFIG.CLAUDE_AI.API_KEY,
            'content-type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Claude AI error:', error);
      return { error: 'Failed to get explanation from Claude AI.' };
    }
  }
};

export const consensusAIService = {
  async searchLiterature(query) {
    try {
      const response = await axios.get(
        API_CONFIG.CONSENSUS_AI.BASE_URL,
        {
          params: { q: query },
          headers: {
            'x-api-key': API_CONFIG.CONSENSUS_AI.API_KEY
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Consensus AI error:', error);
      return { error: 'Failed to search literature with Consensus AI.' };
    }
  }
};

export default aiService; 