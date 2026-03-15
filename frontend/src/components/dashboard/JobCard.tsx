'use client';

import { useState } from 'react';
import { ExternalLink, ChevronDown, ChevronUp, Zap, Mic } from 'lucide-react';
import { MatchBadge, PlatformBadge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { JobListing } from '@/types';

interface JobCardProps {
  job: JobListing;
  onApply: (job: JobListing) => void;
  isApplying: boolean;
  onPracticeInterview?: (job: JobListing) => void;
}

export function JobCard({ job, onApply, isApplying, onPracticeInterview }: JobCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <h3 className="font-semibold text-gray-900 leading-tight">{job.title}</h3>
            {job.match_score !== undefined && <MatchBadge score={job.match_score} />}
          </div>
          <p className="text-sm text-gray-600">
            {job.company}
            {job.location && ` · ${job.location}`}
          </p>
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            <PlatformBadge platform={job.platform} />
            {job.salary_range && (
              <span className="text-xs text-gray-400">{job.salary_range}</span>
            )}
            {job.posted_date && (
              <span className="text-xs text-gray-400">{job.posted_date}</span>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2 shrink-0">
          <Button
            size="sm"
            onClick={() => onApply(job)}
            loading={isApplying}
            icon={<Zap size={12} />}
          >
            Apply
          </Button>
          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-1 px-3 py-1.5 text-xs border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            <ExternalLink size={11} /> View
          </a>
          {onPracticeInterview && (
            <button
              onClick={() => onPracticeInterview(job)}
              title="Practice interview with Nova 2 Sonic"
              className="inline-flex items-center justify-center gap-1 px-3 py-1.5 text-xs border border-purple-200 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors font-medium"
            >
              <Mic size={11} /> Practice
            </button>
          )}
        </div>
      </div>

      {/* Matching skills */}
      {job.matching_skills && job.matching_skills.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {job.matching_skills.slice(0, 6).map((skill) => (
            <span
              key={skill}
              className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full border border-green-100"
            >
              ✓ {skill}
            </span>
          ))}
          {job.matching_skills.length > 6 && (
            <span className="text-xs text-gray-400">
              +{job.matching_skills.length - 6} more
            </span>
          )}
        </div>
      )}

      {/* Expand toggle */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="mt-3 text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1 transition-colors"
      >
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        {expanded ? 'Less detail' : 'View coaching, cover letter & keywords'}
      </button>

      {/* Expanded panel */}
      {expanded && (
        <div className="mt-3 pt-3 border-t border-gray-100 space-y-4">

          {/* Skill gaps + AI coaching */}
          {job.skill_gaps && job.skill_gaps.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-700 mb-1.5">Skill Gaps</p>
              <div className="flex flex-wrap gap-1 mb-2">
                {job.skill_gaps.map((gap) => (
                  <span
                    key={gap}
                    className="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-full border border-red-100"
                  >
                    ✗ {gap}
                  </span>
                ))}
              </div>
              {job.skill_gap_coaching && (
                <div className="p-3 bg-amber-50 border border-amber-100 rounded-xl">
                  <p className="text-xs font-semibold text-amber-800 mb-1">
                    💡 AI Career Coaching
                  </p>
                  <p className="text-xs text-amber-700 leading-relaxed">
                    {job.skill_gap_coaching}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Cover letter */}
          {job.cover_letter && (
            <div>
              <p className="text-xs font-semibold text-gray-700 mb-1.5">
                Generated Cover Letter
              </p>
              <div className="bg-gray-50 rounded-xl p-3 text-xs text-gray-600 max-h-44 overflow-y-auto leading-relaxed border border-gray-100">
                {job.cover_letter}
              </div>
            </div>
          )}

          {/* ATS keywords */}
          {job.recommended_keywords && job.recommended_keywords.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-700 mb-1.5">
                ATS Keywords to Include
              </p>
              <div className="flex flex-wrap gap-1">
                {job.recommended_keywords.map((kw) => (
                  <span
                    key={kw}
                    className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full border border-blue-100"
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
