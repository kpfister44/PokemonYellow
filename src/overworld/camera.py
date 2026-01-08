# ABOUTME: Camera/viewport system for following player and rendering visible tiles
# ABOUTME: Manages what portion of the map is visible on screen with boundary checking

from src.engine import constants


class Camera:
    """Manages the viewport/camera that follows the player."""

    def __init__(self, map_width_pixels, map_height_pixels):
        """
        Initialize the camera.

        Args:
            map_width_pixels: Total map width in pixels
            map_height_pixels: Total map height in pixels
        """
        self.x = 0
        self.y = 0
        self.map_width = map_width_pixels
        self.map_height = map_height_pixels

    def center_on(self, target_x, target_y):
        """
        Center camera on a target position (like the player).

        Args:
            target_x: X position in pixels to center on
            target_y: Y position in pixels to center on
        """
        # Center the camera on the target
        self.x = target_x - constants.GAME_WIDTH // 2
        self.y = target_y - constants.GAME_HEIGHT // 2

        # Clamp camera to map boundaries
        self.clamp_to_bounds()

    def clamp_to_bounds(self):
        """Ensure camera doesn't show area outside the map."""
        # Don't scroll past left edge
        if self.x < 0:
            self.x = 0

        # Don't scroll past top edge
        if self.y < 0:
            self.y = 0

        # Don't scroll past right edge
        max_x = self.map_width - constants.GAME_WIDTH
        if max_x < 0:
            max_x = 0
        if self.x > max_x:
            self.x = max_x

        # Don't scroll past bottom edge
        max_y = self.map_height - constants.GAME_HEIGHT
        if max_y < 0:
            max_y = 0
        if self.y > max_y:
            self.y = max_y

    def get_offset(self):
        """Get camera offset for rendering. Returns (x, y) tuple."""
        return (self.x, self.y)

    def world_to_screen(self, world_x, world_y):
        """
        Convert world coordinates to screen coordinates.

        Args:
            world_x: X position in world space
            world_y: Y position in world space

        Returns:
            Tuple of (screen_x, screen_y)
        """
        return (world_x - self.x, world_y - self.y)

    def screen_to_world(self, screen_x, screen_y):
        """
        Convert screen coordinates to world coordinates.

        Args:
            screen_x: X position on screen
            screen_y: Y position on screen

        Returns:
            Tuple of (world_x, world_y)
        """
        return (screen_x + self.x, screen_y + self.y)

    def get_visible_tile_range(self):
        """
        Get the range of tiles that are visible in the viewport.

        Returns:
            Tuple of (start_tile_x, start_tile_y, end_tile_x, end_tile_y)
        """
        start_x = self.x // constants.TILE_SIZE
        start_y = self.y // constants.TILE_SIZE
        end_x = (self.x + constants.GAME_WIDTH) // constants.TILE_SIZE + 1
        end_y = (self.y + constants.GAME_HEIGHT) // constants.TILE_SIZE + 1

        return (start_x, start_y, end_x, end_y)
