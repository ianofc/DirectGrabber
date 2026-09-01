import { useState, useEffect, useCallback } from 'react';
import { mediaService } from '../services/api';
import { MediaItem } from '../types';

interface UseMediaOptions {
  threadId?: string;
  mediaType?: 'image' | 'video';
  limit?: number;
}

export function useMedia(options: UseMediaOptions = {}) {
  const [items, setItems] = useState<MediaItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMedia = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await mediaService.listMedia({
        thread_id: options.threadId,
        media_type: options.mediaType,
        limit: options.limit || 100,
      });
      setItems(data.items);
      setTotal(data.total);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Erro ao carregar mídias.');
    } finally {
      setLoading(false);
    }
  }, [options.threadId, options.mediaType, options.limit]);

  useEffect(() => {
    fetchMedia();
  }, [fetchMedia]);

  return {
    items,
    total,
    loading,
    error,
    refresh: fetchMedia,
  };
}
