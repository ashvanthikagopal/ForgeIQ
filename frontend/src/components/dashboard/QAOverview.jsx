import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

export function QAOverview({ summary }) {
  if (!summary) return null;

  const total = summary.total_products || 1;
  const passedPct = Math.round((summary.passed / total) * 100);
  const reviewPct = Math.round((summary.review / total) * 100);
  const failedPct = Math.round((summary.failed / total) * 100);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">QA DISTRIBUTION OVERVIEW</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Progress Bar */}
        <div className="w-full bg-slate-800 rounded-full h-4 overflow-hidden flex shadow-inner">
          <div style={{ width: `${passedPct}%` }} className="bg-emerald-500 transition-all duration-500" title={`Passed: ${passedPct}%`} />
          <div style={{ width: `${reviewPct}%` }} className="bg-amber-500 transition-all duration-500" title={`Review: ${reviewPct}%`} />
          <div style={{ width: `${failedPct}%` }} className="bg-rose-500 transition-all duration-500" title={`Failed: ${failedPct}%`} />
        </div>

        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            <div className="flex items-center justify-center gap-1 text-emerald-400 text-sm font-semibold">
              <CheckCircle className="h-4 w-4" /> Passed
            </div>
            <div className="text-2xl font-bold mt-1 text-textMain">{summary.passed}</div>
            <div className="text-xs text-textMuted">{passedPct}%</div>
          </div>

          <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
            <div className="flex items-center justify-center gap-1 text-amber-400 text-sm font-semibold">
              <AlertTriangle className="h-4 w-4" /> Review
            </div>
            <div className="text-2xl font-bold mt-1 text-textMain">{summary.review}</div>
            <div className="text-xs text-textMuted">{reviewPct}%</div>
          </div>

          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20">
            <div className="flex items-center justify-center gap-1 text-rose-400 text-sm font-semibold">
              <XCircle className="h-4 w-4" /> Failed
            </div>
            <div className="text-2xl font-bold mt-1 text-textMain">{summary.failed}</div>
            <div className="text-xs text-textMuted">{failedPct}%</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
