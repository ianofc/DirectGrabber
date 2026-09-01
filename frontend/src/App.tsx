import React, { useState, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { Container } from './components/layout/Container';
import { Dashboard } from './pages/Dashboard';
import { SessionAuth } from './pages/SessionAuth';
import { Gallery } from './pages/Gallery';
import { authService } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'session' | 'gallery'>('dashboard');
  const [sessionAuthenticated, setSessionAuthenticated] = useState<boolean>(false);
  const [selectedGalleryThread, setSelectedGalleryThread] = useState<string | undefined>(undefined);

  const checkSession = async () => {
    try {
      const status = await authService.getStatus();
      setSessionAuthenticated(status.authenticated);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    checkSession();
  }, []);

  const handleNavigateToGallery = (threadId?: string) => {
    setSelectedGalleryThread(threadId);
    setActiveTab('gallery');
  };

  return (
    <div className="min-h-screen bg-[#090a0f] text-zinc-100 flex flex-col selection:bg-pink-600 selection:text-white">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        sessionAuthenticated={sessionAuthenticated}
      />

      <Container className="flex-1">
        {activeTab === 'dashboard' && (
          <Dashboard
            sessionAuthenticated={sessionAuthenticated}
            onNavigateToAuth={() => setActiveTab('session')}
            onNavigateToGallery={handleNavigateToGallery}
          />
        )}

        {activeTab === 'session' && (
          <SessionAuth onSessionChange={checkSession} />
        )}

        {activeTab === 'gallery' && (
          <Gallery
            initialThreadId={selectedGalleryThread}
            onClearThreadFilter={() => setSelectedGalleryThread(undefined)}
          />
        )}
      </Container>

      {/* Footer */}
      <footer className="border-t border-zinc-900 bg-zinc-950 py-6 text-center text-xs text-zinc-400">
        <p>DirectGrabber — Extrator de Fotos e Vídeos de DMs do Instagram • FastAPI & Playwright</p>
      </footer>
    </div>
  );
}

export default App;
