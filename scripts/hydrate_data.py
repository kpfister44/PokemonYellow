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
SPRITES_DIR = PROJECT_ROOT / "assets" / "sprites" / "pokemon"

# Gen 1 constants
GEN1_POKEMON_COUNT = 151
GEN1_MOVE_IDS = range(1, 166)  # Gen 1 moves are IDs 1-165

# Rate limiting
REQUEST_DELAY = 0.1  # 100ms between requests to be respectful


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


def get_yellow_learnset(pokemon_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract Yellow version learnset from Pokemon data."""
    learnset = []

    for move_entry in pokemon_data.get('moves', []):
        for version_detail in move_entry.get('version_group_details', []):
            version_group = version_detail.get('version_group', {}).get('name')

            # Yellow version data
            if version_group == 'yellow':
                learn_method = version_detail.get('move_learn_method', {}).get('name')

                # Only include level-up moves for now
                if learn_method == 'level-up':
                    level = version_detail.get('level_learned_at', 0)
                    move_name = move_entry.get('move', {}).get('name')

                    learnset.append({
                        'level': level,
                        'move': move_name
                    })

    # Sort by level
    learnset.sort(key=lambda x: x['level'])
    return learnset


def fetch_pokemon_species(pokemon_id: int) -> Dict[str, Any]:
    """Fetch and process a single Pokemon's data."""
    print(f"📦 Fetching Pokemon #{pokemon_id}...")

    # Fetch main Pokemon data
    pokemon_url = f"{POKEAPI_BASE}/pokemon/{pokemon_id}"
    pokemon_data = fetch_json(pokemon_url)

    if not pokemon_data:
        return None

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

    # Download sprites
    sprites = pokemon_data.get('sprites', {})
    front_sprite_url = sprites.get('front_default')
    back_sprite_url = sprites.get('back_default')

    pokemon_name = pokemon_data.get('name')
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

    # Build move entry
    move_entry = {
        'id': move_id,
        'name': move_name,
        'type': move_type,
        'power': power,
        'accuracy': accuracy,
        'pp': pp,
        'category': damage_class
    }

    return move_entry


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

    # Hydrate data
    hydrate_pokemon()
    hydrate_moves()

    print("\n" + "=" * 60)
    print("✅ HYDRATION COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
