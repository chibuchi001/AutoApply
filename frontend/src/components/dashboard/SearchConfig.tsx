'use client';

import { useState } from 'react';
import { Search, Zap } from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export interface SearchConfig {
  query: string;
  location: string;
  platforms: string[];
  min_match_score: number;
  dry_run: boolean;
  max_applications: number;
}

interface SearchConfigPanelProps {
  onSearch: (config: SearchConfig) => void;
  loading: boolean;
}

const PLATFORMS = [
  { id: 'indeed', label: 'Indeed' },
  { id: 'linkedin', label: 'LinkedIn' },
  { id: 'glassdoor', label: 'Glassdoor' },
];

export function SearchConfigPanel({ onSearch, loading }: SearchConfigPanelProps) {
  const [config, setConfig] = useState<SearchConfig>({
    query: '',
    location: '',
    platforms: ['indeed', 'linkedin', 'glassdoor'],
    min_match_score: 60,
    dry_run: true,
    max_applications: 5,
  });

  const togglePlatform = (id: string) => {
    setConfig((p) => ({
      ...p,
      platforms: p.platforms.includes(id)
        ? p.platforms.filter((x) => x !== id)
        : [...p.platforms, id],
    }));
  };

  const canSearch = config.query.trim() && config.location.trim() && config.platforms.length > 0;

  return (
    <Card>
      <CardHeader title="Job Search" icon={<Search size={18} />} />

      <div className="space-y-4">
        <Input
          label="Job Title"
          required
          placeholder="e.g. .NET Developer"
          value={config.query}
          onChange={(e) => setConfig((p) => ({ ...p, query: e.target.value }))}
        />
        <Input
          label="Location"
          required
          placeholder="e.g. Lagos, Nigeria"
          value={config.location}
          onChange={(e) => setConfig((p) => ({ ...p, location: e.target.value }))}
        />

        {/* Platform toggles */}
        <div>
          <p className="text-xs font-medium text-gray-700 mb-2">Platforms</p>
          <div className="flex gap-2 flex-wrap">
            {PLATFORMS.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => togglePlatform(p.id)}
                className={`
                  text-xs px-3 py-1.5 rounded-lg border font-medium transition-colors
                  ${config.platforms.includes(p.id)
                    ? 'bg-indigo-600 text-white border-indigo-600'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-indigo-300'}
                `}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Match score slider */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <p className="text-xs font-medium text-gray-700">Min match score</p>
            <span className="text-xs font-bold text-indigo-600">{config.min_match_score}%</span>
          </div>
          <input
            type="range"
            min={40}
            max={90}
            step={5}
            value={config.min_match_score}
            onChange={(e) =>
              setConfig((p) => ({ ...p, min_match_score: Number(e.target.value) }))
            }
            className="w-full accent-indigo-600 cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-0.5">
            <span>40% (more results)</span>
            <span>90% (strict)</span>
          </div>
        </div>

        {/* Max applications */}
        <div>
          <p className="text-xs font-medium text-gray-700 mb-1">
            Max applications: {config.max_applications}
          </p>
          <input
            type="range"
            min={1}
            max={20}
            step={1}
            value={config.max_applications}
            onChange={(e) =>
              setConfig((p) => ({ ...p, max_applications: Number(e.target.value) }))
            }
            className="w-full accent-indigo-600 cursor-pointer"
          />
        </div>

        {/* Demo mode toggle */}
        <label className="flex items-start gap-3 cursor-pointer group">
          <div className="relative mt-0.5">
            <input
              type="checkbox"
              checked={config.dry_run}
              onChange={(e) => setConfig((p) => ({ ...p, dry_run: e.target.checked }))}
              className="sr-only"
            />
            <div
              className={`w-9 h-5 rounded-full transition-colors ${
                config.dry_run ? 'bg-amber-500' : 'bg-gray-300'
              }`}
            />
            <div
              className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                config.dry_run ? 'translate-x-4' : 'translate-x-0.5'
              }`}
            />
          </div>
          <div>
            <p className="text-xs font-medium text-gray-700">Demo mode</p>
            <p className="text-xs text-gray-400">
              {config.dry_run
                ? 'Fills forms but does NOT submit — safe for testing'
                : 'LIVE — will submit real applications'}
            </p>
          </div>
        </label>

        {!config.dry_run && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700">
            ⚠️ Live mode enabled — applications will be submitted for real. Make sure your profile and resume are complete.
          </div>
        )}

        <Button
          className="w-full"
          size="lg"
          onClick={() => onSearch(config)}
          loading={loading}
          disabled={!canSearch}
          icon={<Zap size={16} />}
        >
          {loading ? 'Searching…' : 'Launch Agent'}
        </Button>
      </div>
    </Card>
  );
}
