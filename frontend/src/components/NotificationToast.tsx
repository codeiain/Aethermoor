import { useEffect, useState } from "react";
import { useGameStore, type Notification, type NotificationType } from "../store/useGameStore";

const NOTIFICATION_CONFIG: Record<NotificationType, { icon: string; color: string; duration: number }> = {
  quest_update: { icon: "📜", color: "#FFD700", duration: 8000 },
  party_invite: { icon: "⚔️", color: "#7CB9E8", duration: 30000 },
  trade_request: { icon: "💰", color: "#98FB98", duration: 15000 },
  guild_event: { icon: "🏰", color: "#9370DB", duration: 10000 },
  system: { icon: "⚙️", color: "#A0A0A0", duration: 5000 },
  whisper: { icon: "💬", color: "#FFB6C1", duration: 10000 },
};

export default function NotificationToast() {
  const notifications = useGameStore((s) => s.notifications);
  const unreadCount = useGameStore((s) => s.unreadCount);
  const dismiss = useGameStore((s) => s.dismissNotification);
  const markRead = useGameStore((s) => s.markNotificationRead);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [visibleToasts, setVisibleToasts] = useState<Notification[]>([]);

  useEffect(() => {
    const toShow = notifications.filter((n) => !n.read).slice(0, 3);
    setVisibleToasts(toShow);

    const timers: ReturnType<typeof setTimeout>[] = [];
    toShow.forEach((notif) => {
      const config = NOTIFICATION_CONFIG[notif.type];
      const timer = setTimeout(() => {
        dismiss(notif.id);
      }, config.duration);
      timers.push(timer);
    });

    return () => timers.forEach(clearTimeout);
  }, [notifications, dismiss]);

  const handleDismiss = (id: string) => {
    dismiss(id);
  };

  const handleToastClick = (notif: Notification) => {
    markRead(notif.id);
    if (notif.actionUrl) {
      console.log("Action URL:", notif.actionUrl);
    }
  };

  const isMobile = typeof window !== "undefined" && (window.matchMedia("(pointer: coarse)").matches || window.innerWidth < 768);

  return (
    <>
      <div style={S.bellBtn(isMobile)} onClick={() => setDrawerOpen(!drawerOpen)}>
        🔔
        {unreadCount > 0 && <span style={S.bellBadge}>{unreadCount > 9 ? "9+" : unreadCount}</span>}
      </div>

      <div style={S.toastContainer(isMobile)}>
        {visibleToasts.map((notif) => {
          const config = NOTIFICATION_CONFIG[notif.type];
          return (
            <div
              key={notif.id}
              style={S.toast(config.color)}
              onClick={() => handleToastClick(notif)}
            >
              <span style={S.toastIcon}>{config.icon}</span>
              <div style={S.toastContent}>
                <div style={S.toastTitle}>{notif.title}</div>
                <div style={S.toastBody}>{notif.body}</div>
              </div>
              <button style={S.toastDismiss} onClick={(e) => { e.stopPropagation(); handleDismiss(notif.id); }}>
                ×
              </button>
            </div>
          );
        })}
      </div>

      {drawerOpen && (
        <div style={S.drawer(isMobile)}>
          <div style={S.drawerHeader}>
            <span style={S.drawerTitle}>Notifications</span>
            <button style={S.drawerClose} onClick={() => setDrawerOpen(false)}>×</button>
          </div>
          <div style={S.drawerList}>
            {notifications.length === 0 ? (
              <div style={S.drawerEmpty}>No notifications</div>
            ) : (
              notifications.map((notif) => {
                const config = NOTIFICATION_CONFIG[notif.type];
                return (
                  <div
                    key={notif.id}
                    style={S.drawerItem(!notif.read)}
                    onClick={() => markRead(notif.id)}
                  >
                    <span style={S.drawerItemIcon}>{config.icon}</span>
                    <div style={S.drawerItemContent}>
                      <div style={S.drawerItemTitle}>{notif.title}</div>
                      <div style={S.drawerItemBody}>{notif.body}</div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </>
  );
}

export function addNotification(
  type: NotificationType,
  title: string,
  body: string,
  actionUrl?: string
) {
  const notif: Notification = {
    id: `notif-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    type,
    title,
    body,
    timestamp: Date.now() / 1000,
    read: false,
    actionUrl,
  };
  useGameStore.getState().addNotification(notif);
}

const S = {
  bellBtn: (isMobile: boolean): React.CSSProperties => ({
    position: "absolute" as const,
    top: isMobile ? 10 : 10,
    right: isMobile ? 60 : (typeof window !== "undefined" && window.innerWidth > 1024 ? 300 : 80),
    fontSize: 16,
    cursor: "pointer",
    zIndex: 35,
    padding: "6px 8px",
    background: "rgba(26, 26, 46, 0.9)",
    border: "1px solid #2a3a5a",
    borderRadius: 4,
  }),
  bellBadge: {
    position: "absolute" as const,
    top: -4,
    right: 0,
    background: "#cc4433",
    color: "#fff",
    fontSize: 6,
    fontFamily: "'Press Start 2P', monospace",
    padding: "2px 5px",
    borderRadius: 8,
  } as React.CSSProperties,
  toastContainer: (isMobile: boolean): React.CSSProperties => ({
    position: "absolute" as const,
    top: isMobile ? 50 : 10,
    right: 10,
    display: "flex",
    flexDirection: "column" as const,
    gap: 8,
    zIndex: 34,
    maxWidth: isMobile ? "100%" : 320,
  }),
  toast: (color: string): React.CSSProperties => ({
    background: "rgba(45, 45, 68, 0.98)",
    border: `2px solid ${color}`,
    borderRadius: 4,
    padding: "8px 12px",
    display: "flex",
    alignItems: "flex-start",
    gap: 8,
    cursor: "pointer",
    animation: "slideIn 0.3s ease-out",
  }),
  toastIcon: {
    fontSize: 14,
    flexShrink: 0,
  } as React.CSSProperties,
  toastContent: {
    flex: 1,
    minWidth: 0,
  },
  toastTitle: {
    fontSize: 7,
    fontFamily: "'Press Start 2P', monospace",
    color: "#e8e8e8",
    fontWeight: "bold" as const,
    marginBottom: 2,
  } as React.CSSProperties,
  toastBody: {
    fontSize: 6,
    fontFamily: "'Press Start 2P', monospace",
    color: "#a0a0a0",
    lineHeight: 1.4,
    display: "-webkit-box",
    WebkitLineClamp: 2,
    WebkitBoxOrient: "vertical" as const,
    overflow: "hidden",
  } as React.CSSProperties,
  toastDismiss: {
    background: "transparent",
    border: "none",
    color: "#667788",
    fontSize: 14,
    cursor: "pointer",
    padding: 0,
    lineHeight: 1,
  } as React.CSSProperties,
  drawer: (isMobile: boolean): React.CSSProperties => ({
    position: "absolute" as const,
    top: isMobile ? 0 : 10,
    right: isMobile ? 0 : 10,
    width: isMobile ? "100%" : 300,
    maxHeight: isMobile ? "60%" : "80%",
    background: "rgba(26, 26, 46, 0.98)",
    border: "2px solid #2a3a5a",
    borderRadius: isMobile ? 0 : 4,
    zIndex: 40,
    display: "flex",
    flexDirection: "column" as const,
    fontFamily: "'Press Start 2P', monospace",
  }),
  drawerHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "10px 12px",
    borderBottom: "1px solid #2a3a5a",
  },
  drawerTitle: {
    fontSize: 8,
    color: "#c8a84b",
  } as React.CSSProperties,
  drawerClose: {
    background: "transparent",
    border: "none",
    color: "#667788",
    fontSize: 16,
    cursor: "pointer",
  } as React.CSSProperties,
  drawerList: {
    flex: 1,
    overflowY: "auto" as const,
    padding: 8,
  },
  drawerEmpty: {
    color: "#445566",
    fontSize: 6,
    textAlign: "center" as const,
    marginTop: 20,
  },
  drawerItem: (isUnread: boolean): React.CSSProperties => ({
    display: "flex",
    gap: 8,
    padding: 8,
    background: isUnread ? "rgba(200, 168, 75, 0.1)" : "transparent",
    borderRadius: 3,
    cursor: "pointer",
    marginBottom: 4,
  }),
  drawerItemIcon: {
    fontSize: 12,
    flexShrink: 0,
  } as React.CSSProperties,
  drawerItemContent: {
    flex: 1,
    minWidth: 0,
  },
  drawerItemTitle: {
    fontSize: 6,
    color: "#e8e8e8",
    marginBottom: 2,
  } as React.CSSProperties,
  drawerItemBody: {
    fontSize: 5,
    color: "#778899",
    lineHeight: 1.3,
  } as React.CSSProperties,
};