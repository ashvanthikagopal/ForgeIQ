import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { CheckCircle2, Clock, Loader2 } from 'lucide-react';
import { cn } from '../../utils/cn';

export function PipelineOverview({ pipelineState, isRunning }) {
  const stages = [
    { name: 'Part 1', title: 'Foundation', count: pipelineState.part1_count, desc: 'Clean + Load' },
    { name: 'Part 2', title: 'Classification', count: pipelineState.part2_count, desc: '+ Attributes' },
    { name: 'Part 3', title: 'Normalization', count: pipelineState.part3_count, desc: '+ Descriptions' },
    { name: 'Part 4', title: 'Enrichment & QA', count: pipelineState.part4_count, desc: 'Quality Check' },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center justify-between">
          <span>PIPELINE STATUS</span>
          <span className="text-xs font-normal text-textMuted uppercase tracking-wider">
            {pipelineState.status.toUpperCase()}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {stages.map((stage) => {
            const isDone = stage.count > 0 && !isRunning;
            const isCurrentlyRunning = isRunning && pipelineState.current_stage?.includes(stage.name);
            return (
              <div 
                key={stage.name} 
                className={cn(
                  "p-4 rounded-xl border flex flex-col justify-between transition-all",
                  isCurrentlyRunning ? "border-primary bg-primary/10 ring-1 ring-primary" : (isDone ? "border-emerald-500/30 bg-emerald-500/5" : "border-border bg-slate-900/40")
                )}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-textMuted">{stage.name}</span>
                    <h4 className="font-bold text-base text-textMain">{stage.title}</h4>
                  </div>
                  {isCurrentlyRunning ? (
                    <Loader2 className="h-5 w-5 text-primary animate-spin" />
                  ) : isDone ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                  ) : (
                    <Clock className="h-5 w-5 text-slate-500" />
                  )}
                </div>
                <div className="mt-4 pt-3 border-t border-border/40">
                  <div className="text-xs text-textMuted">{stage.desc}</div>
                  <div className="text-xl font-bold text-textMain">{stage.count} products</div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
