import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Badge } from '../common/Badge';

export function Part4Details({ product }) {
  const p4 = product._part4 || {};
  const confidenceMap = product.part4_confidence || p4.confidence || {};
  const enrichedFields = p4.enriched_fields || [];
  const missingBefore = p4.missing_before_enrichment || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base text-emerald-400">PART 4: Enrichment & Confidence</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-3 bg-slate-900 rounded-lg border border-border">
            <span className="text-xs font-semibold text-textMuted uppercase block">Enrichment Status</span>
            <span className="text-sm font-bold text-textMain">{p4.status || 'Processed'}</span>
          </div>

          <div className="p-3 bg-slate-900 rounded-lg border border-border">
            <span className="text-xs font-semibold text-textMuted uppercase block">Missing Before Enrichment</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {missingBefore.length === 0 ? (
                <span className="text-xs text-slate-400">None</span>
              ) : (
                missingBefore.map((attr) => (
                  <Badge key={attr} variant="outline" className="text-xs">{attr}</Badge>
                ))
              )}
            </div>
          </div>
        </div>

        {Object.keys(confidenceMap).length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-textMuted uppercase mb-2">Attribute Confidence Scores</h4>
            <div className="space-y-2">
              {Object.entries(confidenceMap).map(([field, item]) => (
                <div key={field} className="p-2.5 bg-slate-900 rounded-lg border border-border/60 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-bold text-textMain uppercase">{field}</span>
                    {item.reason && <span className="text-slate-400 block text-[11px]">{item.reason}</span>}
                  </div>
                  <span className="font-mono font-bold text-emerald-400">{Math.round((item.score || 0) * 100)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
