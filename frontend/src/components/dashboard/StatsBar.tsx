import { Search, CheckCircle, Briefcase, Clock } from 'lucide-react';

interface StatsBarProps {
  totalFound: number;
  matchedCount: number;
  platformsSearched: number;
  applicationsSubmitted?: number;
}

export function StatsBar({
  totalFound,
  matchedCount,
  platformsSearched,
  applicationsSubmitted = 0,
}: StatsBarProps) {
  const stats = [
    { label: 'Jobs Found', value: totalFound, icon: Search, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Matched', value: matchedCount, icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50' },
    { label: 'Platforms', value: platformsSearched, icon: Briefcase, color: 'text-purple-600', bg: 'bg-purple-50' },
    { label: 'Applied', value: applicationsSubmitted, icon: Clock, color: 'text-indigo-600', bg: 'bg-indigo-50' },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {stats.map(({ label, value, icon: Icon, color, bg }) => (
        <div
          key={label}
          className="bg-white rounded-xl border border-gray-200 p-4 text-center shadow-sm"
        >
          <div className={`w-9 h-9 ${bg} rounded-xl flex items-center justify-center mx-auto mb-2`}>
            <Icon size={18} className={color} />
          </div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-xs text-gray-500 mt-0.5">{label}</p>
        </div>
      ))}
    </div>
  );
}
