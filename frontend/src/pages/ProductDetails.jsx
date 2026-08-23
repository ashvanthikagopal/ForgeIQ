import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProductDetails } from '../hooks/useProducts';
import { ProductHeader } from '../components/product/ProductHeader';
import { ProductIntelligenceCard } from '../components/product/ProductIntelligenceCard';
import { Part1Details } from '../components/product/Part1Details';
import { Part2Details } from '../components/product/Part2Details';
import { Part3Details } from '../components/product/Part3Details';
import { Part4Details } from '../components/product/Part4Details';
import { QAViolations } from '../components/product/QAViolations';
import { ErrorState } from '../components/common/ErrorState';
import { Loader2 } from 'lucide-react';

export default function ProductDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { product, loading, error, refetch } = useProductDetails(id);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="h-10 w-10 animate-spin text-indigo-500" />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="space-y-6 max-w-4xl">
        <ErrorState
          title="Product Not Found"
          message={error?.message || `Unable to load details for product ID/MPN: ${id}`}
          onRetry={() => navigate('/products')}
        />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      <ProductHeader product={product} onBack={() => navigate('/products')} />

      {/* Main Product Intelligence Card */}
      <ProductIntelligenceCard product={product} onUpdate={refetch} />

      {/* Grid of details for Stages 1 to 4 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Part1Details details={product.part1_details} />
        <Part2Details details={product.part2_details} product={product} />
        <div className="lg:col-span-2">
          <Part3Details product={product} />
        </div>
        <Part4Details product={product} />
        <div className="lg:col-span-1">
          <QAViolations violations={product.part4_violations} />
        </div>
      </div>
    </div>
  );
}
