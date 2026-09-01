import React, { useState } from 'react';
import { useMedia } from '../hooks/useMedia';
import { MediaGallery } from '../components/MediaGallery/MediaGallery';
import { Input } from '../components/common/Input';
import { Search, FolderGit2, ArrowLeft } from 'lucide-react';

interface GalleryPageProps {
  initialThreadId?: string;
  onClearThreadFilter?: () => void;
}

export const Gallery: React.FC<GalleryPageProps> = ({
  initialThreadId,
  onClearThreadFilter,
}) => {
  const [searchThread, setSearchThread] = useState<string>(initialThreadId || '');
  const [activeThread, setActiveThread] = useState<string | undefined>(initialThreadId);

  const { items, total, loading, refresh } = useMedia({
    threadId: activeThread,
  });

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setActiveThread(searchThread.trim() || undefined);
  };

  const handleClearFilter = () => {
    setSearchThread('');
    setActiveThread(undefined);
    if (onClearThreadFilter) onClearThreadFilter();
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-zinc-100 flex items-center gap-2">
            <FolderGit2 className="w-6 h-6 text-pink-500" />
            Galeria de Mídias Extraídas
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Total de {total} {total === 1 ? 'mídia armazenada' : 'mídias armazenadas'} localmente.
          </p>
        </div>

        {/* Thread Search Filter */}
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 max-w-sm w-full">
          <Input
            placeholder="Filtrar por ID da Thread..."
            value={searchThread}
            onChange={(e) => setSearchThread(e.target.value)}
            icon={<Search className="w-4 h-4" />}
            className="py-2 text-xs"
          />
          {activeThread && (
            <button
              type="button"
              onClick={handleClearFilter}
              className="p-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-200 text-xs shrink-0 transition-colors"
              title="Limpar filtro"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
          )}
        </form>
      </div>

      {activeThread && (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-pink-500/10 border border-pink-500/20 text-pink-300 text-xs w-fit">
          <span>Filtrando por thread: <strong>{activeThread}</strong></span>
          <button
            onClick={handleClearFilter}
            className="hover:text-white font-bold ml-1"
          >
            ×
          </button>
        </div>
      )}

      {/* Main Media Grid Gallery Component */}
      <MediaGallery
        items={items}
        loading={loading}
        onRefresh={refresh}
      />
    </div>
  );
};
