# Implementation Plan: 8x8 Base Tiles with 16x16 Movement Grid

## Overview

Convert the game from 32x32 tiles to an 8x8 base tile system with 16x16 metatile movement grid, matching the original Pokemon Yellow architecture.

**Current State:**
- TILE_SIZE = 16
- Sprites: 16x16 (scale=1)
- Movement: 16-pixel increments

**Target State:**
- TILE_SIZE = 8 (base rendering unit)
- METATILE_SIZE = 16 (movement/collision grid)
- Sprites: 16x16 (no scaling, spans 2x2 base tiles)
- Movement: 16-pixel increments (on metatile grid)

## Files to Modify

### 1. `src/engine/constants.py`

**Changes:**
```python
# Tile and grid settings
TILE_SIZE = 8                    # Base tile for rendering (was 16)
METATILE_SIZE = 16               # Movement/collision grid (2x2 tiles)
TILES_WIDE = GAME_WIDTH // TILE_SIZE    # 60 tiles (was 30)
TILES_HIGH = GAME_HEIGHT // TILE_SIZE   # 52 tiles (was 26)

# Movement operates on metatile grid
METATILES_WIDE = GAME_WIDTH // METATILE_SIZE   # 30 metatiles
METATILES_HIGH = GAME_HEIGHT // METATILE_SIZE  # 26 metatiles

# Movement speed (pixels per frame when moving)
# Player moves one metatile (16 pixels) over 8 frames
MOVEMENT_SPEED = 2  # 16 pixels / 8 frames = 2 pixels per frame
```

### 2. `src/overworld/entity.py`

**Changes to Entity class:**

The entity position system needs to work on the metatile grid (16x16), not the base tile grid (8x8).

```python
def __init__(self, metatile_x, metatile_y, sprite_surface=None):
    # Grid position (in metatiles, not base tiles)
    self.tile_x = metatile_x  # Keep variable name for compatibility
    self.tile_y = metatile_y

    # Pixel position uses METATILE_SIZE
    self.pixel_x = metatile_x * constants.METATILE_SIZE
    self.pixel_y = metatile_y * constants.METATILE_SIZE
```

**Update all references from TILE_SIZE to METATILE_SIZE for:**
- `pixel_x` / `pixel_y` calculations
- `move_progress` threshold
- `start_move()` target calculations
- `update_movement()` pixel updates
- `finish_move()` pixel snapping
- `cancel_move()` pixel snapping
- `get_rect()` hitbox size

**SpriteSheet class:**
- Keep scale=1 (sprites are already 16x16)
- No changes needed

### 3. `src/overworld/player.py`

**Changes:**
- Update any direct TILE_SIZE references to METATILE_SIZE
- Movement input should work on metatile grid
- Collision checking uses metatile coordinates

### 4. `src/overworld/npc.py`

**Changes:**
- Same as player.py - use METATILE_SIZE for position/movement

### 5. `src/overworld/map.py`

**Major changes needed:**

The map now has 8x8 base tiles but collision/walkability is on 16x16 metatile grid.

```python
class MapManager:
    def __init__(self, tmx_path: str, dialog_loader=None):
        # Validate base tile size
        if self.tile_width != constants.TILE_SIZE:
            raise ValueError(f"TMX tile size must be {constants.TILE_SIZE}")

        # Map dimensions in base tiles
        self.width = self.tmx_data.width      # in 8x8 tiles
        self.height = self.tmx_data.height

        # Map dimensions in metatiles (for collision grid)
        self.metatile_width = self.width // 2
        self.metatile_height = self.height // 2
```

**Collision grid changes:**
```python
def _build_collision_grid(self):
    # Build collision on metatile grid (16x16), not base tile grid
    self._solid_grid = [[False] * self.metatile_width for _ in range(self.metatile_height)]
    self._grass_grid = [[False] * self.metatile_width for _ in range(self.metatile_height)]

    # When checking tile properties, aggregate 2x2 base tiles into 1 metatile
    # A metatile is solid if ANY of its 4 base tiles are solid
    for metatile_y in range(self.metatile_height):
        for metatile_x in range(self.metatile_width):
            base_x = metatile_x * 2
            base_y = metatile_y * 2

            # Check all 4 base tiles in this metatile
            for dy in range(2):
                for dx in range(2):
                    tile_x = base_x + dx
                    tile_y = base_y + dy
                    # Get tile properties and set metatile as solid/grass
```

**Walkability check:**
```python
def is_walkable(self, metatile_x: int, metatile_y: int) -> bool:
    """Check if metatile position is walkable."""
    # Bounds check on metatile grid
    if metatile_x < 0 or metatile_x >= self.metatile_width:
        return False
    if metatile_y < 0 or metatile_y >= self.metatile_height:
        return False
    return not self._solid_grid[metatile_y][metatile_x]
```

**Object spawning (NPCs, items, warps):**
```python
def _object_tile_position(self, obj):
    # Convert pixel position to metatile position
    metatile_x = int(obj.x // constants.METATILE_SIZE)
    metatile_y = int(obj.y // constants.METATILE_SIZE)
    return (metatile_x, metatile_y)
```

**Warp detection:**
```python
def get_warp_at(self, metatile_x: int, metatile_y: int):
    # Check warps on metatile grid
```

### 6. `src/overworld/camera.py` (if exists) or camera logic

**Changes:**
- Camera follows player on pixel grid (unchanged)
- No special changes needed since pixel positions are still used for rendering

### 7. `src/states/overworld_state.py`

**Changes:**
- Player spawn position is in metatiles
- NPC positions are in metatiles
- Interaction detection uses metatile coordinates

### 8. `src/overworld/item_pickup.py`

**Changes:**
- Position stored in metatile coordinates
- Collision detection on metatile grid

## Rendering Considerations

**Map rendering** (no changes needed):
- pytmx renders the map using base 8x8 tiles automatically
- The cached surfaces work the same way

**Entity rendering:**
- Sprites are 16x16 (2x2 base tiles)
- Render position: `pixel_x - camera_x`, `pixel_y - camera_y`
- Sprite visually covers 2x2 base tiles, which is correct

## Testing Checklist

1. [ ] Player spawns at correct metatile position
2. [ ] Player moves 16 pixels per movement (one metatile)
3. [ ] Collision detection works on metatile grid
4. [ ] NPCs spawn at correct positions
5. [ ] NPCs block player movement correctly
6. [ ] Warps trigger at correct metatile positions
7. [ ] Item pickups work correctly
8. [ ] Grass encounters trigger correctly
9. [ ] Sprites render at correct positions (centered on metatile)
10. [ ] Camera follows player smoothly

## Migration Notes

**TMX Map Requirements:**
- Tile size must be 8x8
- Map dimensions should be even numbers (for clean metatile grid)
- Object positions should be on 16-pixel boundaries

**Tileset Requirements:**
- Base tileset: 8x8 tiles
- Can also use 16x16 metatile tileset (each metatile = 2x2 placement in Tiled)

## Summary of Key Constants

| Constant | Old Value | New Value | Purpose |
|----------|-----------|-----------|---------|
| TILE_SIZE | 16 | 8 | Base rendering tile |
| METATILE_SIZE | (new) | 16 | Movement/collision grid |
| TILES_WIDE | 30 | 60 | Viewport in base tiles |
| TILES_HIGH | 26 | 52 | Viewport in base tiles |
| METATILES_WIDE | (new) | 30 | Viewport in metatiles |
| METATILES_HIGH | (new) | 26 | Viewport in metatiles |
| MOVEMENT_SPEED | 2 | 2 | No change (16px / 8 frames) |

## Order of Implementation

1. Update `constants.py` with new tile constants
2. Update `entity.py` to use METATILE_SIZE for movement
3. Update `map.py` collision grid to use metatile system
4. Update `player.py` and `npc.py` for metatile coordinates
5. Update `overworld_state.py` for spawn/interaction logic
6. Update `item_pickup.py` for metatile positions
7. Run tests and fix any failures
8. Manual testing in game
