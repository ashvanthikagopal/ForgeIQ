import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';

export function Part3Details({ product }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base text-blue-400">PART 3: Normalization & Copy Generation</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <DescBox label="Invoice Description" value={product.invoice_desc} />
          <DescBox label="Mobile Description" value={product.mobile_desc} />
          <DescBox label="Product Title" value={product.product_title} />
        </div>

        <div className="space-y-3">
          <div>
            <span className="text-xs font-bold text-textMuted uppercase tracking-wider block mb-1">Long Description</span>
            <div className="p-3 bg-slate-900 rounded-lg border border-border text-sm text-slate-300 font-mono">
              {product.long_description || '-'}
            </div>
          </div>

          <div>
            <span className="text-xs font-bold text-textMuted uppercase tracking-wider block mb-1">Marketing Copy</span>
            <div className="p-3 bg-slate-900 rounded-lg border border-border text-sm text-slate-300">
              {product.marketing_copy || '-'}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function DescBox({ label, value }) {
  return (
    <div className="p-3 bg-slate-900 rounded-lg border border-border">
      <span className="text-xs font-semibold text-textMuted uppercase block">{label}</span>
      <span className="text-sm font-bold text-textMain mt-1 block truncate">{value || '-'}</span>
    </div>
  );
}
