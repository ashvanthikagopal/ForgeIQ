import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Loader2, CheckCircle2 } from 'lucide-react';

export function PipelineProgress({ isRunning, currentStage, completedStages = [] }) {
  if (!isRunning && completedStages.length === 0) return null;

  const sixStages = [
    { key: 'input', label: 'Input Analysis', part: 'Part 1' },
    { key: 'classification', label: 'Classification', part: 'Part 2' },
    { key: 'attributes', label: 'Attribute Extraction', part: 'Part 2' },
    { key: 'normalization', label: 'Normalization', part: 'Part 3' },
    { key: 'descriptions', label: 'Description Generation', part: 'Part 3' },
    { key: 'enrichment', label: 'Enrichment & QA', part: 'Part 4' },
  ];

  // Map backend current_stage string ("Part 1", "Part 2", "Part 3", "Part 4")
  const getStageStatus = (stagePart) => {
    if (!isRunning) return 'done';
    const stageOrder = ['Part 1', 'Part 2', 'Part 3', 'Part 4'];
    const currentIdx = stageOrder.indexOf(currentStage);
    const targetIdx = stageOrder.indexOf(stagePart);
    if (targetIdx < currentIdx) return 'done';
    if (targetIdx === currentIdx) return 'running';
    return 'waiting';
  };

  return (
    <Card className="border-indigo-500/40 bg-slate-900/90 shadow-xl">
      <CardHeader className="border-b border-slate-800">
        <CardTitle className="text-base flex items-center justify-between text-white">
          <span className="flex items-center gap-2">
            {isRunning ? <Loader2 className="h-4 w-4 animate-spin text-indigo-400" /> : <CheckCircle2 className="h-4 w-4 text-emerald-400" />}
            Pipeline Execution Progress
          </span>
          <span className="text-xs font-normal text-slate-400">
            {isRunning ? `Currently processing: ${currentStage}` : 'All 6 Sub-stages Completed ✓'}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="py-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {sixStages.map((stage) => {
            const status = getStageStatus(stage.part);
            return (
              <div
                key={stage.key}
                className={`p-3 rounded-xl border flex items-center justify-between text-xs transition-all ${
                  status === 'running'
                    ? 'border-indigo-500 bg-indigo-500/10 text-indigo-200 shadow-md shadow-indigo-500/10'
                    : status === 'done'
                    ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
                    : 'border-slate-800 bg-slate-950/40 text-slate-500'
                }`}
              >
                <div className="flex items-center gap-2">
                  {status === 'done' ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                  ) : status === 'running' ? (
                    <Loader2 className="h-4 w-4 animate-spin text-indigo-400 shrink-0" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border border-slate-700 shrink-0" />
                  )}
                  <span className="font-medium text-slate-200">{stage.label}</span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950/60 border border-slate-800">
                  {stage.part}
                </span>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

