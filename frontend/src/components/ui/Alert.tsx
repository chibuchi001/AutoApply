'use client';

import { AlertCircle, CheckCircle, Info, X, AlertTriangle } from 'lucide-react';
import { ReactNode } from 'react';

type AlertType = 'error' | 'success' | 'info' | 'warning';

const alertConfig = {
  error: {
    bg: 'bg-red-50 border-red-200',
    text: 'text-red-700',
    icon: <AlertCircle size={16} className="text-red-500 shrink-0 mt-0.5" />,
  },
  success: {
    bg: 'bg-green-50 border-green-200',
    text: 'text-green-700',
    icon: <CheckCircle size={16} className="text-green-500 shrink-0 mt-0.5" />,
  },
  info: {
    bg: 'bg-blue-50 border-blue-200',
    text: 'text-blue-700',
    icon: <Info size={16} className="text-blue-500 shrink-0 mt-0.5" />,
  },
  warning: {
    bg: 'bg-amber-50 border-amber-200',
    text: 'text-amber-700',
    icon: <AlertTriangle size={16} className="text-amber-500 shrink-0 mt-0.5" />,
  },
};

interface AlertProps {
  type?: AlertType;
  message: string;
  onDismiss?: () => void;
}

export function Alert({ type = 'info', message, onDismiss }: AlertProps) {
  const cfg = alertConfig[type];
  return (
    <div className={`flex items-start gap-3 border rounded-xl p-4 ${cfg.bg}`}>
      {cfg.icon}
      <p className={`text-sm flex-1 ${cfg.text}`}>{message}</p>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className={`${cfg.text} opacity-60 hover:opacity-100 transition-opacity`}
        >
          <X size={14} />
        </button>
      )}
    </div>
  );
}
