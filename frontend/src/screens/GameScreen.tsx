import { useEffect, useRef, useState } from "react";
import { useGameStore } from "../store/useGameStore";
import { getZone, getTutorialState, listZones, ApiError } from "../api/client";
import { createGame } from "../game/AethermoorGame";
import HUD from "../components/HUD";
import Joystick from "../components/Joystick";
import CombatOverlay from "../components/CombatOverlay";
import Chat from "../components/Chat";
import NotificationToast from "../components/NotificationToast";
import TutorialOverlay from "../components/TutorialOverlay";
import { useChatWebSocket } from "../hooks/useChatWebSocket";
import type Phaser from "phaser";

/**
 * GameScreen — mounts the Phaser canvas + React overlays (HUD, Joystick).
 *
 * Lifecycle:
 * 1. On mount: load zone data for the active character's zone_id.
 *    If the zone list is needed first (to resolve zone_id → full data),
 *    we call getZone() directly by ID.
 * 2. Push zone + tilemap into Phaser scene.registry before starting scenes.
 * 3. Create the Phaser.Game instance inside the container div.
 * 4. On unmount: destroy the Phaser.Game instance cleanly.
 *
 * The HUD reads from Zustand (reactive). The Joystick writes into
 * Phaser scene.registry (imperative). Both coexist safely.
 *
 * Touch detection: show Joystick only when the primary pointer is coarse
 * (touchscreen). On desktop only keyboard input is shown.
 */
export default function GameScreen() {
  const token = useGameStore((s) => s.token)!;
  const activeCharacter = useGameStore((s) => s.activeCharacter);
  const setCurrentZone = useGameStore((s) => s.setCurrentZone);
  const setScreen = useGameStore((s) => s.setScreen);
  const combat = useGameStore((s) => s.combat);
  const clearCombat = useGameStore((s) => s.clearCombat);

  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<Phaser.Game | null>(null);
  const [game, setGame] = useState<Phaser.Game | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [gameReady, setGameReady] = useState(false);
  const [showTutorial, setShowTutorial] = useState(false);

  // Detect touch device for joystick visibility
  const [isTouch] = useState(
    () => window.matchMedia("(pointer: coarse)").matches
  );

  const wsProto = typeof window !== "undefined" && window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsHost = import.meta.env.DEV
    ? `${wsProto}//localhost:8010`
    : typeof window !== "undefined" ? `${wsProto}//${window.location.host.replace(":3000", ":8010")}` : "";
  const wsConfig = token && activeCharacter ? {
    wsUrl: wsHost,
    token,
    characterId: activeCharacter.id,
    characterName: activeCharacter.name,
    characterLevel: activeCharacter.level,
  } : null;

  const { sendChat } = useChatWebSocket({ config: wsConfig, enabled: !!wsConfig });
  // Expose sendChat to global for testing
  if (typeof window !== "undefined") {
    (window as unknown as { sendChat: typeof sendChat }).sendChat = sendChat;
  }

  useEffect(() => {
    if (!activeCharacter) {
      setScreen("character-select");
      return;
    }

    let destroyed = false;

    async function initGame() {
      try {
        const zoneId = activeCharacter!.zone_id || "starter_town";

        // Load zone — try direct lookup, fall back to list scan
        let zone;
        try {
          zone = await getZone(token, zoneId);
        } catch {
          // Zone not found by direct ID — scan list for starter zone
          const zones = await listZones(token);
          zone = zones[0];
          if (!zone) throw new Error("No zones available");
        }

        if (destroyed) return;

        setCurrentZone(zone);

        if (!containerRef.current) return;

        // Create Phaser game — registry must be set before PreloadScene
        // calls scene.start("WorldScene") so WorldScene.create() can read it.
        const phaserGame = createGame(containerRef.current);
        gameRef.current = phaserGame;

        // Wait one tick for Phaser boot then set registry data
        // so WorldScene.create() can access zone + tilemap.
        phaserGame.events.once("ready", () => {
          // Tilemap is embedded in zone.tilemap (world service returns it
          // in the zone detail response). Push into registry for WorldScene.
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          const zoneWithMap = zone as any;
          if (zoneWithMap.tilemap) {
            phaserGame.registry.set("tilemap", zoneWithMap.tilemap);
          }
          // Also push zone into registry for resilience (WorldScene reads store)
          phaserGame.registry.set("zone", zone);

          // Presence WebSocket config — WorldScene creates PresenceManager from this
          const char = activeCharacter!;
          const wsProto = window.location.protocol === "https:" ? "wss:" : "ws:";
          const wsHost = import.meta.env.DEV
            ? `${wsProto}//localhost:8010`
            : `${wsProto}//${window.location.host.replace(":3000", ":8010")}`;
          phaserGame.registry.set("presenceConfig", {
            wsUrl: wsHost,
            token,
            characterId: char.id,
            name: char.name,
            level: char.level,
          });
        });

        if (!destroyed) {
          setGame(phaserGame);
          setLoading(false);
          setGameReady(true);

          // Check if tutorial should show (tutorial_step === null means not started)
          if (activeCharacter) {
            getTutorialState(token, activeCharacter.id)
              .then((state) => {
                if (!destroyed && state.tutorial_step === null) {
                  setShowTutorial(true);
                }
              })
              .catch(() => {/* non-blocking */});
          }
        }
      } catch (err) {
        if (!destroyed) {
          setError(err instanceof ApiError ? err.message : "Failed to load game world");
          setLoading(false);
        }
      }
    }

    initGame();

    return () => {
      destroyed = true;
      if (gameRef.current) {
        gameRef.current.destroy(true);
        gameRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (error) {
    return (
      <div style={S.errorWrap}>
        <div style={S.errorText}>{error}</div>
        <button style={S.errorBtn} onClick={() => setScreen("character-select")}>
          BACK TO HEROES
        </button>
      </div>
    );
  }

  return (
    <div style={S.wrap}>
      {loading && (
        <div style={S.loadingOverlay}>
          <div style={S.loadingText}>ENTERING WORLD...</div>
        </div>
      )}

      {/* Phaser canvas mounts here */}
      <div ref={containerRef} style={S.canvas} />

      {/* React overlays — rendered after game is ready */}
      {!loading && game && (
        <>
          <HUD />
          {gameReady && <Chat sendChat={sendChat} />}
          {gameReady && <NotificationToast />}
          {isTouch && <Joystick game={game} />}
          {combat && (
            <CombatOverlay
              combatId={combat.combatId}
              game={game}
              onEnd={(result) => {
                console.log("Combat ended:", result);
                clearCombat();
              }}
            />
          )}
          {showTutorial && (
            <TutorialOverlay onDone={() => setShowTutorial(false)} />
          )}
        </>
      )}
    </div>
  );
}

const S = {
  wrap: {
    position: "relative" as const,
    width: "100%",
    height: "100%",
    background: "#0d0d2b",
    overflow: "hidden" as const,
  },
  canvas: {
    position: "absolute" as const,
    inset: 0,
    width: "100%",
    height: "100%",
  },
  loadingOverlay: {
    position: "absolute" as const,
    inset: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#0d0d2b",
    zIndex: 50,
  },
  loadingText: {
    fontFamily: "'Press Start 2P', monospace",
    fontSize: 10,
    color: "#c8a84b",
  },
  errorWrap: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    height: "100%",
    background: "#0d0d2b",
    gap: 20,
    padding: 24,
    fontFamily: "'Press Start 2P', monospace",
  },
  errorText: {
    fontSize: 9,
    color: "#dd5555",
    textAlign: "center" as const,
    maxWidth: 300,
    lineHeight: 1.8,
  },
  errorBtn: {
    background: "#1a2233",
    border: "2px solid #2a3a4a",
    color: "#8899aa",
    fontSize: 8,
    fontFamily: "inherit",
    padding: "12px 20px",
    cursor: "pointer" as const,
    borderRadius: 2,
  },
};
