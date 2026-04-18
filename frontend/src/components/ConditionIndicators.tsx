import { PlayerCombatState } from "../api/client";

interface Props {
  player: PlayerCombatState;
}

const CONDITION_ICONS: Record<string, string> = {
  poisoned: "🟢",
  burning: "🔥",
  frozen: "❄️",
  bleeding: "🩸",
  stunned: "⭐",
  charmed: "💕",
  frightened: "👻",
  blinded: "👁️",
  dead: "💀",
};

export default function ConditionIndicators({ player }: Props) {
  const conditions = player.conditions;

  return (
    <div style={S.container}>
      {conditions.length > 0 && (
        <div style={S.row}>
          {conditions.slice(0, 3).map((cond) => (
            <div key={cond} style={S.badge}>
              {CONDITION_ICONS[cond.toLowerCase()] || "❓"}
            </div>
          ))}
          {conditions.length > 3 && <span style={S.more}>+{conditions.length - 3}</span>}
        </div>
      )}
    </div>
  );
}

const S = {
  container: {
    position: "absolute" as const,
    bottom: 100,
    left: 10,
  },
  row: {
    display: "flex",
    gap: 4,
    alignItems: "center",
  },
  badge: {
    width: 20,
    height: 20,
    background: "rgba(170, 68, 255, 0.3)",
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 10,
  },
  more: {
    fontSize: 5,
    color: "#aa44ff",
  },
};