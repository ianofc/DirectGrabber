import React, { useState, useEffect } from 'react';
import { useTask } from '../hooks/useTask';
import { taskService } from '../services/api';
import { TaskStatus } from '../types';
import { TaskMonitor } from '../components/TaskMonitor/TaskMonitor';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Badge } from '../components/common/Badge';
import {
  Link2,
  Sparkles,
  History,
  ArrowRight,
  ShieldAlert,
  Film,
  Image as ImageIcon,
  Compass,
  CalendarDays,
  Flame,
  Clock,
  Eye,
  MonitorPlay
} from 'lucide-react';

interface DashboardProps {
  sessionAuthenticated?: boolean;
  onNavigateToAuth: () => void;
  onNavigateToGallery: (threadId?: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  sessionAuthenticated = false,
  onNavigateToAuth,
  onNavigateToGallery,
}) => {
  const [threadUrl, setThreadUrl] = useState<string>('');
  const [historyScope, setHistoryScope] = useState<'full' | 'deep' | 'recent'>('full');
  const [watchLive, setWatchLive] = useState<boolean>(true); // Modo visual visível por padrão
  const { task, loading, error, startExtraction, setTaskId } = useTask();
  const [recentTasks, setRecentTasks] = useState<TaskStatus[]>([]);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(false);

  const fetchRecentTasks = async () => {
    setLoadingHistory(true);
    try {
      const res = await taskService.listTasks(10);
      setRecentTasks(res.tasks);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    fetchRecentTasks();
  }, []);

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!threadUrl.trim()) return;

    let scrolls = 150;
    if (historyScope === 'deep') scrolls = 350; // Conversas de vários anos
    if (historyScope === 'recent') scrolls = 25; // Apenas mensagens recentes

    try {
      // Se watchLive estiver ativo, headless é false (janela visível)
      await startExtraction(threadUrl.trim(), scrolls, !watchLive);
      fetchRecentTasks();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-10">
      {/* Session warning banner if not authenticated */}
      {!sessionAuthenticated && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
            <p className="text-xs text-amber-200">
              Você ainda não conectou sua sessão do Instagram. A extração de DMs requer a sessão salva.
            </p>
          </div>
          <button
            onClick={onNavigateToAuth}
            className="px-3 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-zinc-950 font-bold text-xs shrink-0 transition-colors"
          >
            Conectar Instagram Agora
          </button>
        </div>
      )}

      {/* Main Hero / Extraction Input */}
      <section className="relative rounded-3xl overflow-hidden bg-gradient-to-b from-zinc-900 via-zinc-900/90 to-zinc-950 border border-zinc-800/80 p-8 sm:p-12 shadow-2xl space-y-6">
        <div className="max-w-2xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-pink-500/10 border border-pink-500/20 text-pink-400 text-xs font-semibold">
            <Compass className="w-3.5 h-3.5" />
            Backtracking Visual de Histórico & Resolução Máxima
          </div>

          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
            Extrair Mídias da Conversa
          </h2>

          <p className="text-sm text-zinc-400 max-w-lg mx-auto">
            O aplicativo abre a conversa, <strong>rola o chat para cima em tempo real na sua tela</strong> e extrai automaticamente todas as fotos e vídeos MP4 até o início da conversa.
          </p>

          {/* Form */}
          <form onSubmit={handleStart} className="pt-2 space-y-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <Input
                placeholder="Cole o link da conversa: https://www.instagram.com/direct/t/1234567890/"
                value={threadUrl}
                onChange={(e) => setThreadUrl(e.target.value)}
                icon={<Link2 className="w-4 h-4" />}
                className="py-3.5 text-sm"
                disabled={loading}
              />
              <Button
                type="submit"
                variant="gradient"
                size="lg"
                loading={loading}
                className="shrink-0"
              >
                Iniciar Extração
              </Button>
            </div>

            {/* Opções de Modo Visual e Alcance de Histórico */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-left">
              {/* Toggle Modo Visual */}
              <div
                onClick={() => setWatchLive(!watchLive)}
                className={`p-3.5 rounded-2xl border cursor-pointer transition-all flex items-center justify-between gap-3 ${
                  watchLive
                    ? 'bg-pink-950/20 border-pink-500/50 shadow-md shadow-pink-500/10'
                    : 'bg-zinc-950/60 border-zinc-800 text-zinc-400'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-xl ${watchLive ? 'bg-pink-500 text-white' : 'bg-zinc-800 text-zinc-400'}`}>
                    <MonitorPlay className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-zinc-100 flex items-center gap-1.5">
                      Modo Visual na Tela
                      {watchLive && <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />}
                    </p>
                    <p className="text-[11px] text-zinc-400">
                      Abre a janela para você ver a conversa rolando ao vivo
                    </p>
                  </div>
                </div>

                <div className={`w-5 h-5 rounded-md border flex items-center justify-center transition-colors ${
                  watchLive ? 'bg-pink-600 border-pink-500 text-white' : 'border-zinc-700 bg-zinc-900'
                }`}>
                  {watchLive && <Eye className="w-3 h-3" />}
                </div>
              </div>

              {/* Alcance de Histórico Selector */}
              <div className="bg-zinc-950/80 border border-zinc-800 p-3 rounded-2xl flex flex-col justify-center gap-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-zinc-300">
                  <CalendarDays className="w-4 h-4 text-purple-400" />
                  <span>Alcance:</span>
                </div>

                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => setHistoryScope('full')}
                    className={`flex items-center gap-1 px-2.5 py-1 rounded-xl text-[11px] font-medium transition-all ${
                      historyScope === 'full'
                        ? 'bg-purple-600/30 text-purple-300 border border-purple-500/50 shadow-sm'
                        : 'bg-zinc-900 text-zinc-400 hover:text-zinc-200 border border-zinc-800'
                    }`}
                  >
                    <Sparkles className="w-3 h-3 text-purple-400" />
                    Até o Início (Padrão)
                  </button>

                  <button
                    type="button"
                    onClick={() => setHistoryScope('deep')}
                    className={`flex items-center gap-1 px-2.5 py-1 rounded-xl text-[11px] font-medium transition-all ${
                      historyScope === 'deep'
                        ? 'bg-pink-600/30 text-pink-300 border border-pink-500/50 shadow-sm'
                        : 'bg-zinc-900 text-zinc-400 hover:text-zinc-200 border border-zinc-800'
                    }`}
                  >
                    <Flame className="w-3 h-3 text-pink-400" />
                    +350 Blocos
                  </button>

                  <button
                    type="button"
                    onClick={() => setHistoryScope('recent')}
                    className={`flex items-center gap-1 px-2.5 py-1 rounded-xl text-[11px] font-medium transition-all ${
                      historyScope === 'recent'
                        ? 'bg-zinc-700 text-zinc-200 border border-zinc-600 shadow-sm'
                        : 'bg-zinc-900 text-zinc-400 hover:text-zinc-200 border border-zinc-800'
                    }`}
                  >
                    <Clock className="w-3 h-3" />
                    Recentes
                  </button>
                </div>
              </div>
            </div>
          </form>

          {error && (
            <p className="text-xs text-red-400 text-left sm:text-center mt-2">{error}</p>
          )}

          <div className="flex items-center justify-center gap-6 pt-2 text-xs text-zinc-500">
            <div className="flex items-center gap-1.5">
              <ImageIcon className="w-3.5 h-3.5 text-purple-400" />
              <span>Fotos JPG/PNG</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Film className="w-3.5 h-3.5 text-pink-400" />
              <span>Vídeos MP4</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>Rolagem Visível na Tela</span>
            </div>
          </div>
        </div>
      </section>

      {/* Active Task Monitor */}
      {task && (
        <section className="space-y-3">
          <h3 className="text-sm font-bold text-zinc-300 uppercase tracking-wider">
            Tarefa em Andamento
          </h3>
          <TaskMonitor task={task} onViewGallery={(threadId) => onNavigateToGallery(threadId)} />
        </section>
      )}

      {/* Recent Extraction Tasks */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-zinc-400" />
            <h3 className="text-sm font-bold text-zinc-200">Histórico de Extrações Recentes</h3>
          </div>
          <button
            onClick={fetchRecentTasks}
            className="text-xs text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            Atualizar lista
          </button>
        </div>

        {recentTasks.length === 0 ? (
          <div className="p-8 rounded-2xl bg-zinc-900/40 border border-zinc-800 text-center text-xs text-zinc-500">
            Nenhuma extração realizada ainda. Cole uma URL acima para começar!
          </div>
        ) : (
          <div className="rounded-2xl bg-zinc-900/60 border border-zinc-800/80 divide-y divide-zinc-800/60 overflow-hidden shadow-lg">
            {recentTasks.map((t) => (
              <div
                key={t.id}
                onClick={() => setTaskId(t.id)}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-zinc-800/30 cursor-pointer transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-zinc-200 font-mono">
                      Thread: {t.thread_id || 'ID Desconhecido'}
                    </span>
                    <Badge variant={t.status as any}>{t.status}</Badge>
                  </div>
                  <p className="text-[11px] text-zinc-500 truncate max-w-lg">{t.thread_url}</p>
                </div>

                <div className="flex items-center gap-4 text-xs text-zinc-400 self-end sm:self-auto">
                  <span className="font-semibold text-zinc-300">
                    {t.total_downloaded} {t.total_downloaded === 1 ? 'mídia' : 'mídias'}
                  </span>
                  <span className="text-zinc-500">
                    {new Date(t.created_at).toLocaleDateString('pt-BR')}
                  </span>
                  {t.thread_id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onNavigateToGallery(t.thread_id!);
                      }}
                      className="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
                      title="Ver galeria desta conversa"
                    >
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
