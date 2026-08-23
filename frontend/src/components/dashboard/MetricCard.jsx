import React from 'react';
import { Card, CardContent } from '../common/Card';
import { cn } from '../../utils/cn';

export function MetricCard({ title, value, subtitle, icon: Icon, color = "text-primary", bg = "bg-primary/10" }) {
  return (
    <Card className="hover:border-slate-700 transition-all duration-200">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs font-semibold text-textMuted uppercase tracking-wider">{title}</p>
            <p className="text-3xl font-extrabold tracking-tight text-textMain">{value}</p>
          </div>
          <div className={cn("h-12 w-12 rounded-xl flex items-center justify-center border border-slate-700/50 shadow-inner", bg)}>
            <Icon className={cn("h-6 w-6", color)} />
          </div>
        </div>
        <p className="text-xs font-medium text-textMuted mt-4 flex items-center gap-1">
          {subtitle}
        </p>
      </CardContent>
    </Card>
  );
}
