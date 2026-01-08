# ABOUTME: Pokemon species data structures
# ABOUTME: Defines species stats and move learning

from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseStats:
    """Gen 1 base stats (5 stats, not 6)."""
    hp: int
    attack: int
    defense: int
    special: int  # Gen 1 has single "Special" stat
    speed: int


@dataclass
class LevelUpMove:
    """Move learned at a specific level."""
    level: int
    move: str  # Move ID/name


@dataclass
class Species:
    """Pokemon species definition (Pokedex entry)."""
    species_id: str  # e.g., "rattata"
    number: int  # Pokedex number
    name: str  # Display name
    type1: str
    type2: Optional[str]
    base_stats: BaseStats
    level_up_moves: list[LevelUpMove]

    @classmethod
    def from_dict(cls, species_id: str, data: dict):
        """Create Species from YAML data."""
        return cls(
            species_id=species_id,
            number=data["number"],
            name=data["name"],
            type1=data["type1"],
            type2=data.get("type2"),
            base_stats=BaseStats(**data["base_stats"]),
            level_up_moves=[
                LevelUpMove(**move_data)
                for move_data in data.get("level_up_moves", [])
            ]
        )
