'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { AgentMessage } from '@/types';
import { createAgentWebSocket } from '@/lib/api';

export function useAgentWebSocket(userId: string | null) {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<AgentMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const pingRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!userId || wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = createAgentWebSocket(userId);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      // Keep-alive ping every 25 seconds
      pingRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 25000);
    };

    ws.onmessage = (event) => {
      try {
        const msg: AgentMessage = JSON.parse(event.data);
        if (msg.type === 'pong') return;

        const msgWithTime = { ...msg, timestamp: new Date().toISOString() };
        setLastMessage(msgWithTime);
        setMessages((prev) => [...prev.slice(-99), msgWithTime]); // Keep last 100
      } catch (e) {
        console.error('WebSocket message parse error:', e);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      if (pingRef.current) clearInterval(pingRef.current);
      // Reconnect after 3s
      setTimeout(() => connect(), 3000);
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };
  }, [userId]);

  useEffect(() => {
    connect();
    return () => {
      if (pingRef.current) clearInterval(pingRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const clearMessages = useCallback(() => setMessages([]), []);

  return { messages, connected, lastMessage, clearMessages };
}
