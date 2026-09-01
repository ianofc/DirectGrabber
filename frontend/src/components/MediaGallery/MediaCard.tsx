import React from 'react';
import { MediaItem } from '../../types';
import { mediaService } from '../../services/api';
import { Play, Download, Image as ImageIcon, Video as VideoIcon } from 'lucide-react';

interface MediaCardProps {
  item: MediaItem;
  onClick: () => void;
}

export const MediaCard: React.FC<MediaCardProps> = ({ item, onClick }) => {
  const fileUrl = mediaService.getMediaFileUrl(item.id);
  const isVideo = item.media_type === 'video';

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div
      onClick={onClick}
      className="group relative aspect-square rounded-2xl overflow-hidden bg-zinc-900 border border-zinc-800/80 cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:border-pink-500/50 hover:shadow-xl hover:shadow-pink-500/10"
    >
      {isVideo ? (
        <div className="w-full h-full relative bg-zinc-950 flex items-center justify-center">
          <video
            src={fileUrl}
            className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
            preload="metadata"
            muted
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-12 h-12 rounded-full bg-black/60 backdrop-blur-sm border border-white/20 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Play className="w-5 h-5 text-pink-400 fill-pink-400 ml-0.5" />
            </div>
          </div>
        </div>
      ) : (
        <img
          src={fileUrl}
          alt={`DM Media ${item.id}`}
          loading="lazy"
          className="w-full h-full object-cover transition-all duration-300 group-hover:scale-105"
        />
      )}

      {/* Type badge overlay */}
      <div className="absolute top-2.5 left-2.5 px-2 py-1 rounded-lg bg-black/60 backdrop-blur-md border border-white/10 flex items-center gap-1.5 text-[10px] font-semibold text-zinc-200">
        {isVideo ? (
          <>
            <VideoIcon className="w-3 h-3 text-pink-400" />
            <span>MP4</span>
          </>
        ) : (
          <>
            <ImageIcon className="w-3 h-3 text-purple-400" />
            <span>JPG</span>
          </>
        )}
      </div>

      {/* Info overlay on hover */}
      <div className="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-black/90 via-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-between">
        <div className="text-[11px] text-zinc-300">
          <p className="font-semibold truncate max-w-[120px]">Thread: {item.thread_id}</p>
          <p className="text-zinc-500">{formatBytes(item.file_size)}</p>
        </div>

        <a
          href={fileUrl}
          download
          onClick={(e) => e.stopPropagation()}
          className="p-2 rounded-xl bg-pink-500/20 hover:bg-pink-500 text-pink-300 hover:text-white transition-colors"
          title="Baixar arquivo"
        >
          <Download className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  );
};
