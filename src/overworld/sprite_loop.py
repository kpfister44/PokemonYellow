# ABOUTME: Animated sprite class for looping tile animations (water, flowers)
# ABOUTME: Uses TMX tile properties to configure animation parameters

import pygame


class SpriteLoop(pygame.sprite.Sprite):
    """A looped animated sprite for tiles like water and flowers.

    Requires TMX tile properties:
    - src: Path to sprite sheet image
    - width, height: Dimensions of each animation frame
    - frame_count: Number of animation frames
    - mspf: Milliseconds per frame (animation speed)
    """

    def __init__(self, location: tuple[int, int], cell: dict, *groups):
        """
        Initialize the animated sprite.

        Args:
            location: (x, y) pixel position
            cell: Dictionary with tile properties (src, width, height, frames, mspf)
            *groups: Sprite groups to add this sprite to
        """
        super().__init__(*groups)

        self.sheet = pygame.image.load(cell['src']).convert_alpha()

        # Use frame_width/frame_height to avoid pytmx reserved name conflicts
        self.width = int(cell.get('frame_width', cell.get('width', 16)))
        self.height = int(cell.get('frame_height', cell.get('height', 16)))
        self.rect = pygame.Rect(location, (self.width, self.height))

        self.frames = int(cell.get('frame_count', cell.get('frames', 2)))
        self.frame_index = 0
        self.mspf = int(cell['mspf'])  # Milliseconds per frame
        self.time_count = 0

    def update(self, dt: int):
        """
        Update animation frame based on elapsed time.

        Args:
            dt: Delta time in milliseconds
        """
        self.time_count += dt

        if self.time_count >= self.mspf:
            # Advance to next frame
            self.frame_index = (self.frame_index + 1) % self.frames
            self.time_count = 0

    def render(self, renderer, camera_x: int, camera_y: int):
        """
        Render the animated sprite.

        Args:
            renderer: Renderer instance
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        # Only draw the current frame (width x height from top-left)
        frame_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        source_x = self.frame_index * self.width
        frame_surface.blit(self.sheet, (0, 0), (source_x, 0, self.width, self.height))
        renderer.draw_surface(frame_surface, (screen_x, screen_y))
