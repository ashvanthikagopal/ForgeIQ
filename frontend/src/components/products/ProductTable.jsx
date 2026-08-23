import React from 'react';
import { ProductRow } from './ProductRow';
import { Button } from '../common/Button';

export function ProductTable({ products = [], total = 0, page = 1, totalPages = 1, onPageChange, onViewDetails }) {
  return (
    <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden flex flex-col">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-900 border-b border-border text-xs uppercase tracking-wider text-textMuted font-semibold">
              <th className="px-6 py-4">MPN</th>
              <th className="px-6 py-4">Manufacturer</th>
              <th className="px-6 py-4 hidden md:table-cell">Brand</th>
              <th className="px-6 py-4 hidden lg:table-cell">Classpath</th>
              <th className="px-6 py-4">Product Title</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4 hidden sm:table-cell">Confidence</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60">
            {products.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-6 py-12 text-center text-textMuted font-medium">
                  No products match the selected criteria.
                </td>
              </tr>
            ) : (
              products.map((p, i) => (
                <ProductRow key={p.id || i} product={p} onViewDetails={onViewDetails} />
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="px-6 py-4 border-t border-border flex items-center justify-between bg-slate-900/50 text-sm">
          <div className="text-textMuted">
            Showing Page <span className="font-bold text-textMain">{page}</span> of <span className="font-bold text-textMain">{totalPages}</span> ({total} total products)
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
