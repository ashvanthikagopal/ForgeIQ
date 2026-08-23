import React from 'react';
import { ProductStatusBadge } from './ProductStatusBadge';
import { Button } from '../common/Button';
import { ChevronRight, ArrowUpRight } from 'lucide-react';

export function ProductRow({ product, onViewDetails }) {
  const confidenceScore = product._part3_classification_confidence || 
    (product.part4_evaluation?.average_confidence ?? 0.85);

  const confPct = Math.round((confidenceScore || 0.85) * 100);

  return (
    <tr 
      onClick={() => onViewDetails(product)}
      className="hover:bg-slate-800/50 transition-colors border-b border-slate-800/60 cursor-pointer group"
    >
      <td className="px-6 py-4">
        <span className="font-mono font-bold text-xs text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-1 rounded-md group-hover:border-indigo-500/50 transition-colors">
          {product.mpn || '-'}
        </span>
      </td>
      <td className="px-6 py-4 text-xs font-semibold text-slate-200 max-w-[180px] truncate">
        {product.manufacturer || 'Unbranded'}
      </td>
      <td className="px-6 py-4 text-xs text-slate-400 hidden md:table-cell max-w-[140px] truncate">
        {product.brand || 'Generic'}
      </td>
      <td className="px-6 py-4 text-xs text-slate-300 hidden lg:table-cell max-w-[180px] truncate font-medium">
        {product.classpath || 'Unclassified'}
      </td>
      <td className="px-6 py-4 text-xs text-slate-300 max-w-[260px] truncate">
        {product.product_title || product.invoice_desc || '-'}
      </td>
      <td className="px-6 py-4">
        <ProductStatusBadge status={product.part4_status} />
      </td>
      <td className="px-6 py-4 hidden sm:table-cell">
        <div className="flex items-center gap-2">
          <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${confPct >= 80 ? 'bg-emerald-500' : 'bg-amber-500'}`}
              style={{ width: `${confPct}%` }}
            />
          </div>
          <span className="font-mono text-[11px] text-slate-400">{confPct}%</span>
        </div>
      </td>
      <td className="px-6 py-4 text-right">
        <span className="inline-flex items-center justify-center p-1.5 rounded-lg text-slate-400 group-hover:text-white group-hover:bg-indigo-600/20 transition-all">
          <ArrowUpRight className="h-4 w-4" />
        </span>
      </td>
    </tr>
  );
}
