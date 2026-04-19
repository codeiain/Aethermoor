import { useState, useEffect } from "react";
import {
  getParty,
  createParty,
  sendPartyInvite,
  acceptPartyInvite,
  declinePartyInvite,
  leaveParty,
  kickPartyMember,
  promotePartyLeader,
  setPartyLootMode,
  type LootMode,
} from "../api/client";
import { useGameStore } from "../store/useGameStore";

interface Props {
  onClose: () => void;
}

const LOOT_LABELS: Record<LootMode, string> = {
  free_for_all: "Free For All",
  round_robin: "Round Robin",
  need_before_greed: "Need Before Greed",
};

const LOOT_MODES: LootMode[] = ["free_for_all", "round_robin", "need_before_greed"];

export default function PartyPanel({ onClose }: Props) {
  const token = useGameStore((s) => s.token);
  const char = useGameStore((s) => s.activeCharacter);
  const party = useGameStore((s) => s.party);
  const pendingInvites = useGameStore((s) => s.pendingPartyInvites);
  const setParty = useGameStore((s) => s.setParty);
  const removePendingPartyInvite = useGameStore((s) => s.removePendingPartyInvite);

  const [inviteTargetId, setInviteTargetId] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !char) return;
    getParty(token, char.id)
      .then((p) => setParty(p))
      .catch(() => {});
  }, [token, char?.id]);

  const isLeader = party?.leader_id === char?.id;

  async function handleCreateParty() {
    if (!token || !char) return;
    setBusy(true);
    setError(null);
    try {
      const p = await createParty(token, char.id, char.name);
      setParty({ ...p, leader_name: char.name, member_count: 1, xp_multiplier: 1.0 });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create party");
    } finally {
      setBusy(false);
    }
  }

  async function handleInvite() {
    if (!token || !char || !party || !inviteTargetId.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await sendPartyInvite(token, char.id, char.name, inviteTargetId.trim());
      setInviteTargetId("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send invite");
    } finally {
      setBusy(false);
    }
  }

  async function handleLeave() {
    if (!token || !char || !party) return;
    setBusy(true);
    setError(null);
    try {
      await leaveParty(token, party.party_id, char.id);
      setParty(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to leave party");
    } finally {
      setBusy(false);
    }
  }

  async function handleKick(memberId: string) {
    if (!token || !char || !party) return;
    setBusy(true);
    setError(null);
    try {
      await kickPartyMember(token, party.party_id, memberId, char.id);
      const updated = await getParty(token, char.id);
      setParty(updated);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to kick member");
    } finally {
      setBusy(false);
    }
  }

  async function handlePromote(newLeaderId: string) {
    if (!token || !char || !party) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await promotePartyLeader(token, party.party_id, newLeaderId, char.id);
      setParty(updated);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to promote leader");
    } finally {
      setBusy(false);
    }
  }

  async function handleLootMode(mode: LootMode) {
    if (!token || !char || !party) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await setPartyLootMode(token, party.party_id, char.id, mode);
      setParty(updated);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to change loot mode");
    } finally {
      setBusy(false);
    }
  }

  async function handleAcceptInvite(inviteId: string) {
    if (!token) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await acceptPartyInvite(token, inviteId);
      setParty(updated);
      removePendingPartyInvite(inviteId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to accept invite");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeclineInvite(inviteId: string) {
    if (!token) return;
    setBusy(true);
    setError(null);
    try {
      await declinePartyInvite(token, inviteId);
      removePendingPartyInvite(inviteId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to decline invite");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={S.overlay}>
      <div style={S.panel}>
        <div style={S.header}>
          <span style={S.title}>PARTY</span>
          <button style={S.closeBtn} onClick={onClose}>✕</button>
        </div>

        {error && <div style={S.error}>{error}</div>}

        {/* Pending invites */}
        {pendingInvites.length > 0 && (
          <div style={S.section}>
            <div style={S.sectionLabel}>PENDING INVITES</div>
            {pendingInvites.map((inv) => (
              <div key={inv.invite_id} style={S.inviteRow}>
                <span style={S.inviteName}>{inv.from_name} invited you</span>
                <button style={S.acceptBtn} onClick={() => handleAcceptInvite(inv.invite_id)} disabled={busy}>
                  Accept
                </button>
                <button style={S.declineBtn} onClick={() => handleDeclineInvite(inv.invite_id)} disabled={busy}>
                  Decline
                </button>
              </div>
            ))}
          </div>
        )}

        {!party ? (
          <div style={S.noParty}>
            <div style={S.noPartyText}>You are not in a party.</div>
            <button style={S.createBtn} onClick={handleCreateParty} disabled={busy}>
              {busy ? "..." : "Create Party"}
            </button>
          </div>
        ) : (
          <>
            {/* Roster */}
            <div style={S.section}>
              <div style={S.sectionLabel}>
                ROSTER ({party.member_count}/5) · XP ×{party.xp_multiplier.toFixed(2)}
              </div>
              {party.members.map((memberId) => (
                <div key={memberId} style={S.memberRow}>
                  <span style={S.memberIcon}>{memberId === party.leader_id ? "★" : "·"}</span>
                  <span style={S.memberId}>{memberId === char?.id ? `${memberId} (you)` : memberId}</span>
                  {isLeader && memberId !== char?.id && (
                    <div style={S.memberActions}>
                      <button style={S.smallBtn} onClick={() => handlePromote(memberId)} disabled={busy}>
                        Promote
                      </button>
                      <button style={S.kickBtn} onClick={() => handleKick(memberId)} disabled={busy}>
                        Kick
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Invite */}
            <div style={S.section}>
              <div style={S.sectionLabel}>INVITE PLAYER</div>
              <div style={S.inviteInputRow}>
                <input
                  style={S.input}
                  placeholder="Character ID"
                  value={inviteTargetId}
                  onChange={(e) => setInviteTargetId(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleInvite()}
                />
                <button style={S.inviteBtn} onClick={handleInvite} disabled={busy || !inviteTargetId.trim()}>
                  Invite
                </button>
              </div>
            </div>

            {/* Loot mode */}
            <div style={S.section}>
              <div style={S.sectionLabel}>LOOT MODE</div>
              <div style={S.lootRow}>
                {LOOT_MODES.map((mode) => (
                  <button
                    key={mode}
                    style={party.loot_mode === mode ? S.lootBtnActive : S.lootBtn}
                    onClick={() => handleLootMode(mode)}
                    disabled={!isLeader || busy}
                  >
                    {LOOT_LABELS[mode]}
                  </button>
                ))}
              </div>
            </div>

            {/* Leave */}
            <div style={S.footer}>
              <button style={S.leaveBtn} onClick={handleLeave} disabled={busy}>
                Leave Party
              </button>
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
    minWidth: 340,
    maxWidth: 420,
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 10,
    color: "#c8d4e8",
    padding: 16,
    display: "flex",
    flexDirection: "column" as const,
    gap: 12,
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  title: { fontSize: 12, color: "#e8e0d0" },
  closeBtn: {
    background: "none",
    border: "none",
    color: "#667788",
    cursor: "pointer" as const,
    fontFamily: "inherit",
    fontSize: 12,
  },
  error: {
    color: "#cc4433",
    fontSize: 9,
    border: "1px solid #cc443344",
    padding: "4px 8px",
    borderRadius: 2,
  },
  section: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 6,
  },
  sectionLabel: {
    color: "#556677",
    fontSize: 9,
    letterSpacing: 1,
    marginBottom: 2,
  },
  noParty: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    gap: 12,
    padding: "16px 0",
  },
  noPartyText: { color: "#667788" },
  createBtn: {
    background: "#1a2a3a",
    border: "1px solid #4488ee",
    color: "#4488ee",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 10,
    padding: "8px 20px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
  memberRow: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    padding: "4px 6px",
    background: "#0e1420",
    borderRadius: 2,
  },
  memberIcon: { color: "#c8a84b", minWidth: 12 },
  memberId: { flex: 1, color: "#c8d4e8", overflow: "hidden" as const, textOverflow: "ellipsis" as const },
  memberActions: { display: "flex", gap: 4 },
  smallBtn: {
    background: "#1a2a3a",
    border: "1px solid #334455",
    color: "#8899aa",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 8,
    padding: "3px 6px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
  kickBtn: {
    background: "#1a0a0a",
    border: "1px solid #553333",
    color: "#cc6655",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 8,
    padding: "3px 6px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
  inviteRow: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    padding: "4px 6px",
    background: "#0a1a0a",
    border: "1px solid #2a5a2a",
    borderRadius: 2,
  },
  inviteName: { flex: 1, color: "#88cc88", fontSize: 9 },
  acceptBtn: {
    background: "#0a1a0a",
    border: "1px solid #44aa55",
    color: "#44aa55",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 8,
    padding: "3px 6px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
  declineBtn: {
    background: "#1a0a0a",
    border: "1px solid #553333",
    color: "#cc4433",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 8,
    padding: "3px 6px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
  inviteInputRow: {
    display: "flex",
    gap: 6,
  },
  input: {
    flex: 1,
    background: "#0e1420",
    border: "1px solid #2a3a5a",
    color: "#c8d4e8",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 9,
    padding: "5px 8px",
    borderRadius: 2,
    outline: "none" as const,
  },
  inviteBtn: {
    background: "#1a2a3a",
    border: "1px solid #4488ee",
    color: "#4488ee",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 9,
    padding: "5px 10px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
  lootRow: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 4,
  },
  lootBtn: {
    background: "#0e1420",
    border: "1px solid #2a3a5a",
    color: "#667788",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 8,
    padding: "5px 8px",
    cursor: "pointer" as const,
    borderRadius: 2,
    textAlign: "left" as const,
  },
  lootBtnActive: {
    background: "#1a2a3a",
    border: "1px solid #c8a84b",
    color: "#c8a84b",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 8,
    padding: "5px 8px",
    cursor: "pointer" as const,
    borderRadius: 2,
    textAlign: "left" as const,
  },
  footer: {
    display: "flex",
    justifyContent: "flex-end",
    paddingTop: 4,
    borderTop: "1px solid #1a2a3a",
  },
  leaveBtn: {
    background: "#1a0a0a",
    border: "1px solid #553333",
    color: "#cc4433",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 9,
    padding: "6px 12px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
};
