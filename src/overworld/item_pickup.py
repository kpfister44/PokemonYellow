# ABOUTME: Overworld item pickup entity for visible map items
# ABOUTME: Renders pickup sprites and tracks item identifiers

from src.engine import constants


class ItemPickup:
    """Represents a ground item pickup."""

    def __init__(self, pickup_id: str, item_id: str, tile_x: int, tile_y: int):
        self.pickup_id = pickup_id
        self.item_id = item_id
        self.tile_x = tile_x
        self.tile_y = tile_y

    def render(self, renderer, camera_x: int, camera_y: int) -> None:
        x = self.tile_x * constants.TILE_SIZE - camera_x
        y = self.tile_y * constants.TILE_SIZE - camera_y
        renderer.draw_rect((0, 0, 0), (x + 4, y + 4, 8, 8), 0)
