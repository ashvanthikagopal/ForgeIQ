import React, { useEffect, useState } from 'react';
import { getDescriptions } from '../api/forgeiqApi';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Loader2, FileText, CheckCircle2, AlertTriangle, Layers, ArrowRight } from 'lucide-react';

export default function Descriptions() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('invoice');

  useEffect(() => {
    getDescriptions()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load description intelligence');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="h-10 w-10 animate-spin text-indigo-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-rose-500/10 border border-rose-500/30 rounded-2xl text-rose-400">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-10">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white">5-Tier Content Description Builder</h1>
        <p className="text-slate-400 text-sm mt-1">
          Part 3 Description Engine building Invoice, Mobile, Product Title, Long Description, and Marketing Copy with character limit enforcement.
        </p>
      </div>

      {/* Description Pipeline Visual Flow */}
      <Card className="bg-slate-900/60 border-slate-800">
        <CardHeader>
          <CardTitle className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">DESCRIPTION GENERATION PIPELINE</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
              <span className="text-indigo-400 font-bold block mb-1">1. RAW PRODUCT DATA</span>
              <p className="text-slate-400 font-sans">Reads MPN, manufacturer, brand & raw description attributes from Part 1 & Part 2.</p>
            </div>
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
              <span className="text-cyan-400 font-bold block mb-1">2. VALIDATED ATTRIBUTES</span>
              <p className="text-slate-400 font-sans">Ensures non-placeholder values, unit abbreviations & uppercase casing rules.</p>
            </div>
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800">
              <span className="text-emerald-400 font-bold block mb-1">3. GENERATED CONTENT</span>
              <p className="text-slate-400 font-sans">Produces 5 formatted channels matching POS & ERP character bounds (40 & 80 chars).</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs for 5 Description Channels */}
      <div className="flex border-b border-slate-800 space-x-4">
        {[
          { key: 'invoice', label: 'Invoice Description (≤40)' },
          { key: 'mobile', label: 'Mobile Description (≤80)' },
          { key: 'title', label: 'Product Title' },
          { key: 'long', label: 'Long Description' },
          { key: 'marketing', label: 'Marketing Copy' }
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`pb-3 text-xs font-bold uppercase transition-colors relative ${
              activeTab === tab.key
                ? 'text-indigo-400 border-b-2 border-indigo-500'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Description Channel Content */}
      <Card className="bg-slate-900/60 border-slate-800 overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base text-slate-200">
            GENERATED {activeTab.toUpperCase()} COPY
          </CardTitle>
          <span className="text-xs text-slate-400 font-mono">
            {activeTab === 'invoice' && 'Limit: 40 Characters'}
            {activeTab === 'mobile' && 'Limit: 80 Characters'}
            {activeTab === 'title' && 'Full Standard Product Name'}
            {activeTab === 'long' && 'Rich Catalog Detail'}
            {activeTab === 'marketing' && 'Commerce Copy'}
          </span>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3">MPN</th>
                  <th className="px-6 py-3">Generated Content</th>
                  <th className="px-6 py-3">Length</th>
                  <th className="px-6 py-3">Validation Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {data.items?.map((item, idx) => {
                  let text = item.invoice_desc;
                  let len = item.invoice_len;
                  let limit = 40;
                  let valid = item.invoice_valid;

                  if (activeTab === 'mobile') {
                    text = item.mobile_desc;
                    len = item.mobile_len;
                    limit = 80;
                    valid = item.mobile_valid;
                  } else if (activeTab === 'title') {
                    text = item.product_title;
                    len = text?.length || 0;
                    limit = 120;
                    valid = true;
                  } else if (activeTab === 'long') {
                    text = item.long_description;
                    len = text?.length || 0;
                    limit = 500;
                    valid = true;
                  } else if (activeTab === 'marketing') {
                    text = item.marketing_copy;
                    len = text?.length || 0;
                    limit = 500;
                    valid = true;
                  }

                  return (
                    <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-3.5 font-mono font-bold text-indigo-300">{item.mpn || 'PROD'}</td>
                      <td className="px-6 py-3.5 font-mono text-slate-200">{text || '—'}</td>
                      <td className="px-6 py-3.5">
                        <div className="flex items-center gap-2">
                          <div className="w-20 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${valid ? 'bg-indigo-500' : 'bg-rose-500'}`}
                              style={{ width: `${Math.min(100, (len / limit) * 100)}%` }}
                            />
                          </div>
                          <span className="font-mono text-slate-400 text-[11px]">{len} / {limit}</span>
                        </div>
                      </td>
                      <td className="px-6 py-3.5">
                        {valid ? (
                          <Badge variant="success">✓ Valid</Badge>
                        ) : (
                          <Badge variant="danger">! Overflow</Badge>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
