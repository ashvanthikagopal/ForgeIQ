import React, { useEffect } from 'react';
import { usePipeline } from '../context/PipelineContext';
import { useQASummary } from '../hooks/useQA';
import { ErrorState } from '../components/common/ErrorState';
import { MetricCard } from '../components/dashboard/MetricCard';
import { PipelineOverview } from '../components/dashboard/PipelineOverview';
import { QAOverview } from '../components/dashboard/QAOverview';
import { PipelineProgress } from '../components/pipeline/PipelineProgress';
import { CSVUploadSection } from '../components/pipeline/CSVUploadSection';
import { Package, CheckCircle2, AlertTriangle, XCircle, Download, ExternalLink, ShieldCheck } from 'lucide-react';
import { Button } from '../components/common/Button';
import { downloadResults } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const { pipelineState, isRunning, startPipeline, refreshStatus, backendConnected } = usePipeline();
  const { summary, loading: summaryLoading, error: summaryError, refetch } = useQASummary();
  const navigate = useNavigate();

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  const handleStartPipeline = async (file) => {
    try {
      await startPipeline(file);
      refetch();
    } catch (err) {
      console.error('Failed to run pipeline:', err);
    }
  };

  if (!backendConnected) {
    return (
      <div className="space-y-6 max-w-4xl">
        <ErrorState
          title="Backend API Offline"
          message="Unable to connect to the ForgeIQ Python backend server on http://localhost:8000. Please ensure the Python FastAPI backend process is running."
          onRetry={refreshStatus}
        />
      </div>
    );
  }

  const data = summary || {
    total_products: pipelineState.part4_count || 1000,
    passed: 0,
    review: pipelineState.part4_count || 1000,
    failed: 0,
    high_severity: 0
  };

  const total = data.total_products || 1000;
  const passedPct = total > 0 ? (data.passed / total * 100).toFixed(1) : '0.0';

  return (
    <div className="space-y-8 pb-10">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">ForgeIQ</h1>
          <p className="text-sm font-medium text-slate-400 mt-1">
            Product Content Enrichment & Quality Assurance Platform
          </p>
          <p className="text-xs text-indigo-400 font-mono mt-0.5">
            Enrich. Normalize. Validate. Deliver.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={() => navigate('/qa')}
            className="border-slate-700 hover:bg-slate-800 text-slate-200"
          >
            <ShieldCheck className="h-4 w-4 mr-2 text-indigo-400" />
            QA Dashboard
          </Button>
          <Button
            variant="outline"
            onClick={() => downloadResults('csv')}
            className="border-slate-700 hover:bg-slate-800 text-slate-200"
          >
            <Download className="h-4 w-4 mr-2 text-emerald-400" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* CSV Upload & Sample Dataset Selector Section */}
      <CSVUploadSection onStartPipeline={handleStartPipeline} isRunning={isRunning} />

      {/* Live Pipeline Progress Indicator when running */}
      {(isRunning || pipelineState.status === 'completed') && (
        <PipelineProgress isRunning={isRunning} currentStage={pipelineState.current_stage} />
      )}

      {/* 4 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="PRODUCTS PROCESSED"
          value={data.total_products.toLocaleString()}
          subtitle="Catalog total"
          icon={Package}
          color="text-indigo-400"
          bg="bg-indigo-500/10"
        />
        <MetricCard
          title="SUCCESSFULLY PROCESSED"
          value={data.passed.toLocaleString()}
          subtitle={`${passedPct}% QA pass rate`}
          icon={CheckCircle2}
          color="text-emerald-400"
          bg="bg-emerald-500/10"
        />
        <MetricCard
          title="NEEDS REVIEW"
          value={data.review.toLocaleString()}
          subtitle="Review queue items"
          icon={AlertTriangle}
          color="text-amber-400"
          bg="bg-amber-500/10"
        />
        <MetricCard
          title="QA PASS RATE"
          value={`${passedPct}%`}
          subtitle="Quality assurance score"
          icon={ShieldCheck}
          color="text-emerald-400"
          bg="bg-emerald-500/10"
        />
      </div>

      {/* Quick Action Navigation Bar after Pipeline Run */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/40 border border-slate-800">
        <div className="text-xs text-slate-400">
          <span className="font-semibold text-slate-200">Catalog Actions:</span> Direct access to QA review queue and export features.
        </div>
        <div className="flex items-center gap-3">
          <Button size="sm" variant="outline" onClick={() => navigate('/qa')} className="border-amber-500/40 text-amber-300 hover:bg-amber-500/10">
            <AlertTriangle className="h-3.5 w-3.5 mr-1.5" /> Review Queue ({data.review})
          </Button>
          <Button size="sm" onClick={() => downloadResults('csv')} className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold">
            <Download className="h-3.5 w-3.5 mr-1.5" /> Download Enriched CSV
          </Button>
        </div>
      </div>

      {/* Pipeline Status */}
      <PipelineOverview pipelineState={pipelineState} isRunning={isRunning} />

      {/* QA Breakdown Overview */}
      <QAOverview summary={data} />
    </div>
  );
}
