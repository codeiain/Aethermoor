import { useEffect, useRef, useState } from "react";
import {
  craftItem,
  getRecipes,
  type RecipeDetail,
  type RecipeSummary,
} from "../api/client";
import { useGameStore } from "../store/useGameStore";

type Category = "weapon" | "armour" | "consumable" | "material" | "misc";
const CATEGORIES: Category[] = ["weapon", "armour", "consumable", "material", "misc"];

interface BackpackItem {
  slot_index: number;
  item_id: string | null;
  quantity: number;
}

interface Props {
  onClose: () => void;
}

export default function CraftingPanel({ onClose }: Props) {
  const token = useGameStore((s) => s.token);
  const activeCharacter = useGameStore((s) => s.activeCharacter);

  const [category, setCategory] = useState<Category | null>(null);
  const [recipes, setRecipes] = useState<RecipeSummary[]>([]);
  const [selected, setSelected] = useState<RecipeDetail | null>(null);
  const [loadingRecipes, setLoadingRecipes] = useState(false);
  const [crafting, setCrafting] = useState(false);
  const [feedback, setFeedback] = useState<{ ok: boolean; msg: string } | null>(null);
  const feedbackTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Backpack inventory from store (character detail has backpack)
  const backpack: BackpackItem[] = (activeCharacter as unknown as { backpack?: BackpackItem[] })?.backpack ?? [];
  const inventory = buildInventory(backpack);

  useEffect(() => {
    if (!token) return;
    setLoadingRecipes(true);
    getRecipes(token, category ?? undefined)
      .then(setRecipes)
      .catch(() => setRecipes([]))
      .finally(() => setLoadingRecipes(false));
  }, [token, category]);

  function handleSelectRecipe(recipe: RecipeSummary) {
    setSelected(recipe as RecipeDetail);
    setFeedback(null);
  }

  async function handleCraft() {
    if (!token || !activeCharacter || !selected) return;
    setCrafting(true);
    setFeedback(null);
    try {
      const result = await craftItem(token, activeCharacter.id, selected.id);
      showFeedback(true, result.message);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Crafting failed";
      showFeedback(false, msg);
    } finally {
      setCrafting(false);
    }
  }

  function showFeedback(ok: boolean, msg: string) {
    setFeedback({ ok, msg });
    if (feedbackTimer.current) clearTimeout(feedbackTimer.current);
    feedbackTimer.current = setTimeout(() => setFeedback(null), 3000);
  }

  function canCraft(recipe: RecipeSummary | RecipeDetail): boolean {
    if (!("ingredients" in recipe)) return true; // summary — optimistic
    return (recipe as RecipeDetail).ingredients.every(
      (ing) => (inventory[ing.item_id] ?? 0) >= ing.quantity
    );
  }

  return (
    <div style={S.overlay}>
      <div style={S.panel}>
        {/* Header */}
        <div style={S.header}>
          <span style={S.title}>CRAFTING</span>
          <button style={S.closeBtn} onClick={onClose}>✕</button>
        </div>

        {/* Category tabs */}
        <div style={S.tabs}>
          <button
            style={S.tab(category === null)}
            onClick={() => setCategory(null)}
          >
            All
          </button>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              style={S.tab(category === cat)}
              onClick={() => setCategory(cat)}
            >
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>

        <div style={S.body}>
          {/* Recipe list */}
          <div style={S.recipeList}>
            {loadingRecipes ? (
              <div style={S.hint}>Loading…</div>
            ) : recipes.length === 0 ? (
              <div style={S.hint}>No recipes</div>
            ) : (
              recipes.map((r) => (
                <button
                  key={r.id}
                  style={S.recipeRow(selected?.id === r.id)}
                  onClick={() => handleSelectRecipe(r)}
                >
                  <span style={S.recipeName}>{r.name}</span>
                  <span style={S.recipeLevel}>Lv.{r.level_required}</span>
                </button>
              ))
            )}
          </div>

          {/* Detail pane */}
          <div style={S.detail}>
            {selected ? (
              <>
                <div style={S.detailName}>{selected.name}</div>
                {selected.description && (
                  <div style={S.detailDesc}>{selected.description}</div>
                )}
                <div style={S.sectionLabel}>RESULT</div>
                <div style={S.resultRow}>
                  <span style={S.itemTag}>{selected.result_item_id}</span>
                  <span style={S.qty}>×{selected.result_quantity}</span>
                </div>

                {"ingredients" in selected && (selected as RecipeDetail).ingredients.length > 0 && (
                  <>
                    <div style={S.sectionLabel}>MATERIALS</div>
                    {(selected as RecipeDetail).ingredients.map((ing) => {
                      const have = inventory[ing.item_id] ?? 0;
                      const enough = have >= ing.quantity;
                      return (
                        <div key={ing.item_id} style={S.ingredientRow}>
                          <span style={S.itemTag}>{ing.item_id}</span>
                          <span style={enough ? S.haveOk : S.haveShort}>
                            {have}/{ing.quantity}
                          </span>
                        </div>
                      );
                    })}
                  </>
                )}

                <button
                  style={S.craftBtn(canCraft(selected) && !crafting)}
                  disabled={!canCraft(selected) || crafting}
                  onClick={handleCraft}
                >
                  {crafting ? "Crafting…" : "Craft"}
                </button>

                {feedback && (
                  <div style={S.feedback(feedback.ok)}>
                    {feedback.msg}
                  </div>
                )}
              </>
            ) : (
              <div style={S.hint}>Select a recipe</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function buildInventory(backpack: BackpackItem[]): Record<string, number> {
  const inv: Record<string, number> = {};
  for (const item of backpack) {
    if (item.item_id) {
      inv[item.item_id] = (inv[item.item_id] ?? 0) + item.quantity;
    }
  }
  return inv;
}

// ── Styles ────────────────────────────────────────────────────────────────────

const S = {
  overlay: {
    position: "fixed" as const,
    inset: 0,
    background: "rgba(0,0,0,0.7)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 100,
    pointerEvents: "auto" as const,
  },
  panel: {
    width: 520,
    maxWidth: "95vw",
    background: "#0d1320",
    border: "1px solid #2a3a5a",
    borderRadius: 4,
    display: "flex",
    flexDirection: "column" as const,
    maxHeight: "80vh",
    overflow: "hidden" as const,
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "8px 12px",
    borderBottom: "1px solid #1e2a3a",
    background: "#0a0e18",
  },
  title: {
    fontSize: 18,
    color: "#c8a84b",
    letterSpacing: 2,
  },
  closeBtn: {
    background: "transparent",
    border: "none",
    color: "#667788",
    fontSize: 16,
    cursor: "pointer" as const,
    padding: "0 4px",
    fontFamily: "inherit",
  },
  tabs: {
    display: "flex",
    gap: 2,
    padding: "6px 10px",
    borderBottom: "1px solid #1e2a3a",
    flexWrap: "wrap" as const,
  },
  tab: (active: boolean) => ({
    background: active ? "#1e3a5a" : "transparent",
    border: `1px solid ${active ? "#3a5a8a" : "#1e2a3a"}`,
    color: active ? "#c8d8e8" : "#667788",
    fontSize: 14,
    padding: "6px 16px",
    cursor: "pointer" as const,
    borderRadius: 2,
    fontFamily: "inherit",
  }),
  body: {
    display: "flex",
    flex: 1,
    overflow: "hidden" as const,
  },
  recipeList: {
    width: 180,
    borderRight: "1px solid #1e2a3a",
    overflowY: "auto" as const,
    display: "flex",
    flexDirection: "column" as const,
    gap: 1,
    padding: 4,
  },
  recipeRow: (active: boolean) => ({
    background: active ? "#162030" : "transparent",
    border: `1px solid ${active ? "#2a3a5a" : "transparent"}`,
    color: active ? "#c8d8e8" : "#8899aa",
    fontSize: 14,
    padding: "10px 16px",
    cursor: "pointer" as const,
    borderRadius: 2,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    fontFamily: "inherit",
    textAlign: "left" as const,
    width: "100%",
  }),
  recipeName: { flex: 1 },
  recipeLevel: { color: "#c8a84b", fontSize: 12, marginLeft: 6 },
  detail: {
    flex: 1,
    padding: 12,
    overflowY: "auto" as const,
    display: "flex",
    flexDirection: "column" as const,
    gap: 8,
  },
  detailName: { fontSize: 16, color: "#e8e0d0" },
  detailDesc: { fontSize: 14, color: "#667788", lineHeight: 1.4 },
  sectionLabel: {
    fontSize: 12,
    color: "#445566",
    letterSpacing: 1,
    marginTop: 4,
  },
  resultRow: {
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  ingredientRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 8,
  },
  itemTag: {
    fontSize: 14,
    color: "#aabbcc",
    background: "#0a1018",
    border: "1px solid #1e2a3a",
    borderRadius: 2,
    padding: "2px 6px",
  },
  qty: { fontSize: 14, color: "#8899aa" },
  haveOk: { fontSize: 14, color: "#44aa55", minWidth: 40, textAlign: "right" as const },
  haveShort: { fontSize: 14, color: "#cc4433", minWidth: 40, textAlign: "right" as const },
  craftBtn: (enabled: boolean) => ({
    marginTop: 8,
    padding: "12px 28px",
    background: enabled ? "#1a3a5a" : "#0a1018",
    border: `1px solid ${enabled ? "#3a6a9a" : "#1e2a3a"}`,
    color: enabled ? "#88ccee" : "#334455",
    fontSize: 16,
    cursor: enabled ? ("pointer" as const) : ("default" as const),
    borderRadius: 2,
    fontFamily: "inherit",
    alignSelf: "flex-start" as const,
    transition: "background 0.15s",
  }),
  feedback: (ok: boolean) => ({
    fontSize: 14,
    color: ok ? "#44aa55" : "#cc4433",
    padding: "5px 8px",
    background: ok ? "#0a1a0a" : "#1a0a0a",
    border: `1px solid ${ok ? "#1a4a1a" : "#4a1a1a"}`,
    borderRadius: 2,
    animation: "fadeIn 0.2s ease-in",
  }),
  hint: {
    fontSize: 14,
    color: "#445566",
    padding: 12,
  },
};
