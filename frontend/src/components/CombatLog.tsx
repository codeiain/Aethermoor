interface Props {
  entries: string[];
}

export default function CombatLog({ entries }: Props) {
  return (
    <div style={S.panel}>
      <div style={S.label}>COMBAT LOG</div>
      <div style={S.log}>
        {entries.slice(-10).map((entry, idx) => (
          <div
            key={idx}
            style={{
              ...S.entry,
              ...(entry.includes("HIT") || entry.includes("CRIT") ? S.hit : {}),
              ...(entry.includes("MISS") ? S.miss : {}),
            }}
          >
            {entry}
          </div>
        ))}
      </div>
    </div>
  );
}

const S = {
  panel: {
    position: "absolute" as const,
    left: 10,
    top: 80,
    width: 180,
    maxHeight: "40%",
    background: "rgba(0,0,0,0.7)",
    borderRadius: 4,
    padding: 8,
    display: "flex",
    flexDirection: "column" as const,
    gap: 4,
  },
  label: {
    fontSize: 6,
    color: "#8899aa",
    marginBottom: 4,
  },
  log: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 2,
    overflowY: "auto" as const,
  },
  entry: {
    fontSize: 5,
    color: "#e8e0d0",
    lineHeight: 1.4,
    fontFamily: "monospace",
  },
  hit: {
    color: "#FFD700",
  },
  miss: {
    color: "#888888",
  },
};