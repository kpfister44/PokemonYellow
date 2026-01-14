# ABOUTME: Tests collision against item pickups in the overworld
# ABOUTME: Ensures items block movement until collected

from src.engine import constants
from src.overworld.item_pickup import ItemPickup
from src.overworld.player import Player


class FakeInput:
    def __init__(self, direction):
        self.direction = direction

    def get_direction(self):
        return self.direction


class FakeMap:
    def is_walkable(self, _x, _y):
        return True


def test_player_cannot_walk_onto_item_pickup():
    player = Player(5, 5)
    pickups = [ItemPickup("test_item", "potion", 5, 6)]
    input_handler = FakeInput(constants.DIR_DOWN)

    moved = player.handle_input(input_handler, FakeMap(), [], pickups)

    assert moved is False
    assert player.tile_x == 5
    assert player.tile_y == 5
