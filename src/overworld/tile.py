# ABOUTME: Tile class representing individual map tiles
# ABOUTME: Handles tile properties like collision, sprite reference, and special types

from src.engine import constants


class Tile:
    """Represents a single tile in the game world."""

    def __init__(self, tile_id, collision=False, tile_type="normal"):
        """
        Initialize a tile.

        Args:
            tile_id: The ID of this tile (used to look up sprite)
            collision: Whether this tile blocks movement
            tile_type: Type of tile (normal, grass, water, warp, etc.)
        """
        self.tile_id = tile_id
        self.collision = collision
        self.tile_type = tile_type

    def is_walkable(self):
        """Check if entities can walk on this tile."""
        return not self.collision

    def is_grass(self):
        """Check if this is a grass tile (for wild encounters)."""
        return self.tile_type == "grass"

    def is_water(self):
        """Check if this is a water tile."""
        return self.tile_type == "water"

    def __repr__(self):
        """String representation for debugging."""
        return f"Tile(id={self.tile_id}, collision={self.collision}, type={self.tile_type})"


class TileType:
    """Constants for different tile types."""
    NORMAL = "normal"
    GRASS = "grass"
    WATER = "water"
    LEDGE = "ledge"
    DOOR = "door"
    WARP = "warp"
