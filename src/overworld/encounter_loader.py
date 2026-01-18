# ABOUTME: Encounter data loader for wild Pokemon encounters
# ABOUTME: Loads and caches encounter zones from YAML

from src.overworld.encounter_zones import EncounterZone, EncounterSlot
from src.data import data_loader


class EncounterLoader:
    """Loads and caches wild encounter data."""

    def __init__(self):
        """Initialize encounter loader."""
        self.encounter_zones = {}
        self._load_all_encounters()

    def _load_all_encounters(self):
        """Load all encounter zones from YAML."""
        data = data_loader.load_yaml("data/encounters/yellow_encounters.yaml")
        locations = data.get("locations", {})

        for location_key, encounters_data in locations.items():
            # Build list of encounter slots
            encounter_slots = []

            for encounter in encounters_data:
                # Only load "walk" encounters for now (skip surf, fish, etc.)
                if encounter.get("method") == "walk":
                    slot = EncounterSlot(
                        species_id=encounter["pokemon"],
                        min_level=encounter["min_level"],
                        max_level=encounter["max_level"],
                        weight=encounter["chance"]  # Chance % becomes weight
                    )
                    encounter_slots.append(slot)

            # Only create zone if we have walk encounters
            if encounter_slots:
                # Determine encounter rate (default 10% for grass)
                encounter_rate = 10

                # Create encounter zone
                zone = EncounterZone(
                    map_name=self._normalize_map_name(location_key),
                    grass_tiles=[],
                    encounters=encounter_slots,
                    encounter_rate=encounter_rate
                )

                self.encounter_zones[zone.map_name] = zone

    def _normalize_map_name(self, location_key: str) -> str:
        """
        Convert PokéAPI location key to our map name format.

        Args:
            location_key: PokéAPI location key (e.g., "kanto-route-1-area")

        Returns:
            Normalized map name (e.g., "route_1")
        """
        # Remove "kanto-" prefix and "-area" suffix
        name = location_key.replace("kanto-", "").replace("-area", "")

        # Replace hyphens with underscores
        name = name.replace("-", "_")

        return name

    def get_encounter_zone(self, map_name: str) -> EncounterZone:
        """
        Get encounter zone for a map.

        Args:
            map_name: Name of the map (e.g., "route_1")

        Returns:
            EncounterZone or None if no encounters on this map
        """
        return self.encounter_zones.get(map_name)

    def get_all_zones(self) -> dict[str, EncounterZone]:
        """Get all loaded encounter zones."""
        return self.encounter_zones.copy()
