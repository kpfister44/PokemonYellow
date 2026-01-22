# ABOUTME: Tests for animated tile parsing and positioning in MapManager
# ABOUTME: Ensures animated sprites are offset for larger frame heights

import pygame
import pytmx

from src.overworld.map import MapManager


def setup_module(_module):
    pygame.init()
    pygame.display.set_mode((1, 1))


def teardown_module(_module):
    pygame.quit()


def test_animated_sprite_positions_account_for_frame_height():
    map_path = "assets/maps/pallet_town.tmx"
    manager = MapManager(map_path)
    tmx_data = pytmx.load_pygame(map_path)

    expected_positions = []
    for layer in tmx_data.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        for x, y, gid in layer:
            if gid == 0:
                continue
            properties = tmx_data.get_tile_properties_by_gid(gid) or {}
            if "src" not in properties:
                continue
            frame_height = int(properties.get("frame_height", properties.get("height", 16)))
            y_offset = max(0, frame_height - tmx_data.tileheight)
            expected_positions.append(
                (x * tmx_data.tilewidth, y * tmx_data.tileheight - y_offset)
            )

    actual_positions = [(sprite.rect.x, sprite.rect.y) for sprite in manager.animated_sprites]
    assert actual_positions == expected_positions
