import { useState, useEffect, useCallback } from "react";
import { useGameStore } from "../store/useGameStore";
import {
  CombatState,
  getCombat,
  submitCombatAction,
} from "../api/client";
import ActionBar from "./ActionBar";
import TurnOrder from "./TurnOrder";
import CombatLog from "./CombatLog";
import TargetInfo from "./TargetInfo";
import PlayerStatus from "./PlayerStatus";
import type Phaser from "phaser";

interface Props {
  combatId: string;
  game: Phaser.Game;
  onEnd: (result: "victory" | "defeat" | "fled") => void;
}

export default function CombatOverlay({ combatId, game, onEnd }: Props) {
  const token = useGameStore((s) => s.token)!;
  const [combatState, setCombatState] = useState<CombatState | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null);
  const [actioning, setActioning] = useState(false);
  const [combatLog, setCombatLog] = useState<string[]>([]);

  const fetchCombat = useCallback(async () => {
    try {
      const state = await getCombat(token, combatId);
      setCombatState(state);
      setCombatLog(state.combat_log);
      if (state.status !== "active") {
        onEnd(state.status);
      }
    } catch (err) {
      console.error("Failed to fetch combat state:", err);
    } finally {
      setLoading(false);
    }
  }, [token, combatId, onEnd]);

  useEffect(() => {
    fetchCombat();
    const interval = setInterval(fetchCombat, 2000);
    return () => clearInterval(interval);
  }, [fetchCombat]);

  const handleAction = async (
    actionType: "attack" | "spell" | "item" | "flee",
    targetId?: string,
  ) => {
    if (actioning || !combatState) return;
    setActioning(true);
    try {
      const result = await submitCombatAction(token, combatId, {
        action_type: actionType,
        target_id: targetId,
      });

      const showDamage = (game.registry.get("showDamageNumber") as ((x: number, y: number, amount: number, type: "damage" | "heal" | "crit" | "miss") => void) | undefined);
      if (showDamage) {
        const playerX = 160;
        const playerY = 120;
        const enemyX = 480;
        const enemyY = 120;

        if (result.roll_result) {
          if (result.roll_result.is_crit) {
            showDamage(enemyX, enemyY, result.roll_result.total, "crit");
          } else if (result.roll_result.is_miss) {
            showDamage(enemyX, enemyY, 0, "miss");
          } else if (result.damage) {
            showDamage(enemyX, enemyY, result.damage, "damage");
          }
        }

        if (result.npc_action && result.updated_state.player) {
          showDamage(playerX, playerY, 5, "damage");
        }
      }

      setCombatState(result.updated_state);
      setCombatLog(result.combat_log);
      if (result.updated_state.status !== "active") {
        onEnd(result.updated_state.status);
      }
    } catch (err) {
      console.error("Action failed:", err);
    } finally {
      setActioning(false);
    }
  };

  if (loading || !combatState) {
    return (
      <div style={S.overlay}>
        <div style={S.loading}>LOADING COMBAT...</div>
      </div>
    );
  }

  const currentActor = combatState.turn_order[combatState.current_turn_index];
  const isPlayerTurn = currentActor?.is_player;

  return (
    <div style={S.overlay}>
      <div style={S.background} />
      
      <TurnOrder
        turnOrder={combatState.turn_order}
        currentIndex={combatState.current_turn_index}
        onSelect={setSelectedTarget}
      />

      <CombatLog entries={combatLog} />

      <TargetInfo
        targetId={selectedTarget}
        enemies={combatState.enemies}
        onClose={() => setSelectedTarget(null)}
      />

      <PlayerStatus player={combatState.player} />

      <ActionBar
        disabled={!isPlayerTurn || actioning}
        onAction={handleAction}
        canFlee={isPlayerTurn}
      />
    </div>
  );
}

const S = {
  overlay: {
    position: "absolute" as const,
    inset: 0,
    zIndex: 1000,
    display: "flex",
    flexDirection: "column" as const,
    fontFamily: "'Press Start 2P', monospace",
  },
  background: {
    position: "absolute" as const,
    inset: 0,
    background: "rgba(0,0,0,0.75)",
  },
  loading: {
    position: "absolute" as const,
    inset: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#c8a84b",
    fontSize: 10,
  },
};