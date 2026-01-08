# ABOUTME: Non-player character class for map NPCs
# ABOUTME: Handles NPC rendering, interaction, and dialog

import pygame
from src.engine import constants
from src.overworld.entity import Entity


class NPC(Entity):
    """Non-player character."""

    def __init__(self, npc_id, tile_x, tile_y, direction="down", dialog_text=None):
        """
        Initialize NPC.

        Args:
            npc_id: Unique identifier
            tile_x, tile_y: Starting position
            direction: Facing direction
            dialog_text: What NPC says when talked to
        """
        sprite = self._create_placeholder_sprite()
        super().__init__(tile_x, tile_y, sprite)

        self.npc_id = npc_id
        self.dialog_text = dialog_text or "..."
        self.direction = direction

    def _create_placeholder_sprite(self):
        """Create placeholder sprite (different color from player)."""
        sprite = pygame.Surface((constants.TILE_SIZE, constants.TILE_SIZE))
        sprite.fill(constants.COLOR_LIGHTEST)

        # Blue circle (vs player's yellow)
        pygame.draw.circle(
            sprite,
            (50, 100, 200),  # Blue
            (constants.TILE_SIZE // 2, constants.TILE_SIZE // 2),
            constants.TILE_SIZE // 3
        )
        return sprite

    def interact(self):
        """Called when player interacts with this NPC."""
        return self.dialog_text

    def update(self):
        """Update NPC (stationary for now)."""
        # NPCs don't move in Phase 5
        # Future: Add AI movement patterns
        pass
