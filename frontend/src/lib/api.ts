import axios from 'axios';
import { UserProfile, JobPreferences, SearchResult } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 600000, // 10 min for long agent operations
});

// Automatically inject the auth token on every request
api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  if (token) {
    config.headers['X-User-Token'] = token;
  }
  return config;
});

export const autoApplyApi = {
  // User
  createUser: (profile: Omit<UserProfile, 'user_id'>) =>
    api.post('/api/users', profile).then((r) => {
      // Persist the token so subsequent requests are authenticated
      if (r.data.token && typeof window !== 'undefined') {
        localStorage.setItem('auth_token', r.data.token);
      }
      return r.data;
    }),

  getUser: (userId: string) =>
    api.get(`/api/users/${userId}`).then((r) => r.data),

  // Resume
  uploadResume: (userId: string, file: File) => {
    const form = new FormData();
    form.append('file', file);
    return api.post(`/api/users/${userId}/resume`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data);
  },

  // Preferences
  savePreferences: (userId: string, prefs: JobPreferences) =>
    api.post(`/api/users/${userId}/preferences`, prefs).then((r) => r.data),

  // Search + match
  searchJobs: (payload: {
    user_id: string;
    query: string;
    location: string;
    platforms: string[];
    min_match_score?: number;
    auto_apply?: boolean;
    dry_run?: boolean;
  }): Promise<SearchResult> =>
    api.post('/api/search', payload).then((r) => r.data),

  // Apply
  applyToJob: (userId: string, job: object, dryRun = true) =>
    api.post('/api/apply', { user_id: userId, job, dry_run: dryRun }).then((r) => r.data),

  // Applications
  getApplications: (userId: string) =>
    api.get(`/api/users/${userId}/applications`).then((r) => r.data),

  // Health
  health: () => api.get('/health').then((r) => r.data),
};

// WebSocket helper
export const createAgentWebSocket = (userId: string): WebSocket => {
  const wsUrl = (API_BASE.replace('http', 'ws'));
  const ws = new WebSocket(`${wsUrl}/ws/${userId}`);
  return ws;
};
