import React from 'react';
import { usePipeline } from '../context/PipelineContext';
import { PipelineFlow } from '../components/pipeline/PipelineFlow';
import { PipelineProgress } from '../components/pipeline/PipelineProgress';
import { CSVUploadSection } from '../components/pipeline/CSVUploadSection';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { RefreshCw } from 'lucide-react';

export default function Pipeline() {
  const { pipelineState, isRunning, startPipeline, refreshStatus } = usePipeline();

  const handleStartPipeline = async (file) => {
    try {
      await startPipeline(file);
    } catch (err) {
      console.error('Failed to run pipeline:', err);
    }
  };

  return (
    <div className="space-y-8 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">Pipeline Execution & Monitoring</h1>
          <p className="text-slate-400 text-sm mt-1">
            Upload custom CSV or choose sample dataset to trigger stage-by-stage enrichment.
          </p>
        </div>

        <div className="flex gap-3">
          <Button variant="outline" size="sm" onClick={refreshStatus} className="border-slate-700 hover:bg-slate-800">
            <RefreshCw className="h-4 w-4 mr-1.5" /> Refresh Status
          </Button>
        </div>
      </div>

      {/* CSV Upload & Sample Dataset Selector */}
      <CSVUploadSection onStartPipeline={handleStartPipeline} isRunning={isRunning} />

      {/* Live Pipeline Progress Indicator */}
      {(isRunning || pipelineState.status === 'completed') && (
        <PipelineProgress isRunning={isRunning} currentStage={pipelineState.current_stage} />
      )}

      {/* Main visual pipeline flow */}
      <PipelineFlow status={pipelineState} isRunning={isRunning} />

      {/* Architecture Summary */}
      <Card className="bg-slate-900/60 border-slate-800">
        <CardHeader>
          <CardTitle className="text-base text-slate-300">FORGEIQ PIPELINE ARCHITECTURE</CardTitle>
        </CardHeader>
        <CardContent className="text-xs text-slate-400 space-y-2 font-mono">
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-slate-300">
            Input CSV → [PART 1: Input Analysis & Lookups] → [PART 2: Classification & Attribute Extraction] → [PART 3: Normalization & Descriptions] → [PART 4: Enrichment & QA] → Enriched Catalog
          </div>
          <p className="text-slate-400 font-sans text-xs">
            The built-in 1,000-row catalog serves as model reference data to classify, normalize, generate descriptions, and enforce quality assurance rules on custom user CSV uploads.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

