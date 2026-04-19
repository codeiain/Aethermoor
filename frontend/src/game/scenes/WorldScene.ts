import Phaser from "phaser";
import { useGameStore } from "../../store/useGameStore";
import { PresenceManager } from "../PresenceManager";
import { startCombat, getNpcDialogue } from "../../api/client";
import { DamageNumberLayer } from "../DamageNumberLayer";


const TILE_SIZE = 32;
const MOVE_SPEED = 140; // px/s
// Camera padding as half the viewport size
const CAMERA_PADDING_X = 0.5; // in viewport units (half viewport width)
const CAMERA_PADDING_Y = 0.5; // in viewport units (half viewport height)

/** Shape of the tilemap data returned by the world service. */
interface TilemapLayer {
  name: string;
  type: string;
  data: number[];
  width: number;
  height: number;
}

interface TilemapData {
  width: number;
  height: number;
  layers: TilemapLayer[];
}

/**
 * WorldScene — main game world renderer.
 *
 * Receives zone + character data via scene.registry (set before launch).
 * Renders tiles as individual sprites for simplicity (prototype approach).
 * Player sprite follows keyboard/joystick input; camera follows player.
 *
 * Multiplayer presence is handled by PresenceManager which owns the WebSocket
 * connection and manages remote player sprites. The scene calls sendMove()
 * whenever the local player tile position changes.
 */
export class WorldScene extends Phaser.Scene {
  private player!: Phaser.GameObjects.Sprite;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private wasd!: {
    up: Phaser.Input.Keyboard.Key;
    left: Phaser.Input.Keyboard.Key;
    down: Phaser.Input.Keyboard.Key;
    right: Phaser.Input.Keyboard.Key;
  };
  private collisionMap: boolean[] = [];
  private mapWidth = 0;
  private mapHeight = 0;

  // Logical position tracking (world coordinates)
  private playerWorldX = 0;
  private playerWorldY = 0;
  private playerTileX = 0;
  private playerTileY = 0;

  // Joystick velocity — populated by nipplejs via registry
  private joystickVx = 0;
  private joystickVy = 0;

  private presence: PresenceManager | null = null;
  private lastTileX = -1;
  private lastTileY = -1;

  // NPC interaction
  private npcSprites: Phaser.GameObjects.Image[] = [];
  private npcIds: Map<Phaser.GameObjects.Image, string> = new Map();

  // Damage number overlay
  private damageNumberLayer: DamageNumberLayer | null = null;

  constructor() {
    super({ key: "WorldScene" });
  }

  create(): void {
    const store = useGameStore.getState();
    const zone = store.currentZone;
    const char = store.activeCharacter;

    if (!zone) {
      console.error("WorldScene: no zone in store — returning to login");
      store.setScreen("login");
      return;
    }

    const tilemap = this.registry.get("tilemap") as TilemapData | undefined;
    this.mapWidth = zone.width;
    this.mapHeight = zone.height;

    this._renderTiles(tilemap, zone.width, zone.height, zone.biome);
    this._buildCollisionMap(tilemap, zone.width, zone.height);

    // Calculate viewport center
    const centerX = this.scale.width / 2;
    const centerY = this.scale.height / 2;

    // Initialize logical world position from spawn
    this.playerWorldX = (char?.x ?? zone.spawn_x) * TILE_SIZE + TILE_SIZE / 2;
    this.playerWorldY = (char?.y ?? zone.spawn_y) * TILE_SIZE + TILE_SIZE / 2;
    this.playerTileX = Math.floor(this.playerWorldX / TILE_SIZE);
    this.playerTileY = Math.floor(this.playerWorldY / TILE_SIZE);

    // Position player sprite at viewport center (fixed)
    this.player = this.add.sprite(centerX, centerY, "player");
    this.player.setDepth(10);
    this.player.setScrollFactor(0); // CRITICAL: Sprite doesn't scroll with camera

    this.lastTileX = this.playerTileX;
    this.lastTileY = this.playerTileY;

    // Camera setup with padding to allow reaching edge tiles
    const paddingX = this.scale.width * CAMERA_PADDING_X;
    const paddingY = this.scale.height * CAMERA_PADDING_Y;
    this.cameras.main.setBounds(
      -paddingX,
      -paddingY,
      zone.width * TILE_SIZE + paddingX * 2,
      zone.height * TILE_SIZE + paddingY * 2
    );
    this.cameras.main.setViewport(0, 0, this.scale.width, this.scale.height);
    
    // Position camera at player's world position with bounds clamping
    const minScrollX = 0;
    const maxScrollX = Math.max(0, zone.width * TILE_SIZE + paddingX - this.scale.width);
    const minScrollY = 0;
    const maxScrollY = Math.max(0, zone.height * TILE_SIZE + paddingY - this.scale.height);
    
    // Center map if smaller than viewport
    let scrollX = this.playerWorldX - centerX;
    let scrollY = this.playerWorldY - centerY;
    
    if (zone.width * TILE_SIZE < this.scale.width) {
      scrollX = -(this.scale.width - zone.width * TILE_SIZE) / 2;
    } else {
      scrollX = Phaser.Math.Clamp(scrollX, minScrollX, maxScrollX);
    }
    
    if (zone.height * TILE_SIZE < this.scale.height) {
      scrollY = -(this.scale.height - zone.height * TILE_SIZE) / 2;
    } else {
      scrollY = Phaser.Math.Clamp(scrollY, minScrollY, maxScrollY);
    }
    
    this.cameras.main.scrollX = scrollX;
    this.cameras.main.scrollY = scrollY;

    // Stub NPC dots
    if (tilemap) {
      this._spawnNpcDots(tilemap, zone.width, zone.height);
    }

    // Input
    this.cursors = this.input.keyboard!.createCursorKeys();
    this.wasd = {
      up: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.W),
      left: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.A),
      down: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      right: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.D),
    };

    // Listen for joystick events from nipplejs (set via registry)
    this.registry.events.on("changedata-joystick", (_: unknown, data: { vx: number; vy: number }) => {
      this.joystickVx = data.vx;
      this.joystickVy = data.vy;
    });

    // Zone name flash
    const zoneName = this.add.text(
      this.scale.width / 2,
      this.scale.height / 2 - 40,
      zone.name.toUpperCase(),
      { fontSize: "8px", fontFamily: "'Press Start 2P'", color: "#e8e0d0" },
    );
    zoneName.setScrollFactor(0);
    zoneName.setDepth(100);
    zoneName.setOrigin(0.5);
    this.tweens.add({
      targets: zoneName,
      alpha: 0,
      delay: 2000,
      duration: 1000,
      onComplete: () => zoneName.destroy(),
    });

    // Multiplayer presence
    const presenceConfig = this.registry.get("presenceConfig") as {
      wsUrl: string;
      token: string;
      characterId: string;
      name: string;
      level: number;
    } | undefined;

    if (presenceConfig) {
      this.presence = new PresenceManager({
        scene: this,
        zoneId: zone.id,
        wsUrl: presenceConfig.wsUrl,
        token: presenceConfig.token,
        characterId: presenceConfig.characterId,
        name: presenceConfig.name,
        level: presenceConfig.level,
      });
      this.presence.connect();
    }

    // Damage number layer for combat
    this.damageNumberLayer = new DamageNumberLayer(this);
    this.registry.set("damageNumbers", this.damageNumberLayer);
    this.registry.set("showDamageNumber", (x: number, y: number, amount: number, type: "damage" | "heal" | "crit" | "miss") => {
      this.damageNumberLayer?.show(x, y, amount, type);
    });

    // Clean up presence on scene shutdown
    this.events.on(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.presence?.destroy();
      this.presence = null;
      this.damageNumberLayer?.destroy();
      this.damageNumberLayer = null;
    });
  }

  update(_time: number, delta: number): void {
    const dt = delta / 1000;
    let vx = 0;
    let vy = 0;

    // Keyboard
    if (this.cursors.left.isDown || this.wasd.left.isDown) vx -= MOVE_SPEED;
    if (this.cursors.right.isDown || this.wasd.right.isDown) vx += MOVE_SPEED;
    if (this.cursors.up.isDown || this.wasd.up.isDown) vy -= MOVE_SPEED;
    if (this.cursors.down.isDown || this.wasd.down.isDown) vy += MOVE_SPEED;

    // Joystick (normalised -1 to 1 → scale by speed)
    if (vx === 0 && vy === 0) {
      vx = this.joystickVx * MOVE_SPEED;
      vy = this.joystickVy * MOVE_SPEED;
    }

    if (vx !== 0 && vy !== 0) {
      const factor = 1 / Math.SQRT2;
      vx *= factor;
      vy *= factor;
    }

    // Calculate new world position (not sprite position)
    const nx = this.playerWorldX + vx * dt;
    const ny = this.playerWorldY + vy * dt;

    const tileX = Math.floor(nx / TILE_SIZE);
    const tileY = Math.floor(ny / TILE_SIZE);

    if (!this._isBlocked(tileX, tileY)) {
      // Update logical world position
      this.playerWorldX = Phaser.Math.Clamp(
        nx,
        TILE_SIZE / 2,
        this.mapWidth * TILE_SIZE - TILE_SIZE / 2
      );
      this.playerWorldY = Phaser.Math.Clamp(
        ny,
        TILE_SIZE / 2,
        this.mapHeight * TILE_SIZE - TILE_SIZE / 2
      );

      this.playerTileX = Math.floor(this.playerWorldX / TILE_SIZE);
      this.playerTileY = Math.floor(this.playerWorldY / TILE_SIZE);
    }

    // Update camera position (always, not just when moving)
    const centerX = this.scale.width / 2;
    const centerY = this.scale.height / 2;
    
    // Padding to allow reaching edge tiles
    const paddingX = this.scale.width * CAMERA_PADDING_X;
    const paddingY = this.scale.height * CAMERA_PADDING_Y;

    // Check if map is smaller than viewport on each axis
    const isSmallMapX = this.mapWidth * TILE_SIZE < this.scale.width;
    const isSmallMapY = this.mapHeight * TILE_SIZE < this.scale.height;

    let scrollX: number;
    let scrollY: number;

    if (isSmallMapX) {
      // Map smaller than viewport on X - center it
      scrollX = -(this.scale.width - this.mapWidth * TILE_SIZE) / 2;
    } else {
      // Map larger than viewport on X - follow player with clamping (with padding)
      const minScrollX = -paddingX;
      const maxScrollX = this.mapWidth * TILE_SIZE + paddingX - this.scale.width;
      scrollX = Phaser.Math.Clamp(this.playerWorldX - centerX, minScrollX, maxScrollX);
    }

    if (isSmallMapY) {
      // Map smaller than viewport on Y - center it
      scrollY = -(this.scale.height - this.mapHeight * TILE_SIZE) / 2;
    } else {
      // Map larger than viewport on Y - follow player with clamping (with padding)
      const minScrollY = -paddingY;
      const maxScrollY = this.mapHeight * TILE_SIZE + paddingY - this.scale.height;
      scrollY = Phaser.Math.Clamp(this.playerWorldY - centerY, minScrollY, maxScrollY);
    }

    this.cameras.main.scrollX = scrollX;
    this.cameras.main.scrollY = scrollY;
    
    // Update player sprite position
    // For large maps: player stays centered on screen
    // For small maps: player moves around on screen based on world position
    if (isSmallMapX && isSmallMapY) {
      // Small map - player sprite moves with world position relative to camera
      this.player.x = this.playerWorldX - scrollX;
      this.player.y = this.playerWorldY - scrollY;
    } else if (isSmallMapX) {
      // Small width, large height - player moves horizontally, centered vertically
      this.player.x = this.playerWorldX - scrollX;
      this.player.y = centerY;
    } else if (isSmallMapY) {
      // Large width, small height - player centered horizontally, moves vertically
      this.player.x = centerX;
      this.player.y = this.playerWorldY - scrollY;
    } else {
      // Large map - player stays centered
      this.player.x = centerX;
      this.player.y = centerY;
    }

    // Push position to store + presence on tile change
    if (this.playerTileX !== this.lastTileX || this.playerTileY !== this.lastTileY) {
      this.lastTileX = this.playerTileX;
      this.lastTileY = this.playerTileY;

      const state = useGameStore.getState();
      if (state.activeCharacter) {
        useGameStore.getState().updatePosition(this.playerTileX, this.playerTileY);
      }

      // Broadcast position to other players via WebSocket
      this.presence?.sendMove(this.playerTileX, this.playerTileY);
    }

    // Update damage number animations
    this.damageNumberLayer?.update(delta);
  }

  private _renderTiles(
    tilemap: TilemapData | undefined,
    width: number,
    height: number,
    biome: string,
  ): void {
    const groundTile = biome === "town" ? "tile_town" : "tile_grass";
    const collisionLayer = tilemap?.layers.find((l) => l.name === "Collision");
    const collData = collisionLayer?.data ?? [];

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = y * width + x;
        const blocked = collData[idx] !== undefined ? collData[idx] !== 0 : false;
        const key = blocked ? "tile_wall" : groundTile;
        this.add.image(x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + TILE_SIZE / 2, key);
      }
    }
  }

  private _buildCollisionMap(
    tilemap: TilemapData | undefined,
    width: number,
    height: number,
  ): void {
    const collisionLayer = tilemap?.layers.find((l) => l.name === "Collision");
    const collData = collisionLayer?.data ?? [];
    this.collisionMap = Array.from({ length: width * height }, (_, i) =>
      collData[i] !== undefined ? collData[i] !== 0 : false,
    );
  }

  private _isBlocked(tileX: number, tileY: number): boolean {
    if (tileX < 0 || tileY < 0 || tileX >= this.mapWidth || tileY >= this.mapHeight) {
      return true;
    }
    return this.collisionMap[tileY * this.mapWidth + tileX] === true;
  }

  private _spawnNpcDots(tilemap: TilemapData, width: number, _height: number): void {
    // Spawn a few static NPC stub dots on walkable tiles in the centre area
    const collisionLayer = tilemap.layers.find((l) => l.name === "Collision");
    const collData = collisionLayer?.data ?? [];
    let spawned = 0;
    const target = 5;
    const midX = Math.floor(width / 2);
    const offsets = [
      [2, 0], [-2, 0], [0, 2], [0, -2], [3, 3],
    ];
    for (const [ox, oy] of offsets) {
      if (spawned >= target) break;
      const tx = midX + ox;
      const ty = Math.floor(_height / 2) + oy;
      const idx = ty * width + tx;
      if (!collData[idx]) {
        const npcSprite = this.add
          .image(tx * TILE_SIZE + TILE_SIZE / 2, ty * TILE_SIZE + TILE_SIZE / 2, "npc_dot")
          .setDepth(5)
          .setInteractive({ useHandCursor: true });
        
        const npcId = `npc_${spawned + 1}`;
        this.npcSprites.push(npcSprite);
        this.npcIds.set(npcSprite, npcId);

        npcSprite.on("pointerdown", () => this._onNpcClick(npcId));
        spawned++;
      }
    }
  }

  private async _onNpcClick(npcId: string): Promise<void> {
    const state = useGameStore.getState();
    const token = state.token;
    const character = state.activeCharacter;

    if (!token || !character) return;

    // Check for quest dialogue first; fall back to combat if none.
    try {
      const dialogue = await getNpcDialogue(token, npcId, character.id);
      if (dialogue && dialogue.options.length > 0) {
        useGameStore.getState().setNpcDialogue(dialogue);
        return;
      }
    } catch {
      // No quest dialogue — proceed to combat
    }

    try {
      const combatState = await startCombat(token, npcId, character.id);
      useGameStore.getState().setCombat({
        combatId: combatState.combat_id,
        npcId,
      });
    } catch (err) {
      console.error("Failed to start combat:", err);
    }
  }
}
