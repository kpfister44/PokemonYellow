# Handoff: Implement 8x8 Tile System

## Task

Implement the tile system changes described in `TILE_SYSTEM_PLAN.md`. Convert the game from the current 16x16 tile system to an 8x8 base tile system with 16x16 metatile movement grid.

## Context

This is a Pokemon Yellow recreation using PyGame. We're aligning the tile system with the original Game Boy architecture:
- **8x8 base tiles** for map rendering (what Tiled uses)
- **16x16 metatiles** for player movement and collision (2x2 base tiles)
- **16x16 sprites** for player and NPCs

The player and NPCs move on the metatile grid (16px steps), not the base tile grid.

## Current State

- `TILE_SIZE = 16` in constants.py (was recently changed from 32)
- Sprites are 16x16 (scale=1)
- Movement is 16-pixel increments
- Tests are currently failing because TMX maps have 32x32 tiles

## Your Task

1. Read `TILE_SYSTEM_PLAN.md` for the full implementation details
2. Implement the changes in this order:
   - `src/engine/constants.py` - Add METATILE_SIZE, change TILE_SIZE to 8
   - `src/overworld/entity.py` - Use METATILE_SIZE for movement logic
   - `src/overworld/map.py` - Collision grid on metatile boundaries
   - `src/overworld/player.py` - Metatile coordinates
   - `src/overworld/npc.py` - Metatile coordinates
   - `src/states/overworld_state.py` - Spawn positions
   - `src/overworld/item_pickup.py` - Metatile positions
3. Run tests with `uv run pytest`
4. Note: Some tests may fail until Kyle creates new 8x8 TMX maps in Tiled

## Key Concept

```
Base Tile (8x8)          Metatile (16x16)
┌───┬───┐                ┌───────────┐
│ A │ B │                │           │
├───┼───┤  = 1 metatile  │  Player   │
│ C │ D │                │  moves    │
└───┴───┘                │  here     │
                         └───────────┘
```

- Map renders with 8x8 tiles
- Player/NPC positions and movement use 16x16 metatile coordinates
- Collision checks aggregate 2x2 base tiles into metatiles

## Commands

- Run tests: `uv run pytest`
- Run game: `uv run python -m src.main`

## Important

- Use `uv run` for all Python commands (never raw `python` or `pip`)
- Follow existing code style
- The TMX validation in map.py will need to check for TILE_SIZE (8), not METATILE_SIZE
