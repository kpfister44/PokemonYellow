# ABOUTME: Tests for TMX-based MapManager loading and properties
# ABOUTME: Verifies collisions, grass detection, and object parsing

import pygame

from src.overworld.map import MapManager


def setup_module(_module):
    pygame.init()
    pygame.display.set_mode((1, 1))


def teardown_module(_module):
    pygame.quit()


def test_map_manager_loads_tmx():
    manager = MapManager("assets/maps/test_map.tmx")

    assert manager.width == 10
    assert manager.height == 9
    assert manager.tile_width == 32
    assert manager.tile_height == 32


def test_map_manager_collision_and_grass():
    manager = MapManager("assets/maps/test_map.tmx")

    assert manager.is_walkable(1, 1) is False
    assert manager.is_walkable(0, 0) is True
    assert manager.is_grass(0, 0) is True


def test_map_manager_parses_objects():
    manager = MapManager("assets/maps/test_map.tmx")

    assert len(manager.npcs) == 1
    assert manager.npcs[0].npc_id == "npc_1"
    assert len(manager.item_pickups) == 1
    assert manager.item_pickups[0].item_id == "potion"

    warp = manager.get_warp_at(3, 1)
    assert warp is not None
    assert warp["dest_map"] == "player_house"
    assert warp["dest_x"] == 2
    assert warp["dest_y"] == 3


def test_fringe_surface_uses_alpha():
    manager = MapManager("assets/maps/test_map.tmx")

    assert manager.fringe_surface.get_flags() & pygame.SRCALPHA
