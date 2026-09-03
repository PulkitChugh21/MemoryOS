/**
 * MemoryOS Frontend — API Client
 * Axios instance configured for the MemoryOS backend.
 * Timeout set to 60s for Railway cold starts + Gemini API calls.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000, // 60s — Railway cold starts + Gemini can take 15-30s
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('memoryos_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('memoryos_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// --- Auth API ---
export const authApi = {
  register: (data: { email: string; name: string; password: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
  updateProfile: (data: { name?: string; email?: string }) =>
    api.patch('/auth/me', data),
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
  deleteAccount: () => api.delete('/auth/me'),
};

// --- Projects API ---
export const projectsApi = {
  list: () => api.get('/projects'),
  get: (id: string) => api.get(`/projects/${id}`),
  create: (data: { name: string; description?: string; tech_stack?: string[]; project_type?: string }) =>
    api.post('/projects', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/projects/${id}`, data),
  delete: (id: string) => api.delete(`/projects/${id}`),
};

// --- Chat API ---
export const chatApi = {
  send: (projectId: string, data: { message: string; session_id?: string }) =>
    api.post(`/chat/${projectId}`, data),
  streamUrl: (projectId: string) => `${API_BASE}/chat/${projectId}/stream`,
};

// --- Memory API ---
export const memoryApi = {
  episodes: (projectId: string, params?: { limit?: number; session_id?: string }) =>
    api.get(`/memory/${projectId}/episodes`, { params }),
  sessions: (projectId: string) =>
    api.get(`/memory/${projectId}/sessions`),
  sessionDetail: (projectId: string, sessionId: string) =>
    api.get(`/memory/${projectId}/sessions/${sessionId}`),
  stats: (projectId: string) =>
    api.get(`/memory/${projectId}/stats`),
};

export default api;
