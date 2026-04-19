#!/usr/bin/env python3
"""Generate placeholder PNG assets for Aethermoor starter zone.
All assets use RGBA (colour type 6). No third-party libs required.
"""
import struct, zlib, os

OUT_BASE = "/home/iain/Aethermoor/frontend/src/assets"

# ---------------------------------------------------------------------------
# PNG primitives
# ---------------------------------------------------------------------------
def _chunk(tag: bytes, data: bytes) -> bytes:
    c = tag + data
    return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)

def png_bytes(width: int, height: int, pixels: list) -> bytes:
    """pixels: flat list of (R,G,B,A) 4-tuples, row-major."""
    sig   = b'\x89PNG\r\n\x1a\n'
    ihdr  = _chunk(b'IHDR', struct.pack('>II', width, height) + bytes([8, 6, 0, 0, 0]))
    raw   = bytearray()
    for y in range(height):
        raw += b'\x00'                       # filter byte: None
        for x in range(width):
            raw += bytes(pixels[y * width + x])
    idat  = _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    iend  = _chunk(b'IEND', b'')
    return sig + ihdr + idat + iend

def write_png(path: str, width: int, height: int, pixels: list):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(png_bytes(width, height, pixels))

def tile16(pixels) -> bytes:
    return png_bytes(16, 16, pixels)

def write16(path: str, pixels: list):
    write_png(path, 16, 16, pixels)

def grid_png(cols: int, rows: int, frames: list) -> bytes:
    """Compose a spritesheet of cols*rows 16x16 frames."""
    W, H = cols * 16, rows * 16
    out = [(0, 0, 0, 0)] * (W * H)
    for idx, frame in enumerate(frames):
        tx, ty = idx % cols, idx // cols
        for py in range(16):
            for px in range(16):
                dst = (ty * 16 + py) * W + (tx * 16 + px)
                src = py * 16 + px
                out[dst] = frame[src] if src < len(frame) else (0, 0, 0, 0)
    return png_bytes(W, H, out)

def write_grid(path: str, cols: int, rows: int, frames: list):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(grid_png(cols, rows, frames))

def write_sized(path: str, width: int, height: int, pixels: list):
    write_png(path, width, height, pixels)

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
T    = (  0,   0,   0,   0)   # transparent
K    = (  0,   0,   0, 255)   # black
W    = (255, 255, 255, 255)   # white

G1   = ( 76, 153,   0, 255)   # grass dark
G2   = (102, 179,   0, 255)   # grass mid
G3   = (128, 204,   0, 255)   # grass light
GF   = ( 51, 128,   0, 255)   # grass feature
FLWR = (255, 220,  50, 255)   # flower yellow
FLWP = (255, 100, 150, 255)   # flower pink

BR   = (139,  90,  43, 255)   # wood/dirt brown
LBR  = (185, 122,  87, 255)   # light brown
DBR  = (110,  70,  30, 255)   # dark brown

DG   = ( 80,  80,  80, 255)   # dark gray
MG   = (128, 128, 128, 255)   # mid gray
LG   = (192, 192, 192, 255)   # light gray

BL   = ( 64, 164, 223, 255)   # water blue
BL2  = (100, 180, 240, 255)   # water highlight

TAN  = (210, 180, 140, 255)   # wall tan
ROOF = (160,  60,  60, 255)   # inn roof red
DKRF = ( 80,  80, 100, 255)   # smithy roof
AWNG = ( 70, 130, 180, 255)   # store awning
DOOR = (100,  60,  30, 255)   # door brown
WIN  = (180, 220, 255, 255)   # window blue

SKIN = (255, 213, 170, 255)
H_BRN= (101,  55,   0, 255)
H_BLK= ( 30,  20,  10, 255)
H_GLD= (200, 150,  50, 255)
H_TAN= (180, 130,  80, 255)
SR   = (200,  50,  50, 255)   # shirt red
SB   = ( 50, 100, 200, 255)   # shirt blue
SG   = ( 50, 160,  50, 255)   # shirt green
PB   = ( 60,  60, 120, 255)   # pants blue
PBR  = (100,  70,  40, 255)   # pants brown
BOOT = ( 80,  50,  20, 255)

GOB  = ( 80, 140,  60, 255)   # goblin skin
GOBD = ( 50, 100,  30, 255)   # goblin dark
GOBE = (255,  50,   0, 255)   # goblin eye
WPN  = (200, 200, 200, 255)   # weapon silver

UI_BG   = ( 40,  40,  60, 200)
UI_FR   = (100, 100, 140, 255)
HP_R    = (220,  50,  50, 255)
HP_D    = (100,  20,  20, 255)
MP_B    = ( 50,  80, 220, 255)
MP_D    = ( 20,  30, 100, 255)
BTN_N   = ( 80, 100, 140, 255)
BTN_H   = (110, 140, 190, 255)
BTN_P   = ( 50,  70, 100, 255)
QUEST_Y = (255, 220,   0, 255)
BUBBLE  = (240, 240, 240, 220)

C_CMN   = (150, 150, 150, 255)
C_UNC   = ( 30, 200,  30, 255)
C_RARE  = ( 30, 100, 220, 255)
C_EPIC  = (160,   0, 220, 255)

# ---------------------------------------------------------------------------
# Tile generators  (all return list of 256 RGBA tuples)
# ---------------------------------------------------------------------------
def _p(w=16, h=16, base=None):
    if base is None: base = T
    return [base] * (w * h)

def grass1():
    p = _p(base=G2)
    for i in [18, 35, 72, 120, 180, 220]: p[i] = G1
    for i in [50, 100, 150, 200]:          p[i] = G3
    return p

def grass2():
    p = _p(base=G3)
    for i in [10, 30, 80, 130, 190, 240]: p[i] = G2
    for i in [20, 60, 110, 160]:           p[i] = GF
    return p

def grass3():
    p = _p(base=G2)
    for i in [38, 39, 54, 55]:   p[i] = FLWR
    for i in [130, 131, 146, 147]: p[i] = FLWP
    return p

def dirt_path():
    p = _p(base=BR)
    for i in range(256):
        if (i // 16 + i % 16) % 3 == 0: p[i] = LBR
        if i % 17 == 0:                  p[i] = DBR
    return p

def stone():
    p = []
    for y in range(16):
        for x in range(16):
            if x % 5 == 0 or y % 5 == 0:        p.append(DG)
            elif (x // 5 + y // 5) % 2 == 0:    p.append(MG)
            else:                                 p.append(LG)
    return p

def water(frame: int):
    off = 3 if frame == 2 else 0
    p = []
    for y in range(16):
        for x in range(16):
            if (x + y * 2 + off) % 6 < 2: p.append(BL2)
            else:                           p.append(BL)
    return p

def tree_oak():
    p = _p()
    for y in range(10, 16):
        for x in range(6, 10): p[y*16+x] = BR
    for y in range(12):
        for x in range(16):
            if (x-8)**2 + (y-5)**2 < 40: p[y*16+x] = G1
    for y in range(1, 5):
        for x in range(5, 11):
            if (x-8)**2 + (y-4)**2 < 14: p[y*16+x] = G3
    return p

def tree_pine():
    p = _p()
    for y in range(12, 16):
        for x in range(7, 9): p[y*16+x] = BR
    layers = [(7,9,2),(5,11,3),(3,13,4),(1,15,5),(0,16,6),(0,16,7),(1,15,8),(0,16,9)]
    for (s, e, row) in layers:
        if row < 16:
            for x in range(s, e): p[row*16+x] = G1 if (row%2)==0 else G2
    return p

def _building(wall, roof, door):
    p = []
    for y in range(16):
        for x in range(16):
            if y < 6:
                if x <= y or x >= 15-y: p.append(T)
                else:                    p.append(roof)
            elif x == 0 or x == 15 or y == 15:
                p.append(DG)
            elif 6 <= x <= 9 and y >= 10:
                p.append(door)
            elif 2 <= x <= 4 and 7 <= y <= 9:
                p.append(WIN)
            elif 11 <= x <= 13 and 7 <= y <= 9:
                p.append(WIN)
            else:
                p.append(wall)
    return p

def dungeon_entrance():
    p = _p()
    for y in range(16):
        for x in range(16):
            if y < 4 or x < 1 or x > 14: p[y*16+x] = MG
            elif (x-8)**2 + (y-9)**2 < 30 and y > 5: p[y*16+x] = (20, 10, 30, 255)
            elif y < 12 or x < 2 or x > 13: p[y*16+x] = MG if (x+y)%3 != 0 else DG
    return p

def ruins():
    p = _p()
    blocks = [(0,0,4,4),(6,0,3,3),(12,0,4,4),(0,7,3,5),(4,10,5,3),(11,8,4,4),(0,13,6,3),(9,12,7,4)]
    for (bx, by, bw, bh) in blocks:
        for y in range(by, min(by+bh, 16)):
            for x in range(bx, min(bx+bw, 16)):
                p[y*16+x] = MG if (x+y) % 2 == 0 else DG
    return p

# ---------------------------------------------------------------------------
# Character sprite generators
# ---------------------------------------------------------------------------
WALK_ARM  = [0,  1,  0, -1]    # arm y-offset per frame
WALK_LEG  = [0,  1,  2,  1]    # left-leg x-offset per frame

def _char_frame(shirt, pants, hair, facing: str, frame: int, is_goblin=False, weapon=False):
    p = _p()
    skin = SKIN if not is_goblin else GOB

    # --- head ---
    for y in range(2, 7):
        for x in range(5, 11):
            p[y*16+x] = skin
    # hair
    for x in range(4, 12): p[1*16+x] = hair
    for x in range(4, 12): p[2*16+x] = hair
    # eyes (only front-facing variants show eyes; simplified for placeholder)
    if facing in ('down',):
        p[4*16+6] = K; p[4*16+9] = K
    if is_goblin:
        p[4*16+6] = GOBE; p[4*16+9] = GOBE

    # --- body ---
    for y in range(7, 12):
        for x in range(5, 11): p[y*16+x] = shirt

    # --- arms (animated) ---
    arm_off = WALK_ARM[frame % 4]
    for y in range(7+arm_off, 11+arm_off):
        if 0 <= y < 16:
            p[y*16+4]  = shirt
            p[y*16+11] = shirt

    # --- legs (animated) ---
    leg_off = WALK_LEG[frame % 4]
    for y in range(12, 16):
        lx = 6 + leg_off
        rx = 9 - leg_off
        if 0 <= lx < 16: p[y*16+lx] = pants
        if 0 <= rx < 16 and rx != lx: p[y*16+rx] = pants
    # boots
    for x in range(5, 8):  p[15*16+x] = BOOT
    for x in range(8, 11): p[15*16+x] = BOOT

    # --- weapon ---
    if weapon:
        for y in range(4, 13): p[y*16+12] = WPN

    return p

def hero_sheet(shirt, pants, hair) -> bytes:
    """64×64: 4 cols (frames 0-3) × 4 rows (down/up/left/right)"""
    frames = []
    for facing in ['down', 'up', 'left', 'right']:
        for fr in range(4):
            frames.append(_char_frame(shirt, pants, hair, facing, fr))
    return grid_png(4, 4, frames)

def npc_sheet(shirt, pants, hair) -> bytes:
    """64×16: 1 frame × 4 directions (idle)"""
    frames = [_char_frame(shirt, pants, hair, d, 0) for d in ['down','up','left','right']]
    return grid_png(4, 1, frames)

def goblin_sheet() -> bytes:
    """64×32: row0=4 walk frames, row1=4 attack frames"""
    walk   = [_char_frame(GOB, GOBD, GOBD, 'down', fr, is_goblin=True) for fr in range(4)]
    attack = [_char_frame(GOB, GOBD, GOBD, 'down', fr, is_goblin=True, weapon=True) for fr in range(4)]
    return grid_png(4, 2, walk + attack)

# ---------------------------------------------------------------------------
# UI generators
# ---------------------------------------------------------------------------
def bar_img(w: int, h: int, fill_c, bg_c, border_c) -> list:
    p = []
    for y in range(h):
        for x in range(w):
            if x == 0 or x == w-1 or y == 0 or y == h-1: p.append(border_c)
            elif x-1 < w-3:                                p.append(fill_c)
            else:                                           p.append(bg_c)
    return p

def inventory_slot() -> bytes:
    p = []
    for y in range(32):
        for x in range(32):
            if x < 2 or x > 29 or y < 2 or y > 29: p.append(UI_FR)
            elif x < 3 or x > 28 or y < 3 or y > 28: p.append((60,60,80,255))
            else: p.append(UI_BG)
    return png_bytes(32, 32, p)

def rarity_border(colour) -> bytes:
    sz = 32
    p = []
    r, g, b, a = colour
    light = (min(255,r+60), min(255,g+60), min(255,b+60), a)
    for y in range(sz):
        for x in range(sz):
            on_outer = x < 2 or x >= sz-2 or y < 2 or y >= sz-2
            on_inner = x == 2 or x == sz-3 or y == 2 or y == sz-3
            if on_outer: p.append(colour)
            elif on_inner: p.append(light)
            else: p.append(T)
    return png_bytes(sz, sz, p)

def quest_marker(symbol: str) -> list:
    p = _p()
    for y in range(16):
        for x in range(16):
            if (x-8)**2 + (y-8)**2 < 56: p[y*16+x] = (40, 40, 40, 200)
    if symbol == '!':
        for y in range(3, 11): p[y*16+8] = QUEST_Y
        p[13*16+8] = QUEST_Y
    else:
        for x in range(5, 11): p[3*16+x] = QUEST_Y
        p[4*16+11] = QUEST_Y; p[5*16+11] = QUEST_Y
        p[6*16+10] = QUEST_Y; p[7*16+9]  = QUEST_Y
        p[8*16+8]  = QUEST_Y; p[9*16+8]  = QUEST_Y
        p[11*16+8] = QUEST_Y
    return p

def chat_bubble() -> list:
    p = _p()
    for y in range(1, 11):
        for x in range(1, 15):
            corner = (x < 2 and y < 2) or (x > 12 and y < 2) or (x < 2 and y > 9) or (x > 12 and y > 9)
            if not corner: p[y*16+x] = BUBBLE
    p[11*16+4] = BUBBLE; p[11*16+3] = BUBBLE; p[12*16+3] = BUBBLE
    for y in range(1, 11): p[y*16+0] = MG; p[y*16+14] = MG
    for x in range(1, 15): p[0*16+x] = MG; p[10*16+x] = MG
    return p

def button_img(colour, w=64, h=20) -> bytes:
    r, g, b, a = colour
    light = (min(255,r+30), min(255,g+30), min(255,b+30), a)
    p = []
    for y in range(h):
        for x in range(w):
            if x == 0 or x == w-1 or y == 0 or y == h-1: p.append(K)
            elif x == 1 or x == w-2 or y == 1 or y == h-2: p.append(light)
            else: p.append(colour)
    return png_bytes(w, h, p)

# ---------------------------------------------------------------------------
# Generate everything
# ---------------------------------------------------------------------------
def main():
    tiles   = f"{OUT_BASE}/tiles"
    sprites = f"{OUT_BASE}/sprites"
    ui      = f"{OUT_BASE}/ui"

    # --- Tiles ---
    write16(f"{tiles}/grass_1.png",            grass1())
    write16(f"{tiles}/grass_2.png",            grass2())
    write16(f"{tiles}/grass_3.png",            grass3())
    write16(f"{tiles}/dirt_path.png",          dirt_path())
    write16(f"{tiles}/stone.png",              stone())
    write16(f"{tiles}/water_1.png",            water(1))
    write16(f"{tiles}/water_2.png",            water(2))
    write16(f"{tiles}/tree_oak.png",           tree_oak())
    write16(f"{tiles}/tree_pine.png",          tree_pine())
    write16(f"{tiles}/building_inn.png",       _building(TAN, ROOF, DOOR))
    write16(f"{tiles}/building_blacksmith.png",_building(LG,  DKRF, DOOR))
    write16(f"{tiles}/building_store.png",     _building(TAN, AWNG, DOOR))
    write16(f"{tiles}/dungeon_entrance.png",   dungeon_entrance())
    write16(f"{tiles}/ruins.png",              ruins())
    print("Tiles: 14 PNGs")

    # --- Sprites ---
    def _ws(path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f: f.write(data)

    _ws(f"{sprites}/hero_m.png",          hero_sheet(SR,  PB,  H_BRN))
    _ws(f"{sprites}/hero_f.png",          hero_sheet(SB,  PBR, H_GLD))
    _ws(f"{sprites}/npc_farmer.png",      npc_sheet(SG,   PBR, H_BRN))
    _ws(f"{sprites}/npc_blacksmith.png",  npc_sheet(DG,   PB,  H_BLK))
    _ws(f"{sprites}/npc_innkeeper.png",   npc_sheet(TAN,  PBR, H_TAN))
    _ws(f"{sprites}/enemy_goblin.png",    goblin_sheet())
    print("Sprites: 6 PNG spritesheets")

    # --- UI ---
    write_sized(f"{ui}/hp_bar.png",   64, 10, bar_img(64, 10, HP_R, HP_D, K))
    write_sized(f"{ui}/mana_bar.png", 64, 10, bar_img(64, 10, MP_B, MP_D, K))
    _ws(f"{ui}/inventory_slot.png",          inventory_slot())
    _ws(f"{ui}/rarity_border_common.png",    rarity_border(C_CMN))
    _ws(f"{ui}/rarity_border_uncommon.png",  rarity_border(C_UNC))
    _ws(f"{ui}/rarity_border_rare.png",      rarity_border(C_RARE))
    _ws(f"{ui}/rarity_border_epic.png",      rarity_border(C_EPIC))
    write16(f"{ui}/quest_marker_exclaim.png", quest_marker('!'))
    write16(f"{ui}/quest_marker_question.png",quest_marker('?'))
    write16(f"{ui}/chat_bubble.png",          chat_bubble())
    _ws(f"{ui}/button_normal.png",  button_img(BTN_N))
    _ws(f"{ui}/button_hover.png",   button_img(BTN_H))
    _ws(f"{ui}/button_pressed.png", button_img(BTN_P))
    print("UI: 13 PNGs")

    print(f"\nDone! All assets in {OUT_BASE}/")
    print("Spritesheet dimensions:")
    print("  hero_m.png / hero_f.png   : 64x64  (4 frames × 4 directions, each frame 16x16)")
    print("  npc_*.png                  : 64x16  (4 directions × 1 idle frame, each 16x16)")
    print("  enemy_goblin.png           : 64x32  (row0=4 walk, row1=4 attack, each frame 16x16)")
    print("  tiles                      : 16x16  (individual tiles)")
    print("  hp_bar / mana_bar          : 64x10")
    print("  inventory_slot             : 32x32")
    print("  rarity_border_*            : 32x32  (transparent centre, coloured border)")
    print("  quest_marker_*             : 16x16")
    print("  chat_bubble                : 16x16")
    print("  button_*                   : 64x20")

if __name__ == '__main__':
    main()
