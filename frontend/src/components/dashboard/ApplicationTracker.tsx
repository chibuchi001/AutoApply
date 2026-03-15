'use client';

import { useEffect, useState } from 'react';
import { Briefcase, ExternalLink, RefreshCw } from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { StatusBadge, MatchBadge, PlatformBadge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { autoApplyApi } from '@/lib/api';
import { ApplicationStatus } from '@/types';

interface Application {
  session_id: string;
  title: string;
  company: string;
  platform: string;
  match_score: number;
  status: ApplicationStatus;
  url: string;
  confirmation?: string;
  applied_at?: string;
}

interface ApplicationTrackerProps {
  userId: string;
  refreshTrigger?: number;
}

export function ApplicationTracker({ userId, refreshTrigger }: ApplicationTrackerProps) {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const result = await autoApplyApi.getApplications(userId);
      setApplications(result.applications || []);
    } catch (e) {
      console.error('Failed to load applications', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [userId, refreshTrigger]);

  if (applications.length === 0 && !loading) {
    return null; // Don't show empty tracker
  }

  return (
    <Card padding="none">
      <div className="px-5 py-4 border-b border-gray-100">
        <CardHeader
          title={`Application Tracker (${applications.length})`}
          icon={<Briefcase size={18} />}
          action={
            <Button
              variant="ghost"
              size="sm"
              onClick={load}
              loading={loading}
              icon={<RefreshCw size={12} />}
            >
              Refresh
            </Button>
          }
        />
      </div>

      <div className="divide-y divide-gray-50 max-h-96 overflow-y-auto">
        {applications.map((app, i) => (
          <div key={`${app.session_id}-${i}`} className="px-5 py-3 hover:bg-gray-50 transition-colors">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-medium text-gray-900 truncate">{app.title}</p>
                  <StatusBadge status={app.status} />
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{app.company}</p>
                <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                  <PlatformBadge platform={app.platform} />
                  {app.match_score > 0 && <MatchBadge score={app.match_score} />}
                  {app.confirmation && (
                    <span className="text-xs text-gray-400">
                      Ref: {app.confirmation}
                    </span>
                  )}
                </div>
              </div>
              <a
                href={app.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-indigo-600 transition-colors shrink-0 mt-1"
              >
                <ExternalLink size={14} />
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* Stats bar */}
      <div className="px-5 py-3 bg-gray-50 border-t border-gray-100 flex gap-4 text-xs text-gray-500">
        <span>
          <strong className="text-green-600">
            {applications.filter((a) => a.status === 'submitted' || a.status === 'confirmed').length}
          </strong>{' '}
          submitted
        </span>
        <span>
          <strong className="text-yellow-600">
            {applications.filter((a) => a.status === 'pending_review').length}
          </strong>{' '}
          pending review
        </span>
        <span>
          <strong className="text-orange-600">
            {applications.filter((a) => a.status === 'requires_human').length}
          </strong>{' '}
          need attention
        </span>
      </div>
    </Card>
  );
}
