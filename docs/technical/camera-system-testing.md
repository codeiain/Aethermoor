# Camera System Testing Guide

> Date: 2026-04-15
> Test Subject: Fixed Viewport Camera Implementation
> Tester: IainBrown
> Status: Ready for Execution

## Test Environment

- **Browser**: Chrome/Firefox/Edge (recommended: Chrome DevTools)
- **URL**: http://localhost:3000
- **Services Required**: auth, character, world, frontend containers running
- **Test Account**: Any registered user account
- **Test Character**: Any character (will test with multiple)

## Pre-Test Setup

1. Ensure all Docker containers are running:
   ```powershell
   cd code/aethermoor/infra
   docker-compose ps
   ```

2. Open browser DevTools (F12) and monitor console for errors

3. Log in and select/create a test character

## Test Cases

### Test 1: Small Map (20×20 tiles)

**Objective**: Verify small maps are centered in viewport

**Current Map Size**: Check current zone size in console or DB
- If starter_town is already small, use it
- If not, may need to create a test zone or verify behavior on existing small areas

**Steps**:
1. Spawn in zone (starter_town or smallest available zone)
2. Open browser console and check:
   ```javascript
   // Check map dimensions
   console.log('Map tiles:', zone.width, zone.height);
   console.log('Map pixels:', zone.width * 32, zone.height * 32);
   console.log('Viewport:', window.innerWidth, window.innerHeight);
   ```
3. Verify visual appearance:
   - [ ] Map appears centered if smaller than viewport
   - [ ] Black/empty space visible around edges if map < viewport
   - [ ] Player can move to all edges of small map

**Expected Results**:
- Small map centered in viewport
- Player sprite stays centered while world scrolls
- No camera scroll beyond map bounds

**Status**: ⬜ Not Started | ⬜ Pass | ⬜ Fail

**Notes**:


---

### Test 2: Large Map (Current Map Size)

**Objective**: Verify camera scrolling and culling on standard-sized maps

**Steps**:
1. Spawn in starter_town or main zone
2. Open F12 DevTools → Performance tab
3. Start performance recording
4. Move player in all 4 directions for 10 seconds each
5. Stop recording and check:
   - [ ] FPS stays above 55fps
   - [ ] No frame drops or stuttering
   - [ ] Smooth camera scrolling

**Expected Results**:
- Consistent 60fps on standard maps (50×50 or smaller)
- Player sprite remains centered on screen
- World scrolls smoothly around player
- Only visible tiles rendered (verify in Phaser debug if available)

**Performance Metrics**:
- Target FPS: 60fps
- Minimum FPS: 55fps
- Frame time: <17ms

**Status**: ⬜ Not Started | ⬜ Pass | ⬜ Fail

**Notes**:


---

### Test 3: Edge/Corner Movement

**Objective**: Verify camera clamping at map boundaries

**Steps**:

**3.1: Top-Left Corner**
1. Move player to top-left corner of map
2. Verify:
   - [ ] Player can reach corner tile
   - [ ] Camera stops scrolling before showing area outside map
   - [ ] Player sprite may move away from center toward bottom-right
   - [ ] No black void visible at top or left edges

**3.2: Top-Right Corner**
1. Move player to top-right corner
2. Verify same behavior (player may move toward bottom-left of screen)

**3.3: Bottom-Left Corner**
1. Move player to bottom-left corner
2. Verify same behavior (player may move toward top-right of screen)

**3.4: Bottom-Right Corner**
1. Move player to bottom-right corner
2. Verify same behavior (player may move toward top-left of screen)

**3.5: Edge Scrolling**
1. Walk along top edge from left to right
2. Walk along right edge from top to bottom
3. Walk along bottom edge from right to left
4. Walk along left edge from bottom to top
5. Verify smooth scrolling along edges

**Expected Results**:
- Camera clamps at map boundaries
- Player can access all walkable tiles including corners
- No visual glitches or black voids at edges
- Smooth transition from center scrolling to edge clamping

**Status**: ⬜ Not Started | ⬜ Pass | ⬜ Fail

**Notes**:


---

### Test 4: Multiplayer Sprite Rendering

**Objective**: Verify other players render correctly with camera system

**Prerequisites**: Requires second browser/incognito window for second player

**Steps**:
1. Open second browser window (incognito mode)
2. Log in with different account
3. Create/select character and join same zone
4. Position players at different locations

**4.1: Static Positioning**
1. Player 1 stays still
2. Player 2 moves to various positions
3. From Player 1's view, verify:
   - [ ] Player 2 sprite visible when in viewport
   - [ ] Player 2 sprite scrolls with world (not fixed like player 1)
   - [ ] Player 2 nameplate scrolls with sprite

**4.2: Dynamic Movement**
1. Both players move simultaneously
2. Verify:
   - [ ] Smooth interpolation of Player 2 sprite
   - [ ] No jittering or teleporting
   - [ ] Nameplate follows sprite correctly

**4.3: Edge Cases**
1. Player 2 moves to edge of Player 1's viewport
2. Verify:
   - [ ] Player 2 disappears smoothly when out of view
   - [ ] Player 2 reappears when entering viewport

**Expected Results**:
- Multiplayer sprites positioned correctly in world space
- Sprites scroll with camera (not fixed like local player)
- Smooth movement interpolation
- Nameplates stay attached to sprites

**Status**: ⬜ Not Started | ⬜ Pass | ⬜ Fail

**Notes**:


---

### Test 5: Mobile/Touch Joystick

**Objective**: Verify joystick controls work with fixed camera

**Prerequisites**: Touch device or Chrome DevTools device emulation

**Steps**:
1. Open Chrome DevTools (F12)
2. Click device toolbar icon (Ctrl+Shift+M)
3. Select "iPad Air" or "iPhone 14"
4. Reload page

**5.1: Joystick Appearance**
1. Verify:
   - [ ] Virtual joystick appears on touch screen
   - [ ] Joystick positioned correctly (bottom area)
   - [ ] Joystick visible and doesn't scroll with camera

**5.2: Movement**
1. Drag joystick in all 8 directions (N, NE, E, SE, S, SW, W, NW)
2. Verify:
   - [ ] Player moves in expected direction
   - [ ] Camera scrolls correctly
   - [ ] Smooth movement in diagonal directions
   - [ ] Release joystick → player stops

**5.3: Edge Movement**
1. Use joystick to move to map edges
2. Verify same edge clamping behavior as keyboard

**Expected Results**:
- Joystick controls work identically to WASD
- Smooth 360° movement
- Camera follows player correctly
- No lag or input delay

**Status**: ⬜ Not Started | ⬜ Pass | ⬜ Fail

**Notes**:


---

### Test 6: Collision Detection

**Objective**: Verify collision still works with logical position tracking

**Steps**:

**6.1: Wall Collision**
1. Find a wall tile in the game
2. Attempt to walk through it
3. Verify:
   - [ ] Player blocked by wall
   - [ ] Camera doesn't scroll when blocked
   - [ ] No visual glitching

**6.2: Diagonal Wall Collision**
1. Find corner where two walls meet
2. Attempt to walk diagonally into corner
3. Verify:
   - [ ] Player blocked correctly
   - [ ] No sliding along walls in unexpected ways

**6.3: Movement Between Walkable Tiles**
1. Walk across several walkable tiles
2. Verify:
   - [ ] Smooth movement with no unexpected blocking
   - [ ] Camera follows smoothly

**6.4: Spawn Point Collision**
1. Log out and log back in (or select different character)
2. Verify:
   - [ ] Player spawns on walkable tile
   - [ ] Camera positioned correctly at spawn
   - [ ] No collision errors on spawn

**Expected Results**:
- Collision detection works correctly with logical position
- No movement through walls
- Player blocked appropriately
- Camera doesn't scroll when player is blocked

**Status**: ⬜ Not Started | ⬜ Pass | ⬜ Fail

**Notes**:


---

### Test 7: NPC Rendering

**Objective**: Verify NPCs scroll correctly with world

**Steps**:
1. Locate NPC dots in the zone (pink/magenta circles)
2. Move player around NPCs
3. Verify:
   - [ ] NPCs positioned at fixed world coordinates
   - [ ] NPCs scroll with world as player moves
   - [ ] NPCs render at correct depth (behind player but above tiles)
   - [ ] NPCs visible when in viewport, culled when out of view

**Expected Results**:
- NPCs scroll with world
- NPCs stay at their world position
- No visual glitches or depth issues

**Status**: ⬜ Not Started | ⬜ Pass | ⬜ Fail

**Notes**:


---

### Test 8: UI Elements

**Objective**: Verify HUD and UI elements don't scroll with camera

**Steps**:
1. Move player around the map
2. Check all UI elements:
   - [ ] HUD (health, gold, XP bar) stays fixed on screen
   - [ ] Zone name text stays centered when it appears
   - [ ] Any other UI overlays stay fixed

**Expected Results**:
- All UI elements have setScrollFactor(0) and stay fixed
- Only world objects (tiles, NPCs, other players) scroll
- Player sprite and UI both fixed on screen

**Status**: ⬜ Not Started | ⬜ Pass | ⬜ Fail

**Notes**:


---

## Browser Console Debugging

### Check Camera Position

Open console and run:
```javascript
// Access the game scene
const scene = window.game.scene.getScene('WorldScene');

// Check camera position
console.log('Camera scrollX:', scene.cameras.main.scrollX);
console.log('Camera scrollY:', scene.cameras.main.scrollY);

// Check player logical position (if exposed)
console.log('Player world position:', scene.playerWorldX, scene.playerWorldY);
console.log('Player tile position:', scene.playerTileX, scene.playerTileY);

// Check map bounds
console.log('Map size:', scene.mapWidth, scene.mapHeight);
console.log('Map pixels:', scene.mapWidth * 32, scene.mapHeight * 32);

// Check viewport
console.log('Viewport:', scene.scale.width, scene.scale.height);
```

### Enable Phaser Debug (if available)

If Phaser debug mode is enabled:
```javascript
scene.physics.world.drawDebug = true;
```

### Monitor FPS

```javascript
// Check game FPS
console.log('FPS:', window.game.loop.actualFps.toFixed(2));

// Monitor continuously
setInterval(() => {
  console.log('FPS:', window.game.loop.actualFps.toFixed(2));
}, 1000);
```

---

## Known Issues / Expected Behaviors

### Player Sprite Movement at Edges

**EXPECTED**: When camera reaches map edge, player sprite moves away from viewport center
- This is correct behavior - camera stops scrolling at edge
- Player can still move within walkable area
- Player sprite position shifts toward opposite edge of screen

### Small Map Centering

**EXPECTED**: Maps smaller than viewport show black/empty space around edges
- This is correct - map is centered in viewport
- Camera doesn't scroll for small maps

### Camera Initialization Delay

**MAY OCCUR**: Brief camera adjustment on spawn
- Scene loads → camera positioned → might see quick snap
- Not a bug if it happens once on load

---

## Performance Benchmarks

### Target Metrics

| Metric | Target | Minimum Acceptable |
|--------|--------|-------------------|
| FPS (standard movement) | 60fps | 55fps |
| FPS (edge scrolling) | 60fps | 55fps |
| Frame time | <16.7ms | <18ms |
| Camera scroll smoothness | Butter smooth | No visible stutter |
| Input latency | <50ms | <100ms |

### Asset Loading

- Initial zone load: <2 seconds
- Tile rendering: <100ms
- Sprite spawning: <50ms

---

## Test Results Summary

**Date Tested**: _________________

**Tester**: IainBrown

**Overall Status**: ⬜ All Pass | ⬜ Partial Pass | ⬜ Fail

### Test Results

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Small Map | ⬜ | |
| 2 | Large Map | ⬜ | |
| 3 | Edge/Corner Movement | ⬜ | |
| 4 | Multiplayer Sprites | ⬜ | |
| 5 | Mobile Joystick | ⬜ | |
| 6 | Collision Detection | ⬜ | |
| 7 | NPC Rendering | ⬜ | |
| 8 | UI Elements | ⬜ | |

### Issues Found

| Issue # | Description | Severity | Status |
|---------|-------------|----------|--------|
| | | | |

### Recommendations

---

## Sign-off

**Fixed Viewport Camera System is**: ⬜ Production Ready | ⬜ Needs Fixes | ⬜ Major Issues

**Tested By**: _________________ **Date**: _________________

**Reviewed By**: _________________ **Date**: _________________
