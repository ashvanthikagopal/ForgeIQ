import React from 'react';
import { Badge } from '../common/Badge';

export function ProductStatusBadge({ status }) {
  if (!status) return <Badge variant="outline">UNKNOWN</Badge>;
  const s = status.toUpperCase();
  if (s === 'PASSED') {
    return (
      <Badge variant="success">
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> PASSED
      </Badge>
    );
  }
  if (s === 'REVIEW') {
    return (
      <Badge variant="warning">
        <span className="h-1.5 w-1.5 rounded-full bg-amber-400 animate-pulse" /> REVIEW
      </Badge>
    );
  }
  if (s === 'FAILED') {
    return (
      <Badge variant="error">
        <span className="h-1.5 w-1.5 rounded-full bg-rose-400" /> FAILED
      </Badge>
    );
  }
  return <Badge variant="outline">{s}</Badge>;
}
