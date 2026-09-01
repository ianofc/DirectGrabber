import React from 'react';

interface BadgeProps {
  variant?: 'pending' | 'processing' | 'completed' | 'failed' | 'image' | 'video' | 'default';
  children: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  children,
  className = '',
}) => {
  const variants = {
    pending: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    processing: 'bg-blue-500/10 text-blue-400 border-blue-500/30 animate-pulse',
    completed: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    failed: 'bg-red-500/10 text-red-400 border-red-500/30',
    image: 'bg-purple-500/10 text-purple-300 border-purple-500/30',
    video: 'bg-pink-500/10 text-pink-300 border-pink-500/30',
    default: 'bg-zinc-800 text-zinc-300 border-zinc-700',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${variants[variant]} ${className}`}
    >
      {children}
    </span>
  );
};
