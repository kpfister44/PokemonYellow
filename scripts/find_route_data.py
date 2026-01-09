#!/usr/bin/env python3
# ABOUTME: Script to find how routes are named in PokéAPI
# ABOUTME: Tests different naming patterns for route data

import requests
import time

POKEAPI_BASE = "https://pokeapi.co/api/v2"
REQUEST_DELAY = 0.1

def try_location_patterns():
    """Try different naming patterns for Route 1."""
    patterns = [
        "route-1-area",
        "route-1",
        "kanto-route-1",
        "kanto-route-1-area",
        "route-01-area",
        "route-01",
    ]

    print("🔍 Trying different naming patterns for Route 1:\n")

    for pattern in patterns:
        try:
            time.sleep(REQUEST_DELAY)
            url = f"{POKEAPI_BASE}/location-area/{pattern}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                encounter_count = len(data.get('pokemon_encounters', []))
                print(f"✅ FOUND: {pattern} ({encounter_count} Pokemon)")
                return pattern
            else:
                print(f"❌ Not found: {pattern}")
        except Exception as e:
            print(f"❌ Error with {pattern}: {e}")

    return None

def check_location_list():
    """Check what locations are available in the API."""
    print("\n🗺️  Fetching location list...\n")

    try:
        url = f"{POKEAPI_BASE}/location"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"Total locations: {data.get('count')}")
        print("\nFirst 20 locations:")

        for location in data.get('results', [])[:20]:
            print(f"  - {location['name']}")

        # Check if there's a "route-1" or "kanto-route-1"
        all_results = data.get('results', [])
        route_locations = [loc for loc in all_results if 'route' in loc['name'].lower()]
        print(f"\nFound {len(route_locations)} route-related locations:")
        for loc in route_locations[:10]:
            print(f"  - {loc['name']}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 FINDING ROUTE DATA IN POKÉAPI")
    print("=" * 60)

    try_location_patterns()
    check_location_list()

    print("\n" + "=" * 60)
