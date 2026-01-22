# Pokemon Yellow - PyGame Recreation

A pixel-perfect recreation of Pokemon Yellow using PyGame, built incrementally from movement system to full battle mechanics.

## Project Status

**Current Phase**: Phase 6 Complete - Battle System Foundation ✓
**Next Phase**: Phase 7 - Advanced Battle Mechanics

### Completed Features
- ✅ Core game loop with 60 FPS frame timing
- ✅ State machine architecture
- ✅ Input handling system (Arrow keys + Z/X/Enter)
- ✅ Rendering pipeline at native 160x144 resolution
- ✅ Sprite caching system
- ✅ Game Boy color palette
- ✅ Tile-based map system with multi-layer rendering
- ✅ Camera/viewport management with boundary checking
- ✅ JSON data loading for maps
- ✅ Pallet Town and Route 1 maps
- ✅ Map transitions via warp points
- ✅ Player sprite with grid-based movement
- ✅ Smooth pixel interpolation (8 frames per tile)
- ✅ Collision detection (tiles + NPCs)
- ✅ Camera follows player smoothly
- ✅ NPC interaction with dialog system
- ✅ Wild Pokemon encounters on grass tiles
- ✅ Authentic Pokemon Yellow battle UI with HP bars
- ✅ Turn-based battle system with Gen 1 damage calculation
- ✅ All 151 Gen 1 Pokemon with Yellow version learnsets
- ✅ All 165 Gen 1 moves with accurate stats
- ✅ Pokemon sprites (front and back) from PokéAPI

## Setup

### Requirements
- Python 3.11+
- uv package manager (globally installed)

### Installation

```bash
# Install dependencies
uv sync --all-extras

# Run the game
uv run python -m src.main

# (Optional) Re-fetch Pokemon data from PokéAPI
# Only needed if data files are missing or you want fresh data
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
pokemon_yellow/
├── src/
│   ├── engine/           # Core game engine
│   │   ├── constants.py  # Game constants
│   │   ├── game.py       # Main game loop
│   │   ├── input.py      # Input handling
│   │   └── renderer.py   # Rendering system
│   ├── states/           # Game states
│   │   ├── base_state.py        # State interface
│   │   └── overworld_state.py   # (Coming soon)
│   ├── overworld/        # Overworld system
│   ├── battle/           # Battle system (post-MVP)
│   ├── data/             # Data loading
│   └── ui/               # UI components
├── data/                 # Game data (maps, pokemon, moves)
├── assets/               # Graphics and fonts
└── tests/                # Unit tests
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

### Phase 7: Advanced Battle Mechanics (Completed)
- Battle menu system (FIGHT/ITEM/PKM/RUN)
- Move selection UI
- Status effects (paralysis, sleep, poison, burn, freeze)
- Stat changes and accuracy/evasion
- Experience and leveling
- Pokemon catching mechanics
- Trainer battles

### Phase 8: Advanced Features (In Progress)
- Title menu (Continue/New Game/Option)
- Start menu (Pokemon, Bag, Save)
- Party management screen
- Inventory system
- Save/Load functionality (stored in `saves/save.json`)
- Pokedex

## Technical Details

- **Display**: 160x144 native resolution (no scaling)
- **Tile Size**: 8x8 pixels (Game Boy standard)
- **Frame Rate**: 60 FPS
- **Architecture**: State machine with clean separation
- **Data Format**: JSON for maps, YAML for Pokemon/moves
- **Sprites**: PokeAPI for Pokemon, Gen 1 tilesets for environment

## Testing

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src
```

## Documentation

See `IMPLEMENTATION_PLAN.md` for detailed architecture and implementation plans.

## License

This is a fan project for educational purposes. Pokemon is © Nintendo/Game Freak.
