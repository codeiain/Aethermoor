import { EnemyCombatState } from "../api/client";

interface Props {
  targetId: string | null;
  enemies: EnemyCombatState[];
  onClose: () => void;
}

export default function TargetInfo({ targetId, enemies, onClose }: Props) {
  const target = targetId ? enemies.find((e) => e.id === targetId) : null;

  if (!target) return null;

  const hpPct = target.hp / target.max_hp;
  const hpColor = hpPct > 0.5 ? "#44aa55" : hpPct > 0.25 ? "#aaaa33" : "#cc4433";

  return (
    <div style={S.panel}>
      <div style={S.header}>
        <span style={S.name}>{target.name}</span>
        <button style={S.closeBtn} onClick={onClose}>✕</button>
      </div>
      <div style={S.row}>
        <span style={S.label}>HP</span>
        <div style={S.hpBar}>
          <div style={{ ...S.hpFill, width: `${hpPct * 100}%`, background: hpColor }} />
        </div>
        <span style={S.value}>{target.hp}/{target.max_hp}</span>
      </div>
      <div style={S.row}>
        <span style={S.label}>AC</span>
        <span style={S.value}>{target.ac}</span>
      </div>
      {target.conditions.length > 0 && (
        <div style={S.conditions}>
          <span style={S.label}>STATUS</span>
          <div style={S.condList}>
            {target.conditions.map((c) => (
              <span key={c} style={S.condBadge}>{c}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

const S = {
  panel: {
    position: "absolute" as const,
    right: 10,
    top: 80,
    width: 160,
    background: "rgba(0,0,0,0.8)",
    border: "2px solid #4a5a6a",
    borderRadius: 4,
    padding: 10,
    display: "flex",
    flexDirection: "column" as const,
    gap: 8,
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  name: {
    fontSize: 7,
    color: "#e8e0d0",
    textTransform: "uppercase" as const,
  },
  closeBtn: {
    background: "none",
    border: "none",
    color: "#667788",
    fontSize: 10,
    cursor: "pointer",
  },
  row: {
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  label: {
    fontSize: 5,
    color: "#8899aa",
    width: 20,
  },
  hpBar: {
    flex: 1,
    height: 6,
    background: "#0a0e18",
    borderRadius: 1,
    overflow: "hidden" as const,
  },
  hpFill: {
    height: "100%",
    transition: "width 0.3s",
  },
  value: {
    fontSize: 5,
    color: "#e8e0d0",
    minWidth: 50,
    textAlign: "right" as const,
  },
  conditions: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 4,
  },
  condList: {
    display: "flex",
    flexWrap: "wrap" as const,
    gap: 4,
  },
  condBadge: {
    fontSize: 5,
    color: "#aa44ff",
    background: "rgba(170, 68, 255, 0.2)",
    padding: "2px 4px",
    borderRadius: 2,
  },
};