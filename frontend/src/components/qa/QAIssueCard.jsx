import React from 'react';
import { Card, CardContent } from '../common/Card';
import { Button } from '../common/Button';
import { SeverityBadge } from './SeverityBadge';
import { AlertTriangle, ChevronRight } from 'lucide-react';
import { formatConfidence } from '../../utils/formatters';

export function QAIssueCard({ item, onViewProduct }) {
  const violations = item.violations || [];
  const reviewReasons = item.review_reasons || [];

  return (
    <Card className="hover:border-slate-700 transition-all border-amber-500/20 bg-slate-900/90">
      <CardContent className="p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-3">
            <h3 className="font-extrabold font-mono text-lg text-textMain">{item.mpn || 'Unknown MPN'}</h3>
            <SeverityBadge severity={item.highest_severity} />
          </div>

          <p className="text-xs text-textMuted font-medium">{item.manufacturer || 'Unknown Manufacturer'}</p>

          {/* List issues / violations */}
          <div className="space-y-1 pt-1">
            {violations.map((v, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-amber-300">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-400 flex-shrink-0" />
                <span className="font-semibold uppercase font-mono text-[11px] text-textMuted">{v.field}:</span>
                <span>{v.issue}</span>
              </div>
            ))}
            {reviewReasons.map((r, i) => (
              <div key={`reason-${i}`} className="flex items-center gap-2 text-xs text-slate-400">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-400 flex-shrink-0" />
                <span>{r}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between md:flex-col md:items-end w-full md:w-auto pt-3 md:pt-0 border-t md:border-0 border-border">
          <div className="text-xs text-textMuted font-mono mb-2">
            Confidence: <span className="font-bold text-textMain">{formatConfidence(item.confidence)}</span>
          </div>
          <Button onClick={() => onViewProduct(item)}>
            View Product <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
