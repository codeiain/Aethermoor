import { Combatant } from "../api/client";

interface Props {
  turnOrder: Combatant[];
  currentIndex: number;
  onSelect: (id: string) => void;
}

export default function TurnOrder({ turnOrder, currentIndex, onSelect }: Props) {
  return (
    <div style={S.panel}>
      <div style={S.label}>TURN ORDER</div>
      <div style={S.row}>
        {turnOrder.slice(0, 6).map((combatant, idx) => (
          <button
            key={combatant.id}
            style={{
              ...S.portrait,
              ...(idx === currentIndex ? S.active : {}),
              ...(combatant.is_player ? S.player : S.enemy),
            }}
            onClick={() => onSelect(combatant.id)}
          >
            <div style={S.initiative}>{combatant.initiative}</div>
            <div style={S.portraitIcon}>
              {combatant.is_player ? "🧑" : "👾"}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

const S = {
  panel: {
    position: "absolute" as const,
    top: 10,
    left: "50%",
    transform: "translateX(-50%)",
    background: "rgba(0,0,0,0.7)",
    borderRadius: 4,
    padding: "8px 12px",
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    gap: 6,
    maxWidth: "90%",
  },
  label: {
    fontSize: 6,
    color: "#8899aa",
  },
  row: {
    display: "flex",
    gap: 6,
  },
  portrait: {
    width: 40,
    height: 40,
    borderRadius: "50%",
    border: "2px solid #4a5a6a",
    background: "rgba(26, 34, 51, 0.8)",
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    position: "relative" as const,
  },
  active: {
    borderColor: "#FFD700",
    boxShadow: "0 0 8px #FFD700",
  },
  player: {
    borderColor: "#4A90D9",
  },
  enemy: {
    borderColor: "#D94A4A",
  },
  initiative: {
    fontSize: 5,
    color: "#c8a84b",
    position: "absolute" as const,
    top: 2,
  },
  portraitIcon: {
    fontSize: 16,
  },
};