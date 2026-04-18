import { useState } from "react";
import { createCharacter, ApiError } from "../api/client";
import { useGameStore } from "../store/useGameStore";

const CLASSES = [
  { id: "Fighter", icon: "⚔", color: "#dd7722", desc: "Martial might. Shield & blade." },
  { id: "Wizard", icon: "✦", color: "#5577dd", desc: "Arcane mastery. Spells & scrolls." },
  { id: "Rogue", icon: "🗡", color: "#44aa66", desc: "Swift shadows. Daggers & guile." },
  { id: "Cleric", icon: "✙", color: "#ddcc33", desc: "Divine favour. Heals & smites." },
  { id: "Ranger", icon: "🏹", color: "#558844", desc: "Wild paths. Bow & beast." },
  { id: "Paladin", icon: "🛡", color: "#cc88dd", desc: "Sacred oath. Aura & wrath." },
];

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
  header: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  title: { fontSize: 20, color: "#c8a84b" },
  backBtn: {
    background: "transparent",
    border: "1px solid #334455",
    color: "#667788",
    fontSize: 14,
    fontFamily: "inherit",
    padding: "10px 16px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
  section: { fontSize: 14, color: "#8899aa", marginBottom: 6 },
  nameInput: {
    background: "#0d1220",
    border: "2px solid #2a3a5a",
    borderRadius: 2,
    color: "#e8e0d0",
    fontSize: 18,
    fontFamily: "inherit",
    padding: "14px 18px",
    width: "100%",
    outline: "none" as const,
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(2, 1fr)",
    gap: 10,
    overflowY: "auto" as const,
    flex: 1,
  },
  classCard: (selected: boolean, color: string) => ({
    background: selected ? "#12182a" : "#0a0e16",
    border: `2px solid ${selected ? color : "#1e2a3a"}`,
    borderRadius: 4,
    padding: 12,
    cursor: "pointer" as const,
    display: "flex",
    flexDirection: "column" as const,
    gap: 6,
    alignItems: "center",
    textAlign: "center" as const,
  }),
  classIcon: (color: string) => ({ fontSize: 32, color }),
  className: { fontSize: 14, color: "#e8e0d0" },
  classDesc: { fontSize: 12, color: "#667788", lineHeight: 1.6 },
  btn: (disabled: boolean) => ({
    background: disabled ? "#1a2233" : "#2a4a8a",
    border: `2px solid ${disabled ? "#2a3a4a" : "#4a7acc"}`,
    color: disabled ? "#445566" : "#e8e0d0",
    fontSize: 16,
    fontFamily: "inherit",
    padding: "16px 0",
    cursor: disabled ? "not-allowed" as const : "pointer" as const,
    borderRadius: 2,
    width: "100%",
    flexShrink: 0,
  }),
  note: { fontSize: 14, color: "#556677", textAlign: "center" as const },
  error: { fontSize: 14, color: "#dd5555", textAlign: "center" as const },
};

export default function CharacterCreateScreen() {
  const token = useGameStore((s) => s.token)!;
  const characters = useGameStore((s) => s.characters);
  const setCharacters = useGameStore((s) => s.setCharacters);
  const setActiveCharacter = useGameStore((s) => s.setActiveCharacter);
  const setScreen = useGameStore((s) => s.setScreen);

  const [name, setName] = useState("");
  const [selectedClass, setSelectedClass] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const nextSlot = ([1, 2, 3] as const).find(
    (s) => !characters.some((c) => c.slot === s)
  );

  async function handleCreate() {
    if (!name.trim() || !selectedClass || !nextSlot) return;
    setError("");
    setLoading(true);
    try {
      const char = await createCharacter(token, name.trim(), selectedClass, nextSlot);
      const summary = {
        id: char.id,
        slot: char.slot,
        name: char.name,
        character_class: char.character_class,
        level: char.level,
        xp: char.xp,
        current_hp: char.current_hp,
        max_hp: char.max_hp,
        gold: char.gold,
      };
      setCharacters([...characters, summary]);
      setActiveCharacter({
        ...summary,
        zone_id: char.position?.zone_id ?? "starter_town",
        x: char.position?.x ?? 0,
        y: char.position?.y ?? 0,
      });
      setScreen("game");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create character");
    } finally {
      setLoading(false);
    }
  }

  const canCreate =
    name.trim().length >= 2 && selectedClass !== null && !loading && !!nextSlot;

  return (
    <div style={S.wrap}>
      <div style={S.header}>
        <div style={S.title}>NEW HERO</div>
        <button style={S.backBtn} onClick={() => setScreen("character-select")}>
          ← BACK
        </button>
      </div>

      <div>
        <div style={S.section}>HERO NAME</div>
        <input
          style={S.nameInput}
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter your name..."
          maxLength={30}
        />
      </div>

      <div style={S.section}>CHOOSE CLASS</div>
      <div style={S.grid}>
        {CLASSES.map((cls) => (
          <div
            key={cls.id}
            style={S.classCard(selectedClass === cls.id, cls.color)}
            onClick={() => setSelectedClass(cls.id)}
          >
            <div style={S.classIcon(cls.color)}>{cls.icon}</div>
            <div style={S.className}>{cls.id.toUpperCase()}</div>
            <div style={S.classDesc}>{cls.desc}</div>
          </div>
        ))}
      </div>

      {error && <div style={S.error}>{error}</div>}
      {!nextSlot && (
        <div style={S.error}>All character slots are full.</div>
      )}

      <div style={S.note}>
        Ability scores are rolled randomly per D&D rules. Good luck, adventurer.
      </div>

      <button style={S.btn(!canCreate)} disabled={!canCreate} onClick={handleCreate}>
        {loading ? "FORGING HERO..." : "BEGIN ADVENTURE"}
      </button>
    </div>
  );
}
