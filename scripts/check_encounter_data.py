#!/usr/bin/env python3
# ABOUTME: Diagnostic script to check what encounter data is available in PokéAPI
# ABOUTME: Tests Yellow, Red, and Blue versions for route and location data

import requests
import time

POKEAPI_BASE = "https://pokeapi.co/api/v2"
REQUEST_DELAY = 0.1

def check_location_area(location_area: str, versions: list[str]):
    """Check if a location area has encounter data for specified versions."""
    print(f"\n📍 Checking {location_area}...")

    try:
        time.sleep(REQUEST_DELAY)
        url = f"{POKEAPI_BASE}/location-area/{location_area}"
        response = requests.get(url, timeout=10)

        if response.status_code == 404:
            print(f"  ❌ Location not found in API")
            return

        response.raise_for_status()
        data = response.json()

        pokemon_encounters = data.get('pokemon_encounters', [])

        for version in versions:
            version_encounters = []
            for encounter in pokemon_encounters:
                pokemon_name = encounter.get('pokemon', {}).get('name')

                for version_detail in encounter.get('version_details', []):
                    if version_detail.get('version', {}).get('name') == version:
                        for encounter_detail in version_detail.get('encounter_details', []):
                            version_encounters.append({
                                'pokemon': pokemon_name,
                                'method': encounter_detail.get('method', {}).get('name'),
                                'chance': encounter_detail.get('chance', 0)
                            })

            if version_encounters:
                print(f"  ✅ {version.upper()}: {len(version_encounters)} encounters")
                # Show first 3 as examples
                for enc in version_encounters[:3]:
                    print(f"     - {enc['pokemon']} ({enc['method']}, {enc['chance']}%)")
            else:
                print(f"  ❌ {version.upper()}: No encounters")

    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    print("=" * 60)
    print("🔍 POKÉAPI ENCOUNTER DATA CHECKER")
    print("=" * 60)

    # Test some routes
    print("\n🛤️  TESTING ROUTES")
    print("-" * 60)
    routes_to_test = [
        "route-1-area",
        "route-2-area",
        "route-22-area"
    ]

    for route in routes_to_test:
        check_location_area(route, ['yellow', 'red', 'blue'])

    # Test known working locations
    print("\n🏔️  TESTING KNOWN LOCATIONS")
    print("-" * 60)
    locations_to_test = [
        "viridian-forest-area",
        "mt-moon-1f",
        "digletts-cave-area"
    ]

    for location in locations_to_test:
        check_location_area(location, ['yellow', 'red', 'blue'])

    print("\n" + "=" * 60)
    print("✅ CHECK COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
