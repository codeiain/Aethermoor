import { useCallback, useEffect, useState } from "react";
import { advanceTutorialStep, getTutorialState } from "../api/client";
import { useGameStore } from "../store/useGameStore";

interface Step {
  title: string;
  body: string;
  highlight?: string; // CSS selector hint shown in the arrow label
  arrowDir?: "up" | "down" | "left" | "right";
}

const STEPS: Step[] = [
  {
    title: "Movement",
    body: "Use WASD or the arrow keys to move your character. On mobile, use the joystick in the bottom-left corner.",
    arrowDir: "down",
    highlight: "Joystick",
  },
  {
    title: "Talk to NPCs",
    body: "Click or tap on any NPC to start a conversation. Look for characters with speech bubbles above them.",
    arrowDir: "up",
  },
  {
    title: "Combat",
    body: "A goblin approaches! Click or tap it to initiate combat. Watch the turn order panel on the right and choose your actions.",
    arrowDir: "right",
    highlight: "Turn Order",
  },
  {
    title: "Inventory & Loot",
    body: "After defeating an enemy you can loot its remains. Open your backpack with the B key or the bag icon in the action bar.",
    arrowDir: "up",
    highlight: "Action Bar",
  },
  {
    title: "Explore the World",
    body: "Walk to the edge of the starter zone to transition to a new area. The world of AETHERMOOR is yours to discover!",
  },
];

interface Props {
  onDone: () => void;
}

export default function TutorialOverlay({ onDone }: Props) {
  const token = useGameStore((s) => s.token);
  const activeCharacter = useGameStore((s) => s.activeCharacter);

  const [stepIndex, setStepIndex] = useState(0);
  const [advancing, setAdvancing] = useState(false);

  // Restore progress from server on mount
  useEffect(() => {
    if (!token || !activeCharacter) return;
    getTutorialState(token, activeCharacter.id)
      .then((state) => {
        if (state.tutorial_step === -1) {
          onDone();
        } else if (state.tutorial_step !== null) {
          setStepIndex(Math.min(state.tutorial_step + 1, STEPS.length - 1));
        }
      })
      .catch(() => {/* non-blocking — show from step 0 */});
  }, [token, activeCharacter, onDone]);

  const handleNext = useCallback(async () => {
    if (!token || !activeCharacter || advancing) return;
    setAdvancing(true);
    try {
      await advanceTutorialStep(token, activeCharacter.id, stepIndex);
    } catch {/* non-blocking */}
    if (stepIndex >= STEPS.length - 1) {
      // Mark fully done
      try { await advanceTutorialStep(token, activeCharacter.id, -1); } catch {/* */}
      onDone();
    } else {
      setStepIndex((i) => i + 1);
    }
    setAdvancing(false);
  }, [token, activeCharacter, advancing, stepIndex, onDone]);

  const handleSkip = useCallback(async () => {
    if (!token || !activeCharacter) return;
    try { await advanceTutorialStep(token, activeCharacter.id, -1); } catch {/* */}
    onDone();
  }, [token, activeCharacter, onDone]);

  const step = STEPS[stepIndex];
  const isLast = stepIndex === STEPS.length - 1;

  return (
    <div style={S.overlay}>
      <div style={S.panel}>
        {/* Progress dots */}
        <div style={S.dots}>
          {STEPS.map((_, i) => (
            <div key={i} style={S.dot(i <= stepIndex)} />
          ))}
        </div>

        {/* Arrow indicator */}
        {step.arrowDir && (
          <div style={S.arrow(step.arrowDir)}>
            {ARROW_CHARS[step.arrowDir]}
            {step.highlight && <span style={S.highlightLabel}>{step.highlight}</span>}
          </div>
        )}

        {/* Content */}
        <div style={S.stepLabel}>Step {stepIndex + 1} of {STEPS.length}</div>
        <div style={S.title}>{step.title}</div>
        <div style={S.body}>{step.body}</div>

        {/* Actions */}
        <div style={S.actions}>
          <button style={S.skipBtn} onClick={handleSkip}>
            Skip Tutorial
          </button>
          <button style={S.nextBtn} onClick={handleNext} disabled={advancing}>
            {advancing ? "…" : isLast ? "Finish" : "Next →"}
          </button>
        </div>
      </div>
    </div>
  );
}

const ARROW_CHARS: Record<string, string> = {
  up: "↑",
  down: "↓",
  left: "←",
  right: "→",
};

// ── Styles ────────────────────────────────────────────────────────────────────

const S = {
  overlay: {
    position: "fixed" as const,
    inset: 0,
    background: "rgba(0,0,0,0.55)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 200,
    pointerEvents: "auto" as const,
  },
  panel: {
    width: 420,
    maxWidth: "92vw",
    background: "#0d1320",
    border: "1px solid #2a3a5a",
    borderRadius: 6,
    padding: "20px 24px",
    display: "flex",
    flexDirection: "column" as const,
    gap: 12,
    position: "relative" as const,
  },
  dots: {
    display: "flex",
    gap: 6,
    justifyContent: "center" as const,
  },
  dot: (active: boolean) => ({
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: active ? "#c8a84b" : "#1e2a3a",
    border: "1px solid #2a3a5a",
    transition: "background 0.2s",
  }),
  arrow: (dir: string) => ({
    fontSize: 28,
    color: "#c8a84b",
    textAlign: "center" as const,
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center" as const,
    gap: 4,
  }),
  highlightLabel: {
    fontSize: 11,
    color: "#667788",
    letterSpacing: 1,
  },
  stepLabel: {
    fontSize: 11,
    color: "#445566",
    letterSpacing: 1,
    textAlign: "center" as const,
  },
  title: {
    fontSize: 20,
    color: "#c8a84b",
    letterSpacing: 1,
    textAlign: "center" as const,
  },
  body: {
    fontSize: 15,
    color: "#aabbd0",
    lineHeight: 1.55,
    textAlign: "center" as const,
  },
  actions: {
    display: "flex",
    justifyContent: "space-between" as const,
    alignItems: "center" as const,
    marginTop: 8,
  },
  skipBtn: {
    background: "transparent",
    border: "none",
    color: "#445566",
    fontSize: 13,
    cursor: "pointer" as const,
    fontFamily: "inherit",
    padding: "4px 0",
  },
  nextBtn: {
    background: "#1a3a5a",
    border: "1px solid #3a6a9a",
    color: "#88ccee",
    fontSize: 15,
    padding: "10px 24px",
    borderRadius: 3,
    cursor: "pointer" as const,
    fontFamily: "inherit",
  },
};
