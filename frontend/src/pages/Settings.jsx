import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { downloadResults } from '../services/api';
import { usePipeline } from '../context/PipelineContext';
import { useTheme } from '../context/ThemeContext';
import { 
  Palette, 
  Moon, 
  Sun, 
  Sparkles, 
  Sliders, 
  Bell, 
  Download, 
  CheckCircle2, 
  SlidersHorizontal,
  Check
} from 'lucide-react';

export default function Settings() {
  const { showToast } = usePipeline();
  const { theme, setTheme, accent, setAccent } = useTheme();

  // Local state for non-theme preferences (persisted in localStorage)
  const [notifications, setNotifications] = useState(() => localStorage.getItem('forgeiq_notifs') !== 'false');
  const [autoRefresh, setAutoRefresh] = useState(() => localStorage.getItem('forgeiq_refresh') !== 'false');
  const [exportFormat, setExportFormat] = useState(() => localStorage.getItem('forgeiq_export') || 'csv');
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    localStorage.setItem('forgeiq_notifs', notifications);
    localStorage.setItem('forgeiq_refresh', autoRefresh);
    localStorage.setItem('forgeiq_export', exportFormat);
  }, [notifications, autoRefresh, exportFormat]);

  const handleSaveSettings = () => {
    setSavedSuccess(true);
    showToast('Platform preferences saved successfully!', 'success');
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  const handleExport = async (format) => {
    try {
      await downloadResults(format || exportFormat);
    } catch (error) {
      alert(error.message || 'Export failed');
    }
  };

  const themes = [
    { id: 'slate', name: 'Cyber Slate (Default)', desc: 'Sleek dark mode with slate tones', preview: 'bg-slate-900 border-slate-800' },
    { id: 'obsidian', name: 'Obsidian Glass', desc: 'Ultra-dark deep black glassmorphism', preview: 'bg-black border-slate-900' },
    { id: 'midnight', name: 'Midnight Navy', desc: 'Rich indigo-navy dark mode', preview: 'bg-indigo-950/60 border-indigo-900/60' }
  ];

  const accents = [
    { id: 'indigo', name: 'Indigo Electric', color: 'bg-indigo-500' },
    { id: 'emerald', name: 'Emerald Cyber', color: 'bg-emerald-500' },
    { id: 'violet', name: 'Violet Neon', color: 'bg-violet-500' },
    { id: 'amber', name: 'Amber Gold', color: 'bg-amber-500' }
  ];

  return (
    <div className="space-y-8 max-w-4xl pb-16">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">Platform Settings</h1>
          <p className="text-slate-400 text-sm mt-1">
            Customize appearance, themes, notification triggers, and export preferences.
          </p>
        </div>

        <Button
          onClick={handleSaveSettings}
          className="bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold px-6 py-2.5 rounded-xl shadow-lg shadow-indigo-600/30 flex items-center gap-2"
        >
          {savedSuccess ? <Check className="h-4 w-4 text-emerald-300" /> : <Sparkles className="h-4 w-4" />}
          {savedSuccess ? 'Settings Saved ✓' : 'Save Preferences'}
        </Button>
      </div>

      {savedSuccess && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 font-semibold text-xs flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4" /> Platform settings updated and saved to local preferences!
        </div>
      )}

      {/* Theme & Appearance */}
      <Card className="bg-slate-900/80 border-slate-800 backdrop-blur-md">
        <CardHeader className="border-b border-slate-800">
          <CardTitle className="text-base font-bold text-white flex items-center gap-2">
            <Palette className="h-5 w-5 text-indigo-400" /> Appearance & Theme Style
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          {/* Theme Preset Cards */}
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
              Theme Preset
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {themes.map((t) => (
                <div
                  key={t.id}
                  onClick={() => setTheme(t.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    theme === t.id
                      ? 'border-indigo-500 bg-indigo-600/10 ring-2 ring-indigo-500/30'
                      : 'border-slate-800 bg-slate-950/60 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold text-white">{t.name}</span>
                    {theme === t.id && <CheckCircle2 className="h-4 w-4 text-indigo-400" />}
                  </div>
                  <p className="text-xs text-slate-400">{t.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Accent Color Selection */}
          <div className="pt-4 border-t border-slate-800/80">
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
              Accent Highlight Color
            </label>
            <div className="flex flex-wrap gap-4">
              {accents.map((a) => (
                <button
                  key={a.id}
                  onClick={() => setAccent(a.id)}
                  className={`flex items-center gap-2.5 px-4 py-2 rounded-xl border text-xs font-semibold transition-all ${
                    accent === a.id
                      ? 'border-indigo-500 bg-slate-950 text-white shadow-md'
                      : 'border-slate-800 bg-slate-950/40 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <span className={`h-3 w-3 rounded-full ${a.color}`} />
                  {a.name}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notifications & Automation */}
      <Card className="bg-slate-900/80 border-slate-800 backdrop-blur-md">
        <CardHeader className="border-b border-slate-800">
          <CardTitle className="text-base font-bold text-white flex items-center gap-2">
            <Bell className="h-5 w-5 text-emerald-400" /> Notifications & Live Data Sync
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 space-y-4">
          <div className="flex items-center justify-between py-2 border-b border-slate-800/60">
            <div>
              <span className="text-sm font-semibold text-white block">Pipeline Execution Toasts</span>
              <span className="text-xs text-slate-400">Display live status notifications when enrichment starts or completes.</span>
            </div>
            <button
              onClick={() => setNotifications(!notifications)}
              className={`w-12 h-6 rounded-full transition-colors p-1 flex items-center ${
                notifications ? 'bg-indigo-600 justify-end' : 'bg-slate-800 justify-start'
              }`}
            >
              <span className="w-4 h-4 rounded-full bg-white shadow-sm" />
            </button>
          </div>

          <div className="flex items-center justify-between py-2">
            <div>
              <span className="text-sm font-semibold text-white block">Live Status Auto-Polling</span>
              <span className="text-xs text-slate-400">Automatically sync pipeline progress every 1 second during background runs.</span>
            </div>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`w-12 h-6 rounded-full transition-colors p-1 flex items-center ${
                autoRefresh ? 'bg-indigo-600 justify-end' : 'bg-slate-800 justify-start'
              }`}
            >
              <span className="w-4 h-4 rounded-full bg-white shadow-sm" />
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Export & Data Options */}
      <Card className="bg-slate-900/80 border-slate-800 backdrop-blur-md">
        <CardHeader className="border-b border-slate-800">
          <CardTitle className="text-base font-bold text-white flex items-center gap-2">
            <Download className="h-5 w-5 text-amber-400" /> Catalog Export Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              Default Download Format
            </label>
            <div className="inline-flex rounded-xl bg-slate-950 p-1 border border-slate-800">
              <button
                onClick={() => setExportFormat('csv')}
                className={`px-4 py-2 text-xs font-bold rounded-lg transition-all ${
                  exportFormat === 'csv' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                CSV (.csv)
              </button>
              <button
                onClick={() => setExportFormat('json')}
                className={`px-4 py-2 text-xs font-bold rounded-lg transition-all ${
                  exportFormat === 'json' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                JSON (.json)
              </button>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 flex flex-wrap gap-4">
            <Button onClick={() => handleExport('csv')} className="bg-indigo-600 hover:bg-indigo-500 flex items-center gap-2 text-xs font-bold">
              <Download className="h-4 w-4" /> Export Enriched CSV Catalog
            </Button>
            <Button onClick={() => handleExport('json')} variant="secondary" className="bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center gap-2 text-xs font-bold">
              <Download className="h-4 w-4" /> Export JSON Catalog
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
