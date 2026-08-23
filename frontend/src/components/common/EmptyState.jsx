import React from 'react';
import { PackageOpen } from 'lucide-react';
import { Button } from './Button';

export function EmptyState({ title = "No data found", message, action, actionText = "Try Again", icon: Icon = PackageOpen }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center rounded-xl border border-dashed border-border bg-card/50">
      <div className="h-12 w-12 rounded-full bg-border/50 flex items-center justify-center mb-4">
        <Icon className="h-6 w-6 text-textMuted" />
      </div>
      <h3 className="text-lg font-semibold text-textMain mb-2">{title}</h3>
      <p className="text-textMuted max-w-md mb-6">{message}</p>
      {action && (
        <Button onClick={action}>
          {actionText}
        </Button>
      )}
    </div>
  );
}
