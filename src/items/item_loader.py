# ABOUTME: Loads item data from YAML into Item objects
# ABOUTME: Provides cached access to Pokemon Yellow item definitions

from src.data import data_loader
from src.items.item import Item


class ItemLoader:
    """Loads and caches item data."""

    def __init__(self):
        """Initialize item loader."""
        self.item_cache = {}
        self._load_all_items()

    def _load_all_items(self):
        """Load all items from YAML."""
        data = data_loader.load_yaml("data/items/items.yaml")
        items_list = data.get("items", [])

        for item_data in items_list:
            item = Item.from_dict(item_data)
            self.item_cache[item.item_id] = item

    def get_item(self, item_id: str) -> Item:
        """
        Get item by ID.

        Args:
            item_id: Item identifier (e.g., "potion")
        """
        if item_id not in self.item_cache:
            raise KeyError(f"Item not found: {item_id}")
        return self.item_cache[item_id]

    def get_all_items(self) -> dict[str, Item]:
        """Get all loaded items."""
        return self.item_cache.copy()
