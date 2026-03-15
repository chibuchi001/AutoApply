'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Square, Volume2 } from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { JobListing } from '@/types';

interface VoiceCoachProps {
  job: JobListing;
  resumeSummary: string;
  userId: string;
  onClose: () => void;
}

interface TranscriptLine {
  id: number;
  role: 'user' | 'assistant';
  text: string;
}

type SessionStatus = 'idle' | 'connecting' | 'active' | 'done' | 'error';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function VoiceCoach({ job, resumeSummary, userId, onClose }: VoiceCoachProps) {
  const [status, setStatus] = useState<SessionStatus>('idle');
  const [statusMsg, setStatusMsg] = useState('');
  const [transcript, setTranscript] = useState<TranscriptLine[]>([]);
  const [muted, setMuted] = useState(false);

  const wsRef      = useRef<WebSocket | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef  = useRef<MediaStream | null>(null);
  const nextIdRef  = useRef(0);
  const bottomRef  = useRef<HTMLDivElement | null>(null);
  // Keep a ref in sync so the ScriptProcessor closure always reads up-to-date value
  const mutedRef   = useRef(false);

  useEffect(() => { mutedRef.current = muted; }, [muted]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript]);

  const addLine = (role: 'user' | 'assistant', text: string) =>
    setTranscript((prev: TranscriptLine[]) => [...prev, { id: nextIdRef.current++, role, text }]);

  // ── Teardown all audio/WS resources ────────────────────────────────────────
  const teardown = useCallback(() => {
    processorRef.current?.disconnect();
    streamRef.current?.getTracks().forEach((t: MediaStreamTrack) => t.stop());
    audioCtxRef.current?.close().catch(() => {});
    wsRef.current?.close();
    processorRef.current = null;
    streamRef.current    = null;
    audioCtxRef.current  = null;
    wsRef.current        = null;
  }, []);

  useEffect(() => () => teardown(), [teardown]);

  // ── Decode base64 PCM and play it ──────────────────────────────────────────
  const playPcm = useCallback(async (b64: string) => {
    const ctx = audioCtxRef.current;
    if (!ctx) return;

    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);

    // 16-bit little-endian PCM → Float32
    const samples = bytes.length / 2;
    const buf = ctx.createBuffer(1, samples, 16000);
    const ch = buf.getChannelData(0);
    const view = new DataView(bytes.buffer);
    for (let i = 0; i < samples; i++) {
      ch[i] = view.getInt16(i * 2, true) / 32768;
    }

    const src = ctx.createBufferSource();
    src.buffer = buf;
    src.connect(ctx.destination);
    src.start();
  }, []);

  // ── Encode Float32 samples → base64 PCM safely ─────────────────────────────
  const encodeChunk = (f32: Float32Array): string => {
    const i16 = new Int16Array(f32.length);
    for (let i = 0; i < f32.length; i++) {
      i16[i] = Math.max(-32768, Math.min(32767, f32[i] * 32768));
    }
    const bytes = new Uint8Array(i16.buffer);
    let binary = '';
    // Convert in chunks to avoid call-stack limits; use Array.from so TypeScript
    // treats it as number[] (compatible with es5 target without --downlevelIteration)
    const CHUNK = 1024;
    for (let i = 0; i < bytes.length; i += CHUNK) {
      binary += String.fromCharCode(...Array.from(bytes.subarray(i, i + CHUNK)));
    }
    return btoa(binary);
  };

  // ── Start voice session ────────────────────────────────────────────────────
  const startSession = useCallback(async () => {
    setStatus('connecting');
    setTranscript([]);
    setStatusMsg('Connecting to Nova 2 Sonic…');

    try {
      const ctx = new AudioContext({ sampleRate: 16000 });
      audioCtxRef.current = ctx;

      const mic = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      streamRef.current = mic;

      const wsUrl = API_BASE.replace(/^http/, 'ws');
      const ws = new WebSocket(`${wsUrl}/api/voice/interview/${userId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        ws.send(JSON.stringify({
          type: 'start',
          job: {
            title:        job.title,
            company:      job.company,
            location:     job.location,
            requirements: job.requirements ?? [],
          },
          resume_summary: resumeSummary,
        }));
        setStatus('active');
        setStatusMsg('Connected — speak your answers when the coach asks a question');
      };

      ws.onmessage = async (e) => {
        const msg = JSON.parse(e.data as string);
        switch (msg.type) {
          case 'status':
            setStatusMsg(msg.message);
            break;
          case 'audio':
            await playPcm(msg.data);
            break;
          case 'transcript':
            addLine(msg.role as 'user' | 'assistant', msg.text);
            break;
          case 'done':
            setStatus('done');
            setStatusMsg('Session complete — great work!');
            teardown();
            break;
          case 'error':
            setStatus('error');
            setStatusMsg(`Error: ${msg.message}`);
            teardown();
            break;
        }
      };

      ws.onclose = () => setStatus((s: SessionStatus) => (s === 'active' ? 'done' : s));
      ws.onerror = () => {
        setStatus('error');
        setStatusMsg('Connection error — is the backend running on port 8000?');
      };

      // ── Capture mic PCM and stream to server ───────────────────────────────
      const source = ctx.createMediaStreamSource(mic);
      // ScriptProcessorNode is the most compatible option across browsers
      const proc = ctx.createScriptProcessor(4096, 1, 1);
      processorRef.current = proc;

      proc.onaudioprocess = (ev) => {
        if (mutedRef.current || ws.readyState !== WebSocket.OPEN) return;
        const b64 = encodeChunk(ev.inputBuffer.getChannelData(0));
        ws.send(JSON.stringify({ type: 'audio', data: b64 }));
      };

      source.connect(proc);
      proc.connect(ctx.destination);

    } catch (err: unknown) {
      setStatus('error');
      setStatusMsg(
        err instanceof Error ? err.message : 'Failed to start voice session'
      );
      teardown();
    }
  }, [job, resumeSummary, userId, playPcm, teardown]);

  // ── Stop session ────────────────────────────────────────────────────────────
  const stopSession = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'stop' }));
    }
    teardown();
    setStatus('done');
    setStatusMsg('Session ended');
  }, [teardown]);

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <Card>
      <CardHeader
        title="Voice Interview Coach"
        subtitle="Amazon Nova 2 Sonic — real-time speech AI"
        icon={<Volume2 size={18} />}
        action={
          <button
            onClick={onClose}
            className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close voice coach"
          >
            ✕ Close
          </button>
        }
      />

      <div className="space-y-4">

        {/* Job context */}
        <p className="text-xs text-gray-500">
          Practicing for{' '}
          <span className="font-semibold text-gray-700">{job.title}</span>
          {' '}at{' '}
          <span className="font-semibold text-gray-700">{job.company}</span>
        </p>

        {/* Status banner */}
        {statusMsg && (
          <p className={`text-sm px-3 py-2 rounded-lg ${
            status === 'error'
              ? 'bg-red-50 text-red-700'
              : status === 'done'
              ? 'bg-green-50 text-green-700'
              : status === 'active'
              ? 'bg-indigo-50 text-indigo-700'
              : 'bg-gray-50 text-gray-600'
          }`}>
            {statusMsg}
          </p>
        )}

        {/* Controls */}
        <div className="flex items-center gap-3 flex-wrap">
          {status === 'idle' || status === 'error' || status === 'done' ? (
            <Button onClick={startSession} icon={<Mic size={14} />}>
              {status === 'done' ? 'Practice Again' : 'Start Mock Interview'}
            </Button>
          ) : (
            <>
              <Button
                variant="danger"
                size="sm"
                onClick={stopSession}
                icon={<Square size={12} />}
              >
                End Session
              </Button>
              <button
                onClick={() => setMuted((m: boolean) => !m)}
                title={muted ? 'Unmute microphone' : 'Mute microphone'}
                className={`p-2 rounded-lg border transition-colors ${
                  muted
                    ? 'bg-red-50 border-red-200 text-red-600'
                    : 'bg-gray-50 border-gray-200 text-gray-500 hover:bg-gray-100'
                }`}
              >
                {muted ? <MicOff size={15} /> : <Mic size={15} />}
              </button>
              <span className="flex items-center gap-1.5 text-xs text-green-600 font-medium">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                Live
              </span>
            </>
          )}
        </div>

        {/* Transcript */}
        {transcript.length > 0 && (
          <div className="space-y-2 max-h-72 overflow-y-auto rounded-xl border border-gray-100 bg-gray-50 p-3">
            {transcript.map((line: TranscriptLine) => (
              <div
                key={line.id}
                className={`flex ${line.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`text-xs px-3 py-2 rounded-xl max-w-[85%] leading-relaxed ${
                  line.role === 'assistant'
                    ? 'bg-white border border-gray-200 text-gray-800'
                    : 'bg-indigo-600 text-white'
                }`}>
                  {line.text}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        )}

        {/* Hint when idle */}
        {status === 'idle' && (
          <p className="text-xs text-gray-400">
            Nova 2 Sonic will conduct a 4-question mock interview tailored to this role,
            give feedback after each answer, and close with coaching tips.
          </p>
        )}
      </div>
    </Card>
  );
}
