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
class SpriteData:
    """Sprite file paths for a Pokemon."""
    front: Optional[str]
    back: Optional[str]


@dataclass
class Species:
    """Pokemon species definition (Pokedex entry)."""
    species_id: str  # e.g., "bulbasaur"
    number: int  # Pokedex number
    name: str  # Display name
    types: list[str]  # List of 1-2 types
    base_stats: BaseStats
    level_up_moves: list[LevelUpMove]
    sprites: Optional[SpriteData] = None

    @property
    def type1(self) -> str:
        """Primary type (for backwards compatibility)."""
        return self.types[0] if self.types else "normal"

    @property
    def type2(self) -> Optional[str]:
        """Secondary type (for backwards compatibility)."""
        return self.types[1] if len(self.types) > 1 else None

    @classmethod
    def from_dict(cls, data: dict):
        """Create Species from YAML data (PokéAPI format)."""
        species_id = data["name"].lower()

        # Parse sprites if present
        sprites = None
        if "sprites" in data:
            sprites = SpriteData(
                front=data["sprites"].get("front"),
                back=data["sprites"].get("back")
            )

        return cls(
            species_id=species_id,
            number=data["id"],
            name=data["name"],
            types=data["types"],
            base_stats=BaseStats(**data["base_stats"]),
            level_up_moves=[
                LevelUpMove(**move_data)
                for move_data in data.get("learnset", [])
            ],
            sprites=sprites
        )
