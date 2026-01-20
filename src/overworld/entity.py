# ABOUTME: Base entity class for player and NPCs
# ABOUTME: Handles position, sprite, animation states, and movement logic

import pygame
from src.engine import constants


class SpriteSheet:
    """Handles sprite sheet loading and frame extraction for entity sprites."""

    def __init__(self, filepath: str, frame_width: int = 16, frame_height: int = 16, scale: int = 2):
        """
        Load a sprite sheet and extract frames.

        Args:
            filepath: Path to sprite sheet PNG
            frame_width: Width of each frame in pixels (default 16)
            frame_height: Height of each frame in pixels (default 16)
            scale: Scale factor for output frames (default 2, for 32x32 output)
        """
        self.sheet = pygame.image.load(filepath).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scale = scale
        self.frames = self._extract_frames()
        self._frame_cache = {}

    def _extract_frames(self) -> list[pygame.Surface]:
        """Extract and scale all frames from the sprite sheet."""
        frames = []
        num_frames = self.sheet.get_height() // self.frame_height
        for i in range(num_frames):
            frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
            frame.blit(self.sheet, (0, 0), (0, i * self.frame_height, self.frame_width, self.frame_height))
            scaled = pygame.transform.scale(frame, (self.frame_width * self.scale, self.frame_height * self.scale))
            frames.append(scaled)
        return frames

    def get_frame(self, direction: int, is_walking: bool) -> pygame.Surface:
        """
        Get the appropriate frame for direction and walking state.

        Frame layout (from Pokemon Yellow ROM):
        - 0: Down standing, 1: Down walking
        - 2: Up standing, 3: Up walking
        - 4: Side standing, 5: Side walking (flip for right)
        """
        cache_key = (direction, is_walking)
        if cache_key in self._frame_cache:
            return self._frame_cache[cache_key]

        frame_map = {
            (constants.DIR_DOWN, False): 0,
            (constants.DIR_DOWN, True): 1,
            (constants.DIR_UP, False): 2,
            (constants.DIR_UP, True): 3,
            (constants.DIR_LEFT, False): 4,
            (constants.DIR_LEFT, True): 5,
            (constants.DIR_RIGHT, False): 4,
            (constants.DIR_RIGHT, True): 5,
        }
        frame_idx = frame_map.get((direction, is_walking), 0)
        frame = self.frames[frame_idx]

        if direction == constants.DIR_RIGHT:
            frame = pygame.transform.flip(frame, True, False)

        self._frame_cache[cache_key] = frame
        return frame


class Entity:
    """Base class for entities (player, NPCs) in the overworld."""

    def __init__(self, tile_x, tile_y, sprite_surface=None):
        """
        Initialize an entity.

        Args:
            tile_x: Starting tile X coordinate
            tile_y: Starting tile Y coordinate
            sprite_surface: Optional pygame Surface for the entity sprite
        """
        # Grid position (in tiles)
        self.tile_x = tile_x
        self.tile_y = tile_y

        # Pixel position (for smooth movement)
        self.pixel_x = tile_x * constants.TILE_SIZE
        self.pixel_y = tile_y * constants.TILE_SIZE

        # Movement state
        self.is_moving = False
        self.move_progress = 0  # 0 to TILE_SIZE
        self.direction = constants.DIR_DOWN  # Facing direction

        # Target position when moving
        self.target_tile_x = tile_x
        self.target_tile_y = tile_y

        # Sprite
        self.sprite = sprite_surface

        # Animation
        self.animation_frame = 0
        self.animation_counter = 0

    def start_move(self, direction):
        """
        Start moving in a direction.

        Args:
            direction: Direction constant (DIR_UP, DIR_DOWN, etc.)

        Returns:
            True if movement started, False if already moving
        """
        if self.is_moving:
            return False

        self.direction = direction
        self.is_moving = True
        self.move_progress = 0

        # Set target tile based on direction
        if direction == constants.DIR_UP:
            self.target_tile_y = self.tile_y - 1
            self.target_tile_x = self.tile_x
        elif direction == constants.DIR_DOWN:
            self.target_tile_y = self.tile_y + 1
            self.target_tile_x = self.tile_x
        elif direction == constants.DIR_LEFT:
            self.target_tile_x = self.tile_x - 1
            self.target_tile_y = self.tile_y
        elif direction == constants.DIR_RIGHT:
            self.target_tile_x = self.tile_x + 1
            self.target_tile_y = self.tile_y

        return True

    def update_movement(self, speed=2):
        """
        Update movement animation.

        Args:
            speed: Pixels to move per frame (default 2)
        """
        if not self.is_moving:
            return

        # Increment move progress
        self.move_progress += speed

        # Update pixel position based on direction and progress
        if self.direction == constants.DIR_UP:
            self.pixel_y = self.tile_y * constants.TILE_SIZE - self.move_progress
        elif self.direction == constants.DIR_DOWN:
            self.pixel_y = self.tile_y * constants.TILE_SIZE + self.move_progress
        elif self.direction == constants.DIR_LEFT:
            self.pixel_x = self.tile_x * constants.TILE_SIZE - self.move_progress
        elif self.direction == constants.DIR_RIGHT:
            self.pixel_x = self.tile_x * constants.TILE_SIZE + self.move_progress

        # Check if movement is complete
        if self.move_progress >= constants.TILE_SIZE:
            self.finish_move()

    def finish_move(self):
        """Complete the current movement."""
        self.is_moving = False
        self.move_progress = 0
        self.tile_x = self.target_tile_x
        self.tile_y = self.target_tile_y
        self.pixel_x = self.tile_x * constants.TILE_SIZE
        self.pixel_y = self.tile_y * constants.TILE_SIZE

    def cancel_move(self):
        """Cancel current movement and snap back to original position."""
        self.is_moving = False
        self.move_progress = 0
        self.target_tile_x = self.tile_x
        self.target_tile_y = self.tile_y
        self.pixel_x = self.tile_x * constants.TILE_SIZE
        self.pixel_y = self.tile_y * constants.TILE_SIZE

    def update_animation(self):
        """Update animation frame counter."""
        if self.is_moving:
            self.animation_counter += 1
            if self.animation_counter >= constants.ANIMATION_FRAME_DURATION:
                self.animation_counter = 0
                self.animation_frame = (self.animation_frame + 1) % 2  # 2 frame walk cycle

    def get_pixel_position(self):
        """Get current pixel position. Returns (x, y) tuple."""
        return (self.pixel_x, self.pixel_y)

    def get_tile_position(self):
        """Get current tile position. Returns (x, y) tuple."""
        return (self.tile_x, self.tile_y)

    def get_rect(self) -> pygame.Rect:
        """Get the entity's current hitbox rectangle."""
        return pygame.Rect(
            self.pixel_x,
            self.pixel_y,
            constants.TILE_SIZE,
            constants.TILE_SIZE
        )

    def get_target_tile_position(self):
        """Get target tile position (where entity is moving to). Returns (x, y) tuple."""
        return (self.target_tile_x, self.target_tile_y)

    def render(self, renderer, camera_x, camera_y):
        """
        Render the entity.

        Args:
            renderer: Renderer instance
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        if self.sprite:
            screen_x = self.pixel_x - camera_x
            screen_y = self.pixel_y - camera_y
            renderer.draw_surface(self.sprite, (screen_x, screen_y))
