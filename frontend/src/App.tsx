import { useEffect } from "react";
import { useGameStore } from "./store/useGameStore";
import LoginScreen from "./screens/LoginScreen";
import CharacterSelectScreen from "./screens/CharacterSelectScreen";
import CharacterCreateScreen from "./screens/CharacterCreateScreen";
import GameScreen from "./screens/GameScreen";

/**
 * App — root component and screen router for AETHERMOOR.
 *
 * Screen transitions are driven by Zustand store state — no URL router.
 * This keeps the game SPA simple and avoids back-button issues on mobile.
 *
 * Screen flow:
 *   loading → login → character-select → character-create → game
 *                                      ↑___________________________↓
 *
 * The "loading" screen resolves immediately on mount (no persisted session —
 * token is memory-only for security). It transitions to "login" so the
 * initial render never shows a blank frame.
 */
export default function App() {
  const screen = useGameStore((s) => s.screen);
  const setScreen = useGameStore((s) => s.setScreen);

  // Resolve loading state immediately — no persisted auth token
  useEffect(() => {
    if (screen === "loading") {
      setScreen("login");
    }
  }, [screen, setScreen]);

  return (
    <div style={S.root}>
      {screen === "loading" && <LoadingScreen />}
      {screen === "login" && <LoginScreen />}
      {screen === "character-select" && <CharacterSelectScreen />}
      {screen === "character-create" && <CharacterCreateScreen />}
      {screen === "game" && <GameScreen />}
    </div>
  );
}

function LoadingScreen() {
  return (
    <div style={S.loading}>
      <div style={S.loadingText}>AETHERMOOR</div>
    </div>
  );
}

const S = {
  root: {
    width: "100%",
    height: "100%",
    fontFamily: "'Press Start 2P', monospace",
    WebkitFontSmoothing: "none" as const,
    MozOsxFontSmoothing: "grayscale" as const,
    imageRendering: "pixelated" as const,
  },
  loading: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    height: "100%",
    background: "#0d0d2b",
  },
  loadingText: {
    fontSize: 18,
    color: "#c8a84b",
    textShadow: "0 0 12px #c8a84b88",
  },
};
