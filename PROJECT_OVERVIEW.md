# Pokemon Yellow - Project Overview

## What This Is

A pixel-perfect recreation of Pokemon Yellow using PyGame, built incrementally from the ground up. We're recreating the entire game with authentic Gen 1 mechanics, starting with core movement and maps, then expanding to battles, Pokemon, and full gameplay.

## Current Status

**Completed**: Phases 1-7 (Core Engine through Advanced Battle Mechanics)
**Current Phase**: Phase 8 - Advanced Features (Move learning + EXP flow)

The game currently has:
- A working overworld with Pallet Town and Route 1 maps
- TMX-based map system (Tiled) with cached lower/fringe layers
- Player character that can walk around with smooth movement
- Collision detection (tiles and NPCs)
- Smooth camera following
- Map transitions between areas
- NPCs with dialog interaction system
- Dialog boxes with text rendering
- **Wild Pokemon encounters on grass tiles**
- **Authentic Pokemon Yellow battle UI with HP bars**
- **Turn-based battle system with Gen 1 damage calculation**
- **Battle menu + move selection UI**
- **Accuracy/critical hits/priority-based turn order**
- **Status effects (paralysis, burn, freeze, poison, sleep)**
- **Stat stage changes and modifiers**
- **Advanced move effects (drain, multi-hit, flinch)**
- **Experience gain and level-ups**
- **Move learning on level-up with 4-move limit and forget flow**
- **Catching flow via Poké Balls from the item bag (with throw/shake animation)**
- **Trainer battles (via NPC interaction)**
- **All 151 Gen 1 Pokemon with Yellow version learnsets**
- **All 165 Gen 1 moves with accurate stats**
- **Pokemon sprites (front and back) from PokéAPI**
- **Title menu with Continue/New Game/Option**
- **Start menu with Pokemon, Bag, and Save options**
- **Pokedex list and entry screens (seen/caught visibility rules)**
- **Save/Load system (manual save from start menu, stored in `saves/save.json`)**
- **Party screen with HP bar ticking**
- **Inventory/Bag system with item pickups**
- **Item effects (healing, status cures, revives, balls, X items)**
- **HP bar ticking in battle**

## Tech Stack

### Language & Framework
- **Python 3.11+** (using Python 3.13.5)
- **PyGame 2.6.1** - Game framework
- **Resolution**: 320x288 internal render size, scaled 3x in window
- **pytmx** - Tiled TMX map loader for PyGame
- **PyYAML** - For Pokemon/move data files
- **Requests** - For PokéAPI data hydration (build-time only)

### Package Management
- **uv** - Fast Python package manager (globally installed)
- **NEVER** use `pip` or `python` directly
- **ALWAYS** use `uv run python` or `uv sync`

### Data Formats
- **Maps**: Tiled `.tmx/.tsx` files in `assets/maps/`
- **Pokemon/Moves**: YAML files in `data/pokemon/` and `data/moves/`
- **Encounters**: YAML file in `data/encounters/`
- **Type Chart**: YAML file in `data/types/`
- **Config**: `pyproject.toml` for dependencies
- **Items**: YAML files in `data/items/`

## Data Hydration from PokéAPI

**IMPORTANT**: All Pokemon, move, and encounter data is fetched from PokéAPI at **build-time** (not runtime). The data is stored locally in YAML files and loaded by the game.

### What Gets Hydrated

The `scripts/hydrate_data.py` script fetches comprehensive Gen 1 data:

**Pokemon Data** (`data/pokemon/species.yaml`):
- All 151 Gen 1 Pokemon
- Base stats (HP, Attack, Defense, Special, Speed)
- Types (1-2 types per Pokemon)
- Evolution chains (with trigger method, level, or item requirements)
- Growth rates (medium-slow, fast, etc. for leveling curves)
- Pokedex entries (Yellow version flavor text)
- Pokedex genus/category, height, and weight
- Capture rates (0-255, for catch difficulty calculations)
- Base happiness (friendship starting values)
- Gender ratios
- Base experience (XP yield when defeated)
- Complete learnsets (level-up moves + TM/HM compatibility)
- Sprite file paths (front and back)

**Move Data** (`data/moves/moves.yaml`):
- All 165 Gen 1 moves
- Power, accuracy, PP, type
- Category (physical, special, status)
- Priority (-7 to +5 for turn order)
- Effect chance (e.g., 10% freeze chance)

**Encounter Data** (`data/encounters/yellow_encounters.yaml`):
- Wild encounters for 24 Gen 1 locations
- Locations: Viridian Forest, Mt. Moon, Rock Tunnel, Power Plant, Pokemon Tower, Seafoam Islands, Pokemon Mansion, Cerulean Cave, Diglett's Cave
- For each encounter: Pokemon name, encounter method (walk/surf/fish), chance percentage, min/max levels

**Sprites** (`assets/sprites/pokemon/`):
- 302 PNG files (front + back for each of 151 Pokemon)
- Downloaded from PokéAPI sprite URLs

### How to Run Hydration

```bash
# Fetch all data (only needed if data files are missing or you want fresh data)
uv run python scripts/hydrate_data.py
```

**When to run:**
- Initial setup (if data files don't exist)
- If you delete data files
- If you want to update to latest PokéAPI data
- If you modify the script to fetch different data

**You do NOT need to run this normally** - all data is already committed to the repo.

### API Endpoints Used

The script fetches from these PokéAPI endpoints:
- `/pokemon/{id}` - Base stats, sprites, learnsets
- `/pokemon-species/{id}` - Evolution chains, Pokedex entries, growth rates
- `/evolution-chain/{id}` - Detailed evolution data
- `/growth-rate/{id}` - Leveling curves
- `/move/{id}` - Move stats and effects
- `/location-area/{area}` - Wild encounter data

All data is filtered for **Pokemon Yellow version** where available, falling back to Red/Blue when Yellow-specific data isn't available.

### Script Features

- Rate limiting (100ms delay between requests)
- Caching (evolution chains and growth rates cached to avoid duplicate API calls)
- Error handling (continues on 404s for missing locations)
- Progress indicators (shows each Pokemon/move being fetched)
- YAML output (human-readable and easy to manually edit if needed)

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
│   │   ├── bag_state.py             # Bag item use flow
│   │   ├── party_state.py           # Party screen state
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
│   │   ├── hp_bar_display.py         # HP bar tick animation logic
│   │   ├── species_loader.py        # Species YAML loader
│   │   └── move_loader.py           # Move YAML loader
│   ├── items/                       # Item system
│   │   ├── bag.py                   # Bag inventory rules
│   │   ├── item.py                  # Item data structures
│   │   ├── item_effects.py          # Item usage effects
│   │   └── item_loader.py           # Item YAML loader
│   ├── data/                        # Data loading
│   │   └── data_loader.py           # JSON/YAML loader with caching
│   └── ui/                          # UI components
│       └── dialog_box.py            # Dialog box for NPCs
│       └── bag_screen.py            # Bag UI list
│       └── party_screen.py          # Party UI list
├── data/
│   ├── maps/                        # (Legacy JSON maps removed)
│   ├── pokemon/
│   │   └── species.yaml             # All 151 Gen 1 Pokemon (from PokéAPI)
│   ├── moves/
│   │   └── moves.yaml               # All 165 Gen 1 moves (from PokéAPI)
│   ├── encounters/
│   │   └── yellow_encounters.yaml   # Wild encounters for 24 locations (from PokéAPI)
│   ├── items/
│   │   ├── items.yaml               # Yellow item data (from PokéAPI)
│   │   └── yellow_item_list.yaml    # Curated item list for hydration
│   └── types/
│       └── type_chart.yaml          # Gen 1 type effectiveness
├── assets/
│   ├── maps/                        # TMX/TSX maps and tileset images
│   └── sprites/
│       └── pokemon/                 # 302 Pokemon sprites (front + back)
├── scripts/
│   └── hydrate_data.py              # PokéAPI data fetching script
├── tests/                           # Automated tests
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
- **BattleState**: Pokemon battles
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
- **Z**: A button (confirm/interact)
- **X**: B button (cancel/back)
- **Start (S)**: Start button (menu)

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
- Set for New Game in `src/states/title_menu_state.py`

### Warp Points (Defined, Not Yet Functional)
- Route 1: Two tiles at top (x=8, y=0) and (x=10, y=0)
- Player's house door: (x=4, y=14)
- Rival's house door: (x=14, y=14)
- Oak's Lab door: (x=9, y=4)

## What's NOT Implemented Yet

### Phase 8+ Features
- ❌ Building interiors (door warps)
- ❌ NPC movement/AI
- ❌ Advanced dialog features (typewriter effect, branching, multi-page)
- ⚠️ Inventory/Bag system + item effects (missing: TMs/HMs, key items, repels, PP restores, vitamins)

### Technical Debt
- Using colored rectangles as placeholders for tiles
- Player sprite is a yellow circle
- NPC sprites are blue circles
- No animation frames (player doesn't animate when walking)
- No sound/music
- Dialog text has no word wrapping

## Key Files to Know

### Entry Point
- `src/main.py` - Creates game, starts title menu, then loads game

### Core Systems
- `src/engine/game.py` - Main game loop (60 FPS, state stack)
- `src/engine/renderer.py` - Rendering with 3x scaling and text rendering
- `src/engine/input.py` - Keyboard input mapping

### Overworld
- `src/states/overworld_state.py` - Manages map, player, camera, NPCs, dialog
- `src/states/title_menu_state.py` - Title menu state (Continue/New Game/Option)
- `src/overworld/player.py` - Player movement and collision (tiles + NPCs)
- `src/overworld/npc.py` - NPC class with dialog interaction
- `src/overworld/map.py` - Map loading and tile rendering
- `src/overworld/camera.py` - Viewport following player

### UI
- `src/ui/dialog_box.py` - Dialog box for NPC conversations
- `src/ui/title_menu.py` - Title menu UI component

### Battle System
- `src/battle/species.py` - Species data structures (with evolution, growth rate, etc.)
- `src/battle/move.py` - Move data structures (with priority, effect chance)
- `src/battle/pokemon.py` - Pokemon instances with Gen 1 stats
- `src/battle/damage_calculator.py` - Gen 1 damage formula
- `src/battle/experience_calculator.py` - Gen 1 EXP formulas and level thresholds
- `src/battle/catch_calculator.py` - Gen 1 catch rate formula
- `src/battle/trainer.py` - Trainer data structure
- `src/battle/status_effects.py` - Status condition enum
- `src/battle/stat_stages.py` - Stat stage tracking
- `src/battle/species_loader.py` - Loads species from YAML
- `src/battle/move_loader.py` - Loads moves from YAML
- `src/states/battle_state.py` - Battle state with authentic UI
- `src/ui/battle_menu.py` - FIGHT/ITEM/PKM/RUN menu
- `src/ui/move_menu.py` - Move selection UI

### Data Files
- `data/maps/pallet_town.json` - Pallet Town map (with NPCs and warps)
- `data/maps/route_1.json` - Route 1 map
- `data/pokemon/species.yaml` - All 151 Pokemon (comprehensive data from PokéAPI)
- `data/moves/moves.yaml` - All 165 moves (from PokéAPI)
- `data/encounters/yellow_encounters.yaml` - Wild encounters for 24 locations
- `data/types/type_chart.yaml` - Gen 1 type effectiveness chart

### Data Hydration Script
- `scripts/hydrate_data.py` - Fetches all Pokemon, move, and encounter data from PokéAPI

## Available Pokemon Data Fields

When implementing new features, you have access to these fields in the Species dataclass:

**Basic Info:**
- `species_id` (str) - lowercase name, e.g., "bulbasaur"
- `number` (int) - Pokedex number (1-151)
- `name` (str) - Display name, e.g., "Bulbasaur"
- `types` (list[str]) - 1-2 types, e.g., ["grass", "poison"]
- `type1`, `type2` (properties) - Backwards compatibility

**Stats:**
- `base_stats` (BaseStats) - HP, Attack, Defense, Special, Speed

**Evolution & Leveling:**
- `evolution_chain` (dict) - Complete evolution data with triggers, levels, items
- `growth_rate` (str) - "medium-slow", "fast", etc. (for XP curves)
- `base_experience` (int) - XP yield when this Pokemon is defeated

**Capture & Friendship:**
- `capture_rate` (int) - 0-255, higher = easier to catch
- `base_happiness` (int) - Starting friendship value
- `gender_rate` (int) - -1=genderless, 0=male, 8=female, else ratio

**Moves:**
- `level_up_moves` (list[LevelUpMove]) - Complete learnset with levels and methods
  - Each has: `level`, `move` (name), `method` ("level-up" or "machine")

**Display:**
- `pokedex_entry` (str) - Yellow version Pokedex text
- `sprites` (SpriteData) - `front` and `back` sprite file paths

## Available Move Data Fields

**Basic Info:**
- `move_id` (str) - move name
- `id_number` (int) - Gen 1 move ID (1-165)
- `name` (str) - Display name
- `type` (str) - Move type

**Battle Stats:**
- `power` (Optional[int]) - Damage (None for status moves)
- `accuracy` (Optional[int]) - Hit chance (None for never-miss)
- `pp` (int) - Power points
- `category` (str) - "physical", "special", or "status"

**Advanced:**
- `priority` (int) - Turn order (-7 to +5, default 0)
- `effect_chance` (Optional[int]) - % chance for secondary effect (e.g., 10% freeze)

## Implementation Plan Reference

The detailed phase-by-phase plan is in `IMPLEMENTATION_PLAN.md`.

**Where we are**: Phase 8 in progress
**What's next**: Continue Phase 8 - Advanced Features

### Completed Phases:
- ✅ Phase 1: Core Engine Setup
- ✅ Phase 2: Map Rendering System
- ✅ Phase 3: Player Movement
- ✅ Phase 4: Map Transitions
- ✅ Phase 5: NPCs and Dialog System
- ✅ Phase 6: Battle System Foundation (with full Gen 1 data from PokéAPI)

### Next Up (Phase 8):
- Inventory/Bag remaining items (TMs/HMs, key items, repels, PP restores, vitamins)
- Building interiors (door warps)
- NPC movement/AI
- Advanced dialog features (typewriter effect, branching, multi-page)

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

When picking up Phase 8:

1. **Read** `IMPLEMENTATION_PLAN.md` Phase 8 section
2. **Run** `uv run python -m src.main` to see current state
3. **Test** a wild battle (status effects, multi-hit, drain, EXP)
4. **Test** a trainer battle on Route 1 (RUN blocked, next Pokemon sent)
5. **Decide** whether to split Phase 8 into party UI vs. inventory vs. save/load

The foundation is solid. All battle mechanics and trainer battles are in place, so Phase 8 can focus on menus, party management, and persistence.

## Questions?

- Check `README.md` for user documentation
- Check `IMPLEMENTATION_PLAN.md` for detailed specs
- Check `CLAUDE.md` for Kyle's development rules
- Map data format example: `data/maps/pallet_town.json`
- Code patterns established in existing `src/` files

Good luck! The game is coming together nicely. 🎮
