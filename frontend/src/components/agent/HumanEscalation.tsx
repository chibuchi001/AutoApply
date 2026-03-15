'use client';

import { AlertTriangle, ExternalLink, X } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface HumanEscalationProps {
  jobTitle: string;
  company: string;
  devtoolsUrl?: string;
  onDismiss: () => void;
}

export function HumanEscalation({
  jobTitle,
  company,
  devtoolsUrl,
  onDismiss,
}: HumanEscalationProps) {
  return (
    <div className="bg-orange-50 border-2 border-orange-300 rounded-2xl p-5 shadow-md">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-orange-100 rounded-xl flex items-center justify-center shrink-0">
          <AlertTriangle size={20} className="text-orange-600" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-orange-900 text-sm">Human Intervention Required</h3>
          <p className="text-xs text-orange-700 mt-1">
            A CAPTCHA was detected while applying to{' '}
            <strong>{jobTitle}</strong> at <strong>{company}</strong>.
            Click the link below to take control of the browser session and solve it.
          </p>
          {devtoolsUrl && (
            <a
              href={devtoolsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 mt-3 px-4 py-2 bg-orange-600 text-white text-xs font-semibold rounded-lg hover:bg-orange-700 transition-colors"
            >
              <ExternalLink size={12} />
              Open Browser Session
            </a>
          )}
        </div>
        <button
          onClick={onDismiss}
          className="text-orange-400 hover:text-orange-600 transition-colors"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
}
