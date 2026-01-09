# ABOUTME: Move data structures for battle system
# ABOUTME: Defines move stats and effects

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MoveMeta:
    """Move metadata for battle mechanics (status effects, healing, multi-hit, etc.)."""
    ailment: Optional[str] = None  # Status condition inflicted (paralysis, burn, etc.)
    ailment_chance: int = 0  # Percentage chance to inflict ailment
    drain: int = 0  # HP drain percentage (positive = attacker heals)
    healing: int = 0  # HP healing percentage (positive = self-healing)
    crit_rate: int = 0  # Critical hit rate bonus
    flinch_chance: int = 0  # Percentage chance to flinch
    stat_chance: int = 0  # Percentage chance for stat changes
    min_hits: Optional[int] = None  # Minimum hits (for multi-hit moves)
    max_hits: Optional[int] = None  # Maximum hits (for multi-hit moves)
    category: Optional[str] = None  # Move category (damage, damage+ailment, etc.)


@dataclass
class StatChange:
    """Stat stage change from a move (e.g., Swords Dance +2 Attack)."""
    change: int  # Number of stages to change (-6 to +6)
    stat: str  # Stat name (attack, defense, speed, special, accuracy, evasion)


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
    priority: int = 0  # Move priority (-7 to +5, default 0)
    effect_chance: Optional[int] = None  # Percentage chance for secondary effect
    description: str = ""  # Optional description
    meta: Optional[MoveMeta] = None  # Move metadata for battle mechanics
    stat_changes: list[StatChange] = field(default_factory=list)  # Stat stage changes

    @classmethod
    def from_dict(cls, data: dict):
        """Create Move from YAML data (PokéAPI format)."""
        move_id = data["name"]

        # Parse meta data
        meta = None
        if "meta" in data:
            meta_data = data["meta"]
            meta = MoveMeta(
                ailment=meta_data.get("ailment"),
                ailment_chance=meta_data.get("ailment_chance", 0),
                drain=meta_data.get("drain", 0),
                healing=meta_data.get("healing", 0),
                crit_rate=meta_data.get("crit_rate", 0),
                flinch_chance=meta_data.get("flinch_chance", 0),
                stat_chance=meta_data.get("stat_chance", 0),
                min_hits=meta_data.get("min_hits"),
                max_hits=meta_data.get("max_hits"),
                category=meta_data.get("category")
            )

        # Parse stat changes
        stat_changes = []
        for sc in data.get("stat_changes", []):
            stat_changes.append(StatChange(
                change=sc["change"],
                stat=sc["stat"]
            ))

        return cls(
            move_id=move_id,
            id_number=data["id"],
            name=data["name"],
            type=data["type"],
            power=data.get("power"),
            accuracy=data.get("accuracy"),
            pp=data["pp"],
            category=data["category"],
            priority=data.get("priority", 0),
            effect_chance=data.get("effect_chance"),
            description=data.get("description", ""),
            meta=meta,
            stat_changes=stat_changes
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
