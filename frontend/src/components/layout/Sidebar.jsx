import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  GitMerge, 
  Package, 
  ClipboardCheck, 
  BarChart3, 
  Settings, 
  Zap, 
  ChevronLeft, 
  ChevronRight,
  Layers,
  Cpu,
  SlidersHorizontal,
  FileText,
  Globe,
  Sparkles
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { usePipeline } from '../../context/PipelineContext';

const navGroups = [
  {
    title: 'OVERVIEW',
    items: [
      { name: 'Welcome & Overview', to: '/', icon: Sparkles },
      { name: 'Command Center', to: '/dashboard', icon: LayoutDashboard },
      { name: 'Pipeline Execution', to: '/pipeline', icon: GitMerge },
      { name: 'Products Catalog', to: '/products', icon: Package },
      { name: 'Human Review Queue', to: '/qa', icon: ClipboardCheck },
      { name: 'Executive Analytics', to: '/analytics', icon: BarChart3 },
    ]
  },
  {
    title: 'INTELLIGENCE',
    items: [
      { name: 'Taxonomy Classification', to: '/classification', icon: Layers },
      { name: 'Attribute Extraction', to: '/attributes', icon: Cpu },
      { name: 'Product Normalization', to: '/normalization', icon: SlidersHorizontal },
      { name: '5-Tier Descriptions', to: '/descriptions', icon: FileText },
      { name: 'Source Enrichment', to: '/enrichment', icon: Globe },
    ]
  },
  {
    title: 'SYSTEM',
    items: [
      { name: 'Settings & Health', to: '/settings', icon: Settings }
    ]
  }
];

import { useTheme } from '../../context/ThemeContext';

export default function Sidebar({ isOpen, setIsOpen }) {
  const { isRunning, backendConnected } = usePipeline();
  const { theme } = useTheme();
  const [collapsed, setCollapsed] = useState(false);

  const getSidebarBg = () => {
    if (theme === 'obsidian') return 'bg-black border-slate-900';
    if (theme === 'midnight') return 'bg-[#050819] border-indigo-950';
    return 'bg-slate-900 border-slate-800';
  };

  return (
    <aside className={cn(
      "fixed inset-y-0 left-0 z-50 border-r transition-all duration-300 ease-in-out md:static md:translate-x-0 flex flex-col justify-between shadow-2xl",
      getSidebarBg(),
      isOpen ? "translate-x-0" : "-translate-x-full",
      collapsed ? "w-20" : "w-64"
    )}>
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Logo & Header */}
        <div className={cn("h-18 flex items-center border-b border-slate-800 py-4 transition-all relative", collapsed ? "px-3 justify-center" : "px-5 justify-between")}>
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20 flex-shrink-0">
              <Zap className="h-5 w-5 fill-current" />
            </div>
            {!collapsed && (
              <div className="overflow-hidden">
                <span className="text-lg font-extrabold tracking-tight text-white block">FORGEIQ</span>
                <span className="text-[10px] text-slate-400 font-medium truncate block">Forge Intelligence From Data</span>
              </div>
            )}
          </div>

          <button
            onClick={() => setCollapsed(!collapsed)}
            className={cn(
              "hidden md:flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all",
              collapsed 
                ? "absolute -right-3 top-5.5 bg-slate-800 border border-slate-700 shadow-xl text-white z-30 rounded-full h-6 w-6 p-0 hover:scale-110" 
                : "h-7 w-7"
            )}
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <ChevronRight className="h-3.5 w-3.5 text-indigo-300" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>

        {/* Navigation items */}
        <nav className={cn("flex-1 overflow-y-auto py-4 space-y-6", collapsed ? "px-2" : "px-3")}>
          {navGroups.map((group, idx) => (
            <div key={idx} className="space-y-1.5">
              {!collapsed && (
                <div className="px-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                  {group.title}
                </div>
              )}
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.name}
                    to={item.to}
                    onClick={() => setIsOpen(false)}
                    className={({ isActive }) => cn(
                      "flex items-center rounded-xl text-xs font-semibold transition-all duration-150 group",
                      collapsed ? "justify-center px-0 py-3 text-center" : "px-3 py-2.5",
                      isActive 
                        ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shadow-md shadow-indigo-500/10" 
                        : "text-slate-400 hover:bg-slate-800/80 hover:text-slate-200"
                    )}
                    title={collapsed ? item.name : undefined}
                  >
                    <Icon className={cn("h-5 w-5 flex-shrink-0 transition-transform group-hover:scale-110", collapsed ? "mr-0" : "mr-3")} />
                    {!collapsed && <span>{item.name}</span>}
                  </NavLink>
                );
              })}
            </div>
          ))}
        </nav>
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/50">
        {!collapsed ? (
          <div className="space-y-3">
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">System Status</div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Backend</span>
                <div className="flex items-center gap-1.5 font-semibold">
                  <span className={cn("h-2 w-2 rounded-full", backendConnected ? "bg-emerald-500 shadow-sm shadow-emerald-500" : "bg-rose-500 animate-pulse")} />
                  <span className={backendConnected ? "text-emerald-400" : "text-rose-400"}>
                    {backendConnected ? 'Connected' : 'Offline'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Pipeline</span>
                <div className="flex items-center gap-1.5 font-semibold">
                  <span className={cn("h-2 w-2 rounded-full", isRunning ? "bg-indigo-500 animate-ping" : "bg-emerald-500")} />
                  <span className={isRunning ? "text-indigo-400 font-bold" : "text-emerald-400"}>
                    {isRunning ? 'Running' : 'Ready'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3 py-1">
            <span 
              className={cn("h-2.5 w-2.5 rounded-full", backendConnected ? "bg-emerald-500" : "bg-rose-500")} 
              title={backendConnected ? 'Backend Connected' : 'Backend Offline'} 
            />
            <span 
              className={cn("h-2.5 w-2.5 rounded-full", isRunning ? "bg-indigo-500 animate-pulse" : "bg-emerald-500")} 
              title={isRunning ? 'Pipeline Running' : 'Pipeline Ready'} 
            />
          </div>
        )}
      </div>
    </aside>
  );
}
