import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { formatConfidence } from '../../utils/formatters';

export function Part2Details({ details = {}, product }) {
  const confidence = details.classification_confidence ?? product._part3_classification_confidence ?? 0;
  const attributes = details.attributes || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base text-indigo-400">PART 2: Classification & Attributes</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-3 bg-slate-900 rounded-lg border border-border">
            <span className="text-xs text-textMuted uppercase font-semibold block">Class Path</span>
            <span className="text-sm font-bold text-textMain font-mono">{details.classpath || product.classpath || 'None'}</span>
          </div>

          <div className="p-3 bg-slate-900 rounded-lg border border-border">
            <span className="text-xs text-textMuted uppercase font-semibold block">Classification Confidence</span>
            <span className="text-sm font-bold text-emerald-400 font-mono">{formatConfidence(confidence)}</span>
          </div>
        </div>

        {details.classification_reasoning && (
          <div className="p-3 bg-slate-900/60 rounded-lg border border-border text-xs text-slate-300">
            <span className="font-bold text-textMuted block mb-1">Reasoning:</span>
            {details.classification_reasoning}
          </div>
        )}

        {attributes.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-textMuted uppercase mb-2">Extracted Attributes</h4>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead>
                  <tr className="border-b border-border text-textMuted">
                    <th className="py-2">Attribute</th>
                    <th className="py-2">Value</th>
                    <th className="py-2 text-right">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {attributes.map((attr, idx) => (
                    <tr key={idx}>
                      <td className="py-2 font-medium text-slate-300">{attr.attribute}</td>
                      <td className="py-2 text-textMain font-mono">{attr.value}</td>
                      <td className="py-2 text-right font-mono text-emerald-400">{formatConfidence(attr.confidence)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
