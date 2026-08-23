import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';

export function ProductInformation({ product }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">PRODUCT INFORMATION</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <InfoField label="MPN" value={product.mpn} />
        <InfoField label="Manufacturer" value={product.manufacturer} />
        <InfoField label="Brand" value={product.brand} />
        <InfoField label="Classpath" value={product.classpath} />
      </CardContent>
    </Card>
  );
}

function InfoField({ label, value }) {
  return (
    <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
      <span className="text-xs font-bold text-textMuted uppercase tracking-wider block">{label}</span>
      <span className="text-sm font-semibold text-textMain font-mono mt-1 block truncate">{value || '-'}</span>
    </div>
  );
}
