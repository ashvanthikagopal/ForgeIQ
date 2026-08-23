import React, { useEffect, useState } from 'react';
import { getNormalization } from '../api/forgeiqApi';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Loader2, ArrowRight, ArrowRightLeft, SlidersHorizontal, CheckCircle2 } from 'lucide-react';

export default function Normalization() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getNormalization()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load normalization intelligence');
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
        <h1 className="text-3xl font-extrabold tracking-tight text-white">Product Normalization Engine</h1>
        <p className="text-slate-400 text-sm mt-1">
          Part 3 Normalizer standardizing manufacturer names, brand placeholders, electrical units, and decimal-to-fraction unit conversions.
        </p>
      </div>

      {/* Before / After Conversion Showcase Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader>
            <CardTitle className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">UNIT NORMALIZATION (UOM)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-slate-950 rounded-xl border border-slate-800">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-bold block">RAW INPUT</span>
                <span className="text-sm font-mono text-slate-300">50.25 inches</span>
              </div>
              <ArrowRight className="h-4 w-4 text-indigo-400" />
              <div className="text-right">
                <span className="text-[10px] text-emerald-400 uppercase font-bold block">NORMALIZED</span>
                <span className="text-sm font-mono font-bold text-emerald-400">50-1/4 in</span>
              </div>
            </div>
            <p className="text-xs text-slate-400">Rule: Fraction mapping + Unit of Measure abbreviation.</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader>
            <CardTitle className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">ELECTRICAL SPECIFICATIONS</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-slate-950 rounded-xl border border-slate-800">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-bold block">RAW INPUT</span>
                <span className="text-sm font-mono text-slate-300">120 VOLTS / 15 AMPS</span>
              </div>
              <ArrowRight className="h-4 w-4 text-cyan-400" />
              <div className="text-right">
                <span className="text-[10px] text-emerald-400 uppercase font-bold block">NORMALIZED</span>
                <span className="text-sm font-mono font-bold text-emerald-400">120V 15A</span>
              </div>
            </div>
            <p className="text-xs text-slate-400">Rule: Electrical suffix standardization for Invoice descriptions.</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800">
          <CardHeader>
            <CardTitle className="text-xs font-semibold text-purple-400 uppercase tracking-wider">BRAND PLACEHOLDER STRIPPING</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-slate-950 rounded-xl border border-slate-800">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-bold block">RAW INPUT</span>
                <span className="text-sm font-mono text-slate-300">UNBRANDED / NO BRAND</span>
              </div>
              <ArrowRight className="h-4 w-4 text-purple-400" />
              <div className="text-right">
                <span className="text-[10px] text-emerald-400 uppercase font-bold block">NORMALIZED</span>
                <span className="text-sm font-mono font-bold text-emerald-400">Generic / Removed</span>
              </div>
            </div>
            <p className="text-xs text-slate-400">Rule: Placeholder cleaning prevents garbage text in generated copy.</p>
          </CardContent>
        </Card>
      </div>

      {/* Normalization Conversion Audit Table */}
      <Card className="bg-slate-900/60 border-slate-800 overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base text-slate-200">NORMALIZATION CONVERSION LOGS</CardTitle>
          <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
            <SlidersHorizontal className="h-4 w-4 text-indigo-400" /> 1000 Products Normalized
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3">MPN</th>
                  <th className="px-6 py-3">Raw Value</th>
                  <th className="px-6 py-3">Normalized Output</th>
                  <th className="px-6 py-3">Applied Rule</th>
                  <th className="px-6 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {data.uom_conversions_sample?.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-3.5 font-mono font-bold text-indigo-300">SAMPLE-{idx+1}</td>
                    <td className="px-6 py-3.5 text-slate-300 font-mono">{item.raw}</td>
                    <td className="px-6 py-3.5 text-emerald-400 font-mono font-bold">{item.normalized}</td>
                    <td className="px-6 py-3.5 text-slate-300">{item.rule}</td>
                    <td className="px-6 py-3.5">
                      <Badge variant="success">PASSED</Badge>
                    </td>
                  </tr>
                ))}

                {data.brand_normalizations?.map((item, idx) => (
                  <tr key={`b-${idx}`} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-3.5 font-mono font-bold text-indigo-300">{item.mpn}</td>
                    <td className="px-6 py-3.5 text-slate-300 font-mono">{item.raw}</td>
                    <td className="px-6 py-3.5 text-emerald-400 font-mono font-bold">{item.normalized}</td>
                    <td className="px-6 py-3.5 text-slate-300">{item.rule}</td>
                    <td className="px-6 py-3.5">
                      <Badge variant="success">PASSED</Badge>
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
