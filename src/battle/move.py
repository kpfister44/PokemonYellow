# ABOUTME: Move data structures for battle system
# ABOUTME: Defines move stats and effects

from dataclasses import dataclass


@dataclass
class Move:
    """Pokemon move definition."""
    move_id: str  # e.g., "tackle"
    id_number: int  # Gen 1 move ID
    name: str  # Display name
    type: str
    power: int  # 0 for status moves
    accuracy: int  # 0-100, or -1 for "never miss"
    pp: int  # Power points
    category: str  # "damage", "status", etc.
    description: str

    @classmethod
    def from_dict(cls, move_id: str, data: dict):
        """Create Move from YAML data."""
        return cls(
            move_id=move_id,
            id_number=data["id"],
            name=data["name"],
            type=data["type"],
            power=data["power"],
            accuracy=data["accuracy"],
            pp=data["pp"],
            category=data["category"],
            description=data["description"]
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
        return not self.is_physical() and self.power > 0
