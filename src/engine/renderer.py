# ABOUTME: Rendering system for Pokemon Yellow with sprite caching
# ABOUTME: Handles display initialization, layer-based rendering, and sprite loading

import pygame
from src.engine import constants


class Renderer:
    """Manages rendering with layer system and sprite caching."""

    def __init__(self):
        """Initialize the renderer and display."""
        self.screen = pygame.display.set_mode(
            (constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Pokemon Yellow")

        # Create game surface at native resolution
        self.game_surface = pygame.Surface(
            (constants.GAME_WIDTH, constants.GAME_HEIGHT)
        )

        # Sprite cache {filepath: Surface}
        self.sprite_cache = {}

    def clear(self, color=constants.COLOR_BLACK):
        """Clear the game surface."""
        self.game_surface.fill(color)

    def draw_surface(self, surface, position):
        """Draw a surface at the given position on the game surface."""
        self.game_surface.blit(surface, position)

    def draw_rect(self, color, rect, width=0):
        """Draw a rectangle on the game surface."""
        pygame.draw.rect(self.game_surface, color, rect, width)

    def draw_text(self, text, x, y, color=(0, 0, 0), font_size=16):
        """
        Draw text at specified position.

        Args:
            text: String to render
            x, y: Position on game surface (not window)
            color: RGB tuple
            font_size: Font size in pixels

        Returns:
            Tuple of (width, height) of rendered text
        """
        if not hasattr(self, '_font_cache'):
            self._font_cache = {}

        if font_size not in self._font_cache:
            self._font_cache[font_size] = pygame.font.Font(None, font_size)

        font = self._font_cache[font_size]
        text_surface = font.render(text, True, color)
        self.game_surface.blit(text_surface, (x, y))
        return text_surface.get_width(), text_surface.get_height()

    def load_sprite(self, filepath):
        """Load a sprite with caching. Returns the loaded Surface."""
        if filepath not in self.sprite_cache:
            try:
                sprite = pygame.image.load(filepath).convert_alpha()
                self.sprite_cache[filepath] = sprite
            except pygame.error as e:
                print(f"Error loading sprite {filepath}: {e}")
                # Return a placeholder surface
                placeholder = pygame.Surface((constants.TILE_SIZE, constants.TILE_SIZE))
                placeholder.fill(constants.COLOR_DEBUG)
                self.sprite_cache[filepath] = placeholder

        return self.sprite_cache[filepath]

    def get_sprite(self, filepath):
        """Get a cached sprite. Load it if not already cached."""
        return self.load_sprite(filepath)

    def present(self):
        """Scale the game surface to window size and display it."""
        # Scale the game surface up to the window size
        scaled_surface = pygame.transform.scale(
            self.game_surface,
            (constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT)
        )
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    def clear_sprite_cache(self):
        """Clear the sprite cache (useful when changing maps)."""
        self.sprite_cache.clear()
