import { useState, useEffect, useRef } from 'react';
import { taskService } from '../services/api';
import { TaskStatus } from '../types';

export function useTask(initialTaskId?: string | null) {
  const [taskId, setTaskId] = useState<string | null>(initialTaskId || null);
  const [task, setTask] = useState<TaskStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const pollTimer = useRef<number | null>(null);

  const startExtraction = async (threadUrl: string, maxScrolls = 150, headless = false) => {
    setLoading(true);
    setError(null);
    try {
      const newTask = await taskService.startTask(threadUrl, maxScrolls, headless);
      setTaskId(newTask.id);
      setTask(newTask);
      return newTask;
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Falha ao iniciar a extração.';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!taskId) return;

    const fetchStatus = async () => {
      try {
        const current = await taskService.getTaskStatus(taskId);
        setTask(current);

        // Se ainda está pendente ou processando, continua o polling a cada 2 segundos
        if (current.status === 'pending' || current.status === 'processing') {
          pollTimer.current = window.setTimeout(fetchStatus, 2000);
        }
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Erro ao consultar status da tarefa.');
      }
    };

    fetchStatus();

    return () => {
      if (pollTimer.current) {
        clearTimeout(pollTimer.current);
      }
    };
  }, [taskId]);

  return {
    taskId,
    task,
    loading,
    error,
    startExtraction,
    setTaskId,
  };
}
