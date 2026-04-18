import { useEffect, useRef } from "react";
import nipplejs from "nipplejs";
import Phaser from "phaser";
import type { JoystickManager } from "nipplejs";

interface JoystickProps {
  game: Phaser.Game;
}

export default function Joystick({ game }: JoystickProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const managerRef = useRef<JoystickManager | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    managerRef.current = nipplejs.create({
      zone: el,
      mode: "static",
      position: { left: "50%", top: "50%" },
      size: 90,
      color: "rgba(255,255,255,0.18)",
      restJoystick: true,
    });

    const manager = managerRef.current;
    if (!manager) return;

    manager.on("move", (_evt: unknown, data: unknown) => {
      const d = data as { vector?: { x: number; y: number } };
      if (!d.vector) return;
      const vx = d.vector.x;
      const vy = -d.vector.y;
      game.scene.scenes.forEach((scene) => {
        scene.registry.set("joystick", { vx, vy });
      });
    });

    manager.on("end", () => {
      game.scene.scenes.forEach((scene) => {
        scene.registry.set("joystick", { vx: 0, vy: 0 });
      });
    });

    return () => {
      manager.destroy();
      managerRef.current = null;
    };
  }, [game]);

  return (
    <div
      ref={containerRef}
      style={S.zone}
      aria-hidden="true"
    />
  );
}

const S = {
  zone: {
    position: "absolute" as const,
    bottom: "calc(env(safe-area-inset-bottom, 0px) + 16px)",
    left: 16,
    width: 120,
    height: 120,
    zIndex: 30,
    borderRadius: "50%",
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.08)",
    touchAction: "none" as const,
  },
};