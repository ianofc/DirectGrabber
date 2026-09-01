import axios from 'axios';
import { MediaItem, TaskStatus, SessionStatus, MediaListResponse, TaskListResponse } from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const authService = {
  getStatus: () => api.get<SessionStatus>('/auth/session/status').then(res => res.data),
  startSession: () => api.post<{ status: string; message: string }>('/auth/session/start').then(res => res.data),
  loginWithCredentials: (data: { username: string; password: string; two_factor_code?: string }) =>
    api.post<{ success: boolean; requires_2fa: boolean; message: string }>('/auth/login', data).then(res => res.data),
  importCookies: (data: { session_id?: string; ds_user_id?: string; raw_cookies?: string; storage_state_json?: string }) =>
    api.post<{ success: boolean; message: string }>('/auth/import-cookies', data).then(res => res.data),
  deleteSession: () => api.delete<{ success: boolean; message: string }>('/auth/session').then(res => res.data),
};

export const taskService = {
  startTask: (threadUrl: string, maxScrolls = 150, headless = false) => 
    api.post<TaskStatus>('/tasks/start', { thread_url: threadUrl, max_scrolls: maxScrolls, headless: headless }).then(res => res.data),
  getTaskStatus: (taskId: string) => 
    api.get<TaskStatus>(`/tasks/${taskId}/status`).then(res => res.data),
  listTasks: (limit = 20) => 
    api.get<TaskListResponse>(`/tasks/?limit=${limit}`).then(res => res.data),
};

export const mediaService = {
  listMedia: (params?: { thread_id?: string; media_type?: string; limit?: number; offset?: number }) => 
    api.get<MediaListResponse>('/media/', { params }).then(res => res.data),
  getThreadMedia: (threadId: string) => 
    api.get<MediaListResponse>(`/media/thread/${threadId}`).then(res => res.data),
  getMediaFileUrl: (mediaId: string) => `/api/v1/media/${mediaId}/file`,
};

export default api;
