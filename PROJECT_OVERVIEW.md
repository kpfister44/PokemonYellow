# Pokemon Yellow - Project Overview

## What This Is

A pixel-perfect recreation of Pokemon Yellow using PyGame, built incrementally from the ground up. We're recreating the entire game with authentic Gen 1 mechanics, starting with core movement and maps, then expanding to battles, Pokemon, and full gameplay.

## Current Status

**Completed**: Phases 1-3 (Core Engine, Map Rendering, Player Movement)
**Next Phase**: Phase 4 - Map Transitions

The game currently has:
- A working overworld with Pallet Town map
- Player character that can walk around
- Collision detection
- Smooth camera following
- All ready for connecting multiple maps

## Tech Stack

### Language & Framework
- **Python 3.11+** (using Python 3.13.5)
- **PyGame 2.6.1** - Game framework
- **PyYAML** - For Pokemon/move data files

### Package Management
- **uv** - Fast Python package manager (globally installed)
- **NEVER** use `pip` or `python` directly
- **ALWAYS** use `uv run python` or `uv sync`

### Data Formats
- **Maps**: JSON files in `data/maps/`
- **Pokemon/Moves**: YAML files (future) in `data/pokemon/` and `data/moves/`
- **Config**: `pyproject.toml` for dependencies

## Project Structure

```
pokemon_yellow/
├── src/
│   ├── main.py                      # Entry point - starts in Pallet Town
│   ├── engine/                      # Core game engine
│   │   ├── constants.py             # Screen size, tile size, colors, FPS
│   │   ├── game.py                  # Main game loop, state management
│   │   ├── input.py                 # Keyboard input handling
│   │   └── renderer.py              # Rendering with sprite caching
│   ├── states/                      # Game states
│   │   ├── base_state.py            # Abstract state interface
│   │   └── overworld_state.py       # Overworld (exploration)
│   ├── overworld/                   # Overworld system
│   │   ├── tile.py                  # Tile definitions
│   │   ├── map.py                   # Map loading and rendering
│   │   ├── camera.py                # Viewport management
│   │   ├── entity.py                # Base entity class
│   │   └── player.py                # Player character
│   ├── battle/                      # Battle system (NOT YET IMPLEMENTED)
│   ├── data/                        # Data loading
│   │   └── data_loader.py           # JSON/YAML loader with caching
│   └── ui/                          # UI components (NOT YET IMPLEMENTED)
├── data/
│   ├── maps/
│   │   └── pallet_town.json         # Pallet Town map data
│   ├── pokemon/                     # (empty - future)
│   └── moves/                       # (empty - future)
├── assets/
│   └── sprites/                     # (empty - using placeholder colors)
├── tests/                           # (empty - future)
├── pyproject.toml                   # uv project config
├── README.md                        # User-facing documentation
└── IMPLEMENTATION_PLAN.md           # Detailed phase-by-phase plan
```

## Key Commands

### Setup
```bash
# Install dependencies
uv sync --all-extras

# Run the game
uv run python -m src.main
```

### Development
```bash
# Test imports
uv run python -c "from src.main import main; print('✓ Imports OK')"

# Run tests (when we have them)
uv run pytest
```

### Git Workflow
```bash
# Check status
git status

# Stage and commit
git add <files>
git commit -m "type(scope): message"

# Push to GitHub
git push
```

## Architecture Overview

### State Machine
The game uses a state machine pattern:
- **OverworldState**: Walking around towns/routes
- **BattleState**: Pokemon battles (not yet implemented)
- **MenuState**: Menus (not yet implemented)

States are managed via a stack in `Game` class.

### Grid-Based Movement
- **16x16 pixel tiles** (Game Boy standard)
- Player moves one tile at a time
- **Smooth interpolation**: 8 frames per tile (2 pixels/frame)
- **Collision**: Tile-based boolean grid

### Rendering Pipeline
1. Game renders at native **160x144** resolution
2. Scaled **3x** to **480x432** window
3. Layers: Background (map) → Entities (player) → UI
4. Camera follows player, clamped to map bounds

### Data-Driven Design
- Maps defined in JSON with layers: ground, decorations, collision
- Warp points defined in map data (ready for Phase 4)
- Future: Pokemon stats, moves in YAML

## Technical Specifications

### Display
- **Native Resolution**: 160x144 pixels (Game Boy)
- **Window Size**: 480x432 pixels (3x scale)
- **Tile Size**: 16x16 pixels
- **Viewport**: 10 tiles wide × 9 tiles tall
- **FPS**: 60

### Colors (Game Boy Palette)
- Light green grass: `(139, 172, 15)`
- Dark green trees: `(34, 139, 34)`
- Gray buildings: `(48, 98, 48)`
- Tan paths: `(180, 180, 150)`
- Blue water: `(50, 100, 200)`
- Brown signs: `(139, 69, 19)`
- Yellow player: Circle placeholder

### Controls
- **Arrow Keys**: Move player
- **Z**: A button (confirm/interact) - not yet used
- **X**: B button (cancel) - not yet used
- **Enter**: Start button (menu) - not yet used

## Current Map: Pallet Town

### Layout
- **Size**: 20 × 18 tiles (320 × 288 pixels)
- **Professor Oak's Lab**: Top center (larger building)
- **Player's House**: Bottom left
- **Rival's House**: Bottom right
- **Pond**: Left side (water tiles)
- **Trees**: Perimeter
- **Signs**: 5 sign posts

### Player Starting Position
- Tile (8, 13) - On the path between the houses
- Set in `src/main.py`

### Warp Points (Defined, Not Yet Functional)
- Route 1: Two tiles at top (x=8, y=0) and (x=10, y=0)
- Player's house door: (x=4, y=14)
- Rival's house door: (x=14, y=14)
- Oak's Lab door: (x=9, y=4)

## What's NOT Implemented Yet

### Phase 4+ Features
- ❌ Map transitions / warps
- ❌ Building interiors
- ❌ Route 1 map
- ❌ NPCs
- ❌ Dialog system
- ❌ Battle system
- ❌ Pokemon
- ❌ Moves
- ❌ Menus
- ❌ Save/Load

### Technical Debt
- Using colored rectangles as placeholders for tiles
- Player sprite is a yellow circle
- No actual sprite sheets loaded
- No animation frames (player doesn't animate when walking)
- No sound/music

## Key Files to Know

### Entry Point
- `src/main.py` - Creates game, loads Pallet Town, starts game loop

### Core Systems
- `src/engine/game.py` - Main game loop (60 FPS, state stack)
- `src/engine/renderer.py` - Rendering with 3x scaling
- `src/engine/input.py` - Keyboard input mapping

### Overworld
- `src/states/overworld_state.py` - Manages map, player, camera
- `src/overworld/player.py` - Player movement and collision
- `src/overworld/map.py` - Map loading and tile rendering
- `src/overworld/camera.py` - Viewport following player

### Data
- `data/maps/pallet_town.json` - Map data (ground, decorations, collision, warps)

## Implementation Plan Reference

The detailed phase-by-phase plan is in `IMPLEMENTATION_PLAN.md`.

**Where we are**: End of Phase 3
**What's next**: Phase 4 - Map Transitions

Phase 4 will implement:
1. Create Route 1 map JSON
2. Warp detection (when player steps on warp tile)
3. Map switching functionality
4. Player repositioning after warp
5. Camera adjustment to new map

## Testing Checklist

Before moving to Phase 4, verify:
- ✅ Player moves smoothly in all 4 directions
- ✅ Collision blocks buildings, water, trees, signs
- ✅ Camera follows player
- ✅ Map boundaries respected
- ✅ No performance issues

## Common Issues & Solutions

### Import Errors
- Make sure to use `uv run python -m src.main`, not `python src/main.py`
- The project uses package-style imports

### Player Can Walk Through Things
- Check `collision` layer in map JSON
- 0 = walkable, 1 = blocked

### Camera Shows Black Areas
- Camera clamping is working - this happens at map edges
- It's correct behavior (can't scroll past map bounds)

### Window Won't Close
- This is a PyGame thing - might need to force quit
- Check that game loop exits properly on QUIT event

## Development Philosophy

From `CLAUDE.md`:
- **YAGNI** - Don't add features we don't need yet
- **Simple over clever** - Readable code over complex solutions
- **No over-engineering** - Minimal changes to achieve goals
- **Test frequently** - Run the game after each change
- **Commit often** - Small atomic commits

## Next Session Onboarding

When picking up Phase 4:

1. **Read** `IMPLEMENTATION_PLAN.md` Phase 4 section
2. **Run** `uv run python -m src.main` to see current state
3. **Test** player movement in Pallet Town
4. **Check** `data/maps/pallet_town.json` to see warp points defined
5. **Start** by creating `data/maps/route_1.json`

The foundation is solid. All the hard architectural decisions are made. Phase 4 is straightforward implementation.

## Questions?

- Check `README.md` for user documentation
- Check `IMPLEMENTATION_PLAN.md` for detailed specs
- Check `CLAUDE.md` for Kyle's development rules
- Map data format example: `data/maps/pallet_town.json`
- Code patterns established in existing `src/` files

Good luck! The game is coming together nicely. 🎮
