# Pokemon Yellow - PyGame Recreation

A pixel-perfect recreation of Pokemon Yellow using PyGame, built incrementally from movement system to full battle mechanics.

## Project Status

**Current Phase**: Phase 1 Complete - Core Engine ✓
**Next Phase**: Phase 2 - Map Rendering System

### Completed Features
- ✅ Core game loop with 60 FPS frame timing
- ✅ State machine architecture
- ✅ Input handling system (Arrow keys + Z/X/Enter)
- ✅ Rendering pipeline with 3x scaling (160x144 → 480x432)
- ✅ Sprite caching system
- ✅ Game Boy color palette

### In Progress
- Map rendering system
- Tile-based collision
- Player movement

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

### Phase 2: Map Rendering (In Progress)
- Tile-based map system
- Map loading from JSON
- Camera/viewport system
- Multi-layer rendering (ground, decorations, collision)

### Phase 3: Player Movement
- Player sprite and animation
- Grid-based movement with smooth interpolation
- Collision detection
- 4-direction walking animation

### Phase 4: Map Transitions
- Warp points between maps
- Map switching
- Player repositioning after warps

### Phase 5+: Advanced Features
- NPCs and dialog system
- Battle system with Gen 1 mechanics
- Pokemon data and moves
- Menu system
- Save/Load functionality

## Technical Details

- **Display**: 160x144 native resolution scaled 3x to 480x432
- **Tile Size**: 16x16 pixels (Game Boy standard)
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
