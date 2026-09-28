/**
 * ============================================================================
 * VaporStore API Client Module
 * Configured Axios instance with baseURL auto-discovery, interceptors,
 * and structured endpoints for Categories and Games resources.
 * ============================================================================
 */

// Determine API Base URL automatically based on runtime origin and path
const getBaseApiUrl = () => {
  // If running via FastAPI static files mounting (/client/), use relative path
  if (window.location.pathname.startsWith('/client')) {
    return '/api/v1';
  }
  // If running via local static server or file, use default backend port
  return 'http://127.0.0.1:8000/api/v1';
};

// Create configured Axios instance
const apiClient = axios.create({
  baseURL: getBaseApiUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Response interceptor to normalize FastAPI error responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let formattedMessage = 'An unexpected server error occurred.';

    if (error.response) {
      const data = error.response.data;
      if (data && data.detail) {
        if (typeof data.detail === 'string') {
          formattedMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          // Format Pydantic validation errors (array of objects)
          formattedMessage = data.detail
            .map((err) => `${err.loc ? err.loc.join('.') : 'field'}: ${err.msg}`)
            .join(' | ');
        }
      } else if (error.response.status === 404) {
        formattedMessage = 'Requested resource not found (404).';
      } else if (error.response.status === 500) {
        formattedMessage = 'Internal Server Error (500). Please check backend logs.';
      }
    } else if (error.request) {
      formattedMessage = 'Cannot connect to backend API server. Is FastAPI running on port 8000?';
    } else {
      formattedMessage = error.message;
    }

    // Attach human-readable error message to error object
    error.userMessage = formattedMessage;
    return Promise.reject(error);
  }
);

// Categories API Service
export const categoriesApi = {
  /**
   * Fetch all categories with associated game count
   * @returns {Promise<Array>} List of categories
   */
  async getAll() {
    const res = await apiClient.get('/categories/');
    return res.data;
  },

  /**
   * Fetch single category by ID
   * @param {number} id - Category ID
   * @returns {Promise<Object>} Category details
   */
  async getById(id) {
    const res = await apiClient.get(`/categories/${id}`);
    return res.data;
  },

  /**
   * Create a new category
   * @param {Object} data - Category creation payload { name, description }
   * @returns {Promise<Object>} Created category
   */
  async create(data) {
    const res = await apiClient.post('/categories/', data);
    return res.data;
  },

  /**
   * Update an existing category
   * @param {number} id - Category ID
   * @param {Object} data - Updated category fields
   * @returns {Promise<Object>} Updated category
   */
  async update(id, data) {
    const res = await apiClient.put(`/categories/${id}`, data);
    return res.data;
  },

  /**
   * Delete a category by ID (triggers cascade delete of its games)
   * @param {number} id - Category ID
   * @returns {Promise<void>}
   */
  async delete(id) {
    await apiClient.delete(`/categories/${id}`);
  }
};

// Games API Service
export const gamesApi = {
  /**
   * Fetch paginated and filtered list of games
   * @param {Object} params - Query filters { page, page_size, category_id, search, min_rating, max_price, is_active }
   * @returns {Promise<Object>} Paginated games envelope { total, page, page_size, total_pages, items }
   */
  async getAll(params = {}) {
    // Filter out undefined, null, or empty string values
    const cleanParams = {};
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== '') {
        cleanParams[key] = value;
      }
    }
    const res = await apiClient.get('/games/', { params: cleanParams });
    return res.data;
  },

  /**
   * Fetch single game by ID
   * @param {number} id - Game ID
   * @returns {Promise<Object>} Game details with relational category
   */
  async getById(id) {
    const res = await apiClient.get(`/games/${id}`);
    return res.data;
  },

  /**
   * Create a new game
   * @param {Object} data - Game creation payload
   * @returns {Promise<Object>} Created game with category details
   */
  async create(data) {
    const res = await apiClient.post('/games/', data);
    return res.data;
  },

  /**
   * Update an existing game
   * @param {number} id - Game ID
   * @param {Object} data - Updated game fields
   * @returns {Promise<Object>} Updated game
   */
  async update(id, data) {
    const res = await apiClient.put(`/games/${id}`, data);
    return res.data;
  },

  /**
   * Delete a game by ID
   * @param {number} id - Game ID
   * @returns {Promise<void>}
   */
  async delete(id) {
    await apiClient.delete(`/games/${id}`);
  }
};

// System Health API Service
export const healthApi = {
  /**
   * Check backend connectivity and database health
   * @returns {Promise<Object>} Health status
   */
  async check() {
    const res = await apiClient.get('/health');
    return res.data;
  },

  /**
   * Get root API metadata
   * @returns {Promise<Object>} Root info
   */
  async getRoot() {
    // Root endpoint is at origin root /
    const rootUrl = getBaseApiUrl().replace('/api/v1', '');
    const res = await axios.get(rootUrl || '/');
    return res.data;
  }
};

export default apiClient;
