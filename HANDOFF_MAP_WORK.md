# Map Development Handoff

## Session Summary (Jan 19, 2026)

Kyle and Claude worked on creating Route 1 in Tiled Map Editor and fixing map-related bugs in the game code.

## Current State

### Maps Completed
- **pallet_town.tmx** - Working, has warps to Route 1 and player houses
- **route_1.tmx** - NEW, created this session, 40x72 tiles at 32x32 pixels

### Code Fixes Applied

1. **Collision Detection** (`src/overworld/map.py` line 90-93)
   - Fixed: pytmx converts empty string `""` to `None` for tile properties
   - Changed from `if self._is_truthy(properties.get("solid"))` to `if "solid" in properties`
   - Same fix applied for `is_grass`

2. **Player Spawn Position** (`src/overworld/map.py` line 200-201)
   - Fixed: Tile-based warps now use `dest_x: -1, dest_y: -1` instead of `0, 0`
   - This tells the game to use the destination map's `playerStart` position

3. **Route 1 North PlayerStart Removed**
   - Removed P tile at (20, 1) since Viridian City doesn't exist yet
   - Only south playerStart at (19, 70) remains

## Tiled Map Editor Notes

### Tileset Structure (route_1.tmx)
| Tileset | FirstGID | Purpose |
|---------|----------|---------|
| ground | 1 | Grass, paths (groundCompiled.png) |
| objects | 7 | Signs, items (objects.png) |
| triggers | 25 | P, E, X tiles (triggers.png) |
| overworld | 37 | Trees, buildings, terrain (overworld.png - scaled 4x from pret/pokeyellow) |

### Tile Properties
Set on tiles in the tileset (Edit Tileset mode), not individual placements:
- `solid` (empty string) - Blocks player movement
- `is_grass` (empty string) - Triggers wild Pokemon encounters
- `playerStart` = "up" or "down" - Spawn point, value is facing direction
- `entry` = "mapname.tmx" - Warp to another map

### Layer Structure
- **background** - Base terrain (grass, paths)
- **foreground** - Objects on top of player (tree tops, roofs)
- **triggers** - P and E tiles (invisible in game)

### Map Dimensions
- Route 1: 40x72 tiles (matches original 10x18 blocks, where each block = 4 base tiles)
- Pallet Town: 40x36 tiles
- All maps use 32x32 pixel tiles

## Known Issues / Next Steps

1. **Viridian City doesn't exist** - Route 1 has E tiles pointing to `viridian_city.tmx` at the north exit. Game will crash if player walks there.

2. **Pallet Town playerStart** - Currently at (10, 12). May need adjustment for coming from Route 1.

3. **Multiple spawn points not supported** - The game only uses the FIRST `playerStart` found in a map. Can't have different spawn points for different source maps without code changes.

4. **Wild encounters** - Route 1 needs encounter data in `data/encounters/yellow_encounters.yaml` (may already have placeholder data).

## File Locations

- Maps: `assets/maps/*.tmx`
- Tilesets: `assets/maps/*.png`
- Overworld tileset (scaled from pret): `assets/maps/overworld.png`
- Original pret tilesets: `/Users/kyle.pfister/Desktop/pokeyellow/gfx/tilesets/`

## How to Test

```bash
# Run the game
uv run python -m src.main

# Quick map test without full game
uv run python -c "
import pygame
pygame.init()
pygame.display.set_mode((480, 416))
from src.overworld.map import MapManager
mm = MapManager('assets/maps/route_1.tmx')
print(f'Size: {mm.width}x{mm.height}')
print(f'Player start: {mm.player_start}')
print(f'Warps: {len(mm.warps)}')
"
```

## Reference Documentation

- `MAP_SYSTEM.md` - Full map system documentation
- `PROJECT_OVERVIEW.md` - Project architecture and status
- [Tiled Docs](https://doc.mapeditor.org/en/stable/) - Tiled Map Editor documentation
- [pret/pokeyellow](https://github.com/pret/pokeyellow) - Original game disassembly (Kyle has copy at ~/Desktop/pokeyellow)

## Important Commands

```bash
# Never use pip or python directly
uv run python -m src.main  # Run game
uv run pytest              # Run tests
uv sync --all-extras       # Install dependencies
```
