import React, { useEffect, useState } from 'react';
import { getAttributes } from '../api/forgeiqApi';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Loader2, Cpu, CheckCircle2, AlertTriangle, ListFilter } from 'lucide-react';

export default function Attributes() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getAttributes()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load attribute intelligence');
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
        <h1 className="text-3xl font-extrabold tracking-tight text-white">Attribute Extraction Intelligence</h1>
        <p className="text-slate-400 text-sm mt-1">
          Part 2 Attribute Extractor extracting structured key-value pairs constrained by LOV dictionaries.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card className="bg-slate-900/60 border-slate-800">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">TOTAL EXTRACTED ATTRIBUTES</p>
              <p className="text-2xl font-bold text-white mt-1">{data.total_extracted || 0}</p>
              <span className="text-[11px] text-indigo-400 font-semibold">Structured Fields</span>
            </div>
            <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl">
              <Cpu className="h-6 w-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">LOV COMPLIANCE RATE</p>
              <p className="text-2xl font-bold text-white mt-1">{data.lov_compliance_pct}%</p>
              <span className="text-[11px] text-emerald-400 font-semibold">Strict LOV Match</span>
            </div>
            <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl">
              <CheckCircle2 className="h-6 w-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">MISSING ATTRIBUTES</p>
              <p className="text-2xl font-bold text-white mt-1">{data.missing_attribute_products || 0}</p>
              <span className="text-[11px] text-amber-400 font-semibold">Flagged for Part 4 Enrichment</span>
            </div>
            <div className="p-3 bg-amber-500/10 text-amber-400 rounded-xl">
              <AlertTriangle className="h-6 w-6" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Attributes Extraction Matrix */}
      <Card className="bg-slate-900/60 border-slate-800 overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base text-slate-200">EXTRACTED ATTRIBUTES MATRIX</CardTitle>
          <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
            <ListFilter className="h-4 w-4 text-indigo-400" /> LOV Constrained Extraction
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3">MPN</th>
                  <th className="px-6 py-3">Classpath</th>
                  <th className="px-6 py-3">Attribute Name</th>
                  <th className="px-6 py-3">Extracted Value</th>
                  <th className="px-6 py-3">LOV Match Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {data.items?.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-3.5 font-mono font-bold text-indigo-300">{item.mpn || 'PROD'}</td>
                    <td className="px-6 py-3.5 text-slate-300 truncate max-w-[200px]">{item.classpath}</td>
                    <td className="px-6 py-3.5 text-slate-200 font-medium">{item.attribute}</td>
                    <td className="px-6 py-3.5 font-mono text-emerald-400 font-bold">{item.value}</td>
                    <td className="px-6 py-3.5">
                      {item.lov_matched ? (
                        <span className="inline-flex items-center gap-1.5 text-emerald-400 font-semibold text-xs">
                          <span className="h-2 w-2 rounded-full bg-emerald-500" /> LOV Matched ✓
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 text-amber-400 font-semibold text-xs">
                          <span className="h-2 w-2 rounded-full bg-amber-500" /> Non-LOV Value !
                        </span>
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
