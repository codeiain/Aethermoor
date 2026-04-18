import { useEffect, useState } from "react";
import { getMyCharacters, getZone, ApiError } from "../api/client";
import { useGameStore } from "../store/useGameStore";
import type { CharacterSummary } from "../store/useGameStore";

const CLASS_COLORS: Record<string, string> = {
  Fighter: "#dd7722",
  Wizard: "#5577dd",
  Rogue: "#44aa66",
  Cleric: "#ddcc33",
  Ranger: "#558844",
  Paladin: "#cc88dd",
};

const CLASS_ICONS: Record<string, string> = {
  Fighter: "⚔",
  Wizard: "✦",
  Rogue: "🗡",
  Cleric: "✙",
  Ranger: "🏹",
  Paladin: "🛡",
};

const S = {
  wrap: {
    display: "flex",
    flexDirection: "column" as const,
    height: "100%",
    background: "linear-gradient(180deg, #0d0d2b 0%, #1a0a2e 100%)",
    padding: 20,
    gap: 16,
    overflow: "hidden" as const,
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  title: { fontSize: 20, color: "#c8a84b" },
  logoutBtn: {
    background: "transparent",
    border: "1px solid #334455",
    color: "#556677",
    fontSize: 14,
    fontFamily: "inherit",
    padding: "10px 16px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
  slots: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 12,
    flex: 1,
    overflowY: "auto" as const,
  },
  slot: (occupied: boolean) => ({
    background: occupied ? "#12182a" : "#0a0e18",
    border: `2px solid ${occupied ? "#3a4a6b" : "#1e2a3a"}`,
    borderRadius: 4,
    padding: 16,
    display: "flex",
    alignItems: "center",
    gap: 16,
    cursor: "pointer" as const,
    transition: "border-color 0.15s",
  }),
  icon: (cls: string) => ({
    width: 48,
    height: 48,
    background: "#0d1220",
    border: `2px solid ${CLASS_COLORS[cls] ?? "#445566"}`,
    borderRadius: 2,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 20,
    flexShrink: 0,
  }),
  emptyIcon: {
    width: 48,
    height: 48,
    background: "#0a0e18",
    border: "2px dashed #1e2a3a",
    borderRadius: 2,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 20,
    color: "#334455",
    flexShrink: 0,
  },
  charInfo: { display: "flex", flexDirection: "column" as const, gap: 6 },
  charName: { fontSize: 18, color: "#e8e0d0" },
  charClass: (cls: string) => ({ fontSize: 14, color: CLASS_COLORS[cls] ?? "#8899aa" }),
  charStats: { fontSize: 12, color: "#667788" },
  emptyText: { fontSize: 14, color: "#445566" },
  hpBar: { width: 120, height: 6, background: "#1a0a0a", borderRadius: 1 },
  hpFill: (pct: number) => ({
    width: `${pct * 100}%`,
    height: "100%",
    background: pct > 0.5 ? "#44aa55" : pct > 0.25 ? "#aaaa33" : "#cc4433",
    borderRadius: 1,
  }),
  error: { fontSize: 14, color: "#dd5555", textAlign: "center" as const },
};

export default function CharacterSelectScreen() {
  const token = useGameStore((s) => s.token)!;
  const username = useGameStore((s) => s.username);
  const setScreen = useGameStore((s) => s.setScreen);
  const setCharacters = useGameStore((s) => s.setCharacters);
  const setActiveCharacter = useGameStore((s) => s.setActiveCharacter);
  const setCurrentZone = useGameStore((s) => s.setCurrentZone);
  const logout = useGameStore((s) => s.logout);
  const characters = useGameStore((s) => s.characters);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getMyCharacters(token)
      .then((chars) => {
        setCharacters(chars);
        setLoading(false);
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Failed to load characters");
        setLoading(false);
      });
  }, [token, setCharacters]);

  async function handleSelectCharacter(char: CharacterSummary) {
    setLoading(true);
    try {
      // Fetch zone to get spawn point
      const zone = await getZone(token, "starter_town");
      setCurrentZone(zone);
      setActiveCharacter({
        ...char,
        zone_id: zone.id,
        x: zone.spawn_x,
        y: zone.spawn_y,
      });
      setScreen("game");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load zone");
    } finally {
      setLoading(false);
    }
  }

  function handleNewCharacter() {
    setScreen("character-create");
  }

  const slots = [1, 2, 3];

  return (
    <div style={S.wrap}>
      <div style={S.header}>
        <div style={S.title}>CHOOSE HERO</div>
        <div style={{ fontSize: 8, color: "#667788" }}>
          {username}
          <button style={S.logoutBtn} onClick={logout}>
            LOGOUT
          </button>
        </div>
      </div>

      {error && <div style={S.error}>{error}</div>}

      <div style={S.slots}>
        {loading
          ? [1, 2, 3].map((i) => (
              <div key={i} style={S.slot(false)}>
                <div style={S.emptyIcon}>…</div>
                <div style={S.emptyText}>LOADING...</div>
              </div>
            ))
          : slots.map((slotNum) => {
              const char = characters.find((c) => c.slot === slotNum);
              if (char) {
                const hpPct = char.current_hp / char.max_hp;
                return (
                  <div
                    key={slotNum}
                    style={S.slot(true)}
                    onClick={() => handleSelectCharacter(char)}
                  >
                    <div style={S.icon(char.character_class)}>
                      {CLASS_ICONS[char.character_class] ?? "?"}
                    </div>
                    <div style={S.charInfo}>
                      <div style={S.charName}>{char.name}</div>
                      <div style={S.charClass(char.character_class)}>
                        LV.{char.level} {char.character_class.toUpperCase()}
                      </div>
                      <div style={S.hpBar}>
                        <div style={S.hpFill(hpPct)} />
                      </div>
                      <div style={S.charStats}>
                        HP {char.current_hp}/{char.max_hp} &nbsp;·&nbsp; {char.gold}G
                      </div>
                    </div>
                  </div>
                );
              }
              return (
                <div key={slotNum} style={S.slot(false)} onClick={handleNewCharacter}>
                  <div style={S.emptyIcon}>+</div>
                  <div style={S.emptyText}>NEW CHARACTER</div>
                </div>
              );
            })}
      </div>
    </div>
  );
}
