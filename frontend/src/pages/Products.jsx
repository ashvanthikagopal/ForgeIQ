import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProducts } from '../hooks/useProducts';
import { ProductTable } from '../components/products/ProductTable';
import { ProductFilters } from '../components/products/ProductFilters';
import { ErrorState } from '../components/common/ErrorState';
import { Loader2 } from 'lucide-react';

export default function Products() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [manufacturerFilter, setManufacturerFilter] = useState('all');
  const [classpathFilter, setClasspathFilter] = useState('all');
  const [reviewOnly, setReviewOnly] = useState(false);
  const [page, setPage] = useState(1);

  // Combine query params
  const params = {
    page,
    limit: 20,
    q: searchTerm || undefined,
    status: statusFilter !== 'all' ? statusFilter : undefined,
    manufacturer: manufacturerFilter !== 'all' ? manufacturerFilter : undefined,
    classpath: classpathFilter !== 'all' ? classpathFilter : undefined,
    needs_review: reviewOnly ? true : undefined
  };

  const { products, total, total_pages, manufacturers, classpaths, loading, error } = useProducts(params);

  const handleClearFilters = () => {
    setSearchTerm('');
    setStatusFilter('all');
    setManufacturerFilter('all');
    setClasspathFilter('all');
    setReviewOnly(false);
    setPage(1);
  };

  if (error) {
    return (
      <div className="space-y-6 max-w-4xl">
        <h1 className="text-3xl font-bold tracking-tight text-white">Products Catalog</h1>
        <ErrorState
          title="Failed to Load Products"
          message={error.message || "An error occurred while fetching products from backend."}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">Products Catalog</h1>
          <p className="text-slate-400 text-sm mt-1">
            Browse and inspect all processed product catalog records ({total} total products).
          </p>
        </div>
      </div>

      <ProductFilters
        searchTerm={searchTerm}
        onSearchChange={(val) => { setSearchTerm(val); setPage(1); }}
        statusFilter={statusFilter}
        onStatusChange={(val) => { setStatusFilter(val); setPage(1); }}
        manufacturerFilter={manufacturerFilter}
        onManufacturerChange={(val) => { setManufacturerFilter(val); setPage(1); }}
        classpathFilter={classpathFilter}
        onClasspathChange={(val) => { setClasspathFilter(val); setPage(1); }}
        reviewOnly={reviewOnly}
        onReviewOnlyChange={(val) => { setReviewOnly(val); setPage(1); }}
        manufacturers={manufacturers}
        classpaths={classpaths}
        onClearFilters={handleClearFilters}
      />

      {loading ? (
        <div className="flex h-64 items-center justify-center bg-card border border-border rounded-xl">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        </div>
      ) : (
        <ProductTable
          products={products}
          total={total}
          page={page}
          totalPages={total_pages}
          onPageChange={setPage}
          onViewDetails={(prod) => navigate(`/products/${prod.id || prod.mpn}`)}
        />
      )}
    </div>
  );
}
