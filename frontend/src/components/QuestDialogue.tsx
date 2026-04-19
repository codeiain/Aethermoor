import { useState } from "react";
import { acceptQuest, completeQuest, type NpcDialogueOption } from "../api/client";
import { useGameStore } from "../store/useGameStore";

export default function QuestDialogue() {
  const token = useGameStore((s) => s.token);
  const char = useGameStore((s) => s.activeCharacter);
  const dialogue = useGameStore((s) => s.npcDialogue);
  const setNpcDialogue = useGameStore((s) => s.setNpcDialogue);
  const updateQuest = useGameStore((s) => s.updateQuest);
  const removeQuest = useGameStore((s) => s.removeQuest);
  const addNotification = useGameStore((s) => s.addNotification);

  const [selected, setSelected] = useState<NpcDialogueOption | null>(null);
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  if (!dialogue) return null;

  async function handleAccept(option: NpcDialogueOption) {
    if (!token || !char) return;
    setBusy(true);
    setFeedback(null);
    try {
      const quest = await acceptQuest(token, char.id, option.quest_id);
      updateQuest(quest);
      addNotification({
        id: `quest-accepted-${option.quest_id}`,
        type: "quest_update",
        title: "Quest Accepted",
        body: option.quest_title,
        timestamp: Date.now(),
        read: false,
      });
      setFeedback(`Quest accepted: ${option.quest_title}`);
      setTimeout(() => setNpcDialogue(null), 1200);
    } catch (e) {
      setFeedback(e instanceof Error ? e.message : "Failed to accept quest");
    } finally {
      setBusy(false);
    }
  }

  async function handleComplete(option: NpcDialogueOption) {
    if (!token || !char) return;
    setBusy(true);
    setFeedback(null);
    try {
      const result = await completeQuest(token, char.id, option.quest_id);
      removeQuest(option.quest_id);
      addNotification({
        id: `quest-done-${option.quest_id}`,
        type: "quest_update",
        title: "Quest Complete!",
        body: `${result.quest_title} — +${result.xp_awarded} XP, +${result.gold_awarded} gold${result.item_awarded ? `, ${result.item_awarded}` : ""}`,
        timestamp: Date.now(),
        read: false,
      });
      setFeedback(result.message);
      setTimeout(() => setNpcDialogue(null), 2000);
    } catch (e) {
      setFeedback(e instanceof Error ? e.message : "Failed to complete quest");
    } finally {
      setBusy(false);
    }
  }

  const activeOption = selected ?? dialogue.options[0] ?? null;

  return (
    <div style={S.overlay}>
      <div style={S.modal}>
        <div style={S.header}>
          <span style={S.npcName}>NPC · {dialogue.npc_id}</span>
          <button style={S.closeBtn} onClick={() => setNpcDialogue(null)}>✕</button>
        </div>

        {/* Dialogue text */}
        {activeOption && (
          <div style={S.dialogueBox}>
            <div style={S.questTitle}>{activeOption.quest_title}</div>
            <div style={S.dialogueText}>{activeOption.dialogue}</div>
          </div>
        )}

        {feedback && <div style={S.feedback}>{feedback}</div>}

        {/* Quest options list */}
        {dialogue.options.length > 1 && (
          <div style={S.optionsList}>
            {dialogue.options.map((opt) => (
              <button
                key={opt.quest_id}
                style={opt === activeOption ? S.optionActive : S.option}
                onClick={() => setSelected(opt)}
              >
                {opt.quest_title}
              </button>
            ))}
          </div>
        )}

        {/* Action buttons */}
        <div style={S.actions}>
          {activeOption?.type === "offer" && (
            <>
              <button style={S.acceptBtn} onClick={() => handleAccept(activeOption)} disabled={busy}>
                {busy ? "..." : "Accept Quest"}
              </button>
              <button style={S.declineBtn} onClick={() => setNpcDialogue(null)} disabled={busy}>
                Decline
              </button>
            </>
          )}
          {activeOption?.type === "ready_to_complete" && (
            <button style={S.acceptBtn} onClick={() => handleComplete(activeOption)} disabled={busy}>
              {busy ? "..." : "Turn In"}
            </button>
          )}
          {(activeOption?.type === "in_progress" || activeOption?.type === "completed") && (
            <button style={S.declineBtn} onClick={() => setNpcDialogue(null)}>
              Farewell
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

const S = {
  overlay: {
    position: "fixed" as const,
    inset: 0,
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "center",
    paddingBottom: 100,
    zIndex: 50,
    pointerEvents: "auto" as const,
  },
  modal: {
    background: "#0a0e18",
    border: "1px solid #2a3a5a",
    borderRadius: 4,
    width: 460,
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 10,
    color: "#c8d4e8",
    padding: 16,
    display: "flex",
    flexDirection: "column" as const,
    gap: 10,
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  npcName: { fontSize: 10, color: "#c8a84b" },
  closeBtn: {
    background: "none",
    border: "none",
    color: "#667788",
    cursor: "pointer" as const,
    fontFamily: "inherit",
    fontSize: 12,
  },
  dialogueBox: {
    background: "#0e1420",
    border: "1px solid #1a2a3a",
    borderRadius: 2,
    padding: "10px 12px",
    display: "flex",
    flexDirection: "column" as const,
    gap: 6,
  },
  questTitle: { fontSize: 10, color: "#e8e0d0", marginBottom: 4 },
  dialogueText: { fontSize: 9, color: "#c8d4e8", lineHeight: 1.6 },
  feedback: { fontSize: 9, color: "#44aa55", padding: "4px 8px", background: "#0a1a0a", border: "1px solid #2a5a2a", borderRadius: 2 },
  optionsList: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 4,
  },
  option: {
    background: "#0e1420",
    border: "1px solid #1a2a3a",
    color: "#667788",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 9,
    padding: "5px 8px",
    cursor: "pointer" as const,
    borderRadius: 2,
    textAlign: "left" as const,
  },
  optionActive: {
    background: "#1a2a3a",
    border: "1px solid #c8a84b",
    color: "#c8a84b",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 9,
    padding: "5px 8px",
    cursor: "pointer" as const,
    borderRadius: 2,
    textAlign: "left" as const,
  },
  actions: {
    display: "flex",
    gap: 8,
    justifyContent: "flex-end",
    paddingTop: 4,
    borderTop: "1px solid #1a2a3a",
  },
  acceptBtn: {
    background: "#0a1a0a",
    border: "1px solid #44aa55",
    color: "#44aa55",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 9,
    padding: "6px 14px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
  declineBtn: {
    background: "#1a0a0a",
    border: "1px solid #553333",
    color: "#cc6655",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 9,
    padding: "6px 14px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
};
