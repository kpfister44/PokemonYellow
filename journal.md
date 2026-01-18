Journal
=======

2025-01-05
- Created journal for tracking decisions and work notes.
- Added item pickup collision and test coverage.
- Implemented HP bar display ticking and tests.
- Added party screen HP ticking and item-use animation flow.
- Skipped party animation for active battle Pokemon item use.
- Updated item pickup dialog text to match Yellow phrasing.
- Updated docs for completed bag/item system.

2026-01-15
- Added save data schema and JSON storage helpers.
- Added serialization for Pokemon, Party, Bag, and Player with tests.
- Integrated title menu startup flow and save handling in start menu.
- Persisted defeated trainer and map path state for save/load.
- Added save confirmation dialog and title menu cursor rendering.
- Added Pokedex list/detail screens with start menu entry.
- Persisted pokedex seen/caught flags and seeded starter on new game.
- Hydrated Pokedex genus/height/weight data from PokéAPI.
- Added Pokedex entry paging and right-side menu cursor actions.
- Marked pokedex seen/caught during battles and added INFO no-data dialog.
- Fixed battle flow to advance after faint animation completes.
- Ensured party Pokemon always populate pokedex flags on load.

2026-01-16
- Read PROJECT_OVERVIEW.md and captured current phase, systems, and data layout.
- Documented battle mechanics fix plan in battle-mechanics-fix.md.
- Implemented sequential battle flow with attack animations and HP tick phases.
- Added logic-only tests for battle sequencing and shared battle test helpers.
- Fixed battle bag cancel to restore menu and added test coverage.
- Fixed battle party cancel to restore menu and added test coverage.
- Added run escape logic and pokeball catch animation sequencing with ball sprites.
- Hydrated item sprites from PokéAPI and extended item metadata with sprite paths.
- Added two Poke Ball pickups to Pallet Town for catch testing.
- Updated PROJECT_OVERVIEW.md catch flow description.
- Implemented Gen 1 EXP split and multi-level-up flow with move learning prompts.
- Added move learning logic in Pokemon (last-4 moves, replace/skip) and battle flow integration.
- Added logic-only tests for EXP and move learning plus updated trainer victory tests.
- Added yes/no and forget-move menus for level-up move replacement flow.
- Updated PROJECT_OVERVIEW.md to reflect move learning completion and next steps.

2026-01-18
- Migrated map system to TMX via pytmx with cached lower/fringe layers and object parsing.
- Switched resolution to 320x288, added UI_SCALE=2, and scaled battle/menus/UI layout.
- Updated overworld to use TMX collisions/grass properties, warp objects, and Y-sorted rendering.
- Added TMX fixture maps and tests for map loading, collisions, grass, and object spawns.
- Removed legacy JSON maps and updated save/menu defaults to assets/maps TMX paths.

2026-01-18 (Session 2)
- Integrated pylletTown tilesets (32x32 Game Boy-style graphics) from GitHub.
- Copied pallet_town.tmx and player_house.tmx from pylletTown with real tile graphics.
- Updated MapManager._is_truthy() to handle empty string as truthy (pylletTown convention).
- Added _build_tile_warps() to parse tile-based warps from `entry` property.
- Added player_start attribute from `playerStart` tile property.
- Updated OverworldState to use map's player_start when coords are -1,-1.
- Fixed SCALE_FACTOR from 3 to 2 (was too zoomed in with 32x32 tiles).
- Deleted old save file that referenced removed JSON map paths.
- Updated PROJECT_OVERVIEW.md with new resolution/map system details.
- Added Phase 10 map creation guide to IMPLEMENTATION_PLAN.md for future agents.
- Phase 9 complete: Maps now render with authentic Pokemon-style graphics.
