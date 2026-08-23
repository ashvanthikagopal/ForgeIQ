import React from 'react';
import { useQASummary } from '../hooks/useQA';
import { usePipeline } from '../context/PipelineContext';
import { QAStatusChart } from '../components/analytics/QAStatusChart';
import { PipelineChart } from '../components/analytics/PipelineChart';
import { SeverityChart } from '../components/analytics/SeverityChart';
import { ReviewReasonsChart } from '../components/analytics/ReviewReasonsChart';
import { ErrorState } from '../components/common/ErrorState';
import { Loader2 } from 'lucide-react';

export default function Analytics() {
  const { summary, loading, error, refetch } = useQASummary();
  const { pipelineState } = usePipeline();

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="h-10 w-10 animate-spin text-indigo-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6 max-w-4xl">
        <h1 className="text-3xl font-bold tracking-tight text-white">Analytics</h1>
        <ErrorState
          title="Failed to Load Analytics"
          message={error.message || "An error occurred while fetching analytics from backend."}
          onRetry={refetch}
        />
      </div>
    );
  }

  const data = summary || {};

  return (
    <div className="space-y-8 pb-10">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white">Analytics & Quality Insights</h1>
        <p className="text-slate-400 text-sm mt-1">
          Catalog Quality Assurance metrics, severity breakdown, and pipeline throughput.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <QAStatusChart
          passed={data.passed || 0}
          review={data.review || 0}
          failed={data.failed || 0}
        />

        <PipelineChart
          part1={pipelineState.part1_count || 1000}
          part2={pipelineState.part2_count || 1000}
          part3={pipelineState.part3_count || 1000}
          part4={pipelineState.part4_count || 1000}
        />

        <SeverityChart
          high={data.high_severity || 0}
          medium={data.medium_severity || 0}
          low={data.low_severity || 0}
        />

        <ReviewReasonsChart
          reasons={data.reasons || []}
        />
      </div>
    </div>
  );
}
