import { useEffect, useState } from "react";
import { getCharacterQuests, type ActiveQuest, type QuestObjective } from "../api/client";
import { useGameStore } from "../store/useGameStore";

interface Props {
  onClose: () => void;
}

function ObjectiveRow({ obj }: { obj: QuestObjective }) {
  const done = obj.current >= obj.required;
  const label = obj.target ?? obj.item_id ?? obj.npc_id ?? obj.zone_id ?? obj.type;
  return (
    <div style={{ ...S.objectiveRow, opacity: done ? 0.5 : 1 }}>
      <span style={S.objCheck}>{done ? "✓" : "○"}</span>
      <span style={S.objLabel}>{label}</span>
      <span style={S.objProgress}>{obj.current}/{obj.required}</span>
    </div>
  );
}

function QuestCard({ quest, isActive }: { quest: ActiveQuest; isActive: boolean }) {
  const [expanded, setExpanded] = useState(false);
  const allDone = quest.objectives.every((o) => o.current >= o.required);

  return (
    <div style={S.questCard}>
      <button style={S.questCardHeader} onClick={() => setExpanded((v) => !v)}>
        <span style={allDone ? S.questTitleDone : S.questTitleActive}>{quest.quest_title}</span>
        <span style={S.questStatusBadge(quest.status)}>
          {quest.status === "ready_to_complete" ? "READY" : quest.status === "completed" ? "DONE" : "IN PROG"}
        </span>
      </button>
      {expanded && (
        <div style={S.questBody}>
          <div style={S.rewardRow}>
            <span style={S.rewardLabel}>XP</span>
            <span style={S.rewardVal}>{quest.xp_reward}</span>
            <span style={S.rewardLabel}>Gold</span>
            <span style={S.rewardVal}>{quest.gold_reward}</span>
            {quest.item_reward && (
              <>
                <span style={S.rewardLabel}>Item</span>
                <span style={S.rewardVal}>{quest.item_reward}</span>
              </>
            )}
          </div>
          {isActive && quest.objectives.map((obj, i) => (
            <ObjectiveRow key={i} obj={obj as QuestObjective} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function QuestLog({ onClose }: Props) {
  const token = useGameStore((s) => s.token);
  const char = useGameStore((s) => s.activeCharacter);
  const activeQuests = useGameStore((s) => s.activeQuests);
  const setActiveQuests = useGameStore((s) => s.setActiveQuests);

  const [completed, setCompleted] = useState<ActiveQuest[]>([]);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState<"active" | "completed">("active");

  useEffect(() => {
    if (!token || !char) return;
    setLoading(true);
    getCharacterQuests(token, char.id)
      .then((res) => {
        setActiveQuests(res.active);
        setCompleted(res.completed);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token, char?.id]);

  return (
    <div style={S.overlay}>
      <div style={S.panel}>
        <div style={S.header}>
          <span style={S.title}>QUEST LOG</span>
          <button style={S.closeBtn} onClick={onClose}>✕</button>
        </div>

        <div style={S.tabs}>
          <button style={tab === "active" ? S.tabActive : S.tab} onClick={() => setTab("active")}>
            ACTIVE ({activeQuests.length})
          </button>
          <button style={tab === "completed" ? S.tabActive : S.tab} onClick={() => setTab("completed")}>
            DONE ({completed.length})
          </button>
        </div>

        {loading ? (
          <div style={S.loading}>Loading...</div>
        ) : (
          <div style={S.list}>
            {tab === "active" && (
              activeQuests.length === 0
                ? <div style={S.empty}>No active quests. Talk to NPCs to find quests.</div>
                : activeQuests.map((q) => <QuestCard key={q.quest_id} quest={q} isActive />)
            )}
            {tab === "completed" && (
              completed.length === 0
                ? <div style={S.empty}>No completed quests yet.</div>
                : completed.map((q) => <QuestCard key={q.quest_id} quest={q} isActive={false} />)
            )}
          </div>
        )}
      </div>
    </div>
  );
}

const questStatusColor: Record<string, string> = {
  in_progress: "#4488ee",
  ready_to_complete: "#44aa55",
  completed: "#556677",
};

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
    overflowY: "hidden" as const,
  },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  title: { fontSize: 12, color: "#e8e0d0" },
  closeBtn: { background: "none", border: "none", color: "#667788", cursor: "pointer" as const, fontFamily: "inherit", fontSize: 12 },
  tabs: { display: "flex", gap: 6, borderBottom: "1px solid #1a2a3a", paddingBottom: 8 },
  tab: { background: "none", border: "none", color: "#556677", fontFamily: "'Press Start 2P', monospace", fontSize: 9, cursor: "pointer" as const, padding: "3px 6px" },
  tabActive: { background: "#1a2a3a", border: "1px solid #2a3a5a", color: "#c8d4e8", fontFamily: "'Press Start 2P', monospace", fontSize: 9, cursor: "pointer" as const, padding: "3px 6px", borderRadius: 2 },
  list: { display: "flex", flexDirection: "column" as const, gap: 6, overflowY: "auto" as const, flex: 1 },
  loading: { color: "#556677", textAlign: "center" as const, padding: 16 },
  empty: { color: "#556677", fontSize: 9, padding: "12px 0", textAlign: "center" as const },
  questCard: {
    border: "1px solid #1a2a3a",
    borderRadius: 2,
    overflow: "hidden" as const,
  },
  questCardHeader: {
    width: "100%",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    background: "#0e1420",
    border: "none",
    color: "inherit",
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 9,
    padding: "7px 10px",
    cursor: "pointer" as const,
    textAlign: "left" as const,
  },
  questTitleActive: { color: "#c8d4e8", flex: 1 },
  questTitleDone: { color: "#556677", flex: 1, textDecoration: "line-through" as const },
  questStatusBadge: (status: string) => ({
    fontSize: 8,
    color: questStatusColor[status] ?? "#667788",
    border: `1px solid ${questStatusColor[status] ?? "#667788"}44`,
    padding: "2px 5px",
    borderRadius: 2,
    minWidth: 50,
    textAlign: "center" as const,
  }),
  questBody: {
    padding: "8px 10px",
    background: "#08111a",
    display: "flex",
    flexDirection: "column" as const,
    gap: 5,
  },
  rewardRow: { display: "flex", gap: 8, alignItems: "center", marginBottom: 4 },
  rewardLabel: { fontSize: 8, color: "#556677" },
  rewardVal: { fontSize: 8, color: "#c8a84b" },
  objectiveRow: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    padding: "2px 4px",
  },
  objCheck: { fontSize: 9, color: "#44aa55", minWidth: 12 },
  objLabel: { flex: 1, fontSize: 9, color: "#8899aa" },
  objProgress: { fontSize: 8, color: "#556677" },
};
