import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      return Promise.reject({
        status: error.response.status,
        message: error.response.data?.detail || error.response.data?.message || 'Server error occurred',
        data: error.response.data,
      });
    } else if (error.request) {
      return Promise.reject({
        status: 0,
        message: `Backend unavailable. Please make sure the ForgeIQ Python API is running on: ${API_BASE_URL.replace('/api', '')}`,
        data: null,
      });
    } else {
      return Promise.reject({
        status: -1,
        message: error.message || 'An unexpected error occurred',
        data: null,
      });
    }
  }
);

// Individual Service API Functions
export const getHealth = () => api.get('/health');
export const runPipeline = () => api.post('/pipeline/run');
export const runPipelineWithCSV = (formData) => api.post('/pipeline/run', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
export const previewCSV = (formData) => api.post('/pipeline/preview', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
export const getPipelineStatus = () => api.get('/pipeline/status');
export const getProducts = (params) => api.get('/products', { params });
export const getProduct = (id) => api.get(`/products/${id}`);
export const getReviewProducts = (params) => api.get('/products/review', { params });
export const getQAReviews = (params) => api.get('/qa/reviews', { params });
export const getMetrics = () => api.get('/metrics');
export const getQASummary = () => api.get('/qa/summary');
export const getPipelineResults = () => api.get('/pipeline/results');

export const getClassification = () => api.get('/classification');
export const getAttributes = () => api.get('/attributes');
export const getNormalization = () => api.get('/normalization');
export const getDescriptions = () => api.get('/descriptions');
export const getEnrichment = () => api.get('/enrichment');

export const approveReview = (id) => api.post(`/reviews/${id}/approve`);
export const rejectReview = (id) => api.post(`/reviews/${id}/reject`);

export const downloadResults = async (format = 'csv') => {
  const url = `${API_BASE_URL}/pipeline/export?format=${format}`;
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `forgeiq_export.${format}`);
  document.body.appendChild(link);
  link.click();
  link.parentNode.removeChild(link);
  return true;
};

export default api;
