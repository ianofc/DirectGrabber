import React from 'react';
import { TaskStatus } from '../../types';
import { Badge } from '../common/Badge';
import { Loader2, CheckCircle2, XCircle, Clock, FileDown, ExternalLink } from 'lucide-react';

interface TaskMonitorProps {
  task: TaskStatus | null;
  onViewGallery?: (threadId: string) => void;
}

export const TaskMonitor: React.FC<TaskMonitorProps> = ({ task, onViewGallery }) => {
  if (!task) return null;

  const getStatusBadge = () => {
    switch (task.status) {
      case 'processing':
        return (
          <Badge variant="processing">
            <Loader2 className="w-3 h-3 animate-spin" /> Em Processamento
          </Badge>
        );
      case 'completed':
        return (
          <Badge variant="completed">
            <CheckCircle2 className="w-3 h-3" /> Concluído
          </Badge>
        );
      case 'failed':
        return (
          <Badge variant="failed">
            <XCircle className="w-3 h-3" /> Falhou
          </Badge>
        );
      default:
        return (
          <Badge variant="pending">
            <Clock className="w-3 h-3" /> Na Fila
          </Badge>
        );
    }
  };

  return (
    <div className="w-full rounded-2xl bg-zinc-900/80 border border-zinc-800 p-6 shadow-xl space-y-4 transition-all">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-zinc-100 text-sm">Status da Extração</h3>
            {getStatusBadge()}
          </div>
          <p className="text-xs text-zinc-400 font-mono mt-1 truncate max-w-md">
            URL: {task.thread_url}
          </p>
        </div>

        {task.status === 'completed' && task.thread_id && onViewGallery && (
          <button
            onClick={() => onViewGallery(task.thread_id!)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-pink-500/10 text-pink-400 border border-pink-500/20 hover:bg-pink-500/20 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            Ver na Galeria
          </button>
        )}
      </div>

      {/* Progress Bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs font-medium">
          <span className="text-zinc-400">Progresso</span>
          <span className="text-pink-400 font-bold">{task.progress}%</span>
        </div>
        <div className="w-full h-2.5 bg-zinc-800 rounded-full overflow-hidden p-[2px]">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              task.status === 'failed'
                ? 'bg-red-500'
                : 'bg-gradient-to-r from-purple-600 via-pink-600 to-amber-500'
            }`}
            style={{ width: `${Math.max(task.progress, 3)}%` }}
          />
        </div>
      </div>

      {/* Metrics & Details */}
      <div className="grid grid-cols-2 gap-4 pt-2 text-xs">
        <div className="flex items-center gap-2 p-3 rounded-xl bg-zinc-950/60 border border-zinc-800/60">
          <FileDown className="w-4 h-4 text-pink-400" />
          <div>
            <p className="text-zinc-500">Mídias Baixadas</p>
            <p className="text-zinc-200 font-bold text-sm">{task.total_downloaded}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 p-3 rounded-xl bg-zinc-950/60 border border-zinc-800/60">
          <Clock className="w-4 h-4 text-purple-400" />
          <div>
            <p className="text-zinc-500">Iniciado em</p>
            <p className="text-zinc-200 font-medium">
              {new Date(task.created_at).toLocaleTimeString('pt-BR')}
            </p>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {task.error_message && (
        <div className="p-3 rounded-xl bg-red-950/30 border border-red-800/40 text-red-300 text-xs">
          <span className="font-bold">Erro: </span>
          {task.error_message}
        </div>
      )}
    </div>
  );
};
