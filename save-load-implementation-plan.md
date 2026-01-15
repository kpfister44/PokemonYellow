# Save/Load Implementation Plan

## Goals

- Add a Gen 1 style title menu overlay with CONTINUE/NEW GAME/OPTION.
- Implement save/load for party, bag, map, position, and flags.
- Use JSON save data stored in `saves/`.
- Preserve future extensibility with a versioned save schema.
- Match Gen 1 behavior (manual save from in-game menu only).

## Assumptions

- Single save slot (Gen 1 behavior).
- Player name is hardcoded as "PLAYER" for now.
- Flags are schema-first with a small active subset and placeholders for future use.

## Save Data Schema (v1)

Structure (not final code, just field intent):

- version: integer
- player:
  - name: string ("PLAYER")
  - direction: string (up/down/left/right)
- overworld:
  - map_path: string (e.g., data/maps/pallet_town.json)
  - x: int (tile coordinate)
  - y: int (tile coordinate)
- party: list of Pokemon objects
- bag: list of bag entries in acquisition order
- flags:
  - defeated_trainers: list of NPC ids
  - collected_items: list of pickup keys (map_name:pickup_id)
  - reserved:
    - badges: list
    - story: dict
    - pokedex_seen: list
    - pokedex_caught: list

## Serialization Scope

Pokemon serialization must be full fidelity:

- species_id
- level
- IVs (attack/defense/speed/special/hp)
- stats (or recompute from IVs + level)
- current_hp
- moves (list)
- move_pp (current and max for each move)
- status and status_turns
- stat_stages
- experience and exp_to_next_level

Bag serialization:

- list of entries with item_id + quantity
- preserve acquisition order

Player serialization:

- tile coordinates
- direction

Flags serialization:

- defeated trainer NPC ids
- collected item pickup keys
- reserved placeholder sections for future flags

## Implementation Steps (TDD)

### 1) Add Save/Load Data Types

- Create a save module to define SaveData schema and read/write helpers.
- Add to_dict/from_dict methods for:
  - Pokemon
  - Party
  - Bag
  - Player
- Ensure SaveData versioning is present and validated on load.

Tests:
- Failing test for round-trip save/load of a Pokemon with non-default IVs, PP, status, and stat stages.
- Failing test for Party round-trip preserving order and content.
- Failing test for Bag round-trip preserving quantities and order.
- Failing test for SaveData round-trip with flags and map/position.

### 2) Add Save File Storage

- Create `saves/` directory on first save if missing.
- Save to a single known filename (e.g., `saves/save.json`).
- Load should error with clear message if file missing or invalid.

Tests:
- Failing test for save file creation when directory does not exist.
- Failing test for load error handling when file is missing or invalid JSON.

### 3) Title Menu State (Startup Overlay)

- Add TitleMenuState with Gen 1 overlay layout:
  - CONTINUE (disabled if no save file)
  - NEW GAME
  - OPTION
- It should be the initial state in `src/main.py`.
- Selecting NEW GAME starts a fresh OverworldState.
- Selecting CONTINUE loads save and then starts OverworldState.

Tests:
- Failing test for Continue option disabled when save does not exist.
- Failing test for Continue option enabled when save exists.

### 4) Integrate Save Into In-Game Start Menu

- Wire SAVE option in StartMenuState:
  - Only available in overworld.
  - Writes SaveData constructed from current OverworldState.
- Confirm it does not auto-load and does not auto-save on exit.

Tests:
- Failing test that Save option writes file and updates save existence.

### 5) Load Application to Overworld

- On load, create OverworldState with map path and player position.
- Apply loaded party, bag, and flags after map load:
  - Set collected_items set.
  - Mark trainer NPCs defeated.

Tests:
- Failing test that defeated trainers remain defeated after load.
- Failing test that collected items are removed after load.

## Open Risks

- Need to confirm how NPC ids are assigned in map data to ensure stable trainer defeat tracking.
- Need to confirm pickup ids are stable per map and match collected_items keys.
- Some save data (like status conditions and stat stages) has to match existing data structures exactly.

## Done Criteria

- Title menu appears at boot and matches Gen 1 overlay layout.
- Continue is disabled if no save exists.
- Save writes to `saves/save.json`.
- Load restores map, position, party, bag, and flags exactly.
- Save data schema is versioned and future-extensible.

