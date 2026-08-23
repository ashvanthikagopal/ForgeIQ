import React from 'react';
import { cn } from '../../utils/cn';

export function Badge({ children, variant = 'default', className, ...props }) {
  const variants = {
    default: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30 badge-glow-indigo',
    success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30 badge-glow-emerald',
    warning: 'bg-amber-500/15 text-amber-400 border-amber-500/30 badge-glow-amber',
    danger: 'bg-rose-500/15 text-rose-400 border-rose-500/30 badge-glow-rose',
    error: 'bg-rose-500/15 text-rose-400 border-rose-500/30 badge-glow-rose',
    outline: 'border-slate-800 text-slate-400 bg-slate-900/60',
  };

  return (
    <div 
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wide transition-all",
        variants[variant] || variants.default,
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
