import { useState } from "react";
import { useGameStore } from "../store/useGameStore";
import CraftingPanel from "./CraftingPanel";
import SkillTreePanel from "./SkillTreePanel";

/**
 * HUD — React overlay rendered on top of the Phaser canvas.
 *
 * Displays: HP/MP bars, player name + level badge, zone name,
 * minimap stub, and HUD action buttons (Craft, Menu).
 */
export default function HUD() {
  const char = useGameStore((s) => s.activeCharacter);
  const zone = useGameStore((s) => s.currentZone);
  const setScreen = useGameStore((s) => s.setScreen);
  const [craftingOpen, setCraftingOpen] = useState(false);
  const [skillTreeOpen, setSkillTreeOpen] = useState(false);

  if (!char) return null;

  const hpPct = Math.max(0, Math.min(1, char.current_hp / char.max_hp));
  // MP not yet tracked server-side — show full bar as placeholder
  const mpPct = 1.0;

  return (
    <>
      <div style={S.hud}>
        {/* Top-left: player info + HP/MP bars */}
        <div style={S.topLeft}>
          <div style={S.nameRow}>
            <span style={S.charName}>{char.name}</span>
            <span style={S.levelBadge}>Lv.{char.level}</span>
          </div>
          <div style={S.barRow}>
            <span style={S.barLabel}>HP</span>
            <div style={S.barTrack}>
              <div style={S.hpFill(hpPct)} />
            </div>
            <span style={S.barValue}>{char.current_hp}/{char.max_hp}</span>
          </div>
          <div style={S.barRow}>
            <span style={S.barLabel}>MP</span>
            <div style={S.barTrack}>
              <div style={S.mpFill(mpPct)} />
            </div>
            <span style={S.barValue}>--/--</span>
          </div>
        </div>

        {/* Top-right: minimap stub */}
        <div style={S.minimap}>
          <div style={S.minimapLabel}>MAP</div>
          <div style={S.minimapDot} />
        </div>

        {/* Bottom-left: zone name badge */}
        {zone && (
          <div style={S.zoneBadge}>
            <span style={S.zoneText}>{zone.name.toUpperCase()}</span>
          </div>
        )}

        {/* Bottom-right: action buttons */}
        <div style={S.actionBar}>
          <button style={S.actionBtn} onClick={() => setSkillTreeOpen(true)}>
            SKILLS
          </button>
          <button style={S.actionBtn} onClick={() => setCraftingOpen(true)}>
            CRAFT
          </button>
          <button style={S.actionBtn} onClick={() => setScreen("character-select")}>
            MENU
          </button>
        </div>
      </div>

      {craftingOpen && <CraftingPanel onClose={() => setCraftingOpen(false)} />}
      {skillTreeOpen && <SkillTreePanel onClose={() => setSkillTreeOpen(false)} />}
    </>
  );
}

const S = {
  hud: {
    position: "absolute" as const,
    inset: 0,
    pointerEvents: "none" as const,
    fontFamily: "'Press Start 2P', monospace",
    zIndex: 20,
  },
  topLeft: {
    position: "absolute" as const,
    top: 10,
    left: 10,
    background: "rgba(0,0,0,0.55)",
    border: "1px solid #2a3a5a",
    borderRadius: 3,
    padding: "8px 10px",
    display: "flex",
    flexDirection: "column" as const,
    gap: 5,
    minWidth: 160,
  },
  nameRow: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    marginBottom: 2,
  },
  charName: { fontSize: 12, color: "#e8e0d0" },
  levelBadge: {
    fontSize: 10,
    color: "#c8a84b",
    background: "#1a1408",
    border: "1px solid #c8a84b44",
    borderRadius: 2,
    padding: "1px 4px",
  },
  barRow: {
    display: "flex",
    alignItems: "center",
    gap: 5,
  },
  barLabel: { fontSize: 10, color: "#8899aa", width: 18 },
  barTrack: {
    flex: 1,
    height: 7,
    background: "#0a0e18",
    borderRadius: 1,
    overflow: "hidden" as const,
    border: "1px solid #1e2a3a",
  },
  hpFill: (pct: number) => ({
    width: `${pct * 100}%`,
    height: "100%",
    background: pct > 0.5 ? "#44aa55" : pct > 0.25 ? "#aaaa33" : "#cc4433",
    transition: "width 0.2s",
  }),
  mpFill: (pct: number) => ({
    width: `${pct * 100}%`,
    height: "100%",
    background: "#4466cc",
    transition: "width 0.2s",
  }),
  barValue: { fontSize: 10, color: "#667788", minWidth: 42, textAlign: "right" as const },
  minimap: {
    position: "absolute" as const,
    top: 10,
    right: 10,
    width: 64,
    height: 64,
    background: "rgba(0,0,0,0.6)",
    border: "1px solid #2a3a5a",
    borderRadius: 2,
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
  },
  minimapLabel: { fontSize: 10, color: "#445566" },
  minimapDot: {
    width: 5,
    height: 5,
    background: "#4488ee",
    borderRadius: "50%",
  },
  zoneBadge: {
    position: "absolute" as const,
    bottom: 70,
    left: "50%",
    transform: "translateX(-50%)",
    background: "rgba(0,0,0,0.55)",
    border: "1px solid #2a3a5a",
    borderRadius: 2,
    padding: "5px 12px",
  },
  zoneText: { fontSize: 10, color: "#8899aa" },
  actionBar: {
    position: "absolute" as const,
    bottom: 70,
    right: 10,
    display: "flex",
    flexDirection: "column" as const,
    gap: 4,
    pointerEvents: "auto" as const,
  },
  actionBtn: {
    background: "rgba(0,0,0,0.55)",
    border: "1px solid #2a3a5a",
    color: "#667788",
    fontSize: 12,
    fontFamily: "inherit",
    padding: "6px 10px",
    cursor: "pointer" as const,
    borderRadius: 2,
    pointerEvents: "auto" as const,
  },
};
