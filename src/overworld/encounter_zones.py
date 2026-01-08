# ABOUTME: Wild encounter zone definitions
# ABOUTME: Defines which Pokemon appear in which map areas

from dataclasses import dataclass
import random


@dataclass
class EncounterSlot:
    """Single encounter possibility."""
    species_id: str
    min_level: int
    max_level: int
    weight: int  # Relative probability


class EncounterZone:
    """Defines wild encounters for a map area."""

    def __init__(self, map_name: str, grass_tiles: list[int],
                 encounters: list[EncounterSlot], encounter_rate: int = 10):
        """
        Initialize encounter zone.

        Args:
            map_name: Map identifier
            grass_tiles: List of tile IDs that trigger encounters
            encounters: List of possible encounters
            encounter_rate: Percentage chance per step (1-100)
        """
        self.map_name = map_name
        self.grass_tiles = set(grass_tiles)
        self.encounters = encounters
        self.encounter_rate = encounter_rate

    def is_grass_tile(self, tile_id: int) -> bool:
        """Check if tile ID is grass."""
        return tile_id in self.grass_tiles

    def should_encounter(self) -> bool:
        """Roll for random encounter."""
        return random.randint(1, 100) <= self.encounter_rate

    def get_random_encounter(self) -> tuple[str, int]:
        """
        Get a random encounter.

        Returns:
            Tuple of (species_id, level)
        """
        # Weight-based selection
        total_weight = sum(slot.weight for slot in self.encounters)
        roll = random.randint(1, total_weight)

        cumulative = 0
        for slot in self.encounters:
            cumulative += slot.weight
            if roll <= cumulative:
                level = random.randint(slot.min_level, slot.max_level)
                return (slot.species_id, level)

        # Fallback (shouldn't reach here)
        slot = self.encounters[0]
        return (slot.species_id, slot.min_level)


# Define encounter zones for each map
ENCOUNTER_ZONES = {
    "route_1": EncounterZone(
        map_name="route_1",
        grass_tiles=[0],  # Tile ID 0 is grass in our tileset
        encounters=[
            EncounterSlot("rattata", 2, 5, 50),  # 50% chance
            EncounterSlot("pidgey", 2, 5, 50),   # 50% chance
        ],
        encounter_rate=10  # 10% per step
    ),
    # Pallet Town has no encounters
}


def get_encounter_zone(map_name: str):
    """
    Get encounter zone for a map.

    Args:
        map_name: Name of the map

    Returns:
        EncounterZone or None if no encounters on this map
    """
    return ENCOUNTER_ZONES.get(map_name)
