# ABOUTME: Item data definitions loaded from Pokemon Yellow item data
# ABOUTME: Provides structured access to item metadata

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Item:
    """Represents a single item and its metadata."""
    id: int
    item_id: str
    name: str
    category: Optional[str]
    pocket: Optional[str]
    attributes: list[str]
    cost: int
    effect: str
    flavor_text: str
    machines: list[dict[str, Any]]
    usable_in_battle: bool
    usable_in_overworld: bool
    countable: bool
    consumable: bool
    sprite: Optional[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Item":
        """Create an Item from a dictionary."""
        return cls(
            id=data.get("id", 0),
            item_id=data.get("item_id", ""),
            name=data.get("name", ""),
            category=data.get("category"),
            pocket=data.get("pocket"),
            attributes=data.get("attributes", []),
            cost=data.get("cost", 0),
            effect=data.get("effect", ""),
            flavor_text=data.get("flavor_text", ""),
            machines=data.get("machines", []),
            usable_in_battle=data.get("usable_in_battle", False),
            usable_in_overworld=data.get("usable_in_overworld", False),
            countable=data.get("countable", False),
            consumable=data.get("consumable", False),
            sprite=data.get("sprite")
        )
