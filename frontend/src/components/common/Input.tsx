import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  icon,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-xs font-semibold text-zinc-300 uppercase tracking-wider">
          {label}
        </label>
      )}
      <div className="relative flex items-center">
        {icon && (
          <div className="absolute left-3.5 text-zinc-400 pointer-events-none flex items-center">
            {icon}
          </div>
        )}
        <input
          id={inputId}
          className={`w-full rounded-xl bg-zinc-900/90 border ${
            error ? 'border-red-500/70 focus:border-red-500 focus:ring-red-500/20' : 'border-zinc-700/70 focus:border-pink-500 focus:ring-pink-500/20'
          } ${icon ? 'pl-11' : 'pl-4'} pr-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 shadow-inner focus:outline-none focus:ring-4 transition-all duration-200 ${className}`}
          {...props}
        />
      </div>
      {error && <p className="text-xs text-red-400 font-medium">{error}</p>}
      {helperText && !error && <p className="text-xs text-zinc-400">{helperText}</p>}
    </div>
  );
};
