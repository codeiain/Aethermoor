import { useState, useEffect, useRef } from "react";
import {
  getGuildForCharacter,
  getGuildRoster,
  getGuildByName,
  createGuild,
  sendGuildInvite,
  acceptGuildInvite,
  declineGuildInvite,
  leaveGuild,
  kickGuildMember,
  promoteGuildMember,
  demoteGuildMember,
  setGuildMotd,
  postGuildChat,
  getGuildChatHistory,
  type GuildMember,
  type GuildChatMessage,
} from "../api/client";
import { useGameStore } from "../store/useGameStore";

interface Props {
  onClose: () => void;
}

type Tab = "roster" | "chat" | "admin";

const ROLE_LABEL: Record<string, string> = {
  leader: "★",
  officer: "◆",
  member: "·",
};

export default function GuildPanel({ onClose }: Props) {
  const token = useGameStore((s) => s.token);
  const char = useGameStore((s) => s.activeCharacter);
  const guild = useGameStore((s) => s.guild);
  const pendingInvites = useGameStore((s) => s.pendingGuildInvites);
  const setGuild = useGameStore((s) => s.setGuild);
  const removePendingGuildInvite = useGameStore((s) => s.removePendingGuildInvite);

  const [tab, setTab] = useState<Tab>("roster");
  const [roster, setRoster] = useState<GuildMember[]>([]);
  const [chatMessages, setChatMessages] = useState<GuildChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [motdEdit, setMotdEdit] = useState("");
  const [editingMotd, setEditingMotd] = useState(false);
  const [inviteTargetId, setInviteTargetId] = useState("");
  const [searchName, setSearchName] = useState("");
  const [createName, setCreateName] = useState("");
  const [createTag, setCreateTag] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const myRole = roster.find((m) => m.character_id === char?.id)?.role ?? "member";
  const isLeader = myRole === "leader";
  const isOfficerOrLeader = isLeader || myRole === "officer";

  useEffect(() => {
    if (!token || !char) return;
    getGuildForCharacter(token, char.id)
      .then((g) => { setGuild(g); if (g) setMotdEdit(g.motd ?? ""); })
      .catch(() => {});
  }, [token, char?.id]);

  useEffect(() => {
    if (!token || !guild) return;
    getGuildRoster(token, guild.guild_id)
      .then((r) => setRoster(r.members))
      .catch(() => {});
  }, [token, guild?.guild_id]);

  useEffect(() => {
    if (!token || !guild || tab !== "chat") return;
    getGuildChatHistory(token, guild.guild_id)
      .then(setChatMessages)
      .catch(() => {});
  }, [token, guild?.guild_id, tab]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  async function handleCreate() {
    if (!token || !char || !createName.trim() || !createTag.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const g = await createGuild(token, createName.trim(), createTag.trim(), char.id, char.name);
      setGuild(g);
      setMotdEdit(g.motd ?? "");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create guild");
    } finally {
      setBusy(false);
    }
  }

  async function handleSearch() {
    if (!token || !searchName.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const g = await getGuildByName(token, searchName.trim());
      setError(`Found: ${g.name} [${g.tag}] — ${g.member_count} members`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Guild not found");
    } finally {
      setBusy(false);
    }
  }

  async function handleInvite() {
    if (!token || !char || !guild || !inviteTargetId.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await sendGuildInvite(token, guild.guild_id, char.id, char.name, inviteTargetId.trim());
      setInviteTargetId("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send invite");
    } finally {
      setBusy(false);
    }
  }

  async function handleAcceptInvite(inviteId: string) {
    if (!token || !char) return;
    setBusy(true);
    setError(null);
    try {
      const g = await acceptGuildInvite(token, inviteId, char.id, char.name);
      setGuild(g);
      removePendingGuildInvite(inviteId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to accept invite");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeclineInvite(inviteId: string) {
    if (!token || !char) return;
    setBusy(true);
    setError(null);
    try {
      await declineGuildInvite(token, inviteId, char.id);
      removePendingGuildInvite(inviteId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to decline invite");
    } finally {
      setBusy(false);
    }
  }

  async function handleLeave() {
    if (!token || !char || !guild) return;
    setBusy(true);
    setError(null);
    try {
      await leaveGuild(token, guild.guild_id, char.id);
      setGuild(null);
      setRoster([]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to leave guild");
    } finally {
      setBusy(false);
    }
  }

  async function handleKick(targetId: string) {
    if (!token || !char || !guild) return;
    setBusy(true);
    setError(null);
    try {
      await kickGuildMember(token, guild.guild_id, char.id, targetId);
      const r = await getGuildRoster(token, guild.guild_id);
      setRoster(r.members);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to kick member");
    } finally {
      setBusy(false);
    }
  }

  async function handlePromote(targetId: string) {
    if (!token || !char || !guild) return;
    setBusy(true);
    setError(null);
    try {
      await promoteGuildMember(token, guild.guild_id, char.id, targetId, "officer");
      const r = await getGuildRoster(token, guild.guild_id);
      setRoster(r.members);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to promote");
    } finally {
      setBusy(false);
    }
  }

  async function handleDemote(targetId: string) {
    if (!token || !char || !guild) return;
    setBusy(true);
    setError(null);
    try {
      await demoteGuildMember(token, guild.guild_id, char.id, targetId);
      const r = await getGuildRoster(token, guild.guild_id);
      setRoster(r.members);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to demote");
    } finally {
      setBusy(false);
    }
  }

  async function handleSaveMotd() {
    if (!token || !char || !guild) return;
    setBusy(true);
    setError(null);
    try {
      const g = await setGuildMotd(token, guild.guild_id, char.id, motdEdit);
      setGuild(g);
      setEditingMotd(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to set MOTD");
    } finally {
      setBusy(false);
    }
  }

  async function handleSendChat() {
    if (!token || !char || !guild || !chatInput.trim()) return;
    setBusy(true);
    try {
      const msg = await postGuildChat(token, guild.guild_id, char.id, char.name, chatInput.trim());
      setChatMessages((prev) => [...prev, msg]);
      setChatInput("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send message");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={S.overlay}>
      <div style={S.panel}>
        <div style={S.header}>
          <span style={S.title}>
            {guild ? `[${guild.tag}] ${guild.name}` : "GUILD"}
          </span>
          <button style={S.closeBtn} onClick={onClose}>✕</button>
        </div>

        {error && <div style={S.error}>{error}</div>}

        {/* Pending invites */}
        {pendingInvites.length > 0 && (
          <div style={S.section}>
            <div style={S.sectionLabel}>GUILD INVITES</div>
            {pendingInvites.map((inv) => (
              <div key={inv.invite_id} style={S.inviteRow}>
                <span style={S.inviteName}>{inv.guild_name} — from {inv.inviter_name}</span>
                <button style={S.acceptBtn} onClick={() => handleAcceptInvite(inv.invite_id)} disabled={busy}>Accept</button>
                <button style={S.declineBtn} onClick={() => handleDeclineInvite(inv.invite_id)} disabled={busy}>Decline</button>
              </div>
            ))}
          </div>
        )}

        {!guild ? (
          <div style={S.noGuild}>
            {/* Create */}
            <div style={S.sectionLabel}>CREATE GUILD</div>
            <div style={S.row}>
              <input style={S.input} placeholder="Name (3-24 chars)" value={createName} onChange={(e) => setCreateName(e.target.value)} />
              <input style={{ ...S.input, maxWidth: 70 }} placeholder="Tag" value={createTag} onChange={(e) => setCreateTag(e.target.value)} />
            </div>
            <button style={S.createBtn} onClick={handleCreate} disabled={busy || !createName.trim() || !createTag.trim()}>
              {busy ? "..." : "Create Guild"}
            </button>

            {/* Search */}
            <div style={{ ...S.sectionLabel, marginTop: 12 }}>SEARCH GUILD</div>
            <div style={S.row}>
              <input style={S.input} placeholder="Guild name" value={searchName} onChange={(e) => setSearchName(e.target.value)} />
              <button style={S.smallBtn2} onClick={handleSearch} disabled={busy}>Search</button>
            </div>
          </div>
        ) : (
          <>
            {/* MOTD */}
            {guild.motd && !editingMotd && (
              <div style={S.motd}>
                <span style={S.motdLabel}>MOTD</span>
                <span style={S.motdText}>{guild.motd}</span>
                {isOfficerOrLeader && (
                  <button style={S.tinyBtn} onClick={() => setEditingMotd(true)}>edit</button>
                )}
              </div>
            )}
            {editingMotd && (
              <div style={S.motdEditRow}>
                <input style={S.input} value={motdEdit} onChange={(e) => setMotdEdit(e.target.value)} maxLength={256} />
                <button style={S.smallBtn2} onClick={handleSaveMotd} disabled={busy}>Save</button>
                <button style={S.tinyBtn} onClick={() => setEditingMotd(false)}>cancel</button>
              </div>
            )}

            {/* Tabs */}
            <div style={S.tabs}>
              {(["roster", "chat", "admin"] as Tab[]).map((t) => (
                <button key={t} style={tab === t ? S.tabActive : S.tab} onClick={() => setTab(t)}>
                  {t.toUpperCase()}
                </button>
              ))}
            </div>

            {tab === "roster" && (
              <div style={S.section}>
                <div style={S.sectionLabel}>MEMBERS ({roster.length})</div>
                <div style={S.rosterList}>
                  {roster.map((m) => (
                    <div key={m.character_id} style={S.memberRow}>
                      <span style={S.roleIcon}>{ROLE_LABEL[m.role] ?? "·"}</span>
                      <span style={S.memberName}>{m.character_name}</span>
                      <span style={S.roleBadge}>{m.role}</span>
                      {isOfficerOrLeader && m.character_id !== char?.id && (
                        <div style={S.memberActions}>
                          {isLeader && m.role !== "officer" && (
                            <button style={S.smallBtn} onClick={() => handlePromote(m.character_id)} disabled={busy}>+</button>
                          )}
                          {isLeader && m.role === "officer" && (
                            <button style={S.smallBtn} onClick={() => handleDemote(m.character_id)} disabled={busy}>-</button>
                          )}
                          <button style={S.kickBtn} onClick={() => handleKick(m.character_id)} disabled={busy}>kick</button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                {isOfficerOrLeader && (
                  <div style={S.inviteInputRow}>
                    <input style={S.input} placeholder="Invite by character ID" value={inviteTargetId} onChange={(e) => setInviteTargetId(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleInvite()} />
                    <button style={S.inviteBtn} onClick={handleInvite} disabled={busy || !inviteTargetId.trim()}>Invite</button>
                  </div>
                )}
              </div>
            )}

            {tab === "chat" && (
              <div style={S.section}>
                <div style={S.chatBox}>
                  {chatMessages.map((m) => (
                    <div key={m.message_id} style={S.chatMsg}>
                      <span style={S.chatAuthor}>{m.author_name}:</span>
                      <span style={S.chatText}> {m.message}</span>
                    </div>
                  ))}
                  <div ref={chatEndRef} />
                </div>
                <div style={S.chatInputRow}>
                  <input
                    style={S.input}
                    placeholder="Message..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
                  />
                  <button style={S.inviteBtn} onClick={handleSendChat} disabled={busy || !chatInput.trim()}>Send</button>
                </div>
              </div>
            )}

            {tab === "admin" && (
              <div style={S.section}>
                <div style={S.sectionLabel}>MANAGE</div>
                {!editingMotd && isOfficerOrLeader && (
                  <button style={S.smallBtn2} onClick={() => setEditingMotd(true)}>Edit MOTD</button>
                )}
                <button style={S.leaveBtn} onClick={handleLeave} disabled={busy}>Leave Guild</button>
              </div>
            )}

            <div style={S.footer}>
              <span style={S.footerInfo}>{guild.member_count} members</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

const S = {
  overlay: {
    position: "fixed" as const,
    inset: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 50,
    pointerEvents: "auto" as const,
  },
  panel: {
    background: "#0a0e18",
    border: "1px solid #2a3a5a",
    borderRadius: 4,
    width: 400,
    maxHeight: "80vh",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 10,
    color: "#c8d4e8",
    padding: 16,
    display: "flex",
    flexDirection: "column" as const,
    gap: 10,
    overflowY: "auto" as const,
  },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  title: { fontSize: 11, color: "#e8e0d0" },
  closeBtn: { background: "none", border: "none", color: "#667788", cursor: "pointer" as const, fontFamily: "inherit", fontSize: 12 },
  error: { color: "#cc4433", fontSize: 9, border: "1px solid #cc443344", padding: "4px 8px", borderRadius: 2 },
  section: { display: "flex", flexDirection: "column" as const, gap: 6 },
  sectionLabel: { color: "#556677", fontSize: 9, letterSpacing: 1, marginBottom: 2 },
  noGuild: { display: "flex", flexDirection: "column" as const, gap: 8 },
  row: { display: "flex", gap: 6 },
  input: { flex: 1, background: "#0e1420", border: "1px solid #2a3a5a", color: "#c8d4e8", fontFamily: "'Press Start 2P', monospace", fontSize: 9, padding: "5px 8px", borderRadius: 2, outline: "none" as const },
  createBtn: { background: "#1a2a3a", border: "1px solid #4488ee", color: "#4488ee", fontFamily: "'Press Start 2P', monospace", fontSize: 10, padding: "8px 20px", cursor: "pointer" as const, borderRadius: 2 },
  motd: { display: "flex", alignItems: "center", gap: 6, background: "#0e1420", border: "1px solid #2a3a5a", borderRadius: 2, padding: "5px 8px" },
  motdLabel: { color: "#556677", fontSize: 8, minWidth: 34 },
  motdText: { flex: 1, color: "#c8a84b", fontSize: 9 },
  motdEditRow: { display: "flex", gap: 6, alignItems: "center" },
  tabs: { display: "flex", gap: 4, borderBottom: "1px solid #1a2a3a", paddingBottom: 6 },
  tab: { background: "none", border: "none", color: "#556677", fontFamily: "'Press Start 2P', monospace", fontSize: 9, cursor: "pointer" as const, padding: "3px 6px" },
  tabActive: { background: "#1a2a3a", border: "1px solid #2a3a5a", color: "#c8d4e8", fontFamily: "'Press Start 2P', monospace", fontSize: 9, cursor: "pointer" as const, padding: "3px 6px", borderRadius: 2 },
  rosterList: { display: "flex", flexDirection: "column" as const, gap: 4, maxHeight: 200, overflowY: "auto" as const },
  memberRow: { display: "flex", alignItems: "center", gap: 6, padding: "3px 6px", background: "#0e1420", borderRadius: 2 },
  roleIcon: { color: "#c8a84b", minWidth: 12, fontSize: 10 },
  memberName: { flex: 1, color: "#c8d4e8" },
  roleBadge: { fontSize: 8, color: "#556677" },
  memberActions: { display: "flex", gap: 3 },
  smallBtn: { background: "#1a2a3a", border: "1px solid #334455", color: "#8899aa", fontFamily: "'Press Start 2P', monospace", fontSize: 8, padding: "2px 5px", cursor: "pointer" as const, borderRadius: 2 },
  smallBtn2: { background: "#1a2a3a", border: "1px solid #4488ee", color: "#4488ee", fontFamily: "'Press Start 2P', monospace", fontSize: 9, padding: "5px 10px", cursor: "pointer" as const, borderRadius: 2 },
  kickBtn: { background: "#1a0a0a", border: "1px solid #553333", color: "#cc6655", fontFamily: "'Press Start 2P', monospace", fontSize: 8, padding: "2px 5px", cursor: "pointer" as const, borderRadius: 2 },
  inviteInputRow: { display: "flex", gap: 6, marginTop: 4 },
  inviteBtn: { background: "#1a2a3a", border: "1px solid #4488ee", color: "#4488ee", fontFamily: "'Press Start 2P', monospace", fontSize: 9, padding: "5px 10px", cursor: "pointer" as const, borderRadius: 2 },
  inviteRow: { display: "flex", alignItems: "center", gap: 6, padding: "4px 6px", background: "#0a1a0a", border: "1px solid #2a5a2a", borderRadius: 2 },
  inviteName: { flex: 1, color: "#88cc88", fontSize: 9 },
  acceptBtn: { background: "#0a1a0a", border: "1px solid #44aa55", color: "#44aa55", fontFamily: "'Press Start 2P', monospace", fontSize: 8, padding: "3px 6px", cursor: "pointer" as const, borderRadius: 2 },
  declineBtn: { background: "#1a0a0a", border: "1px solid #553333", color: "#cc4433", fontFamily: "'Press Start 2P', monospace", fontSize: 8, padding: "3px 6px", cursor: "pointer" as const, borderRadius: 2 },
  chatBox: { height: 160, overflowY: "auto" as const, background: "#0e1420", border: "1px solid #1a2a3a", borderRadius: 2, padding: "6px 8px", display: "flex", flexDirection: "column" as const, gap: 3 },
  chatMsg: { fontSize: 9, lineHeight: 1.4 },
  chatAuthor: { color: "#c8a84b" },
  chatText: { color: "#c8d4e8" },
  chatInputRow: { display: "flex", gap: 6 },
  leaveBtn: { background: "#1a0a0a", border: "1px solid #553333", color: "#cc4433", fontFamily: "'Press Start 2P', monospace", fontSize: 9, padding: "6px 12px", cursor: "pointer" as const, borderRadius: 2 },
  footer: { borderTop: "1px solid #1a2a3a", paddingTop: 6, display: "flex", justifyContent: "flex-end" },
  footerInfo: { color: "#556677", fontSize: 8 },
  tinyBtn: { background: "none", border: "none", color: "#556677", fontFamily: "'Press Start 2P', monospace", fontSize: 8, cursor: "pointer" as const, padding: "2px 4px" },
};
