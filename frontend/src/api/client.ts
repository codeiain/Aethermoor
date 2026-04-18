/**
 * AETHERMOOR API client.
 *
 * All requests go through the gateway at /api/* (Vite dev: proxied + rewritten;
 * production: Nginx strips /api/ prefix before the gateway sees the path).
 */

const BASE = "/api";

// ── Store import (for runtime access) ─────────────────────────────────────────
import { useGameStore } from "../store/useGameStore";

// ── Typed response shapes ─────────────────────────────────────────────────────

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface UserInfo {
  user_id: string;
  username: string;
}

export interface CharacterSummary {
  id: string;
  slot: number;
  name: string;
  character_class: string;
  level: number;
  xp: number;
  current_hp: number;
  max_hp: number;
  gold: number;
  created_at: string;
  updated_at: string;
}

export interface CharacterDetail extends CharacterSummary {
  user_id: string;
  ability_scores: {
    strength: number;
    dexterity: number;
    constitution: number;
    intelligence: number;
    wisdom: number;
    charisma: number;
  };
  position: {
    zone_id: string;
    x: number;
    y: number;
    respawn_zone_id: string;
    respawn_x: number;
    respawn_y: number;
  } | null;
  equipment: Array<{ slot_name: string; item_id: string | null }>;
  backpack: Array<{ slot_index: number; item_id: string | null; quantity: number }>;
}

export interface ZoneSummary {
  id: string;
  name: string;
  biome: string;
  level_min: number;
  level_max: number;
  max_players: number;
  current_players: number;
  width: number;
  height: number;
  spawn_x: number;
  spawn_y: number;
  is_active: boolean;
}

export interface ZoneDetail extends ZoneSummary {
  tilemap: unknown;
  npc_templates: Array<{
    id: string;
    npc_type: string;
    name: string;
    spawn_x: number;
    spawn_y: number;
    patrol_path: Array<{ x: number; y: number }>;
    respawn_timer_sec: number;
  }>;
}

// ── HTTP helper ───────────────────────────────────────────────────────────────

class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  token?: string | null,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const resp = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      const err = (await resp.json()) as { detail?: string };
      if (err.detail) detail = err.detail;
    } catch {
      // ignore parse error
    }
    throw new ApiError(resp.status, detail);
  }

  return resp.json() as Promise<T>;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

/** Register a new account. Returns the new user's auth token pair. */
export async function register(
  email: string,
  password: string,
): Promise<AuthResponse> {
  return request<AuthResponse>("POST", "/auth/register", {
    email,
    password,
  });
}

/** Log in with email + password. Returns JWT access token. */
export async function login(
  email: string,
  password: string,
): Promise<AuthResponse> {
  return request<AuthResponse>("POST", "/auth/login", {
    email,
    password,
  });
}

/** Verify a token and get user info. */
export async function getMe(token: string): Promise<UserInfo> {
  return request<UserInfo>("GET", "/auth/me", undefined, token);
}

// ── Players ───────────────────────────────────────────────────────────────────

/** Get all characters for the authenticated user. */
export async function getMyCharacters(token: string): Promise<CharacterSummary[]> {
  return request<CharacterSummary[]>("GET", "/players/me", undefined, token);
}

/** Get full character details including position. */
export async function getCharacter(
  token: string,
  characterId: string,
): Promise<CharacterDetail> {
  return request<CharacterDetail>("GET", `/players/${characterId}`, undefined, token);
}

/** Create a new character. */
export async function createCharacter(
  token: string,
  name: string,
  characterClass: string,
  slot: number,
): Promise<CharacterDetail> {
  return request<CharacterDetail>(
    "POST",
    "/players/create",
    { name, character_class: characterClass, slot },
    token,
  );
}

// ── World ─────────────────────────────────────────────────────────────────────

/** List all active zones. */
export async function listZones(token: string): Promise<ZoneSummary[]> {
  return request<ZoneSummary[]>("GET", "/world/zones", undefined, token);
}

/** Get full zone detail including tilemap. */
export async function getZone(token: string, zoneId: string): Promise<ZoneDetail> {
  return request<ZoneDetail>("GET", `/world/zones/${zoneId}`, undefined, token);
}

// ── Combat ─────────────────────────────────────────────────────────────────────

interface BackendCombatant {
  id: string;
  name: string;
  is_player: boolean;
  character_class?: string;
  level?: number;
  hp: number;
  max_hp: number;
  ac: number;
  weapon?: string;
  conditions: Array<{ name: string; stacks: number }>;
  cr?: number;
  gold_drop_min?: number;
  gold_drop_max?: number;
}

interface BackendCombatState {
  combat_id: string;
  status: "active" | "player_won" | "player_fled" | "player_died";
  round: number;
  turn_order: string[];
  current_turn_index: number;
  combatants: Record<string, BackendCombatant>;
  last_actions?: Array<{ description: string }>;
  xp_awarded?: number;
  gold_awarded?: number;
  message?: string;
}

interface BackendActionResponse {
  combat_id: string;
  status: "active" | "player_won" | "player_fled" | "player_died";
  round: number;
  current_turn_id: string | null;
  turn_order: string[];
  combatants: Record<string, BackendCombatant>;
  action_result: {
    round: number;
    acting_id: string;
    action_type: string;
    target_id: string | null;
    roll_result: Record<string, unknown> | null;
    description: string;
  };
  npc_action: {
    round: number;
    acting_id: string;
    action_type: string;
    target_id: string | null;
    roll_result: Record<string, unknown> | null;
    description: string;
  } | null;
  message: string;
  xp_awarded: number;
  gold_awarded: number;
}

export interface Combatant {
  id: string;
  name: string;
  is_player: boolean;
  initiative: number;
}

export interface PlayerCombatState {
  hp: number;
  max_hp: number;
  ac: number;
  conditions: string[];
}

export interface EnemyCombatState {
  id: string;
  name: string;
  npc_type: string;
  hp: number;
  max_hp: number;
  ac: number;
  conditions: string[];
}

export interface CombatState {
  combat_id: string;
  turn_order: Combatant[];
  current_turn_index: number;
  player: PlayerCombatState;
  enemies: EnemyCombatState[];
  combat_log: string[];
  status: "active" | "victory" | "defeat" | "fled";
}

export interface ActionResponse {
  success: boolean;
  roll_result?: {
    d20: number;
    modifier: number;
    total: number;
    is_crit: boolean;
    is_miss: boolean;
  };
  damage?: number;
  damage_type?: string;
  npc_action?: string;
  combat_log: string[];
  updated_state: CombatState;
}

function transformBackendCombatState(backend: BackendCombatState, initiativeRolls?: Record<string, { initiative: number }>): CombatState {
  const combatants = backend.combatants;
  const turnOrder = backend.turn_order;

  const turnOrderCombatants: Combatant[] = turnOrder.map((id, idx) => {
    const combatant = combatants[id];
    const initiative = initiativeRolls?.[id]?.initiative ?? (100 - idx);
    return {
      id,
      name: combatant?.name ?? id,
      is_player: combatant?.is_player ?? false,
      initiative,
    };
  });

  const playerCombatant = Object.values(combatants).find((c) => c.is_player);
  const npcCombatants = Object.values(combatants).filter((c) => !c.is_player);

  const player: PlayerCombatState = playerCombatant ? {
    hp: playerCombatant.hp,
    max_hp: playerCombatant.max_hp,
    ac: playerCombatant.ac,
    conditions: playerCombatant.conditions.map((c) => c.name),
  } : { hp: 0, max_hp: 0, ac: 0, conditions: [] };

  const enemies: EnemyCombatState[] = npcCombatants.map((c) => ({
    id: c.id,
    name: c.name,
    npc_type: c.weapon ?? "creature",
    hp: c.hp,
    max_hp: c.max_hp,
    ac: c.ac,
    conditions: c.conditions.map((cond) => cond.name),
  }));

  const combatLog = (backend.last_actions ?? []).map((a) => a.description);

  let status: CombatState["status"] = "active";
  if (backend.status === "player_won") status = "victory";
  else if (backend.status === "player_died") status = "defeat";
  else if (backend.status === "player_fled") status = "fled";

  return {
    combat_id: backend.combat_id,
    turn_order: turnOrderCombatants,
    current_turn_index: backend.current_turn_index,
    player,
    enemies,
    combat_log: combatLog,
    status,
  };
}

function transformBackendActionResponse(backend: BackendActionResponse): ActionResponse {
  const rollResult = backend.action_result?.roll_result as { d20?: number; modifier?: number; total?: number; is_crit?: boolean; is_miss?: boolean } | undefined;
  const combatLog = [
    backend.action_result.description,
    ...(backend.npc_action ? [backend.npc_action.description] : []),
  ];

  let status: CombatState["status"] = "active";
  if (backend.status === "player_won") status = "victory";
  else if (backend.status === "player_died") status = "defeat";
  else if (backend.status === "player_fled") status = "fled";

  return {
    success: backend.status === "active",
    roll_result: rollResult ? {
      d20: rollResult.d20 ?? 0,
      modifier: rollResult.modifier ?? 0,
      total: rollResult.total ?? 0,
      is_crit: rollResult.is_crit ?? false,
      is_miss: rollResult.is_miss ?? false,
    } : undefined,
    npc_action: backend.npc_action?.description,
    combat_log: combatLog,
    updated_state: {
      combat_id: backend.combat_id,
      turn_order: backend.turn_order.map((id, idx) => ({
        id,
        name: backend.combatants[id]?.name ?? id,
        is_player: backend.combatants[id]?.is_player ?? false,
        initiative: 100 - idx,
      })),
      current_turn_index: 0,
      player: (() => {
        const p = Object.values(backend.combatants).find((c) => c.is_player);
        return p ? {
          hp: p.hp,
          max_hp: p.max_hp,
          ac: p.ac,
          conditions: p.conditions.map((c) => c.name),
        } : { hp: 0, max_hp: 0, ac: 0, conditions: [] };
      })(),
      enemies: Object.values(backend.combatants)
        .filter((c) => !c.is_player)
        .map((c) => ({
          id: c.id,
          name: c.name,
          npc_type: c.weapon ?? "creature",
          hp: c.hp,
          max_hp: c.max_hp,
          ac: c.ac,
          conditions: c.conditions.map((cond) => cond.name),
        })),
      combat_log: [],
      status,
    },
  };
}

/** Start combat with an NPC. */
export async function startCombat(
  token: string,
  npcId: string,
  playerId: string,
): Promise<CombatState> {
  const char = useGameStore.getState().activeCharacter;
  const backend = await request<BackendCombatState & { initiative_rolls?: Record<string, { initiative: number }> }>(
    "POST",
    "/combat/start",
    {
      character_id: playerId,
      character_name: char?.name ?? "Hero",
      character_class: char?.character_class ?? "Fighter",
      character_level: char?.level ?? 1,
      character_hp: char?.current_hp ?? 10,
      character_max_hp: char?.max_hp ?? 10,
      character_ac: 10,
      npc_template_id: npcId,
      npc_name: "Wild Creature",
      npc_hp: 20,
      npc_max_hp: 20,
      npc_ac: 12,
      zone_id: char?.zone_id ?? "starter_town",
    },
    token,
  );
  return transformBackendCombatState(backend, backend.initiative_rolls);
}

/** Get current combat state. */
export async function getCombat(token: string, combatId: string): Promise<CombatState> {
  const backend = await request<BackendCombatState>("GET", `/combat/${combatId}`, undefined, token);
  return transformBackendCombatState(backend);
}

/** Submit player action in combat. */
export async function submitCombatAction(
  token: string,
  combatId: string,
  action: {
    action_type: "attack" | "spell" | "item" | "flee";
    target_id?: string;
    spell_id?: string;
    item_id?: string;
  },
): Promise<ActionResponse> {
  const charId = useGameStore.getState().activeCharacter?.id ?? "";
  const backend = await request<BackendActionResponse>(
    "POST",
    `/combat/${combatId}/action`,
    {
      character_id: charId,
      action_type: action.action_type,
      target_id: action.target_id,
    },
    token,
  );
  return transformBackendActionResponse(backend);
}

// ── Crafting ──────────────────────────────────────────────────────────────────

export interface RecipeIngredient {
  item_id: string;
  quantity: number;
}

export interface RecipeSummary {
  id: string;
  name: string;
  description: string;
  category: "weapon" | "armour" | "consumable" | "material" | "misc";
  result_item_id: string;
  result_quantity: number;
  level_required: number;
}

export interface RecipeDetail extends RecipeSummary {
  ingredients: RecipeIngredient[];
}

export interface CraftResult {
  success: boolean;
  message: string;
  result_item_id: string;
  result_quantity: number;
}

/** List all crafting recipes, optionally filtered by category. */
export async function getRecipes(
  token: string,
  category?: RecipeSummary["category"],
): Promise<RecipeSummary[]> {
  const qs = category ? `?category=${encodeURIComponent(category)}` : "";
  return request<RecipeSummary[]>("GET", `/crafting/recipes${qs}`, undefined, token);
}

/** Get full recipe detail including ingredients. */
export async function getRecipeDetail(token: string, recipeId: string): Promise<RecipeDetail> {
  return request<RecipeDetail>("GET", `/crafting/recipes/${recipeId}`, undefined, token);
}

/** Attempt to craft an item. Deducts materials and adds result to backpack. */
export async function craftItem(
  token: string,
  characterId: string,
  recipeId: string,
): Promise<CraftResult> {
  return request<CraftResult>(
    "POST",
    "/crafting/craft",
    { character_id: characterId, recipe_id: recipeId },
    token,
  );
}

// ── Tutorial ──────────────────────────────────────────────────────────────────

export interface TutorialState {
  /** null = not started, 0–4 = last completed step, -1 = done/skipped */
  tutorial_step: number | null;
}

/** Get tutorial progress for a character. */
export async function getTutorialState(
  token: string,
  characterId: string,
): Promise<TutorialState> {
  return request<TutorialState>("GET", `/players/${characterId}/tutorial-state`, undefined, token);
}

/** Advance tutorial to the given step (0–4) or skip entirely (-1). */
export async function advanceTutorialStep(
  token: string,
  characterId: string,
  step: number,
): Promise<TutorialState> {
  return request<TutorialState>(
    "POST",
    `/players/${characterId}/tutorial-step/${step}`,
    undefined,
    token,
  );
}

// ── Inventory ──────────────────────────────────────────────────────────────────

export interface ItemStats {
  bonus_attack?: number;
  bonus_defense?: number;
  bonus_hp?: number;
  hp_restore?: number;
  [key: string]: number | undefined;
}

export interface InventoryItemDetail {
  id: string;
  name: string;
  type: "weapon" | "armour" | "consumable" | "material" | "misc";
  rarity: "common" | "uncommon" | "rare" | "epic" | "legendary";
  stackable: boolean;
  max_stack: number;
  stats: ItemStats;
  description: string;
  equippable_slot: string | null;
}

export interface InventoryItem {
  id: string;
  item_id: string;
  quantity: number;
  slot_index: number | null;
  equipped_slot: string | null;
  item: InventoryItemDetail;
}

export interface InventoryResponse {
  character_id: string;
  backpack: Array<InventoryItem | null>;
  equipment: Record<string, InventoryItem | null>;
  equipped_stats: ItemStats;
}

export interface LootResponse {
  character_id: string;
  item_id: string;
  quantity: number;
  result: "equipped" | "backpack" | "stacked" | "rejected";
  inventory_item_id: string | null;
  slot_type: string | null;
  slot_value: string | number | null;
}

export interface UseItemResponse {
  inventory_item_id: string;
  item_id: string;
  quantity_remaining: number;
  effects: ItemStats;
}

/** Get a character's full inventory (backpack + equipment). */
export async function getInventory(
  token: string,
  characterId: string,
): Promise<InventoryResponse> {
  return request<InventoryResponse>("GET", `/inventory/${characterId}`, undefined, token);
}

/** Equip a backpack item to an equipment slot. */
export async function equipItem(
  token: string,
  characterId: string,
  inventoryItemId: string,
  slot: string,
): Promise<InventoryResponse> {
  return request<InventoryResponse>(
    "POST",
    `/inventory/${characterId}/equip`,
    { inventory_item_id: inventoryItemId, slot },
    token,
  );
}

/** Move an equipped item back to the backpack. */
export async function unequipItem(
  token: string,
  characterId: string,
  slot: string,
): Promise<InventoryResponse> {
  return request<InventoryResponse>(
    "POST",
    `/inventory/${characterId}/unequip`,
    { slot },
    token,
  );
}

/** Drop (destroy) an inventory item. */
export async function dropItem(
  token: string,
  characterId: string,
  inventoryItemId: string,
  quantity: number = 1,
): Promise<{ message: string }> {
  return request<{ message: string }>(
    "POST",
    `/inventory/${characterId}/drop`,
    { inventory_item_id: inventoryItemId, quantity },
    token,
  );
}

/** Use a consumable item (e.g. health potion). Returns the item's effects. */
export async function useItem(
  token: string,
  characterId: string,
  inventoryItemId: string,
): Promise<UseItemResponse> {
  return request<UseItemResponse>(
    "POST",
    `/inventory/${characterId}/use`,
    { inventory_item_id: inventoryItemId },
    token,
  );
}

export { ApiError };
