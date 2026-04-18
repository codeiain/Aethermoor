interface Props {
  disabled: boolean;
  onAction: (type: "attack" | "spell" | "item" | "flee", targetId?: string) => void;
  canFlee: boolean;
}

export default function ActionBar({ disabled, onAction, canFlee }: Props) {
  const btnStyle: React.CSSProperties = {
    width: 64,
    height: 64,
    background: "rgba(26, 34, 51, 0.9)",
    border: "2px solid #4a5a6a",
    borderRadius: 4,
    color: "#e8e0d0",
    fontFamily: "inherit",
    fontSize: 7,
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.5 : 1,
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
    transition: "transform 0.1s, background 0.1s",
  };

  return (
    <div style={S.bar}>
      <button
        style={btnStyle}
        onClick={() => onAction("attack")}
        disabled={disabled}
      >
        <span style={S.icon}>⚔️</span>
        <span>ATTACK</span>
      </button>
      <button
        style={btnStyle}
        onClick={() => onAction("spell")}
        disabled={disabled}
      >
        <span style={S.icon}>✨</span>
        <span>SPELL</span>
      </button>
      <button
        style={btnStyle}
        onClick={() => onAction("item")}
        disabled={disabled}
      >
        <span style={S.icon}>🎒</span>
        <span>ITEM</span>
      </button>
      <button
        style={{ ...btnStyle, ...(canFlee ? {} : { opacity: 0.4 }) }}
        onClick={() => onAction("flee")}
        disabled={disabled || !canFlee}
      >
        <span style={S.icon}>🏃</span>
        <span>FLEE</span>
      </button>
    </div>
  );
}

const S = {
  bar: {
    position: "absolute" as const,
    bottom: 20,
    left: "50%",
    transform: "translateX(-50%)",
    display: "flex",
    gap: 8,
    padding: 12,
    background: "rgba(0,0,0,0.5)",
    borderRadius: 8,
  },
  icon: {
    fontSize: 16,
  },
};