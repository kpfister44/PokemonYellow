# ABOUTME: Converts Gen 1 .blk map data into the project's JSON map format
# ABOUTME: Expands block grids into tile grids for use by the overworld system

import json
from pathlib import Path


def convert_blk_bytes(blk_bytes, block_width, block_height, tileset_name):
    if len(blk_bytes) != block_width * block_height:
        raise ValueError("Block data size does not match block dimensions")

    tile_width = block_width * 2
    tile_height = block_height * 2
    ground = [[0 for _ in range(tile_width)] for _ in range(tile_height)]
    collision = [[0 for _ in range(tile_width)] for _ in range(tile_height)]

    for block_y in range(block_height):
        for block_x in range(block_width):
            block_id = blk_bytes[block_y * block_width + block_x]
            tile_y = block_y * 2
            tile_x = block_x * 2
            ground[tile_y][tile_x] = block_id
            ground[tile_y][tile_x + 1] = block_id
            ground[tile_y + 1][tile_x] = block_id
            ground[tile_y + 1][tile_x + 1] = block_id

    return {
        "width": tile_width,
        "height": tile_height,
        "tileset": tileset_name,
        "layers": {
            "ground": ground,
            "collision": collision,
        },
    }


def convert_blk_file(blk_path, block_width, block_height, output_path, tileset_name):
    blk_path = Path(blk_path)
    output_path = Path(output_path)
    blk_bytes = blk_path.read_bytes()
    map_data = convert_blk_bytes(blk_bytes, block_width, block_height, tileset_name)
    output_path.write_text(json.dumps(map_data, indent=2))
    return output_path
