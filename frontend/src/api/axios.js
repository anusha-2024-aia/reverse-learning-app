import axios from 'axios';

const API_BASE_URL = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api`;

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Request interceptor to add the JWT token to requests
api.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to format API error messages gracefully
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const data = error.response.data;
      if (error.response.status === 429) {
        const retryAfter = error.response.headers && (error.response.headers['retry-after'] || error.response.headers['Retry-After']);
        const msg = (data && (data.message || data.detail)) || 'Too many requests. Please wait a moment and try again.';
        error.message = retryAfter ? `Too many requests. Please wait ${retryAfter} seconds before trying again.` : msg;
      } else if (data) {
        const msg = data.message || data.detail;
        if (msg && typeof msg === 'string') {
          error.message = msg;
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;