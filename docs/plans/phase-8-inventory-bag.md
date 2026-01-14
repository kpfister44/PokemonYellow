# Phase 8 Plan: Inventory/Bag + Item Effects

## Scope
- Implement Gen 1 Yellow bag behavior with a single ordered list.
- Enforce capacity limits (20 slots) and stack limits (99 per item).
- Support pickups only (no shops or trainer rewards yet).
- Implement item effects that are supported by existing systems.
- Stub unsupported items as unusable with clear messaging.
- Integrate in overworld and battle.
- Prepare data pipeline using PokeAPI with Yellow-only catalog/order.

## Data + Hydration
1. Add a curated Yellow item list (name + order) to drive inclusion and ordering.
2. Extend `scripts/hydrate_data.py` to fetch item data for that list.
3. Store results in `data/items/items.yaml` with fields:
   - id, name, category, pocket, attributes
   - cost
   - effect text (English)
   - flavor text (Yellow, fallback Red/Blue)
   - machine info (TM/HM)
   - flags: usable_in_battle, usable_in_overworld, countable

## Runtime Data Model
1. Add item data model + loader for `data/items/items.yaml`.
2. Add bag inventory class:
   - single ordered list
   - capacity 20 slots
   - stack limit 99
   - non-countable items take one slot per item

## Item Effects
Supported now:
- HP healing (Potion, Super/Hyper/Max, Fresh Water, Soda Pop, Lemonade)
- Status cures (Antidote, Burn Heal, Ice Heal, Awakening, Paralyze Heal, Full Heal)
- Revives (Revive, Max Revive)
- PP restore (Ether/Max Ether, Elixir/Max Elixir)
- Battle stat boosts (X Attack/Defense/Speed/Special/Accuracy, Guard Spec, Dire Hit)
- Pokeballs (Poke/Great/Ultra/Master/Safari) via existing catch logic

Stub for later (unusable now):
- TMs/HMs
- Evolution stones
- Repels
- Key items requiring new systems
- Vitamins/stat experience

## UI + States
1. Add Bag UI state for overworld and battle contexts.
2. Overworld: Start menu ITEM opens bag; items can target any party member when applicable.
3. Battle: ITEM opens bag filtered to battle-usable items.
4. If item needs a target, reuse party selection flow.

## Pickups
1. Extend map JSON with `items` list (id, tile position, item id).
2. Add a pickup entity renderer.
3. On interaction, add to bag if space allows and mark collected for the session.

## Testing
- Bag capacity, stack limits, and ordering
- Healing/status/revive/PP restore effects
- Battle item use filtering and consumption

## Execution
1. Implement data/hydration changes and re-run hydration.
2. Add data model + bag inventory.
3. Add supported item effects + stubs for unsupported.
4. Integrate bag UI and battle/overworld usage.
5. Add pickups.
6. Add tests and run `uv run pytest`.
