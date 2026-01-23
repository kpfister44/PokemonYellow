# Map System Documentation

## Overview

Maps are TMX files created with [Tiled Map Editor](https://www.mapeditor.org/) and loaded via the `pytmx` library. Each map contains embedded tilesets, tile layers, and optional object layers for NPCs/items/warps.

**Current Resolution**: 160x144 pixels (20x18 tiles at 8x8 each)

## File Structure

```
assets/maps/
├── pallet_town.tmx      # Outdoor map (40x36 tiles)
├── player_house.tmx     # Interior map (18x18 tiles)
├── route_1.tmx          # Placeholder (needs real graphics)
├── groundCompiled.png   # Grass, paths, terrain
├── house.png            # Building exteriors
├── lab.png              # Oak's Lab tiles
├── indoors.png          # Interior floors, walls, furniture
├── objects.png          # Signs, fences, decorations
├── sprites.png          # Animated tiles (water, flowers)
└── triggers.png         # Invisible warp/spawn markers

assets/sprites/
├── player/
│   └── red.png          # Player sprite sheet (16x96, 6 frames)
└── npcs/
    ├── youngster.png    # Default NPC sprite
    ├── girl.png         # Lass trainer sprite
    ├── oak.png          # Professor Oak
    └── mom.png          # Player's mother
```

**Sprite Sheet Format:** Character sprites are 16x96 PNG files containing 6 frames (16x16 each):
- Frame 0-1: Down (standing, walking)
- Frame 2-3: Up (standing, walking)
- Frame 4-5: Side (standing, walking) - flipped for right direction

Sprites are 16x16 to match metatiles (2x2 base tiles).

## How MapManager Works

When a TMX file is loaded, `MapManager` (`src/overworld/map.py`) does the following:

```
TMX File
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ 1. Load tilesets and tile images via pytmx          │
├─────────────────────────────────────────────────────┤
│ 2. Separate layers into:                            │
│    • Lower layers → cached to one surface           │
│    • Fringe layers → cached to transparent surface  │
│    (Layers with "fringe/upper/top" in name)         │
├─────────────────────────────────────────────────────┤
│ 3. Build collision grid by scanning tile properties │
│    • `solid` property → marks tile as blocked       │
│    • `is_grass` property → marks for encounters     │
├─────────────────────────────────────────────────────┤
│ 4. Build warp list from tile properties             │
│    • `entry` property → destination map filename    │
│    • `playerStart` property → spawn point           │
├─────────────────────────────────────────────────────┤
│ 5. Parse object layer for NPCs, items, warps        │
│    • type="NPC" → spawns NPC                        │
│    • type="Item" → spawns item pickup               │
│    • type="Warp" → adds explicit warp point         │
└─────────────────────────────────────────────────────┘
```

## Tile Properties

Set these on individual tiles in the tileset (in Tiled: select tile → add Custom Property):

| Property | Value | Effect |
|----------|-------|--------|
| `solid` | `""` or `"true"` | Blocks player movement |
| `is_grass` | `""` or `"true"` | Triggers wild Pokemon encounters |
| `entry` | `"mapname.tmx"` | Warps player to another map |
| `playerStart` | `"down"` | Marks spawn point (value = facing direction) |
| `water` | `""` or `"true"` | Water tile (currently treated as decoration) |

**Note**: Empty string `""` is treated as truthy. Just adding the property is enough.

## Object Layer (Optional)

For more control, use an object layer instead of/in addition to tile properties:

### NPC Object
```xml
<object name="professor_oak" type="NPC" x="320" y="256" width="32" height="32">
  <properties>
    <property name="npc_id" value="oak"/>
    <property name="dialog_id" value="oak_greeting"/>
    <property name="direction" value="down"/>
    <property name="sprite_id" value="oak.png"/>
  </properties>
</object>
```

**NPC Properties:**
| Property | Required | Description |
|----------|----------|-------------|
| `npc_id` | No | Unique identifier (auto-generated if missing) |
| `dialog_id` | No | Dialog key for speech |
| `direction` | No | Facing direction: `up`, `down`, `left`, `right` (default: `down`) |
| `sprite_id` | No | Sprite filename override (e.g., `oak.png`) |
| `is_trainer` | No | Set to trigger battle |
| `trainer_class` | No | Trainer type for sprite selection (e.g., `Youngster`, `Lass`) |

**Sprite Selection:** NPCs select sprites in this priority:
1. `sprite_id` property if specified
2. `trainer_class` mapped to sprite (Youngster→youngster.png, Lass→girl.png)
3. Default: youngster.png

### Item Pickup Object
```xml
<object name="potion_1" type="Item" x="128" y="64" width="32" height="32">
  <properties>
    <property name="item_id" value="potion"/>
    <property name="pickup_id" value="pallet_potion_1"/>
  </properties>
</object>
```

### Warp Object (alternative to `entry` tile property)
```xml
<object name="to_route1" type="warp" x="320" y="0" width="32" height="32">
  <properties>
    <property name="dest_map" value="route_1.tmx"/>
    <property name="dest_x" value="5"/>
    <property name="dest_y" value="29"/>
  </properties>
</object>
```

**Warp Object Properties:**
| Property | Required | Description |
|----------|----------|-------------|
| `dest_map` | Yes | Destination map filename (e.g., `route_1.tmx`) |
| `dest_x` | Yes | Destination X coordinate in metatiles |
| `dest_y` | Yes | Destination Y coordinate in metatiles |

**Note**: The warp rectangle (x, y, width, height) defines a trigger zone. When the player enters ANY metatile within this zone, the warp activates. This allows multi-tile warp areas (e.g., a large doorway or transition zone).

## Creating a New Map

### Step 1: Set Up Tiled

1. Download and install [Tiled](https://www.mapeditor.org/)
2. Open an existing map as reference: `assets/maps/pallet_town.tmx`

### Step 2: Create New Map

1. File → New → New Map
2. Settings:
   - Orientation: Orthogonal
   - Tile size: **8 x 8 pixels** (must match)
   - Map size: Your desired dimensions (e.g., 20x15 tiles)
3. Save as `assets/maps/your_map.tmx`

### Step 3: Add Tilesets

1. Map → New Tileset
2. Name it (e.g., "ground")
3. Source: Browse to `assets/maps/groundCompiled.png`
4. Tile size: **8 x 8**
5. Check "Embed in map" (keeps everything in one TMX file)
6. Repeat for other tilesets you need

**Available tileset PNGs:**
| File | Contents |
|------|----------|
| `groundCompiled.png` | Grass, dirt paths, basic terrain |
| `lab.png` | Oak's Lab building and interior |
| `house.png` | Generic building exteriors |
| `indoors.png` | Interior floors, walls, furniture |
| `objects.png` | Signs, fences, small decorations |
| `sprites.png` | Animated tiles (water, flowers) |
| `triggers.png` | Invisible markers for warps/spawns |

### Step 4: Set Tile Properties

For each tileset, mark which tiles have special behavior:

1. In Tiled, click on the tileset panel (bottom)
2. Select a tile (e.g., a wall tile)
3. View → Views and Toolbars → Tile Properties
4. Add custom property: `solid` with empty value
5. Repeat for grass tiles (`is_grass`), warp tiles (`entry`), etc.

### Step 5: Create Layers

Recommended layer structure (bottom to top):
1. `background` - Ground tiles (grass, paths, floor)
2. `objects` - Objects layer for NPCs/items (optional)
3. `foreground` - Trees, building tops, anything that overlaps player

**Fringe layers**: Name a layer with "fringe", "upper", or "top" to render it above the player.

### Step 6: Paint Your Map

1. Select a tile layer
2. Use Stamp Brush (B) to paint tiles
3. Place a `playerStart` tile where the player should spawn
4. Place `entry` tiles at map edges/doorways for transitions

### Step 7: Connect to Other Maps

For the player to travel between maps:

1. **In your new map**: Place `entry` tiles at exits pointing to destination maps
2. **In destination map**: Ensure there's a `playerStart` tile OR the warp object specifies `dest_x`/`dest_y`

Example warp flow:
```
pallet_town.tmx                    player_house.tmx
┌─────────────────┐                ┌─────────────────┐
│                 │                │                 │
│    [entry] ─────┼───────────────►│ [playerStart]   │
│    tile         │                │ tile            │
│                 │                │                 │
│ [playerStart] ◄─┼────────────────┤ [entry]         │
│                 │                │ tile            │
└─────────────────┘                └─────────────────┘
```

### Step 8: Test Your Map

```bash
# Quick test - verify map loads
uv run python -c "
from src.overworld.map import MapManager
import pygame
pygame.init()
pygame.display.set_mode((480, 416))
mm = MapManager('assets/maps/your_map.tmx')
print(f'Size: {mm.width}x{mm.height} tiles')
print(f'Player spawn: {mm.player_start}')
print(f'Warps: {len(mm.warps)}')
print(f'NPCs: {len(mm.npcs)}')
print(f'Items: {len(mm.item_pickups)}')
"

# Full test - run the game
uv run python -m src.main
```

### Step 9: Add Wild Encounters (Optional)

To enable wild Pokemon encounters on your map:

1. Mark grass tiles with `is_grass` property in the tileset
2. Add encounter data to `data/encounters/yellow_encounters.yaml`:

```yaml
your_map_name:  # Must match map filename without .tmx
  - pokemon: rattata
    method: walk
    chance: 40
    min_level: 2
    max_level: 4
  - pokemon: pidgey
    method: walk
    chance: 35
    min_level: 2
    max_level: 5
```

## MapManager API Reference

```python
class MapManager:
    """Loads TMX maps, caches render surfaces, and exposes map helpers."""

    # Attributes
    width: int                      # Map width in tiles
    height: int                     # Map height in tiles
    player_start: tuple[int, int]   # (x, y) spawn from playerStart tile
    warps: list[dict]               # Warp points (tile-based and object-based)
    npcs: list[NPC]                 # NPCs from object layer
    item_pickups: list[ItemPickup]  # Items from object layer

    # Methods
    def is_walkable(self, tile_x: int, tile_y: int) -> bool:
        """Check if tile is walkable (not solid, within bounds)."""

    def is_grass(self, tile_x: int, tile_y: int) -> bool:
        """Check if tile triggers wild encounters."""

    def get_warp_at(self, tile_x: int, tile_y: int) -> dict | None:
        """Get warp data at position, or None."""

    def draw_base(self, renderer, camera_x: int, camera_y: int) -> None:
        """Draw lower layers (background)."""

    def draw_fringe(self, renderer, camera_x: int, camera_y: int) -> None:
        """Draw upper layers (rendered above player)."""
```

## Troubleshooting

### Map doesn't load
- Check file path is correct (`assets/maps/your_map.tmx`)
- Verify tile size is exactly 8x8
- Ensure tileset images are in `assets/maps/`

### Player can walk through walls
- Select the wall tile in Tiled
- Add `solid` property (value can be empty)
- Re-save the TMX file

### Warps don't work
- Check `entry` property value matches exact filename (e.g., `player_house.tmx`)
- Ensure destination map has a `playerStart` tile
- Or use object-based warp with explicit `dest_x`/`dest_y`

### Wild encounters don't trigger
- Verify grass tiles have `is_grass` property
- Check map name in `yellow_encounters.yaml` matches filename
- Encounters only trigger 10% of the time on grass

## Current Maps

| Map | Size | Description |
|-----|------|-------------|
| `pallet_town.tmx` | 40x36 | Main starting area with Oak's Lab |
| `player_house.tmx` | 18x18 | Player's house interior |
| `route_1.tmx` | 10x9 | Placeholder (needs real tileset) |

## Resources

- **Tiled Documentation**: https://doc.mapeditor.org/
- **pytmx Library**: https://github.com/bitcraft/pytmx
- **pylletTown** (tileset source): https://github.com/renfredxh/pylletTown
- **pret/pokeyellow** (reference): https://github.com/pret/pokeyellow
