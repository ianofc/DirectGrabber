import React, { useState } from 'react';
import { MediaItem } from '../../types';
import { MediaCard } from './MediaCard';
import { Lightbox } from './Lightbox';
import { Spinner } from '../common/Spinner';
import { Image as ImageIcon, Video as VideoIcon, RefreshCw, FolderSearch } from 'lucide-react';

interface MediaGalleryProps {
  items: MediaItem[];
  loading?: boolean;
  onRefresh?: () => void;
  filterThreadId?: string;
  setFilterThreadId?: (id: string) => void;
}

export const MediaGallery: React.FC<MediaGalleryProps> = ({
  items,
  loading = false,
  onRefresh,
}) => {
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);
  const [selectedType, setSelectedType] = useState<'all' | 'image' | 'video'>('all');

  const filteredItems = items.filter((item) => {
    if (selectedType === 'all') return true;
    return item.media_type === selectedType;
  });

  return (
    <div className="space-y-6">
      {/* Gallery Header & Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-zinc-900/60 border border-zinc-800/80 p-4 rounded-2xl">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-zinc-400">Filtrar por:</span>
          <div className="flex items-center gap-1 bg-zinc-950 p-1 rounded-xl border border-zinc-800">
            <button
              onClick={() => setSelectedType('all')}
              className={`px-3 py-1 text-xs font-medium rounded-lg transition-all ${
                selectedType === 'all'
                  ? 'bg-zinc-800 text-white'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Todos ({items.length})
            </button>
            <button
              onClick={() => setSelectedType('image')}
              className={`flex items-center gap-1 px-3 py-1 text-xs font-medium rounded-lg transition-all ${
                selectedType === 'image'
                  ? 'bg-purple-600/30 text-purple-300 border border-purple-500/40'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <ImageIcon className="w-3.5 h-3.5" />
              Fotos ({items.filter((i) => i.media_type === 'image').length})
            </button>
            <button
              onClick={() => setSelectedType('video')}
              className={`flex items-center gap-1 px-3 py-1 text-xs font-medium rounded-lg transition-all ${
                selectedType === 'video'
                  ? 'bg-pink-600/30 text-pink-300 border border-pink-500/40'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <VideoIcon className="w-3.5 h-3.5" />
              Vídeos ({items.filter((i) => i.media_type === 'video').length})
            </button>
          </div>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-zinc-400 hover:text-zinc-200 bg-zinc-800/60 hover:bg-zinc-800 rounded-xl transition-all self-end sm:self-auto"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </button>
        )}
      </div>

      {/* Media Grid */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center space-y-3">
          <Spinner size="lg" />
          <p className="text-xs text-zinc-500">Carregando galeria de mídias...</p>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="py-20 flex flex-col items-center justify-center text-center p-6 rounded-2xl border border-dashed border-zinc-800">
          <div className="w-12 h-12 rounded-2xl bg-zinc-900 flex items-center justify-center mb-3">
            <FolderSearch className="w-6 h-6 text-zinc-500" />
          </div>
          <h4 className="text-sm font-bold text-zinc-300">Nenhuma mídia encontrada</h4>
          <p className="text-xs text-zinc-500 max-w-sm mt-1">
            Inicie uma extração de DM no painel principal ou ajuste os filtros para visualizar os arquivos.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {filteredItems.map((item, index) => (
            <MediaCard
              key={item.id}
              item={item}
              onClick={() => setLightboxIndex(index)}
            />
          ))}
        </div>
      )}

      {/* Lightbox Modal */}
      {lightboxIndex !== null && (
        <Lightbox
          items={filteredItems}
          currentIndex={lightboxIndex}
          onClose={() => setLightboxIndex(null)}
          onNavigate={(newIdx) => setLightboxIndex(newIdx)}
        />
      )}
    </div>
  );
};
