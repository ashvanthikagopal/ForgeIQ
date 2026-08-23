import React from 'react';
import { ArrowLeft } from 'lucide-react';
import { Button } from '../common/Button';
import { ProductStatusBadge } from '../products/ProductStatusBadge';

export function ProductHeader({ product, onBack }) {
  return (
    <div className="space-y-4">
      <Button variant="ghost" className="pl-0 text-textMuted hover:text-textMain" onClick={onBack}>
        <ArrowLeft className="h-4 w-4 mr-2" /> Back to Catalog
      </Button>

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-border">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight font-mono text-textMain">{product.mpn || 'Unknown MPN'}</h1>
            <ProductStatusBadge status={product.part4_status} />
          </div>
          <p className="text-slate-400 text-sm mt-1">{product.manufacturer || 'Unknown Manufacturer'}</p>
        </div>

        <div className="flex items-center gap-4 bg-slate-900 px-4 py-2 rounded-xl border border-border">
          <div className="text-right">
            <span className="text-xs text-textMuted uppercase block">Class Path</span>
            <span className="text-sm font-semibold text-textMain">{product.classpath || 'Not Classified'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
