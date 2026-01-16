# Battle Mechanics Fix Plan

## Goals
- Make battle flow sequential like Gen 1 Pokemon Yellow.
- Add minimal attack animations and HP bar tick animations for damage.
- Ensure enemy attack waits for player HP bar tick completion.
- Keep timing consistent with existing HP bar tick rates.

## Current Behavior (Observed)
- Both player and enemy HP drop immediately after move selection.
- Messages appear after HP changes, so visuals and narration are out of order.

## Target Gen 1 Sequence (Per Turn)
1. Show "X used MOVE!"
2. Play attack animation for attacker.
3. Animate defender HP bar tick down to new HP.
4. Show secondary messages (critical, multi-hit, status, effectiveness).
5. If defender faints, run faint flow before next action.
6. Enemy attack follows the same sequence, only after player HP tick completes.

## Animation Scope
- Minimal attack animation using existing renderer:
  - Attacker sprite shake or brief flash (1 short cycle).
  - No new assets required.
- HP tick uses existing `HpBarDisplay` timing (damage direction).

## Implementation Steps
1. Map current phases and message queue handling in `src/states/battle_state.py`.
2. Define explicit per-attack sub-phases:
   - `attack_message`, `attack_animation`, `hp_tick`, `post_attack_messages`.
3. Refactor `_execute_player_attack` to stage actions rather than applying all damage immediately.
   - Precompute damage and outcome messages.
   - Apply damage when entering the HP tick phase.
4. Add rendering hooks for the attack animation phase.
5. Gate enemy action on completion of player HP tick animation.
6. Ensure fainting flow interrupts remaining actions as in Gen 1.

## Tests (TDD)
- Add battle flow tests that assert:
  - HP is unchanged until the HP tick phase begins.
  - Enemy attack does not start until player HP tick completes.
  - Message ordering follows Gen 1 sequence for single-hit, multi-hit, and critical cases.
- Run targeted tests after each change.

## Files Likely Touched
- `src/states/battle_state.py`
- `src/battle/hp_bar_display.py` (if timing or hooks needed)
- `tests/` (new or updated battle flow tests)

## Notes
- Multi-hit and critical messaging must match Gen 1 ordering.
- HP tick timing uses the existing item heal tick speed, reversed for damage.
