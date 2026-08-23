import React from 'react';
import { QAIssueCard } from './QAIssueCard';

export function QAReviewList({ reviews = [], onViewProduct }) {
  if (reviews.length === 0) {
    return (
      <div className="text-center p-12 bg-card border border-border rounded-xl">
        <p className="text-textMuted font-medium text-base">No products currently require review.</p>
        <p className="text-xs text-slate-500 mt-1">All products meet Quality Assurance criteria.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {reviews.map((item, idx) => (
        <QAIssueCard key={item.id || item.mpn || idx} item={item} onViewProduct={onViewProduct} />
      ))}
    </div>
  );
}
