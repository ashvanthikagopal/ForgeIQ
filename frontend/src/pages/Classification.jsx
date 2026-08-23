import React, { useEffect, useState } from 'react';
import { getClassification } from '../api/forgeiqApi';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Loader2, Layers, CheckCircle2, AlertTriangle, ShieldCheck, ChevronRight } from 'lucide-react';

export default function Classification() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getClassification()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load classification intelligence');
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
        <h1 className="text-3xl font-extrabold tracking-tight text-white">Taxonomy & AI Classification</h1>
        <p className="text-slate-400 text-sm mt-1">
          Part 2 Classification engine mapping raw product descriptions to standard industrial UNSPSC classpaths.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-slate-900/60 border-slate-800">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">CLASSIFIED PRODUCTS</p>
              <p className="text-2xl font-bold text-white mt-1">{data.total_classified} / {data.total_products}</p>
              <span className="text-[11px] text-emerald-400 font-semibold">100% Taxonomized</span>
            </div>
            <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl">
              <Layers className="h-6 w-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">AVG CONFIDENCE</p>
              <p className="text-2xl font-bold text-white mt-1">{(data.average_confidence * 100).toFixed(1)}%</p>
              <span className="text-[11px] text-indigo-400 font-semibold">LLM Classification Score</span>
            </div>
            <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl">
              <ShieldCheck className="h-6 w-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">NEEDS CLASSPATH REVIEW</p>
              <p className="text-2xl font-bold text-white mt-1">{data.needs_review_count}</p>
              <span className="text-[11px] text-amber-400 font-semibold">Missing LOV Match</span>
            </div>
            <div className="p-3 bg-amber-500/10 text-amber-400 rounded-xl">
              <AlertTriangle className="h-6 w-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">CLASSPATH CATEGORIES</p>
              <p className="text-2xl font-bold text-white mt-1">{data.classpath_distribution?.length || 0}</p>
              <span className="text-[11px] text-slate-400 font-semibold">Taxonomy Clusters</span>
            </div>
            <div className="p-3 bg-purple-500/10 text-purple-400 rounded-xl">
              <CheckCircle2 className="h-6 w-6" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Taxonomy Tree Visualizer */}
      <Card className="bg-slate-900/60 border-slate-800">
        <CardHeader>
          <CardTitle className="text-base text-slate-200">INDUSTRIAL TAXONOMY TREE</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="p-4 bg-slate-950/80 rounded-xl border border-slate-800 space-y-3 font-mono text-xs text-slate-300">
            <div className="flex items-center gap-2 text-indigo-400 font-bold">
              <ChevronRight className="h-4 w-4" /> Commercial & Industrial Equipment
            </div>
            <div className="pl-6 space-y-2 border-l border-slate-800">
              <div className="flex items-center gap-2 text-emerald-400">
                <ChevronRight className="h-4 w-4" /> Commercial Food Service Equipment
              </div>
              <div className="pl-6 space-y-1 text-slate-400">
                <p>├── Commercial Dishwashers & Components</p>
                <p>├── Commercial Refrigeration</p>
                <p>└── Heating & Cooking Appliances</p>
              </div>

              <div className="flex items-center gap-2 text-cyan-400">
                <ChevronRight className="h-4 w-4" /> Electrical & Power Components
              </div>
              <div className="pl-6 space-y-1 text-slate-400">
                <p>├── Heating Elements & Motors</p>
                <p>└── Relays, Controls & Switches</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Classpath Predictions Table */}
      <Card className="bg-slate-900/60 border-slate-800 overflow-hidden">
        <CardHeader>
          <CardTitle className="text-base text-slate-200">PRODUCT CLASSPATH PREDICTIONS</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3">MPN</th>
                  <th className="px-6 py-3">Manufacturer</th>
                  <th className="px-6 py-3">Predicted Classpath</th>
                  <th className="px-6 py-3">Confidence</th>
                  <th className="px-6 py-3">LOV Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {data.items?.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-3.5 font-mono font-bold text-indigo-300">{item.mpn || 'MPN-N/A'}</td>
                    <td className="px-6 py-3.5 text-slate-300">{item.manufacturer || 'Unbranded'}</td>
                    <td className="px-6 py-3.5 text-slate-200 font-medium">{item.classpath}</td>
                    <td className="px-6 py-3.5">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-emerald-500 h-full rounded-full"
                            style={{ width: `${(item.confidence || 0.85) * 100}%` }}
                          />
                        </div>
                        <span className="font-mono text-slate-400">{((item.confidence || 0.85) * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-3.5">
                      {item.needs_review ? (
                        <Badge variant="warning">Needs Review</Badge>
                      ) : (
                        <Badge variant="success">LOV Validated</Badge>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
