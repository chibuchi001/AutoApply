'use client';

import { useEffect, useRef } from 'react';
import { Bot, Wifi, WifiOff } from 'lucide-react';
import { AgentMessage } from '@/types';

interface AgentFeedProps {
  messages: AgentMessage[];
  connected: boolean;
  loading?: boolean;
}

function getMessageColor(msg: AgentMessage): string {
  if (msg.type === 'application_submitted') return 'text-green-400';
  if (msg.type === 'human_required' || msg.type === 'captcha_detected') return 'text-orange-400';
  if (msg.status === 'error') return 'text-red-400';
  if (msg.status === 'complete') return 'text-green-400';
  if (msg.type === 'job_matched') return 'text-yellow-400';
  if (msg.type === 'search_started' || msg.type === 'search_complete') return 'text-cyan-400';
  if (msg.type === 'cover_letter_ready') return 'text-purple-400';
  return 'text-blue-400';
}

function getTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    connected: 'CONNECTED',
    search_started: 'SEARCH',
    search_complete: 'SEARCH',
    agent_status: 'AGENT',
    job_matched: 'MATCH',
    matching_started: 'MATCH',
    matching_complete: 'MATCH',
    cover_letter_generating: 'COVER',
    cover_letter_ready: 'COVER',
    application_starting: 'APPLY',
    application_progress: 'APPLY',
    application_submitted: 'SUBMIT',
    human_required: 'HUMAN',
    captcha_detected: 'CAPTCHA',
    pipeline_complete: 'DONE',
    error: 'ERROR',
  };
  return labels[type] || type.toUpperCase().slice(0, 8);
}

export function AgentFeed({ messages, connected, loading }: AgentFeedProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const relevant = messages.filter((m) => m.type !== 'pong');

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  return (
    <div className="bg-gray-950 rounded-xl overflow-hidden">
      {/* Terminal header */}
      <div className="flex items-center gap-2 px-4 py-2.5 bg-gray-900 border-b border-gray-800">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-red-500/70" />
          <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
          <div className="w-3 h-3 rounded-full bg-green-500/70" />
        </div>
        <div className="flex items-center gap-2 ml-2">
          <Bot size={13} className="text-green-400" />
          <span className="text-xs font-mono text-green-400 font-semibold">
            nova-act — live agent feed
          </span>
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          {connected ? (
            <>
              <Wifi size={11} className="text-green-400" />
              <span className="text-xs text-green-400 font-mono">connected</span>
            </>
          ) : (
            <>
              <WifiOff size={11} className="text-gray-500" />
              <span className="text-xs text-gray-500 font-mono">disconnected</span>
            </>
          )}
          {loading && (
            <span className="ml-2 text-xs text-yellow-400 font-mono animate-pulse">
              running…
            </span>
          )}
        </div>
      </div>

      {/* Log output */}
      <div className="h-72 overflow-y-auto p-4 font-mono text-xs space-y-1">
        {relevant.length === 0 ? (
          <p className="text-gray-600 text-center mt-16">
            Waiting for agent activity…
          </p>
        ) : (
          relevant.slice(-80).map((msg, i) => (
            <div key={i} className="flex gap-2 items-start leading-relaxed">
              <span className="text-gray-600 shrink-0 tabular-nums">
                {msg.timestamp
                  ? new Date(msg.timestamp).toLocaleTimeString('en-US', {
                      hour12: false,
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit',
                    })
                  : '--:--:--'}
              </span>
              <span className={`shrink-0 w-16 ${getMessageColor(msg)}`}>
                [{getTypeLabel(msg.type)}]
              </span>
              <span className="text-gray-300 break-all">
                {msg.message || ''}
                {msg.match_score !== undefined && (
                  <span className="text-yellow-400"> ({msg.match_score}%)</span>
                )}
                {msg.platform && (
                  <span className="text-gray-500"> [{msg.platform}]</span>
                )}
                {msg.progress && (
                  <span className="text-gray-500"> {msg.progress}</span>
                )}
              </span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
