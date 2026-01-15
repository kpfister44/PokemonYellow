# ABOUTME: Bag inventory storage for items and quantities
# ABOUTME: Enforces Gen 1 capacity and stacking rules

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class BagEntry:
    """Represents one item entry in the bag."""
    item_id: str
    quantity: int


class Bag:
    """Bag inventory with Gen 1 capacity and stacking behavior."""

    MAX_SLOTS = 20
    MAX_STACK = 99

    def __init__(self, item_lookup: Optional[Callable[[str], object]] = None):
        """Initialize an empty bag."""
        if item_lookup is None:
            from src.items.item_loader import ItemLoader
            self._item_loader = ItemLoader()
            self._item_lookup = self._item_loader.get_item
        else:
            self._item_lookup = item_lookup

        self._entries: list[BagEntry] = []

    def add_item(self, item_id: str) -> bool:
        """
        Add a single item to the bag.

        Returns:
            True if the item was added, False if the bag is full or stack is capped.
        """
        added, _reason = self.add_item_with_reason(item_id)
        return added

    def add_item_with_reason(self, item_id: str) -> tuple[bool, Optional[str]]:
        """
        Add a single item to the bag and return a reason when it fails.

        Returns:
            Tuple of (success, reason). Reason is None on success.
        """
        item = self._item_lookup(item_id)
        if item is None:
            raise ValueError(f"Unknown item: {item_id}")

        entry = self._find_entry(item_id)

        if item.countable:
            if entry:
                if entry.quantity >= self.MAX_STACK:
                    return False, "stack_full"
                entry.quantity += 1
                return True, None
            if len(self._entries) >= self.MAX_SLOTS:
                return False, "bag_full"
            self._entries.append(BagEntry(item_id=item_id, quantity=1))
            return True, None

        if entry:
            return False, "already_have"
        if len(self._entries) >= self.MAX_SLOTS:
            return False, "bag_full"
        self._entries.append(BagEntry(item_id=item_id, quantity=1))
        return True, None

    def remove_item(self, item_id: str) -> bool:
        """
        Remove a single item from the bag.

        Returns:
            True if removed, False if not found.
        """
        entry = self._find_entry(item_id)
        if not entry:
            return False

        entry.quantity -= 1
        if entry.quantity <= 0:
            self._entries.remove(entry)
        return True

    def get_entries(self) -> list[BagEntry]:
        """Return bag entries in acquisition order."""
        return list(self._entries)

    def get_quantity(self, item_id: str) -> int:
        """Get quantity for a specific item."""
        entry = self._find_entry(item_id)
        return entry.quantity if entry else 0

    def has_item(self, item_id: str) -> bool:
        """Check if bag contains the item."""
        return self._find_entry(item_id) is not None

    def _find_entry(self, item_id: str) -> Optional[BagEntry]:
        for entry in self._entries:
            if entry.item_id == item_id:
                return entry
        return None

    def to_dict(self) -> list[dict]:
        """Serialize bag entries to a list of dictionaries."""
        return [
            {"item_id": entry.item_id, "quantity": entry.quantity}
            for entry in self._entries
        ]

    @classmethod
    def from_dict(cls, data: list[dict]) -> "Bag":
        """Deserialize bag entries from a list of dictionaries."""
        bag = cls()
        for entry in data:
            item_id = entry.get("item_id")
            quantity = entry.get("quantity", 1)
            if not item_id:
                continue
            bag._entries.append(BagEntry(item_id=item_id, quantity=quantity))
        return bag
