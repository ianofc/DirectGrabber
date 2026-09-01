export interface MediaItem {
  id: string;
  task_id?: string | null;
  thread_id: string;
  file_path: string;
  original_url: string;
  media_type: 'image' | 'video';
  file_size: number;
  created_at: string;
}

export interface TaskStatus {
  id: string;
  thread_url: string;
  thread_id?: string | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  total_downloaded: number;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface SessionStatus {
  authenticated: boolean;
  session_file_exists: boolean;
  last_modified?: string | null;
  message: string;
}

export interface MediaListResponse {
  items: MediaItem[];
  total: number;
}

export interface TaskListResponse {
  tasks: TaskStatus[];
}
