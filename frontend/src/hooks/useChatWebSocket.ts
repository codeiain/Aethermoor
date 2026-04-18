import { useEffect, useRef, useCallback } from "react";
import { useGameStore, type ChatMessage, type Notification } from "../store/useGameStore";

interface WebSocketConfig {
  wsUrl: string;
  token: string;
  characterId: string;
  characterName: string;
  characterLevel: number;
}

interface UseChatWebSocketOptions {
  config: WebSocketConfig | null;
  enabled?: boolean;
}

export function useChatWebSocket({ config, enabled = true }: UseChatWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const addMessage = useGameStore((s) => s.addChatMessage);
  const addNotification = useGameStore((s) => s.addNotification);

  const connect = useCallback(() => {
    if (!config || wsRef.current?.readyState === WebSocket.OPEN) return;

    // Build WebSocket URL with query params, pass service token via header
    const wsUrl = `${config.wsUrl}/ws/${config.characterId}?token=${encodeURIComponent(config.token)}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("[ChatWS] Connected");
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === "chat") {
          const msg: ChatMessage = {
            id: `ws-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
            channel: data.channel || "zone",
            sender: data.from,
            senderName: data.senderName || data.from,
            message: data.message,
            timestamp: data.timestamp || Date.now() / 1000,
          };
          addMessage(msg);
        } else if (data.type === "notification") {
          const notif: Notification = {
            id: `ws-notif-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
            type: data.notificationType || "system",
            title: data.title,
            body: data.body,
            timestamp: Date.now() / 1000,
            read: false,
            actionUrl: data.actionUrl,
          };
          addNotification(notif);
        } else if (data.type === "heartbeat_ack") {
          // Heartbeat acknowledged
        }
      } catch (err) {
        console.warn("[ChatWS] Failed to parse message:", err);
      }
    };

    ws.onerror = (err) => {
      console.error("[ChatWS] Error:", err);
    };

    ws.onclose = () => {
      console.log("[ChatWS] Disconnected");
      wsRef.current = null;
      
      if (enabled && config) {
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log("[ChatWS] Reconnecting...");
          connect();
        }, 3000);
      }
    };

    wsRef.current = ws;
  }, [config, enabled, addMessage, addNotification]);

  const sendChat = useCallback((message: string, channel: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.warn("[ChatWS] Not connected, cannot send");
      return;
    }
    
    wsRef.current.send(JSON.stringify({
      type: "chat",
      message,
      channel,
    }));
  }, []);

  const joinChannel = useCallback((channel: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    
    wsRef.current.send(JSON.stringify({
      type: "join_channel",
      channel,
    }));
  }, []);

  const sendHeartbeat = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    
    wsRef.current.send(JSON.stringify({
      type: "heartbeat",
    }));
  }, []);

  useEffect(() => {
    if (enabled && config) {
      connect();
    }

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [config, enabled, connect]);

  useEffect(() => {
    if (!enabled || !wsRef.current) return;

    const interval = setInterval(() => {
      sendHeartbeat();
    }, 30000);

    return () => clearInterval(interval);
  }, [enabled, sendHeartbeat]);

  return {
    sendChat,
    joinChannel,
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
  };
}