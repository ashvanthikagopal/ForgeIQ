import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';

export function Part1Details({ details = {} }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base text-primary">PART 1: Foundation (Raw / Cleaned Input)</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <Row label="Part Description" value={details.part_desc || details.part_description || '-'} />
        <Row label="MPN" value={details.mpn || '-'} />
        <Row label="Raw Manufacturer" value={details.manufacturer || '-'} />
        <Row label="Raw Brand" value={details.brand || '-'} />
      </CardContent>
    </Card>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex flex-col sm:flex-row justify-between py-2 border-b border-border/40 last:border-0">
      <span className="text-xs font-semibold text-textMuted uppercase">{label}</span>
      <span className="text-textMain font-medium sm:text-right max-w-sm truncate">{value}</span>
    </div>
  );
}
