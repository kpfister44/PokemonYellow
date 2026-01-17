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

2026-01-17
- Added pokeyellow .blk conversion utilities and CLI export script.
- Added unit test for block expansion into tile grids.
- Generated a Pallet Town JSON export at /tmp/pallet_town_from_blk.json for verification.
