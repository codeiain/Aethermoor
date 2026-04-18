import { useState, useRef, useEffect, useCallback } from "react";
import { useGameStore, type ChatChannel, type ChatMessage } from "../store/useGameStore";

const CHANNEL_INFO: Record<ChatChannel, { icon: string; color: string; label: string; minLevel?: number }> = {
  global: { icon: "🌐", color: "#7CB9E8", label: "Global", minLevel: 3 },
  zone: { icon: "🗺️", color: "#98FB98", label: "Zone" },
  party: { icon: "⚔️", color: "#FFD700", label: "Party" },
  guild: { icon: "🏰", color: "#9370DB", label: "Guild" },
  whisper: { icon: "💬", color: "#FFB6C1", label: "Whispers" },
};

const PROFANITY_WORDS = ["badword1", "badword2"];

function filterProfanity(text: string): string {
  let filtered = text;
  for (const word of PROFANITY_WORDS) {
    const regex = new RegExp(word, "gi");
    filtered = filtered.replace(regex, "****");
  }
  return filtered;
}

function formatTime(ts: number): string {
  const date = new Date(ts * 1000);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function Chat({ sendChat }: { sendChat?: (message: string, channel: string) => void }) {
  const token = useGameStore((s) => s.token);
  const messages = useGameStore((s) => s.chatMessages);
  const channel = useGameStore((s) => s.chatChannel);
  const expanded = useGameStore((s) => s.chatExpanded);
  const activeChar = useGameStore((s) => s.activeCharacter);
  const addMessage = useGameStore((s) => s.addChatMessage);
  const setChannel = useGameStore((s) => s.setChatChannel);
  const setExpanded = useGameStore((s) => s.setChatExpanded);

  const [input, setInput] = useState("");
  const [isMobile, setIsMobile] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsMobile(window.matchMedia("(pointer: coarse)").matches || window.innerWidth < 768);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(() => {
    if (!input.trim() || !token || !activeChar) return;

    const msg: ChatMessage = {
      id: `msg-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      channel,
      sender: activeChar.id,
      senderName: activeChar.name,
      message: filterProfanity(input.trim().slice(0, 200)),
      timestamp: Date.now() / 1000,
    };

    if (sendChat) {
      sendChat(msg.message, channel);
    }
    addMessage(msg);
    setInput("");
  }, [input, token, activeChar, channel, addMessage, sendChat]);

  const handleChannelChange = useCallback((newChannel: ChatChannel) => {
    setChannel(newChannel);
    if (sendChat) {
      sendChat("", newChannel); // Empty message signals channel join
    }
  }, [setChannel, sendChat]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !isMobile) {
      e.preventDefault();
      handleSend();
    }
  };

  const filteredMessages = messages.filter((m) => m.channel === channel);

  const channels: ChatChannel[] = channel === "whisper" ? ["zone", "global", "party", "guild", "whisper"] : ["global", "zone", "party", "guild", "whisper"];

  if (!expanded) {
    return (
      <button style={S.collapsedBtn} onClick={() => setExpanded(true)}>
        <span style={S.collapsedIcon}>💬</span>
        {messages.length > 0 && <span style={S.collapsedBadge}>{messages.length}</span>}
      </button>
    );
  }

  return (
    <div style={S.chat(isMobile)}>
      <div style={S.header}>
        <div style={S.tabs}>
          {channels.map((ch) => {
            const info = CHANNEL_INFO[ch];
            const isActive = channel === ch;
            const isLocked = !!(info.minLevel && (activeChar?.level ?? 0) < info.minLevel);
            return (
              <button
                key={ch}
                style={S.tab(isActive, info.color, isLocked)}
                onClick={() => !isLocked && handleChannelChange(ch)}
                disabled={isLocked}
                title={isLocked ? `Unlocks at Lv.${info.minLevel}` : info.label}
              >
                {info.icon}
              </button>
            );
          })}
        </div>
        <button style={S.collapseBtn} onClick={() => setExpanded(false)}>−</button>
      </div>

      <div style={S.messages}>
        {filteredMessages.length === 0 ? (
          <div style={S.empty}>No messages yet</div>
        ) : (
          filteredMessages.map((msg) => {
            const info = CHANNEL_INFO[msg.channel];
            return (
              <div key={msg.id} style={S.messageRow}>
                {!isMobile && <span style={S.timestamp}>{formatTime(msg.timestamp)}</span>}
                <span style={S.sender(msg.sender === activeChar?.id ? "#c8a84b" : info.color)}>
                  {msg.senderName}:
                </span>
                <span style={S.text}>{msg.message}</span>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={S.inputRow}>
        <input
          style={S.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Say in ${CHANNEL_INFO[channel].label}...`}
          maxLength={200}
        />
        <button style={S.sendBtn} onClick={handleSend}>➤</button>
      </div>
    </div>
  );
}

const S = {
  chat: (isMobile: boolean): React.CSSProperties => ({
    position: "absolute" as const,
    bottom: isMobile ? 80 : 10,
    right: 10,
    width: isMobile ? "100%" : 300,
    maxHeight: isMobile ? 250 : 350,
    background: "rgba(26, 26, 46, 0.95)",
    border: "2px solid #2a3a5a",
    borderRadius: isMobile ? 0 : 4,
    display: "flex",
    flexDirection: "column" as const,
    fontFamily: "'Press Start 2P', monospace",
    zIndex: 30,
    ...(isMobile ? { left: 0, right: 0, borderRadius: 0 } : {}),
  }),
  collapsedBtn: {
    position: "absolute" as const,
    bottom: 80,
    right: 10,
    width: 44,
    height: 44,
    background: "rgba(26, 26, 46, 0.95)",
    border: "2px solid #2a3a5a",
    borderRadius: 22,
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 18,
    cursor: "pointer",
    zIndex: 30,
  } as React.CSSProperties,
  collapsedIcon: {
    fontSize: 24,
  } as React.CSSProperties,
  collapsedBadge: {
    position: "absolute" as const,
    top: -4,
    right: -4,
    background: "#cc4433",
    color: "#fff",
    fontSize: 14,
    padding: "2px 5px",
    borderRadius: 8,
  } as React.CSSProperties,
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "6px 8px",
    borderBottom: "1px solid #2a3a5a",
  },
  tabs: {
    display: "flex",
    gap: 6,
  },
  tab: (isActive: boolean, color: string, isLocked: boolean): React.CSSProperties => ({
    background: isActive ? color + "33" : "transparent",
    border: `1px solid ${isActive ? color : "#3a4a5a"}`,
    borderRadius: 3,
    padding: "4px 6px",
    fontSize: 18,
    cursor: isLocked ? "not-allowed" : "pointer",
    opacity: isLocked ? 0.5 : 1,
    transition: "background 0.15s",
  }),
  collapseBtn: {
    background: "transparent",
    border: "none",
    color: "#667788",
    fontSize: 14,
    cursor: "pointer",
    padding: "2px 6px",
  } as React.CSSProperties,
  messages: {
    flex: 1,
    overflowY: "auto" as const,
    padding: 8,
    display: "flex",
    flexDirection: "column" as const,
    gap: 4,
    minHeight: 100,
  },
  empty: {
    color: "#445566",
    fontSize: 14,
    textAlign: "center" as const,
    marginTop: 20,
  },
  messageRow: {
    fontSize: 14,
    lineHeight: 1.4,
    wordBreak: "break-word" as const,
  },
  timestamp: {
    color: "#556677",
    marginRight: 6,
  } as React.CSSProperties,
  sender: (color: string): React.CSSProperties => ({
    color,
    fontWeight: "bold" as const,
    marginRight: 4,
  }),
  text: {
    color: "#e8e8e8",
  } as React.CSSProperties,
  inputRow: {
    display: "flex",
    gap: 6,
    padding: 8,
    borderTop: "1px solid #2a3a5a",
  },
  input: {
    flex: 1,
    background: "#2d2d44",
    border: "1px solid #3a4a5a",
    borderRadius: 3,
    padding: "6px 8px",
    color: "#e8e8e8",
    fontSize: 14,
    fontFamily: "inherit",
    outline: "none",
  } as React.CSSProperties,
  sendBtn: {
    background: "#1a2233",
    border: "1px solid #2a3a4a",
    borderRadius: 3,
    padding: "4px 10px",
    color: "#8899aa",
    fontSize: 10,
    cursor: "pointer",
  } as React.CSSProperties,
};