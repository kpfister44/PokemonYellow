# ABOUTME: Move data structures for battle system
# ABOUTME: Defines move stats and effects

from dataclasses import dataclass
from typing import Optional


@dataclass
class Move:
    """Pokemon move definition."""
    move_id: str  # e.g., "tackle"
    id_number: int  # Gen 1 move ID
    name: str  # Display name
    type: str
    power: Optional[int]  # None for status moves
    accuracy: Optional[int]  # 0-100, or None for "never miss"
    pp: int  # Power points
    category: str  # "physical", "special", "status"
    description: str = ""  # Optional description

    @classmethod
    def from_dict(cls, data: dict):
        """Create Move from YAML data (PokéAPI format)."""
        move_id = data["name"]
        return cls(
            move_id=move_id,
            id_number=data["id"],
            name=data["name"],
            type=data["type"],
            power=data.get("power"),
            accuracy=data.get("accuracy"),
            pp=data["pp"],
            category=data["category"],
            description=data.get("description", "")
        )

    def is_physical(self) -> bool:
        """
        Check if move is physical (Gen 1 mechanics).
        Physical/Special split is based on TYPE, not move.
        """
        physical_types = {"normal", "fighting", "flying", "poison",
                         "ground", "rock", "bug", "ghost"}
        return self.type in physical_types

    def is_special(self) -> bool:
        """Check if move is special (Gen 1 mechanics)."""
        return not self.is_physical() and self.power is not None and self.power > 0
