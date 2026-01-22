# ABOUTME: Overworld item pickup entity for visible map items
# ABOUTME: Renders pickup sprites and tracks item identifiers

import pygame

from src.engine import constants


class ItemPickup:
    """Represents a ground item pickup."""

    def __init__(self, pickup_id: str, item_id: str, tile_x: int, tile_y: int):
        self.pickup_id = pickup_id
        self.item_id = item_id
        self.tile_x = tile_x
        self.tile_y = tile_y

    def render(self, renderer, camera_x: int, camera_y: int) -> None:
        x = self.tile_x * constants.METATILE_SIZE - camera_x
        y = self.tile_y * constants.METATILE_SIZE - camera_y
        size = constants.METATILE_SIZE // 2
        offset = constants.METATILE_SIZE // 4
        renderer.draw_rect((0, 0, 0), (x + offset, y + offset, size, size), 0)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.tile_x * constants.METATILE_SIZE,
            self.tile_y * constants.METATILE_SIZE,
            constants.METATILE_SIZE,
            constants.METATILE_SIZE
        )
