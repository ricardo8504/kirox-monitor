import { useEffect, useRef, useCallback } from "react";
import type { WsMessage } from "@/types";

interface UseWebSocketOptions {
  onMessage: (msg: WsMessage) => void;
  enabled?: boolean;
}

function getWsBaseUrl(): string {
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}`;
}

export function useServerMetricsWs(serverId: string, token: string, opts: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const { onMessage, enabled = true } = opts;

  const connect = useCallback(() => {
    if (!enabled || !token) return;
    const url = `${getWsBaseUrl()}/ws/metrics/${serverId}?token=${token}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onmessage = (e) => {
      try {
        onMessage(JSON.parse(e.data) as WsMessage);
      } catch {
        // ignore malformed frames
      }
    };

    ws.onclose = () => {
      reconnectTimer.current = setTimeout(connect, 3000);
    };
  }, [serverId, token, enabled, onMessage]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connect]);
}

export function useAlertsWs(token: string, opts: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const { onMessage, enabled = true } = opts;

  const connect = useCallback(() => {
    if (!enabled || !token) return;
    const url = `${getWsBaseUrl()}/ws/alerts?token=${token}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onmessage = (e) => {
      try {
        onMessage(JSON.parse(e.data) as WsMessage);
      } catch {
        // ignore malformed frames
      }
    };

    ws.onclose = () => {
      reconnectTimer.current = setTimeout(connect, 3000);
    };
  }, [token, enabled, onMessage]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connect]);
}
