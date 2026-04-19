import { useEffect, useState, useCallback } from "react";
import {
  getSkillTree,
  unlockSkill,
  respecSkills,
  type SkillDef,
  type SkillBranch,
  type SkillTreeResponse,
} from "../api/client";
import { useGameStore } from "../store/useGameStore";

interface Props {
  onClose: () => void;
}

type SkillState = "locked" | "available" | "unlocked";

function getSkillState(
  skill: SkillDef,
  unlocked: string[],
  characterLevel: number,
): SkillState {
  if (unlocked.includes(skill.id)) return "unlocked";
  const levelOk = characterLevel >= skill.level_requirement;
  const prereqOk = skill.prerequisites.every((p) => unlocked.includes(p));
  return levelOk && prereqOk ? "available" : "locked";
}

function SkillNode({
  skill,
  state,
  branchColour,
  tpRemaining,
  onUnlock,
}: {
  skill: SkillDef;
  state: SkillState;
  branchColour: string;
  tpRemaining: number;
  onUnlock: (skill: SkillDef) => void;
}) {
  const [hovered, setHovered] = useState(false);

  const canAfford = tpRemaining >= skill.tp_cost;
  const clickable = state === "available" && canAfford;

  const border =
    state === "unlocked"
      ? `2px solid ${branchColour}`
      : state === "available"
        ? `2px solid ${canAfford ? "#c8a84b" : "#554422"}`
        : "2px solid #2a3a5a";

  const bg =
    state === "unlocked"
      ? `${branchColour}33`
      : state === "available"
        ? "rgba(30,24,8,0.8)"
        : "rgba(10,14,24,0.6)";

  const textColour =
    state === "unlocked"
      ? "#e8e0d0"
      : state === "available"
        ? "#c8a84b"
        : "#445566";

  return (
    <div
      style={{
        ...S.skillNode,
        border,
        background: bg,
        cursor: clickable ? "pointer" : "default",
        opacity: state === "locked" ? 0.5 : 1,
        transform: hovered && clickable ? "scale(1.03)" : "scale(1)",
        transition: "transform 0.1s, box-shadow 0.1s",
        boxShadow:
          hovered && clickable ? `0 0 8px ${branchColour}66` : "none",
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={() => clickable && onUnlock(skill)}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 3 }}>
        <span style={{ ...S.skillName, color: textColour }}>{skill.name}</span>
        <span style={S.tpBadge(state === "unlocked" ? branchColour : state === "available" ? "#c8a84b" : "#334455")}>
          {state === "unlocked" ? "✓" : `${skill.tp_cost}TP`}
        </span>
      </div>
      <div style={S.skillMeta}>
        <span style={{ color: "#667788" }}>T{skill.tier}</span>
        <span style={{ color: "#445566" }}>Lv.{skill.level_requirement}</span>
        <span style={{ color: "#556677", textTransform: "capitalize" as const }}>
          {skill.type.replace("active_", "").replace("_", " ")}
        </span>
      </div>
      {hovered && (
        <div style={S.tooltip}>
          <div style={{ color: "#c8a84b", marginBottom: 4, fontSize: 11 }}>{skill.name}</div>
          <div style={{ color: "#8899aa", marginBottom: 4, fontSize: 10 }}>{skill.effect}</div>
          {skill.prerequisites.length > 0 && (
            <div style={{ color: "#556677", fontSize: 10 }}>
              Requires: {skill.prerequisites.join(", ").replace(/_/g, " ")}
            </div>
          )}
          {state === "locked" && (
            <div style={{ color: "#cc4433", fontSize: 10, marginTop: 2 }}>
              {skill.prerequisites.length > 0 ? "Missing prerequisites" : `Requires level ${skill.level_requirement}`}
            </div>
          )}
          {state === "available" && !canAfford && (
            <div style={{ color: "#cc4433", fontSize: 10, marginTop: 2 }}>
              Not enough TP (need {skill.tp_cost})
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SkillBranchColumn({
  branch,
  unlocked,
  characterLevel,
  tpRemaining,
  onUnlock,
}: {
  branch: SkillBranch;
  unlocked: string[];
  characterLevel: number;
  tpRemaining: number;
  onUnlock: (skill: SkillDef) => void;
}) {
  const tiers = [1, 2, 3, 4];

  return (
    <div style={S.branchColumn}>
      <div style={{ ...S.branchHeader, borderColor: branch.colour }}>
        <span style={{ ...S.branchName, color: branch.colour }}>{branch.name}</span>
      </div>
      <div style={S.branchPassive}>
        <span style={{ color: "#8899aa", fontSize: 9 }}>Branch passive: </span>
        <span style={{ color: "#c8a84b", fontSize: 9 }}>{branch.passive.name}</span>
      </div>
      {tiers.map((tier) => {
        const tierSkills = branch.skills.filter((s) => s.tier === tier);
        return (
          <div key={tier} style={S.tierGroup}>
            <div style={S.tierLabel}>T{tier}</div>
            {tierSkills.map((skill) => (
              <SkillNode
                key={skill.id}
                skill={skill}
                state={getSkillState(skill, unlocked, characterLevel)}
                branchColour={branch.colour}
                tpRemaining={tpRemaining}
                onUnlock={onUnlock}
              />
            ))}
          </div>
        );
      })}
    </div>
  );
}

export default function SkillTreePanel({ onClose }: Props) {
  const token = useGameStore((s) => s.token);
  const char = useGameStore((s) => s.activeCharacter);

  const [tree, setTree] = useState<SkillTreeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pendingSkill, setPendingSkill] = useState<SkillDef | null>(null);
  const [unlocking, setUnlocking] = useState(false);
  const [respecConfirm, setRespecConfirm] = useState(false);
  const [respecing, setRespecing] = useState(false);
  const [feedback, setFeedback] = useState<{ ok: boolean; msg: string } | null>(null);

  const load = useCallback(async () => {
    if (!token || !char) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getSkillTree(token, char.id);
      setTree(data);
    } catch {
      setError("Failed to load skill tree");
    } finally {
      setLoading(false);
    }
  }, [token, char]);

  useEffect(() => { load(); }, [load]);

  function showFeedback(ok: boolean, msg: string) {
    setFeedback({ ok, msg });
    setTimeout(() => setFeedback(null), 2500);
  }

  async function handleUnlock(skill: SkillDef) {
    if (!token || !char || unlocking) return;
    setPendingSkill(skill);
  }

  async function confirmUnlock() {
    if (!token || !char || !pendingSkill) return;
    setUnlocking(true);
    try {
      const result = await unlockSkill(token, char.id, pendingSkill.id);
      setTree((prev) =>
        prev
          ? {
              ...prev,
              talent_points_spent: result.talent_points_spent,
              unlocked_skills: result.unlocked_skills,
            }
          : prev
      );
      showFeedback(true, `Unlocked: ${pendingSkill.name}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to unlock skill";
      showFeedback(false, msg);
    } finally {
      setUnlocking(false);
      setPendingSkill(null);
    }
  }

  async function handleRespec() {
    if (!token || !char || respecing) return;
    setRespecing(true);
    setRespecConfirm(false);
    try {
      const result = await respecSkills(token, char.id);
      setTree((prev) =>
        prev
          ? {
              ...prev,
              talent_points_spent: result.talent_points_spent,
              unlocked_skills: result.unlocked_skills,
            }
          : prev
      );
      showFeedback(true, `Respec complete. ${result.gold_cost}g deducted.`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Respec failed";
      showFeedback(false, msg);
    } finally {
      setRespecing(false);
    }
  }

  const tpRemaining = tree ? tree.talent_points_total - tree.talent_points_spent : 0;
  const respecCost = char ? 50 * char.level : 0;

  return (
    <div style={S.overlay}>
      <div style={S.panel}>
        {/* Header */}
        <div style={S.header}>
          <div>
            <span style={S.title}>
              {tree ? `${tree.display_name} — Skill Tree` : "Skill Tree"}
            </span>
            {tree && (
              <span style={S.classPassive}>
                {" "}· {tree.class_passive.name}
              </span>
            )}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            {tree && (
              <div style={S.tpCounter}>
                <span style={{ color: "#8899aa", fontSize: 10 }}>TP: </span>
                <span style={{ color: tpRemaining > 0 ? "#c8a84b" : "#667788", fontSize: 12 }}>
                  {tpRemaining}
                </span>
                <span style={{ color: "#445566", fontSize: 10 }}>/{tree.talent_points_total}</span>
              </div>
            )}
            <button style={S.respecBtn} onClick={() => setRespecConfirm(true)}>
              Respec ({respecCost}g)
            </button>
            <button style={S.closeBtn} onClick={onClose}>✕</button>
          </div>
        </div>

        {/* Feedback */}
        {feedback && (
          <div style={{ ...S.feedback, background: feedback.ok ? "#1a3a1a" : "#3a1a1a", borderColor: feedback.ok ? "#44aa55" : "#cc4433" }}>
            {feedback.msg}
          </div>
        )}

        {/* Body */}
        <div style={S.body}>
          {loading && <div style={S.center}>Loading...</div>}
          {error && <div style={{ ...S.center, color: "#cc4433" }}>{error}</div>}
          {tree && !loading && (
            <div style={S.branchRow}>
              {tree.branches.map((branch) => (
                <SkillBranchColumn
                  key={branch.id}
                  branch={branch}
                  unlocked={tree.unlocked_skills}
                  characterLevel={char?.level ?? 1}
                  tpRemaining={tpRemaining}
                  onUnlock={handleUnlock}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Unlock confirm dialog */}
      {pendingSkill && (
        <div style={S.dialogOverlay}>
          <div style={S.dialog}>
            <div style={{ color: "#c8a84b", fontSize: 13, marginBottom: 8 }}>
              Unlock {pendingSkill.name}?
            </div>
            <div style={{ color: "#8899aa", fontSize: 11, marginBottom: 12 }}>
              Costs {pendingSkill.tp_cost} TP. {tpRemaining - pendingSkill.tp_cost} TP remaining after.
            </div>
            <div style={{ display: "flex", gap: 8, justifyContent: "center" }}>
              <button style={S.confirmBtn} onClick={confirmUnlock} disabled={unlocking}>
                {unlocking ? "..." : "Confirm"}
              </button>
              <button style={S.cancelBtn} onClick={() => setPendingSkill(null)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Respec confirm dialog */}
      {respecConfirm && (
        <div style={S.dialogOverlay}>
          <div style={S.dialog}>
            <div style={{ color: "#ee8833", fontSize: 13, marginBottom: 8 }}>
              Respec Skills?
            </div>
            <div style={{ color: "#8899aa", fontSize: 11, marginBottom: 4 }}>
              Cost: {respecCost}g · All talent points refunded.
            </div>
            <div style={{ color: "#667788", fontSize: 10, marginBottom: 12 }}>
              Once per 7 days. Cannot respec in an active dungeon.
            </div>
            <div style={{ display: "flex", gap: 8, justifyContent: "center" }}>
              <button style={{ ...S.confirmBtn, background: "#2a1800", borderColor: "#ee8833", color: "#ee8833" }}
                onClick={handleRespec} disabled={respecing}>
                {respecing ? "..." : "Respec"}
              </button>
              <button style={S.cancelBtn} onClick={() => setRespecConfirm(false)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const S = {
  overlay: {
    position: "fixed" as const,
    inset: 0,
    background: "rgba(0,0,0,0.75)",
    zIndex: 100,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "'Press Start 2P', monospace",
  },
  panel: {
    background: "#090d17",
    border: "1px solid #2a3a5a",
    borderRadius: 4,
    width: "min(90vw, 760px)",
    maxHeight: "85vh",
    display: "flex",
    flexDirection: "column" as const,
    overflow: "hidden",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "10px 14px",
    borderBottom: "1px solid #1e2a3a",
    flexShrink: 0,
  },
  title: { fontSize: 13, color: "#e8e0d0" },
  classPassive: { fontSize: 10, color: "#667788" },
  tpCounter: {
    background: "rgba(0,0,0,0.5)",
    border: "1px solid #2a3a5a",
    borderRadius: 2,
    padding: "3px 8px",
  },
  respecBtn: {
    background: "rgba(0,0,0,0.5)",
    border: "1px solid #554422",
    color: "#887744",
    fontSize: 9,
    fontFamily: "inherit",
    padding: "4px 8px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
  closeBtn: {
    background: "transparent",
    border: "none",
    color: "#667788",
    fontSize: 14,
    cursor: "pointer" as const,
    fontFamily: "inherit",
    padding: "0 4px",
  },
  feedback: {
    margin: "6px 14px 0",
    padding: "5px 10px",
    border: "1px solid",
    borderRadius: 2,
    fontSize: 10,
    color: "#ccddcc",
    flexShrink: 0,
  },
  body: {
    flex: 1,
    overflowY: "auto" as const,
    padding: "12px 14px",
  },
  center: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    height: 200,
    color: "#667788",
    fontSize: 12,
  },
  branchRow: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 16,
  },
  branchColumn: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 8,
  },
  branchHeader: {
    borderBottom: "2px solid",
    paddingBottom: 6,
    marginBottom: 2,
  },
  branchName: {
    fontSize: 12,
    fontWeight: "bold" as const,
  },
  branchPassive: {
    background: "rgba(255,255,255,0.03)",
    border: "1px solid #1e2a3a",
    borderRadius: 2,
    padding: "4px 6px",
    marginBottom: 4,
    lineHeight: 1.5,
  },
  tierGroup: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 4,
  },
  tierLabel: {
    fontSize: 9,
    color: "#334455",
    marginBottom: 1,
  },
  skillNode: {
    padding: "6px 8px",
    borderRadius: 3,
    position: "relative" as const,
    userSelect: "none" as const,
  },
  skillName: {
    fontSize: 10,
    lineHeight: 1.3,
  },
  tpBadge: (colour: string) => ({
    fontSize: 9,
    color: colour,
    border: `1px solid ${colour}44`,
    borderRadius: 2,
    padding: "1px 4px",
    flexShrink: 0,
    marginLeft: 6,
  }),
  skillMeta: {
    display: "flex",
    gap: 8,
    fontSize: 9,
    marginTop: 2,
  },
  tooltip: {
    position: "absolute" as const,
    left: "calc(100% + 8px)",
    top: 0,
    width: 200,
    background: "#0a0e18",
    border: "1px solid #2a3a5a",
    borderRadius: 3,
    padding: "8px 10px",
    zIndex: 200,
    lineHeight: 1.5,
  },
  dialogOverlay: {
    position: "fixed" as const,
    inset: 0,
    background: "rgba(0,0,0,0.6)",
    zIndex: 200,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  dialog: {
    background: "#0d1420",
    border: "1px solid #2a3a5a",
    borderRadius: 4,
    padding: "20px 24px",
    textAlign: "center" as const,
    fontFamily: "'Press Start 2P', monospace",
    minWidth: 260,
  },
  confirmBtn: {
    background: "#0a180a",
    border: "1px solid #44aa55",
    color: "#44aa55",
    fontSize: 11,
    fontFamily: "inherit",
    padding: "6px 14px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
  cancelBtn: {
    background: "transparent",
    border: "1px solid #334455",
    color: "#667788",
    fontSize: 11,
    fontFamily: "inherit",
    padding: "6px 14px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
};
