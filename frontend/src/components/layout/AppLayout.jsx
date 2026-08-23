import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import { usePipeline } from '../../context/PipelineContext';
import { useTheme } from '../../context/ThemeContext';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

const PAGE_TITLES = {
  '/': 'Welcome & Overview',
  '/dashboard': 'Command Center',
  '/pipeline': 'Pipeline Flow',
  '/products': 'Products Catalog',
  '/qa': 'QA Review Queue',
  '/analytics': 'Analytics & Metrics',
  '/settings': 'Platform Settings',
};

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { toast, setToast } = usePipeline();
  const { theme } = useTheme();

  const getTitle = () => {
    if (location.pathname.startsWith('/products/')) return 'Product Details';
    return PAGE_TITLES[location.pathname] || 'ForgeIQ';
  };

  const getBgClass = () => {
    if (theme === 'obsidian') return 'bg-black';
    if (theme === 'midnight') return 'bg-[#030612]';
    return 'bg-[#07090e]';
  };

  return (
    <div className={`flex h-screen overflow-hidden text-slate-100 font-sans transition-colors duration-300 ${getBgClass()}`}>
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-xs md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

      <div className="flex flex-col flex-1 overflow-hidden">
        <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} title={getTitle()} />
        
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          {/* Toast Notification Banner */}
          {toast && (
            <div className="mb-6 p-4 rounded-xl border flex items-center justify-between shadow-xl animate-in slide-in-from-top-2 duration-200 bg-slate-900 border-indigo-500/40 text-slate-100">
              <div className="flex items-center gap-3">
                {toast.type === 'success' && <CheckCircle2 className="h-5 w-5 text-emerald-400" />}
                {toast.type === 'error' && <AlertCircle className="h-5 w-5 text-rose-400" />}
                {toast.type === 'info' && <Info className="h-5 w-5 text-indigo-400" />}
                <span className="text-sm font-medium">{toast.message}</span>
              </div>
              <button 
                onClick={() => setToast(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          <Outlet />
        </main>
      </div>
    </div>
  );
}
