# ABOUTME: Base entity class for player and NPCs
# ABOUTME: Handles position, sprite, animation states, and movement logic (pylletTown-style)

import pygame
from src.engine import constants


class SpriteSheet:
    """Handles sprite sheet loading with scroll-based frame selection (pylletTown style).

    Sprite sheet layout (32x64 for 16x16 frames):
    - 2 columns: standing (left) + walking (right)
    - 4 rows: down, up, left, right
    """

    def __init__(self, filepath: str, frame_size: int = 16):
        """
        Load a sprite sheet.

        Args:
            filepath: Path to sprite sheet PNG
            frame_size: Size of each frame in pixels (default 16)
        """
        self.original_image = pygame.image.load(filepath).convert_alpha()
        self.image = self.original_image.copy()
        self.frame_size = frame_size

    def set_orientation(self, direction: int):
        """Reset image and scroll to the correct row for the given direction."""
        self.image = self.original_image.copy()

        # Scroll vertically to correct row
        if direction == constants.DIR_DOWN:
            pass  # Row 0, no scroll needed
        elif direction == constants.DIR_UP:
            self.image.scroll(0, -self.frame_size)
        elif direction == constants.DIR_LEFT:
            self.image.scroll(0, -self.frame_size * 2)
        elif direction == constants.DIR_RIGHT:
            self.image.scroll(0, -self.frame_size * 3)

    def set_walking_frame(self):
        """Scroll horizontally to the walking frame (column 1)."""
        self.image.scroll(-self.frame_size, 0)

    def flip_horizontal(self):
        """Flip the image horizontally for foot alternation."""
        self.image = pygame.transform.flip(self.image, True, False)

    def get_current_frame(self) -> pygame.Surface:
        """Get the current visible frame (top-left frame_size x frame_size area)."""
        frame = pygame.Surface((self.frame_size, self.frame_size), pygame.SRCALPHA)
        frame.blit(self.image, (0, 0), (0, 0, self.frame_size, self.frame_size))
        return frame


class Entity:
    """Base class for entities (player, NPCs) in the overworld."""

    # Frames to hold direction before walking starts (6 frames at 60 FPS ≈ 100ms)
    HOLD_FRAMES_THRESHOLD = 6

    def __init__(self, tile_x, tile_y, sprite_surface=None):
        """
        Initialize an entity.

        Args:
            tile_x: Starting metatile X coordinate
            tile_y: Starting metatile Y coordinate
            sprite_surface: Optional pygame Surface for the entity sprite
        """
        # Grid position (in metatiles, not base tiles)
        self.tile_x = tile_x
        self.tile_y = tile_y

        # Pixel position (for smooth movement) uses METATILE_SIZE
        self.pixel_x = tile_x * constants.METATILE_SIZE
        self.pixel_y = tile_y * constants.METATILE_SIZE

        # Movement state
        self.is_moving = False
        self.move_progress = 0  # 0 to METATILE_SIZE
        self.direction = constants.DIR_DOWN  # Facing direction
        self.hold_time = 0  # Time direction key has been held
        self.step = 'right_foot'  # Tracks which foot for alternating animation

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
            self.pixel_y = self.tile_y * constants.METATILE_SIZE - self.move_progress
        elif self.direction == constants.DIR_DOWN:
            self.pixel_y = self.tile_y * constants.METATILE_SIZE + self.move_progress
        elif self.direction == constants.DIR_LEFT:
            self.pixel_x = self.tile_x * constants.METATILE_SIZE - self.move_progress
        elif self.direction == constants.DIR_RIGHT:
            self.pixel_x = self.tile_x * constants.METATILE_SIZE + self.move_progress

        # Check if movement is complete
        if self.move_progress >= constants.METATILE_SIZE:
            self.finish_move()

    def finish_move(self):
        """Complete the current movement."""
        self.is_moving = False
        self.move_progress = 0
        self.tile_x = self.target_tile_x
        self.tile_y = self.target_tile_y
        self.pixel_x = self.tile_x * constants.METATILE_SIZE
        self.pixel_y = self.tile_y * constants.METATILE_SIZE

    def cancel_move(self):
        """Cancel current movement and snap back to original position."""
        self.is_moving = False
        self.move_progress = 0
        self.target_tile_x = self.tile_x
        self.target_tile_y = self.tile_y
        self.pixel_x = self.tile_x * constants.METATILE_SIZE
        self.pixel_y = self.tile_y * constants.METATILE_SIZE

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
            constants.METATILE_SIZE,
            constants.METATILE_SIZE
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
