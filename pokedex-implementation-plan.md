# Pokedex Implementation Plan (Phase 8)

## Goals
- Implement the Gen 1 Pokemon Yellow Pokedex with Yellow list order (1–151) and visibility rules.
- Add start menu entry that opens the Pokedex.
- Persist seen/caught flags via save data.
- Seed starter as seen/caught on new game.

## UX References
- Main list screen: matches provided Yellow screenshot (list of entries, right-side submenu).
- Entry screen: matches provided Yellow screenshot (sprite, category, height/weight, entry text).

## Visibility Rules (Per Kyle)
- If seen: show full entry details (same as caught).
- If unseen: show “?????” in list and block entry details (unknown screen or no entry).

## Data Model
- Store `pokedex_seen` and `pokedex_caught` as **species IDs** (e.g., "pikachu") to align with PokéAPI data.
- Display list order by species `number` (1–151) from `data/pokemon/species.yaml` via `SpeciesLoader`.

## Files to Add
- `src/states/pokedex_state.py`
  - Owns list/detail state and navigation (up/down/A/B).
  - Bridges player save flags and UI component.
- `src/ui/pokedex_screen.py`
  - Renders list view and entry view.
  - Provides pure logic helpers for ordering and visibility (to unit test without pygame).

## Files to Update
- `src/states/start_menu_state.py`
  - Wire “POKéDEX” to push `PokedexState`.
- `src/states/title_menu_state.py`
  - On NEW GAME, seed `pokedex_seen` and `pokedex_caught` with starter species ID.
- `src/states/overworld_state.py`
  - Accept/store `pokedex_seen` and `pokedex_caught` and expose them for save/UI.
- `src/save/save_data.py`
  - Ensure `pokedex_seen`/`pokedex_caught` round-trip through `reserved_flags`.
  - Keep JSON as lists; provide set access in code.

## UI Rendering Details
- List view:
  - Render 1–151 in dex order.
  - If seen: show name and number (padded to 3 digits).
  - If unseen: show number and “?????” like Yellow.
  - Cursor arrow and scrolling behavior similar to `BagScreen`.
- Entry view:
  - If seen/caught: render sprite, name, category, height/weight, dex number, and `pokedex_entry`.
  - If unseen: block entry detail or show unknown placeholder.

## Save/Load Integration
- Save: include `pokedex_seen` and `pokedex_caught` in `reserved_flags`.
- Load: default to empty lists when missing.
- Starter on New Game: add starter ID ("pikachu") to both sets.

## TDD Plan
1. Add failing tests for:
   - SaveData round-trip for `pokedex_seen`/`pokedex_caught`.
   - Dex ordering logic by species number.
   - Visibility logic (unseen vs seen vs caught).
2. Run tests to confirm failure: `uv run pytest`.
3. Implement minimal code to pass tests.
4. Re-run tests to confirm success.
5. Refactor if needed while keeping tests green.

## Open Dependencies (Resolved)
- UI reference provided by Kyle (two Yellow screenshots).
- Visibility: seen shows full details.
- Storage: species IDs (PokéAPI format).
