/**
 * MemoryOS Frontend — Auth Store (Zustand)
 */

import { create } from 'zustand';
import { authApi } from '../api/client';

interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, name: string, password: string) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('memoryos_token'),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await authApi.login({ email, password });
      localStorage.setItem('memoryos_token', data.access_token);
      set({ user: data.user, token: data.access_token, isLoading: false });
    } catch (err: any) {
      const message = err.response?.data?.detail?.error?.message || 'Login failed';
      set({ error: message, isLoading: false });
    }
  },

  register: async (email, name, password) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await authApi.register({ email, name, password });
      localStorage.setItem('memoryos_token', data.access_token);
      set({ user: data.user, token: data.access_token, isLoading: false });
    } catch (err: any) {
      const message = err.response?.data?.detail?.error?.message || 'Registration failed';
      set({ error: message, isLoading: false });
    }
  },

  logout: () => {
    localStorage.removeItem('memoryos_token');
    set({ user: null, token: null });
  },

  loadUser: async () => {
    const token = localStorage.getItem('memoryos_token');
    if (!token) return;
    set({ isLoading: true });
    try {
      const { data } = await authApi.me();
      set({ user: data, isLoading: false });
    } catch {
      localStorage.removeItem('memoryos_token');
      set({ user: null, token: null, isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
