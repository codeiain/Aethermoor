import Phaser from "phaser";

/**
 * PreloadScene — creates synthetic tile textures for the prototype.
 *
 * We have no tileset PNG at this stage, so we generate small textures
 * programmatically using Phaser Graphics + generateTexture. This is sufficient
 * for a playable prototype; real art assets replace these textures in a later
 * sprint once the art pipeline is established.
 *
 * Textures created:
 *   "tile_grass"   32×32  — walkable ground (biome-tinted green)
 *   "tile_wall"    32×32  — collision tile (stone brown)
 *   "tile_town"    32×32  — town floor (cobblestone grey)
 *   "player"       28×28  — player character placeholder
 *   "npc_dot"      10×10  — NPC stub dot
 */
export class PreloadScene extends Phaser.Scene {
  constructor() {
    super({ key: "PreloadScene" });
  }

  create(): void {
    this._makeTile("tile_grass", 0x4a7c3f, 0x3d6632, 0x2d4d26);
    this._makeTile("tile_wall", 0x7d6b4f, 0x5c4d3a, 0x3d3226);
    this._makeTile("tile_town", 0x5a5550, 0x3d3a38, 0x2a2827);
    this._makePlayer();
    this._makeNpcDot();

    this.scene.start("WorldScene");
  }

  private _makeTile(key: string, fill: number, border: number, shadow: number): void {
    const SIZE = 32;
    const g = this.add.graphics();

    // Main fill
    g.fillStyle(fill);
    g.fillRect(0, 0, SIZE, SIZE);

    // Subtle top-left highlight
    g.fillStyle(0xffffff, 0.06);
    g.fillRect(0, 0, SIZE, 2);
    g.fillRect(0, 0, 2, SIZE);

    // Bottom-right shadow
    g.fillStyle(shadow, 0.5);
    g.fillRect(0, SIZE - 2, SIZE, 2);
    g.fillRect(SIZE - 2, 0, 2, SIZE);

    // Grid line border
    g.lineStyle(1, border, 0.35);
    g.strokeRect(0.5, 0.5, SIZE - 1, SIZE - 1);

    g.generateTexture(key, SIZE, SIZE);
    g.destroy();
  }

  private _makePlayer(): void {
    const SIZE = 28;
    const g = this.add.graphics();

    // Body
    g.fillStyle(0x4488ee);
    g.fillRoundedRect(4, 8, 20, 20, 3);

    // Head
    g.fillStyle(0xddbb88);
    g.fillCircle(14, 7, 6);

    // Outline
    g.lineStyle(2, 0x2266bb);
    g.strokeRoundedRect(4, 8, 20, 20, 3);
    g.lineStyle(2, 0xbb9966);
    g.strokeCircle(14, 7, 6);

    // Direction dot (facing indicator — top of body)
    g.fillStyle(0xffffff, 0.8);
    g.fillCircle(14, 12, 2);

    g.generateTexture("player", SIZE, SIZE);
    g.destroy();
  }

  private _makeNpcDot(): void {
    const g = this.add.graphics();
    g.fillStyle(0xdd8844);
    g.fillCircle(5, 5, 4);
    g.lineStyle(1, 0xaa5522);
    g.strokeCircle(5, 5, 4);
    g.generateTexture("npc_dot", 10, 10);
    g.destroy();
  }
}
