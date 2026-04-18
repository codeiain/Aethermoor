import { PlayerCombatState } from "../api/client";

interface Props {
  player: PlayerCombatState;
}

export default function PlayerStatus({ player }: Props) {
  const hpPct = player.hp / player.max_hp;
  const hpColor = hpPct > 0.5 ? "#44aa55" : hpPct > 0.25 ? "#aaaa33" : "#cc4433";

  return (
    <div style={S.panel}>
      <div style={S.row}>
        <div style={S.portrait}>🧑</div>
        <div style={S.stats}>
          <div style={S.name}>HERO</div>
          <div style={S.row}>
            <span style={S.label}>HP</span>
            <div style={S.bar}>
              <div style={{ ...S.fill, width: `${hpPct * 100}%`, background: hpColor }} />
            </div>
            <span style={S.value}>{player.hp}/{player.max_hp}</span>
          </div>
          <div style={S.row}>
            <span style={S.label}>AC</span>
            <span style={S.value}>{player.ac}</span>
          </div>
        </div>
      </div>
      {player.conditions.length > 0 && (
        <div style={S.conds}>
          {player.conditions.map((c) => (
            <span key={c} style={S.condBadge}>{c}</span>
          ))}
        </div>
      )}
    </div>
  );
}

const S = {
  panel: {
    position: "absolute" as const,
    bottom: 100,
    left: 10,
    background: "rgba(0,0,0,0.75)",
    border: "2px solid #2a3a5a",
    borderRadius: 4,
    padding: 8,
    minWidth: 140,
  },
  row: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    marginBottom: 4,
  },
  portrait: {
    fontSize: 24,
  },
  stats: {
    flex: 1,
  },
  name: {
    fontSize: 6,
    color: "#c8a84b",
    marginBottom: 4,
  },
  label: {
    fontSize: 5,
    color: "#8899aa",
    width: 14,
  },
  bar: {
    flex: 1,
    height: 5,
    background: "#0a0e18",
    borderRadius: 1,
    overflow: "hidden" as const,
  },
  fill: {
    height: "100%",
    transition: "width 0.3s",
  },
  value: {
    fontSize: 5,
    color: "#667788",
    minWidth: 35,
    textAlign: "right" as const,
  },
  conds: {
    display: "flex",
    flexWrap: "wrap" as const,
    gap: 4,
    marginTop: 4,
  },
  condBadge: {
    fontSize: 5,
    color: "#aa44ff",
    background: "rgba(170, 68, 255, 0.2)",
    padding: "2px 4px",
    borderRadius: 2,
  },
};