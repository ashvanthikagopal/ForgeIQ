import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQAReviews } from '../hooks/useQA';
import { getProduct, approveReview, rejectReview } from '../api/forgeiqApi';
import { ErrorState } from '../components/common/ErrorState';
import { Button } from '../components/common/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Loader2, AlertTriangle, CheckCircle2, ChevronRight, UserCheck, UserX, CheckSquare, Square, XSquare } from 'lucide-react';

export default function QAReview() {
  const navigate = useNavigate();
  const [severityFilter, setSeverityFilter] = useState('all');
  const [selectedItemId, setSelectedItemId] = useState(null);
  const [selectedProductDetails, setSelectedProductDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [actionMessage, setActionMessage] = useState(null);

  // Bulk Selection State
  const [selectedIds, setSelectedIds] = useState([]);
  const [isBulkProcessing, setIsBulkProcessing] = useState(false);

  const { reviews, loading, error, refetch } = useQAReviews({
    severity: severityFilter !== 'all' ? severityFilter : undefined
  });

  useEffect(() => {
    if (reviews) {
      if (reviews.length === 0) {
        setSelectedItemId(null);
        setSelectedProductDetails(null);
      } else if (!selectedItemId || !reviews.some((r) => (r.id || r.mpn) === selectedItemId)) {
        setSelectedItemId(reviews[0].id || reviews[0].mpn);
      }
    }
  }, [reviews, selectedItemId]);

  useEffect(() => {
    if (selectedItemId) {
      setLoadingDetails(true);
      getProduct(selectedItemId)
        .then((res) => {
          setSelectedProductDetails(res);
          setLoadingDetails(false);
        })
        .catch(() => {
          setLoadingDetails(false);
        });
    }
  }, [selectedItemId]);

  // Handle Select All / Deselect All
  const handleToggleSelectAll = () => {
    if (selectedIds.length === reviews.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(reviews.map((r) => r.id || r.mpn));
    }
  };

  // Handle Individual Checkbox Toggle
  const handleToggleSelectItem = (id, e) => {
    e.stopPropagation();
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter((item) => item !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  // Bulk Approve
  const handleBulkApprove = async () => {
    if (selectedIds.length === 0) return;
    if (!window.confirm(`Approve all ${selectedIds.length} selected products?`)) return;

    setIsBulkProcessing(true);
    try {
      await Promise.all(selectedIds.map((id) => approveReview(id)));
      setActionMessage(`Successfully approved ${selectedIds.length} products!`);
      setSelectedIds([]);
      setSelectedItemId(null);
      setSelectedProductDetails(null);
      setTimeout(() => setActionMessage(null), 4000);
      await refetch();
    } catch (err) {
      alert(err.message || 'Failed to approve selected products');
    } finally {
      setIsBulkProcessing(false);
    }
  };

  // Bulk Reject
  const handleBulkReject = async () => {
    if (selectedIds.length === 0) return;
    if (!window.confirm(`Reject all ${selectedIds.length} selected products?`)) return;

    setIsBulkProcessing(true);
    try {
      await Promise.all(selectedIds.map((id) => rejectReview(id)));
      setActionMessage(`Rejected ${selectedIds.length} products.`);
      setSelectedIds([]);
      setSelectedItemId(null);
      setSelectedProductDetails(null);
      setTimeout(() => setActionMessage(null), 4000);
      await refetch();
    } catch (err) {
      alert(err.message || 'Failed to reject selected products');
    } finally {
      setIsBulkProcessing(false);
    }
  };

  // Single Approve
  const handleApprove = async () => {
    if (!selectedItemId) return;
    try {
      await approveReview(selectedItemId);
      setActionMessage(`Product ${selectedItemId} approved successfully!`);
      setTimeout(() => setActionMessage(null), 3000);
      refetch();
    } catch (err) {
      alert(err.message || 'Failed to approve product');
    }
  };

  // Single Reject
  const handleReject = async () => {
    if (!selectedItemId) return;
    try {
      await rejectReview(selectedItemId);
      setActionMessage(`Product ${selectedItemId} rejected.`);
      setTimeout(() => setActionMessage(null), 3000);
      refetch();
    } catch (err) {
      alert(err.message || 'Failed to reject product');
    }
  };

  if (error) {
    return (
      <div className="space-y-6 max-w-4xl">
        <h1 className="text-3xl font-bold tracking-tight text-white">Human Review Queue</h1>
        <ErrorState
          title="Failed to Load QA Review Items"
          message={error.message || 'An error occurred while fetching QA review queue.'}
          onRetry={refetch}
        />
      </div>
    );
  }

  const allSelected = reviews.length > 0 && selectedIds.length === reviews.length;

  return (
    <div className="space-y-6 pb-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">Human-in-the-Loop Review Workspace</h1>
          <p className="text-slate-400 text-sm mt-1">
            Audit, verify, bulk approve, or bulk reject products flagged with QA violations or missing attributes.
          </p>
        </div>

        {/* Severity Filter Buttons */}
        <div className="flex flex-wrap gap-2 bg-slate-900 p-1.5 rounded-xl border border-slate-800">
          {['all', 'high', 'medium', 'low'].map((sev) => (
            <button
              key={sev}
              onClick={() => {
                setSeverityFilter(sev);
                setSelectedItemId(null);
                setSelectedIds([]);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-colors ${
                severityFilter === sev
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {sev === 'all' ? 'All Severities' : `${sev} Severity`}
            </button>
          ))}
        </div>
      </div>

      {actionMessage && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 font-semibold text-xs flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4" /> {actionMessage}
        </div>
      )}

      {/* Bulk Action Bar */}
      {reviews.length > 0 && (
        <div className="bg-slate-900/90 border border-indigo-500/30 p-3.5 rounded-2xl flex flex-wrap items-center justify-between gap-4 shadow-xl backdrop-blur-md">
          <div className="flex items-center gap-3">
            <button
              onClick={handleToggleSelectAll}
              className="flex items-center gap-2 text-xs font-bold text-slate-200 hover:text-white bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 transition-colors"
            >
              {allSelected ? (
                <CheckSquare className="h-4 w-4 text-indigo-400" />
              ) : selectedIds.length > 0 ? (
                <CheckSquare className="h-4 w-4 text-indigo-400/60" />
              ) : (
                <Square className="h-4 w-4 text-slate-500" />
              )}
              {allSelected ? 'Deselect All' : `Select All (${reviews.length})`}
            </button>

            <span className="text-xs font-mono font-semibold text-indigo-300">
              {selectedIds.length} of {reviews.length} selected
            </span>
          </div>

          <div className="flex items-center gap-3">
            <Button
              size="sm"
              onClick={handleBulkReject}
              disabled={selectedIds.length === 0 || isBulkProcessing}
              className="bg-rose-600/20 hover:bg-rose-600 text-rose-300 hover:text-white border border-rose-500/40 text-xs font-bold px-4 py-2 flex items-center gap-1.5"
            >
              {isBulkProcessing ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <UserX className="h-3.5 w-3.5" />
              )}
              Reject Selected ({selectedIds.length})
            </Button>

            <Button
              size="sm"
              onClick={handleBulkApprove}
              disabled={selectedIds.length === 0 || isBulkProcessing}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs px-5 py-2 flex items-center gap-1.5 shadow-md shadow-emerald-600/30"
            >
              {isBulkProcessing ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <UserCheck className="h-3.5 w-3.5" />
              )}
              Approve Selected ({selectedIds.length})
            </Button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex h-64 items-center justify-center bg-card border border-border rounded-xl">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
        </div>
      ) : (
        /* Split-Screen Review Experience */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Panel: Review Items List */}
          <div className="lg:col-span-5 space-y-3 max-h-[750px] overflow-y-auto pr-1">
            {reviews.length === 0 ? (
              <div className="p-8 text-center bg-slate-900/60 border border-slate-800 rounded-xl text-slate-400 text-sm">
                No review queue items found for current filter. All items passed!
              </div>
            ) : (
              reviews.map((item) => {
                const itemId = item.id || item.mpn;
                const isSelected = itemId === selectedItemId;
                const isChecked = selectedIds.includes(itemId);

                return (
                  <div
                    key={itemId}
                    onClick={() => setSelectedItemId(itemId)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-indigo-600/15 border-indigo-500/50 shadow-lg shadow-indigo-500/10'
                        : isChecked
                        ? 'bg-slate-900/90 border-indigo-500/30'
                        : 'bg-slate-900/60 border-slate-800 hover:bg-slate-800/40'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <button
                          onClick={(e) => handleToggleSelectItem(itemId, e)}
                          className="text-slate-400 hover:text-indigo-400 focus:outline-none"
                        >
                          {isChecked ? (
                            <CheckSquare className="h-4 w-4 text-indigo-400 fill-indigo-400/20" />
                          ) : (
                            <Square className="h-4 w-4 text-slate-600 hover:text-slate-400" />
                          )}
                        </button>
                        <span className="font-mono font-bold text-sm text-indigo-300">{item.mpn || item.id}</span>
                      </div>

                      <Badge variant={item.highest_severity === 'high' ? 'danger' : 'warning'}>
                        {item.highest_severity?.toUpperCase()} SEVERITY
                      </Badge>
                    </div>

                    <div className="mt-2 text-xs text-slate-400 space-y-1 pl-6">
                      <p><strong className="text-slate-300">Mfg:</strong> {item.manufacturer || 'Unbranded'}</p>
                      <p><strong className="text-slate-300">Issues:</strong> {item.issue_count} QA flags</p>
                    </div>

                    <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400 pl-6">
                      <span className="font-mono text-emerald-400">Conf: {((item.confidence || 0.8) * 100).toFixed(0)}%</span>
                      <span className="text-indigo-400 font-semibold flex items-center gap-1">
                        Inspect <ChevronRight className="h-3 w-3" />
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Right Panel: Selected Item Deep Audit & Actions */}
          <div className="lg:col-span-7">
            {loadingDetails ? (
              <div className="flex h-96 items-center justify-center bg-slate-900/60 border border-slate-800 rounded-xl">
                <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
              </div>
            ) : selectedProductDetails ? (
              <Card className="bg-slate-900/60 border-slate-800">
                <CardHeader className="border-b border-slate-800 flex flex-row items-center justify-between">
                  <div>
                    <CardTitle className="text-lg font-mono text-white">
                      AUDIT: {selectedProductDetails.mpn}
                    </CardTitle>
                    <p className="text-xs text-slate-400 mt-0.5">{selectedProductDetails.product_title || 'Industrial Product'}</p>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => navigate(`/products/${selectedProductDetails.id || selectedProductDetails.mpn}`)}
                    className="text-xs border-slate-700"
                  >
                    Full Details Page
                  </Button>
                </CardHeader>

                <CardContent className="p-6 space-y-6">
                  {/* QA Violations Summary */}
                  <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl space-y-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" /> REASON FOR HUMAN REVIEW
                    </h4>
                    <ul className="text-xs text-slate-300 space-y-1 list-disc pl-4">
                      {selectedProductDetails.part4_violations?.map((v, i) => (
                        <li key={i}>
                          <strong className="text-amber-300 font-mono">{v.field || 'General'}:</strong> {v.issue || v.message || 'QA check flagged'}
                        </li>
                      )) || <li>Flagged due to missing brand or unverified source credentials.</li>}
                    </ul>
                  </div>

                  {/* Product Key Metadata */}
                  <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                    <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                      <span className="text-slate-400 block text-[10px]">MANUFACTURER</span>
                      <span className="text-slate-200 font-bold">{selectedProductDetails.manufacturer || 'Unbranded'}</span>
                    </div>
                    <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                      <span className="text-slate-400 block text-[10px]">BRAND</span>
                      <span className="text-slate-200 font-bold">{selectedProductDetails.brand || 'Generic'}</span>
                    </div>
                    <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 col-span-2">
                      <span className="text-slate-400 block text-[10px]">CLASSPATH</span>
                      <span className="text-indigo-300 font-bold">{selectedProductDetails.classpath || 'Unclassified'}</span>
                    </div>
                  </div>

                  {/* Generated Descriptions Preview */}
                  <div className="space-y-2">
                    <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block">Generated Invoice Description</span>
                    <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono text-emerald-400">
                      {selectedProductDetails.invoice_desc || 'N/A'}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-4">
                    <Button
                      onClick={handleReject}
                      className="bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs flex-1 py-2.5 flex items-center justify-center gap-2"
                    >
                      <UserX className="h-4 w-4" /> Reject Product
                    </Button>

                    <Button
                      onClick={handleApprove}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex-1 py-2.5 flex items-center justify-center gap-2"
                    >
                      <UserCheck className="h-4 w-4" /> Approve Product
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : reviews.length === 0 ? (
              <div className="p-12 text-center bg-slate-900/60 border border-slate-800 rounded-2xl space-y-3">
                <div className="p-4 bg-emerald-500/10 text-emerald-400 rounded-full w-16 h-16 mx-auto flex items-center justify-center border border-emerald-500/20">
                  <CheckCircle2 className="h-8 w-8" />
                </div>
                <h3 className="text-lg font-bold text-white">All Queue Items Processed!</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto">
                  There are no remaining products requiring human review. All products in your catalog have been verified and approved.
                </p>
              </div>
            ) : (
              <div className="p-8 text-center bg-slate-900/60 border border-slate-800 rounded-xl text-slate-400 text-sm">
                Select an item from the left panel to inspect and perform review actions.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
