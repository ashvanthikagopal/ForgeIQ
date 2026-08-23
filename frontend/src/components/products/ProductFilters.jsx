import React from 'react';
import { Search, RotateCcw } from 'lucide-react';
import { Button } from '../common/Button';

export function ProductFilters({
  searchTerm,
  onSearchChange,
  statusFilter,
  onStatusChange,
  manufacturerFilter,
  onManufacturerChange,
  classpathFilter,
  onClasspathChange,
  reviewOnly,
  onReviewOnlyChange,
  manufacturers = [],
  classpaths = [],
  onClearFilters
}) {
  return (
    <div className="p-4 bg-card border border-border rounded-xl space-y-4 shadow-sm">
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
        {/* Search Input */}
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-textMuted" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search MPN, Manufacturer, Brand, Title..."
            className="w-full bg-slate-900 border border-border rounded-lg pl-10 pr-4 py-2 text-sm text-textMain focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => onStatusChange(e.target.value)}
            className="bg-slate-900 border border-border rounded-lg px-3 py-2 text-sm text-textMain focus:outline-none focus:border-primary"
          >
            <option value="all">All Statuses</option>
            <option value="PASSED">Passed</option>
            <option value="REVIEW">Review</option>
            <option value="FAILED">Failed</option>
          </select>

          {/* Manufacturer Filter */}
          {manufacturers.length > 0 && (
            <select
              value={manufacturerFilter}
              onChange={(e) => onManufacturerChange(e.target.value)}
              className="bg-slate-900 border border-border rounded-lg px-3 py-2 text-sm text-textMain focus:outline-none focus:border-primary max-w-[180px] truncate"
            >
              <option value="all">All Manufacturers</option>
              {manufacturers.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          )}

          {/* Classpath Filter */}
          {classpaths.length > 0 && (
            <select
              value={classpathFilter}
              onChange={(e) => onClasspathChange(e.target.value)}
              className="bg-slate-900 border border-border rounded-lg px-3 py-2 text-sm text-textMain focus:outline-none focus:border-primary max-w-[180px] truncate"
            >
              <option value="all">All Classpaths</option>
              {classpaths.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          )}

          {/* Review Only Toggle */}
          <label className="flex items-center gap-2 text-xs font-semibold text-textMuted cursor-pointer select-none bg-slate-900 border border-border rounded-lg px-3 py-2 hover:text-textMain">
            <input
              type="checkbox"
              checked={reviewOnly}
              onChange={(e) => onReviewOnlyChange(e.target.checked)}
              className="rounded bg-slate-950 border-border text-primary focus:ring-primary h-4 w-4"
            />
            Needs Review Only
          </label>

          <Button variant="ghost" size="sm" onClick={onClearFilters} className="text-textMuted hover:text-textMain">
            <RotateCcw className="h-4 w-4 mr-1" /> Clear
          </Button>
        </div>
      </div>
    </div>
  );
}
