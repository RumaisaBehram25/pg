import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const dashboardAPI = {
  getStats: async (period = 'this_week') => {
    const response = await api.get('/dashboard/stats', { params: { period } });
    return response.data;
  },
};

export const claimsAPI = {
  uploadCSV: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/claims/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getClaims: (params) => api.get('/claims', { params }),
  getClaim: (id) => api.get(`/claims/${id}`),
  getJobs: async () => {
    const response = await api.get('/claims/jobs');
    return response;
  },
  getJobStatus: async (jobId) => {
    const response = await api.get(`/claims/jobs/${jobId}`);
    return response;
  },
  getJobErrors: async (jobId) => {
    const response = await api.get(`/claims/jobs/${jobId}/errors`);
    return response;
  },
  getJobClaims: async (jobId, params = {}) => {
    const response = await api.get(`/claims/jobs/${jobId}/claims`, { params });
    return response;
  },
  deleteJob: async (jobId) => {
    const response = await api.delete(`/claims/jobs/${jobId}`);
    return response;
  },
};

export const fraudAPI = {
  getFlagged: async (params = {}) => {
    const response = await api.get('/fraud/flagged', { params });
    return response;
  },
  getFlagDetail: async (id) => {
    const response = await api.get(`/fraud/flagged/${id}`);
    return response;
  },
  reviewFlag: async (id, data) => {
    const response = await api.patch(`/fraud/flagged/${id}/review`, data);
    return response;
  },
  getStats: async (params = {}) => {
    const response = await api.get('/fraud/stats', { params });
    return response;
  },
};

export const rulesAPI = {
  getRules: async (params = {}) => {
    const response = await api.get('/rules', { params });
    return response;
  },
  getRule: async (id) => {
    const response = await api.get(`/rules/${id}`);
    return response;
  },
  createRule: async (data) => {
    const response = await api.post('/rules', data);
    return response;
  },
  updateRule: async (id, data) => {
    const response = await api.put(`/rules/${id}`, data);
    return response;
  },
  toggleRule: async (id, isActive) => {
    const response = await api.patch(`/rules/${id}/toggle`, { is_active: isActive });
    return response;
  },
  deleteRule: async (id) => {
    const response = await api.delete(`/rules/${id}`);
    return response;
  },
  getRuleVersions: async (id) => {
    const response = await api.get(`/rules/${id}/versions`);
    return response;
  },
  bulkUploadRules: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/rules/bulk-upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response;
  },
};

export const usersAPI = {
  getUsers: async () => {
    const response = await api.get('/users');
    return response;
  },
  getCurrentUser: async () => {
    const response = await api.get('/users/me');
    return response;
  },
  getUser: async (id) => {
    const response = await api.get(`/users/${id}`);
    return response;
  },
  createUser: async (data) => {
    const response = await api.post('/users', data);
    return response;
  },
  updateUser: async (id, data) => {
    const response = await api.put(`/users/${id}`, data);
    return response;
  },
  deleteUser: async (id) => {
    const response = await api.delete(`/users/${id}`);
    return response;
  },
};

export const authAPI = {
  login: async (credentials) => {
    const response = await api.post('/auth/login', {
      email: credentials.email,
      password: credentials.password
    });
    return response;
  },
  logout: () => api.post('/auth/logout'),
  register: (data) => api.post('/auth/register', data),
};

export const auditAPI = {
  getLogs: async (params = {}) => {
    const response = await api.get('/audit', { params });
    return response;
  },
  getActionTypes: async () => {
    const response = await api.get('/audit/actions');
    return response;
  },
};

export const runsAPI = {
  getRuns: async (params = {}) => {
    const response = await api.get('/runs', { params });
    return response;
  },
  getRunDetails: async (runId) => {
    const response = await api.get(`/runs/${runId}`);
    return response;
  },
  getRunStats: async (runId) => {
    const response = await api.get(`/runs/${runId}/stats`);
    return response;
  },
};

export default api;

