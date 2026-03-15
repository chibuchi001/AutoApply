import { ApplicationStatus } from '@/types';

interface BadgeProps {
  label: string;
  color?: 'green' | 'yellow' | 'red' | 'blue' | 'purple' | 'gray' | 'orange';
  size?: 'sm' | 'md';
}

const colorClasses = {
  green: 'bg-green-100 text-green-800 border-green-200',
  yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  red: 'bg-red-100 text-red-800 border-red-200',
  blue: 'bg-blue-100 text-blue-800 border-blue-200',
  purple: 'bg-purple-100 text-purple-800 border-purple-200',
  gray: 'bg-gray-100 text-gray-700 border-gray-200',
  orange: 'bg-orange-100 text-orange-800 border-orange-200',
};

export function Badge({ label, color = 'gray', size = 'sm' }: BadgeProps) {
  return (
    <span
      className={`
        inline-flex items-center font-medium border rounded-full
        ${size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1'}
        ${colorClasses[color]}
      `}
    >
      {label}
    </span>
  );
}

export function MatchBadge({ score }: { score: number }) {
  const color =
    score >= 80 ? 'green' : score >= 60 ? 'yellow' : 'red';
  return <Badge label={`${score}% match`} color={color} />;
}

export function PlatformBadge({ platform }: { platform: string }) {
  const colorMap: Record<string, 'blue' | 'purple' | 'green' | 'gray'> = {
    indeed: 'blue',
    linkedin: 'purple',
    glassdoor: 'green',
  };
  return (
    <Badge
      label={platform.charAt(0).toUpperCase() + platform.slice(1)}
      color={colorMap[platform] ?? 'gray'}
    />
  );
}

const statusConfig: Record<
  ApplicationStatus,
  { label: string; color: BadgeProps['color'] }
> = {
  discovered: { label: 'Discovered', color: 'gray' },
  matched: { label: 'Matched', color: 'blue' },
  cover_letter_ready: { label: 'Ready', color: 'purple' },
  pending_review: { label: 'Pending Review', color: 'yellow' },
  applying: { label: 'Applying…', color: 'orange' },
  submitted: { label: 'Submitted', color: 'green' },
  confirmed: { label: 'Confirmed', color: 'green' },
  rejected: { label: 'Rejected', color: 'red' },
  error: { label: 'Error', color: 'red' },
  requires_human: { label: 'Needs You', color: 'orange' },
};

export function StatusBadge({ status }: { status: ApplicationStatus }) {
  const cfg = statusConfig[status] ?? { label: status, color: 'gray' as const };
  return <Badge label={cfg.label} color={cfg.color} />;
}
