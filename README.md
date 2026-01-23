# Pokemon Yellow - PyGame Recreation

A pixel-perfect recreation of Pokemon Yellow using PyGame, built incrementally from movement system to full battle mechanics.

## Project Status

**Current Phase**: Phase 8 - Advanced Features (In Progress)

### Completed Features
- ✅ Core game loop with 60 FPS frame timing and state machine
- ✅ Native 160x144 resolution (Game Boy standard)
- ✅ Tile-based TMX map system with Tiled editor support
- ✅ Multi-layer rendering (background, entities, fringe/overlay)
- ✅ Camera/viewport management with smooth following
- ✅ Player sprite with grid-based movement and smooth interpolation
- ✅ Collision detection (tiles + NPCs)
- ✅ Bidirectional warp system between maps (supports rectangular zones)
- ✅ NPC interaction with dialog system
- ✅ Wild Pokemon encounters on grass tiles
- ✅ Complete turn-based battle system with Gen 1 mechanics:
  - Authentic Pokemon Yellow battle UI with HP bar animations
  - Accurate Gen 1 damage calculation (STAB, type effectiveness, critical hits, accuracy)
  - Status effects (paralysis, burn, freeze, poison, sleep)
  - Stat stage changes and modifiers
  - Priority-based turn order
  - Multi-hit and drain moves
- ✅ All 151 Gen 1 Pokemon with Yellow version stats and learnsets
- ✅ All 165 Gen 1 moves with proper classifications
- ✅ Pokemon sprites (front and back) from PokéAPI
- ✅ Trainer battles with NPC trainers
- ✅ Pokemon catching via Poké Balls with throw/shake animation
- ✅ Experience gain and level-up system with move learning
- ✅ Title menu and Start menu (Pokemon, Bag, Save)
- ✅ Party screen with HP bar ticking
- ✅ Pokedex with seen/caught tracking
- ✅ Inventory system with item effects
- ✅ Save/Load functionality

## Getting Started

### Requirements
- Python 3.11+ (tested on 3.13.5)
- uv package manager (fast Python package manager)

### Installation & Running

```bash
# Clone the repo
git clone https://github.com/kpfister44/PokemonYellow.git
cd PokemonYellow

# Install dependencies
uv sync --all-extras

# Run the game
uv run python -m src.main
```

The game launches in a 160x144 window at Pallet Town. You can walk around, warp to Route 1, and battle Pokemon immediately.

### Optional: Refresh Pokemon Data

```bash
# Re-fetch all Pokemon, move, and encounter data from PokéAPI
# Only needed if data files are missing or you want the latest data
uv run python scripts/hydrate_data.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrow Keys | Movement / Navigation |
| Z | A Button (Confirm/Interact) |
| X | B Button (Cancel/Back) |
| Enter | Start Button (Menu) |
| Shift | Select Button (Future) |

## Project Structure

```
PokemonYellow/
├── src/
│   ├── main.py                   # Entry point
│   ├── engine/                   # Core engine
│   │   ├── constants.py          # Game constants and colors
│   │   ├── game.py               # Main game loop (60 FPS)
│   │   ├── input.py              # Input handling
│   │   └── renderer.py           # Rendering pipeline
│   ├── states/                   # Game states
│   │   ├── base_state.py         # State interface
│   │   ├── overworld_state.py    # Map exploration
│   │   ├── battle_state.py       # Turn-based battles
│   │   ├── title_menu_state.py   # Title screen
│   │   ├── party_state.py        # Party management
│   │   └── bag_state.py          # Inventory
│   ├── overworld/                # Overworld system
│   │   ├── map.py                # TMX map loader with warp/NPC/item parsing
│   │   ├── player.py             # Player movement and collision
│   │   ├── camera.py             # Viewport management
│   │   ├── npc.py                # NPC definitions and dialog
│   │   └── encounter_zones.py    # Wild encounter definitions
│   ├── battle/                   # Battle system
│   │   ├── pokemon.py            # Pokemon instances with stats
│   │   ├── move.py               # Move definitions
│   │   ├── species.py            # Pokemon species data
│   │   ├── damage_calculator.py  # Gen 1 damage formula
│   │   ├── catch_calculator.py   # Gen 1 catch rate
│   │   ├── experience_calculator.py  # Level/XP curves
│   │   └── trainer.py            # Trainer data
│   ├── items/                    # Item system
│   │   ├── bag.py                # Inventory management
│   │   ├── item.py               # Item data
│   │   └── item_effects.py       # Item usage logic
│   └── ui/                       # UI components
│       ├── dialog_box.py         # NPC dialog rendering
│       ├── battle_menu.py        # Battle UI
│       └── move_menu.py          # Move selection
├── data/
│   ├── pokemon/species.yaml      # All 151 Gen 1 Pokemon
│   ├── moves/moves.yaml          # All 165 Gen 1 moves
│   ├── encounters/               # Wild encounter tables
│   ├── items/                    # Item definitions
│   └── types/type_chart.yaml     # Type effectiveness
├── assets/
│   ├── maps/                     # TMX map files and tilesets
│   └── sprites/pokemon/          # Pokemon sprites (302 files)
├── scripts/
│   └── hydrate_data.py           # PokéAPI data fetcher
├── saves/                        # Save files (created at runtime)
└── tests/                        # Unit tests
```

## Development Roadmap

### Phase 1: Core Engine ✅ COMPLETE
- Basic game loop with state management
- Input handling and rendering pipeline
- Window opens at 480x432 with Game Boy colors

### Phase 2: Map Rendering ✅ COMPLETE
- Tile-based map system
- Map loading from JSON
- Camera/viewport system
- Multi-layer rendering (ground, decorations, collision)
- Pallet Town map data created

### Phase 3: Player Movement ✅ COMPLETE
- Player sprite (yellow circle placeholder)
- Grid-based movement with smooth interpolation
- Collision detection against map collision layer
- Camera follows player
- Movement respects building/water/tree boundaries

### Phase 4: Map Transitions ✅ COMPLETE
- Warp points between maps
- Map switching
- Player repositioning after warps
- Route 1 map

### Phase 5: NPCs and Dialog ✅ COMPLETE
- NPC sprites and collision
- Dialog box system
- Text rendering
- Interaction system (press Z near NPCs)

### Phase 6: Battle System Foundation ✅ COMPLETE
- Wild encounter system
- Battle state with authentic Pokemon Yellow UI
- Gen 1 damage calculation (STAB, type effectiveness, random factor)
- Turn-based battle flow
- All 151 Gen 1 Pokemon with learnsets
- All 165 Gen 1 moves
- Pokemon sprites from PokéAPI

### Phase 7: Advanced Battle Mechanics ✅ COMPLETE
- ✅ Battle menu system (FIGHT/ITEM/PKM/RUN)
- ✅ Move selection UI
- ✅ Status effects (paralysis, sleep, poison, burn, freeze)
- ✅ Stat changes and accuracy/evasion
- ✅ Experience and leveling with move learning
- ✅ Pokemon catching mechanics
- ✅ Trainer battles

### Phase 8: Advanced Features (In Progress)
- ✅ Title menu (Continue/New Game/Option)
- ✅ Start menu (Pokemon, Bag, Save)
- ✅ Party management screen
- ✅ Inventory system
- ✅ Save/Load functionality (stored in `saves/save.json`)
- ✅ Pokedex
- ⏳ Building interiors (door warps)
- ⏳ NPC movement/AI
- ⏳ Advanced dialog features (typewriter, branching)
- ⏳ Remaining item types (TMs/HMs, key items, repels)

## What You Can Do Right Now

When you run the game, you can:
1. **Explore Pallet Town and Route 1** - Walk around with smooth movement and camera following
2. **Warp between maps** - Use the warp zones at map edges to transition between areas
3. **Battle Wild Pokemon** - Encounter random Pokemon on grass tiles
4. **Battle Trainers** - Interact with NPC trainers for battles
5. **Catch Pokemon** - Use Poké Balls to catch wild Pokemon
6. **Manage your party** - View your Pokemon in the party screen
7. **Use items** - Access your inventory from the Start menu
8. **Check Pokedex** - View caught and seen Pokemon
9. **Save/Load** - Manually save your progress (stored in `saves/save.json`)

## Technical Details

- **Display**: 160x144 native resolution (Game Boy accurate, no scaling)
- **Tile Size**: 8x8 pixels with 16x16 metatile collision grid
- **Frame Rate**: 60 FPS with smooth interpolation
- **Architecture**: State machine with clean separation of concerns
- **Map Format**: TMX files (Tiled editor compatible)
- **Data Format**: YAML for Pokemon/moves/encounters, JSON for game state
- **Sprites**: PokéAPI for Pokemon (302 sprites), Game Boy-style tilesets for environment
- **Battle System**: Authentic Gen 1 mechanics with full accuracy/critical hit/status system

## Testing

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src
```

## Documentation

- **`PROJECT_OVERVIEW.md`** - High-level project overview, feature list, and current status
- **`MAP_SYSTEM.md`** - Detailed guide to creating and editing maps with Tiled
- **`IMPLEMENTATION_PLAN.md`** - Detailed architecture and phase-by-phase implementation plan
- **`CLAUDE.md`** - Development guidelines and code standards

## License

This is a fan project for educational purposes. Pokemon is © Nintendo/Game Freak.
