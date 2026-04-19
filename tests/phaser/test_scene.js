// Minimal Phaser 3 scene to validate SVG asset loading and layout
// This is a lightweight test harness; run in a browser environment with Phaser 3 loaded.
class AssetTestScene extends Phaser.Scene {
  constructor() {
    super({ key: 'AssetTest' });
  }

  preload() {
    // Tiles
    this.load.image('grass', 'assets/tiles/grass_tile_v0.svg');
    this.load.image('grassEdge', 'assets/tiles/grass_edge_tile_v0.svg');
    this.load.image('dirt', 'assets/tiles/dirt_tile_v0.svg');
    this.load.image('water', 'assets/tiles/water_tile_v0.svg');
    this.load.image('worldmap', 'assets/tiles/worldmap_tile_v0.svg');
    // Buildings / props
    this.load.image('stoneWall', 'assets/tiles/stone_wall_tile_v0.svg');
    this.load.image('door', 'assets/tiles/door_tile_v0.svg');
    // Characters / NPCs
    this.load.image('heroDown', 'assets/sprites/hero_idle_down_v0.svg');
    this.load.image('npcDown', 'assets/sprites/npc_idle_down_v0.svg');
    this.load.image('heroLeft', 'assets/sprites/hero_idle_left_v0.svg');
    this.load.image('heroRight', 'assets/sprites/hero_idle_right_v0.svg');
    // UI
    this.load.image('hpBar', 'assets/ui/hp_bar_v1.svg');
    this.load.image('dialogue', 'assets/ui/dialogue_window_v1.svg');
    // Extras
    this.load.image('worldPt', 'assets/tiles/worldmap_tile_v0.svg');
  }

  create() {
    // Simple grid of tiles
    this.add.image(60, 60, 'grassEdge');
    this.add.image(102, 60, 'grass');
    this.add.image(144, 60, 'dirt');
    this.add.image(186, 60, 'water');
    // Characters
    this.add.image(60, 120, 'heroDown');
    this.add.image(100, 120, 'npcDown');
    // UI overlays
    this.add.image(280, 20, 'hpBar');
    this.add.image(250, 90, 'dialogue');
  }
}

// If you are running this in a standalone HTML page, ensure Phaser is loaded and this scene is started.
// The following bootstrap will start automatically when this script is loaded in an HTML page
// that also includes the Phaser library via CDN or local file.
(function bootstrapPhaserTest() {
  if (typeof Phaser === 'undefined') {
    // Phaser not loaded yet; wait for global execution environment to load it.
    return;
  }
  const config = {
    type: Phaser.AUTO,
    width: 320,
    height: 180,
    backgroundColor: '#1a1a1a',
    scene: AssetTestScene
  };
  // eslint-disable-next-line no-new
  new Phaser.Game(config);
})();
