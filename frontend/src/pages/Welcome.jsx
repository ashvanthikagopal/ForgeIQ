import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { 
  Zap, 
  Sparkles, 
  ArrowRight, 
  Database, 
  Upload, 
  ShieldCheck, 
  LayoutDashboard, 
  GitMerge, 
  CheckCircle2, 
  Layers, 
  Cpu, 
  SlidersHorizontal, 
  FileText, 
  Globe, 
  BarChart3,
  Search,
  Check
} from 'lucide-react';
import { usePipeline } from '../context/PipelineContext';

export default function Welcome() {
  const navigate = useNavigate();
  const { pipelineState, isRunning } = usePipeline();

  const stages = [
    {
      part: 'Part 1',
      title: 'Foundation Data & Lookups',
      icon: Database,
      color: 'from-blue-600 to-indigo-600',
      description: 'Parses raw CSV inputs, cleans non-breaking spaces, removes placeholders, and initializes ground-truth lookups.'
    },
    {
      part: 'Part 2',
      title: 'Classification & Attributes',
      icon: Cpu,
      color: 'from-indigo-600 to-violet-600',
      description: 'Model-driven classification determines product taxonomy (Faucets, Fittings, Abrasives) and extracts structured specs.'
    },
    {
      part: 'Part 3',
      title: 'Normalization & 5-Tier Copy',
      icon: SlidersHorizontal,
      color: 'from-violet-600 to-purple-600',
      description: 'Standardizes UOMs (e.g. 120 VOLTS → 120V) and generates Invoice (≤40ch), Mobile (≤80ch), Title, & Long descriptions.'
    },
    {
      part: 'Part 4',
      title: 'Enrichment & QA Validation',
      icon: ShieldCheck,
      color: 'from-emerald-600 to-teal-600',
      description: 'Enriches missing attributes from official sources and validates LOV rules, auto-passing ~84% and routing ~16% for review.'
    }
  ];

  return (
    <div className="space-y-12 pb-16 max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-slate-900 via-indigo-950/40 to-slate-950 border border-slate-800 p-8 sm:p-12 shadow-2xl">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-wider">
            <Sparkles className="h-3.5 w-3.5 text-amber-400 fill-amber-400" />
            ForgeIQ Enterprise AI Product Platform
          </div>

          <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-white leading-tight">
            Forge Intelligence From Raw Catalog Data
          </h1>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
            Welcome to <span className="text-indigo-400 font-bold">ForgeIQ</span> — the automated product content enrichment and quality assurance engine. Transform raw, fragmented CSV input into enriched, LOV-compliant e-commerce catalogs powered by Python Part 1→Part 4 pipeline intelligence.
          </p>

          {/* Quick Action Navigation Buttons */}
          <div className="pt-4 flex flex-wrap items-center gap-4">
            <Button
              size="lg"
              onClick={() => navigate('/dashboard')}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold px-7 py-3.5 rounded-xl shadow-xl shadow-indigo-600/30 flex items-center gap-2.5 text-sm"
            >
              <LayoutDashboard className="h-5 w-5" />
              Enter Command Center
              <ArrowRight className="h-4 w-4" />
            </Button>

            <Button
              size="lg"
              variant="outline"
              onClick={() => navigate('/pipeline')}
              className="border-slate-700 bg-slate-900/80 hover:bg-slate-800 text-white font-bold px-6 py-3.5 rounded-xl flex items-center gap-2 text-sm"
            >
              <GitMerge className="h-5 w-5 text-indigo-400" />
              Upload CSV / Run Pipeline
            </Button>

            <Button
              size="lg"
              variant="outline"
              onClick={() => navigate('/qa')}
              className="border-slate-700 bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white font-semibold px-5 py-3.5 rounded-xl flex items-center gap-2 text-sm"
            >
              <ShieldCheck className="h-5 w-5 text-emerald-400" />
              Human Review Queue
            </Button>
          </div>
        </div>
      </div>

      {/* 4 Pipeline Stages Walkthrough */}
      <div className="space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl font-extrabold text-white tracking-tight">
            How ForgeIQ Works: The 4-Part Architecture
          </h2>
          <p className="text-xs text-slate-400">
            A visual, stage-by-stage handoff ensuring schema validation, normalized attributes, and high-confidence content.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stages.map((st, idx) => {
            const Icon = st.icon;
            return (
              <Card key={idx} className="bg-slate-900/70 border-slate-800 hover:border-slate-700 transition-all duration-200 relative overflow-hidden group">
                <div className={`h-1.5 w-full bg-gradient-to-r ${st.color}`} />
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-indigo-400">
                      {st.part}
                    </span>
                    <div className="p-2 rounded-xl bg-slate-800/60 text-indigo-300 group-hover:scale-110 transition-transform">
                      <Icon className="h-5 w-5" />
                    </div>
                  </div>
                  <CardTitle className="text-base font-bold text-white mt-3">
                    {st.title}
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-slate-400 leading-relaxed">
                  {st.description}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Capabilities & Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-slate-900/60 border-slate-800 p-6 space-y-3">
          <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl w-fit border border-indigo-500/20">
            <Upload className="h-6 w-6" />
          </div>
          <h3 className="text-base font-bold text-white">Custom CSV Upload</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Drag & drop any user input CSV file with Mfg Part Num, Description, Brand, and Manufacturer headers. The pipeline automatically normalizes column names.
          </p>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800 p-6 space-y-3">
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl w-fit border border-emerald-500/20">
            <Database className="h-6 w-6" />
          </div>
          <h3 className="text-base font-bold text-white">1,000 Product Sample Dataset</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Test the complete pipeline instantly using the built-in ground-truth challenge dataset — perfect for judge demonstrations without requiring file prep.
          </p>
        </Card>

        <Card className="bg-slate-900/60 border-slate-800 p-6 space-y-3">
          <div className="p-3 bg-amber-500/10 text-amber-400 rounded-xl w-fit border border-amber-500/20">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <h3 className="text-base font-bold text-white">Human-in-the-Loop QA & Bulk Actions</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            ~84% of catalog items pass QA automatically. The remaining ~16% are sent to the Review Queue where catalog managers can inspect and 1-click bulk approve.
          </p>
        </Card>
      </div>

      {/* Ready Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-8 flex flex-col sm:flex-row items-center justify-between gap-6">
        <div>
          <h3 className="text-xl font-extrabold text-white">Ready to explore ForgeIQ?</h3>
          <p className="text-xs text-slate-400 mt-1">
            Jump directly to the Command Center dashboard or launch a new enrichment run.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <Button
            size="lg"
            onClick={() => navigate('/dashboard')}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold px-6 py-3 rounded-xl flex items-center gap-2 text-xs"
          >
            <LayoutDashboard className="h-4 w-4" />
            Go to Command Center
          </Button>
        </div>
      </div>
    </div>
  );
}
