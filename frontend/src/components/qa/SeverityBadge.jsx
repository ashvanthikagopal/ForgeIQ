import React from 'react';
import { Badge } from '../common/Badge';

export function SeverityBadge({ severity }) {
  const sev = (severity || 'low').toLowerCase();
  if (sev === 'high') return <Badge variant="error">HIGH</Badge>;
  if (sev === 'medium') return <Badge variant="warning">MEDIUM</Badge>;
  return <Badge variant="outline">LOW</Badge>;
}
