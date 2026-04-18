import Phaser from "phaser";

const TILE_SIZE = 32;
const INTERP_MS = 150; // tween duration for remote player movement

interface RemotePlayer {
  sprite: Phaser.GameObjects.Sprite;
  nameplate: Phaser.GameObjects.Text;
  targetX: number;
  targetY: number;
}

interface WelcomePayload {
  type: "welcome";
  players: PlayerInfo[];
}

interface PlayerJoinPayload {
  type: "player_join";
  id: string;
  name: string;
  level: number;
  x: number;
  y: number;
}

interface PlayerMovePayload {
  type: "player_move";
  id: string;
  x: number;
  y: number;
}

interface PlayerLeavePayload {
  type: "player_leave";
  id: string;
}

interface ErrorPayload {
  type: "error";
  message: string;
}

interface PlayerInfo {
  id: string;
  name: string;
  level: number;
  x: number;
  y: number;
}

type ServerMessage =
  | WelcomePayload
  | PlayerJoinPayload
  | PlayerMovePayload
  | PlayerLeavePayload
  | ErrorPayload;

/**
 * PresenceManager — owns the WebSocket connection for multiplayer presence
 * and manages remote player sprites within a Phaser scene.
 *
 * Lifecycle:
 *   1. Instantiate in WorldScene.create() after the player sprite is ready.
 *   2. Call connect() to open the WebSocket.
 *   3. WorldScene.update() calls sendMove(tileX, tileY) when the local player moves.
 *   4. Call destroy() in WorldScene shutdown to clean up sprites and close WS.
 *
 * All remote players are rendered as "player" sprites (same texture as local
 * player) with a subtle colour tint to distinguish them, plus a nameplate text.
 */
export class PresenceManager {
  private scene: Phaser.Scene;
  private ws: WebSocket | null = null;
  private players = new Map<string, RemotePlayer>();
  private ownCharId: string;
  private ownToken: string;
  private ownName: string;
  private ownLevel: number;
  private zoneId: string;
  private wsUrl: string;
  private lastSentX = -1;
  private lastSentY = -1;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private destroyed = false;

  constructor(opts: {
    scene: Phaser.Scene;
    zoneId: string;
    wsUrl: string;
    token: string;
    characterId: string;
    name: string;
    level: number;
  }) {
    this.scene = opts.scene;
    this.zoneId = opts.zoneId;
    this.wsUrl = opts.wsUrl;
    this.ownToken = opts.token;
    this.ownCharId = opts.characterId;
    this.ownName = opts.name;
    this.ownLevel = opts.level;
  }

  connect(): void {
    if (this.destroyed) return;
    try {
      this.ws = new WebSocket(`${this.wsUrl}/world/zones/${this.zoneId}/ws`);
      this.ws.onopen = () => this._onOpen();
      this.ws.onmessage = (evt) => this._onMessage(evt.data as string);
      this.ws.onclose = () => this._onClose();
      this.ws.onerror = () => {
        // onerror is always followed by onclose — handle reconnect there
      };
    } catch {
      this._scheduleReconnect();
    }
  }

  private _onOpen(): void {
    if (!this.ws) return;
    this.ws.send(JSON.stringify({
      type: "auth",
      token: this.ownToken,
      character_id: this.ownCharId,
      name: this.ownName,
      level: this.ownLevel,
    }));
  }

  private _onMessage(raw: string): void {
    let msg: ServerMessage;
    try {
      msg = JSON.parse(raw) as ServerMessage;
    } catch {
      return;
    }

    switch (msg.type) {
      case "welcome":
        // Add all existing players (excluding self)
        for (const p of msg.players) {
          if (p.id !== this.ownCharId) this._addPlayer(p);
        }
        break;

      case "player_join":
        if (msg.id !== this.ownCharId) this._addPlayer(msg);
        break;

      case "player_move":
        if (msg.id !== this.ownCharId) this._movePlayer(msg.id, msg.x, msg.y);
        break;

      case "player_leave":
        this._removePlayer(msg.id);
        break;

      case "error":
        console.warn("[Presence] server error:", msg.message);
        break;
    }
  }

  private _onClose(): void {
    if (!this.destroyed) this._scheduleReconnect();
  }

  private _scheduleReconnect(): void {
    if (this.destroyed || this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, 3000);
  }

  /** Send local player position. Throttled externally (WorldScene calls at move time). */
  sendMove(tileX: number, tileY: number): void {
    if (tileX === this.lastSentX && tileY === this.lastSentY) return;
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({ type: "move", x: tileX, y: tileY }));
    this.lastSentX = tileX;
    this.lastSentY = tileY;
  }

  private _addPlayer(p: PlayerInfo): void {
    if (this.players.has(p.id)) return;
    if (!this.scene.sys.isActive()) return;

    const px = p.x * TILE_SIZE + TILE_SIZE / 2;
    const py = p.y * TILE_SIZE + TILE_SIZE / 2;

    const sprite = this.scene.add.sprite(px, py, "player");
    sprite.setDepth(9); // just below local player (depth 10)
    sprite.setTint(0xffaa44); // warm tint to distinguish remote players

    const nameplate = this.scene.add.text(px, py - 22, `${p.name} ${p.level}`, {
      fontSize: "5px",
      fontFamily: "'Press Start 2P'",
      color: "#e8e0d0",
    });
    nameplate.setOrigin(0.5, 1);
    nameplate.setDepth(11);

    this.players.set(p.id, { sprite, nameplate, targetX: p.x, targetY: p.y });
  }

  private _movePlayer(id: string, tileX: number, tileY: number): void {
    const remote = this.players.get(id);
    if (!remote) return;
    if (!this.scene.sys.isActive()) return;

    const worldX = tileX * TILE_SIZE + TILE_SIZE / 2;
    const worldY = tileY * TILE_SIZE + TILE_SIZE / 2;

    remote.targetX = tileX;
    remote.targetY = tileY;

    // Smooth interpolation — tween sprite and nameplate together
    this.scene.tweens.add({
      targets: [remote.sprite, remote.nameplate],
      x: worldX,
      y: worldY,
      duration: INTERP_MS,
      ease: "Linear",
    });

    // Nameplate needs offset correction after tween
    // We correct by re-setting y on the nameplate via a separate tween offset
    this.scene.tweens.add({
      targets: remote.nameplate,
      y: worldY - 22,
      duration: INTERP_MS,
      ease: "Linear",
    });
  }

  private _removePlayer(id: string): void {
    const remote = this.players.get(id);
    if (!remote) return;
    remote.sprite.destroy();
    remote.nameplate.destroy();
    this.players.delete(id);
  }

  get playerCount(): number {
    return this.players.size;
  }

  destroy(): void {
    this.destroyed = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.onclose = null; // prevent reconnect loop on intentional destroy
      this.ws.close();
      this.ws = null;
    }
    for (const remote of this.players.values()) {
      remote.sprite.destroy();
      remote.nameplate.destroy();
    }
    this.players.clear();
  }
}
