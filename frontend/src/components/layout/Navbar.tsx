import React from 'react';
import { DownloadCloud, KeyRound, Images, Sparkles } from 'lucide-react';

interface NavbarProps {
  activeTab: 'dashboard' | 'session' | 'gallery';
  setActiveTab: (tab: 'dashboard' | 'session' | 'gallery') => void;
  sessionAuthenticated?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, sessionAuthenticated }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo / Brand */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-pink-600 to-amber-500 p-[2px] flex items-center justify-center shadow-lg shadow-pink-600/20">
            <div className="w-full h-full bg-zinc-950 rounded-[10px] flex items-center justify-center">
              <DownloadCloud className="w-5 h-5 text-pink-500" />
            </div>
          </div>
          <div>
            <h1 className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-zinc-200 to-pink-400 bg-clip-text text-transparent">
              DirectGrabber
            </h1>
            <p className="text-[10px] text-zinc-400 font-mono">Instagram DM Downloader</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1.5 p-1 rounded-2xl bg-zinc-900/90 border border-zinc-800">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'dashboard'
                ? 'bg-zinc-800 text-pink-400 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Extrator
          </button>

          <button
            onClick={() => setActiveTab('gallery')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'gallery'
                ? 'bg-zinc-800 text-pink-400 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
            }`}
          >
            <Images className="w-3.5 h-3.5" />
            Galeria
          </button>

          <button
            onClick={() => setActiveTab('session')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all relative ${
              activeTab === 'session'
                ? 'bg-zinc-800 text-pink-400 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
            }`}
          >
            <KeyRound className="w-3.5 h-3.5" />
            Sessão / Login
            <span
              className={`w-2 h-2 rounded-full ${
                sessionAuthenticated ? 'bg-emerald-500 shadow-sm shadow-emerald-500/50' : 'bg-amber-500 animate-pulse'
              }`}
            />
          </button>
        </nav>
      </div>
    </header>
  );
};
