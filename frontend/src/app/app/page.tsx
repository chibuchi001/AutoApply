'use client';

import { useState } from 'react';
import { Zap, Activity } from 'lucide-react';

import { ProfileSetup, ProfileData } from '@/components/dashboard/ProfileSetup';
import { ResumeUpload } from '@/components/dashboard/ResumeUpload';
import { SearchConfigPanel, SearchConfig } from '@/components/dashboard/SearchConfig';
import { JobCard } from '@/components/dashboard/JobCard';
import { ApplicationTracker } from '@/components/dashboard/ApplicationTracker';
import { StatsBar } from '@/components/dashboard/StatsBar';
import { AgentFeed } from '@/components/agent/AgentFeed';
import { HumanEscalation } from '@/components/agent/HumanEscalation';
import { VoiceCoach } from '@/components/agent/VoiceCoach';
import { Card } from '@/components/ui/Card';
import { Stepper } from '@/components/ui/Stepper';
import { Alert } from '@/components/ui/Alert';

import { useAgentWebSocket } from '@/hooks/useAgentWebSocket';
import { autoApplyApi } from '@/lib/api';
import { JobListing, ResumeData, SearchResult } from '@/types';

const STEPS = [
  { id: 'profile', label: 'Profile' },
  { id: 'resume', label: 'Resume' },
  { id: 'search', label: 'Search' },
  { id: 'results', label: 'Results' },
];

interface EscalationState {
  jobTitle: string;
  company: string;
  devtoolsUrl?: string;
}

export default function HomePage() {
  const [userId, setUserId] = useState<string | null>(null);
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [searching, setSearching] = useState(false);
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [applyingJob, setApplyingJob] = useState<string | null>(null);
  const [refreshTracker, setRefreshTracker] = useState(0);
  const [error, setError] = useState('');
  const [escalation, setEscalation] = useState<EscalationState | null>(null);
  const [voiceCoachJob, setVoiceCoachJob] = useState<JobListing | null>(null);

  const completedSteps: string[] = [];
  if (userId) completedSteps.push('profile');
  if (resumeData) completedSteps.push('resume');
  if (searchResult) completedSteps.push('search');

  const currentStep = !userId ? 'profile' : !resumeData ? 'resume' : !searchResult ? 'search' : 'results';

  const { messages, connected, clearMessages } = useAgentWebSocket(userId);

  const handleProfileComplete = (uid: string) => setUserId(uid);

  const handleResumeComplete = (parsed: ResumeData) => setResumeData(parsed);

  const handleSearch = async (config: SearchConfig) => {
    if (!userId) return;
    setSearching(true);
    setError('');
    clearMessages();
    setSearchResult(null);
    try {
      const result = await autoApplyApi.searchJobs({
        user_id: userId,
        query: config.query,
        location: config.location,
        platforms: config.platforms,
        min_match_score: config.min_match_score,
        dry_run: config.dry_run,
      });
      setSearchResult(result);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Search failed. Is the backend running on port 8000?');
    } finally {
      setSearching(false);
    }
  };

  const handleApply = async (job: JobListing) => {
    if (!userId) return;
    setApplyingJob(job.url);
    setError('');
    try {
      await autoApplyApi.applyToJob(userId, job, true);
      setRefreshTracker((n) => n + 1);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Application failed');
    } finally {
      setApplyingJob(null);
    }
  };

  const sortedJobs = (searchResult?.matched_jobs ?? [])
    .slice()
    .sort((a, b) => (b.match_score ?? 0) - (a.match_score ?? 0));

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">

      {/* Header */}
      <header className="bg-white/80 backdrop-blur sticky top-0 z-50 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center shadow-sm">
              <Zap size={15} className="text-white" />
            </div>
            <div>
              <h1 className="font-bold text-gray-900 leading-none">AutoApply</h1>
              <p className="text-xs text-gray-500 leading-none mt-0.5">Powered by Amazon Nova</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden md:flex">
              <Stepper steps={STEPS} currentStep={currentStep} completedSteps={completedSteps} />
            </div>
            {userId && (
              <div className="flex items-center gap-1.5 text-xs text-gray-500">
                <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-gray-300'}`} />
                {connected ? 'Agent live' : 'Connecting…'}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">

        {error && (
          <div className="mb-6">
            <Alert type="error" message={error} onDismiss={() => setError('')} />
          </div>
        )}

        {escalation && (
          <div className="mb-6">
            <HumanEscalation
              jobTitle={escalation.jobTitle}
              company={escalation.company}
              devtoolsUrl={escalation.devtoolsUrl}
              onDismiss={() => setEscalation(null)}
            />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Left column */}
          <div className="lg:col-span-1 space-y-5">
            <ProfileSetup onComplete={handleProfileComplete} />
            {userId && (
              <ResumeUpload userId={userId} onComplete={handleResumeComplete} />
            )}
            {userId && resumeData && (
              <SearchConfigPanel onSearch={handleSearch} loading={searching} />
            )}
          </div>

          {/* Right column */}
          <div className="lg:col-span-2 space-y-5">

            {/* Welcome */}
            {!userId && (
              <Card className="text-center py-14">
                <div className="w-16 h-16 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-5">
                  <Zap size={30} className="text-indigo-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to AutoApply</h2>
                <p className="text-gray-500 text-sm max-w-sm mx-auto mb-8">
                  Upload your resume and let Amazon Nova Act apply to jobs across multiple platforms while you focus on what matters.
                </p>
                <div className="grid grid-cols-3 gap-4 max-w-sm mx-auto">
                  {[{ value: '3+', label: 'Job boards' }, { value: '40hrs', label: 'Time saved' }, { value: '100%', label: 'AI-powered' }].map(({ value, label }) => (
                    <div key={label} className="bg-indigo-50 rounded-xl p-3">
                      <p className="text-xl font-bold text-indigo-600">{value}</p>
                      <p className="text-xs text-indigo-500 mt-0.5">{label}</p>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Agent live feed */}
            {userId && (
              <Card padding="none">
                <div className="px-5 py-3 border-b border-gray-100 flex items-center gap-2">
                  <Activity size={16} className="text-indigo-600" />
                  <h2 className="text-sm font-semibold text-gray-900">Nova Act — Live Agent View</h2>
                </div>
                <div className="p-4">
                  <AgentFeed messages={messages} connected={connected} loading={searching} />
                </div>
              </Card>
            )}

            {/* Stats */}
            {searchResult && (
              <StatsBar
                totalFound={searchResult.total_found}
                matchedCount={searchResult.matched_count}
                platformsSearched={3}
              />
            )}

            {/* Job results */}
            {searchResult && sortedJobs.length > 0 && (
              <Card padding="none">
                <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-gray-900">
                    Matched Jobs ({sortedJobs.length})
                  </h2>
                  <p className="text-xs text-gray-400">Sorted by match score</p>
                </div>
                <div className="p-4 space-y-3 max-h-[640px] overflow-y-auto">
                  {sortedJobs.map((job, i) => (
                    <JobCard
                      key={`${job.url}-${i}`}
                      job={job}
                      onApply={handleApply}
                      isApplying={applyingJob === job.url}
                      onPracticeInterview={setVoiceCoachJob}
                    />
                  ))}
                </div>
              </Card>
            )}

            {searchResult && sortedJobs.length === 0 && (
              <Alert type="info" message="No jobs matched your criteria. Try lowering the minimum match score or broadening your search." />
            )}

            {/* Voice Interview Coach */}
            {voiceCoachJob && userId && resumeData && (
              <VoiceCoach
                job={voiceCoachJob}
                resumeSummary={`${resumeData.name} — ${resumeData.years_experience} years experience. Skills: ${resumeData.skills.slice(0, 10).join(', ')}.`}
                userId={userId}
                onClose={() => setVoiceCoachJob(null)}
              />
            )}

            {/* Application tracker */}
            {userId && (
              <ApplicationTracker userId={userId} refreshTrigger={refreshTracker} />
            )}
          </div>
        </div>
      </main>

      <footer className="mt-16 border-t border-gray-200 bg-white/50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between text-xs text-gray-400">
          <span>AutoApply — Amazon Nova Hackathon 2025</span>
          <span>#AmazonNova</span>
        </div>
      </footer>
    </div>
  );
}
