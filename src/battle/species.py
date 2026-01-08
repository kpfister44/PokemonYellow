# ABOUTME: Pokemon species data structures
# ABOUTME: Defines species stats and move learning

from dataclasses import dataclass, field
from typing import Optional, Any


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
    method: str = "level-up"  # level-up, machine, egg, tutor


@dataclass
class EvolutionDetails:
    """Evolution details for a single evolution step."""
    species: str
    trigger: str  # level-up, use-item, trade
    min_level: Optional[int] = None
    item: Optional[str] = None
    evolves_to: list[Any] = field(default_factory=list)  # Recursive type


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
    base_experience: int  # XP yield when defeated
    growth_rate: str  # slow, medium-slow, medium, medium-fast, fast, fluctuating
    capture_rate: int  # 0-255, higher = easier to catch
    base_happiness: int  # Starting happiness value
    gender_rate: int  # -1 = genderless, 0 = always male, 8 = always female, else ratio
    pokedex_entry: str  # Pokedex flavor text
    evolution_chain: dict  # Evolution chain data
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

        # Parse learnset
        learnset = []
        for move_data in data.get("learnset", []):
            learnset.append(LevelUpMove(
                level=move_data.get("level", 0),
                move=move_data.get("move", ""),
                method=move_data.get("method", "level-up")
            ))

        return cls(
            species_id=species_id,
            number=data["id"],
            name=data["name"],
            types=data["types"],
            base_stats=BaseStats(**data["base_stats"]),
            base_experience=data.get("base_experience", 0),
            growth_rate=data.get("growth_rate", "medium"),
            capture_rate=data.get("capture_rate", 255),
            base_happiness=data.get("base_happiness", 70),
            gender_rate=data.get("gender_rate", -1),
            pokedex_entry=data.get("pokedex_entry", ""),
            evolution_chain=data.get("evolution_chain", {}),
            level_up_moves=learnset,
            sprites=sprites
        )
