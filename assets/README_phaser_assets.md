# Phaser Asset Loading Guide (AETHERMOOR)

- Use SVGs for scalable assets during development. Phaser 3 can load SVGs via this.load.svg(key, url).
- Example:
  this.load.svg('grass', 'assets/tiles/grass_tile_v0.svg');
  this.load.svg('hero_idle_down', 'assets/sprites/hero_idle_down_v0.svg');
- Ensure your server serves SVGs with correct MIME types (image/svg+xml).
- For production, consider rasterizing to PNG spritesheets if needed for performance.
- Organize assets by type under assets/{tiles,sprites,ui,portraits,environment} for clarity.
