// Set `REACT_APP_API_BASE_URL` to point the frontend at Lambda / API Gateway.
// Example: https://xxxxx.lambda-url.us-east-1.on.aws/api
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

// Small wrapper around the backend Flask API.
// The UI calls these methods instead of using fetch() directly.
class ApiService {
  /**
   * Get list of all available strategies
   */
  async getStrategies() {
    try {
      const response = await fetch(`${API_BASE_URL}/strategies`);
      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to fetch strategies');
      }

      return data.strategies;
    } catch (error) {
      console.error('Error fetching strategies:', error);
      throw error;
    }
  }

  /**
   * Calculate allocation for a strategy
   * @param {string} strategyId - Strategy identifier
   * @param {number} totalMoney - Total amount to allocate
   * @param {object} parameters - Strategy-specific parameters
   */
  async calculateAllocation(strategyId, totalMoney, parameters = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // Backend expects: strategy_id, total_money, and strategy-specific parameters
        body: JSON.stringify({
          strategy_id: strategyId,
          total_money: totalMoney,
          parameters: parameters,
        }),
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to calculate allocation');
      }

      return data.result;
    } catch (error) {
      console.error('Error calculating allocation:', error);
      throw error;
    }
  }

  /**
   * Get cached monthly walk-forward performance metrics for a strategy
   * @param {string} strategyId - Strategy identifier
   * @param {boolean} refresh - Force recompute before reading cache
   */
  async getPerformance(strategyId, refresh = false) {
    try {
      const qs = new URLSearchParams({
        strategy_id: String(strategyId || ''),
      });
      if (refresh) qs.set('refresh', 'true');

      const response = await fetch(`${API_BASE_URL}/performance?${qs.toString()}`);
      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to fetch performance');
      }

      return data.performance;
    } catch (error) {
      console.error('Error fetching performance:', error);
      throw error;
    }
  }

  /**
   * Get calculation history
   */
  async getHistory() {
    try {
      const response = await fetch(`${API_BASE_URL}/history`);
      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to fetch history');
      }

      return data.history;
    } catch (error) {
      console.error('Error fetching history:', error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}

const apiService = new ApiService();
export default apiService;
