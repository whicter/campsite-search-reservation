import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests automatically
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// API methods
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (email, password) => api.post('/auth/register', { email, password }),
  getMe: () => api.get('/auth/me')
};

export const monitoringAPI = {
  getTasks: (status = null) =>
    api.get('/monitoring/tasks', { params: status ? { status } : {} }),
  getTask: (id) => api.get(`/monitoring/tasks/${id}`),
  createTask: (data) => api.post('/monitoring/tasks', data),
  updateTask: (id, data) => api.patch(`/monitoring/tasks/${id}`, data),
  deleteTask: (id) => api.delete(`/monitoring/tasks/${id}`),
  getTaskStatus: (id) => api.get(`/monitoring/tasks/${id}/status`),
  getNotifications: () => api.get('/monitoring/notifications')
};

export const campsiteAPI = {
  getProviders: () => axios.get(`${API_URL}/api/providers`),
  searchCampgrounds: (provider, search) =>
    axios.get(`${API_URL}/api/campgrounds`, { params: { provider, search } }),
  checkAvailability: (data) => axios.post(`${API_URL}/api/availability`, data),
  searchMultiCampground: (data) => axios.post(`${API_URL}/api/availability/search`, data)
};

// Admin API
export const adminAPI = {
  getAllUsers: () => api.get('/admin/users'),
  getAllTasks: () => api.get('/admin/tasks'),
  getSystemStats: () => api.get('/admin/stats'),
  getQueueStatus: () => api.get('/admin/queue/status')
};
