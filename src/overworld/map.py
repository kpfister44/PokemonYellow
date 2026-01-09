# ABOUTME: Map class for loading and rendering tile-based maps
# ABOUTME: Handles multi-layer rendering, collision detection, and warp points

import pygame
from src.engine import constants
from src.overworld.tile import Tile
from src.data import data_loader


class Map:
    """Represents a game map with tiles, collision, and warps."""

    def __init__(self, map_filepath, renderer):
        """
        Initialize and load a map from JSON.

        Args:
            map_filepath: Path to the map JSON file
            renderer: Renderer instance for loading sprites
        """
        self.renderer = renderer
        self.map_data = data_loader.load_json(map_filepath)

        # Extract map name from filepath (e.g., "route_1" from "data/maps/route_1.json")
        import os
        self.map_name = os.path.splitext(os.path.basename(map_filepath))[0]

        # Extract map properties
        self.width = self.map_data["width"]  # Width in tiles
        self.height = self.map_data["height"]  # Height in tiles
        self.tileset_name = self.map_data.get("tileset", "default")

        # Load layers
        self.ground_layer = self.map_data["layers"]["ground"]
        self.decoration_layer = self.map_data["layers"].get("decorations", None)
        self.collision_layer = self.map_data["layers"]["collision"]

        # Load warps
        self.warps = self.map_data.get("warps", [])

        # Load tileset sprite
        self.tileset = self._load_tileset()

    def _load_tileset(self):
        """
        Load the tileset sprites.

        Returns:
            Dictionary mapping tile_id to pygame Surface
        """
        tileset = {}

        # Map tile IDs to sprite files
        tile_sprites = {
            0: "assets/tiles/grass.png",
            1: "assets/tiles/building.png",
            2: "assets/tiles/path.png",
            3: "assets/tiles/water.png",
            4: "assets/tiles/tree.png",
            5: "assets/tiles/sign.png",
        }

        # Load sprites for each tile ID
        for tile_id, sprite_path in tile_sprites.items():
            try:
                tileset[tile_id] = self.renderer.load_sprite(sprite_path)
            except Exception as e:
                print(f"Warning: Failed to load tile sprite {sprite_path}: {e}")
                # Fallback to colored rectangle
                surface = pygame.Surface((constants.TILE_SIZE, constants.TILE_SIZE))
                surface.fill(constants.COLOR_DEBUG)
                tileset[tile_id] = surface

        # Create default tile for any unmapped IDs
        default_tile = pygame.Surface((constants.TILE_SIZE, constants.TILE_SIZE))
        default_tile.fill(constants.COLOR_DARKEST)
        for tile_id in range(6, 10):
            tileset[tile_id] = default_tile

        return tileset

    def render(self, camera_x, camera_y):
        """
        Render the visible portion of the map.

        Args:
            camera_x: Camera X offset in pixels
            camera_y: Camera Y offset in pixels

        Returns:
            pygame.Surface with the rendered map
        """
        # Create a surface for the entire map view
        map_surface = pygame.Surface((constants.GAME_WIDTH, constants.GAME_HEIGHT))

        # Calculate visible tile range
        start_tile_x = max(0, camera_x // constants.TILE_SIZE)
        start_tile_y = max(0, camera_y // constants.TILE_SIZE)
        end_tile_x = min(self.width, (camera_x + constants.GAME_WIDTH) // constants.TILE_SIZE + 1)
        end_tile_y = min(self.height, (camera_y + constants.GAME_HEIGHT) // constants.TILE_SIZE + 1)

        # Render ground layer
        for y in range(start_tile_y, end_tile_y):
            for x in range(start_tile_x, end_tile_x):
                tile_id = self.ground_layer[y][x]
                if tile_id in self.tileset:
                    tile_sprite = self.tileset[tile_id]
                    screen_x = x * constants.TILE_SIZE - camera_x
                    screen_y = y * constants.TILE_SIZE - camera_y
                    map_surface.blit(tile_sprite, (screen_x, screen_y))

        # Render decoration layer if it exists
        if self.decoration_layer:
            for y in range(start_tile_y, end_tile_y):
                for x in range(start_tile_x, end_tile_x):
                    tile_id = self.decoration_layer[y][x]
                    if tile_id > 0 and tile_id in self.tileset:
                        tile_sprite = self.tileset[tile_id]
                        screen_x = x * constants.TILE_SIZE - camera_x
                        screen_y = y * constants.TILE_SIZE - camera_y
                        map_surface.blit(tile_sprite, (screen_x, screen_y))

        return map_surface

    def is_walkable(self, tile_x, tile_y):
        """
        Check if a tile position is walkable.

        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate

        Returns:
            True if walkable, False otherwise
        """
        # Out of bounds is not walkable
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return False

        # Check collision layer (0 = walkable, 1 = blocked)
        return self.collision_layer[tile_y][tile_x] == 0

    def get_warp_at(self, tile_x, tile_y):
        """
        Get warp data if there's a warp at this tile position.

        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate

        Returns:
            Warp dict if found, None otherwise
        """
        for warp in self.warps:
            if warp["x"] == tile_x and warp["y"] == tile_y:
                return warp
        return None

    def get_width_pixels(self):
        """Get map width in pixels."""
        return self.width * constants.TILE_SIZE

    def get_height_pixels(self):
        """Get map height in pixels."""
        return self.height * constants.TILE_SIZE
