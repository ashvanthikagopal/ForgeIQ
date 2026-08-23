export const STATUS_COLORS = {
  PASSED: {
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    border: 'border-emerald-500/30',
    badge: 'bg-emerald-500 text-white',
  },
  REVIEW: {
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    border: 'border-amber-500/30',
    badge: 'bg-amber-500 text-white',
  },
  FAILED: {
    bg: 'bg-rose-500/10',
    text: 'text-rose-400',
    border: 'border-rose-500/30',
    badge: 'bg-rose-500 text-white',
  },
  UNKNOWN: {
    bg: 'bg-slate-500/10',
    text: 'text-slate-400',
    border: 'border-slate-500/30',
    badge: 'bg-slate-600 text-white',
  },
};

export const SEVERITY_COLORS = {
  high: {
    bg: 'bg-rose-500/10',
    text: 'text-rose-400',
    border: 'border-rose-500/30',
    badge: 'bg-rose-500 text-white',
  },
  medium: {
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    border: 'border-amber-500/30',
    badge: 'bg-amber-500 text-white',
  },
  low: {
    bg: 'bg-blue-500/10',
    text: 'text-blue-400',
    border: 'border-blue-500/30',
    badge: 'bg-blue-500 text-white',
  },
};

export function getStatusStyle(status) {
  if (!status) return STATUS_COLORS.UNKNOWN;
  const key = status.toUpperCase();
  return STATUS_COLORS[key] || STATUS_COLORS.UNKNOWN;
}

export function getSeverityStyle(severity) {
  if (!severity) return SEVERITY_COLORS.low;
  const key = severity.toLowerCase();
  return SEVERITY_COLORS[key] || SEVERITY_COLORS.low;
}
