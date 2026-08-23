import React from 'react';
import { cn } from '../../utils/cn';
import { CheckCircle2, Loader2, AlertCircle, Clock } from 'lucide-react';

export function PipelineStage({ stage, isRunning, currentStage }) {
  const isCurrent = currentStage && currentStage.toLowerCase().includes(stage.id.replace('part', ''));
  const hasCompleted = stage.count > 0 && !isCurrent;
  
  let statusText = "WAITING";
  let statusBadgeClass = "bg-slate-700 text-slate-300";
  let containerClass = "border-slate-800 bg-slate-900/60";
  
  if (isRunning && isCurrent) {
    statusText = "RUNNING";
    statusBadgeClass = "bg-primary text-white animate-pulse";
    containerClass = "border-primary bg-primary/10 ring-1 ring-primary shadow-lg shadow-primary/20";
  } else if (hasCompleted) {
    statusText = "COMPLETED";
    statusBadgeClass = "bg-emerald-500 text-white";
    containerClass = "border-emerald-500/40 bg-emerald-500/5";
  }

  return (
    <div className={cn("flex-1 w-full border rounded-2xl overflow-hidden transition-all duration-300 flex flex-col", containerClass)}>
      <div className="px-5 py-4 border-b border-border/50 flex justify-between items-center bg-slate-900/80">
        <div>
          <span className="text-xs font-extrabold uppercase tracking-widest text-primary">{stage.name}</span>
          <h3 className="text-lg font-bold text-textMain">{stage.title}</h3>
        </div>
        <span className={cn("text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wider flex items-center gap-1", statusBadgeClass)}>
          {statusText === 'RUNNING' && <Loader2 className="h-3 w-3 animate-spin" />}
          {statusText === 'COMPLETED' && <CheckCircle2 className="h-3 w-3" />}
          {statusText}
        </span>
      </div>

      <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
        <div>
          <h4 className="text-xs font-bold text-textMuted uppercase tracking-wider mb-2">Responsibilities:</h4>
          <ul className="space-y-1.5 text-xs text-slate-300">
            {stage.responsibilities.map((r, i) => (
              <li key={i} className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary flex-shrink-0" />
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="pt-4 border-t border-border/40 flex items-center justify-between">
          <div>
            <span className="text-xs text-textMuted block">Processed</span>
            <span className="text-xl font-extrabold font-mono text-textMain">{stage.count}</span>
          </div>
          <div className="text-right">
            <span className="text-xs text-textMuted block">Status</span>
            <span className="text-xs font-semibold text-textMain">{stage.count > 0 ? 'Verified ✓' : 'Pending'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
