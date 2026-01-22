# ABOUTME: Tests display constants for Game Boy sized viewport
# ABOUTME: Ensures window size matches the game surface without scaling

from src.engine import constants


def test_game_boy_viewport_dimensions():
    assert constants.GAME_WIDTH == 160
    assert constants.GAME_HEIGHT == 144
    assert constants.WINDOW_WIDTH == constants.GAME_WIDTH
    assert constants.WINDOW_HEIGHT == constants.GAME_HEIGHT
    assert constants.SCALE_FACTOR == 1
    assert constants.TILE_SIZE == 8
    assert constants.TILES_WIDE == 20
    assert constants.TILES_HIGH == 18
