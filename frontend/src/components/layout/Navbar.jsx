import React, { useState } from 'react';
import { Menu, PlayCircle, Loader2, Server, CheckCircle2, AlertCircle, User, Download } from 'lucide-react';
import { usePipeline } from '../../context/PipelineContext';
import { Button } from '../common/Button';
import { Modal } from '../common/Modal';
import { downloadResults } from '../../services/api';

export default function Navbar({ onMenuClick, title = "ForgeIQ" }) {
  const { isRunning, startPipeline, backendConnected, pipelineState } = usePipeline();
  const [modalOpen, setModalOpen] = useState(false);

  const handleConfirmRun = async () => {
    setModalOpen(false);
    try {
      await startPipeline();
    } catch (e) {
      console.error(e);
    }
  };

  const handleExport = async (format) => {
    try {
      await downloadResults(format);
    } catch (e) {
      alert(e.message || 'Export failed');
    }
  };

  return (
    <>
      <header className="h-16 bg-slate-900/90 border-b border-slate-800 px-4 sm:px-6 flex items-center justify-between backdrop-blur-md sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <button 
            onClick={onMenuClick}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <Menu className="h-5 w-5" />
          </button>
          
          <div>
            <h2 className="text-base sm:text-lg font-bold text-white tracking-tight">{title}</h2>
            <p className="text-[11px] text-slate-400 hidden sm:block">Product Content Enrichment & QA Platform</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Backend Connection Indicator */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-950 border border-slate-800 text-xs">
            <Server className="h-3.5 w-3.5 text-slate-400" />
            <span className={backendConnected ? "text-emerald-400 font-medium" : "text-rose-400 font-medium"}>
              {backendConnected ? 'Connected' : 'Offline'}
            </span>
          </div>

          {/* Quick Export Dropdown or Button */}
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => handleExport('csv')}
            className="hidden lg:flex items-center gap-1.5 text-xs text-slate-300 border-slate-700 hover:bg-slate-800"
          >
            <Download className="h-3.5 w-3.5" /> CSV
          </Button>

          {/* Run Pipeline Button */}
          <Button
            size="sm"
            onClick={() => setModalOpen(true)}
            disabled={isRunning || !backendConnected}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold flex items-center gap-1.5 shadow-md shadow-indigo-600/20"
          >
            {isRunning ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> Processing...</>
            ) : (
              <><PlayCircle className="h-4 w-4" /> Run Pipeline</>
            )}
          </Button>

          {/* Profile avatar */}
          <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
            <User className="h-4 w-4" />
          </div>
        </div>
      </header>

      {/* Confirmation Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Run Complete ForgeIQ Pipeline?"
      >
        <div className="space-y-4">
          <p className="text-sm text-slate-300">
            This action will run all 1000 product records through the 4 sequential processing stages:
          </p>
          <ul className="space-y-2 text-xs text-slate-400 bg-slate-900 p-4 rounded-xl border border-slate-800">
            <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-indigo-400" /> Part 1: Foundation (Data Cleaning & Lookups)</li>
            <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-indigo-400" /> Part 2: Taxonomy & Classification</li>
            <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-indigo-400" /> Part 3: Normalization & Copy Generation</li>
            <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-indigo-400" /> Part 4: Enrichment & Quality Assurance</li>
          </ul>

          <div className="pt-4 flex justify-end gap-3 border-t border-slate-800">
            <Button variant="ghost" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button onClick={handleConfirmRun} className="bg-indigo-600 hover:bg-indigo-500">
              Run Pipeline Now
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
}
