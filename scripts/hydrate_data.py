#!/usr/bin/env python3
# ABOUTME: Hydrates local Pokemon and move data from PokéAPI
# ABOUTME: Fetches Gen 1 Pokemon (1-151) with Yellow version data and downloads sprites

import requests
import yaml
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# Base URL for PokéAPI
POKEAPI_BASE = "https://pokeapi.co/api/v2"

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
POKEMON_DIR = DATA_DIR / "pokemon"
MOVES_DIR = DATA_DIR / "moves"
ENCOUNTERS_DIR = DATA_DIR / "encounters"
ITEMS_DIR = DATA_DIR / "items"
SPRITES_DIR = PROJECT_ROOT / "assets" / "sprites" / "pokemon"
ITEM_LIST_PATH = ITEMS_DIR / "yellow_item_list.yaml"

# Gen 1 constants
GEN1_POKEMON_COUNT = 151
GEN1_MOVE_IDS = range(1, 166)  # Gen 1 moves are IDs 1-165
GEN1_LOCATION_AREAS = [
    # Kanto routes (use "kanto-route-X-area" naming)
    "kanto-route-1-area", "kanto-route-2-area", "kanto-route-3-area", "kanto-route-4-area",
    "kanto-route-5-area", "kanto-route-6-area", "kanto-route-7-area", "kanto-route-8-area",
    "kanto-route-9-area", "kanto-route-10-area", "kanto-route-11-area", "kanto-route-12-area",
    "kanto-route-13-area", "kanto-route-14-area", "kanto-route-15-area", "kanto-route-16-area",
    "kanto-route-17-area", "kanto-route-18-area", "kanto-route-19-area", "kanto-route-20-area",
    "kanto-route-21-area", "kanto-route-22-area", "kanto-route-23-area", "kanto-route-24-area",
    "kanto-route-25-area",
    # Special areas
    "viridian-forest-area", "mt-moon-1f", "mt-moon-b1f", "mt-moon-b2f",
    "rock-tunnel-1f", "rock-tunnel-b1f", "power-plant-area",
    "pokemon-tower-3f", "pokemon-tower-4f", "pokemon-tower-5f", "pokemon-tower-6f", "pokemon-tower-7f",
    "seafoam-islands-1f", "seafoam-islands-b1f", "seafoam-islands-b2f", "seafoam-islands-b3f", "seafoam-islands-b4f",
    "pokemon-mansion-1f", "pokemon-mansion-2f", "pokemon-mansion-3f", "pokemon-mansion-b1f",
    "victory-road-1f-rb", "victory-road-2f-rb", "victory-road-3f-rb",
    "cerulean-cave-1f", "cerulean-cave-2f", "cerulean-cave-b1f",
    "digletts-cave-area", "safari-zone-center-area"
]

# Rate limiting
REQUEST_DELAY = 0.1  # 100ms between requests to be respectful

# Cache for fetched data to avoid duplicate requests
evolution_chain_cache = {}
growth_rate_cache = {}
item_category_cache = {}
machine_cache = {}


def fetch_json(url: str) -> Optional[Dict[str, Any]]:
    """Fetch JSON from URL with error handling and rate limiting."""
    try:
        time.sleep(REQUEST_DELAY)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        return None


def download_sprite(url: str, filepath: Path) -> bool:
    """Download sprite image to filepath."""
    try:
        time.sleep(REQUEST_DELAY)
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading sprite {url}: {e}")
        return False


def get_yellow_flavor_text(species_data: Dict[str, Any]) -> str:
    """Extract Yellow version Pokedex entry."""
    flavor_texts = species_data.get('flavor_text_entries', [])

    # Try to find Yellow version first
    for entry in flavor_texts:
        if entry.get('language', {}).get('name') == 'en':
            version = entry.get('version', {}).get('name')
            if version == 'yellow':
                # Clean up the text (remove newlines/form feeds)
                text = entry.get('flavor_text', '').replace('\n', ' ').replace('\f', ' ')
                return ' '.join(text.split())  # Normalize whitespace

    # Fallback to Red/Blue if Yellow not available
    for entry in flavor_texts:
        if entry.get('language', {}).get('name') == 'en':
            version = entry.get('version', {}).get('name')
            if version in ['red', 'blue']:
                text = entry.get('flavor_text', '').replace('\n', ' ').replace('\f', ' ')
                return ' '.join(text.split())

    return ""


def fetch_evolution_chain(chain_url: str) -> Dict[str, Any]:
    """Fetch and parse evolution chain."""
    if chain_url in evolution_chain_cache:
        return evolution_chain_cache[chain_url]

    chain_data = fetch_json(chain_url)
    if not chain_data:
        return {}

    def parse_chain(chain_link: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively parse evolution chain."""
        species_name = chain_link.get('species', {}).get('name')
        evolves_to = []

        for evolution in chain_link.get('evolves_to', []):
            evo_details = evolution.get('evolution_details', [{}])[0]
            evolves_to.append({
                'species': evolution.get('species', {}).get('name'),
                'trigger': evo_details.get('trigger', {}).get('name'),
                'min_level': evo_details.get('min_level'),
                'item': evo_details.get('item', {}).get('name') if evo_details.get('item') else None,
                'evolves_to': parse_chain(evolution)  # Recursive for 3-stage evolutions
            })

        return {
            'species': species_name,
            'evolves_to': evolves_to
        }

    result = parse_chain(chain_data.get('chain', {}))
    evolution_chain_cache[chain_url] = result
    return result


def get_yellow_learnset(pokemon_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract Yellow version learnset from Pokemon data."""
    learnset = []

    for move_entry in pokemon_data.get('moves', []):
        for version_detail in move_entry.get('version_group_details', []):
            version_group = version_detail.get('version_group', {}).get('name')

            # Yellow version data
            if version_group == 'yellow':
                learn_method = version_detail.get('move_learn_method', {}).get('name')

                # Include level-up and machine moves
                if learn_method in ['level-up', 'machine']:
                    level = version_detail.get('level_learned_at', 0)
                    move_name = move_entry.get('move', {}).get('name')

                    learnset.append({
                        'level': level,
                        'move': move_name,
                        'method': learn_method
                    })

    # Sort by level, then by method (level-up first)
    learnset.sort(key=lambda x: (x['level'], x['method'] != 'level-up'))
    return learnset


def fetch_growth_rate(growth_rate_url: str) -> str:
    """Fetch growth rate name."""
    if growth_rate_url in growth_rate_cache:
        return growth_rate_cache[growth_rate_url]

    growth_data = fetch_json(growth_rate_url)
    if not growth_data:
        return "medium"  # Default fallback

    rate_name = growth_data.get('name', 'medium')
    growth_rate_cache[growth_rate_url] = rate_name
    return rate_name


def get_english_name(entries: List[Dict[str, Any]]) -> str:
    """Extract English name from entries."""
    for entry in entries:
        if entry.get('language', {}).get('name') == 'en':
            return entry.get('name', '')
    return ""


def get_yellow_item_flavor_text(item_data: Dict[str, Any]) -> str:
    """Extract Yellow version flavor text (fallback to Red/Blue)."""
    flavor_texts = item_data.get('flavor_text_entries', [])

    for entry in flavor_texts:
        if entry.get('language', {}).get('name') == 'en':
            version_group = entry.get('version_group', {}).get('name')
            if version_group == 'yellow':
                text = entry.get('text', '').replace('\n', ' ').replace('\f', ' ')
                return ' '.join(text.split())

    for entry in flavor_texts:
        if entry.get('language', {}).get('name') == 'en':
            version_group = entry.get('version_group', {}).get('name')
            if version_group in ['red-blue']:
                text = entry.get('text', '').replace('\n', ' ').replace('\f', ' ')
                return ' '.join(text.split())

    return ""


def get_item_effect_text(item_data: Dict[str, Any]) -> str:
    """Extract English item effect text."""
    for entry in item_data.get('effect_entries', []):
        if entry.get('language', {}).get('name') == 'en':
            return entry.get('short_effect', '') or entry.get('effect', '')
    return ""


def fetch_item_category(category_url: str) -> Optional[Dict[str, Any]]:
    """Fetch and cache item category data."""
    if category_url in item_category_cache:
        return item_category_cache[category_url]

    category_data = fetch_json(category_url)
    if category_data:
        item_category_cache[category_url] = category_data
    return category_data


def fetch_machine(machine_url: str) -> Optional[Dict[str, Any]]:
    """Fetch and cache machine data."""
    if machine_url in machine_cache:
        return machine_cache[machine_url]

    machine_data = fetch_json(machine_url)
    if machine_data:
        machine_cache[machine_url] = machine_data
    return machine_data


def fetch_item_data(item_id: str) -> Optional[Dict[str, Any]]:
    """Fetch and process a single item."""
    print(f"🧰 Fetching Item {item_id}...")
    item_url = f"{POKEAPI_BASE}/item/{item_id}"
    item_data = fetch_json(item_url)

    if not item_data:
        return None

    attributes = [attr.get('name') for attr in item_data.get('attributes', [])]

    category_data = None
    category_url = item_data.get('category', {}).get('url')
    if category_url:
        category_data = fetch_item_category(category_url)

    pocket_name = None
    if category_data:
        pocket_name = category_data.get('pocket', {}).get('name')

    machines = []
    for machine_info in item_data.get('machines', []):
        machine_data = fetch_machine(machine_info.get('machine', {}).get('url'))
        if not machine_data:
            continue
        version_group = machine_data.get('version_group', {}).get('name')
        if version_group != 'yellow':
            continue
        machines.append({
            'machine_id': machine_data.get('id'),
            'move': machine_data.get('move', {}).get('name'),
            'version_group': version_group
        })

    item_entry = {
        'id': item_data.get('id'),
        'item_id': item_data.get('name'),
        'name': get_english_name(item_data.get('names', [])),
        'category': item_data.get('category', {}).get('name'),
        'pocket': pocket_name,
        'attributes': attributes,
        'cost': item_data.get('cost', 0),
        'effect': get_item_effect_text(item_data),
        'flavor_text': get_yellow_item_flavor_text(item_data),
        'machines': machines,
        'usable_in_battle': 'usable-in-battle' in attributes,
        'usable_in_overworld': 'usable-overworld' in attributes,
        'countable': 'countable' in attributes,
        'consumable': 'consumable' in attributes
    }

    return item_entry


def fetch_pokemon_species(pokemon_id: int) -> Dict[str, Any]:
    """Fetch and process a single Pokemon's data."""
    print(f"📦 Fetching Pokemon #{pokemon_id}...")

    # Fetch main Pokemon data
    pokemon_url = f"{POKEAPI_BASE}/pokemon/{pokemon_id}"
    pokemon_data = fetch_json(pokemon_url)

    if not pokemon_data:
        return None

    # Fetch species data
    species_url = f"{POKEAPI_BASE}/pokemon-species/{pokemon_id}"
    species_data = fetch_json(species_url)

    if not species_data:
        return None

    pokemon_name = pokemon_data.get('name')

    # Extract base stats
    stats_map = {
        'hp': 0,
        'attack': 0,
        'defense': 0,
        'special-attack': 0,  # In Gen 1, special-attack and special-defense are combined
        'special-defense': 0,
        'speed': 0
    }

    for stat in pokemon_data.get('stats', []):
        stat_name = stat.get('stat', {}).get('name')
        if stat_name in stats_map:
            stats_map[stat_name] = stat.get('base_stat', 0)

    # Gen 1 only has one "Special" stat
    special = stats_map['special-attack']  # They're the same in Gen 1

    # Extract types
    types = [t.get('type', {}).get('name') for t in pokemon_data.get('types', [])]

    # Get Yellow version learnset
    learnset = get_yellow_learnset(pokemon_data)

    # Get species-specific data
    pokedex_entry = get_yellow_flavor_text(species_data)
    capture_rate = species_data.get('capture_rate', 255)
    base_happiness = species_data.get('base_happiness', 70)
    gender_rate = species_data.get('gender_rate', -1)  # -1 = genderless

    # Get growth rate
    growth_rate_url = species_data.get('growth_rate', {}).get('url')
    growth_rate = fetch_growth_rate(growth_rate_url) if growth_rate_url else "medium"

    # Get evolution chain
    evo_chain_url = species_data.get('evolution_chain', {}).get('url')
    evolution_chain = fetch_evolution_chain(evo_chain_url) if evo_chain_url else {}

    # Get base experience (for XP yield when defeated)
    base_experience = pokemon_data.get('base_experience', 0)

    # Download sprites
    sprites = pokemon_data.get('sprites', {})
    front_sprite_url = sprites.get('front_default')
    back_sprite_url = sprites.get('back_default')

    sprite_paths = {}

    if front_sprite_url:
        front_path = SPRITES_DIR / f"{pokemon_id:03d}_{pokemon_name}_front.png"
        if download_sprite(front_sprite_url, front_path):
            sprite_paths['front'] = str(front_path.relative_to(PROJECT_ROOT))
            print(f"  ✅ Downloaded front sprite")

    if back_sprite_url:
        back_path = SPRITES_DIR / f"{pokemon_id:03d}_{pokemon_name}_back.png"
        if download_sprite(back_sprite_url, back_path):
            sprite_paths['back'] = str(back_path.relative_to(PROJECT_ROOT))
            print(f"  ✅ Downloaded back sprite")

    # Build species entry
    species_entry = {
        'id': pokemon_id,
        'name': pokemon_name.capitalize(),
        'types': types,
        'base_stats': {
            'hp': stats_map['hp'],
            'attack': stats_map['attack'],
            'defense': stats_map['defense'],
            'special': special,
            'speed': stats_map['speed']
        },
        'base_experience': base_experience,
        'growth_rate': growth_rate,
        'capture_rate': capture_rate,
        'base_happiness': base_happiness,
        'gender_rate': gender_rate,
        'pokedex_entry': pokedex_entry,
        'evolution_chain': evolution_chain,
        'learnset': learnset
    }

    # Add sprite paths if downloaded
    if sprite_paths:
        species_entry['sprites'] = sprite_paths

    return species_entry


def fetch_move(move_id: int) -> Optional[Dict[str, Any]]:
    """Fetch and process a single move's data."""
    print(f"⚔️  Fetching Move #{move_id}...")

    move_url = f"{POKEAPI_BASE}/move/{move_id}"
    move_data = fetch_json(move_url)

    if not move_data:
        return None

    # Extract move info
    move_name = move_data.get('name')
    move_type = move_data.get('type', {}).get('name')
    power = move_data.get('power')
    accuracy = move_data.get('accuracy')
    pp = move_data.get('pp')
    damage_class = move_data.get('damage_class', {}).get('name')  # physical, special, status
    priority = move_data.get('priority', 0)

    # Get effect chance (e.g., 10% chance to freeze)
    effect_chance = move_data.get('effect_chance')

    # Extract meta data for battle mechanics
    meta_data = move_data.get('meta', {})
    meta = {
        'ailment': meta_data.get('ailment', {}).get('name'),
        'ailment_chance': meta_data.get('ailment_chance', 0),
        'drain': meta_data.get('drain', 0),
        'healing': meta_data.get('healing', 0),
        'crit_rate': meta_data.get('crit_rate', 0),
        'flinch_chance': meta_data.get('flinch_chance', 0),
        'stat_chance': meta_data.get('stat_chance', 0),
        'min_hits': meta_data.get('min_hits'),
        'max_hits': meta_data.get('max_hits'),
        'category': meta_data.get('category', {}).get('name') if meta_data.get('category') else None
    }

    # Extract stat changes (e.g., Swords Dance increases attack)
    stat_changes = []
    for stat_change in move_data.get('stat_changes', []):
        stat_changes.append({
            'change': stat_change.get('change', 0),
            'stat': stat_change.get('stat', {}).get('name')
        })

    # Build move entry
    move_entry = {
        'id': move_id,
        'name': move_name,
        'type': move_type,
        'power': power,
        'accuracy': accuracy,
        'pp': pp,
        'category': damage_class,
        'priority': priority,
        'effect_chance': effect_chance,
        'meta': meta,
        'stat_changes': stat_changes
    }

    return move_entry


def fetch_location_encounters() -> Dict[str, List[Dict[str, Any]]]:
    """Fetch encounter data for Gen 1 location areas."""
    print(f"\n🗺️  Fetching Gen 1 encounter data...\n")

    encounters_by_location = {}

    for location_area in GEN1_LOCATION_AREAS:
        print(f"  📍 Fetching {location_area}...")

        location_url = f"{POKEAPI_BASE}/location-area/{location_area}"
        location_data = fetch_json(location_url)

        if not location_data:
            continue

        # Get encounters for Yellow version (with Red/Blue fallback)
        pokemon_encounters = location_data.get('pokemon_encounters', [])

        location_encounters = []
        for encounter in pokemon_encounters:
            pokemon_name = encounter.get('pokemon', {}).get('name')

            # Try Yellow first, then fallback to Red/Blue
            yellow_encounters = []
            red_blue_encounters = []

            for version_detail in encounter.get('version_details', []):
                version_name = version_detail.get('version', {}).get('name')

                for encounter_detail in version_detail.get('encounter_details', []):
                    method = encounter_detail.get('method', {}).get('name')
                    chance = encounter_detail.get('chance', 0)
                    min_level = encounter_detail.get('min_level', 1)
                    max_level = encounter_detail.get('max_level', 1)

                    encounter_data = {
                        'pokemon': pokemon_name,
                        'method': method,
                        'chance': chance,
                        'min_level': min_level,
                        'max_level': max_level
                    }

                    if version_name == 'yellow':
                        yellow_encounters.append(encounter_data)
                    elif version_name in ['red', 'blue']:
                        # Only store if we haven't seen this exact encounter yet
                        if encounter_data not in red_blue_encounters:
                            red_blue_encounters.append(encounter_data)

            # Use Yellow data if available, otherwise use Red/Blue
            if yellow_encounters:
                location_encounters.extend(yellow_encounters)
            elif red_blue_encounters:
                location_encounters.extend(red_blue_encounters)

        if location_encounters:
            # Determine which version data was used
            data_source = "Yellow"
            if location_encounters and all(
                any(vd.get('version', {}).get('name') in ['red', 'blue']
                    for vd in encounter.get('version_details', []))
                for encounter in pokemon_encounters
            ):
                data_source = "Red/Blue"

            encounters_by_location[location_area] = location_encounters
            print(f"    ✅ Found {len(location_encounters)} encounters ({data_source} data)")

    return encounters_by_location


def hydrate_pokemon():
    """Fetch all Gen 1 Pokemon data."""
    print(f"\n🎮 Hydrating Gen 1 Pokemon data (1-{GEN1_POKEMON_COUNT})...\n")

    species_list = []

    for pokemon_id in range(1, GEN1_POKEMON_COUNT + 1):
        species_data = fetch_pokemon_species(pokemon_id)
        if species_data:
            species_list.append(species_data)

    # Write to YAML
    output_file = POKEMON_DIR / "species.yaml"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        yaml.dump({'species': species_list}, f, default_flow_style=False, sort_keys=False)

    print(f"\n✅ Saved {len(species_list)} Pokemon to {output_file}")


def hydrate_moves():
    """Fetch all Gen 1 move data."""
    print(f"\n⚔️  Hydrating Gen 1 move data...\n")

    moves_list = []

    for move_id in GEN1_MOVE_IDS:
        move_data = fetch_move(move_id)
        if move_data:
            moves_list.append(move_data)

    # Write to YAML
    output_file = MOVES_DIR / "moves.yaml"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        yaml.dump({'moves': moves_list}, f, default_flow_style=False, sort_keys=False)

    print(f"\n✅ Saved {len(moves_list)} moves to {output_file}")


def hydrate_encounters():
    """Fetch Gen 1 encounter data."""
    encounters = fetch_location_encounters()

    # Write to YAML
    output_file = ENCOUNTERS_DIR / "yellow_encounters.yaml"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        yaml.dump({'locations': encounters}, f, default_flow_style=False, sort_keys=False)

    print(f"\n✅ Saved encounters for {len(encounters)} locations to {output_file}")


def hydrate_items():
    """Fetch Gen 1 item data for Pokemon Yellow."""
    print(f"\n🎒 Hydrating Pokemon Yellow item data...\n")

    if not ITEM_LIST_PATH.exists():
        raise FileNotFoundError(f"Item list not found: {ITEM_LIST_PATH}")

    with open(ITEM_LIST_PATH, 'r') as f:
        item_list_data = yaml.safe_load(f) or {}

    item_ids = item_list_data.get('items', [])
    items_list = []

    for item_id in item_ids:
        item_data = fetch_item_data(item_id)
        if item_data:
            items_list.append(item_data)

    output_file = ITEMS_DIR / "items.yaml"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        yaml.dump({'items': items_list}, f, default_flow_style=False, sort_keys=False)

    print(f"\n✅ Saved {len(items_list)} items to {output_file}")


def main():
    """Main hydration script."""
    print("=" * 60)
    print("🌊 POKÉMON YELLOW DATA HYDRATION SCRIPT")
    print("=" * 60)
    print(f"Source: PokéAPI ({POKEAPI_BASE})")
    print(f"Target: {DATA_DIR}")
    print("=" * 60)

    # Create directories
    SPRITES_DIR.mkdir(parents=True, exist_ok=True)
    POKEMON_DIR.mkdir(parents=True, exist_ok=True)
    MOVES_DIR.mkdir(parents=True, exist_ok=True)
    ENCOUNTERS_DIR.mkdir(parents=True, exist_ok=True)
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)

    # Hydrate data
    hydrate_pokemon()
    hydrate_moves()
    hydrate_encounters()
    hydrate_items()

    print("\n" + "=" * 60)
    print("✅ HYDRATION COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
