import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Badge } from '../common/Badge';

export function QAViolations({ violations = [] }) {
  return (
    <Card className="border-rose-500/30">
      <CardHeader>
        <CardTitle className="text-base text-rose-400 flex items-center justify-between">
          <span>PART 4: QA VIOLATIONS & WARNINGS</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 font-normal">
            {violations.length} {violations.length === 1 ? 'Issue' : 'Issues'}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {violations.length === 0 ? (
          <div className="py-6 text-center text-emerald-400 text-sm font-semibold">
            ✓ No Quality Assurance violations detected for this product.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border/80 text-textMuted uppercase font-semibold">
                  <th className="py-2.5 px-3">Field</th>
                  <th className="py-2.5 px-3">Issue</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3 text-right">Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40">
                {violations.map((v, i) => (
                  <tr key={i} className="hover:bg-slate-900/40">
                    <td className="py-3 px-3 font-bold font-mono text-textMain">{v.field}</td>
                    <td className="py-3 px-3 text-slate-300 font-medium">{v.issue}</td>
                    <td className="py-3 px-3 text-slate-400 font-mono">{v.type}</td>
                    <td className="py-3 px-3 text-right">
                      <Badge variant={v.severity === 'high' ? 'error' : v.severity === 'medium' ? 'warning' : 'outline'}>
                        {(v.severity || 'low').toUpperCase()}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
