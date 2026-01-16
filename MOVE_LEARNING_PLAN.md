# Plan: Move Learning + EXP/Level-Up (Gen 1 Yellow)

## Goals
- Implement Gen 1 EXP gain + level-up flow (wild/trainer), including split EXP.
- Implement move learning at level-up with 4-move limit and forget/replace flow.
- Match Gen 1 Yellow message phrasing and sequencing.

## Plan
1. Review existing EXP/level-up logic and battle victory flow; note Gen 1 mismatches.
2. Add logic-only pytest coverage for:
   - EXP split across participants (no EXP All yet)
   - Multi-level-ups in one gain
   - Auto-learn with fewer than 4 moves
   - Replace/skip with 4 moves
   - Already-known move behavior
   - Gen 1 HP delta on level-up
3. Implement core logic in battle/experience/pokemon:
   - Gen 1 EXP math and trainer multiplier
   - Per-participant EXP distribution
   - Multi-level leveling loop
   - Learnset processing in YAML order
   - Move add/replace + PP handling
   - Gen 1 HP current increase on level-up
4. Implement post-battle move-learning flow:
   - Add forget-move menu UI (player moves only)
   - Pause battle flow, lock input during dialog
   - Use Gen 1 Yellow message strings
5. Run `uv run pytest`, fix failures, update docs (e.g., `PROJECT_OVERVIEW.md`) if needed.

## Notes
- EXP All is not in scope; design should allow future integration.
- Move-learning prompts and messages should be verbatim Gen 1 Yellow text.
