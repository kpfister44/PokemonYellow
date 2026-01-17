# ABOUTME: Tests .blk-to-JSON conversion for pokeyellow map data
# ABOUTME: Validates block expansion into 2x2 tiles

from src.data.pokeyellow_map_converter import convert_blk_bytes


def test_convert_blk_bytes_expands_blocks():
    blk_bytes = bytes([1, 2, 3, 4])
    map_data = convert_blk_bytes(blk_bytes, block_width=2, block_height=2, tileset_name="test")

    assert map_data["width"] == 4
    assert map_data["height"] == 4
    assert map_data["tileset"] == "test"

    ground = map_data["layers"]["ground"]
    assert ground[0][0] == 1
    assert ground[0][1] == 1
    assert ground[1][0] == 1
    assert ground[1][1] == 1
    assert ground[0][2] == 2
    assert ground[0][3] == 2
    assert ground[2][0] == 3
    assert ground[2][1] == 3
    assert ground[2][2] == 4
    assert ground[3][3] == 4
