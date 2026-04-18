import Phaser from "phaser";

interface DamageNumber {
  text: Phaser.GameObjects.Text;
  vy: number;
  life: number;
  isHeal: boolean;
}

export class DamageNumberLayer {
  private scene: Phaser.Scene;
  private damageNumbers: DamageNumber[] = [];

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  show(
    worldX: number,
    worldY: number,
    amount: number,
    type: "damage" | "heal" | "crit" | "miss",
  ): void {
    const color = type === "miss" ? "#888888" : type === "heal" ? "#44FF44" : type === "crit" ? "#FFD700" : "#FF4444";
    const size = type === "crit" ? 28 : type === "miss" ? 14 : 20;
    const prefix = type === "heal" ? "+" : type === "miss" ? "MISS" : "";

    const text = this.scene.add.text(worldX, worldY, `${prefix}${amount}`, {
      fontFamily: "'Press Start 2P', monospace",
      fontSize: `${size}px`,
      color,
      stroke: "#000000",
      strokeThickness: 2,
    });
    text.setOrigin(0.5);
    text.setDepth(100);

    this.damageNumbers.push({
      text,
      vy: type === "miss" ? 0 : -32,
      life: type === "miss" ? 600 : 800,
      isHeal: type === "heal",
    });

    if (type === "crit") {
      text.setScale(1.2);
      this.scene.tweens.add({
        targets: text,
        scaleX: 1.4,
        scaleY: 1.4,
        duration: 200,
        yoyo: true,
      });
    }
  }

  update(delta: number): void {
    const dt = delta / 1000;
    for (let i = this.damageNumbers.length - 1; i >= 0; i--) {
      const dn = this.damageNumbers[i];
      dn.life -= delta;
      dn.text.y += dn.vy * dt;
      dn.text.alpha = Math.min(1, dn.life / 200);

      if (dn.life <= 0) {
        dn.text.destroy();
        this.damageNumbers.splice(i, 1);
      }
    }
  }

  destroy(): void {
    for (const dn of this.damageNumbers) {
      dn.text.destroy();
    }
    this.damageNumbers = [];
  }
}