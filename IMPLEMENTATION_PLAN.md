# Pokemon Yellow PyGame Recreation - Implementation Plan

## Project Overview
This project recreates Pokemon Yellow using PyGame with pixel-perfect accuracy to the original Game Boy game. We're building incrementally, starting with an MVP of core movement and 2 maps, then expanding to include the full battle system, Pokemon roster, and complete game features.

## Technical Specifications

### Display & Graphics
- **Base Resolution**: 160x144 pixels (Game Boy screen size)
- **Display Scaling**: 3x scale → 480x432 pixel window
- **Tile Size**: 16x16 pixels
- **Frame Rate**: 60 FPS
- **Graphics Source**: PokeAPI for Pokemon sprites, Gen 1 tilesets for environment

### Architecture
- **State Machine**: Clean separation between Overworld, Battle, and Menu states
- **Grid-Based Movement**: 16x16 tile grid with smooth pixel interpolation
- **Data-Driven**: All game content (Pokemon, moves, maps) in JSON/YAML
- **Layer-Based Rendering**: Background → Entities → UI

## Project Structure

```
pokemon_yellow/
├── src/
│   ├── main.py                      # Entry point
│   ├── engine/
│   │   ├── constants.py             # Game constants (resolution, tile size, colors)
│   │   ├── game.py                  # Main game loop and state manager
│   │   ├── input.py                 # Keyboard input handling
│   │   └── renderer.py              # Rendering pipeline with sprite caching
│   ├── states/
│   │   ├── base_state.py            # Abstract state interface
│   │   ├── overworld_state.py       # Overworld game state
│   │   ├── battle_state.py          # Battle state (post-MVP)
│   │   └── menu_state.py            # Menu state (post-MVP)
│   ├── overworld/
│   │   ├── tile.py                  # Tile class with collision properties
│   │   ├── map.py                   # Map loading and rendering
│   │   ├── camera.py                # Viewport/camera system
│   │   ├── entity.py                # Base entity class
│   │   ├── player.py                # Player character
│   │   └── npc.py                   # NPCs (post-MVP)
│   ├── battle/
│   │   ├── battle_engine.py         # Battle logic (post-MVP)
│   │   ├── pokemon.py               # Pokemon instances
│   │   ├── move.py                  # Move definitions and effects
│   │   └── damage_calc.py           # Gen 1 damage formula
│   ├── data/
│   │   ├── data_loader.py           # JSON/YAML loading utilities
│   │   └── species.py               # Pokemon species data structures
│   └── ui/
│       ├── textbox.py               # Text rendering utilities
│       ├── dialog.py                # Dialog boxes (post-MVP)
│       └── menu.py                  # Menu rendering (post-MVP)
├── data/
│   ├── maps/
│   │   ├── pallet_town.json
│   │   └── route_1.json
│   ├── pokemon/
│   │   └── species.yaml
│   ├── moves/
│   │   └── moves.yaml
│   └── types/
│       └── effectiveness.yaml
├── assets/
│   ├── sprites/
│   │   ├── player/
│   │   ├── pokemon/
│   │   ├── npcs/
│   │   └── tiles/
│   └── fonts/
├── tests/
│   ├── test_map.py
│   ├── test_player.py
│   └── test_data_loader.py
├── pyproject.toml
└── README.md
```

## MVP Implementation (Phase 1-4)

### Phase 1: Core Engine Setup ✅ COMPLETE
**Goal**: Get a window running with basic game loop

**Files Created**:
1. ✅ `pyproject.toml` - uv project configuration with pygame dependency
2. ✅ `src/engine/constants.py` - Screen resolution, tile size, FPS, keybindings
3. ✅ `src/engine/renderer.py` - PyGame display initialization, sprite loading
4. ✅ `src/engine/input.py` - Keyboard event handling and action mapping
5. ✅ `src/states/base_state.py` - Abstract state interface (update/render/handle_input)
6. ✅ `src/engine/game.py` - Main game loop with state management
7. ✅ `src/main.py` - Entry point

**Success Criteria**: ✅ ALL COMPLETE
- ✅ Window opens at 480x432 resolution
- ✅ Game loop runs at 60 FPS
- ✅ Keyboard input is detected
- ✅ Window can be closed properly

### Phase 2: Map Rendering System ✅ COMPLETE
**Goal**: Display a static map with tiles

**Files Created**:
1. ✅ `src/overworld/tile.py` - Tile class with collision and sprite properties
2. ✅ `src/overworld/map.py` - Load map from JSON, render tile layers
3. ✅ `src/overworld/camera.py` - Viewport management with boundary checks
4. ✅ `src/states/overworld_state.py` - Overworld state implementation
5. ✅ `src/data/data_loader.py` - JSON/YAML loading with caching
6. ✅ `data/maps/pallet_town.json` - First map data (tiles, collision, warps)
7. ✅ Updated `src/main.py` to use OverworldState

**Success Criteria**: ✅ ALL COMPLETE
- ✅ Pallet Town map renders correctly with colored placeholder tiles
- ✅ Camera system works (shows correct portion of map)
- ✅ Multiple tile layers supported (ground, decorations, collision)
- ✅ Collision data loaded properly
- ✅ Warp point data structure ready
- ✅ Camera can be controlled with arrow keys for testing

### Phase 3: Player Movement ← CURRENT PHASE
**Goal**: Move player around the map with collision

**Files to Create**:
1. `src/overworld/entity.py` - Base entity class (position, sprite, animation)
2. `src/overworld/player.py` - Player movement, collision detection, animation
3. Player sprite assets in `assets/sprites/player/`

**Success Criteria**:
- Player sprite renders on map
- 4-direction movement (arrow keys)
- Smooth pixel interpolation between tiles
- Collision detection prevents walking through walls
- Walking animation cycles work correctly

### Phase 4: Map Transitions
**Goal**: Connect multiple maps with warp points

**Files to Create**:
1. `data/maps/route_1.json` - Second map
2. Update `src/overworld/map.py` for warp handling
3. Update `src/states/overworld_state.py` for map switching

**Success Criteria**:
- Player can walk from Pallet Town to Route 1
- Map switches smoothly
- Player spawns at correct position after warp
- Camera adjusts to new map boundaries

## Post-MVP Phases (Phase 5-8)

### Phase 5: NPCs and Dialog System
- NPC sprites and movement patterns
- Dialog boxes with typewriter effect
- Interaction system (face NPC, press A button)
- Dialog branching

### Phase 6: Battle System Foundation
- Pokemon data structures (stats, moves, types)
- Load Pokemon from YAML
- Battle state implementation
- Basic battle UI
- Wild encounter system (grass tiles trigger battles)

### Phase 7: Battle Mechanics
- Turn-based battle engine
- Gen 1 accurate damage calculation
- Move effects (damage, status, stat changes)
- Type effectiveness chart
- Battle AI for opponent Pokemon
- Experience and leveling system
- Pokemon catching mechanics

### Phase 8: Advanced Features
- Start menu (Pokemon, Bag, Save, Exit)
- Pokemon party management screen
- Inventory/Bag system
- Item effects
- Save/Load system
- Pokedex

## Key Technical Decisions

### Input Mapping
- **Arrow Keys**: Movement (↑↓←→)
- **Z Key**: A button (confirm, interact)
- **X Key**: B button (cancel, run)
- **Enter**: Start button (menu)
- **Shift**: Select button (future use)

### Map Data Format (JSON)
```json
{
  "width": 10,
  "height": 9,
  "tileset": "pallet_town_tileset",
  "layers": {
    "ground": [[...], [...]],
    "decorations": [[...], [...]],
    "collision": [[0,0,1,1,...], [...]]
  },
  "warps": [
    {"x": 5, "y": 8, "target_map": "route_1", "target_x": 5, "target_y": 0}
  ]
}
```

### Pokemon Data Format (YAML)
```yaml
species:
  - id: 25
    name: "Pikachu"
    types: ["electric"]
    base_stats:
      hp: 35
      attack: 55
      defense: 40
      special: 50
      speed: 90
    learnset:
      - level: 1
        move: "thundershock"
      - level: 9
        move: "thunder_wave"
```

### Gen 1 Battle Mechanics
- Stat calculation with DVs and Stat Experience
- Gen 1 damage formula (with critical hit mechanics)
- Gen 1 type chart (Psychic has no weaknesses)
- Status conditions (PAR, SLP, FRZ, BRN, PSN)
- No special/physical split (type-based)

## Testing Strategy

### Unit Tests
- Damage calculation accuracy
- Type effectiveness lookups
- Stat calculations
- Move effect application

### Integration Tests
- Map loading and rendering
- Player collision detection
- Map transitions
- Battle state transitions

### Manual Testing Checklist
- [ ] Player can walk in all 4 directions
- [ ] Player stops at walls and obstacles
- [ ] Walking animation plays correctly
- [ ] Map transitions work both ways
- [ ] Camera stays within map bounds
- [ ] Game runs at consistent 60 FPS

## Performance Considerations

### Optimization Strategies
1. **Sprite Caching**: Load sprites once, reuse across frames
2. **Camera Culling**: Only render tiles visible in viewport
3. **Entity Updates**: Only update entities near player
4. **Dirty Rectangles**: Only redraw changed screen regions (future optimization)

### Memory Management
- Unload unused map data when switching maps
- Limit loaded sprite sheets
- Cache frequently accessed data (type chart, move data)

## Development Workflow

1. **Create Feature Branch**: `git checkout -b feature/phase-N`
2. **Implement Files**: Follow the critical files list for each phase
3. **Test Continuously**: Run game after each major change
4. **Commit Frequently**: Small, atomic commits
5. **Manual Testing**: Verify success criteria before moving to next phase

## Resources & References

### Sprites
- **Pokemon**: PokeAPI (https://pokeapi.co/docs/v2#pokemon)
- **Tilesets**: Research Gen 1 tilesets from pokeemerald, pokecrystal, or fan projects
- **Player/NPCs**: Fan sprite repositories or create placeholders

### Gen 1 Game Mechanics
- Bulbapedia Gen 1 mechanics documentation
- Pokemon Showdown damage calculator
- Disassembly projects (pokered on GitHub)

### Tools
- **uv**: Python package manager
- **PyGame**: Game framework
- **Tiled Map Editor**: For creating map JSON (optional)

## Next Steps

Starting with **Phase 1: Core Engine Setup**. We'll create the foundational game loop, rendering pipeline, and input system to get a window running before adding any game-specific logic.
