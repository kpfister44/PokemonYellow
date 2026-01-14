# PR: Phase 8 Inventory/Bag + Item Effects (Partial)

## Summary
Implements a Gen 1 Yellow-style bag with ordered slots, capacity limits, and core item effects. Adds item data hydration from PokeAPI using a curated Yellow item list, integrates bag usage in overworld and battle, and introduces item pickups. Unsupported items are present but unusable until their systems are built.

## Key Changes
- **Data**: Hydrates item data (`data/items/items.yaml`) using `data/items/yellow_item_list.yaml`.
- **Bag Core**: New bag inventory with slot limit (20), stack limit (99), and countable logic.
- **Item Effects**: Supports healing/status cures/revive/balls/X stat items. Others return a "Can't use that here." result.
- **UI/States**: Bag UI and state for overworld and battle usage; party selection for item targets.
- **Pickups**: Map item pickups with a sample potion in Pallet Town.
- **Tests**: Added bag and item effect tests plus start menu updates.

## Supported Item Effects
- HP healing: Potion/Super/Hyper/Max, Fresh Water, Soda Pop, Lemonade
- Status cures: Antidote, Burn Heal, Ice Heal, Awakening, Paralyze Heal, Full Heal
- Revives: Revive, Max Revive
- Balls: Poke/Great/Ultra/Master/Safari (catch flow)
- X stat items: X Attack/Defense/Speed/Special

## Not Implemented (Present but Unusable)
- TMs/HMs
- Evolution stones
- Repels
- Key items (Town Map, Bicycle, etc.)
- Vitamins/stat experience
- PP restores
- X Accuracy, Guard Spec, Dire Hit

## Files of Interest
- `scripts/hydrate_data.py`
- `data/items/yellow_item_list.yaml`
- `data/items/items.yaml`
- `src/items/bag.py`
- `src/items/item_effects.py`
- `src/states/bag_state.py`
- `src/ui/bag_screen.py`
- `src/states/battle_state.py`
- `src/states/overworld_state.py`
- `data/maps/pallet_town.json`

## Tests
- `uv run pytest`

## Known Issues / Risks
- PokeAPI does not expose several Yellow items (coin, exp-all, item-finder, pokedex); they are excluded.
- Hydration still logs existing 404s for some encounter areas; unchanged behavior.

## Follow-ups
- Add PP item move-selection flow.
- Implement systems for key items, evolution stones, and Repel.
- Replace placeholder pickup sprite with actual asset.
