import React, { useState, useEffect } from 'react';
import { authService } from '../services/api';
import { SessionStatus } from '../types';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import {
  ShieldCheck,
  ShieldAlert,
  KeyRound,
  RefreshCw,
  Trash2,
  CheckCircle2,
  ExternalLink,
  Cookie,
  UserCheck,
  Zap,
  Info
} from 'lucide-react';

interface SessionAuthProps {
  onSessionChange?: () => void;
}

export const SessionAuth: React.FC<SessionAuthProps> = ({ onSessionChange }) => {
  const [status, setStatus] = useState<SessionStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [startingSession, setStartingSession] = useState<boolean>(false);

  // Form states - Cookie manual
  const [sessionId, setSessionId] = useState<string>('');
  const [cookieSubmitting, setCookieSubmitting] = useState<boolean>(false);

  const [feedback, setFeedback] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const data = await authService.getStatus();
      setStatus(data);
      if (onSessionChange) onSessionChange();
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  // 1. Abrir navegador persistente do Playwright
  const handleOpenBrowserLogin = async () => {
    setStartingSession(true);
    setFeedback(null);
    try {
      const res = await authService.startSession();
      setFeedback({ type: 'info', message: res.message });

      // Polling a cada 2.5s para detectar o momento que logou
      const interval = setInterval(async () => {
        const current = await authService.getStatus();
        if (current.authenticated) {
          setStatus(current);
          setStartingSession(false);
          setFeedback({ type: 'success', message: 'Instagram conectado com sucesso! Sessão salva permanentemente.' });
          clearInterval(interval);
          if (onSessionChange) onSessionChange();
        }
      }, 2500);

      setTimeout(() => {
        clearInterval(interval);
        setStartingSession(false);
      }, 300000);
    } catch (err: any) {
      setFeedback({
        type: 'error',
        message: err?.response?.data?.detail || 'Erro ao iniciar navegador de login.',
      });
      setStartingSession(false);
    }
  };

  // 2. Colar sessionid manual (F12)
  const handleCookieSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sessionId.trim()) {
      setFeedback({ type: 'error', message: 'Cole o valor do sessionid do Instagram.' });
      return;
    }

    setCookieSubmitting(true);
    setFeedback(null);

    try {
      const cleanVal = sessionId.trim();
      const res = cleanVal.includes('=')
        ? await authService.importCookies({ raw_cookies: cleanVal })
        : await authService.importCookies({ session_id: cleanVal });

      setFeedback({ type: 'success', message: res.message });
      setSessionId('');
      await fetchStatus();
    } catch (err: any) {
      setFeedback({
        type: 'error',
        message: err?.response?.data?.detail || 'Falha ao salvar sessão.',
      });
    } finally {
      setCookieSubmitting(false);
    }
  };

  const handleDeleteSession = async () => {
    if (!confirm('Deseja realmente desconectar e apagar a sessão salva?')) return;
    try {
      await authService.deleteSession();
      await fetchStatus();
      setFeedback({ type: 'info', message: 'Sessão desconectada com sucesso.' });
    } catch (err: any) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div className="space-y-2 text-center sm:text-left">
        <h2 className="text-2xl font-bold tracking-tight text-zinc-100 flex items-center justify-center sm:justify-start gap-2">
          <KeyRound className="w-6 h-6 text-pink-500" />
          Conexão da Conta do Instagram
        </h2>
        <p className="text-sm text-zinc-400">
          Autentique sua conta para permitir a extração e download das mídias das conversas privadas (DMs).
        </p>
      </div>

      {/* Status Card */}
      <div className="rounded-3xl bg-zinc-900/90 border border-zinc-800 p-6 sm:p-8 shadow-2xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-zinc-800">
          <div className="flex items-start gap-4">
            <div
              className={`p-3.5 rounded-2xl ${
                status?.authenticated
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              }`}
            >
              {status?.authenticated ? (
                <ShieldCheck className="w-8 h-8" />
              ) : (
                <ShieldAlert className="w-8 h-8" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-base text-zinc-100">
                  {status?.authenticated ? 'Sessão Conectada e Ativa' : 'Instagram Desconectado'}
                </h3>
                {status?.authenticated && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    <UserCheck className="w-3 h-3" /> Sessão Gravada
                  </span>
                )}
              </div>
              <p className="text-xs text-zinc-400 mt-1">
                {status?.message || 'Verificando estado dos cookies...'}
              </p>
              {status?.last_modified && (
                <p className="text-[11px] text-zinc-500 mt-1 font-mono">
                  Último login: {new Date(status.last_modified).toLocaleString('pt-BR')}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 self-end sm:self-auto">
            <button
              onClick={fetchStatus}
              disabled={loading}
              className="p-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
              title="Atualizar status"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>

            {status?.session_file_exists && (
              <button
                onClick={handleDeleteSession}
                className="p-2.5 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 transition-colors"
                title="Desconectar sessão"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Método 1: Conexão Automática com Perfil Persistente */}
        <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-800 space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-zinc-100">
            <Zap className="w-4 h-4 text-pink-400" />
            <span>Método Recomendado: Conexão com Navegador Integrado</span>
          </div>

          <p className="text-xs text-zinc-400 leading-relaxed">
            Clique no botão abaixo para abrir o navegador integrado. Entre na sua conta do Instagram normalmente. Uma vez conectado, <strong>a sessão fica salva permanentemente</strong> e você não precisará logar novamente.
          </p>

          <Button
            variant="gradient"
            size="lg"
            className="w-full"
            loading={startingSession}
            onClick={handleOpenBrowserLogin}
          >
            <ExternalLink className="w-4 h-4 mr-2" />
            {status?.authenticated ? 'Reconectar / Atualizar Sessão no Navegador' : 'Abrir Instagram e Conectar Sessão'}
          </Button>

          {startingSession && (
            <div className="p-4 rounded-2xl bg-pink-950/30 border border-pink-800/50 text-pink-300 text-xs space-y-1.5 animate-pulse">
              <p className="font-bold flex items-center gap-1.5">
                <ExternalLink className="w-4 h-4" />
                Janela do navegador aberta!
              </p>
              <p className="text-pink-200/90">
                Faça o login ou confirme sua conta na janela aberta. Assim que a página inicial ou suas DMs carregarem, o DirectGrabber salvará a sessão automaticamente.
              </p>
            </div>
          )}
        </div>

        {/* Método 2: Colar cookie sessionid manualmente */}
        <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-800/80 space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-zinc-100">
            <Cookie className="w-4 h-4 text-purple-400" />
            <span>Método Alternativo: Colar Cookie 'sessionid'</span>
          </div>

          <p className="text-xs text-zinc-400">
            Se você já está logado no Instagram no seu navegador comum (Chrome/Edge/Brave), abra o <strong>Inspecionar (F12) → Aplicativo (Application) → Cookies → https://www.instagram.com</strong>, copie o valor do cookie <code className="text-pink-400 font-mono">sessionid</code> e cole abaixo:
          </p>

          <form onSubmit={handleCookieSubmit} className="flex flex-col sm:flex-row gap-2">
            <Input
              placeholder="Cole aqui o sessionid (ex: 1234567890%3AaBCdEFg...)"
              value={sessionId}
              onChange={(e) => setSessionId(e.target.value)}
              icon={<Cookie className="w-4 h-4" />}
              className="py-3 text-xs"
              disabled={cookieSubmitting}
            />
            <Button
              type="submit"
              variant="secondary"
              size="md"
              loading={cookieSubmitting}
              className="shrink-0"
            >
              Salvar Cookie
            </Button>
          </form>
        </div>

        {/* Feedback Message */}
        {feedback && (
          <div
            className={`p-4 rounded-2xl text-xs flex items-center gap-2 ${
              feedback.type === 'success'
                ? 'bg-emerald-950/30 border border-emerald-800/40 text-emerald-300'
                : feedback.type === 'error'
                ? 'bg-red-950/30 border border-red-800/40 text-red-300'
                : 'bg-zinc-800/80 border border-zinc-700 text-zinc-200'
            }`}
          >
            {feedback.type === 'success' && <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />}
            {feedback.type === 'error' && <ShieldAlert className="w-4 h-4 text-red-400 shrink-0" />}
            {feedback.type === 'info' && <Info className="w-4 h-4 text-pink-400 shrink-0" />}
            <span>{feedback.message}</span>
          </div>
        )}
      </div>
    </div>
  );
};
