import React, { useEffect, useState } from 'react';
import { getEnrichment } from '../api/forgeiqApi';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Loader2, Globe, ShieldCheck, AlertCircle, Link } from 'lucide-react';

export default function Enrichment() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getEnrichment()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load enrichment intelligence');
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
        <h1 className="text-3xl font-extrabold tracking-tight text-white">Source-Backed Web Enrichment</h1>
        <p className="text-slate-400 text-sm mt-1">
          Part 4 Enrichment module retrieving official manufacturer specifications with strict source verification.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card className="bg-slate-900/60 border-slate-800">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">TOTAL ENRICHED FIELDS</p>
              <p className="text-2xl font-bold text-white mt-1">{data.total_enriched_fields || 0}</p>
              <span className="text-[11px] text-indigo-400 font-semibold">Web Search Extracted</span>
            </div>
            <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl">
              <Globe className="h-6 w-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">OFFICIAL SOURCES</p>
              <p className="text-2xl font-bold text-white mt-1">{data.official_sources_count || 0}</p>
              <span className="text-[11px] text-emerald-400 font-semibold">Verified Manufacturer Web</span>
            </div>
            <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl">
              <ShieldCheck className="h-6 w-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">UNVERIFIED SOURCES</p>
              <p className="text-2xl font-bold text-white mt-1">{data.unverified_sources_count || 0}</p>
              <span className="text-[11px] text-amber-400 font-semibold">Requires Human Review</span>
            </div>
            <div className="p-3 bg-amber-500/10 text-amber-400 rounded-xl">
              <AlertCircle className="h-6 w-6" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Source Verifiability Principle Warning */}
      <div className="p-4 bg-slate-900/90 border border-slate-800 rounded-2xl flex items-start gap-4">
        <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-xl flex-shrink-0">
          <ShieldCheck className="h-5 w-5" />
        </div>
        <div className="text-xs space-y-1">
          <h4 className="font-bold text-slate-200">ForgeIQ Source Integrity Principle</h4>
          <p className="text-slate-400 leading-relaxed">
            ForgeIQ never invents product specifications. Missing fields are enriched strictly against official manufacturer portals. If an official source is unverified, the record is flagged for human review rather than outputting speculative data.
          </p>
        </div>
      </div>

      {/* Enrichment Results Matrix */}
      <Card className="bg-slate-900/60 border-slate-800 overflow-hidden">
        <CardHeader>
          <CardTitle className="text-base text-slate-200">ENRICHED ATTRIBUTES LOG</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3">MPN</th>
                  <th className="px-6 py-3">Enriched Field</th>
                  <th className="px-6 py-3">Retrieved Value</th>
                  <th className="px-6 py-3">Web Source</th>
                  <th className="px-6 py-3">Confidence</th>
                  <th className="px-6 py-3">Source Type</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {data.items?.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-3.5 font-mono font-bold text-indigo-300">{item.mpn}</td>
                    <td className="px-6 py-3.5 text-slate-200 font-medium">{item.field}</td>
                    <td className="px-6 py-3.5 font-mono text-emerald-400 font-bold">{item.value}</td>
                    <td className="px-6 py-3.5 text-slate-300 font-mono text-[11px]">{item.source}</td>
                    <td className="px-6 py-3.5">
                      <span className="font-mono text-slate-300">{((item.confidence || 0.95) * 100).toFixed(0)}%</span>
                    </td>
                    <td className="px-6 py-3.5">
                      {item.official ? (
                        <Badge variant="success">Official Manufacturer</Badge>
                      ) : (
                        <Badge variant="warning">Unverified Source</Badge>
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
