import React, { useEffect } from 'react';
import { MediaItem } from '../../types';
import { mediaService } from '../../services/api';
import { X, ChevronLeft, ChevronRight, Download, ExternalLink } from 'lucide-react';

interface LightboxProps {
  items: MediaItem[];
  currentIndex: number;
  onClose: () => void;
  onNavigate: (index: number) => void;
}

export const Lightbox: React.FC<LightboxProps> = ({
  items,
  currentIndex,
  onClose,
  onNavigate,
}) => {
  const currentItem = items[currentIndex];

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft' && currentIndex > 0) onNavigate(currentIndex - 1);
      if (e.key === 'ArrowRight' && currentIndex < items.length - 1) onNavigate(currentIndex + 1);
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, items.length, onClose, onNavigate]);

  if (!currentItem) return null;

  const fileUrl = mediaService.getMediaFileUrl(currentItem.id);
  const isVideo = currentItem.media_type === 'video';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-md">
      {/* Top action bar */}
      <div className="absolute top-4 inset-x-4 flex items-center justify-between z-10">
        <div className="text-zinc-400 text-xs font-mono">
          {currentIndex + 1} de {items.length}
        </div>

        <div className="flex items-center gap-2">
          <a
            href={fileUrl}
            download
            className="p-2.5 rounded-xl bg-zinc-900/80 hover:bg-zinc-800 text-zinc-200 border border-zinc-700/60 transition-colors flex items-center gap-1.5 text-xs font-medium"
          >
            <Download className="w-4 h-4 text-pink-400" />
            Baixar Original
          </a>

          <a
            href={currentItem.original_url}
            target="_blank"
            rel="noreferrer"
            className="p-2.5 rounded-xl bg-zinc-900/80 hover:bg-zinc-800 text-zinc-200 border border-zinc-700/60 transition-colors flex items-center gap-1.5 text-xs font-medium"
          >
            <ExternalLink className="w-4 h-4 text-purple-400" />
            Link CDN
          </a>

          <button
            onClick={onClose}
            className="p-2.5 rounded-xl bg-zinc-900/80 hover:bg-zinc-800 text-zinc-200 border border-zinc-700/60 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Navigation Arrows */}
      {currentIndex > 0 && (
        <button
          onClick={() => onNavigate(currentIndex - 1)}
          className="absolute left-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-zinc-900/80 hover:bg-zinc-800 text-white border border-zinc-700/60 transition-all z-10"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
      )}

      {currentIndex < items.length - 1 && (
        <button
          onClick={() => onNavigate(currentIndex + 1)}
          className="absolute right-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-zinc-900/80 hover:bg-zinc-800 text-white border border-zinc-700/60 transition-all z-10"
        >
          <ChevronRight className="w-6 h-6" />
        </button>
      )}

      {/* Media display container */}
      <div className="max-w-5xl max-h-[85vh] p-4 flex items-center justify-center">
        {isVideo ? (
          <video
            src={fileUrl}
            controls
            autoPlay
            className="max-w-full max-h-[80vh] rounded-2xl shadow-2xl border border-zinc-800"
          />
        ) : (
          <img
            src={fileUrl}
            alt="DM Media Preview"
            className="max-w-full max-h-[80vh] object-contain rounded-2xl shadow-2xl border border-zinc-800"
          />
        )}
      </div>
    </div>
  );
};
