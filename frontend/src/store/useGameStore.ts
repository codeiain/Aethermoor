/**
 * Global Zustand store for AETHERMOOR.
 *
 * Screens are managed as a discriminated string — no URL router needed for a game.
 * Auth token is stored in memory only (not localStorage) for security.
 */
import { create } from "zustand";
import type { PartyInfo, PartyInvite } from "../api/client";

export type Screen =
  | "loading"
  | "login"
  | "character-select"
  | "character-create"
  | "game";

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
}

export interface ActiveCharacter extends CharacterSummary {
  zone_id: string;
  x: number;
  y: number;
}

export interface ZoneSummary {
  id: string;
  name: string;
  biome: string;
  level_min: number;
  level_max: number;
  width: number;
  height: number;
  spawn_x: number;
  spawn_y: number;
}

export interface CombatState {
  combatId: string;
  npcId: string;
}

export type ChatChannel = "global" | "zone" | "party" | "guild" | "whisper";

export interface ChatMessage {
  id: string;
  channel: ChatChannel;
  sender: string;
  senderName: string;
  message: string;
  timestamp: number;
}

export type NotificationType = "quest_update" | "party_invite" | "trade_request" | "guild_event" | "system" | "whisper";

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  body: string;
  timestamp: number;
  read: boolean;
  actionUrl?: string;
}

interface GameState {
  // Navigation
  screen: Screen;

  // Auth
  token: string | null;
  userId: string | null;
  username: string | null;

  // Characters
  characters: CharacterSummary[];
  activeCharacter: ActiveCharacter | null;

  // World
  currentZone: ZoneSummary | null;

  // Combat
  combat: CombatState | null;

  // Chat
  chatMessages: ChatMessage[];
  chatChannel: ChatChannel;
  chatExpanded: boolean;

  // Notifications
  notifications: Notification[];
  unreadCount: number;

  // Party
  party: PartyInfo | null;
  pendingPartyInvites: PartyInvite[];

  // Actions
  setScreen: (screen: Screen) => void;
  login: (token: string, userId: string, username: string) => void;
  logout: () => void;
  setCharacters: (chars: CharacterSummary[]) => void;
  setActiveCharacter: (char: ActiveCharacter) => void;
  setCurrentZone: (zone: ZoneSummary) => void;
  updatePosition: (x: number, y: number) => void;
  setCombat: (combat: CombatState | null) => void;
  clearCombat: () => void;
  addChatMessage: (msg: ChatMessage) => void;
  setChatChannel: (channel: ChatChannel) => void;
  setChatExpanded: (expanded: boolean) => void;
  addNotification: (notif: Notification) => void;
  dismissNotification: (id: string) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;
  setParty: (party: PartyInfo | null) => void;
  addPendingPartyInvite: (invite: PartyInvite) => void;
  removePendingPartyInvite: (inviteId: string) => void;
}

export const useGameStore = create<GameState>()((set) => ({
  screen: "loading",
  token: null,
  userId: null,
  username: null,
  characters: [],
  activeCharacter: null,
  currentZone: null,
  combat: null,
  chatMessages: [],
  chatChannel: "zone",
  chatExpanded: true,
  party: null,
  pendingPartyInvites: [],
  notifications: [],
  unreadCount: 0,

  setScreen: (screen) => set({ screen }),

  login: (token, userId, username) =>
    set({ token, userId, username, screen: "character-select" }),

  logout: () =>
    set({
      token: null,
      userId: null,
      username: null,
      characters: [],
      activeCharacter: null,
      currentZone: null,
      combat: null,
      chatMessages: [],
      notifications: [],
      unreadCount: 0,
      screen: "login",
    }),

  setCharacters: (characters) => set({ characters }),

  setActiveCharacter: (char) => set({ activeCharacter: char }),

  setCurrentZone: (zone) => set({ currentZone: zone }),

  updatePosition: (x, y) =>
    set((state) =>
      state.activeCharacter
        ? { activeCharacter: { ...state.activeCharacter, x, y } }
        : {}
    ),

  setCombat: (combat) => set({ combat }),

  clearCombat: () => set({ combat: null }),

  addChatMessage: (msg) =>
    set((state) => ({
      chatMessages: [...state.chatMessages.slice(-99), msg],
    })),

  setChatChannel: (channel) => set({ chatChannel: channel }),

  setChatExpanded: (expanded) => set({ chatExpanded: expanded }),

  addNotification: (notif) =>
    set((state) => ({
      notifications: [notif, ...state.notifications].slice(0, 20),
      unreadCount: state.unreadCount + 1,
    })),

  dismissNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),

  markNotificationRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),

  clearNotifications: () => set({ notifications: [], unreadCount: 0 }),

  setParty: (party) => set({ party }),

  addPendingPartyInvite: (invite) =>
    set((state) => ({
      pendingPartyInvites: [...state.pendingPartyInvites.filter((i) => i.invite_id !== invite.invite_id), invite],
    })),

  removePendingPartyInvite: (inviteId) =>
    set((state) => ({
      pendingPartyInvites: state.pendingPartyInvites.filter((i) => i.invite_id !== inviteId),
    })),
}));
