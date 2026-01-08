# Pokemon Yellow - Project Overview

## What This Is

A pixel-perfect recreation of Pokemon Yellow using PyGame, built incrementally from the ground up. We're recreating the entire game with authentic Gen 1 mechanics, starting with core movement and maps, then expanding to battles, Pokemon, and full gameplay.

## Current Status

**Completed**: Phases 1-6 (Core Engine through Battle System Foundation)
**Next Phase**: Phase 7 - Battle Mechanics

The game currently has:
- A working overworld with Pallet Town and Route 1 maps
- Player character that can walk around with smooth movement
- Collision detection (tiles and NPCs)
- Smooth camera following
- Map transitions between areas
- NPCs with dialog interaction system
- Dialog boxes with text rendering
- **Wild Pokemon encounters on grass tiles**
- **Authentic Pokemon Yellow battle UI with HP bars**
- **Turn-based battle system with Gen 1 damage calculation**
- **All 151 Gen 1 Pokemon with Yellow version learnsets**
- **All 165 Gen 1 moves with accurate stats**
- **Pokemon sprites (front and back) from PokéAPI**

## Tech Stack

### Language & Framework
- **Python 3.11+** (using Python 3.13.5)
- **PyGame 2.6.1** - Game framework
- **PyYAML** - For Pokemon/move data files
- **Requests** - For PokéAPI data hydration (build-time only)

### Package Management
- **uv** - Fast Python package manager (globally installed)
- **NEVER** use `pip` or `python` directly
- **ALWAYS** use `uv run python` or `uv sync`

### Data Formats
- **Maps**: JSON files in `data/maps/`
- **Pokemon/Moves**: YAML files in `data/pokemon/` and `data/moves/`
- **Type Chart**: YAML file in `data/types/`
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
│   │   ├── overworld_state.py       # Overworld (exploration)
│   │   └── battle_state.py          # Battle state with authentic UI
│   ├── overworld/                   # Overworld system
│   │   ├── tile.py                  # Tile definitions
│   │   ├── map.py                   # Map loading and rendering
│   │   ├── camera.py                # Viewport management
│   │   ├── entity.py                # Base entity class
│   │   ├── player.py                # Player character
│   │   ├── npc.py                   # NPCs with dialog
│   │   └── encounter_zones.py       # Wild encounter definitions
│   ├── battle/                      # Battle system
│   │   ├── species.py               # Pokemon species data structures
│   │   ├── move.py                  # Move data structures
│   │   ├── pokemon.py               # Pokemon instances with Gen 1 stats
│   │   ├── type_chart.py            # Type effectiveness
│   │   ├── damage_calculator.py     # Gen 1 damage formula
│   │   ├── species_loader.py        # Species YAML loader
│   │   └── move_loader.py           # Move YAML loader
│   ├── data/                        # Data loading
│   │   └── data_loader.py           # JSON/YAML loader with caching
│   └── ui/                          # UI components
│       └── dialog_box.py            # Dialog box for NPCs
├── data/
│   ├── maps/
│   │   ├── pallet_town.json         # Pallet Town map data
│   │   └── route_1.json             # Route 1 map
│   ├── pokemon/
│   │   └── species.yaml             # All 151 Gen 1 Pokemon
│   ├── moves/
│   │   └── moves.yaml               # All 165 Gen 1 moves
│   └── types/
│       └── type_chart.yaml          # Gen 1 type effectiveness
├── assets/
│   └── sprites/
│       └── pokemon/                 # 302 Pokemon sprites (front + back)
├── scripts/
│   └── hydrate_data.py              # PokéAPI data fetching script
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

### Data Hydration
```bash
# Re-fetch Pokemon data from PokéAPI (only needed if data is missing or outdated)
uv run python scripts/hydrate_data.py

# This will:
# - Fetch all 151 Gen 1 Pokemon with Yellow version learnsets
# - Fetch all 165 Gen 1 moves
# - Download front and back sprites for each Pokemon
# - Overwrite existing data/pokemon/species.yaml and data/moves/moves.yaml
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

### Phase 7+ Features
- ❌ Advanced battle mechanics (status effects, stat changes, accuracy)
- ❌ Battle menu system (FIGHT/ITEM/PKM/RUN options)
- ❌ Move selection UI (choosing from 4 moves)
- ❌ Experience and leveling system
- ❌ Pokemon catching mechanics
- ❌ Trainer battles
- ❌ Building interiors (door warps)
- ❌ NPC movement/AI
- ❌ Advanced dialog features (typewriter effect, branching, multi-page)
- ❌ Menus (Pokemon, Bag, Save)
- ❌ Party management screen
- ❌ Save/Load system

### Technical Debt
- Using colored rectangles as placeholders for tiles
- Player sprite is a yellow circle
- NPC sprites are blue circles
- Pokemon sprites loaded but not yet displayed in battle (using placeholders)
- No animation frames (player doesn't animate when walking)
- No sound/music
- Dialog text has no word wrapping

## Key Files to Know

### Entry Point
- `src/main.py` - Creates game, loads Pallet Town, starts game loop

### Core Systems
- `src/engine/game.py` - Main game loop (60 FPS, state stack)
- `src/engine/renderer.py` - Rendering with 3x scaling and text rendering
- `src/engine/input.py` - Keyboard input mapping

### Overworld
- `src/states/overworld_state.py` - Manages map, player, camera, NPCs, dialog
- `src/overworld/player.py` - Player movement and collision (tiles + NPCs)
- `src/overworld/npc.py` - NPC class with dialog interaction
- `src/overworld/map.py` - Map loading and tile rendering
- `src/overworld/camera.py` - Viewport following player

### UI
- `src/ui/dialog_box.py` - Dialog box for NPC conversations

### Data
- `data/maps/pallet_town.json` - Pallet Town map (with NPCs and warps)
- `data/maps/route_1.json` - Route 1 map

## Implementation Plan Reference

The detailed phase-by-phase plan is in `IMPLEMENTATION_PLAN.md`.

**Where we are**: End of Phase 5
**What's next**: Phase 6 - Battle System Foundation

### Completed Phases:
- ✅ Phase 1: Core Engine Setup
- ✅ Phase 2: Map Rendering System
- ✅ Phase 3: Player Movement
- ✅ Phase 4: Map Transitions
- ✅ Phase 5: NPCs and Dialog System

### Next Up (Phase 6):
- Pokemon data structures
- Battle state implementation
- Basic battle UI
- Wild encounter system

## Testing Checklist

Before moving to Phase 6, verify:
- ✅ Player moves smoothly in all 4 directions
- ✅ Collision blocks buildings, water, trees, signs, NPCs
- ✅ Camera follows player
- ✅ Map boundaries respected
- ✅ Map transitions work (Pallet Town ↔ Route 1)
- ✅ NPCs are visible and block movement
- ✅ Dialog appears when pressing Z near NPCs
- ✅ Dialog closes with Z button
- ✅ Input blocked during dialog
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
