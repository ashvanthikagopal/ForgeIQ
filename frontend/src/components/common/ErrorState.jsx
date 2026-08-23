import React from 'react';
import { AlertCircle } from 'lucide-react';
import { Button } from './Button';

export function ErrorState({ title = "An error occurred", message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center rounded-xl border border-error/20 bg-error/5">
      <AlertCircle className="h-12 w-12 text-error mb-4" />
      <h3 className="text-lg font-semibold text-textMain mb-2">{title}</h3>
      <p className="text-textMuted max-w-md mb-6">{message}</p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </div>
  );
}
