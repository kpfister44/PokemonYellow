# ABOUTME: CLI for converting pokeyellow .blk maps into JSON for this project
# ABOUTME: Writes expanded tile grids to a specified output path

import argparse

from src.data.pokeyellow_map_converter import convert_blk_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--blk-path", required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--tileset", default="pokeyellow_raw_blocks")
    args = parser.parse_args()

    convert_blk_file(
        args.blk_path,
        args.width,
        args.height,
        args.output,
        args.tileset,
    )


if __name__ == "__main__":
    main()
