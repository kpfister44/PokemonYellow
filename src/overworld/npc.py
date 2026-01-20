# ABOUTME: Non-player character class for map NPCs
# ABOUTME: Handles NPC rendering, interaction, and dialog

import os
import pygame
from src.engine import constants
from src.overworld.entity import Entity, SpriteSheet


NPC_SPRITE_DIR = os.path.join("assets", "sprites", "npcs")

TRAINER_SPRITE_MAP = {
    "Youngster": "youngster.png",
    "Bug Catcher": "youngster.png",
    "Lass": "girl.png",
}
DEFAULT_SPRITE = "youngster.png"

DIRECTION_MAP = {
    "up": constants.DIR_UP,
    "down": constants.DIR_DOWN,
    "left": constants.DIR_LEFT,
    "right": constants.DIR_RIGHT,
}


class NPC(Entity):
    """Non-player character."""

    def __init__(
        self,
        npc_id,
        tile_x,
        tile_y,
        direction="down",
        dialog_text=None,
        is_trainer=False,
        trainer_data=None,
        sprite_id=None
    ):
        """
        Initialize NPC.

        Args:
            npc_id: Unique identifier
            tile_x, tile_y: Starting position
            direction: Facing direction ("up", "down", "left", "right")
            dialog_text: What NPC says when talked to
            is_trainer: Whether this NPC triggers a battle
            trainer_data: Battle data for trainers
            sprite_id: Optional sprite filename override (e.g., "oak.png")
        """
        super().__init__(tile_x, tile_y, sprite_surface=None)

        self.npc_id = npc_id
        self.dialog_text = dialog_text or "..."
        self.direction = DIRECTION_MAP.get(direction, constants.DIR_DOWN)
        self.is_trainer = is_trainer
        self.trainer_data = trainer_data
        self.defeated = False
        self.sprite_sheet = self._load_sprite_sheet(sprite_id)

    def _load_sprite_sheet(self, sprite_id):
        """Load sprite sheet based on sprite_id or trainer class."""
        if sprite_id:
            sprite_file = sprite_id
        elif self.trainer_data:
            trainer_class = self.trainer_data.get("class", "")
            sprite_file = TRAINER_SPRITE_MAP.get(trainer_class, DEFAULT_SPRITE)
        else:
            sprite_file = DEFAULT_SPRITE

        sprite_path = os.path.join(NPC_SPRITE_DIR, sprite_file)
        return SpriteSheet(sprite_path)

    def render(self, renderer, camera_x, camera_y):
        """Render the NPC using direction-aware sprite."""
        use_walk_frame = self.is_moving and self.animation_frame == 1
        frame = self.sprite_sheet.get_frame(self.direction, use_walk_frame)
        screen_x = self.pixel_x - camera_x
        screen_y = self.pixel_y - camera_y
        renderer.draw_surface(frame, (screen_x, screen_y))

    def interact(self):
        """Called when player interacts with this NPC."""
        return self.dialog_text

    def update(self):
        """Update NPC (stationary for now)."""
        # NPCs don't move in Phase 5
        # Future: Add AI movement patterns
        pass
